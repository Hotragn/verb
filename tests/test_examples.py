"""The PMO-40 bundle reproduces the figures the README and the talk quote.

If any of these fail, either the generator changed or the arithmetic changed, and
in both cases the README is now wrong. That is the point of the file.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from vb.gates import run_all
from vb.metrics import compute_all


# ---------------------------------------------------------------------------
# The headline
# ---------------------------------------------------------------------------


def test_class_c_reproduces_the_3_3x_overdraft(pmo40):
    """The figure from the talk. `vb budget --input examples/pmo40`."""
    budget = compute_all(pmo40).by_class("C").budget
    assert budget.overdraft_ratio == pytest.approx(3.31, abs=0.01)
    assert budget.status == "overdraft"


def test_the_class_c_budget_is_21_decisions_a_week(pmo40):
    budget = compute_all(pmo40).by_class("C").budget
    assert budget.budget == pytest.approx(21.12, abs=0.01)
    assert budget.demand == pytest.approx(70.0)
    assert budget.unverified_decisions == pytest.approx(48.88, abs=0.01)


def test_class_a_and_b_are_comfortable(pmo40):
    metrics = compute_all(pmo40)
    assert metrics.by_class("A").budget.status == "in_budget"
    assert metrics.by_class("B").budget.status == "in_budget"


def test_a_portfolio_average_would_hide_the_only_problem(pmo40):
    """The reason every metric in this framework is reported per class."""
    metrics = compute_all(pmo40)
    budgets = [c.budget for c in metrics.classes if c.budget.budget > 0]
    aggregate = sum(b.demand for b in budgets) / sum(b.budget for b in budgets)
    assert aggregate < 0.2
    assert metrics.by_class("C").budget.overdraft_ratio > 3.0


# ---------------------------------------------------------------------------
# Drift
# ---------------------------------------------------------------------------


def test_class_c_drift_rises_across_the_eight_weeks(pmo40):
    drift = compute_all(pmo40).by_class("C").drift
    assert drift is not None
    assert len(drift.periods) == 8
    assert drift.trend == "rising"
    assert drift.slope == pytest.approx(0.058, abs=0.005)
    assert drift.periods[0].drift_rate < 0.15
    assert drift.periods[-1].drift_rate > 0.50


def test_genuine_class_c_reviews_are_pinned_at_the_budget(pmo40):
    """The mechanism: everything approved above the budget line is drift."""
    drift = compute_all(pmo40).by_class("C").drift
    for period in drift.periods:
        assert period.n - period.drift_count == 21


def test_the_overdraft_becomes_backlog_before_it_becomes_drift(pmo40):
    """560 decisions produced, 250 approved. The rest are queued."""
    events = pmo40.events_for("C")
    assert len(events) == 560
    approved = [e for e in events if e.get("outcome") == "approved"]
    queued = [e for e in events if e.get("outcome") == "queued"]
    assert len(approved) == 250
    assert len(queued) == 310


def test_class_a_and_b_drift_sit_at_the_baseline(pmo40):
    metrics = compute_all(pmo40)
    for decision_class in ("A", "B"):
        drift = metrics.by_class(decision_class).drift
        assert drift is not None
        assert drift.excess_drift < 0.05
        assert drift.trend != "rising"


def test_batch_bursts_appear_as_class_c_drift_rises(pmo40):
    drift = compute_all(pmo40).by_class("C").drift
    assert drift.secondary.burst_count > 0


# ---------------------------------------------------------------------------
# Floors
# ---------------------------------------------------------------------------


def test_each_class_floor_comes_from_its_calibrated_baseline(pmo40):
    metrics = compute_all(pmo40)
    floors = {c.decision_class: c.drift.floor for c in metrics.classes if c.drift}
    assert floors["A"].hours == pytest.approx(0.008, abs=0.001)
    assert floors["C"].hours == pytest.approx(0.318, abs=0.001)
    assert floors["A"].sample_size == 44
    assert floors["C"].sample_size == 34


def test_the_reading_floor_binds_for_class_b(pmo40):
    """A floor on the floor, for when the baseline P10 is itself too low."""
    floor = compute_all(pmo40).by_class("B").drift.floor
    assert floor.binding_term == "reading"
    assert floor.hours == pytest.approx(700 / 240 / 60, abs=1e-4)


# ---------------------------------------------------------------------------
# Measured cost
# ---------------------------------------------------------------------------


def test_measured_c_matches_the_budgeted_c_within_gate_2_tolerance(pmo40):
    metrics = compute_all(pmo40)
    for decision_class, budgeted in (("A", 0.02), ("B", 0.15), ("C", 1.25)):
        cost = metrics.by_class(decision_class).cost
        assert cost is not None
        assert abs(cost.hours - budgeted) / budgeted <= 0.25


def test_not_genuine_observations_were_discarded(pmo40):
    cost = compute_all(pmo40).by_class("C").cost
    assert cost.discarded_not_genuine == 6
    assert cost.sample_size == 34


# ---------------------------------------------------------------------------
# Agentic verification
# ---------------------------------------------------------------------------


def test_the_class_a_verifier_is_calibrated_and_banks_the_lower_bound(pmo40):
    containment = compute_all(pmo40).by_class("A").containment
    assert containment.calibrated
    assert containment.false_negative_rate <= 0.05
    assert containment.budget_value == containment.ci95[0]
    assert containment.budget_value < containment.rate


def test_the_class_b_verifier_misses_the_fnr_bar_and_banks_nothing(pmo40):
    """Designed, not drawn. A verifier above 0.05 FNR contributes k = 0."""
    containment = compute_all(pmo40).by_class("B").containment
    assert containment.false_negative_rate > 0.05
    assert not containment.calibrated
    assert containment.budget_value == 0.0
    assert "advisory annotation" in containment.note


def test_there_is_no_verifier_on_class_c(pmo40):
    """The deployment inversion. Agentic verification helps where checking was
    already cheap, and does nothing for the class that is drowning."""
    containment = compute_all(pmo40).by_class("C").containment
    assert containment.offered == 0
    assert containment.budget_value == 0.0


def test_containment_raises_the_class_a_budget_above_the_unassisted_figure(pmo40):
    from vb.budget import verification_budget

    unassisted = verification_budget(14, 8, 0.55, 0.02)
    assert compute_all(pmo40).by_class("A").budget.budget > unassisted


# ---------------------------------------------------------------------------
# Class D
# ---------------------------------------------------------------------------


def test_no_class_d_decision_was_taken_autonomously(pmo40):
    budget = compute_all(pmo40).by_class("D").budget
    assert budget.demand == 0.0
    assert budget.status == "unbudgeted"
    assert budget.overdraft_ratio is None


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def test_all_four_gates_pass_on_the_reference_bundle(pmo40):
    suite = run_all(pmo40)
    assert suite.passed, suite.format()


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def test_the_bundle_declares_itself_synthetic(pmo40):
    assert pmo40.synthetic
    assert "not evidence" in pmo40.config["warning"]
    assert pmo40.config["generated_by"] == "examples/generate_pmo40.py"
    assert pmo40.config["seed"] == 4242


def test_the_bundle_shape_is_as_documented(pmo40):
    assert len(pmo40.projects) == 40
    assert len(pmo40.reviewers) == 14
    assert pmo40.periods == 8
    assert len(pmo40.events) == 4400


def test_the_generator_is_reproducible(repo_root, tmp_path):
    """Re-running the generator must produce a byte-identical decision log."""
    original = (repo_root / "examples" / "pmo40" / "decision_log.jsonl").read_bytes()
    result = subprocess.run(
        [sys.executable, str(repo_root / "examples" / "generate_pmo40.py")],
        capture_output=True,
        cwd=repo_root,
    )
    assert result.returncode == 0, result.stderr.decode()
    regenerated = (repo_root / "examples" / "pmo40" / "decision_log.jsonl").read_bytes()
    assert regenerated == original


def test_every_logged_decision_carries_a_class_and_a_period(pmo40):
    for event in pmo40.events:
        assert event["decision_class"] in ("A", "B", "C")
        assert 1 <= event["period"] <= 8
        assert event["artifact_id"]
