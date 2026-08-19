"""Verification budget calculation, per decision class, with overdraft detection.

    VB = (R * H * u) / c

See README section 2 and spec/metrics.md section 1. The formula is trivial. What
this module adds is the bookkeeping around it: effective cost under agentic
verification, the Class D policy rules, and the inverse calculations that answer
"what would have to change".
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, Literal, Sequence

__all__ = [
    "DecisionClass",
    "BudgetStatus",
    "BudgetError",
    "ClassInputs",
    "ClassBudget",
    "PortfolioBudget",
    "SensitivityPoint",
    "verification_budget",
    "effective_cost",
    "overdraft_ratio",
    "status_for_ratio",
    "evaluate_class",
    "evaluate_portfolio",
    "cost_for_target",
    "reviewers_for_target",
    "utilisation_for_target",
    "reclassification_share",
    "cost_sensitivity",
]

DecisionClass = Literal["A", "B", "C", "D"]
BudgetStatus = Literal["in_budget", "at_limit", "overdraft", "policy_violation", "unbudgeted"]

#: Below this, review has slack. Between this and 1.0 there is none, which
#: matters because arrivals are bursty. See README limitation 3.
AT_LIMIT_LOWER = 0.95

VALID_CLASSES: tuple[str, ...] = ("A", "B", "C", "D")


class BudgetError(ValueError):
    """Raised when budget inputs are inconsistent or violate a class rule."""


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassInputs:
    """Everything needed to size one decision class for one period.

    Attributes:
        decision_class: A, B, C or D.
        reviewers: R. People *qualified for this class*, not headcount. The test
            is whether the organisation would defend this person's approval as a
            qualified judgement.
        hours_per_period: H. Nominal review hours per qualified reviewer.
        utilisation: u. Fraction of H actually available for verification.
        cost_per_decision: c, in hours. Measured, not estimated. Must be None for
            Class D, which has no finite verification cost.
        demand: D. Decisions of this class produced per period.
        containment: k. Fraction of decisions closed by an agent verifier without
            human involvement. Must be 0 unless the verifier passed Gate 3.
        agent_check_cost: c_a. Human hours per decision spent on the verifier's
            own output. Small, never zero.
        label: Optional human-readable name for reports.
    """

    decision_class: str
    reviewers: float
    hours_per_period: float
    utilisation: float
    cost_per_decision: float | None
    demand: float = 0.0
    containment: float = 0.0
    agent_check_cost: float = 0.0
    label: str = ""

    def __post_init__(self) -> None:
        if self.decision_class not in VALID_CLASSES:
            raise BudgetError(
                f"decision_class must be one of {VALID_CLASSES}, got {self.decision_class!r}"
            )
        if self.reviewers < 0:
            raise BudgetError("reviewers (R) must not be negative")
        if self.hours_per_period < 0:
            raise BudgetError("hours_per_period (H) must not be negative")
        if not 0.0 <= self.utilisation <= 1.0:
            raise BudgetError(
                f"utilisation (u) must be within 0 to 1, got {self.utilisation}. "
                "Above 0.7 is almost always fiction; above 1.0 is arithmetic."
            )
        if self.demand < 0:
            raise BudgetError("demand (D) must not be negative")
        if not 0.0 <= self.containment <= 1.0:
            raise BudgetError(f"containment (k) must be within 0 to 1, got {self.containment}")
        if self.agent_check_cost < 0:
            raise BudgetError("agent_check_cost (c_a) must not be negative")

        if self.decision_class == "D":
            if self.cost_per_decision is not None:
                raise BudgetError(
                    "Class D has no finite verification cost. Pass cost_per_decision=None. "
                    "A Class D decision is prepared by an agent and made by a human."
                )
            if self.containment > 0.0:
                raise BudgetError(
                    "Class D cannot be contained by an agent verifier. "
                    "Containment applies where a machine-checkable verdict is possible."
                )
        else:
            if self.cost_per_decision is None:
                raise BudgetError(
                    f"Class {self.decision_class} needs a measured cost_per_decision (c). "
                    "An estimated c produces a budget that restates your assumptions."
                )
            if self.cost_per_decision <= 0:
                raise BudgetError(
                    f"cost_per_decision (c) must be positive, got {self.cost_per_decision}"
                )


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassBudget:
    """The budget position for one class in one period."""

    decision_class: str
    budget: float
    demand: float
    nominal_cost: float | None
    effective_cost: float | None
    containment: float
    overdraft_ratio: float | None
    verified_fraction: float
    unverified_decisions: float
    headroom: float | None
    status: BudgetStatus
    notes: tuple[str, ...] = ()

    @property
    def in_budget(self) -> bool:
        return self.status in ("in_budget", "unbudgeted")

    @property
    def unverified_share(self) -> float:
        """Fraction of this class's demand for which no verification capacity exists."""
        if self.demand <= 0:
            return 0.0
        return self.unverified_decisions / self.demand


@dataclass(frozen=True)
class PortfolioBudget:
    """All classes together, plus the warning that the total is misleading."""

    classes: tuple[ClassBudget, ...]
    period: str = "period"

    def by_class(self, decision_class: str) -> ClassBudget:
        for entry in self.classes:
            if entry.decision_class == decision_class:
                return entry
        raise KeyError(f"no budget computed for class {decision_class!r}")

    @property
    def total_demand(self) -> float:
        return sum(entry.demand for entry in self.classes)

    @property
    def total_unverified(self) -> float:
        return sum(entry.unverified_decisions for entry in self.classes)

    @property
    def overdrafted_classes(self) -> tuple[ClassBudget, ...]:
        return tuple(e for e in self.classes if e.status == "overdraft")

    @property
    def policy_violations(self) -> tuple[ClassBudget, ...]:
        return tuple(e for e in self.classes if e.status == "policy_violation")

    @property
    def worst(self) -> ClassBudget | None:
        """The class in the worst position. This is the number that matters."""
        ranked = [e for e in self.classes if e.overdraft_ratio is not None]
        if not ranked:
            return None
        return max(ranked, key=lambda e: e.overdraft_ratio or 0.0)


@dataclass(frozen=True)
class SensitivityPoint:
    """One point on the "what if c fell" curve."""

    cost_multiplier: float
    nominal_cost: float
    effective_cost: float
    budget: float
    overdraft_ratio: float | None
    status: BudgetStatus


# ---------------------------------------------------------------------------
# Core arithmetic
# ---------------------------------------------------------------------------


def effective_cost(
    cost_per_decision: float,
    containment: float = 0.0,
    agent_check_cost: float = 0.0,
) -> float:
    """c_eff = c_a + (1 - k) * c.

    The agentic verification adjustment. As containment rises, effective cost
    falls and the budget rises without hiring anybody.

    Two things this function cannot check and you must:

    1. Containment counts only if the verifier passed Gate 3. Uncalibrated
       verifiers get k = 0, not an estimate.
    2. ``c`` rises as ``k`` rises, because the verifier closes the easy decisions
       and the residual human queue is harder than the original average.
       Re-measure c after every material change to k.
    """
    if cost_per_decision <= 0:
        raise BudgetError("cost_per_decision must be positive")
    if not 0.0 <= containment <= 1.0:
        raise BudgetError("containment must be within 0 to 1")
    if agent_check_cost < 0:
        raise BudgetError("agent_check_cost must not be negative")
    return agent_check_cost + (1.0 - containment) * cost_per_decision


def verification_budget(
    reviewers: float,
    hours_per_period: float,
    utilisation: float,
    cost_per_decision: float,
) -> float:
    """VB = (R * H * u) / c, in decisions per period."""
    if cost_per_decision <= 0:
        raise BudgetError("cost_per_decision must be positive")
    if not 0.0 <= utilisation <= 1.0:
        raise BudgetError("utilisation must be within 0 to 1")
    if reviewers < 0 or hours_per_period < 0:
        raise BudgetError("reviewers and hours_per_period must not be negative")
    return (reviewers * hours_per_period * utilisation) / cost_per_decision


def overdraft_ratio(demand: float, budget: float) -> float | None:
    """O = D / VB.

    Returns ``None`` when both demand and budget are zero, where the ratio has no
    meaning. Returns infinity when there is demand and no budget, which is the
    honest answer rather than an error.
    """
    if budget == 0.0:
        if demand == 0.0:
            return None
        return math.inf
    return demand / budget


def status_for_ratio(ratio: float | None) -> BudgetStatus:
    """Map an overdraft ratio to a status band."""
    if ratio is None:
        return "in_budget"
    if ratio > 1.0:
        return "overdraft"
    if ratio >= AT_LIMIT_LOWER:
        return "at_limit"
    return "in_budget"


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def evaluate_class(inputs: ClassInputs) -> ClassBudget:
    """Compute the budget position for one class.

    Class D is not an expensive class, it is an unbudgeted one. It gets
    ``budget = 0`` and ``overdraft_ratio = None``, and any autonomous demand is
    reported as ``policy_violation`` rather than overdraft. A policy violation is
    a contract breach handled by revocation, not a capacity problem handled by
    the budget.
    """
    notes: list[str] = []

    if inputs.decision_class == "D":
        if inputs.demand > 0:
            notes.append(
                f"{inputs.demand:g} Class D decisions taken autonomously. "
                "Class D is never delegated. This is a contract breach, not an overdraft: "
                "revoke per the agent's revocation clause and investigate scope."
            )
            status: BudgetStatus = "policy_violation"
        else:
            notes.append(
                "Class D is not budgeted. Agents prepare Class D decisions and humans make them. "
                "The preparation is a Class C artifact and consumes Class C budget."
            )
            status = "unbudgeted"
        return ClassBudget(
            decision_class="D",
            budget=0.0,
            demand=inputs.demand,
            nominal_cost=None,
            effective_cost=None,
            containment=0.0,
            overdraft_ratio=None,
            verified_fraction=0.0 if inputs.demand > 0 else 1.0,
            unverified_decisions=inputs.demand,
            headroom=None,
            status=status,
            notes=tuple(notes),
        )

    nominal = float(inputs.cost_per_decision)  # not None for A, B, C
    c_eff = effective_cost(nominal, inputs.containment, inputs.agent_check_cost)
    budget = verification_budget(
        inputs.reviewers, inputs.hours_per_period, inputs.utilisation, c_eff
    )
    ratio = overdraft_ratio(inputs.demand, budget)
    status = status_for_ratio(ratio)

    unverified = max(0.0, inputs.demand - budget)
    verified_fraction = 1.0 if inputs.demand == 0 else min(1.0, budget / inputs.demand)

    if inputs.containment > 0:
        notes.append(
            f"Containment k={inputs.containment:.3f} applied, cutting cost from "
            f"{nominal:.4g}h to {c_eff:.4g}h. Valid only if the verifier passed Gate 3 and "
            "this is the lower bound of its 95 percent confidence interval."
        )
        notes.append(
            "Re-measure c: the verifier closes the easy decisions, so the residual "
            "human queue is harder than the original average and c rises as k rises."
        )
    if status == "overdraft":
        notes.append(
            f"{unverified:.4g} decisions per period have no verification capacity. "
            "They are not at risk of being unverified. They are unverified."
        )
    elif status == "at_limit":
        notes.append(
            "No absorption capacity for a bad week. Arrivals are bursty, so treat this "
            "as a planning trigger rather than a passing grade."
        )

    return ClassBudget(
        decision_class=inputs.decision_class,
        budget=budget,
        demand=inputs.demand,
        nominal_cost=nominal,
        effective_cost=c_eff,
        containment=inputs.containment,
        overdraft_ratio=ratio,
        verified_fraction=verified_fraction,
        unverified_decisions=unverified,
        headroom=budget - inputs.demand,
        status=status,
        notes=tuple(notes),
    )


def evaluate_portfolio(
    inputs: Iterable[ClassInputs], period: str = "period"
) -> PortfolioBudget:
    """Evaluate every class. Report per class, never as a single portfolio number."""
    return PortfolioBudget(
        classes=tuple(evaluate_class(entry) for entry in inputs), period=period
    )


# ---------------------------------------------------------------------------
# Inverse calculations: what would have to change
# ---------------------------------------------------------------------------


def cost_for_target(
    reviewers: float,
    hours_per_period: float,
    utilisation: float,
    demand: float,
    target_ratio: float = 1.0,
    containment: float = 0.0,
    agent_check_cost: float = 0.0,
) -> float | None:
    """The nominal c that would bring this class to ``target_ratio``.

    Returns ``None`` when the target is unreachable by cutting c alone, which
    happens when the agent-check cost alone already exceeds the budget per
    decision. That is a real answer and it means the lever is R or D, not c.
    """
    if demand <= 0:
        return None
    if target_ratio <= 0:
        raise BudgetError("target_ratio must be positive")

    capacity = reviewers * hours_per_period * utilisation
    if capacity <= 0:
        return None

    c_eff_target = (capacity * target_ratio) / demand
    if containment >= 1.0:
        return None
    nominal = (c_eff_target - agent_check_cost) / (1.0 - containment)
    if nominal <= 0:
        return None
    return nominal


def reviewers_for_target(
    hours_per_period: float,
    utilisation: float,
    cost_per_decision: float,
    demand: float,
    target_ratio: float = 1.0,
    containment: float = 0.0,
    agent_check_cost: float = 0.0,
) -> float | None:
    """Qualified reviewers needed to reach ``target_ratio``.

    Usually reported to show that the number does not exist. Qualification is the
    bottleneck, not hiring.
    """
    if demand <= 0:
        return 0.0
    if hours_per_period <= 0 or utilisation <= 0:
        return None
    if target_ratio <= 0:
        raise BudgetError("target_ratio must be positive")

    c_eff = effective_cost(cost_per_decision, containment, agent_check_cost)
    return (demand * c_eff) / (hours_per_period * utilisation * target_ratio)


def utilisation_for_target(
    reviewers: float,
    hours_per_period: float,
    cost_per_decision: float,
    demand: float,
    target_ratio: float = 1.0,
    containment: float = 0.0,
    agent_check_cost: float = 0.0,
) -> float | None:
    """Utilisation needed to reach ``target_ratio``.

    Returns ``None`` when the answer exceeds 1.0, meaning the target is out of
    reach even with reviewers doing nothing but verification.
    """
    if demand <= 0:
        return 0.0
    if reviewers <= 0 or hours_per_period <= 0:
        return None
    if target_ratio <= 0:
        raise BudgetError("target_ratio must be positive")

    c_eff = effective_cost(cost_per_decision, containment, agent_check_cost)
    required = (demand * c_eff) / (reviewers * hours_per_period * target_ratio)
    if required > 1.0:
        return None
    return required


def reclassification_share(
    demand: float, budget: float, target_ratio: float = 1.0
) -> float:
    """Share of demand that must move to a cheaper class to reach ``target_ratio``.

    Reclassification means making a decision cheaper to check. Renaming a Class C
    decision as Class B changes nothing except how visible the overdraft is, so
    treat this number as a size of engineering work, not a size of paperwork.
    """
    if demand <= 0:
        return 0.0
    if target_ratio <= 0:
        raise BudgetError("target_ratio must be positive")
    keep = budget * target_ratio
    if keep >= demand:
        return 0.0
    return min(1.0, 1.0 - keep / demand)


def cost_sensitivity(
    inputs: ClassInputs,
    multipliers: Sequence[float] = (1.0, 0.9, 0.75, 0.5, 0.35, 0.25, 0.1),
) -> tuple[SensitivityPoint, ...]:
    """The effect on the budget of reducing c.

    ``c`` is the only lever with orders of magnitude in it, which is why the
    calculator and the CLI both show this curve rather than a single number.
    """
    if inputs.decision_class == "D" or inputs.cost_per_decision is None:
        return ()

    points: list[SensitivityPoint] = []
    for multiplier in multipliers:
        if multiplier <= 0:
            raise BudgetError("cost multipliers must be positive")
        nominal = inputs.cost_per_decision * multiplier
        c_eff = effective_cost(nominal, inputs.containment, inputs.agent_check_cost)
        budget = verification_budget(
            inputs.reviewers, inputs.hours_per_period, inputs.utilisation, c_eff
        )
        ratio = overdraft_ratio(inputs.demand, budget)
        points.append(
            SensitivityPoint(
                cost_multiplier=multiplier,
                nominal_cost=nominal,
                effective_cost=c_eff,
                budget=budget,
                overdraft_ratio=ratio,
                status=status_for_ratio(ratio),
            )
        )
    return tuple(points)
