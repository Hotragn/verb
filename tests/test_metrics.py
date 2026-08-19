"""The six metrics, from event logs."""

from __future__ import annotations

import pytest

from vb.metrics import (
    approvals_from_events,
    compute_all,
    compute_class,
    containment,
    demand_per_period,
    escalation_precision,
    measured_cost,
    reversal_latency,
)


# ---------------------------------------------------------------------------
# c-hat
# ---------------------------------------------------------------------------


def test_measured_cost_is_the_median_of_genuine_reviews():
    rows = [
        {"decision_class": "C", "idle_trimmed_seconds": 3600, "genuinely_checked": "true"},
        {"decision_class": "C", "idle_trimmed_seconds": 4500, "genuinely_checked": "true"},
        {"decision_class": "C", "idle_trimmed_seconds": 7200, "genuinely_checked": "true"},
    ]
    cost = measured_cost(rows, "C")
    assert cost is not None
    assert cost.hours == pytest.approx(1.25)
    assert cost.sample_size == 3


def test_observations_the_reviewer_says_were_not_genuine_are_discarded():
    """The step everybody skips, and the step that makes the number mean something."""
    rows = [
        {"decision_class": "C", "idle_trimmed_seconds": 4500, "genuinely_checked": "true"},
        {"decision_class": "C", "idle_trimmed_seconds": 4500, "genuinely_checked": "true"},
        {"decision_class": "C", "idle_trimmed_seconds": 60, "genuinely_checked": "false"},
        {"decision_class": "C", "idle_trimmed_seconds": 45, "genuinely_checked": "false"},
    ]
    cost = measured_cost(rows, "C")
    assert cost is not None
    assert cost.hours == pytest.approx(1.25)
    assert cost.discarded_not_genuine == 2


def test_measured_cost_accepts_boolean_flags():
    rows = [{"decision_class": "A", "idle_trimmed_seconds": 72, "genuinely_checked": True}]
    assert measured_cost(rows, "A").hours == pytest.approx(0.02)


def test_measured_cost_falls_back_to_raw_seconds():
    rows = [{"decision_class": "A", "raw_seconds": 72, "genuinely_checked": "yes"}]
    assert measured_cost(rows, "A").hours == pytest.approx(0.02)


def test_measured_cost_ignores_other_classes():
    rows = [
        {"decision_class": "A", "idle_trimmed_seconds": 72, "genuinely_checked": "true"},
        {"decision_class": "C", "idle_trimmed_seconds": 4500, "genuinely_checked": "true"},
    ]
    assert measured_cost(rows, "A").hours == pytest.approx(0.02)


def test_measured_cost_with_nothing_genuine_is_none():
    rows = [{"decision_class": "C", "idle_trimmed_seconds": 60, "genuinely_checked": "false"}]
    assert measured_cost(rows, "C") is None


def test_a_wide_interquartile_range_is_flagged_as_not_one_class():
    rows = [
        {"decision_class": "C", "idle_trimmed_seconds": s, "genuinely_checked": "true"}
        for s in (60, 90, 120, 3600, 18000, 36000, 40000)
    ]
    cost = measured_cost(rows, "C")
    assert cost.suspiciously_wide
    assert cost.spread_ratio > 10


# ---------------------------------------------------------------------------
# Demand
# ---------------------------------------------------------------------------


def test_demand_per_period_divides_by_periods():
    events = [{"decision_class": "C"} for _ in range(560)]
    assert demand_per_period(events, "C", 8) == 70.0


def test_demand_counts_only_the_named_class():
    events = [{"decision_class": "A"}] * 10 + [{"decision_class": "C"}] * 5
    assert demand_per_period(events, "C", 1) == 5.0


def test_demand_rejects_zero_periods():
    with pytest.raises(ValueError, match="at least 1"):
        demand_per_period([], "C", 0)


# ---------------------------------------------------------------------------
# Containment
# ---------------------------------------------------------------------------


def _verifier_events(offered, contained, known_bad=0, false_negatives=0, decision_class="A"):
    """Build a verifier-offered population with an exact containment and FNR.

    A known-bad decision the verifier rejects is still contained: it was closed
    without human involvement, with a machine-checkable reason. It is only a
    false negative when the verifier passed it.
    """
    assert known_bad <= contained <= offered
    assert false_negatives <= known_bad
    events = []
    for i in range(offered):
        if i < known_bad:
            slipped = i < false_negatives
            verdict, is_contained = ("pass", True) if slipped else ("reject", True)
        elif i < contained:
            verdict, is_contained = "pass", True
        else:
            verdict, is_contained = "cannot_decide", False
        events.append(
            {
                "decision_class": decision_class,
                "verifier_offered": True,
                "verifier_contained": is_contained,
                "verifier_verdict": verdict,
                "known_bad": i < known_bad,
            }
        )
    return events


def test_containment_with_no_verifier_is_zero():
    result = containment([{"decision_class": "C"}] * 10, "C")
    assert result.offered == 0
    assert result.budget_value == 0.0
    assert "No verifier" in result.note


def test_containment_uses_the_ci_lower_bound_not_the_point_estimate():
    events = _verifier_events(240, 170, known_bad=38, false_negatives=1)
    result = containment(events, "A")
    assert result.calibrated
    assert result.budget_value == result.ci95[0]
    assert result.budget_value < result.rate


def test_containment_without_known_bad_is_uncalibrated():
    """k reported without FNR is not a metric, it is a claim."""
    events = _verifier_events(240, 170)
    result = containment(events, "A")
    assert not result.calibrated
    assert result.budget_value == 0.0
    assert "unmeasured" in result.note


def test_containment_above_the_fnr_threshold_is_set_to_zero():
    events = _verifier_events(240, 170, known_bad=30, false_negatives=6)
    result = containment(events, "A")
    assert result.false_negative_rate == pytest.approx(0.2)
    assert not result.calibrated
    assert result.budget_value == 0.0
    assert "advisory annotation" in result.note


def test_a_verifier_that_passes_everything_looks_like_a_triumph_until_you_see_the_fnr():
    events = _verifier_events(200, 200, known_bad=40, false_negatives=40)  # passes all 40 bad ones
    result = containment(events, "A")
    assert result.rate == 1.0            # looks perfect
    assert result.false_negative_rate == 1.0
    assert result.budget_value == 0.0    # contributes nothing


def test_containment_can_be_forced_by_config():
    events = _verifier_events(240, 170)
    result = containment(events, "A", calibrated=True)
    assert result.calibrated
    assert result.budget_value > 0


def test_containment_reportable_string():
    assert "uncalibrated" in containment(_verifier_events(10, 5), "A").reportable
    calibrated = containment(_verifier_events(240, 170, 38, 1), "A")
    assert "CI95" in calibrated.reportable


# ---------------------------------------------------------------------------
# Escalation precision
# ---------------------------------------------------------------------------


def test_escalation_precision():
    events = [
        {"decision_class": "C", "escalated": True, "escalation_upheld": True},
        {"decision_class": "C", "escalated": True, "escalation_upheld": True},
        {"decision_class": "C", "escalated": True, "escalation_upheld": False},
        {"decision_class": "C", "escalated": True, "escalation_upheld": True},
        {"decision_class": "C", "escalated": False},
    ]
    result = escalation_precision(events, "C")
    assert result.escalations == 4
    assert result.precision == pytest.approx(0.75)
    assert result.passes


def test_escalation_precision_below_target_fails():
    events = [{"decision_class": "C", "escalated": True, "escalation_upheld": i < 2} for i in range(10)]
    result = escalation_precision(events, "C")
    assert result.precision == pytest.approx(0.2)
    assert not result.passes


def test_escalation_precision_with_no_escalations_is_none():
    result = escalation_precision([{"decision_class": "C", "escalated": False}], "C")
    assert result.precision is None
    assert not result.passes


def test_recall_gap_is_stated_rather_than_implied():
    note = escalation_precision([], "C").recall_note
    assert "not measured here" in note
    assert "probes" in note


# ---------------------------------------------------------------------------
# Reversal latency
# ---------------------------------------------------------------------------


def test_reversal_latency_median_and_p90():
    events = [
        {"decision_class": "C", "reversed": True, "reversed_after_hours": h,
         "reversed_after_cheap_until": h > 336}
        for h in (12, 24, 36, 48, 400)
    ]
    result = reversal_latency(events, "C")
    assert result.reversals == 5
    assert result.median_hours == pytest.approx(36)
    assert result.p90_hours == pytest.approx(259.2, abs=1)
    assert result.breach_rate == pytest.approx(0.2)


def test_high_breach_rate_means_the_reversal_field_is_fiction():
    events = [
        {"decision_class": "C", "reversed": True, "reversed_after_hours": 500,
         "reversed_after_cheap_until": True}
        for _ in range(5)
    ]
    result = reversal_latency(events, "C")
    assert result.breach_rate == 1.0
    assert result.reversal_field_unreliable


def test_reversal_latency_with_no_reversals():
    result = reversal_latency([{"decision_class": "C", "reversed": False}], "C")
    assert result.reversals == 0
    assert result.median_hours is None
    assert result.breach_rate is None
    assert not result.reversal_field_unreliable


def test_reversal_latency_only_sees_reversals_that_happened():
    assert "lower bound" in reversal_latency([], "C").note


# ---------------------------------------------------------------------------
# Approvals extraction
# ---------------------------------------------------------------------------


def test_approvals_exclude_rejections_because_a_fast_rejection_is_a_good_one():
    events = [
        {"decision_class": "C", "outcome": "approved", "idle_trimmed_seconds": 4500, "period": 1},
        {"decision_class": "C", "outcome": "rejected", "idle_trimmed_seconds": 30, "period": 1},
        {"decision_class": "C", "outcome": "queued", "period": 1},
    ]
    approvals = approvals_from_events(events, "C")
    assert len(approvals) == 1
    assert approvals[0].duration_hours == pytest.approx(1.25)


def test_approvals_skip_events_with_no_duration():
    events = [{"decision_class": "C", "outcome": "approved", "period": 1}]
    assert approvals_from_events(events, "C") == []


# ---------------------------------------------------------------------------
# Assembly, against the reference bundle
# ---------------------------------------------------------------------------


def test_compute_class_assembles_all_six(pmo40):
    entry = compute_class(pmo40, "C")
    assert entry.budget.overdraft_ratio == pytest.approx(3.31, abs=0.01)
    assert entry.drift is not None
    assert entry.containment.budget_value == 0.0
    assert entry.escalation.precision is not None
    assert entry.reversal.median_hours is not None
    assert entry.cost is not None


def test_compute_class_rejects_an_unknown_class(pmo40):
    with pytest.raises(KeyError):
        compute_class(pmo40, "Z")


def test_compute_all_orders_classes_a_to_d(pmo40):
    result = compute_all(pmo40)
    assert [c.decision_class for c in result.classes] == ["A", "B", "C", "D"]


def test_worst_class_is_c(pmo40):
    result = compute_all(pmo40)
    assert result.worst is not None
    assert result.worst.decision_class == "C"


def test_headline_is_one_line(pmo40):
    result = compute_all(pmo40)
    headline = result.by_class("C").headline
    assert "Class C" in headline and "overdraft" in headline


def test_class_d_headline_says_unbudgeted(pmo40):
    result = compute_all(pmo40)
    assert "unbudgeted" in result.by_class("D").headline


def test_metric_set_lookup_of_a_missing_class(pmo40):
    with pytest.raises(KeyError):
        compute_all(pmo40).by_class("Z")
