"""Silent drift detection.

Silent drift is approval without verification. It is measured by review duration
against a per-class floor, where the floor is the line below which a genuine
review could not physically have happened.

The exact calculation is in spec/metrics.md section 3. Two things about it are
easy to get wrong and are handled here explicitly:

1. A P10 floor produces SDR around 0.10 when nothing is wrong, by construction.
   The signal is the excess over that baseline, and the baseline is derived from
   the percentile rather than hard-coded, so the two cannot drift apart.
2. SDR is never used for individual performance management. The moment it is,
   durations become a thing people manage rather than a thing you measure.
   Nothing in this module aggregates by person except the secondary signals,
   which exist to detect patterns and not to attribute them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from ._stats import (
    coefficient_of_variation,
    mean,
    median,
    ols_slope,
    percentile,
)

__all__ = [
    "Approval",
    "Floor",
    "PeriodDrift",
    "SecondarySignals",
    "DriftReport",
    "DEFAULT_PERCENTILE_RANK",
    "DEFAULT_READING_WPM",
    "TREND_THRESHOLD",
    "CV_COLLAPSE_THRESHOLD",
    "floor_from_baseline",
    "drift_rate",
    "trend_label",
    "variance_collapse",
    "batch_bursts",
    "drift_report",
]

#: P10 of a calibrated baseline. Conservative "nobody genuinely checking goes
#: faster than this" line. Not the median: the median would flag half of all
#: genuine reviews and the metric would be discarded within a month, correctly.
DEFAULT_PERCENTILE_RANK = 10.0

#: Words per minute, skim-to-comprehend on technical material. Used for the
#: physical reading floor, which is a floor on the floor.
DEFAULT_READING_WPM = 240.0

#: Drift fraction per period. Above this is rising, below the negative is falling.
TREND_THRESHOLD = 0.02

#: Coefficient of variation below this means reviews have become uniform.
CV_COLLAPSE_THRESHOLD = 0.15

#: Approvals by one reviewer inside this window, at or above BURST_MIN_COUNT.
BURST_WINDOW_SECONDS = 60.0
BURST_MIN_COUNT = 3


@dataclass(frozen=True)
class Approval:
    """One approval event.

    Only approvals count. A fast rejection is often a good rejection, because the
    reviewer spotted something immediately, and counting rejections would penalise
    exactly the behaviour you want.

    Attributes:
        period: Period label. Anything sortable and comparable.
        duration_hours: Idle-trimmed hours from artifact-open to approval-submit.
        reviewer_id: Used only for burst detection. Never aggregated into SDR.
        submitted_at: Epoch seconds, optional. Needed only for burst detection.
    """

    period: str | int
    duration_hours: float
    reviewer_id: str | None = None
    submitted_at: float | None = None


@dataclass(frozen=True)
class Floor:
    """A derived per-class floor, with both terms shown.

    Showing both terms matters: if the reading floor is binding, the calibrated
    baseline was collected under time pressure and is itself suspect.
    """

    hours: float
    baseline_percentile_hours: float
    reading_floor_hours: float
    percentile_rank: float
    baseline_drift_rate: float
    sample_size: int
    binding_term: str

    @property
    def minutes(self) -> float:
        return self.hours * 60.0


@dataclass(frozen=True)
class PeriodDrift:
    """Drift for one period."""

    period: str | int
    n: int
    drift_count: int
    drift_rate: float
    excess_drift: float
    mean_duration_hours: float
    median_duration_hours: float
    coefficient_of_variation: float


@dataclass(frozen=True)
class SecondarySignals:
    """Reported alongside SDR, never used as the metric.

    Patterns have innocent explanations often enough that acting on them directly
    would be wrong.
    """

    coefficient_of_variation: float
    variance_collapsed: bool
    burst_count: int
    approvals_in_bursts: int
    burst_share: float


@dataclass(frozen=True)
class DriftReport:
    """The full silent drift picture for one class."""

    decision_class: str
    floor: Floor
    periods: tuple[PeriodDrift, ...]
    n: int
    drift_count: int
    drift_rate: float
    excess_drift: float
    slope: float
    trend: str
    secondary: SecondarySignals

    @property
    def healthy(self) -> bool:
        """Excess drift within 0.05 of the baseline and not rising."""
        return self.excess_drift <= 0.05 and self.trend != "rising"

    @property
    def diagnostic_signature(self) -> bool:
        """Rising drift. Read next to the overdraft ratio.

        Rising drift with O > 1 is what this framework predicts, and it lags the
        overdraft by a month or two because backlog absorbs the overdraft first.
        """
        return self.trend == "rising"


def floor_from_baseline(
    baseline_durations_hours: Sequence[float],
    median_artifact_words: float | None = None,
    percentile_rank: float = DEFAULT_PERCENTILE_RANK,
    reading_wpm: float = DEFAULT_READING_WPM,
) -> Floor:
    """Derive the per-class floor.

        f_X = max( P10(calibrated baseline), words / 240 / 60 )

    ``baseline_durations_hours`` must come from a calibrated period: at least 30
    reviews per class, reviewers observed, each confirming afterwards that they
    genuinely checked. Durations from a period you have not calibrated will
    produce a floor that ratifies whatever is already happening.

    Raises:
        ValueError: if the baseline is empty.
    """
    if not baseline_durations_hours:
        raise ValueError(
            "cannot derive a floor from an empty baseline. Collect at least 30 "
            "observed reviews per class, and confirm afterwards that each was genuine."
        )
    if reading_wpm <= 0:
        raise ValueError("reading_wpm must be positive")

    baseline_term = percentile(baseline_durations_hours, percentile_rank)
    reading_term = 0.0
    if median_artifact_words is not None:
        if median_artifact_words < 0:
            raise ValueError("median_artifact_words must not be negative")
        reading_term = median_artifact_words / reading_wpm / 60.0

    hours = max(baseline_term, reading_term)
    binding = "reading" if reading_term > baseline_term else "baseline_percentile"

    return Floor(
        hours=hours,
        baseline_percentile_hours=baseline_term,
        reading_floor_hours=reading_term,
        percentile_rank=percentile_rank,
        baseline_drift_rate=percentile_rank / 100.0,
        sample_size=len(baseline_durations_hours),
        binding_term=binding,
    )


def drift_rate(durations_hours: Sequence[float], floor_hours: float) -> float:
    """Fraction of approvals below the floor. Returns 0.0 for an empty sequence."""
    if floor_hours < 0:
        raise ValueError("floor_hours must not be negative")
    if not durations_hours:
        return 0.0
    below = sum(1 for d in durations_hours if d < floor_hours)
    return below / len(durations_hours)


def trend_label(slope: float, threshold: float = TREND_THRESHOLD) -> str:
    """Map an OLS slope to rising, flat or falling."""
    if slope > threshold:
        return "rising"
    if slope < -threshold:
        return "falling"
    return "flat"


def variance_collapse(
    durations_hours: Sequence[float], threshold: float = CV_COLLAPSE_THRESHOLD
) -> tuple[float, bool]:
    """Coefficient of variation and whether it has collapsed.

    Real reviews are not uniform, because real decisions differ in difficulty.
    Uniformity means the duration is being set by something other than the
    decision, usually a habit or a target.
    """
    cv = coefficient_of_variation(durations_hours)
    return cv, (len(durations_hours) >= 3 and cv < threshold)


def batch_bursts(
    approvals: Sequence[Approval],
    window_seconds: float = BURST_WINDOW_SECONDS,
    min_count: int = BURST_MIN_COUNT,
) -> tuple[int, int]:
    """Count burst groups and the approvals inside them.

    A burst is ``min_count`` or more approvals by the same reviewer within
    ``window_seconds``. Occasionally legitimate, when a reviewer queued several
    artifacts, read them all, and then clicked through. Never legitimate as a
    sustained pattern.

    Returns:
        (burst_count, approvals_inside_bursts)
    """
    if min_count < 2:
        raise ValueError("min_count must be at least 2")

    by_reviewer: dict[str, list[float]] = {}
    for approval in approvals:
        if approval.reviewer_id is None or approval.submitted_at is None:
            continue
        by_reviewer.setdefault(approval.reviewer_id, []).append(approval.submitted_at)

    bursts = 0
    inside = 0
    for stamps in by_reviewer.values():
        stamps.sort()
        start = 0
        while start < len(stamps):
            end = start
            while end + 1 < len(stamps) and stamps[end + 1] - stamps[start] <= window_seconds:
                end += 1
            group = end - start + 1
            if group >= min_count:
                bursts += 1
                inside += group
                start = end + 1
            else:
                start += 1
    return bursts, inside


def drift_report(
    approvals: Iterable[Approval],
    floor: Floor | float,
    decision_class: str = "",
    trend_threshold: float = TREND_THRESHOLD,
) -> DriftReport:
    """Full drift report: per-period rates, trend, and the secondary signals.

    ``floor`` may be a :class:`Floor` or a bare number of hours. Passing a bare
    number means the baseline drift rate defaults to 0.10, which is right only if
    the floor came from a P10. Pass a :class:`Floor` if you can.
    """
    events = list(approvals)

    if isinstance(floor, Floor):
        resolved = floor
    else:
        resolved = Floor(
            hours=float(floor),
            baseline_percentile_hours=float(floor),
            reading_floor_hours=0.0,
            percentile_rank=DEFAULT_PERCENTILE_RANK,
            baseline_drift_rate=DEFAULT_PERCENTILE_RANK / 100.0,
            sample_size=0,
            binding_term="supplied",
        )

    baseline = resolved.baseline_drift_rate

    grouped: dict[str | int, list[Approval]] = {}
    for event in events:
        grouped.setdefault(event.period, []).append(event)

    periods: list[PeriodDrift] = []
    for period in sorted(grouped, key=_period_sort_key):
        bucket = grouped[period]
        durations = [e.duration_hours for e in bucket]
        rate = drift_rate(durations, resolved.hours)
        cv, _ = variance_collapse(durations)
        periods.append(
            PeriodDrift(
                period=period,
                n=len(bucket),
                drift_count=sum(1 for d in durations if d < resolved.hours),
                drift_rate=rate,
                excess_drift=max(0.0, rate - baseline),
                mean_duration_hours=mean(durations),
                median_duration_hours=median(durations),
                coefficient_of_variation=cv,
            )
        )

    all_durations = [e.duration_hours for e in events]
    overall_rate = drift_rate(all_durations, resolved.hours)

    if len(periods) >= 3:
        slope = ols_slope([float(i) for i in range(len(periods))], [p.drift_rate for p in periods])
        trend = trend_label(slope, trend_threshold)
    else:
        slope = 0.0
        trend = "insufficient_data"

    cv_all, collapsed = variance_collapse(all_durations)
    burst_count, in_bursts = batch_bursts(events)

    return DriftReport(
        decision_class=decision_class,
        floor=resolved,
        periods=tuple(periods),
        n=len(events),
        drift_count=sum(1 for d in all_durations if d < resolved.hours),
        drift_rate=overall_rate,
        excess_drift=max(0.0, overall_rate - baseline),
        slope=slope,
        trend=trend,
        secondary=SecondarySignals(
            coefficient_of_variation=cv_all,
            variance_collapsed=collapsed,
            burst_count=burst_count,
            approvals_in_bursts=in_bursts,
            burst_share=(in_bursts / len(events)) if events else 0.0,
        ),
    )


def _period_sort_key(period: str | int) -> tuple[int, float, str]:
    """Sort periods numerically where possible, lexically otherwise."""
    if isinstance(period, (int, float)):
        return (0, float(period), "")
    text = str(period)
    try:
        return (0, float(text), "")
    except ValueError:
        return (1, 0.0, text)
