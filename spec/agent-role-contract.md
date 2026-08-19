# The agent role contract

Normative specification. Short form in [README section 5](../README.md#5-the-agent-role-contract). Machine-readable form in [`schema/agent-contract.schema.json`](../schema/agent-contract.schema.json).

---

## 1. Why four fields

Every agent operating in the PMO has a contract with exactly four fields: **Scope**, **Evidence**, **Escalation**, **Revocation**.

The number is a design constraint, not a starting point. Contracts get read in two situations: once at approval, when everyone is calm and has time, and once during an incident, when somebody has to decide in five minutes whether to pull an agent that is producing output nobody trusts. The second reading is the one that matters, and it is the one a fifteen-field contract fails.

Four is the number a reviewer can hold in their head. Every additional field is a field that does not get read in the second situation, which means it protects nobody while creating the impression of protection.

The four are not arbitrary. They are the four questions whose absence makes an agent ungovernable:

| Field | Question | What breaks without it |
|---|---|---|
| Scope | What may it decide? | Scope creep is invisible. The agent ends up deciding things nobody classified, so those decisions have no `c`, so they consume budget nobody allocated. |
| Evidence | What must it emit? | Decisions arrive unverifiable. `c` rises silently, VB falls, and the overdraft appears with no traceable cause. |
| Escalation | When does it stop? | Escalation becomes discretionary. Discretionary escalation stops under load, which is exactly when it is needed. |
| Revocation | How is it turned off? | You cannot turn it off. Every other field is decoration if this one is missing. |

If you find yourself needing a fifth field, check whether it belongs inside one of the four. Rate limits belong in Scope. Retention belongs in Evidence. On-call rotas belong in Escalation. Kill-switch ownership belongs in Revocation. In two years of drafting these, no genuine fifth has appeared.

---

## 2. Field specifications

### 2.1 Scope

**Purpose.** Bound what the agent may decide, in the vocabulary of decision classes, so that its consumption of verification budget is calculable before it runs.

**Required content**

1. `in_scope`: a list of decision types, each with an explicit `decision_class`. Named individually. No wildcards, no categories, no "and similar".
2. `excluded`: decision types explicitly out of scope, each with a `reason`. Include the obvious ones. "Obvious" does not survive a model upgrade or a new team member.
3. `unlisted_types`: what happens on encountering a decision type not in either list. The only permitted value is `escalate`.

**Rules**

- **R1.** An unnamed decision type is out of scope. Encountering one is an escalation condition, not a judgement call.
- **R2.** No Class D decision type may appear in `in_scope`. A contract that contains one is invalid, not risky. Class D decisions are prepared, and the preparation is a separate Class C decision type with its own entry.
- **R3.** Class C decision types in scope must carry `authority: propose`. Agents do not decide Class C.
- **R4.** Class B decision types must carry a `sampling_rate` and the sampling rate must be consistent with the sample size arithmetic in [decision-classes.md](decision-classes.md#class-b-sample-checkable).
- **R5.** Scope may include a `rate_limit` per decision type. If the contract's rate limits sum to more than the class verification budget, the contract is over budget at design time and should not be approved. This is the check most worth automating, and `vb budget` does it.

**Anti-pattern.** Scope written as capability ("schedule analysis") rather than as decisions ("critical path recalculation, dependency cycle flagging"). Capability scope is unbounded and unbudgetable. If you cannot count it per week, it is not a scope entry.

---

### 2.2 Evidence

**Purpose.** Guarantee that every decision arrives at a known verification cost.

**Required content**

1. `required_fields`: the six evidence plane fields, plus any class-specific additions.
2. `artifact_schema`: the schema the artifact validates against.
3. `on_evidence_failure`: what happens when required evidence cannot be produced. The only permitted value is `escalate`.
4. `retention_days`: how long artifacts are kept. Must be at least as long as the reversal window of the longest-lived decision in scope.

**Rules**

- **E1. The binding rule.** If the agent cannot produce the required evidence for a decision, **it must not make the decision**. It escalates. Producing a decision without evidence is never an acceptable degraded mode, and there is no configuration under which it becomes one.
- **E2.** Evidence requirements are per decision class, not per agent. An agent in scope for both A and C emits the six fields for both, and any Class C additions for the C decisions.
- **E3. Verifier agents carry additional obligations.** Any agent claiming containment `k` must emit, per decision: its verdict, a machine-checkable proof object supporting that verdict, and a reference to its current calibration record. The calibration record itself carries the measured false-negative rate, the size and date of the labelled set, and the 95 percent confidence interval on `k`. Missing calibration means `k = 0` in the budget. See [eval-gates.md](eval-gates.md#gate-3-verifier-calibration).
- **E4.** The proof object referenced in E3 must be Class A, meaning re-checkable by machine. A verifier that emits prose reasoning is not supplying containment, it is supplying an opinion, and opinions do not enter the budget.

**Anti-pattern.** `required_fields` listed but not enforced in the pipeline. Evidence that is required by document and optional by code is optional. Gate 2 exists because this degrades quietly.

---

### 2.3 Escalation

**Purpose.** Define, in advance and testably, the conditions under which the agent stops and a human takes over.

**Required content**

1. `conditions`: a list, each with an `id`, a `test` that is machine-evaluable, and a `to_role`.
2. `target_resolution`: how a role becomes a person. The only permitted value is `named_person_at_decision_time`.
3. `max_response_hours`: how long an escalation may sit before it escalates further.

**Rules**

- **S1.** Conditions are testable. "When uncertain" is not a condition. "When `confidence < 0.80`" is a condition. If a condition cannot be evaluated by code, it will not be evaluated.
- **S2. Three mandatory conditions**, present in every contract regardless of what else it names:
  - an unclassifiable decision type,
  - required evidence that cannot be produced,
  - any decision that classifies as D.
- **S3.** The target is a role, and the role resolves to a named individual at decision time. An escalation to "the PMO" is an escalation to nobody. If the role cannot resolve, that is itself an escalation to the contract owner.
- **S4.** Escalations consume verification budget at the class cost of the escalated decision. A contract whose escalation conditions fire often enough to exceed `VB` for that class is over budget, and this is why **escalation precision** is one of the six metrics. An agent escalating everything is safe and useless, and it drains the same budget as an agent deciding everything.
- **S5.** `max_response_hours` must be shorter than the reversal window of the decisions being escalated. An escalation that resolves after the decision becomes expensive to reverse has not helped.

**Anti-pattern.** Escalation conditions tuned to reduce noise until only catastrophes trigger them. The correct response to escalation noise is a rubric fix or a reclassification, not a threshold change.

---

### 2.4 Revocation

**Purpose.** Guarantee the agent can be stopped.

**Required content**

1. `who`: named roles who may revoke. At least two, so revocation does not depend on one person's availability.
2. `method`: the concrete action. One action.
3. `max_time_to_effect_minutes`: from decision to revoke, to the agent no longer acting.
4. `in_flight_work`: what happens to work already started. One of `halt_and_mark_unverified`, `complete_then_halt`, `rollback`.
5. `rollback`: what happens to decisions already made, and over what window.
6. `notify`: who is told.

**Rules**

- **V1.** Revocation is executable by **one named person, without a meeting**. A revocation clause requiring a change advisory board is not a revocation clause, it is a hope.
- **V2.** `max_time_to_effect_minutes` is tested, not asserted. Revoke the agent in a non-production environment, time it, record the result. An untested revocation path is an untested revocation path.
- **V3.** `in_flight_work: complete_then_halt` is only permitted where every in-scope decision type is Class A. For anything else, in-flight work by a revoked agent is unverified work.
- **V4.** `rollback` must state a window and what happens inside it. "All decisions in the last 24 hours flagged for human re-review" is a rollback clause. "As appropriate" is not. Note the budget consequence: a rollback dumps a batch of decisions into the review queue at once, and that batch consumes verification budget that was allocated to the current period. Size the window against `VB`, or the rollback creates the overdraft it was meant to contain.
- **V5.** Revocation is not deletion. Revoked agents keep their decision artifacts for the retention period. You will want them.

**Anti-pattern.** Revocation described as "disable the integration". If nobody has done it, nobody knows how long it takes or what happens to the work in flight.

---

## 3. Worked contracts

Three contracts. Shown as YAML because it reads better on a page. The validator takes JSON, because the package has no dependencies and the standard library has no YAML parser. The same three contracts in JSON are in [`schema/fixtures/valid`](../schema/fixtures/valid) and that is what the validator reads:

```bash
vb gates --contract schema/fixtures/valid/contract-schedule-integrity.json
```

### 3.1 Schedule Integrity Agent, Class A and B

The straightforward case. Machine-checkable work, full authority within scope.

```yaml
agent_id: schedule-integrity-01
name: Schedule Integrity Agent
version: "1.4.0"
owner_role: pmo_lead

scope:
  in_scope:
    - decision_type: critical_path_recalculation
      decision_class: A
      authority: decide
      rate_limit_per_period: 200
    - decision_type: dependency_cycle_flagging
      decision_class: A
      authority: decide
      rate_limit_per_period: 120
    - decision_type: float_erosion_alert
      decision_class: A
      authority: decide
      rate_limit_per_period: 160
    - decision_type: milestone_slip_categorisation
      decision_class: B
      authority: decide
      sampling_rate: 0.15
      rate_limit_per_period: 160
  excluded:
    - decision_type: schedule_rebaselining
      reason: "Class C. Proposed by change-impact-01. This agent does not decide it."
    - decision_type: milestone_removal
      reason: "Class D. Requires change authority."
    - decision_type: baseline_approval
      reason: "Class D. Requires programme board."
  unlisted_types: escalate

evidence:
  required_fields: [decision, basis, alternatives, confidence_and_failure_mode, reversal, owner]
  artifact_schema: schema/decision-artifact.schema.json
  on_evidence_failure: escalate
  retention_days: 730

escalation:
  conditions:
    - id: low_confidence
      test: "confidence < 0.80"
      to_role: portfolio_scheduler
    - id: unclassified_type
      test: "decision_type not in scope.in_scope"
      to_role: pmo_lead
    - id: evidence_unavailable
      test: "any required evidence field cannot be produced"
      to_role: portfolio_scheduler
    - id: class_d_detected
      test: "classification result == D"
      to_role: change_authority_chair
    - id: cross_programme_impact
      test: "affected_programmes > 1"
      to_role: pmo_lead
    - id: critical_path_change
      test: "critical_path_changed and slip_days > 5"
      to_role: portfolio_scheduler
  target_resolution: named_person_at_decision_time
  max_response_hours: 8

revocation:
  who: [pmo_lead, head_of_delivery]
  method: "Set status to REVOKED in the agent registry. Single action, no approval chain."
  max_time_to_effect_minutes: 15
  in_flight_work: halt_and_mark_unverified
  rollback: "Decisions from the last 24h flagged for human re-review. Class A decisions auto-revalidated by their deterministic check, which clears most of them without consuming budget."
  notify: [portfolio_scheduler, change_authority_chair]
  last_tested: "2026-07-14"
  last_tested_seconds: 190
```

Note `last_tested`. Rule V2.

### 3.2 Change Impact Agent, Class C proposal and Class D preparation

The interesting case. This agent touches the most consequential work in the PMO and decides nothing.

```yaml
agent_id: change-impact-01
name: Change Impact Agent
version: "0.9.2"
owner_role: change_authority_chair

scope:
  in_scope:
    - decision_type: change_request_impact_assessment
      decision_class: C
      authority: propose          # R3. Class C is proposed, never decided.
      rate_limit_per_period: 30
    - decision_type: schedule_rebaselining_proposal
      decision_class: C
      authority: propose
      rate_limit_per_period: 12
    - decision_type: workstream_cancellation_preparation
      decision_class: C           # The preparation is C. The decision is D.
      authority: prepare
      rate_limit_per_period: 4
      prepares_class_d: workstream_cancellation
  excluded:
    - decision_type: workstream_cancellation
      reason: "Class D. Prepared here, decided by change authority. R2."
    - decision_type: contract_termination
      reason: "Class D. Legal and commercial. Not prepared here either."
    - decision_type: change_request_approval
      reason: "Class D. Change authority only."
  unlisted_types: escalate

evidence:
  required_fields: [decision, basis, alternatives, confidence_and_failure_mode, reversal, owner]
  class_c_additions: [precedent_cases, stakeholder_positions, second_order_impacts]
  class_d_preparation_additions: [recommendation, options_with_costs, reversal_cost_of_each_option]
  artifact_schema: schema/decision-artifact.schema.json
  on_evidence_failure: escalate
  retention_days: 2555

escalation:
  conditions:
    - id: low_confidence
      test: "confidence < 0.85"
      to_role: change_authority_chair
    - id: unclassified_type
      test: "decision_type not in scope.in_scope"
      to_role: change_authority_chair
    - id: evidence_unavailable
      test: "any required evidence field cannot be produced"
      to_role: change_authority_chair
    - id: class_d_detected
      test: "classification result == D and decision_type not in scope.in_scope"
      to_role: change_authority_chair
    - id: contractual_exposure
      test: "commercial_impact_gbp > 250000 or contract_clause_triggered"
      to_role: commercial_lead
    - id: no_precedent
      test: "precedent_cases.length == 0"
      to_role: change_authority_chair
    - id: budget_pressure
      test: "class_c_overdraft_ratio > 1.0"
      to_role: pmo_lead
  target_resolution: named_person_at_decision_time
  max_response_hours: 24

revocation:
  who: [change_authority_chair, pmo_lead]
  method: "Set status to REVOKED in the agent registry."
  max_time_to_effect_minutes: 30
  in_flight_work: halt_and_mark_unverified   # V3. Not complete_then_halt: nothing here is Class A.
  rollback: "All proposals from the last 7 days withdrawn from the change queue and re-submitted for human preparation. Any change request already approved on the basis of a withdrawn proposal is flagged to the change authority chair individually."
  notify: [change_authority_chair, pmo_lead, commercial_lead, head_of_delivery]
  last_tested: "2026-08-02"
  last_tested_seconds: 410
```

Three things to notice.

`budget_pressure` is an escalation condition on the overdraft ratio itself. When Class C is over budget, the agent stops adding to the queue. This is the S4 throttle in contract form, and it is the cheapest version of it: one condition, no infrastructure.

`workstream_cancellation_preparation` is Class C with `authority: prepare` and a `prepares_class_d` pointer. The agent produces a pack. The chair produces the decision. The pack consumes Class C budget; the cancellation consumes none, because there is none.

The rollback window is 7 days rather than 24 hours, because Class C proposals sit in a change queue rather than acting immediately. Rule V4 applies: 7 days at 30 per period is up to 30 decisions dumped back into a queue with a budget of 21 per week. That is a deliberate, sized decision and it is written down.

### 3.3 Schedule Verifier, a Warden

The agentic verification case. This agent supplies budget rather than consuming it, and its contract is where the containment claim is made and bounded.

```yaml
agent_id: schedule-verifier-01
name: Schedule Verifier
version: "2.1.0"
owner_role: pmo_lead
agent_kind: verifier            # Triggers the E3 and E4 obligations.

verifies:
  agent_ids: [schedule-integrity-01]
  decision_types: [critical_path_recalculation, dependency_cycle_flagging, float_erosion_alert, milestone_slip_categorisation]

scope:
  in_scope:
    - decision_type: verification_verdict
      decision_class: A          # E4. The verdict is machine-checkable or it is not containment.
      authority: decide
      rate_limit_per_period: 640
  excluded:
    - decision_type: verification_verdict_class_c
      reason: "This verifier has no calibration on Class C. Uncalibrated means k = 0, so there is no point running it."
  unlisted_types: escalate

evidence:
  required_fields: [decision, basis, alternatives, confidence_and_failure_mode, reversal, owner]
  verifier_additions:
    - verdict                    # pass | reject | cannot_decide
    - proof_object               # E4. Machine re-checkable. Assertions, not prose.
    - calibration_record_ref
  artifact_schema: schema/decision-artifact.schema.json
  on_evidence_failure: escalate
  retention_days: 730

calibration:
  labelled_set_size: 240
  known_bad_count: 38
  measured_at: "2026-07-30"
  false_negative_rate: 0.021
  false_positive_rate: 0.094
  containment_point_estimate: 0.71
  containment_ci95: [0.652, 0.762]
  containment_used_in_budget: 0.652     # The lower bound. The conservatism rule.
  c_a_hours: 0.008
  gate_3_status: pass
  next_recalibration_due: "2026-10-30"

escalation:
  conditions:
    # The three mandatory conditions. S2 applies to verifiers too.
    - id: unclassified_type
      test: "decision_type not in verifies.decision_types"
      to_role: pmo_lead
    - id: evidence_unavailable
      test: "proof_object cannot be constructed"
      to_role: portfolio_scheduler
    - id: class_d_detected
      test: "classification result == D"
      to_role: change_authority_chair
    # Verifier-specific.
    - id: cannot_decide
      test: "verdict == cannot_decide"
      to_role: portfolio_scheduler
    - id: calibration_stale
      test: "now > calibration.next_recalibration_due"
      to_role: pmo_lead
    - id: fnr_drift
      test: "rolling_30d_false_negative_rate > 0.05"
      to_role: pmo_lead
  target_resolution: named_person_at_decision_time
  max_response_hours: 4

revocation:
  who: [pmo_lead, head_of_delivery]
  method: "Set status to REVOKED. Containment k drops to 0 for all classes this verifier covered."
  max_time_to_effect_minutes: 5
  in_flight_work: halt_and_mark_unverified
  rollback: "Decisions closed by this verifier in the last 72h re-enter the human review queue. See below: this is a budget event."
  notify: [pmo_lead, portfolio_scheduler, head_of_delivery]
  last_tested: "2026-08-05"
  last_tested_seconds: 95
```

**Revoking a verifier is a budget event, and it is the one people do not see coming.** This verifier supplies `k = 0.652` on Class A and B. Revoke it and `c_eff` returns to `c`, so `VB` for those classes drops by roughly two thirds instantly, and 72 hours of contained decisions re-enter a queue that is now much smaller. A contract for a verifier should state that consequence in the rollback clause, and the operating plan should know what it does when a verifier goes down. This is the closest thing the framework has to a single point of failure, and it is worth saying out loud rather than discovering.

Note `calibration.containment_used_in_budget`. It is the lower bound of the confidence interval, 0.652, not the point estimate of 0.71. The difference is about 8 percent of `VB` and it is the margin that stops a good quarter of measurement from becoming a permanent assumption.

Note `fnr_drift`. A verifier that was calibrated in July is not necessarily calibrated in October, and the escalation condition catches the drift before the quarterly recalibration does.

---

## 4. Contract lifecycle

| Event | What happens |
|---|---|
| Draft | Author writes the four fields. Scope entries classified with `vb classify` and Gate 1. |
| Budget check | `vb budget` sums the rate limits against `VB` per class. Over budget at design time means it does not get approved. |
| Approval | Named owner role approves. The owner is a person, not a committee. |
| Gate 1 and Gate 4 | Classification agreement and replay. Both before first run. |
| Live | Gate 2 continuous. Gate 3 quarterly if the agent is a verifier. |
| Material change | Any change to scope, model, prompt or calibration re-runs Gate 1 and Gate 4. Version bump required. |
| Revocation | Per the revocation clause. Artifacts retained. |

**Material change** means: any addition to `in_scope`, any change of `decision_class` on an existing entry, any model version change, any change to the system prompt that could affect which decisions get made, any recalibration. Bump the version. An agent running under a contract version that does not match its deployed configuration is running without a contract.

---

## 5. Validation

```bash
vb gates --contract path/to/contract.json
```

Checks:

- All four fields present.
- Every `in_scope` entry has a `decision_class` (R1).
- No Class D in `in_scope` (R2).
- Class C entries carry `authority: propose` or `prepare` (R3).
- Class B entries carry a `sampling_rate` (R4).
- `unlisted_types == escalate`.
- `on_evidence_failure == escalate` (E1).
- The three mandatory escalation conditions present (S2).
- `target_resolution == named_person_at_decision_time` (S3).
- At least two revokers (V1), `max_time_to_effect_minutes` present, `in_flight_work` valid for the class mix (V3), `rollback` non-empty (V4).
- If `agent_kind: verifier`: calibration block present, FNR measured, containment reported as an interval, and `containment_used_in_budget` equal to the lower bound (E3, E4).

Schema: [`schema/agent-contract.schema.json`](../schema/agent-contract.schema.json). Fixtures, valid and invalid, in [`schema/fixtures`](../schema/fixtures).
