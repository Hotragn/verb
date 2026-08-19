# The evidence plane

Normative specification. Short form in [README section 6](../README.md#6-the-evidence-plane). Machine-readable form in [`schema/decision-artifact.schema.json`](../schema/decision-artifact.schema.json).

---

## 1. What it is for

The evidence plane is the set of fields every agent decision must carry. Six of them.

> **The evidence plane exists to reduce `c`.**

That sentence decides every design question in this document. It is not an audit trail. An audit trail is optimised for reconstructing the past, months later, for somebody who was not there. The evidence plane is optimised for making the *next* review fast, today, for somebody who has eleven other decisions in their queue. Those two goals produce different artifacts, and only one of them changes the verification budget.

The practical difference: an audit trail wants completeness. The evidence plane wants the reviewer to reach a defensible yes or no in the shortest possible time. Where those conflict, the evidence plane wins, because a complete record of a decision nobody has capacity to check is a record of an unverified decision.

### The measurement that motivates it

Ask three reviewers what takes the time in a Class C review. The answer is consistently the same shape:

| Activity | Share of `c` |
|---|---|
| Working out what was actually decided | 5 to 10 percent |
| **Re-gathering the inputs the agent already had** | **40 to 60 percent** |
| Judging whether the reasoning holds | 20 to 30 percent |
| Deciding how hard to look | 10 to 15 percent |

The largest block is the reviewer redoing retrieval that already happened. `basis` exists to delete that block. The rest of the fields attack the other rows in the table, and every field in the plane maps to a row. If you propose a seventh field, say which row it reduces. If it does not reduce one, it belongs in the audit trail.

### The enforcement rule

> **A decision artifact missing any of the six fields is not a decision. It is an output. Outputs must not be actioned.**

This is a schema check in the pipeline, not a guideline in a document. It is [Gate 2](eval-gates.md#gate-2-evidence).

---

## 2. Field specifications

### 2.1 `decision`

**Type.** String. One sentence.

**Definition.** What was decided, stated as an action, with the object identified by a stable ID.

**Rules**

- One sentence. If it needs two, it is two decisions and they need two artifacts.
- Stated as an action taken, not a state observed. "Categorise slip on MS-PRG7-014 as supplier-caused" is a decision. "MS-PRG7-014 appears supplier-caused" is an observation.
- The object carries a stable ID, not a name. Names change and are ambiguous across systems.
- Includes the material quantities. "Eleven working days, absorbed by float" belongs in the sentence, because a reviewer who has to open another field to learn the size of the thing has already spent time.
- No hedging. "Categorise as probably supplier-caused" moves uncertainty into the wrong field. Uncertainty goes in `confidence_and_failure_mode`.

**Reduces.** "Working out what was actually decided", 5 to 10 percent of `c`.

That share sounds too small to bother with. It is not, because it comes first: a reviewer who is unsure what they are approving reads everything else defensively and slowly. This field sets the frame for the entire review.

**Good**

> Categorise slip on milestone MS-PRG7-014 as supplier-caused, 11 working days, absorbed by float.

**Bad**

> Analysis of the milestone slip and its causes, with recommendations for the programme team.

That is a description of an artifact, not a decision. A reviewer cannot approve or reject it.

---

### 2.2 `basis`

**Type.** Array of objects. Each with `source_id`, `retrieved_at`, `detail`.

**Definition.** The actual inputs the decision rested on. A list, not a summary.

**Rules**

- **B1.** `source_id` must be resolvable. A reviewer clicks it and lands on the source. `"the project plan"` is not a source ID. `"P6:PRG7:baseline:v12"` is.
- **B2.** `retrieved_at` is when the agent read it, not when the decision was made. The gap between them is where stale-input errors live, and a reviewer who can see a three-day gap knows to check.
- **B3.** `detail` is the specific fact used, not a description of the source. `"Baseline finish 2026-09-30, float 14d"` is the fact. `"Contains schedule information"` is a description and is worthless.
- **B4.** Every material claim in `decision` traces to at least one basis entry. This is checkable and Gate 2 checks it.
- **B5.** Include inputs that were retrieved and did not change the outcome. Reviewers use these to confirm the agent looked. Omitting them makes the artifact look thin and slows the review down, which is the opposite of the point.
- **B6.** Do not include an input the agent did not actually read. This turns out to be the highest-value integrity property in the whole plane, because a `basis` a reviewer cannot trust is worse than no `basis`: they re-gather everything and you have paid the token cost for nothing.

**Reduces.** "Re-gathering the inputs", 40 to 60 percent of `c`. This is the field that pays for the evidence plane.

**Good**

```json
[
  {"source_id": "P6:PRG7:baseline:v12", "retrieved_at": "2026-08-19T09:13:58Z",
   "detail": "Baseline finish 2026-09-30, float 14d"},
  {"source_id": "JIRA:PRG7-2291", "retrieved_at": "2026-08-19T09:14:01Z",
   "detail": "Supplier confirmed delay in writing 2026-08-15"},
  {"source_id": "SUP:ACME:SLA:2025-11", "retrieved_at": "2026-08-19T09:14:03Z",
   "detail": "SLA clause 7.2, notification requirement met"}
]
```

**Bad**

```json
[
  {"source_id": "schedule data", "retrieved_at": "2026-08-19T09:14:22Z",
   "detail": "Reviewed the schedule and supplier correspondence"}
]
```

Fails B1 (not resolvable), B3 (describes rather than states), and the timestamp equals the decision time, which suggests it was written rather than recorded.

---

### 2.3 `alternatives`

**Type.** Array of objects. Each with `option` and `rejected_because`. Minimum one entry, or an explicit `forced` object.

**Definition.** What was considered and rejected, and why.

**Rules**

- **A1.** At least one alternative, or `{"forced": true, "reason": "..."}` stating why no alternative existed. Forced decisions are real. A milestone that has slipped has slipped. But `forced` is checkable and Gate 2 samples it, because it is the obvious place to hide a thin artifact.
- **A2.** `rejected_because` states a specific reason with a fact in it. "Not applicable" is not a reason. "No approved change request in the window; CR-PRG7-0088 closed 2026-07-02" is a reason.
- **A3.** Alternatives must be options a competent person would actually have considered. Straw men make the artifact longer and the review slower, which is a direct cost. Gate 2's human sample exists mainly to catch this.
- **A4.** Where an alternative was rejected on a judgement rather than a fact, say so: `"rejected_because": "Judgement: the commercial relationship does not survive a second formal notice this quarter."` A reviewer treats judgement rejections differently from factual ones, and correctly so.

**Reduces.** "Judging whether the reasoning holds", 20 to 30 percent of `c`.

The mechanism is worth stating precisely, because it is the least obvious thing in this document. Without `alternatives`, the reviewer's question is *"is this right?"*, which is unbounded: they must generate the option space themselves, then check each branch. With `alternatives`, the question becomes *"is one of these rejection reasons wrong?"*, which is a bounded check over a list that is already written down. The first question has no natural stopping point. The second does. That is the whole of the saving, and it is why one honest alternative beats four decorative ones.

---

### 2.4 `confidence_and_failure_mode`

**Type.** Object. `confidence` (number 0 to 1), `failure_mode` (string), `calibration_basis` (string).

**Definition.** How confident the agent is, and the specific way this decision would be wrong.

**Rules**

- **C1.** `confidence` is calibrated, and `calibration_basis` says against what. `"Reliability measured on 240 labelled categorisations, 2026-Q2. Brier score 0.09."` An uncalibrated confidence is a number with no units and reviewers learn to ignore it, which wastes the field.
- **C2.** `failure_mode` names a **specific, detectable** failure. Three parts: the condition under which the decision is wrong, the consequence, and where it would show up.
- **C3.** "May be inaccurate" and its variants are prohibited. They carry no information and they train reviewers to skip the field.
- **C4.** Where possible, `failure_mode` states *when* the failure would become visible. This is what lets a reviewer decide whether to check now or wait for the checkpoint, and waiting is sometimes correct.

**Reduces.** "Deciding how hard to look", 10 to 15 percent of `c`, and it improves the quality of the remaining review by pointing it somewhere.

A named failure mode is a search target. The reviewer stops reading the artifact evenly and starts looking for one thing. This is a large speed difference in practice and it is why the field is `confidence_and_failure_mode` rather than `confidence`: a confidence number on its own tells the reviewer how worried to be but not where to look, and "worried but undirected" is the most expensive state a reviewer can be in.

**Good**

**Good**

```json
{
  "blast_radius": "Programme board receives an understated slip figure. Two dependent workstreams plan against a date 11 days optimistic. No external or contractual exposure. Authority level 2.",
  "how": "Re-run categorisation with corrected cause code, re-issue slip notice to programme board.",
  "cost_hours": 0.5,
  "cheap_until": "2026-09-02T00:00:00Z",
  "cheap_until_reason": "Programme board pack lock for the September cycle."
}
```

_The confidence example, for contrast:_

```json
{
  "confidence": 0.86,
  "failure_mode": "If the supplier delay is a symptom of an undisclosed resource loss on their side, the 11-day figure understates the slip and float absorption is wrong. Detectable at the next supplier checkpoint on 2026-08-26.",
  "calibration_basis": "Reliability measured on 240 labelled categorisations, 2026-Q2. Brier score 0.09."
}
```

**Bad**

```json
{
  "confidence": 0.86,
  "failure_mode": "The categorisation may be inaccurate if the underlying data is incorrect.",
  "calibration_basis": "Model confidence."
}
```

Fails C1 (model self-report is not calibration), C2 (not specific, not detectable), C3 (prohibited phrasing), C4 (no time).

---

### 2.5 `reversal`

**Type.** Object. `blast_radius`, `how`, `cost_hours`, `cheap_until`, `cheap_until_reason`.

**Definition.** What breaks if the decision is acted on and turns out wrong, how to undo it, what undoing costs, and the window in which undoing is still cheap.

**Rules**

- **R0.** `blast_radius` states what is affected if this decision is acted on and is wrong. Who is downstream, what plans against it, and whether any external or contractual party is exposed. This is a different question from reversal cost: a decision can be cheap to undo and still have done damage while it stood.
- **R1.** `how` is a procedure, not a sentiment. "Re-run categorisation with corrected cause code, re-issue slip notice to programme board" is a procedure. "Can be revisited" is not.
- **R2.** `cost_hours` is the cost of reversal, in the same units as `c`, so the two can be compared. This comparison is what makes the field actionable.
- **R3.** `cheap_until` is a timestamp, and `cheap_until_reason` says what changes at that moment. The reason is usually an external commitment: a board pack lock, an invoice run, a supplier notification deadline, a public announcement.
- **R4.** If reversal is impossible, the decision is Class D and should not have been made by an agent. An agent emitting an artifact with no reversal path has classified something wrongly, and that is an escalation, not a field to leave blank.

**Reduces.** "Deciding how hard to look", the other part of the 10 to 15 percent.

The mechanism is proportionate review, made honest. A reviewer who can see that a decision costs half an hour to reverse and stays cheap for two weeks can consciously choose a lighter check. Without the field they either check everything at full cost, or they check lightly on an unstated assumption about reversibility. The second is what actually happens, and the evidence plane's contribution is to turn an unstated assumption into a stated fact that can be wrong and be caught.

**Why blast radius lives here rather than in its own field.** Blast radius and reversal are the same question asked twice: what happens if this is wrong, and how do I get out of it. A reviewer uses both in a single judgement, which is how hard to look. Splitting them across two fields makes the reviewer assemble one picture from two places, and it pushes the plane to seven fields, which is a plane whose seventh field gets skipped.

Blast radius also does a second job the rest of the plane cannot: it sets the **authority level** for the decision type. Class tells you what checking costs. Blast radius tells you who is allowed to decide. Both are needed, and the ladder is in [decision-classes.md section 5](decision-classes.md#5-class-authority-and-blast-radius).

**The cross-check.** If `reversal.cost_hours` is routinely underestimated, `reversal_latency`, one of the [six metrics](metrics.md), will show it: reversals that consistently happen after `cheap_until` mean the field is fiction and any class assignment that relied on reversibility needs revisiting. This is the only field in the plane with a metric dedicated to auditing it, because it is the field most likely to be optimistic.

---

### 2.6 `owner`

**Type.** Object. `person_id`, `name`, `role`, `resolved_at`.

**Definition.** The named human accountable for this decision.

**Rules**

- **O1.** Resolved to a **person**, not a role, **at decision time**. `"role": "portfolio_scheduler"` is metadata. `"person_id": "u-2291"` is the field.
- **O2.** `resolved_at` is when the resolution happened. If the role-holder changed afterwards, accountability stays with the person who held it at decision time.
- **O3.** If the role cannot resolve to a person, the agent escalates rather than deciding. An unowned decision is an unverifiable decision, because there is nobody whose review would mean anything.
- **O4.** The owner is accountable for the decision, not for having personally reviewed it. This distinction matters: under overdraft, some decisions carry an owner and no genuine review, and pretending otherwise is exactly the silent drift this framework exists to measure. Owner is who answers for it. Whether they checked it is what `silent_drift_rate` measures.

**Reduces.** No single row of the table directly. It protects the whole plane.

Accountability diffusion is what makes review optional. When a decision belongs to "the schedule team", every individual's rational calculation is that somebody else will check it, so nobody does, and the queue drains at a rate that looks like verification. A named owner removes that. It is the cheapest field to implement and the one most often reduced to a role, because resolving a role to a person at decision time requires a live directory and somebody has to build it.

---

## 3. Class-specific additions

The six are mandatory for every class. Some classes need more.

| Class | Additional fields | Why |
|---|---|---|
| A | none | The deterministic check is the verification. Extra fields add cost with no reduction in `c`. |
| B | `batch_id`, `sampled` (bool), `rubric_version` | Sampling only bounds a batch if you can identify the batch and know which rubric produced it. |
| C | `precedent_cases`, `stakeholder_positions`, `second_order_impacts` | These are the three things a Class C reviewer looks for that are not in the base six, and each is retrieval the reviewer would otherwise redo. |
| D preparation | `recommendation`, `options_with_costs`, `reversal_cost_of_each_option`, and **no `decision` field** | The pack recommends. The human decides. The absence of `decision` is the structural guarantee, and it is machine-checkable. |
| Verifier | `verdict`, `proof_object`, `calibration_record_ref` | Rules E3 and E4 in [agent-role-contract.md](agent-role-contract.md#22-evidence). The proof object must be machine re-checkable or the verifier supplies no containment. |

Class D preparation packs are the case worth checking in code: a preparation artifact containing a `decision` field is an agent that has made a Class D decision, whatever its contract says. The schema enforces this and Gate 4 catches it on replay.

---

## 4. Anti-patterns

**The audit trail in disguise.** Twenty fields, complete provenance, immutable hashes, and a `c` that went up rather than down. Test: measure `c` before and after. If it rose, you built an audit trail. Keep it if you need one, but do not call it an evidence plane and do not credit it in the budget.

**`basis` as summary.** One entry saying "reviewed the schedule and supplier correspondence". Fails B1 and B3, and the reviewer re-gathers everything, which means the largest block of `c` is untouched and you paid the token cost anyway.

**Alternatives as theatre.** `"option": "Do nothing", "rejected_because": "Not appropriate"` on every artifact. Passes schema. Contributes nothing. This is the most common quiet degradation and it is why Gate 2 has a human sample rather than only a schema check.

**Confidence without calibration.** A number the model produced about itself. Reviewers learn within about two weeks that it does not correlate with correctness, and then they ignore the field, and then the field costs tokens and saves nothing.

**Reversal as reassurance.** `"how": "This can be revisited if needed"`. Fails R1. It also quietly encourages lighter review on a decision that may not be reversible at all.

**Owner as role.** `"owner": "PMO"`. Fails O1. Accountability diffuses and the review becomes optional, which is where this whole document started.

**Evidence in the document, optional in the pipeline.** Required by policy, unenforced by code. Degrades within a quarter. Gate 2 exists for this and it must be automated, because the failure is silent.

---

## 5. Validation

```bash
vb gates --input examples/pmo40 --gate evidence
```

Machine-checkable:

- All six fields present and correctly typed.
- `basis` non-empty, every entry has a resolvable-shaped `source_id`, `retrieved_at` parses and precedes the decision timestamp.
- `alternatives` non-empty, or `forced` present with a reason.
- `confidence` in [0, 1]. `failure_mode` non-empty and not matching the prohibited phrase list.
- `reversal.cost_hours` present and numeric. `cheap_until` parses.
- `owner.person_id` present and non-empty.
- Class-specific additions present for the artifact's class.
- Class D preparation artifacts contain no `decision` field.

Not machine-checkable, which is why Gate 2 has a human sample of 20:

- Whether `basis` entries were actually read.
- Whether `alternatives` are real options or straw men.
- Whether `failure_mode` names a failure that could actually occur.
- Whether `reversal.cost_hours` is honest.

Schema: [`schema/decision-artifact.schema.json`](../schema/decision-artifact.schema.json). Fixtures in [`schema/fixtures`](../schema/fixtures), including invalid ones for each rule above.
