# Reconciliation record, v0.1.0

The framework was drafted twice: once as a talk, once as this specification. The two drafts disagreed in three places. This file records how the disagreements were settled and why, so that anyone reading an older slide or an older commit can tell which version is current.

**The specification in `/spec` is authoritative.** Where the talk and the spec differ, the spec as amended by this file wins.

In two of the three cases the talk was right and the spec has been changed to match. That is worth stating plainly rather than quietly editing.

---

## 1. Agent role contract fields

| Draft | Fields |
|---|---|
| Talk | Scope, Output contract, Verification method, Escalation trigger |
| Spec | Scope, Evidence, Escalation, Revocation |

### What was actually different

Three of the four line up. `Output contract` is the typed-structure half of `Evidence`. `Escalation trigger` is `Escalation`. `Scope` is `Scope`.

The real disagreement is the fourth field. The talk names **Verification method**: the class, plus who or what checks it, plus the sampling rate. The spec names **Revocation**: how the agent gets turned off.

### Settled

**Keep the spec's four names. Absorb Verification method into Scope.**

Revocation stays, because an agent you cannot stop is not governed, and no other field substitutes for it. The talk's omission of revocation was a gap, not a choice.

But the talk was right that the spec had nothing saying **who checks this**. The spec's scope entries carried a `decision_class`, which is the cost of checking, and then said nothing about who does the checking or how. That is a hole: two decision types can both be Class C and be checked by different people under different sampling.

So each scope entry now carries three more fields:

```yaml
- decision_type: milestone_slip_categorisation
  decision_class: B          # what checking costs
  verified_by: sample        # how it is checked
  checker_role: pmo_analyst  # who checks it
  sampling_rate: 0.15
  authority_level: 2         # see section 3
```

`verified_by` is one of `machine`, `sample`, `expert`, `committee`, `human_only`. It must be consistent with the class: a Class A entry verified by `expert` is either misclassified or wasting an expert.

Verification method belongs inside Scope rather than beside it because it is a property of the decision type, not of the agent. The same decision type is checked the same way whichever agent produces it.

### Changed files

`spec/agent-role-contract.md` section 2.1, `schema/agent-contract.schema.json` `$defs/scopeEntry`.

---

## 2. Evidence plane fields

| Draft | Fields |
|---|---|
| Talk | claim, sources, counter-case, blast radius, reversal path, confidence basis |
| Spec | decision, basis, alternatives, confidence_and_failure_mode, reversal, owner |

### What was actually different

| Talk | Spec | Same thing? |
|---|---|---|
| claim | `decision` | Yes |
| sources | `basis` | Yes |
| counter-case | `confidence_and_failure_mode.failure_mode` | Yes |
| reversal path | `reversal` | Yes |
| confidence basis | `confidence_and_failure_mode.calibration_basis` | Yes |
| **blast radius** | nothing | **No. Missing from the spec.** |
| nothing | **`owner`** | **No. Missing from the talk.** |
| nothing | `alternatives` | No. See below. |

Two genuine gaps in opposite directions, and one field that exists only in the spec.

**`alternatives` and counter-case are not the same field.** A counter-case is the strongest reason the chosen answer is wrong. Alternatives are the other answers and why each was rejected. They do different work: `failure_mode` tells the reviewer where to look inside the chosen decision, `alternatives` bounds the question from unbounded ("is this right?") to bounded ("is one of these rejection reasons wrong?"). Both stay.

**Blast radius was a real omission.** The spec had `reversal` (how to undo, what undoing costs, how long undo stays cheap) but never asked what breaks if the decision is acted on and turns out wrong. Those are different questions. A decision can be cheap to reverse and still have done damage in the meantime.

### Settled

**Six fields stays. `blast_radius` becomes a required sub-field of `reversal`.**

```json
"reversal": {
  "blast_radius": "Programme board receives an understated slip figure. Two dependent workstreams plan against a date that is 11 days optimistic. No external or contractual exposure.",
  "how": "Re-run categorisation with corrected cause code, re-issue slip notice to programme board.",
  "cost_hours": 0.5,
  "cheap_until": "2026-09-02T00:00:00Z",
  "cheap_until_reason": "Programme board pack lock for the September cycle."
}
```

Why merge rather than add a seventh field: blast radius and reversal are the same question asked twice, and the reviewer uses them together in one judgement, which is how hard to look. Splitting them across two fields makes the reviewer assemble the picture from two places. Keeping them together also holds the field count at six, and six is a real constraint rather than a preference. A seven-field plane is a plane where the seventh field is skipped.

`owner` stays. The talk's six fields had nobody accountable, which is the diffusion that makes review optional.

### One claim had to be adjudicated

The talk says the counter-case is "the field that changes verification time the most". The spec says `basis` is, at 40 to 60 percent of `c`.

Both are true about different things and the spec now says so. `basis` removes the largest block of *time*, because it deletes retrieval the reviewer would otherwise redo. The counter-case changes the *quality of attention*, because it converts an even read of the whole artifact into a search for one named thing. The time saving is `basis`. The error-catching improvement is the counter-case. Neither replaces the other.

### Changed files

`spec/evidence-plane.md` section 2.5, `schema/decision-artifact.schema.json` `reversal`, `README.md` section 6.

---

## 3. Authority: a second axis the spec did not have

Not a disagreement. Something the talk had and the spec had not.

The spec derived agent authority from class alone: Class A and B decide, Class C proposes, Class D prepares. That is right about cost and wrong about consequence. A Class A decision can be irreversible, and a Class C decision can be trivially undoable, and the spec had no way to say so.

The talk had a five-level ladder keyed to **blast radius**, and the tell that it was the better model is what it leaves out: model confidence appears nowhere in it. Confident and wrong on an irreversible decision is still a disaster.

### Settled

**Two axes, both required.**

> **Class sets the cost of checking. Blast radius sets the authority. A decision needs both before an agent touches it.**

| Level | Authority | Test that puts you here |
|---|---|---|
| 1 | Agent acts, logs only | Reversible within a day, no external party affected |
| 2 | Agent acts, human notified | Reversible within a week, internal only |
| 3 | Agent proposes, one human approves | Reversible with effort, or affects one team's plan |
| 4 | Agent proposes, committee approves | Hard to reverse, or touches cost, contract or compliance |
| 5 | Human decides, agent supports only | Irreversible, or legally accountable |

The two axes constrain each other. Class C caps authority at level 3, because a decision a human must reconstruct cannot be one an agent takes unilaterally. Class D forces level 5. But a Class A decision with a level 4 blast radius stays at level 4: cheap to check does not mean safe to decide alone.

The full table, the interaction rules and the worked cases are in [`decision-classes.md` section 5](decision-classes.md#5-class-authority-and-blast-radius). Scope entries now carry `authority_level`, and `vb classify` asks for blast radius.

### Changed files

`spec/decision-classes.md` section 5, `schema/agent-contract.schema.json`, `vb/classify.py`, `README.md` section 3.

---

## 4. Eval gates

| Draft | Gates |
|---|---|
| Talk | Replay, Adversarial, Cost measurement, Escalation recall |
| Spec | Classification, Evidence, Verifier calibration, Replay |

Seven distinct gates across two drafts, one shared. Both drafts insist the number is four.

### What each draft got right

The talk had two gates the spec did not, and both are load-bearing.

**Cost measurement.** Three reviewers, twenty real outputs, a stopwatch. The spec treated this as a measurement protocol living inside section 0 of `metrics.md`, and only checked it indirectly through Gate 2 criterion 2.3. The talk makes it a gate and says why: without `ĉ` the verification budget is fiction. Demoting the one number the whole model rests on to an appendix was a mistake.

**Escalation recall.** Inject conditions that must trigger a handoff, and require every one of them to trigger. The spec listed escalation recall under known limitations as something you cannot measure directly, and offered injected probes as a partial proxy. The talk correctly treats injection as the measurement rather than a proxy for one, and sets the bar at 100 percent rather than a percentage. You are not sampling a population, you are testing whether a safety mechanism fires.

**Adversarial** was also missing for ordinary agents. The spec only ran known-bad cases against verifiers, inside Gate 3. Every agent should meet the cases from your own lessons-learned register, and a confident wrong answer on a case you already know is hard should be disqualifying.

The spec had two the talk did not, and both are also load-bearing. **Classification** agreement, because a class nobody agrees on gives a `c` nobody can use. **Verifier calibration**, because containment banked without a measured false-negative rate is a risk transfer wearing the costume of a cost reduction, and the autonomous part of the operating model rests entirely on it.

### Settled

Four gates, each answering one question, absorbing all seven.

| Gate | Question | Absorbs |
|---|---|---|
| **1. Classification and cost** | Do we agree what class this is, and what does checking actually cost? | spec Classification + talk Cost measurement |
| **2. Evidence** | Can every decision be checked at the cost we assumed? | spec Evidence |
| **3. Adversarial** | Does it fail safely on the cases we already know are hard, and is any containment we bank real? | talk Adversarial + talk Escalation recall + spec Verifier calibration |
| **4. Replay** | Would it have been right on history, and did it stay inside its scope? | spec Replay + talk Replay |

Two things moved and both moves matter.

**Cost measurement is now criterion 1.3, in the first gate.** The talk's own note about it was that it is the gate that gets skipped and the only one that tells you how far you can scale. Putting it in Gate 1, alongside the classification it belongs to, makes skipping it a Gate 1 failure. Classification and cost are one question anyway: a class without a measured cost is a label.

**Escalation recall is now criterion 3.2, at 100 percent, and is no longer a stated limitation.** The known-limitations list has been amended: escalation recall is measurable by injection, the framework requires it, and what remains unmeasurable is only recall against failure modes nobody has thought to inject. That is a narrower and more honest claim than the one the spec made before.

Full criteria, procedures and failure handling: [`eval-gates.md`](eval-gates.md).

### Changed files

`spec/eval-gates.md` in full, `vb/gates.py`, `README.md` section 8 and limitation 5, `spec/metrics.md` section 5.

---

## 5. What did not change

For completeness, the parts both drafts already agreed on and which are unamended:

- The formula `VB = (R × H × u) / c`, and that `c` is the only lever with real range in it.
- Four classes defined by cost of checking, not by risk and not by task difficulty.
- The deployment inversion. The talk's `GO FIRST` / `GO SECOND` / `HOLD` / `NEVER YET` labels are now used in the README quadrant, because named actions beat named quadrants.
- Silent drift as the headline metric, measured against a per-class floor derived from your own baseline.
- Class D never delegated, delivered as Class C preparation artifacts.
- No S5.

---

## 6. Version note

Everything above is folded into v0.1.0. There is no earlier released version, so nothing downstream needs migrating. This file exists because the talk circulated before the repository did, and anyone working from those slides should know which four fields and which four gates are current.

Later reconciliations get appended here rather than overwriting, with a dated heading.
