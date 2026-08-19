"""The six operating metrics, computed from an event log.

    1. VB   verification budget          capacity
    2. O    overdraft ratio              are you spending capacity you have
    3. SDR  silent drift rate            are the approvals real
    4. k    containment                  how much verification agents supply
    5. EP   escalation precision         are escalations worth their budget
    6. RL   reversal latency             is the safety net real

All six are reported per decision class, per period. Reporting them portfolio-wide
averages a healthy Class A over a drowning Class C and shows nothing.

See spec/metrics.md for the normative definitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from ._io import Bundle
from ._stats import iqr, median, percentile, wilson_interval
from .budget import ClassBudget, ClassInputs, evaluate_class
from .drift import Approval, DriftReport, Floor, drift_report, floor_from_baseline

__all__ = [
    "MeasuredCost",
    "Containment",
    "EscalationPrecision",
    "ReversalLatency",
    "ClassMetrics",
    "MetricSet",
    "measured_cost",
    "demand_per_period",
    "containment",
    "escalation_precision",
    "reversal_latency",
    "approvals_from_events",
    "compute_class",
    "compute_all",
]

SECONDS_PER_HOUR = 3600.0


# ---------------------------------------------------------------------------
# Metric 0: the measured input
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeasuredCost:
    """c-hat with everything needed to judge whether to trust it."""

    decision_class: str
    hours: float
    sample_size: int
    interquartile_range: tuple[float, float]
    measured_at: str | None
    discarded_not_genuine: int

    @property
    def spread_ratio(self) -> float:
        """P75 over P25. Above about 10 this is not one class."""
        low, high = self.interquartile_range
        if low <= 0:
            return float("inf") if high > 0 else 1.0
        return high / low

    @property
    def suspiciously_wide(self) -> bool:
        return self.spread_ratio > 10.0


def measured_cost(
    rows: Sequence[dict[str, Any]],
    decision_class: str,
    measured_at: str | None = None,
) -> MeasuredCost | None:
    """Compute c-hat from timing observations.

    Expects rows with ``idle_trimmed_seconds`` and ``genuinely_checked``.
    Observations where the reviewer said afterwards they did not genuinely check
    are discarded, which is the step that makes the number mean something.

    Returns the **median**, not the mean. The distribution is right-skewed and
    the mean flatters the budget by pulling toward the tail.
    """
    kept: list[float] = []
    discarded = 0
    for row in rows:
        if str(row.get("decision_class", decision_class)) != decision_class:
            continue
        genuine = row.get("genuinely_checked")
        if isinstance(genuine, str):
            genuine = genuine.strip().lower() in {"1", "true", "yes", "y"}
        if not genuine:
            discarded += 1
            continue
        seconds = row.get("idle_trimmed_seconds", row.get("raw_seconds"))
        if seconds is None:
            continue
        kept.append(float(seconds) / SECONDS_PER_HOUR)

    if not kept:
        return None

    return MeasuredCost(
        decision_class=decision_class,
        hours=median(kept),
        sample_size=len(kept),
        interquartile_range=iqr(kept),
        measured_at=measured_at,
        discarded_not_genuine=discarded,
    )


# ---------------------------------------------------------------------------
# Metric 2 input: demand
# ---------------------------------------------------------------------------


def demand_per_period(
    events: Iterable[dict[str, Any]], decision_class: str, periods: int
) -> float:
    """Decisions of this class produced per period.

    Counts decisions, not artifacts, not tasks, not tokens. Escalations count:
    they consume verification budget at the class cost of the escalated decision,
    which is why escalation precision is one of the six.
    """
    if periods < 1:
        raise ValueError("periods must be at least 1")
    count = sum(1 for e in events if e.get("decision_class") == decision_class)
    return count / periods


# ---------------------------------------------------------------------------
# Metric 4: containment
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Containment:
    """k, with the false-negative rate that makes it a metric rather than a claim."""

    decision_class: str
    offered: int
    contained: int
    rate: float
    ci95: tuple[float, float]
    lower_bound: float
    false_negative_rate: float | None
    known_bad_seen: int
    calibrated: bool
    budget_value: float
    note: str = ""

    @property
    def reportable(self) -> str:
        if not self.calibrated:
            return "k = 0.00 (uncalibrated)"
        return f"k = {self.rate:.3f}  CI95 [{self.ci95[0]:.3f}, {self.ci95[1]:.3f}]  budget uses {self.budget_value:.3f}"


def containment(
    events: Sequence[dict[str, Any]],
    decision_class: str,
    calibrated: bool | None = None,
    max_false_negative_rate: float = 0.05,
) -> Containment:
    """Containment for one class, with the Wilson interval and the FNR.

    A verifier that passes everything has k = 1.0 and FNR = 1.0. The first number
    looks like a triumph. Reporting them together is the only thing that stops it
    being reported as one.

    The budget uses the **lower bound** of the interval, and zero if the verifier
    is not calibrated or its FNR is above the Gate 3 threshold.
    """
    scoped = [e for e in events if e.get("decision_class") == decision_class]
    offered = [e for e in scoped if e.get("verifier_offered")]
    contained_events = [e for e in offered if e.get("verifier_contained")]

    n_offered = len(offered)
    n_contained = len(contained_events)
    rate = (n_contained / n_offered) if n_offered else 0.0
    ci = wilson_interval(n_contained, n_offered) if n_offered else (0.0, 0.0)

    known_bad = [e for e in offered if e.get("known_bad")]
    false_negatives = [e for e in known_bad if e.get("verifier_contained") and e.get("verifier_verdict") == "pass"]
    fnr = (len(false_negatives) / len(known_bad)) if known_bad else None

    if calibrated is None:
        calibrated = bool(known_bad) and fnr is not None and fnr <= max_false_negative_rate

    note = ""
    budget_value = 0.0
    if not n_offered:
        note = "No verifier on this class."
    elif not calibrated:
        if fnr is None:
            note = (
                "No known-bad decisions in the offered set, so the false-negative rate is "
                "unmeasured. Uncalibrated verifiers contribute k = 0. See Gate 3."
            )
        else:
            note = (
                f"False-negative rate {fnr:.3f} is above the Gate 3 threshold of "
                f"{max_false_negative_rate:.2f}. Containment set to 0. The verifier keeps "
                "running as an advisory annotation, which still helps a human by pointing "
                "at what to look at."
            )
    else:
        budget_value = ci[0]
        note = (
            "Budget uses the lower bound of the 95 percent interval, not the point "
            "estimate. Re-measure c: the verifier closes the easy decisions, so the "
            "residual human queue is harder than the original average."
        )

    return Containment(
        decision_class=decision_class,
        offered=n_offered,
        contained=n_contained,
        rate=rate,
        ci95=ci,
        lower_bound=ci[0],
        false_negative_rate=fnr,
        known_bad_seen=len(known_bad),
        calibrated=bool(calibrated),
        budget_value=budget_value,
        note=note,
    )


# ---------------------------------------------------------------------------
# Metric 5: escalation precision
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EscalationPrecision:
    """EP, plus the honest statement that recall is unmeasured."""

    decision_class: str
    escalations: int
    upheld: int
    precision: float | None
    target: float = 0.7

    @property
    def passes(self) -> bool:
        return self.precision is not None and self.precision >= self.target

    @property
    def recall_note(self) -> str:
        return (
            "Escalation recall is what you actually want and it is not measured here, "
            "because you do not observe the escalations that should have happened and "
            "did not. Injected probes are the recommended proxy. See spec/metrics.md."
        )


def escalation_precision(
    events: Sequence[dict[str, Any]], decision_class: str, target: float = 0.7
) -> EscalationPrecision:
    """Of the decisions the agent escalated, the share a human agreed needed it."""
    scoped = [e for e in events if e.get("decision_class") == decision_class]
    escalated = [e for e in scoped if e.get("escalated")]
    upheld = [e for e in escalated if e.get("escalation_upheld")]
    precision = (len(upheld) / len(escalated)) if escalated else None
    return EscalationPrecision(
        decision_class=decision_class,
        escalations=len(escalated),
        upheld=len(upheld),
        precision=precision,
        target=target,
    )


# ---------------------------------------------------------------------------
# Metric 6: reversal latency
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReversalLatency:
    """RL, with the breach rate that audits the evidence plane's reversal field."""

    decision_class: str
    reversals: int
    median_hours: float | None
    p90_hours: float | None
    breach_rate: float | None
    breaches: int

    @property
    def reversal_field_unreliable(self) -> bool:
        """Above 0.2, treat reversal.cheap_until as unreliable across the board."""
        return self.breach_rate is not None and self.breach_rate > 0.2

    @property
    def note(self) -> str:
        return (
            "RL only sees reversals that happened. Decisions that were wrong and never "
            "reversed do not appear, so this is a lower bound on how bad reversal "
            "performance is. Read it next to SDR."
        )


def reversal_latency(
    events: Sequence[dict[str, Any]], decision_class: str
) -> ReversalLatency:
    """Median and P90 hours from decision to reversal, plus the window breach rate."""
    scoped = [e for e in events if e.get("decision_class") == decision_class]
    reversed_events = [e for e in scoped if e.get("reversed")]

    latencies = [
        float(e["reversed_after_hours"])
        for e in reversed_events
        if e.get("reversed_after_hours") is not None
    ]
    breaches = sum(1 for e in reversed_events if e.get("reversed_after_cheap_until"))

    if not latencies:
        return ReversalLatency(
            decision_class=decision_class,
            reversals=len(reversed_events),
            median_hours=None,
            p90_hours=None,
            breach_rate=None,
            breaches=breaches,
        )

    return ReversalLatency(
        decision_class=decision_class,
        reversals=len(reversed_events),
        median_hours=median(latencies),
        p90_hours=percentile(latencies, 90.0),
        breach_rate=breaches / len(reversed_events),
        breaches=breaches,
    )


# ---------------------------------------------------------------------------
# Drift input
# ---------------------------------------------------------------------------


def approvals_from_events(
    events: Sequence[dict[str, Any]], decision_class: str
) -> list[Approval]:
    """Extract approval events for drift analysis.

    Only approvals. A fast rejection is often a good rejection.
    """
    result: list[Approval] = []
    for event in events:
        if event.get("decision_class") != decision_class:
            continue
        if event.get("outcome") != "approved":
            continue
        seconds = event.get("idle_trimmed_seconds", event.get("review_seconds"))
        if seconds is None:
            continue
        result.append(
            Approval(
                period=event.get("period", 1),
                duration_hours=float(seconds) / SECONDS_PER_HOUR,
                reviewer_id=event.get("reviewer_id"),
                submitted_at=event.get("submitted_at_epoch"),
            )
        )
    return result


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassMetrics:
    """All six metrics for one class."""

    decision_class: str
    budget: ClassBudget
    cost: MeasuredCost | None
    drift: DriftReport | None
    containment: Containment
    escalation: EscalationPrecision
    reversal: ReversalLatency
    period_name: str = "period"

    @property
    def headline(self) -> str:
        """The one line worth putting on a slide."""
        ratio = self.budget.overdraft_ratio
        if ratio is None:
            return f"Class {self.decision_class}: {self.budget.status.replace('_', ' ')}"
        drift = f", SDR {self.drift.drift_rate:.2f}" if self.drift else ""
        return (
            f"Class {self.decision_class}: O = {ratio:.2f}x "
            f"({self.budget.status.replace('_', ' ')}){drift}"
        )


@dataclass(frozen=True)
class MetricSet:
    """Every class, plus the bundle context needed to read the numbers."""

    name: str
    synthetic: bool
    periods: int
    period_name: str
    classes: tuple[ClassMetrics, ...]

    def by_class(self, decision_class: str) -> ClassMetrics:
        for entry in self.classes:
            if entry.decision_class == decision_class:
                return entry
        raise KeyError(f"no metrics computed for class {decision_class!r}")

    @property
    def worst(self) -> ClassMetrics | None:
        ranked = [c for c in self.classes if c.budget.overdraft_ratio is not None]
        if not ranked:
            return None
        return max(ranked, key=lambda c: c.budget.overdraft_ratio or 0.0)


def _floor_for(
    bundle: Bundle, decision_class: str, settings: dict[str, Any]
) -> Floor | None:
    """Derive the drift floor, preferring the calibrated baseline in timing.csv."""
    baseline_rows = bundle.timing_for(decision_class, genuine_only=True)
    durations = [
        float(r["idle_trimmed_seconds"]) / SECONDS_PER_HOUR
        for r in baseline_rows
        if r.get("idle_trimmed_seconds")
    ]
    words = settings.get("median_artifact_words")

    if durations:
        return floor_from_baseline(
            durations,
            median_artifact_words=float(words) if words is not None else None,
            percentile_rank=float(settings.get("floor_percentile", 10.0)),
        )

    explicit = settings.get("floor_hours")
    if explicit is None:
        return None
    rank = float(settings.get("floor_percentile", 10.0))
    return Floor(
        hours=float(explicit),
        baseline_percentile_hours=float(explicit),
        reading_floor_hours=0.0,
        percentile_rank=rank,
        baseline_drift_rate=rank / 100.0,
        sample_size=0,
        binding_term="config",
    )


def compute_class(bundle: Bundle, decision_class: str) -> ClassMetrics:
    """Compute all six metrics for one class of a loaded bundle."""
    settings = bundle.class_config.get(decision_class)
    if settings is None:
        raise KeyError(f"config has no entry for class {decision_class!r}")

    demand = demand_per_period(bundle.events, decision_class, bundle.periods)

    cost = measured_cost(
        bundle.timing,
        decision_class,
        measured_at=settings.get("cost_measured_at"),
    )
    configured_cost = settings.get("cost_per_decision")
    cost_hours = configured_cost if configured_cost is not None else (cost.hours if cost else None)

    contained = containment(
        bundle.events,
        decision_class,
        calibrated=settings.get("verifier_calibrated"),
    )

    inputs = ClassInputs(
        decision_class=decision_class,
        reviewers=float(settings.get("reviewers", 0)),
        hours_per_period=float(settings.get("hours_per_period", 0)),
        utilisation=float(settings.get("utilisation", 0)),
        cost_per_decision=None if decision_class == "D" else cost_hours,
        demand=demand,
        containment=0.0 if decision_class == "D" else contained.budget_value,
        agent_check_cost=float(settings.get("agent_check_cost", 0.0)),
    )
    budget = evaluate_class(inputs)

    floor = _floor_for(bundle, decision_class, settings)
    approvals = approvals_from_events(bundle.events, decision_class)
    drift = drift_report(approvals, floor, decision_class) if (floor and approvals) else None

    return ClassMetrics(
        decision_class=decision_class,
        budget=budget,
        cost=cost,
        drift=drift,
        containment=contained,
        escalation=escalation_precision(bundle.events, decision_class),
        reversal=reversal_latency(bundle.events, decision_class),
        period_name=bundle.period_name,
    )


def compute_all(bundle: Bundle) -> MetricSet:
    """Compute every class in the bundle, in A B C D order."""
    order = [c for c in ("A", "B", "C", "D") if c in bundle.class_config]
    order += [c for c in bundle.class_config if c not in order]
    return MetricSet(
        name=bundle.name,
        synthetic=bundle.synthetic,
        periods=bundle.periods,
        period_name=bundle.period_name,
        classes=tuple(compute_class(bundle, c) for c in order),
    )
