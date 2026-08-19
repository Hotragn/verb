# Decision classes

Normative specification. The summary in [README section 3](../README.md#3-the-four-decision-classes) is the short form. This is the version to use when two people disagree.

---

## 1. The classifying principle

> A decision's class is determined by **the cost of verifying it**, measured in qualified human hours, given the evidence that actually accompanies the decision in your organisation.

Three things follow, and all three catch people out.

**Class is not risk.** A decision can be high risk and Class A. Reconciling a 40 million currency-unit budget rollup against the ledger is high risk and machine-checkable in nine seconds. A decision can be low risk and Class C. Whether a minor dependency should be renegotiated with a partner team is low risk and needs somebody who knows what happened in March. Risk tells you *whether* you must check. Class tells you *what checking costs*. Both are needed. Only one is usually present.

**Class is not task difficulty.** How hard the decision is for the model has no bearing on its class. A model that is superb at vendor dispute strategy does not make vendor dispute strategy cheaper to check. This is the single most common classification error and it is the reason for [the deployment inversion](../README.md#4-the-deployment-inversion).

**Class is a property of the triple `(decision type, organisation, evidence available)`.** Not of the decision type alone. The same decision type is Class C in an organisation where the context lives in people's heads, and Class A in an organisation that instrumented that context three years ago. This is good news: class is something you can change. See [section 6](#6-reclassification).

---

## 2. Class definitions

### Class A: machine-checkable

**Definition.** A deterministic check exists that decides correctness, and acting on its verdict costs a qualified human under five minutes. The human sees exceptions, not decisions.

**Necessary conditions, all of them:**

1. The check is deterministic. Same input, same verdict, every time.
2. The check's verdict is the answer, not an input to a judgement. If a human still has to weigh the verdict against something else, it is not Class A.
3. The check is executable without human setup per decision.
4. The exception rate is low enough that exception handling does not itself blow the budget. Rule of thumb: under 5 percent.

**Typical c:** 0.01 to 0.05 hours, and that figure is almost entirely exception handling amortised across the population.

**PMO examples**

| Decision type | The deterministic check |
|---|---|
| Critical path recalculation | Recompute forward and backward pass, compare |
| Dependency cycle flagging | Cycle detection on the dependency graph |
| Budget rollup reconciliation | Sum of children equals parent, compare to the ledger |
| RAID register completeness | Required fields present, owners resolve to real people, dates parse |
| Timesheet compliance | Hours against contract, against calendar, against project codes |
| Invoice to purchase-order match | Three-way match, tolerance thresholds |
| Baseline variance thresholds | Variance against baseline against tolerance |
| Resource over-allocation | Sum of allocations per person per period against capacity |
| Float erosion alert | Float against threshold against previous period |

**The tell.** You can write the check as a test, and the test passing means the decision is right.

**Where it goes wrong.** People classify things as A because a script exists, when the script only produces an *input* to the decision. A variance report is not a check. A variance report plus a threshold plus "flag if over" is a check.

---

### Class B: sample-checkable

**Definition.** No single deterministic test decides an individual case, but decisions arrive as a homogeneous population governed by one rubric, so checking a sample bounds the error rate for the batch.

**Necessary conditions, all of them:**

1. **Population homogeneity.** The decisions are the same kind of decision on different objects. Different rubrics means different populations.
2. **Volume.** At least 30 per period. Below that, a sample bounds nothing and you are just checking a few of them.
3. **Bounded consequence spread.** No decision in the population is much more consequential than the others. This is the condition that fails most often.
4. **A rubric a sampler can apply.** If two samplers would disagree about whether a sampled decision was correct, the population is Class C.

**Typical c:** 0.05 to 0.25 hours amortised. The arithmetic:

```
        c_B = (sample size × cost per sampled review) / batch size
```

A batch of 200 with a 20-decision sample at 1.2 hours each gives `c_B = 24 / 200 = 0.12` hours.

**Sample size.** Use the standard bound for a proportion, not a fixed 10 percent. To be 95 percent confident the true error rate is below `p`, with an observed error rate of zero, the sample size is approximately `n ≈ 3 / p`. For `p = 0.05`, `n ≈ 60`. For `p = 0.10`, `n ≈ 30`. Choose `p` from the risk of the population, which is where risk finally enters the model.

**PMO examples:** status narrative drafting across a portfolio, action extraction from meeting minutes, risk re-scoring against a fixed rubric, change-request categorisation, first-pass supplier invoice queries, weekly RAG rating proposals, stakeholder update personalisation, lessons-learned tagging.

**The tell.** You would be comfortable checking twenty and drawing a conclusion about the other two hundred. If that sentence makes you uncomfortable, it is not Class B.

**Where it goes wrong.** Condition 3. A batch of 200 status narratives usually contains three that go to the board. A sample will miss them. Two fixes, in order of preference: **stratify** the population so the consequential ones form their own Class C stream, or **reclassify** the whole population to C. Averaging over them is the failure this class is most prone to, and it is invisible until the board sees the wrong number.

---

### Class C: expert-checkable

**Definition.** A qualified human can determine correctness in bounded time, but doing so requires reconstructing the reasoning against context that is not in the artifact.

**Necessary conditions:**

1. A qualified reviewer exists and can be named.
2. Checking terminates in bounded time. If a reviewer could spend arbitrary time and still not be sure, it is Class D.
3. The context needed is retrievable, even if slowly and even if the retrieval is a phone call.
4. The decision is reversible within a bounded cost, or its consequences are observable inside one review cycle.

**Typical c:** 0.5 to 3 hours. Class C is where the verification budget is actually spent and where overdraft accumulates.

**PMO examples:** critical-path re-baselining, change-request impact assessment, resource reallocation across programmes, vendor scope dispute positions, forecast revision beyond tolerance, dependency renegotiation between workstreams, risk response strategy selection, benefits-realisation re-forecast, supplier performance assessment.

**The tell.** Two qualified people could look at the same artifact and reasonably disagree, and resolving that disagreement requires knowledge neither of them wrote down.

**Where it goes wrong.** Class C is where the budget bites, so there is quiet pressure to call things B. Test that pressure with one question: *would you be comfortable if a sample of twenty of these was the only check on two hundred?* If the answer is no, it is C and the budget is what it is.

---

### Class D: not checkable in advance

**Definition.** Correctness cannot be established before the outcome. Any one of the following is sufficient:

1. **Irreversible.** No undo, or undo costs more than the original decision.
2. **Outcome-only observability.** Correctness becomes visible on a horizon longer than the review cycle.
3. **Check costs more than the decision.** An honest check costs more qualified time than making the decision from scratch.
4. **Unclassifiable.** Nobody can determine which of A, B, C or D it is. Unclassified defaults to D.

**Typical c:** undefined. Not "high". Undefined. A Class D decision has no finite verification cost, so it has no budget, so no quantity of it is affordable.

**PMO examples:** cancelling a workstream, terminating a contract, declaring a programme red to the board, escalating to a regulator, redundancy selection, go-live authorisation on a safety-relevant system, accepting a risk above appetite, committing to a public delivery date, changing a benefits case after approval.

**The rule.**

> Class D decisions are never delegated to agents. Agents prepare Class D decisions. Humans make them.

**The structural move that recovers the throughput.**

> Class D work is delivered as Class C artifacts.

Split the decision from its preparation. The preparation, meaning options with impacts, precedent, reversal cost, stakeholder position and a named recommendation, is an artifact whose quality a human can check in bounded time. That artifact is Class C, costs Class C to check, and consumes Class C budget. The decision itself stays with a named human and consumes no agent budget at all.

This is not a loophole. The agent has no authority over the outcome and the human's approval is a real decision, not a review of one. The distinction is enforceable: a Class D preparation pack carries a `recommendation` field and no `decision` field, and the human's action creates the decision artifact with themselves as `owner`.

---

## 3. The decision tree

Apply in order. Stop at the first terminal.

```
Q0. Is the decision irreversible, or is correctness only observable
    after the outcome, on a horizon longer than one review cycle?
      YES -> CLASS D  (prepare only)
      NO  -> Q1

Q1. Does a deterministic check exist that decides correctness
    without a human judgement call?
      YES -> Q1a
      NO  -> Q2

    Q1a. Is the human time to act on that check under 5 minutes,
         including the amortised cost of exceptions?
           YES -> CLASS A
           NO  -> CLASS B

Q2. Is this one of a homogeneous population of at least 30 per period,
    governed by one rubric, where a sample bounds the batch error rate
    and no member is much more consequential than the others?
      YES -> Q2a
      NO  -> Q3

    Q2a. Is it reversible within one review cycle at bounded cost?
           YES -> CLASS B
           NO  -> CLASS C

Q3. Can a qualified human decide correctness in bounded time from
    the artifact plus retrievable context?
      YES -> Q3a
      NO  -> CLASS D

    Q3a. Does an honest check cost more qualified human time than
         making the decision from scratch?
           NO  -> CLASS C
           YES -> CLASS D
```

Run it: `vb classify`.

### Tie-breakers

Applied after the tree, in this order. Each can only move a decision to a **more expensive** class, never a cheaper one.

**T1. Reversibility override.** If the decision were wrong and undetected for one full review cycle, could it be undone at bounded cost? If no, the class is at least C, and D if the undo cost exceeds the decision cost. This overrides an A or B result from the tree.

**T2. Disagreement.** If two qualified classifiers disagree, take the more expensive class and log the disagreement with both rationales. Disagreement rate is a property of your rubric, not of your people. Track it. Above about 20 percent on a decision type, the rubric is the problem and no amount of retraining classifiers will fix it.

**T3. Default to D.** Anything unclassified is Class D until classified. Not C. The default has to be the expensive one, or the default becomes the loophole through which unclassified decision types enter agent scope.

---

## 4. Worked classifications

### 4.1 Weekly RAG status proposal, 40 projects

- Q0: reversible, next week's status corrects it. Consequences visible inside one cycle. Not D.
- Q1: no deterministic check. A rubric exists but applying it needs judgement about narrative content. To Q2.
- Q2: 40 per week, one rubric, homogeneous. But: **three of the forty go to the board pack.** Consequence spread fails.
- Result: split. 37 non-board projects are **Class B**. Three board-facing projects are **Class C**.

The stratification is the answer, not a compromise. This is the most common real result and the classifier supports it: classify the strata, not the decision type.

### 4.2 Critical path recalculation after a task update

- Q0: reversible, recompute. Not D.
- Q1: yes. Forward and backward pass is deterministic.
- Q1a: yes, the human sees only cases where the recalculation changes the critical path materially, roughly 3 percent.
- Result: **Class A**, `c ≈ 0.02 h`.

### 4.3 Schedule re-baselining after a supplier delay

- Q0: reversible in principle, but re-baselining resets variance history. Undo is possible at meaningful cost. Not automatically D.
- Q1: no. Which activities absorb the delay is a judgement.
- Q2: roughly 8 per week. Below the volume threshold, and heterogeneous. Not B.
- Q3: yes, a portfolio scheduler can check it against the baseline, the delay evidence and the resourcing position.
- Q3a: no, checking costs about 1.25 h, making it from scratch costs about 4 h.
- Result: **Class C**, `c ≈ 1.25 h`. This is the decision type that produces the overdraft in [PMO-40](../examples/pmo40).

### 4.4 Recommending workstream cancellation

- Q0: cancellation is irreversible. **Class D.**
- Delivered as: a Class C preparation pack. Options, impact on dependent workstreams, sunk and forward cost, contractual exposure, precedent from two comparable cancellations, a named recommendation. The change authority chair decides.
- Budget effect: consumes Class C budget at `c ≈ 1.5 h`. Consumes no Class D budget, because there is none.

### 4.5 Agent verifier verdict on a Class B batch

- Q0: reversible. Not D.
- Q1: yes, if and only if the verifier emits a machine-checkable proof object. The verdict is checked by re-running the assertion, not by re-reading the reasoning.
- Q1a: yes, under a minute.
- Result: **Class A.** This is the [recursion rule](../README.md#24-agentic-verification-reducing-c-with-agents) as a classification, and it is why a verifier whose output is prose does not qualify. Prose verdicts land at Q1 "no" and fall through to C, which means the verifier has moved the cost rather than removed it.

---

## 5. Class, authority and blast radius

Class is one axis. It is not enough on its own.

> **Class sets the cost of checking. Blast radius sets the authority. A decision type needs both before an agent touches it.**

Class alone would let an agent take a cheap-to-check decision that happens to be irreversible, because cheapness of checking says nothing about consequence. A schedule arithmetic correction is Class A whether it moves an internal date or triggers a contractual milestone payment.

### 5.1 The authority ladder

Authority is set by blast radius. Five levels.

| Level | Authority | Test that puts you here | PMO examples |
|---|---|---|---|
| **1** | Agent acts, logs only | Reversible within a day, no external party affected | Reassign a task, update a date, flag a duplicate |
| **2** | Agent acts, human notified | Reversible within a week, internal only | Reallocate slack, reorder a backlog, redraft a summary |
| **3** | Agent proposes, one human approves | Reversible with effort, or affects one team's plan | Move a milestone, change a resource split |
| **4** | Agent proposes, committee approves | Hard to reverse, or touches cost, contract or compliance | Budget reallocation, vendor change, scope reduction |
| **5** | Human decides, agent supports only | Irreversible, or legally accountable | Contract signature, termination, regulatory submission |

**Notice what is absent from the test column: model confidence.** It appears nowhere, at any level. Confident and wrong on an irreversible decision is still a disaster, and a confidence threshold is not a substitute for an authority boundary. Confidence belongs in the evidence plane, where it tells a reviewer where to look. It does not belong in the authority decision.

### 5.2 How the two axes interact

Both constrain, and the more restrictive one wins.

| Class | Authority ceiling | Why |
|---|---|---|
| A | none from class. Blast radius decides. | Cheap to check does not mean safe to decide alone. A Class A decision with level 4 blast radius stays at level 4. |
| B | level 3 | Sampling means most individual decisions are unread. That is acceptable for internal, reversible work and not for anything above it. |
| C | level 3 | A decision a human must reconstruct cannot be one an agent takes unilaterally. |
| D | level 5, forced | No finite `c`, so no budget, so no delegation at any level. |

The practical result is a grid. Most useful agent work sits at Class A or B with authority level 1 or 2, which is the same conclusion [the deployment inversion](../README.md#4-the-deployment-inversion) reaches from the cost side. The two axes agree, which is a reasonable sign that both are pointing at something real.

### 5.3 What each class means for the budget

| Class | Agent may decide | Human involvement | Budget line |
|---|---|---|---|
| A | Yes, within contract scope and authority level | Exceptions only | `VB_A`, large |
| B | Yes, within contract scope and authority level | Sample review per batch | `VB_B`, moderate |
| C | No. Propose only. | Every decision reviewed | `VB_C`, small. Where overdraft lives. |
| D | No. Prepare only. | Human makes the decision | None. Preparation consumes `VB_C`. |

Every agent role contract states its scope in these terms, and every scope entry carries a `decision_class`, a `verified_by`, a `checker_role` and an `authority_level`. A contract containing a Class D decision type in scope is invalid, not risky. See [agent-role-contract.md](agent-role-contract.md).

Gate 1 criterion 1.7 checks that every in-scope entry has an authority level consistent with its blast radius. A classified decision type with no authority level is half specified.

---

## 6. Reclassification

Reclassification is the highest-value activity in the whole framework, because `c` is the only lever with orders of magnitude in it.

> Reclassification means **making a decision cheaper to check**. Relabelling a Class C decision as Class B changes nothing except how visible the overdraft is.

### 6.1 The moves

| From | To | The work | Typical effect on c |
|---|---|---|---|
| C | B | Homogenise: fix the rubric, standardise inputs, remove case-by-case discretion until a sample genuinely bounds the batch | 1.25 h to 0.15 h |
| C | C | Enforce the evidence plane. Most of `c` is the reviewer re-gathering inputs the agent already had | 30 to 60 percent cut |
| B | A | Build the deterministic check. If you can write the test, write it | 0.15 h to 0.02 h |
| any | cheaper | Instrument the context. A decision is Class C mostly because the context is in someone's head | varies, large |
| D | C | Split decision from preparation | makes the work budgetable at all |

### 6.2 The procedure

1. **Measure current ĉ** for the decision type. See [metrics.md](metrics.md#1-measuring-ĉ). Without a before, there is no after.
2. **Name the cost driver.** Ask three reviewers what takes the time. It is almost always input gathering, and almost never the judgement itself.
3. **Make the change.** Evidence plane fields, a rubric change, a deterministic check, an instrumented data source.
4. **Re-measure ĉ** on at least 30 decisions after the change.
5. **Re-run Gate 1** with two classifiers. A reclassification that does not survive Gate 1 has not happened.
6. **Update the budget** and the agent role contracts that reference the decision type.
7. **Record it** in the reclassification log with before ĉ, after ĉ, the change made, and the Gate 1 kappa.

Steps 1 and 4 are the ones that get skipped, and skipping them turns reclassification into relabelling.

### 6.3 Reclassification is not permanent

Class can move back. A Class A check that starts producing 15 percent exceptions is Class B now, whatever the register says. A Class B population that acquires a few high-consequence members is Class C now. Re-run Gate 1 quarterly on anything an agent has authority over, and treat a class register as a live document rather than a policy.

---

## 7. Anti-patterns

**Classifying by risk.** Produces a register where everything important is Class C and everything unimportant is Class A, which is a risk register with different words on it. Class is about cost of checking. A high-risk decision that is cheap to check is Class A and should be automated aggressively, with the risk handled by the check, not by the class.

**Classifying by model capability.** "The model is good at this, so it is Class A." The model's skill has no effect on your cost of checking. This is the deployment inversion stated as a classification error.

**Class B by wishful volume.** Counting a heterogeneous mix as one population to reach 30 per period. Three different decision types at 12 each is three populations of 12, and none of them is Class B.

**The unclassified back door.** Decision types that appear in an agent's behaviour but not in its scope. This is what T3 exists to stop, and it is what Gate 4 catches on replay.

**Permanent classification.** Classifying once at deployment and never again. Class drifts because evidence, rubrics and populations drift.

**Relabelling as reclassification.** Covered above, and worth repeating: it is the failure mode most likely to be presented as a success.
