"""Small statistical helpers, standard library only.

Everything here is used by more than one module. Nothing here is specific to the
verification budget; it is arithmetic that would otherwise be copied around.
"""

from __future__ import annotations

import math
from typing import Sequence

__all__ = [
    "median",
    "percentile",
    "mean",
    "stdev",
    "coefficient_of_variation",
    "ols_slope",
    "wilson_interval",
    "cohens_kappa",
    "iqr",
]


def mean(values: Sequence[float]) -> float:
    """Arithmetic mean. Returns 0.0 for an empty sequence."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    """Median by the usual midpoint convention. Returns 0.0 for an empty sequence."""
    if not values:
        return 0.0
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def percentile(values: Sequence[float], rank: float) -> float:
    """Percentile by linear interpolation between order statistics.

    ``rank`` is 0 to 100. This is the same convention as numpy's default
    ``linear`` method, so results match if anyone cross-checks with numpy.
    """
    if not values:
        raise ValueError("percentile of an empty sequence")
    if not 0.0 <= rank <= 100.0:
        raise ValueError(f"rank must be within 0 to 100, got {rank}")

    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])

    position = (len(ordered) - 1) * (rank / 100.0)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[int(position)])
    weight = position - lower
    return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def iqr(values: Sequence[float]) -> tuple[float, float]:
    """Interquartile range as (P25, P75).

    Reported alongside every measured verification cost. A class whose IQR spans
    an order of magnitude is not one class, and the fix is to split the decision
    type rather than to average it.
    """
    if not values:
        return (0.0, 0.0)
    return (percentile(values, 25.0), percentile(values, 75.0))


def stdev(values: Sequence[float]) -> float:
    """Sample standard deviation. Returns 0.0 for fewer than two values."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def coefficient_of_variation(values: Sequence[float]) -> float:
    """Standard deviation over mean.

    Below 0.15 within a class and period means review durations have become
    uniform, and real reviews are not uniform because real decisions differ in
    difficulty. Secondary drift signal, never the metric itself.
    """
    m = mean(values)
    if m == 0.0:
        return 0.0
    return stdev(values) / m


def ols_slope(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Ordinary least squares slope of y on x.

    Used for the silent drift trend. Returns 0.0 when x has no variance, which
    happens with a single period and is the right answer for a trend question
    that cannot be asked.
    """
    if len(xs) != len(ys):
        raise ValueError("ols_slope needs equal-length sequences")
    if len(xs) < 2:
        return 0.0

    x_bar = mean(xs)
    y_bar = mean(ys)
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0.0:
        return 0.0
    numerator = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys))
    return numerator / denominator


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion.

    Used for containment k. The normal approximation misbehaves near 0 and 1,
    which is exactly where a containment measurement sits, so Wilson is the
    right choice rather than a refinement.

    The budget uses the lower bound, never the point estimate.
    """
    if trials < 0:
        raise ValueError("trials must not be negative")
    if not 0 <= successes <= trials:
        raise ValueError(f"successes {successes} outside 0 to trials {trials}")
    if trials == 0:
        return (0.0, 1.0)

    n = float(trials)
    p_hat = successes / n
    z2 = z * z
    denominator = 1.0 + z2 / n
    centre = (p_hat + z2 / (2.0 * n)) / denominator
    spread = (z * math.sqrt(p_hat * (1.0 - p_hat) / n + z2 / (4.0 * n * n))) / denominator
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def cohens_kappa(a: Sequence[str], b: Sequence[str]) -> float:
    """Cohen's kappa between two classifiers over the same items.

    Gate 1 passes at kappa >= 0.70. Below that the disagreement is in the rubric
    rather than in the people, and retraining classifiers will not fix it.

    Returns 1.0 when both classifiers used a single identical label throughout,
    where chance agreement is 1.0 and the usual formula is undefined.
    """
    if len(a) != len(b):
        raise ValueError("cohens_kappa needs equal-length sequences")
    if not a:
        raise ValueError("cohens_kappa of empty sequences")

    n = len(a)
    observed = sum(1 for x, y in zip(a, b) if x == y) / n

    labels = set(a) | set(b)
    expected = 0.0
    for label in labels:
        p_a = sum(1 for x in a if x == label) / n
        p_b = sum(1 for y in b if y == label) / n
        expected += p_a * p_b

    if expected >= 1.0:
        return 1.0 if observed >= 1.0 else 0.0
    return (observed - expected) / (1.0 - expected)
