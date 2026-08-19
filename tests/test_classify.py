"""The A/B/C/D tree and its tie-breakers."""

from __future__ import annotations

import pytest

from vb.classify import (
    CLASS_EXPENSE,
    TREE,
    Classification,
    IncompleteAnswers,
    apply_tiebreakers,
    classify,
    describe_tree,
    format_classification,
    more_expensive,
    required_answers,
    walk,
)


# ---------------------------------------------------------------------------
# Terminals
# ---------------------------------------------------------------------------


def test_irreversible_is_class_d_immediately():
    """Q0 short-circuits. Cancelling a workstream never reaches Q1."""
    result = classify({"q0": True})
    assert result.decision_class == "D"
    assert result.path == (("q0", True),)


def test_deterministic_check_under_five_minutes_is_class_a():
    result = classify({"q0": False, "q1": True, "q1a": True})
    assert result.decision_class == "A"


def test_deterministic_check_with_expensive_exceptions_is_class_b():
    """A machine check that needs thirty minutes of interpretation is not Class A."""
    result = classify({"q0": False, "q1": True, "q1a": False})
    assert result.decision_class == "B"


def test_homogeneous_and_reversible_is_class_b():
    result = classify({"q0": False, "q1": False, "q2": True, "q2a": True})
    assert result.decision_class == "B"


def test_homogeneous_but_irreversible_within_a_cycle_is_class_c():
    """Sampling is only a control if the errors it misses get corrected."""
    result = classify({"q0": False, "q1": False, "q2": True, "q2a": False})
    assert result.decision_class == "C"


def test_expert_checkable_in_bounded_time_is_class_c():
    result = classify({"q0": False, "q1": False, "q2": False, "q3": True, "q3a": False})
    assert result.decision_class == "C"


def test_check_costlier_than_the_decision_is_class_d():
    result = classify({"q0": False, "q1": False, "q2": False, "q3": True, "q3a": True})
    assert result.decision_class == "D"


def test_unbounded_check_time_is_class_d():
    result = classify({"q0": False, "q1": False, "q2": False, "q3": False})
    assert result.decision_class == "D"


def test_every_terminal_is_reachable():
    reached = set()
    for q0 in (True, False):
        for q1 in (True, False):
            for q1a in (True, False):
                for q2 in (True, False):
                    for q2a in (True, False):
                        for q3 in (True, False):
                            for q3a in (True, False):
                                answers = {"q0": q0, "q1": q1, "q1a": q1a, "q2": q2,
                                           "q2a": q2a, "q3": q3, "q3a": q3a}
                                reached.add(classify(answers).decision_class)
    assert reached == {"A", "B", "C", "D"}


# ---------------------------------------------------------------------------
# Worked classifications from spec/decision-classes.md section 4
# ---------------------------------------------------------------------------


def test_critical_path_recalculation_is_class_a():
    assert classify({"q0": False, "q1": True, "q1a": True}).decision_class == "A"


def test_schedule_rebaselining_is_class_c():
    result = classify({"q0": False, "q1": False, "q2": False, "q3": True, "q3a": False})
    assert result.decision_class == "C"


def test_workstream_cancellation_is_class_d():
    assert classify({"q0": True}).decision_class == "D"


def test_verifier_verdict_with_a_proof_object_is_class_a():
    """The recursion rule, as a classification. A prose verdict falls through to C."""
    with_proof = classify({"q0": False, "q1": True, "q1a": True})
    prose = classify({"q0": False, "q1": False, "q2": False, "q3": True, "q3a": False})
    assert with_proof.decision_class == "A"
    assert prose.decision_class == "C"


# ---------------------------------------------------------------------------
# Incomplete answers
# ---------------------------------------------------------------------------


def test_missing_answer_raises_with_the_node_and_prompt():
    with pytest.raises(IncompleteAnswers) as excinfo:
        classify({"q0": False})
    assert excinfo.value.node_id == "q1"
    assert "deterministic check" in excinfo.value.prompt


def test_required_answers_asks_only_what_the_tree_reaches():
    assert required_answers({}) == ("q0",)
    assert required_answers({"q0": False}) == ("q1",)
    assert required_answers({"q0": True}) == ()
    assert required_answers({"q0": False, "q1": True, "q1a": True}) == ()


# ---------------------------------------------------------------------------
# Tie-breakers
# ---------------------------------------------------------------------------


def test_class_expense_ordering():
    assert CLASS_EXPENSE["A"] < CLASS_EXPENSE["B"] < CLASS_EXPENSE["C"] < CLASS_EXPENSE["D"]


def test_more_expensive():
    assert more_expensive("A", "C") == "C"
    assert more_expensive("D", "B") == "D"
    assert more_expensive("B", "B") == "B"


def test_more_expensive_rejects_a_non_class():
    with pytest.raises(ValueError, match="not a decision class"):
        more_expensive("A", "Z")


def test_t1_reversibility_overrides_the_tree():
    """A Class A result that cannot be undone within a cycle is at least Class C."""
    base = classify({"q0": False, "q1": True, "q1a": True})
    assert base.decision_class == "A"
    result = apply_tiebreakers(base, reversible_within_cycle=False)
    assert result.decision_class == "C"
    assert result.escalated_by_tiebreaker
    assert "T1 reversibility" in result.tiebreakers_applied[0]


def test_t1_sends_to_d_when_undo_costs_more_than_the_decision():
    base = classify({"q0": False, "q1": True, "q1a": True})
    result = apply_tiebreakers(
        base, reversible_within_cycle=False, undo_costs_more_than_decision=True
    )
    assert result.decision_class == "D"


def test_t1_does_nothing_when_reversible():
    base = classify({"q0": False, "q1": True, "q1a": True})
    assert apply_tiebreakers(base, reversible_within_cycle=True) is base


def test_t1_never_makes_a_class_cheaper():
    base = classify({"q0": False, "q1": False, "q2": False, "q3": True, "q3a": True})
    assert base.decision_class == "D"
    result = apply_tiebreakers(base, reversible_within_cycle=False)
    assert result.decision_class == "D"


def test_t2_disagreement_takes_the_more_expensive_class():
    base = classify({"q0": False, "q1": False, "q2": True, "q2a": True})
    assert base.decision_class == "B"
    result = apply_tiebreakers(base, second_opinion="C")
    assert result.decision_class == "C"
    assert "T2 disagreement" in result.tiebreakers_applied[0]
    assert "rubric" in result.tiebreakers_applied[0]


def test_t2_agreement_changes_nothing():
    base = classify({"q0": False, "q1": False, "q2": True, "q2a": True})
    assert apply_tiebreakers(base, second_opinion="B") is base


def test_t2_never_makes_a_class_cheaper():
    base = classify({"q0": False, "q1": False, "q2": False, "q3": True, "q3a": False})
    assert base.decision_class == "C"
    assert apply_tiebreakers(base, second_opinion="A").decision_class == "C"


def test_t2_rejects_a_non_class():
    base = classify({"q0": True})
    with pytest.raises(ValueError, match="not a decision class"):
        apply_tiebreakers(base, second_opinion="X")


def test_both_tiebreakers_compose():
    base = classify({"q0": False, "q1": True, "q1a": True})
    result = apply_tiebreakers(base, reversible_within_cycle=False, second_opinion="D")
    assert result.decision_class == "D"
    assert len(result.tiebreakers_applied) == 2
    assert result.tree_class == "A"


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------


def test_class_metadata_is_attached():
    result = classify({"q0": False, "q1": True, "q1a": True})
    assert result.name == "machine-checkable"
    assert result.typical_cost_hours == (0.01, 0.05)
    assert "may decide" in result.authority


def test_class_d_has_no_typical_cost_because_it_is_undefined_not_high():
    result = classify({"q0": True})
    assert result.typical_cost_hours is None
    assert "never delegated" in result.authority.lower() or "prepares" in result.authority.lower()


def test_describe_tree_lists_every_node_and_the_tiebreakers():
    text = describe_tree()
    for node_id in TREE:
        assert f"{node_id}." in text
    assert "T1 reversibility" in text
    assert "T2 disagreement" in text
    assert "T3 default" in text


def test_format_classification_includes_the_path():
    result = classify({"q0": False, "q1": True, "q1a": True})
    text = format_classification(result, "critical_path_recalculation")
    assert "CLASS A" in text
    assert "critical_path_recalculation" in text
    assert "q1a" in text


def test_format_classification_warns_about_class_d_delegation():
    text = format_classification(classify({"q0": True}))
    assert "never delegated" in text


def test_format_classification_notes_class_c_is_proposed():
    result = classify({"q0": False, "q1": False, "q2": False, "q3": True, "q3a": False})
    assert "proposed by the agent" in format_classification(result)


# ---------------------------------------------------------------------------
# Interactive walk, with injected io
# ---------------------------------------------------------------------------


def _scripted(answers):
    queue = list(answers)

    def read(_prompt: str) -> str:
        return queue.pop(0)

    return read


def test_walk_reaches_class_a():
    lines: list[str] = []
    result = walk(
        input_fn=_scripted(["no", "yes", "yes", "yes"]),
        output_fn=lines.append,
        decision_type="critical_path_recalculation",
    )
    assert result.decision_class == "A"
    assert any("CLASS A" in line for line in lines)


def test_walk_applies_the_reversibility_tiebreaker():
    lines: list[str] = []
    result = walk(
        input_fn=_scripted(["no", "yes", "yes", "no", "no"]),
        output_fn=lines.append,
    )
    assert result.decision_class == "C"
    assert result.tree_class == "A"


def test_walk_escalates_to_d_when_undo_is_expensive():
    result = walk(
        input_fn=_scripted(["no", "yes", "yes", "no", "yes"]),
        output_fn=lambda _line: None,
    )
    assert result.decision_class == "D"


def test_walk_skips_tiebreakers_for_class_d():
    result = walk(input_fn=_scripted(["yes"]), output_fn=lambda _line: None)
    assert result.decision_class == "D"


def test_walk_offers_guidance_and_re_asks():
    lines: list[str] = []
    walk(
        input_fn=_scripted(["why", "no", "yes", "yes", "yes"]),
        output_fn=lines.append,
        ask_tiebreakers=False,
    )
    assert any("Irreversible means" in line for line in lines)


def test_walk_rejects_nonsense_and_re_asks():
    lines: list[str] = []
    walk(
        input_fn=_scripted(["maybe", "no", "yes", "yes"]),
        output_fn=lines.append,
        ask_tiebreakers=False,
    )
    assert any("Answer yes or no" in line for line in lines)


def test_walk_without_tiebreakers_returns_the_tree_result():
    result = walk(
        input_fn=_scripted(["no", "yes", "yes"]),
        output_fn=lambda _line: None,
        ask_tiebreakers=False,
    )
    assert result.decision_class == "A"
    assert result.tiebreakers_applied == ()
