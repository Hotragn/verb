"""Statistical helpers. Small, shared, and load-bearing."""

from __future__ import annotations

import pytest

from vb._stats import (
    coefficient_of_variation,
    cohens_kappa,
    iqr,
    mean,
    median,
    ols_slope,
    percentile,
    stdev,
    wilson_interval,
)


# ---------------------------------------------------------------------------
# Central tendency
# ---------------------------------------------------------------------------


def test_median_odd_and_even():
    assert median([3, 1, 2]) == 2
    assert median([4, 1, 2, 3]) == 2.5


def test_median_of_empty_is_zero():
    assert median([]) == 0.0


def test_mean_of_empty_is_zero():
    assert mean([]) == 0.0


def test_median_not_mean_for_a_right_skewed_distribution():
    """c-hat is the median because the mean flatters the budget."""
    durations = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 6.0]
    assert median(durations) == pytest.approx(0.9)
    assert mean(durations) > median(durations)


# ---------------------------------------------------------------------------
# Percentile
# ---------------------------------------------------------------------------


def test_percentile_matches_linear_interpolation():
    values = [1, 2, 3, 4, 5]
    assert percentile(values, 0) == 1
    assert percentile(values, 100) == 5
    assert percentile(values, 50) == 3
    assert percentile(values, 25) == 2
    assert percentile(values, 10) == pytest.approx(1.4)


def test_percentile_of_single_value():
    assert percentile([7.0], 10) == 7.0


def test_percentile_of_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        percentile([], 10)


@pytest.mark.parametrize("rank", [-1, 101])
def test_percentile_rank_outside_range_raises(rank):
    with pytest.raises(ValueError, match="0 to 100"):
        percentile([1, 2, 3], rank)


def test_percentile_is_order_independent():
    assert percentile([5, 1, 3, 2, 4], 25) == percentile([1, 2, 3, 4, 5], 25)


def test_iqr():
    low, high = iqr([1, 2, 3, 4, 5])
    assert (low, high) == (2, 4)


def test_iqr_of_empty():
    assert iqr([]) == (0.0, 0.0)


# ---------------------------------------------------------------------------
# Dispersion
# ---------------------------------------------------------------------------


def test_stdev_of_short_sequences_is_zero():
    assert stdev([]) == 0.0
    assert stdev([5.0]) == 0.0


def test_coefficient_of_variation():
    assert coefficient_of_variation([10, 10, 10]) == 0.0
    assert coefficient_of_variation([]) == 0.0
    assert coefficient_of_variation([1, 2, 3, 4]) > 0.0


def test_cv_zero_mean_returns_zero():
    assert coefficient_of_variation([0.0, 0.0]) == 0.0


# ---------------------------------------------------------------------------
# Trend
# ---------------------------------------------------------------------------


def test_ols_slope_on_a_straight_line():
    assert ols_slope([0, 1, 2, 3], [0, 2, 4, 6]) == pytest.approx(2.0)


def test_ols_slope_on_flat_data_is_zero():
    assert ols_slope([0, 1, 2, 3], [5, 5, 5, 5]) == pytest.approx(0.0)


def test_ols_slope_with_no_x_variance_is_zero():
    assert ols_slope([2, 2, 2], [1, 5, 9]) == 0.0


def test_ols_slope_with_fewer_than_two_points_is_zero():
    assert ols_slope([1], [1]) == 0.0


def test_ols_slope_length_mismatch_raises():
    with pytest.raises(ValueError, match="equal-length"):
        ols_slope([1, 2], [1])


def test_ols_slope_reproduces_the_pmo40_drift_trend():
    sdr = [0.125, 0.160, 0.192, 0.250, 0.323, 0.382, 0.447, 0.523]
    slope = ols_slope(list(range(8)), sdr)
    assert slope == pytest.approx(0.0579, abs=0.001)


# ---------------------------------------------------------------------------
# Wilson interval
# ---------------------------------------------------------------------------


def test_wilson_interval_brackets_the_point_estimate():
    low, high = wilson_interval(70, 100)
    assert low < 0.70 < high


def test_wilson_interval_stays_inside_zero_and_one_at_the_extremes():
    """The reason Wilson is used rather than the normal approximation."""
    low, high = wilson_interval(100, 100)
    assert 0.0 <= low <= 1.0 and high == pytest.approx(1.0)
    low, high = wilson_interval(0, 100)
    assert low == pytest.approx(0.0) and 0.0 <= high <= 1.0


def test_wilson_interval_narrows_with_more_trials():
    small = wilson_interval(7, 10)
    large = wilson_interval(700, 1000)
    assert (large[1] - large[0]) < (small[1] - small[0])


def test_wilson_interval_with_no_trials_is_maximally_uncertain():
    assert wilson_interval(0, 0) == (0.0, 1.0)


def test_wilson_lower_bound_is_below_the_point_estimate():
    """The budget uses the lower bound, never the point estimate."""
    successes, trials = 170, 240
    low, _ = wilson_interval(successes, trials)
    assert low < successes / trials


@pytest.mark.parametrize("successes,trials", [(-1, 10), (11, 10)])
def test_wilson_interval_rejects_impossible_counts(successes, trials):
    with pytest.raises(ValueError):
        wilson_interval(successes, trials)


def test_wilson_interval_rejects_negative_trials():
    with pytest.raises(ValueError, match="negative"):
        wilson_interval(0, -1)


# ---------------------------------------------------------------------------
# Cohen's kappa
# ---------------------------------------------------------------------------


def test_kappa_of_perfect_agreement():
    assert cohens_kappa(["A", "B", "C", "D"], ["A", "B", "C", "D"]) == pytest.approx(1.0)


def test_kappa_of_total_disagreement_is_negative():
    assert cohens_kappa(["A", "A", "B", "B"], ["B", "B", "A", "A"]) < 0


def test_kappa_discounts_chance_agreement():
    """Two classifiers who always say A agree perfectly and learn nothing."""
    assert cohens_kappa(["A"] * 10, ["A"] * 10) == pytest.approx(1.0)
    # One dissent against an otherwise constant marginal drives kappa down hard.
    assert cohens_kappa(["A"] * 9 + ["B"], ["A"] * 10) < 0.5


def test_kappa_on_a_realistic_sample_passes_gate_1():
    a = ["A"] * 18 + ["B"] * 16 + ["C"] * 13 + ["D"] * 3
    b = list(a)
    for index in (2, 9, 21, 28, 34, 41):
        b[index] = {"A": "B", "B": "C", "C": "B", "D": "D"}[b[index]]
    assert cohens_kappa(a, b) >= 0.70


def test_kappa_length_mismatch_raises():
    with pytest.raises(ValueError, match="equal-length"):
        cohens_kappa(["A"], ["A", "B"])


def test_kappa_of_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        cohens_kappa([], [])
