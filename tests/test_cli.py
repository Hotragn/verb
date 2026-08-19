"""The CLI. A presentation layer over the calculation modules.

Every command is exercised in both text and JSON form. The tests capture output
through the injected writer rather than through stdout, so they say nothing about
terminals and everything about what the command reports.
"""

from __future__ import annotations

import json

import pytest

from vb.cli import build_parser, main


def run(*argv: str) -> tuple[int, str]:
    lines: list[str] = []
    code = main(list(argv), out=lines.append)
    return code, "\n".join(lines)


def run_json(*argv: str) -> tuple[int, dict]:
    code, text = run(*argv)
    return code, json.loads(text)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def test_every_documented_subcommand_exists():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])
    for command in ("budget", "classify", "metrics", "drift", "gates"):
        args = parser.parse_args([command] + (["--input", "x"] if command in ("metrics", "drift") else []))
        assert args.command == command


def test_version_flag():
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["--version"])
    assert excinfo.value.code == 0


# ---------------------------------------------------------------------------
# vb budget, from flags
# ---------------------------------------------------------------------------


def test_budget_from_flags_reproduces_the_readme_output():
    code, text = run(
        "budget", "--reviewers", "6", "--hours", "8", "--utilisation", "0.55",
        "--cost", "1.25", "--demand", "70", "--decision-class", "C",
    )
    assert code == 0
    assert "Class C" in text
    assert "21.12" in text
    assert "3.31x" in text
    assert "OVERDRAFT" in text
    assert "48.88" in text
    assert "0.377" in text          # c needed for O = 1.0
    assert "19.9" in text           # R needed for O = 1.0


def test_budget_reports_the_unverified_share():
    _, text = run("budget", "--reviewers", "6", "--hours", "8", "--utilisation", "0.55",
                  "--cost", "1.25", "--demand", "70")
    assert "69.8%" in text


def test_budget_json_is_machine_readable():
    code, payload = run_json(
        "budget", "--reviewers", "6", "--hours", "8", "--utilisation", "0.55",
        "--cost", "1.25", "--demand", "70", "--json",
    )
    assert code == 0
    assert payload["decision_class"] == "C"
    assert payload["overdraft_ratio"] == pytest.approx(3.3144, rel=1e-3)
    assert payload["status"] == "overdraft"
    assert len(payload["sensitivity"]) > 0


def test_budget_sensitivity_table():
    _, text = run("budget", "--reviewers", "6", "--hours", "8", "--utilisation", "0.55",
                  "--cost", "1.25", "--demand", "70", "--sensitivity")
    assert "Effect of reducing c" in text
    assert "in budget" in text


def test_budget_with_containment_shows_the_effective_cost():
    _, text = run("budget", "--reviewers", "14", "--hours", "8", "--utilisation", "0.55",
                  "--cost", "0.02", "--demand", "320", "--decision-class", "A",
                  "--containment", "0.69", "--agent-check-cost", "0.005")
    assert "c_eff" in text
    assert "k = 0.690" in text
    assert "Gate 3" in text


def test_budget_requires_a_measured_cost_for_classes_a_b_c():
    code, text = run("budget", "--reviewers", "6", "--hours", "8", "--utilisation", "0.55",
                     "--demand", "70")
    assert code == 2
    assert "measured, not" in text


def test_budget_rejects_an_impossible_utilisation():
    code, text = run("budget", "--reviewers", "6", "--hours", "8", "--utilisation", "1.4",
                     "--cost", "1.25", "--demand", "70")
    assert code == 2
    assert "utilisation" in text


def test_budget_for_class_d_needs_no_cost():
    code, text = run("budget", "--decision-class", "D", "--reviewers", "6",
                     "--hours", "8", "--utilisation", "0.55", "--demand", "0")
    assert code == 0
    assert "UNBUDGETED" in text


def test_budget_flags_an_autonomous_class_d_decision_as_a_breach():
    _, text = run("budget", "--decision-class", "D", "--reviewers", "6",
                  "--hours", "8", "--utilisation", "0.55", "--demand", "3")
    assert "POLICY VIOLATION" in text
    assert "contract breach" in text


# ---------------------------------------------------------------------------
# vb budget, from a bundle
# ---------------------------------------------------------------------------


def test_budget_from_the_reference_bundle():
    code, text = run("budget", "--input", "examples/pmo40")
    assert code == 0
    assert "PMO-40" in text
    assert "synthetic" in text
    assert "3.31x" in text
    assert "overdraft" in text


def test_budget_from_bundle_shows_each_lever_and_says_none_alone_is_enough():
    _, text = run("budget", "--input", "examples/pmo40")
    assert "What would bring it to O = 1.0" in text
    assert "unreachable, even at 100% utilisation" in text
    assert "reclassify 70% of demand" in text
    assert "No single lever closes an overdraft of 3x" in text


def test_budget_from_bundle_json():
    code, payload = run_json("budget", "--input", "examples/pmo40", "--json")
    assert code == 0
    assert payload["synthetic"] is True
    classes = {c["decision_class"]: c for c in payload["classes"]}
    assert classes["C"]["overdraft_ratio"] == pytest.approx(3.31, abs=0.01)


def test_a_missing_bundle_is_reported_clearly():
    code, text = run("budget", "--input", "does/not/exist")
    assert code == 2
    assert "no such bundle" in text


def test_a_bundle_without_a_config_says_what_is_missing(tmp_path):
    code, text = run("metrics", "--input", str(tmp_path))
    assert code == 2
    assert "no config.json" in text


# ---------------------------------------------------------------------------
# vb classify
# ---------------------------------------------------------------------------


def test_classify_tree_prints_the_questions():
    code, text = run("classify", "--tree")
    assert code == 0
    assert "q0." in text and "q3a." in text
    assert "T1 reversibility" in text


def test_classify_with_scripted_answers():
    code, text = run("classify", "--answers", "q0=no", "q1=yes", "q1a=yes")
    assert code == 0
    assert "CLASS A" in text


def test_classify_names_the_decision_type():
    _, text = run("classify", "--decision-type", "critical_path_recalculation",
                  "--answers", "q0=no", "q1=yes", "q1a=yes")
    assert "critical_path_recalculation" in text


def test_classify_applies_a_second_opinion():
    _, text = run("classify", "--answers", "q0=no", "q1=no", "q2=yes", "q2a=yes",
                  "--second-opinion", "C")
    assert "CLASS C" in text
    assert "T2 disagreement" in text


def test_classify_json():
    code, payload = run_json("classify", "--answers", "q0=yes", "--json")
    assert code == 0
    assert payload["decision_class"] == "D"


def test_classify_reports_a_missing_answer():
    code, text = run("classify", "--answers", "q0=no")
    assert code == 2
    assert "Need an answer for q1" in text


def test_classify_rejects_malformed_answers():
    with pytest.raises(SystemExit):
        run("classify", "--answers", "q0")


# ---------------------------------------------------------------------------
# vb metrics
# ---------------------------------------------------------------------------


def test_metrics_reports_all_six_per_class():
    code, text = run("metrics", "--input", "examples/pmo40")
    assert code == 0
    for label in ("VB", "Overdraft O", "SDR", "Containment k", "Escalation prec.", "Reversal latency"):
        assert label in text
    for decision_class in ("Class A", "Class B", "Class C", "Class D"):
        assert decision_class in text


def test_metrics_states_the_observation_bias_every_time():
    _, text = run("metrics", "--input", "examples/pmo40")
    assert "biased low" in text and "VB biased high" in text
    assert "never used for individual performance management" in text


def test_metrics_can_be_limited_to_one_class():
    _, text = run("metrics", "--input", "examples/pmo40", "--decision-class", "C")
    assert "Class C" in text
    assert "Class A" not in text


def test_metrics_json():
    code, payload = run_json("metrics", "--input", "examples/pmo40", "--json")
    assert code == 0
    assert len(payload["classes"]) == 4


def test_metrics_shows_the_uncalibrated_verifier_as_zero():
    _, text = run("metrics", "--input", "examples/pmo40", "--decision-class", "B")
    assert "uncalibrated" in text


# ---------------------------------------------------------------------------
# vb drift
# ---------------------------------------------------------------------------


def test_drift_shows_the_floor_its_two_terms_and_the_trend():
    code, text = run("drift", "--input", "examples/pmo40", "--decision-class", "C")
    assert code == 0
    assert "floor f_C" in text
    assert "baseline P10" in text
    assert "reading floor" in text
    assert "RISING" in text
    assert "slope" in text


def test_drift_lists_every_period():
    _, text = run("drift", "--input", "examples/pmo40", "--decision-class", "C")
    for week in range(1, 9):
        assert f"\n  {week}    " in text or f"  {week} " in text


def test_drift_reports_the_secondary_signals_without_promoting_them():
    _, text = run("drift", "--input", "examples/pmo40", "--decision-class", "C")
    assert "never used as the metric" in text
    assert "coefficient of variation" in text
    assert "batch bursts" in text


def test_drift_explains_the_lag_when_the_trend_is_rising():
    _, text = run("drift", "--input", "examples/pmo40", "--decision-class", "C")
    assert "backlog first" in text


def test_drift_json():
    code, payload = run_json("drift", "--input", "examples/pmo40", "--decision-class", "C", "--json")
    assert code == 0
    assert payload["trend"] == "rising"
    assert len(payload["periods"]) == 8


def test_drift_for_a_class_with_no_approvals():
    code, text = run("drift", "--input", "examples/pmo40", "--decision-class", "D")
    assert code == 2
    assert "No drift report" in text


# ---------------------------------------------------------------------------
# vb gates
# ---------------------------------------------------------------------------


def test_gates_runs_all_four():
    code, text = run("gates", "--input", "examples/pmo40")
    assert code == 0
    for gate in ("GATE 1", "GATE 2", "GATE 3", "GATE 4"):
        assert gate in text
    assert "All gates passed" in text


def test_gates_can_run_one():
    _, text = run("gates", "--input", "examples/pmo40", "--gate", "replay")
    assert "GATE 4" in text
    assert "GATE 1" not in text


def test_gates_validates_a_contract():
    code, text = run("gates", "--contract", "schema/fixtures/valid/contract-schedule-integrity.json")
    assert code == 0
    assert "contract structure" in text
    assert "PASS" in text


def test_gates_rejects_an_invalid_contract():
    code, text = run("gates", "--contract", "schema/fixtures/invalid/contract-class-d-in-scope.json")
    assert code == 1
    assert "FAIL" in text
    assert "invalid, not risky" in text


def test_gates_needs_an_input_or_a_contract():
    code, text = run("gates")
    assert code == 2
    assert "--input" in text


def test_gates_json():
    code, payload = run_json("gates", "--input", "examples/pmo40", "--json")
    assert code == 0
    assert len(payload["results"]) == 4


def test_gates_refuses_yaml_contracts_with_a_useful_message(tmp_path):
    path = tmp_path / "c.yaml"
    path.write_text("agent_id: x", encoding="utf-8")
    code, text = run("gates", "--contract", str(path))
    assert code == 2
    assert "JSON, not YAML" in text


# ---------------------------------------------------------------------------
# The synthetic warning travels with the numbers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ("budget", "--input", "examples/pmo40"),
        ("metrics", "--input", "examples/pmo40"),
        ("drift", "--input", "examples/pmo40", "--decision-class", "C"),
        ("gates", "--input", "examples/pmo40"),
    ],
)
def test_every_bundle_command_carries_the_synthetic_warning(argv):
    _, text = run(*argv)
    assert "synthetic" in text
