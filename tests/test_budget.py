"""Budget arithmetic. The formula is trivial; the class rules are not."""

from __future__ import annotations

import math

import pytest

from vb.budget import (
    AT_LIMIT_LOWER,
    BudgetError,
    ClassInputs,
    cost_for_target,
    cost_sensitivity,
    effective_cost,
    evaluate_class,
    evaluate_portfolio,
    overdraft_ratio,
    reclassification_share,
    reviewers_for_target,
    status_for_ratio,
    utilisation_for_target,
    verification_budget,
)


# ---------------------------------------------------------------------------
# The formula
# ---------------------------------------------------------------------------


def test_the_worked_instance_from_the_readme():
    """VB = (6 * 8 * 0.55) / 1.25 = 21.12 decisions per week."""
    assert verification_budget(6, 8, 0.55, 1.25) == pytest.approx(21.12)


def test_units_are_decisions_per_period():
    # Doubling reviewers doubles the budget. Halving c doubles the budget.
    base = verification_budget(6, 8, 0.55, 1.25)
    assert verification_budget(12, 8, 0.55, 1.25) == pytest.approx(2 * base)
    assert verification_budget(6, 8, 0.55, 0.625) == pytest.approx(2 * base)


@pytest.mark.parametrize("utilisation", [-0.1, 1.1, 2.0])
def test_utilisation_outside_zero_to_one_is_rejected(utilisation):
    with pytest.raises(BudgetError, match="utilisation"):
        verification_budget(6, 8, utilisation, 1.25)


def test_zero_cost_is_rejected():
    with pytest.raises(BudgetError, match="positive"):
        verification_budget(6, 8, 0.55, 0.0)


def test_negative_reviewers_rejected():
    with pytest.raises(BudgetError):
        verification_budget(-1, 8, 0.55, 1.25)


# ---------------------------------------------------------------------------
# Effective cost under agentic verification
# ---------------------------------------------------------------------------


def test_effective_cost_without_containment_is_the_nominal_cost():
    assert effective_cost(1.25, 0.0, 0.0) == pytest.approx(1.25)


def test_containment_reduces_effective_cost():
    # c_eff = c_a + (1 - k) * c
    assert effective_cost(0.02, 0.70, 0.005) == pytest.approx(0.005 + 0.30 * 0.02)


def test_full_containment_leaves_only_the_agent_check_cost():
    assert effective_cost(1.25, 1.0, 0.008) == pytest.approx(0.008)


def test_containment_outside_zero_to_one_is_rejected():
    with pytest.raises(BudgetError, match="containment"):
        effective_cost(1.25, 1.5, 0.0)


def test_containment_raises_the_budget():
    plain = verification_budget(14, 8, 0.55, effective_cost(0.02))
    with_verifier = verification_budget(14, 8, 0.55, effective_cost(0.02, 0.69, 0.005))
    assert with_verifier > plain


# ---------------------------------------------------------------------------
# Overdraft
# ---------------------------------------------------------------------------


def test_overdraft_ratio_reproduces_the_headline_figure():
    assert overdraft_ratio(70, 21.12) == pytest.approx(3.3144, rel=1e-4)


def test_demand_with_no_budget_is_infinite_not_an_error():
    assert overdraft_ratio(10, 0.0) == math.inf


def test_no_demand_and_no_budget_has_no_ratio():
    assert overdraft_ratio(0, 0.0) is None


@pytest.mark.parametrize(
    "ratio,expected",
    [
        (0.0, "in_budget"),
        (0.5, "in_budget"),
        (0.94999, "in_budget"),
        (AT_LIMIT_LOWER, "at_limit"),
        (1.0, "at_limit"),
        (1.0001, "overdraft"),
        (3.31, "overdraft"),
        (None, "in_budget"),
    ],
)
def test_status_bands(ratio, expected):
    assert status_for_ratio(ratio) == expected


def test_at_limit_band_exists_because_arrivals_are_bursty():
    result = evaluate_class(
        ClassInputs("C", 6, 8, 0.55, 1.25, demand=21.0)
    )
    assert result.status == "at_limit"
    assert any("absorption capacity" in note for note in result.notes)


# ---------------------------------------------------------------------------
# evaluate_class
# ---------------------------------------------------------------------------


def test_class_c_overdraft_end_to_end():
    result = evaluate_class(ClassInputs("C", 6, 8, 0.55, 1.25, demand=70))
    assert result.budget == pytest.approx(21.12)
    assert result.overdraft_ratio == pytest.approx(3.3144, rel=1e-4)
    assert result.status == "overdraft"
    assert result.unverified_decisions == pytest.approx(48.88)
    assert result.verified_fraction == pytest.approx(21.12 / 70)
    assert result.unverified_share == pytest.approx(48.88 / 70)
    assert result.headroom == pytest.approx(-48.88)
    assert not result.in_budget


def test_unverified_means_unverified_not_at_risk():
    result = evaluate_class(ClassInputs("C", 6, 8, 0.55, 1.25, demand=70))
    joined = " ".join(result.notes)
    assert "not at risk of being unverified" in joined


def test_in_budget_class():
    result = evaluate_class(ClassInputs("B", 9, 8, 0.55, 0.15, demand=160))
    assert result.status == "in_budget"
    assert result.in_budget
    assert result.unverified_decisions == 0.0
    assert result.verified_fraction == 1.0


def test_zero_demand_is_fully_verified():
    result = evaluate_class(ClassInputs("A", 14, 8, 0.55, 0.02, demand=0))
    assert result.verified_fraction == 1.0
    assert result.overdraft_ratio == 0.0


# ---------------------------------------------------------------------------
# Class D rules
# ---------------------------------------------------------------------------


def test_class_d_with_a_cost_is_rejected():
    with pytest.raises(BudgetError, match="no finite verification cost"):
        ClassInputs("D", 6, 8, 0.55, 1.25)


def test_class_d_cannot_be_contained():
    with pytest.raises(BudgetError, match="cannot be contained"):
        ClassInputs("D", 6, 8, 0.55, None, containment=0.5)


def test_class_d_with_no_demand_is_unbudgeted_not_in_budget():
    result = evaluate_class(ClassInputs("D", 6, 8, 0.55, None, demand=0))
    assert result.status == "unbudgeted"
    assert result.budget == 0.0
    assert result.overdraft_ratio is None
    assert "never delegated" in " ".join(result.notes) or "not budgeted" in " ".join(result.notes)


def test_autonomous_class_d_is_a_policy_violation_not_an_overdraft():
    result = evaluate_class(ClassInputs("D", 6, 8, 0.55, None, demand=3))
    assert result.status == "policy_violation"
    assert result.overdraft_ratio is None
    assert result.unverified_decisions == 3
    assert "contract breach" in " ".join(result.notes)


def test_classes_abc_require_a_measured_cost():
    for decision_class in ("A", "B", "C"):
        with pytest.raises(BudgetError, match="measured cost_per_decision"):
            ClassInputs(decision_class, 6, 8, 0.55, None)


def test_unknown_class_rejected():
    with pytest.raises(BudgetError, match="decision_class"):
        ClassInputs("E", 6, 8, 0.55, 1.0)


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------


def test_portfolio_reports_per_class_and_finds_the_worst():
    portfolio = evaluate_portfolio(
        [
            ClassInputs("A", 14, 8, 0.55, 0.02, demand=320),
            ClassInputs("B", 9, 8, 0.55, 0.15, demand=160),
            ClassInputs("C", 6, 8, 0.55, 1.25, demand=70),
            ClassInputs("D", 6, 8, 0.55, None, demand=0),
        ],
        period="week",
    )
    assert portfolio.worst is not None
    assert portfolio.worst.decision_class == "C"
    assert len(portfolio.overdrafted_classes) == 1
    assert portfolio.policy_violations == ()
    assert portfolio.total_demand == 550
    assert portfolio.total_unverified == pytest.approx(48.88)
    assert portfolio.by_class("B").status == "in_budget"


def test_portfolio_average_would_hide_the_problem():
    """The reason every metric is reported per class."""
    portfolio = evaluate_portfolio(
        [
            ClassInputs("A", 14, 8, 0.55, 0.02, demand=320),
            ClassInputs("B", 9, 8, 0.55, 0.15, demand=160),
            ClassInputs("C", 6, 8, 0.55, 1.25, demand=70),
        ]
    )
    total_budget = sum(e.budget for e in portfolio.classes)
    aggregate = portfolio.total_demand / total_budget
    assert aggregate < 0.25              # looks entirely healthy
    assert portfolio.by_class("C").overdraft_ratio > 3.0   # is not


def test_unknown_class_lookup_raises():
    portfolio = evaluate_portfolio([ClassInputs("A", 1, 8, 0.5, 0.02, demand=1)])
    with pytest.raises(KeyError):
        portfolio.by_class("C")


def test_worst_is_none_when_nothing_is_budgetable():
    portfolio = evaluate_portfolio([ClassInputs("D", 6, 8, 0.55, None, demand=0)])
    assert portfolio.worst is None


# ---------------------------------------------------------------------------
# Inverse calculations
# ---------------------------------------------------------------------------


def test_cost_for_target_inverts_the_formula():
    target = cost_for_target(6, 8, 0.55, 70, 1.0)
    assert target == pytest.approx(26.4 / 70)
    # Feeding it back gives exactly O = 1.0.
    assert verification_budget(6, 8, 0.55, target) == pytest.approx(70)


def test_cost_for_target_reports_the_readme_figure():
    target = cost_for_target(6, 8, 0.55, 70, 1.0)
    assert target == pytest.approx(0.377, abs=0.001)
    assert (1 - target / 1.25) == pytest.approx(0.698, abs=0.001)


def test_cost_for_target_is_none_when_agent_check_cost_alone_exceeds_capacity():
    assert cost_for_target(6, 8, 0.55, 70, 1.0, containment=0.5, agent_check_cost=1.0) is None


def test_cost_for_target_with_no_demand():
    assert cost_for_target(6, 8, 0.55, 0) is None


def test_cost_for_target_with_no_capacity():
    assert cost_for_target(0, 8, 0.55, 70) is None


def test_cost_for_target_rejects_non_positive_target():
    with pytest.raises(BudgetError):
        cost_for_target(6, 8, 0.55, 70, target_ratio=0)


def test_reviewers_for_target_reports_the_readme_figure():
    needed = reviewers_for_target(8, 0.55, 1.25, 70, 1.0)
    assert needed == pytest.approx(19.886, abs=0.01)


def test_reviewers_for_target_with_no_demand_is_zero():
    assert reviewers_for_target(8, 0.55, 1.25, 0) == 0.0


def test_reviewers_for_target_without_hours_is_unreachable():
    assert reviewers_for_target(0, 0.55, 1.25, 70) is None


def test_utilisation_for_target_is_none_when_over_one():
    """Class C at 3.3x cannot be fixed by protecting review time."""
    assert utilisation_for_target(6, 8, 1.25, 70, 1.0) is None


def test_utilisation_for_target_when_reachable():
    result = utilisation_for_target(6, 8, 1.25, 20, 1.0)
    assert result is not None and 0 < result <= 1.0


def test_utilisation_for_target_with_no_reviewers():
    assert utilisation_for_target(0, 8, 1.25, 70) is None


def test_reclassification_share_matches_the_readme():
    share = reclassification_share(70, 21.12, 1.0)
    assert share == pytest.approx(0.698, abs=0.001)


def test_reclassification_share_is_zero_when_in_budget():
    assert reclassification_share(10, 21.12) == 0.0


def test_reclassification_share_with_no_demand():
    assert reclassification_share(0, 21.12) == 0.0


# ---------------------------------------------------------------------------
# Sensitivity
# ---------------------------------------------------------------------------


def test_cost_sensitivity_is_monotonic():
    inputs = ClassInputs("C", 6, 8, 0.55, 1.25, demand=70)
    points = cost_sensitivity(inputs, (1.0, 0.5, 0.25))
    assert [p.budget for p in points] == sorted(p.budget for p in points)
    assert points[0].overdraft_ratio == pytest.approx(3.3144, rel=1e-4)
    assert points[1].overdraft_ratio == pytest.approx(3.3144 / 2, rel=1e-4)


def test_cost_sensitivity_crosses_into_budget():
    inputs = ClassInputs("C", 6, 8, 0.55, 1.25, demand=70)
    points = cost_sensitivity(inputs)
    assert any(p.status == "overdraft" for p in points)
    assert any(p.status == "in_budget" for p in points)


def test_cost_sensitivity_is_empty_for_class_d():
    assert cost_sensitivity(ClassInputs("D", 6, 8, 0.55, None)) == ()


def test_cost_sensitivity_rejects_non_positive_multipliers():
    with pytest.raises(BudgetError):
        cost_sensitivity(ClassInputs("C", 6, 8, 0.55, 1.25), (0.0,))
