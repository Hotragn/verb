"""Silent drift: floor derivation, rate, trend, secondary signals."""

from __future__ import annotations

import pytest

from vb.drift import (
    Approval,
    Floor,
    batch_bursts,
    drift_rate,
    drift_report,
    floor_from_baseline,
    trend_label,
    variance_collapse,
)


# ---------------------------------------------------------------------------
# Floor derivation
# ---------------------------------------------------------------------------


def test_floor_uses_the_p10_of_the_calibrated_baseline():
    baseline = [0.2, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0]
    floor = floor_from_baseline(baseline)
    assert floor.hours == pytest.approx(0.29)
    assert floor.binding_term == "baseline_percentile"
    assert floor.sample_size == 10


def test_reading_floor_binds_when_the_baseline_is_too_low():
    """A floor on the floor, for when the baseline was itself collected under pressure."""
    baseline = [0.001] * 30
    floor = floor_from_baseline(baseline, median_artifact_words=700)
    assert floor.hours == pytest.approx(700 / 240 / 60)
    assert floor.binding_term == "reading"


def test_baseline_binds_when_it_exceeds_the_reading_floor():
    floor = floor_from_baseline([0.3] * 30, median_artifact_words=700)
    assert floor.binding_term == "baseline_percentile"
    assert floor.hours == pytest.approx(0.3)


def test_baseline_drift_rate_is_derived_from_the_percentile():
    """A P10 floor yields SDR around 0.10 when nothing is wrong, by construction."""
    assert floor_from_baseline([1.0] * 10).baseline_drift_rate == 0.10
    assert floor_from_baseline([1.0] * 10, percentile_rank=5.0).baseline_drift_rate == 0.05


def test_empty_baseline_raises_with_the_collection_requirement():
    with pytest.raises(ValueError, match="30 observed reviews"):
        floor_from_baseline([])


def test_negative_artifact_words_rejected():
    with pytest.raises(ValueError, match="must not be negative"):
        floor_from_baseline([1.0], median_artifact_words=-5)


def test_zero_reading_speed_rejected():
    with pytest.raises(ValueError, match="reading_wpm"):
        floor_from_baseline([1.0], reading_wpm=0)


def test_floor_minutes_helper():
    assert floor_from_baseline([0.5] * 10).minutes == pytest.approx(30.0)


def test_p10_not_median_the_metric_would_be_discarded_otherwise():
    baseline = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    p10 = floor_from_baseline(baseline, percentile_rank=10.0).hours
    p50 = floor_from_baseline(baseline, percentile_rank=50.0).hours
    # A median floor would flag half of all genuine reviews.
    assert drift_rate(baseline, p10) == pytest.approx(0.0, abs=0.1)
    assert drift_rate(baseline, p50) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Rate
# ---------------------------------------------------------------------------


def test_drift_rate_counts_approvals_below_the_floor():
    assert drift_rate([0.1, 0.2, 0.5, 0.9], 0.3) == 0.5


def test_drift_rate_of_empty_is_zero():
    assert drift_rate([], 0.3) == 0.0


def test_drift_rate_is_strict_below_not_at():
    assert drift_rate([0.3, 0.3], 0.3) == 0.0


def test_negative_floor_rejected():
    with pytest.raises(ValueError, match="must not be negative"):
        drift_rate([1.0], -0.1)


# ---------------------------------------------------------------------------
# Trend
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "slope,expected",
    [(0.05, "rising"), (0.021, "rising"), (0.02, "flat"), (0.0, "flat"),
     (-0.02, "flat"), (-0.021, "falling"), (-0.5, "falling")],
)
def test_trend_labels(slope, expected):
    assert trend_label(slope) == expected


def test_trend_needs_three_periods():
    approvals = [Approval(period=p, duration_hours=0.1) for p in (1, 2)]
    report = drift_report(approvals, 0.3)
    assert report.trend == "insufficient_data"
    assert report.slope == 0.0


# ---------------------------------------------------------------------------
# Secondary signals
# ---------------------------------------------------------------------------


def test_variance_collapse_flags_uniform_reviews():
    cv, collapsed = variance_collapse([1.0, 1.01, 0.99, 1.0, 1.02])
    assert collapsed
    assert cv < 0.15


def test_variance_collapse_does_not_flag_normal_spread():
    _, collapsed = variance_collapse([0.5, 1.2, 2.4, 0.8, 3.1])
    assert not collapsed


def test_variance_collapse_needs_at_least_three_values():
    _, collapsed = variance_collapse([1.0, 1.0])
    assert not collapsed


def test_batch_bursts_detects_a_run_of_approvals():
    approvals = [
        Approval(1, 0.05, "u-1", 1000.0),
        Approval(1, 0.05, "u-1", 1015.0),
        Approval(1, 0.05, "u-1", 1030.0),
        Approval(1, 0.05, "u-1", 5000.0),
    ]
    count, inside = batch_bursts(approvals)
    assert count == 1
    assert inside == 3


def test_batch_bursts_ignores_approvals_by_different_reviewers():
    approvals = [
        Approval(1, 0.05, "u-1", 1000.0),
        Approval(1, 0.05, "u-2", 1005.0),
        Approval(1, 0.05, "u-3", 1010.0),
    ]
    assert batch_bursts(approvals) == (0, 0)


def test_batch_bursts_ignores_events_without_timestamps():
    approvals = [Approval(1, 0.05, "u-1", None) for _ in range(5)]
    assert batch_bursts(approvals) == (0, 0)


def test_batch_bursts_requires_min_count_of_two():
    with pytest.raises(ValueError, match="at least 2"):
        batch_bursts([], min_count=1)


def test_batch_bursts_finds_two_separate_groups():
    approvals = [Approval(1, 0.05, "u-1", t) for t in (0, 10, 20, 5000, 5010, 5020)]
    count, inside = batch_bursts(approvals)
    assert count == 2
    assert inside == 6


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------


def _synthetic(drift_counts, per_period=50, floor=0.3):
    approvals = []
    for period, drifting in enumerate(drift_counts, start=1):
        for i in range(per_period):
            duration = floor * 0.4 if i < drifting else floor * 3.0 + (i % 7) * 0.11
            approvals.append(Approval(period, duration, f"u-{i % 5}", float(period * 10000 + i * 300)))
    return approvals


def test_report_computes_per_period_and_overall_rates():
    report = drift_report(_synthetic([5, 5, 5]), 0.3, "C")
    assert len(report.periods) == 3
    assert all(p.drift_rate == pytest.approx(0.1) for p in report.periods)
    assert report.drift_rate == pytest.approx(0.1)
    assert report.excess_drift == pytest.approx(0.0)
    assert report.trend == "flat"
    assert report.healthy


def test_report_detects_rising_drift():
    report = drift_report(_synthetic([5, 8, 12, 17, 23, 30]), 0.3, "C")
    assert report.trend == "rising"
    assert report.slope > 0.02
    assert report.diagnostic_signature
    assert not report.healthy


def test_report_detects_falling_drift():
    report = drift_report(_synthetic([30, 23, 17, 12, 8, 5]), 0.3, "C")
    assert report.trend == "falling"
    assert report.slope < -0.02


def test_excess_drift_is_the_signal_not_sdr():
    report = drift_report(_synthetic([5, 5, 5]), 0.3)
    assert report.drift_rate == pytest.approx(0.10)
    assert report.excess_drift == pytest.approx(0.0)   # healthy, despite SDR of 0.10


def test_excess_drift_never_goes_negative():
    report = drift_report(_synthetic([0, 0, 0]), 0.3)
    assert report.drift_rate == 0.0
    assert report.excess_drift == 0.0


def test_report_accepts_a_floor_object_and_uses_its_baseline():
    floor = floor_from_baseline([0.3] * 30, percentile_rank=5.0)
    report = drift_report(_synthetic([5, 5, 5]), floor)
    assert report.floor.baseline_drift_rate == 0.05
    assert report.excess_drift == pytest.approx(0.05)


def test_report_accepts_a_bare_number_and_assumes_a_p10_baseline():
    report = drift_report(_synthetic([5, 5, 5]), 0.3)
    assert report.floor.binding_term == "supplied"
    assert report.floor.baseline_drift_rate == 0.10


def test_report_with_no_approvals():
    report = drift_report([], 0.3, "C")
    assert report.n == 0
    assert report.periods == ()
    assert report.trend == "insufficient_data"
    assert report.secondary.burst_share == 0.0


def test_periods_sort_numerically_then_lexically():
    approvals = [Approval(p, 1.0) for p in (10, 2, 1)]
    report = drift_report(approvals, 0.3)
    assert [p.period for p in report.periods] == [1, 2, 10]

    approvals = [Approval(p, 1.0) for p in ("2026-W35", "2026-W33", "2026-W34")]
    report = drift_report(approvals, 0.3)
    assert [p.period for p in report.periods] == ["2026-W33", "2026-W34", "2026-W35"]


def test_report_carries_the_secondary_signals():
    report = drift_report(_synthetic([5, 5, 5]), 0.3)
    assert report.secondary.coefficient_of_variation > 0
    assert isinstance(report.secondary.variance_collapsed, bool)


# ---------------------------------------------------------------------------
# The PMO-40 shape, reproduced from constants rather than from the bundle
# ---------------------------------------------------------------------------


def test_the_pmo40_drift_curve_rises_at_the_documented_slope():
    approvals_per_week = [24, 25, 26, 28, 31, 34, 38, 44]
    drift_per_week = [3, 4, 5, 7, 10, 13, 17, 23]
    approvals = []
    for week, (total, drifting) in enumerate(zip(approvals_per_week, drift_per_week), start=1):
        for i in range(total):
            approvals.append(Approval(week, 0.12 if i < drifting else 1.25))

    report = drift_report(approvals, 0.318, "C")
    assert report.periods[0].drift_rate == pytest.approx(0.125)
    assert report.periods[-1].drift_rate == pytest.approx(0.523, abs=0.001)
    assert report.slope == pytest.approx(0.058, abs=0.002)
    assert report.trend == "rising"
    # Genuine reviews are pinned at the budget of 21 per week throughout.
    for total, drifting in zip(approvals_per_week, drift_per_week):
        assert total - drifting == 21
