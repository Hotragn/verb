"""The A/B/C/D classifier.

Walks a decision through the tree in spec/decision-classes.md section 3, then
applies the three tie-breakers. Usable programmatically and interactively; the
interactive path takes injectable input and output functions so it is testable
without a terminal.

Decisions are classified by the cost of checking them. Not by risk, not by value,
not by how hard the task is for the model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

__all__ = [
    "DecisionClass",
    "Question",
    "Classification",
    "IncompleteAnswers",
    "TREE",
    "ROOT",
    "CLASS_EXPENSE",
    "CLASS_NAMES",
    "TYPICAL_COST_HOURS",
    "more_expensive",
    "classify",
    "apply_tiebreakers",
    "required_answers",
    "walk",
    "describe_tree",
]

DecisionClass = str

ROOT = "q0"

#: Ordered by cost of checking. Tie-breakers may only move a decision up this
#: ordering, never down.
CLASS_EXPENSE: Mapping[str, int] = {"A": 0, "B": 1, "C": 2, "D": 3}

CLASS_NAMES: Mapping[str, str] = {
    "A": "machine-checkable",
    "B": "sample-checkable",
    "C": "expert-checkable",
    "D": "not checkable in advance",
}

#: Indicative only, and PMO-shaped. Measure your own. See spec/metrics.md.
TYPICAL_COST_HOURS: Mapping[str, tuple[float, float] | None] = {
    "A": (0.01, 0.05),
    "B": (0.05, 0.25),
    "C": (0.5, 3.0),
    "D": None,
}

CLASS_AUTHORITY: Mapping[str, str] = {
    "A": "Agent may decide, within contract scope. Human sees exceptions only.",
    "B": "Agent may decide, within contract scope. Human samples each batch.",
    "C": "Agent proposes. Human decides. This is where the budget is spent.",
    "D": "Agent prepares. Human decides. Never delegated, because there is no budget for it.",
}


class IncompleteAnswers(KeyError):
    """Raised when the tree reaches a node with no answer supplied."""

    def __init__(self, node_id: str, prompt: str) -> None:
        self.node_id = node_id
        self.prompt = prompt
        super().__init__(f"no answer supplied for {node_id!r}: {prompt}")


@dataclass(frozen=True)
class Question:
    """One node of the decision tree.

    ``yes`` and ``no`` are either another node id, or ``class:X`` for a terminal.
    """

    id: str
    prompt: str
    yes: str
    no: str
    help: str = ""

    def target(self, answer: bool) -> str:
        return self.yes if answer else self.no


TREE: Mapping[str, Question] = {
    "q0": Question(
        id="q0",
        prompt=(
            "Is the decision irreversible, or is correctness only observable after "
            "the outcome, on a horizon longer than one review cycle?"
        ),
        yes="class:D",
        no="q1",
        help=(
            "Irreversible means no undo, or undo costs more than the original decision. "
            "Examples that answer yes: cancelling a workstream, terminating a contract, "
            "go-live authorisation, redundancy selection."
        ),
    ),
    "q1": Question(
        id="q1",
        prompt=(
            "Does a deterministic check exist that decides correctness without a "
            "human judgement call?"
        ),
        yes="q1a",
        no="q2",
        help=(
            "The check's verdict must be the answer, not an input to a judgement. "
            "A variance report is not a check. A variance report plus a threshold plus "
            "'flag if over' is a check."
        ),
    ),
    "q1a": Question(
        id="q1a",
        prompt=(
            "Is the human time to act on that check under 5 minutes, including the "
            "amortised cost of exceptions?"
        ),
        yes="class:A",
        no="class:B",
        help=(
            "If the exception rate is above roughly 5 percent, exception handling "
            "dominates and the class is B rather than A."
        ),
    ),
    "q2": Question(
        id="q2",
        prompt=(
            "Is this one of a homogeneous population of at least 30 per period, "
            "governed by one rubric, where a sample bounds the batch error rate and "
            "no member is much more consequential than the others?"
        ),
        yes="q2a",
        no="q3",
        help=(
            "The consequence-spread condition fails most often. A batch of 200 status "
            "narratives usually contains three that go to the board, and a sample will "
            "miss them. Stratify those out, or the whole population is Class C."
        ),
    ),
    "q2a": Question(
        id="q2a",
        prompt="Is it reversible within one review cycle at bounded cost?",
        yes="class:B",
        no="class:C",
        help=(
            "Sampling works because the errors it misses get caught and corrected. "
            "If they cannot be corrected inside a cycle, sampling is not a control."
        ),
    ),
    "q3": Question(
        id="q3",
        prompt=(
            "Can a qualified human decide correctness in bounded time from the "
            "artifact plus retrievable context?"
        ),
        yes="q3a",
        no="class:D",
        help=(
            "Bounded time is the operative phrase. If a reviewer could spend arbitrary "
            "time and still not be sure, it is Class D. The context may be slow to "
            "retrieve, including a phone call, as long as it is retrievable."
        ),
    ),
    "q3a": Question(
        id="q3a",
        prompt=(
            "Does an honest check cost more qualified human time than making the "
            "decision from scratch?"
        ),
        yes="class:D",
        no="class:C",
        help=(
            "If checking is more expensive than doing, the agent has not saved anything "
            "and the decision has no usable verification cost."
        ),
    ),
}


@dataclass(frozen=True)
class Classification:
    """The result of walking the tree, after tie-breakers."""

    decision_class: str
    tree_class: str
    path: tuple[tuple[str, bool], ...]
    tiebreakers_applied: tuple[str, ...] = ()
    rationale: str = ""

    @property
    def name(self) -> str:
        return CLASS_NAMES[self.decision_class]

    @property
    def typical_cost_hours(self) -> tuple[float, float] | None:
        return TYPICAL_COST_HOURS[self.decision_class]

    @property
    def authority(self) -> str:
        return CLASS_AUTHORITY[self.decision_class]

    @property
    def escalated_by_tiebreaker(self) -> bool:
        return self.decision_class != self.tree_class


def more_expensive(left: str, right: str) -> str:
    """Return whichever class costs more to check. Used by tie-breaker T2."""
    for value in (left, right):
        if value not in CLASS_EXPENSE:
            raise ValueError(f"not a decision class: {value!r}")
    return left if CLASS_EXPENSE[left] >= CLASS_EXPENSE[right] else right


def required_answers(answers: Mapping[str, bool] | None = None) -> tuple[str, ...]:
    """Node ids still needed to reach a terminal, given the answers so far.

    Returns an empty tuple once the answers are sufficient. Used by the CLI to
    ask only the questions that matter, which is usually three or four of seven.
    """
    answers = answers or {}
    node_id = ROOT
    missing: list[str] = []
    while not node_id.startswith("class:"):
        question = TREE[node_id]
        if question.id not in answers:
            missing.append(question.id)
            break
        node_id = question.target(answers[question.id])
    return tuple(missing)


def classify(answers: Mapping[str, bool]) -> Classification:
    """Walk the tree. Raises IncompleteAnswers if a needed answer is absent.

    Tie-breakers are *not* applied here. Call :func:`apply_tiebreakers` on the
    result, or use the CLI, which does both.
    """
    node_id = ROOT
    path: list[tuple[str, bool]] = []

    while not node_id.startswith("class:"):
        question = TREE[node_id]
        if question.id not in answers:
            raise IncompleteAnswers(question.id, question.prompt)
        answer = bool(answers[question.id])
        path.append((question.id, answer))
        node_id = question.target(answer)

    tree_class = node_id.split(":", 1)[1]
    return Classification(
        decision_class=tree_class,
        tree_class=tree_class,
        path=tuple(path),
        rationale=_rationale(tuple(path), tree_class),
    )


def apply_tiebreakers(
    base: Classification,
    *,
    reversible_within_cycle: bool | None = None,
    undo_costs_more_than_decision: bool | None = None,
    second_opinion: str | None = None,
) -> Classification:
    """Apply the three tie-breakers from spec/decision-classes.md section 3.

    Each can only move a decision to a more expensive class, never a cheaper one.

    Args:
        reversible_within_cycle: T1. If the decision were wrong and undetected for
            one full review cycle, could it be undone at bounded cost?
        undo_costs_more_than_decision: T1 continued. Used only when
            ``reversible_within_cycle`` is False; True sends it to D rather than C.
        second_opinion: T2. Another qualified classifier's answer. Disagreement
            resolves to the more expensive class, and the disagreement is recorded
            in ``tiebreakers_applied`` so it can be logged.
    """
    result = base.decision_class
    applied: list[str] = []

    if reversible_within_cycle is False:
        target = "D" if undo_costs_more_than_decision else "C"
        escalated = more_expensive(result, target)
        if escalated != result:
            applied.append(
                f"T1 reversibility: not reversible within one review cycle, "
                f"escalated {result} to {escalated}"
            )
            result = escalated

    if second_opinion is not None:
        if second_opinion not in CLASS_EXPENSE:
            raise ValueError(f"second_opinion is not a decision class: {second_opinion!r}")
        if second_opinion != result:
            escalated = more_expensive(result, second_opinion)
            applied.append(
                f"T2 disagreement: classifiers split {result} against {second_opinion}, "
                f"resolved to {escalated}. Log both rationales; disagreement rate is a "
                f"property of the rubric, not of the people."
            )
            result = escalated

    if not applied:
        return base

    return Classification(
        decision_class=result,
        tree_class=base.tree_class,
        path=base.path,
        tiebreakers_applied=tuple(applied),
        rationale=base.rationale,
    )


def _rationale(path: Sequence[tuple[str, bool]], result: str) -> str:
    if not path:
        return f"Class {result}."
    last_id, last_answer = path[-1]
    last = TREE[last_id]
    return (
        f"Class {result}, {CLASS_NAMES[result]}. Reached at {last_id} "
        f"({'yes' if last_answer else 'no'}): {last.prompt}"
    )


def describe_tree() -> str:
    """The tree as text, for `vb classify --tree`."""
    lines = ["Classification tree. Apply in order, stop at the first terminal.", ""]
    for question in TREE.values():
        lines.append(f"  {question.id}. {question.prompt}")
        lines.append(f"        yes -> {_target_label(question.yes)}")
        lines.append(f"        no  -> {_target_label(question.no)}")
        if question.help:
            lines.append(f"        note: {question.help}")
        lines.append("")
    lines.append("Tie-breakers, applied after the tree. Each can only make a class more expensive.")
    lines.append("  T1 reversibility  wrong and undetected for one cycle, undoable at bounded cost?")
    lines.append("  T2 disagreement   two qualified classifiers split, take the more expensive")
    lines.append("  T3 default        anything unclassified is Class D until classified")
    return "\n".join(lines)


def _target_label(target: str) -> str:
    if target.startswith("class:"):
        letter = target.split(":", 1)[1]
        return f"CLASS {letter} ({CLASS_NAMES[letter]})"
    return f"question {target}"


# ---------------------------------------------------------------------------
# Interactive walk
# ---------------------------------------------------------------------------

_YES = {"y", "yes", "true", "1"}
_NO = {"n", "no", "false", "0"}


def _ask(
    prompt: str,
    help_text: str,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> bool:
    while True:
        output_fn("")
        output_fn(prompt)
        raw = input_fn("  yes / no / why > ").strip().lower()
        if raw in _YES:
            return True
        if raw in _NO:
            return False
        if raw in {"why", "?", "help"}:
            output_fn(f"  {help_text}" if help_text else "  No further guidance for this one.")
            continue
        output_fn("  Answer yes or no, or type why for guidance.")


def walk(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    decision_type: str | None = None,
    ask_tiebreakers: bool = True,
) -> Classification:
    """Interactive classification. Returns the classified result.

    ``input_fn`` and ``output_fn`` are injectable so this is testable without a
    terminal. The walk asks only the questions the tree actually reaches.
    """
    output_fn("VERB classifier. Cost of checking, not risk, not task difficulty.")
    if decision_type:
        output_fn(f"Decision type: {decision_type}")
    output_fn("Type why at any prompt for guidance.")

    answers: dict[str, bool] = {}
    node_id = ROOT
    while not node_id.startswith("class:"):
        question = TREE[node_id]
        answers[question.id] = _ask(
            f"{question.id}. {question.prompt}", question.help, input_fn, output_fn
        )
        node_id = question.target(answers[question.id])

    result = classify(answers)

    if ask_tiebreakers and result.decision_class != "D":
        output_fn("")
        output_fn("Tie-breaker T1, reversibility.")
        reversible = _ask(
            "  If this were wrong and undetected for one full review cycle, "
            "could it be undone at bounded cost?",
            "This overrides the tree. A decision that cannot be undone within a cycle is "
            "at least Class C, whatever the tree said.",
            input_fn,
            output_fn,
        )
        undo_expensive: bool | None = None
        if not reversible:
            undo_expensive = _ask(
                "  Would undoing it cost more than making the decision in the first place?",
                "Yes sends this to Class D. Class D is prepared by agents and decided by humans.",
                input_fn,
                output_fn,
            )
        result = apply_tiebreakers(
            result,
            reversible_within_cycle=reversible,
            undo_costs_more_than_decision=undo_expensive,
        )

    output_fn("")
    output_fn(format_classification(result, decision_type))
    return result


def format_classification(result: Classification, decision_type: str | None = None) -> str:
    """Human-readable summary. Shared by the interactive walk and the CLI."""
    lines: list[str] = []
    header = f"CLASS {result.decision_class}  {CLASS_NAMES[result.decision_class]}"
    if decision_type:
        header = f"{decision_type}: {header}"
    lines.append(header)
    lines.append("-" * max(48, len(header)))

    cost = result.typical_cost_hours
    if cost is None:
        lines.append("  typical c        undefined. Not high. Undefined.")
    else:
        lines.append(f"  typical c        {cost[0]:g} to {cost[1]:g} h  (indicative, PMO-shaped, measure your own)")
    lines.append(f"  agent authority  {result.authority}")
    lines.append("")
    lines.append("  path")
    for node_id, answer in result.path:
        lines.append(f"    {node_id:<4} {'yes' if answer else 'no ':<4} {TREE[node_id].prompt[:66]}")

    if result.tiebreakers_applied:
        lines.append("")
        lines.append("  tie-breakers")
        for note in result.tiebreakers_applied:
            lines.append(f"    {note}")

    lines.append("")
    if result.decision_class == "D":
        lines.append("  Class D is never delegated to an agent. The agent prepares it and a human")
        lines.append("  decides. The preparation is a Class C artifact and consumes Class C budget.")
    elif result.decision_class == "C":
        lines.append("  Class C is proposed by the agent and decided by a human. This is where")
        lines.append("  verification budget is actually spent and where overdraft accumulates.")
    else:
        lines.append("  Measure c before you deploy. An estimated c produces a budget that")
        lines.append("  restates your assumptions in the shape of arithmetic.")
    return "\n".join(lines)
