"""The four eval gates, plus the contract structure check."""

from __future__ import annotations

import copy
import json

import pytest

from vb.gates import (
    HEDGE_PATTERN,
    classification_gate,
    contract_gate,
    evidence_gate,
    load_contract,
    replay_gate,
    run_all,
    validate_artifact_structure,
    verifier_calibration_gate,
)


# ---------------------------------------------------------------------------
# Gate 1: classification
# ---------------------------------------------------------------------------


def _pairs(n=50, disagreements=6):
    truth = ["A"] * 18 + ["B"] * 16 + ["C"] * 13 + ["D"] * 3
    truth = (truth * 4)[:n]
    a = list(truth)
    b = list(truth)
    shift = {"A": "B", "B": "C", "C": "B", "D": "D"}
    for i in range(disagreements):
        index = (i * 7 + 2) % n
        b[index] = shift[b[index]]
    return a, b


def test_gate_1_passes_on_substantial_agreement():
    a, b = _pairs()
    result = classification_gate(a, b, disagreements_logged=True)
    assert result.passed
    assert result.status == "PASS"
    assert result.criteria[0].value >= 0.70


def test_gate_1_fails_on_poor_agreement_and_blames_the_rubric():
    a = ["B"] * 25 + ["C"] * 25
    b = ["C"] * 25 + ["B"] * 25
    result = classification_gate(a, b)
    assert not result.passed
    assert any("rubric" in c for c in result.consequences)


def test_gate_1_fails_when_class_d_remains_in_scope():
    a = ["A"] * 49 + ["D"]
    b = ["A"] * 50
    result = classification_gate(
        a, b,
        scope_types=["critical_path_recalculation"],
        decision_types=["critical_path_recalculation"] * 50,
    )
    assert not result.passed
    criterion = next(c for c in result.criteria if c.id == "1.2")
    assert criterion.value == 1
    assert any("never delegated" in c for c in result.consequences)


def test_gate_1_fails_on_a_small_sample():
    a, b = _pairs(n=20, disagreements=1)
    result = classification_gate(a, b)
    assert not result.passed
    assert next(c for c in result.criteria if c.id == "1.4").passed is False


def test_gate_1_fails_when_disagreements_are_not_logged():
    a, b = _pairs()
    assert not classification_gate(a, b, disagreements_logged=False).passed


def test_gate_1_warns_when_a_skewed_marginal_depresses_kappa():
    a = ["A"] * 49 + ["B"]
    b = ["A"] * 50
    result = classification_gate(a, b)
    assert any("dominated by one class" in c for c in result.consequences)


def test_gate_1_with_no_pairs_is_skipped_not_passed():
    result = classification_gate([], [])
    assert result.status == "SKIPPED"
    assert not result.passed


def test_gate_1_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="equal-length"):
        classification_gate(["A"], ["A", "B"])


# ---------------------------------------------------------------------------
# Structural artifact validation
# ---------------------------------------------------------------------------


def test_a_sound_artifact_has_no_problems(artifact):
    assert validate_artifact_structure(artifact) == []


@pytest.mark.parametrize(
    "field", ["decision", "basis", "alternatives", "confidence_and_failure_mode", "reversal", "owner"]
)
def test_every_missing_field_is_caught(artifact, field):
    del artifact[field]
    problems = validate_artifact_structure(artifact)
    assert any(field in p for p in problems)


def test_unresolvable_source_id_is_caught(artifact):
    artifact["basis"][0]["source_id"] = "the project plan"
    assert any("not resolvable" in p for p in validate_artifact_structure(artifact))


def test_basis_that_describes_rather_than_states_is_caught(artifact):
    artifact["basis"][0]["detail"] = "sched"
    assert any("describes rather than states" in p for p in validate_artifact_structure(artifact))


def test_empty_basis_is_caught(artifact):
    artifact["basis"] = []
    assert any("basis is empty" in p for p in validate_artifact_structure(artifact))


def test_empty_alternatives_is_caught(artifact):
    artifact["alternatives"] = []
    assert any("alternatives is empty" in p for p in validate_artifact_structure(artifact))


def test_a_forced_declaration_is_accepted(artifact):
    artifact["alternatives"] = {
        "forced": True,
        "reason": "The option set is fixed by contract clause 11.4 and the notice period.",
    }
    assert validate_artifact_structure(artifact) == []


def test_a_forced_declaration_without_a_reason_is_caught(artifact):
    artifact["alternatives"] = {"forced": True, "reason": "n/a"}
    assert any("without a stated reason" in p for p in validate_artifact_structure(artifact))


def test_thin_rejection_reasons_are_caught(artifact):
    artifact["alternatives"][0]["rejected_because"] = "Not applicable"
    assert any("is not a reason" in p for p in validate_artifact_structure(artifact))


@pytest.mark.parametrize(
    "phrase",
    [
        "The categorisation may be inaccurate if the data is incorrect or incomplete here.",
        "This result could be wrong under some circumstances that we cannot enumerate now.",
        "Results may vary depending on the underlying assumptions used in this calculation.",
    ],
)
def test_hedging_phrases_are_prohibited(artifact, phrase):
    artifact["confidence_and_failure_mode"]["failure_mode"] = phrase
    assert any("hedging" in p for p in validate_artifact_structure(artifact))


def test_the_hedge_pattern_is_case_insensitive():
    assert HEDGE_PATTERN.search("MAY BE INACCURATE")


def test_short_failure_mode_is_caught(artifact):
    artifact["confidence_and_failure_mode"]["failure_mode"] = "Could break."
    assert any("specific, detectable failure" in p for p in validate_artifact_structure(artifact))


def test_confidence_out_of_range_is_caught(artifact):
    artifact["confidence_and_failure_mode"]["confidence"] = 1.4
    assert any("outside 0 to 1" in p for p in validate_artifact_structure(artifact))


def test_model_self_report_is_not_calibration(artifact):
    artifact["confidence_and_failure_mode"]["calibration_basis"] = "model"
    assert any("calibration basis" in p for p in validate_artifact_structure(artifact))


def test_reversal_as_sentiment_is_caught(artifact):
    artifact["reversal"]["how"] = "Can be revisited"
    assert any("sentiment, not a procedure" in p for p in validate_artifact_structure(artifact))


def test_reversal_without_a_cost_is_caught(artifact):
    del artifact["reversal"]["cost_hours"]
    assert any("numeric cost_hours" in p for p in validate_artifact_structure(artifact))


def test_owner_as_role_is_caught(artifact):
    artifact["owner"]["person_id"] = ""
    assert any("role with no resolved person" in p for p in validate_artifact_structure(artifact))


def test_class_b_needs_its_batch_fields(artifact):
    artifact["decision_class"] = "B"
    problems = validate_artifact_structure(artifact)
    assert any("batch_id" in p for p in problems)
    assert any("rubric_version" in p for p in problems)


def test_class_c_needs_its_additions(artifact):
    artifact["decision_class"] = "C"
    problems = validate_artifact_structure(artifact)
    assert any("precedent_cases" in p for p in problems)


def test_class_d_preparation_must_not_contain_a_decision(artifact):
    artifact["artifact_kind"] = "class_d_preparation"
    artifact["decides_class_d"] = "workstream_cancellation"
    artifact["recommendation"] = "Recommend cancelling the workstream at the October gate."
    artifact["options_with_costs"] = [{"option": "Cancel", "cost": "2.1m", "reversal_cost_hours": 400}]
    problems = validate_artifact_structure(artifact)
    assert any("has made a Class D decision" in p for p in problems)


def test_class_d_preparation_without_a_decision_is_sound(artifact):
    del artifact["decision"]
    artifact["artifact_kind"] = "class_d_preparation"
    artifact["decides_class_d"] = "workstream_cancellation"
    artifact["recommendation"] = "Recommend cancelling the workstream at the October gate."
    artifact["options_with_costs"] = [{"option": "Cancel", "cost": "2.1m", "reversal_cost_hours": 400}]
    assert validate_artifact_structure(artifact) == []


def test_a_class_d_decision_artifact_is_caught(artifact):
    artifact["decision_class"] = "D"
    assert any("never delegated" in p for p in validate_artifact_structure(artifact))


def test_a_verifier_verdict_needs_a_proof_object(artifact):
    artifact["artifact_kind"] = "verifier_verdict"
    problems = validate_artifact_structure(artifact)
    assert any("proof_object" in p for p in problems)


def test_a_prose_verifier_verdict_supplies_no_containment(artifact):
    artifact["artifact_kind"] = "verifier_verdict"
    artifact["verdict"] = "pass"
    artifact["calibration_record_ref"] = "CAL:v1"
    artifact["proof_object"] = {"recheck_command": "read the reasoning"}
    assert any("opinion, not containment" in p for p in validate_artifact_structure(artifact))


# ---------------------------------------------------------------------------
# Gate 2: evidence
# ---------------------------------------------------------------------------


def test_gate_2_passes_on_sound_artifacts(artifact):
    artifacts = [dict(artifact, artifact_id=f"da-{i}") for i in range(30)]
    result = evidence_gate(
        artifacts,
        substantive_sample=[True] * 19 + [False],
        measured_cost_hours=1.31,
        budgeted_cost_hours=1.25,
    )
    assert result.passed


def test_gate_2_requires_one_hundred_percent_schema_validity(artifact):
    """Not 99. A missing field means the artifact is an output, not a decision."""
    artifacts = [dict(artifact, artifact_id=f"da-{i}") for i in range(100)]
    broken = dict(artifacts[0])
    del broken["owner"]
    artifacts[0] = broken
    result = evidence_gate(artifacts, substantive_sample=[True] * 20,
                           measured_cost_hours=1.25, budgeted_cost_hours=1.25)
    assert not result.passed
    assert next(c for c in result.criteria if c.id == "2.1").value == 0.99


def test_gate_2_fails_when_the_human_sample_is_not_substantive(artifact):
    artifacts = [dict(artifact, artifact_id=f"da-{i}") for i in range(20)]
    result = evidence_gate(artifacts, substantive_sample=[True] * 16 + [False] * 4,
                           measured_cost_hours=1.25, budgeted_cost_hours=1.25)
    assert not result.passed


def test_gate_2_fails_when_measured_cost_drifts_from_the_budget(artifact):
    artifacts = [dict(artifact, artifact_id=f"da-{i}") for i in range(20)]
    result = evidence_gate(artifacts, substantive_sample=[True] * 20,
                           measured_cost_hours=1.90, budgeted_cost_hours=1.25)
    assert not result.passed
    assert next(c for c in result.criteria if c.id == "2.3").value > 0.25


def test_gate_2_fails_without_a_human_sample(artifact):
    """The machine check cannot detect a fabricated basis."""
    result = evidence_gate([artifact], measured_cost_hours=1.25, budgeted_cost_hours=1.25)
    criterion = next(c for c in result.criteria if c.id == "2.2")
    assert not criterion.passed
    assert "fabricated basis" in criterion.detail


def test_gate_2_flags_a_class_d_contract_breach(artifact):
    breach = dict(artifact)
    breach["artifact_kind"] = "class_d_preparation"
    result = evidence_gate([breach], substantive_sample=[True] * 20,
                           measured_cost_hours=1.25, budgeted_cost_hours=1.25)
    assert not result.passed
    assert any("contract breach" in c for c in result.consequences)


def test_gate_2_with_no_artifacts_is_skipped():
    assert evidence_gate([]).status == "SKIPPED"


# ---------------------------------------------------------------------------
# Gate 3: verifier calibration
# ---------------------------------------------------------------------------


def _labelled(n=240, known_bad=38, false_negatives=1, contained_share=0.70):
    records = []
    good_contained = int((n - known_bad) * contained_share)
    for i in range(n):
        if i < known_bad:
            verdict = "pass" if i < false_negatives else "reject"
            contained = True
        elif i < known_bad + good_contained:
            verdict, contained = "pass", True
        else:
            verdict, contained = "cannot_decide", False
        records.append({"known_bad": i < known_bad, "verdict": verdict, "contained": contained})
    return records


def test_gate_3_passes_on_a_calibrated_verifier():
    result = verifier_calibration_gate(_labelled(), cost_remeasured=True)
    assert result.passed
    assert any("lower bound" in c for c in result.consequences)


def test_gate_3_fails_on_false_negatives_and_sets_containment_to_zero():
    result = verifier_calibration_gate(_labelled(false_negatives=8), cost_remeasured=True)
    assert not result.passed
    assert any("k = 0.00" in c for c in result.consequences)
    assert any("green tick" in c for c in result.consequences)


def test_gate_3_failure_keeps_the_verifier_as_an_advisory_annotation():
    result = verifier_calibration_gate(_labelled(false_negatives=8), cost_remeasured=True)
    assert any("advisory annotation" in c for c in result.consequences)


def test_gate_3_enforces_the_recursion_rule():
    """A verifier whose own output is Class C moved the cost, it did not remove it."""
    result = verifier_calibration_gate(_labelled(), verifier_output_class="C", cost_remeasured=True)
    assert not result.passed
    assert not next(c for c in result.criteria if c.id == "3.2").passed


def test_gate_3_fails_on_a_small_labelled_set():
    result = verifier_calibration_gate(_labelled(n=100, known_bad=30), cost_remeasured=True)
    assert not result.passed
    assert not next(c for c in result.criteria if c.id == "3.4").passed


def test_gate_3_fails_on_too_few_known_bad():
    result = verifier_calibration_gate(_labelled(known_bad=8, false_negatives=0), cost_remeasured=True)
    assert not next(c for c in result.criteria if c.id == "3.5").passed


def test_gate_3_requires_cost_to_be_remeasured():
    """The residual human queue is harder than the original average."""
    result = verifier_calibration_gate(_labelled(), cost_remeasured=False)
    assert not result.passed
    assert not next(c for c in result.criteria if c.id == "3.6").passed


def test_gate_3_reports_false_positives_as_a_cost_not_a_risk():
    records = _labelled()
    for record in records[100:150]:
        record["verdict"] = "reject"
    result = verifier_calibration_gate(records, cost_remeasured=True)
    assert any("cost, not a risk" in c for c in result.consequences)


def test_gate_3_with_no_labelled_set_is_skipped():
    assert verifier_calibration_gate([]).status == "SKIPPED"


# ---------------------------------------------------------------------------
# Gate 4: replay
# ---------------------------------------------------------------------------


def _replay(n=120, class_d=0, out_of_scope=0, ep=0.7, agent_ok=0.85, history_ok=0.78):
    scope = ["critical_path_recalculation", "milestone_slip_categorisation"]
    records = []
    for i in range(n):
        records.append(
            {
                "decision_type": "not_in_scope" if i < out_of_scope else scope[i % 2],
                "agent_class": "D" if i < class_d else "A",
                "agent_authority": "decide",
                "historical_outcome_ok": i < int(n * history_ok),
                "agent_outcome_ok": i < int(n * agent_ok),
                "adjudication_hours": 0.5,
                "escalated": i % 10 == 0,
                "escalation_upheld": (i % 10 == 0) and (i % 100 != 0 or ep > 0.7),
            }
        )
    return records


def test_gate_4_passes_on_a_good_replay():
    records = _replay()
    for record in records:
        record["escalation_upheld"] = record["escalated"]
    assert replay_gate(records, scope_types=["critical_path_recalculation",
                                             "milestone_slip_categorisation"],
                       cost_hours=1.25).passed


def test_gate_4_fails_outright_on_a_single_autonomous_class_d():
    """Not few. Zero."""
    records = _replay(class_d=1)
    for record in records:
        record["escalation_upheld"] = record["escalated"]
    result = replay_gate(records, scope_types=["critical_path_recalculation",
                                               "milestone_slip_categorisation"],
                         cost_hours=1.25)
    assert not result.passed
    assert next(c for c in result.criteria if c.id == "4.2").value == 1
    assert any("Gate failed outright" in c for c in result.consequences)


def test_gate_4_catches_scope_creep():
    records = _replay(out_of_scope=3)
    for record in records:
        record["escalation_upheld"] = record["escalated"]
    result = replay_gate(records, scope_types=["critical_path_recalculation",
                                               "milestone_slip_categorisation"],
                         cost_hours=1.25)
    assert not result.passed
    assert any("scope creep" in c for c in result.consequences)


def test_gate_4_fails_when_the_agent_is_worse_than_history():
    records = _replay(agent_ok=0.60, history_ok=0.80)
    result = replay_gate(records, cost_hours=1.25)
    assert not next(c for c in result.criteria if c.id == "4.1").passed


def test_a_right_answer_nobody_can_check_does_not_pass():
    records = _replay(agent_ok=0.95, history_ok=0.70)
    for record in records:
        record["adjudication_hours"] = 9.0        # far above the budgeted c
        record["escalation_upheld"] = record["escalated"]
    result = replay_gate(records, cost_hours=1.25)
    assert not result.passed
    assert any("usable correctness" in c for c in result.consequences)


def test_gate_4_fails_on_poor_escalation_precision_without_suggesting_threshold_raising():
    records = _replay()
    for record in records:
        record["escalation_upheld"] = False
    result = replay_gate(records, cost_hours=1.25)
    assert not result.passed
    assert any("unmeasured\nrecall" in c or "recall failure" in c for c in result.consequences)


def test_gate_4_fails_on_a_small_replay_set():
    records = _replay(n=40)
    for record in records:
        record["escalation_upheld"] = record["escalated"]
    assert not next(c for c in replay_gate(records, cost_hours=1.25).criteria if c.id == "4.6").passed


def test_gate_4_without_a_cost_cannot_check_adjudication_time():
    records = _replay(agent_ok=0.95, history_ok=0.70)
    result = replay_gate(records)
    criterion = next(c for c in result.criteria if c.id == "4.3")
    assert "cannot check" in criterion.detail


def test_gate_4_with_no_records_is_skipped():
    assert replay_gate([]).status == "SKIPPED"


# ---------------------------------------------------------------------------
# Contract structure
# ---------------------------------------------------------------------------


@pytest.fixture
def contract(repo_root):
    return json.loads(
        (repo_root / "schema" / "fixtures" / "valid" / "contract-schedule-integrity.json").read_text(
            encoding="utf-8"
        )
    )


def test_a_valid_contract_passes(contract):
    assert contract_gate(contract).passed


def test_the_verifier_contract_passes(repo_root):
    verifier = json.loads(
        (repo_root / "schema" / "fixtures" / "valid" / "contract-schedule-verifier.json").read_text(
            encoding="utf-8"
        )
    )
    assert contract_gate(verifier).passed


def test_class_d_in_scope_is_invalid_not_risky(contract):
    contract["scope"]["in_scope"].append(
        {"decision_type": "milestone_removal", "decision_class": "D", "authority": "decide"}
    )
    result = contract_gate(contract)
    assert not result.passed
    assert not next(c for c in result.criteria if c.id == "R2").passed
    assert any("invalid, not risky" in c for c in result.consequences)


def test_unlisted_types_must_escalate(contract):
    contract["scope"]["unlisted_types"] = "allow"
    assert not next(c for c in contract_gate(contract).criteria if c.id == "R1").passed


def test_class_c_cannot_be_decided(contract):
    contract["scope"]["in_scope"].append(
        {"decision_type": "schedule_rebaselining", "decision_class": "C", "authority": "decide"}
    )
    assert not next(c for c in contract_gate(contract).criteria if c.id == "R3").passed


def test_class_b_needs_a_sampling_rate(contract):
    del contract["scope"]["in_scope"][3]["sampling_rate"]
    assert not next(c for c in contract_gate(contract).criteria if c.id == "R4").passed


def test_evidence_failure_must_escalate(contract):
    contract["evidence"]["on_evidence_failure"] = "proceed"
    assert not next(c for c in contract_gate(contract).criteria if c.id == "E1").passed


def test_all_six_evidence_fields_are_required(contract):
    contract["evidence"]["required_fields"].remove("alternatives")
    criterion = next(c for c in contract_gate(contract).criteria if c.id == "E2")
    assert not criterion.passed
    assert "alternatives" in criterion.detail


def test_the_three_mandatory_escalations(contract):
    contract["escalation"]["conditions"] = [
        c for c in contract["escalation"]["conditions"] if c["id"] != "class_d_detected"
    ]
    criterion = next(c for c in contract_gate(contract).criteria if c.id == "S2")
    assert not criterion.passed
    assert "class_d_detected" in criterion.detail


def test_escalation_must_resolve_to_a_person(contract):
    contract["escalation"]["target_resolution"] = "role_only"
    assert not next(c for c in contract_gate(contract).criteria if c.id == "S3").passed


def test_two_revokers_are_required(contract):
    contract["revocation"]["who"] = ["pmo_lead"]
    assert not next(c for c in contract_gate(contract).criteria if c.id == "V1").passed


def test_an_untested_revocation_path_is_flagged(contract):
    del contract["revocation"]["last_tested"]
    assert not next(c for c in contract_gate(contract).criteria if c.id == "V2").passed


def test_complete_then_halt_is_only_safe_for_class_a(contract):
    contract["revocation"]["in_flight_work"] = "complete_then_halt"
    assert not next(c for c in contract_gate(contract).criteria if c.id == "V3").passed


def test_complete_then_halt_is_allowed_when_everything_is_class_a(contract):
    contract["scope"]["in_scope"] = [
        e for e in contract["scope"]["in_scope"] if e["decision_class"] == "A"
    ]
    contract["revocation"]["in_flight_work"] = "complete_then_halt"
    assert next(c for c in contract_gate(contract).criteria if c.id == "V3").passed


def test_a_missing_field_is_reported(contract):
    del contract["revocation"]
    result = contract_gate(contract)
    assert not result.passed
    assert not next(c for c in result.criteria if c.id == "0.4").passed


def test_a_verifier_without_calibration_fails(repo_root):
    verifier = json.loads(
        (repo_root / "schema" / "fixtures" / "valid" / "contract-schedule-verifier.json").read_text(
            encoding="utf-8"
        )
    )
    del verifier["calibration"]
    result = contract_gate(verifier)
    assert not result.passed
    assert not next(c for c in result.criteria if c.id == "E3").passed


def test_a_verifier_must_bank_the_lower_bound_not_the_point_estimate(repo_root):
    verifier = json.loads(
        (repo_root / "schema" / "fixtures" / "valid" / "contract-schedule-verifier.json").read_text(
            encoding="utf-8"
        )
    )
    verifier["calibration"]["containment_used_in_budget"] = verifier["calibration"][
        "containment_point_estimate"
    ]
    assert not next(c for c in contract_gate(verifier).criteria if c.id == "E3c").passed


def test_load_contract_refuses_yaml(tmp_path):
    path = tmp_path / "contract.yaml"
    path.write_text("agent_id: x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON, not YAML"):
        load_contract(path)


def test_load_contract_reads_json(repo_root):
    contract = load_contract(
        repo_root / "schema" / "fixtures" / "valid" / "contract-change-impact.json"
    )
    assert contract["agent_id"] == "change-impact-01"


# ---------------------------------------------------------------------------
# Suite
# ---------------------------------------------------------------------------


def test_run_all_passes_on_the_reference_bundle(pmo40):
    suite = run_all(pmo40)
    assert suite.passed
    assert len(suite.results) == 4
    assert suite.blocking_failures == ()


def test_run_all_can_select_one_gate(pmo40):
    suite = run_all(pmo40, only="replay")
    assert len(suite.results) == 1
    assert suite.results[0].gate == 4


def test_gates_with_no_data_are_skipped_not_passed(tmp_path):
    from vb._io import Bundle

    empty = Bundle(path=tmp_path, config={"classes": {"A": {}}})
    suite = run_all(empty)
    assert all(r.status == "SKIPPED" for r in suite.results)
    assert not suite.passed


def test_suite_formats_every_gate(pmo40):
    text = run_all(pmo40).format()
    for gate in (1, 2, 3, 4):
        assert f"GATE {gate}" in text


def test_criterion_formatting_handles_every_value_type(pmo40):
    for result in run_all(pmo40).results:
        for criterion in result.criteria:
            assert criterion.format().strip()
