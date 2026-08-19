"""Build the schema fixtures.

Valid fixtures are written out in full. Invalid fixtures are produced by taking a
valid one and breaking exactly one rule, so that each invalid fixture tests one
thing and the manifest can name which rule it violates.

    python schema/fixtures/build_fixtures.py

Outputs land in schema/fixtures/valid, schema/fixtures/invalid, and
schema/fixtures/manifest.json. Committed to the repository; re-run after any
schema change.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
VALID = HERE / "valid"
INVALID = HERE / "invalid"

Json = dict[str, Any]


# --------------------------------------------------------------------------
# Valid decision artifacts
# --------------------------------------------------------------------------

ARTIFACT_A: Json = {
    "artifact_id": "da-2026-0819-0001",
    "artifact_kind": "decision",
    "decision_type": "critical_path_recalculation",
    "decision_class": "A",
    "agent_id": "schedule-integrity-01",
    "agent_version": "1.4.0",
    "timestamp": "2026-08-19T08:02:11Z",
    "decision": "Recalculate critical path for PRG7 after task T-4419 update; path unchanged, total float 14d.",
    "basis": [
        {
            "source_id": "P6:PRG7:network:v88",
            "retrieved_at": "2026-08-19T08:02:04Z",
            "detail": "412 activities, 3 open constraint violations, none on the critical path",
        },
        {
            "source_id": "P6:PRG7:T-4419",
            "retrieved_at": "2026-08-19T08:02:05Z",
            "detail": "Remaining duration changed 12d to 15d, actual start 2026-08-17",
        },
        {
            "source_id": "P6:PRG7:baseline:v12",
            "retrieved_at": "2026-08-19T08:02:06Z",
            "detail": "Baseline finish 2026-09-30, baseline total float 14d",
            "influenced_outcome": False,
        },
    ],
    "alternatives": [
        {
            "option": "Flag the change as a critical path shift",
            "rejected_because": "Forward and backward pass both return the same critical path; float on T-4419 remains 9d, above the 0d threshold.",
            "rejection_kind": "factual",
        }
    ],
    "confidence_and_failure_mode": {
        "confidence": 0.99,
        "failure_mode": "If the P6 network export is stale, the recalculation runs on a superseded logic set and the unchanged verdict is wrong. Detectable by comparing network version v88 against the P6 change log on the next sync at 09:00.",
        "calibration_basis": "Deterministic. Verified against P6 native scheduler on 1,000 networks, 2026-Q2, zero disagreements.",
        "detectable_at": "2026-08-19T09:00:00Z",
    },
    "reversal": {
        "how": "Re-run the forward and backward pass against the corrected network export and re-issue the float report to the programme scheduler.",
        "cost_hours": 0.05,
        "cheap_until": "2026-08-26T00:00:00Z",
        "cheap_until_reason": "Weekly float report distribution to programme leads.",
    },
    "owner": {
        "person_id": "u-2291",
        "name": "R. Okonjo",
        "role": "portfolio_scheduler",
        "resolved_at": "2026-08-19T08:02:11Z",
    },
    "review": {
        "reviewer_id": "u-2291",
        "opened_at": "2026-08-19T08:40:00Z",
        "submitted_at": "2026-08-19T08:41:12Z",
        "review_seconds": 72,
        "idle_trimmed_seconds": 72,
        "outcome": "approved",
    },
}

ARTIFACT_B: Json = {
    "artifact_id": "da-2026-0819-0447",
    "artifact_kind": "decision",
    "decision_type": "milestone_slip_categorisation",
    "decision_class": "B",
    "agent_id": "schedule-integrity-01",
    "agent_version": "1.4.0",
    "timestamp": "2026-08-19T09:14:22Z",
    "decision": "Categorise slip on milestone MS-PRG7-014 as supplier-caused, 11 working days, absorbed by float.",
    "basis": [
        {
            "source_id": "P6:PRG7:baseline:v12",
            "retrieved_at": "2026-08-19T09:13:58Z",
            "detail": "Baseline finish 2026-09-30, float 14d",
        },
        {
            "source_id": "JIRA:PRG7-2291",
            "retrieved_at": "2026-08-19T09:14:01Z",
            "detail": "Supplier confirmed delay in writing 2026-08-15",
        },
        {
            "source_id": "SUP:ACME:SLA:2025-11",
            "retrieved_at": "2026-08-19T09:14:03Z",
            "detail": "SLA clause 7.2, notification requirement met",
        },
    ],
    "alternatives": [
        {
            "option": "Categorise as scope-change-caused",
            "rejected_because": "No approved change request in the window. CR-PRG7-0088 closed 2026-07-02.",
            "rejection_kind": "factual",
        },
        {
            "option": "Escalate as a float-consuming risk",
            "rejected_because": "Remaining float 3d after absorption, above the 2d escalation threshold.",
            "rejection_kind": "factual",
        },
    ],
    "confidence_and_failure_mode": {
        "confidence": 0.86,
        "failure_mode": "If the supplier delay is a symptom of an undisclosed resource loss on their side, the 11-day figure understates the slip and float absorption is wrong. Detectable at the next supplier checkpoint on 2026-08-26.",
        "calibration_basis": "Reliability measured on 240 labelled categorisations, 2026-Q2. Brier score 0.09.",
        "detectable_at": "2026-08-26T09:00:00Z",
    },
    "reversal": {
        "how": "Re-run categorisation with the corrected cause code and re-issue the slip notice to the programme board.",
        "cost_hours": 0.5,
        "cheap_until": "2026-09-02T00:00:00Z",
        "cheap_until_reason": "Programme board pack lock for the September cycle.",
    },
    "owner": {
        "person_id": "u-2291",
        "name": "R. Okonjo",
        "role": "portfolio_scheduler",
        "resolved_at": "2026-08-19T09:14:22Z",
    },
    "batch_id": "batch-2026-W34-slipcat",
    "sampled": True,
    "rubric_version": "slip-cause-v3.1",
}

ARTIFACT_C: Json = {
    "artifact_id": "da-2026-0819-0912",
    "artifact_kind": "decision",
    "decision_type": "change_request_impact_assessment",
    "decision_class": "C",
    "agent_id": "change-impact-01",
    "agent_version": "0.9.2",
    "timestamp": "2026-08-19T11:31:07Z",
    "decision": "Assess CR-PRG7-0104 as a 19-day schedule impact with 340k cost exposure, recommend absorption into the Q4 contingency rather than re-baselining.",
    "basis": [
        {
            "source_id": "CR:PRG7-0104",
            "retrieved_at": "2026-08-19T11:28:40Z",
            "detail": "Scope addition: two integration environments, requested by the security workstream",
        },
        {
            "source_id": "P6:PRG7:baseline:v12",
            "retrieved_at": "2026-08-19T11:28:52Z",
            "detail": "Critical path runs through integration test window, float 14d",
        },
        {
            "source_id": "FIN:PRG7:contingency:2026Q4",
            "retrieved_at": "2026-08-19T11:29:03Z",
            "detail": "Unallocated contingency 610k against a 340k exposure",
        },
        {
            "source_id": "MIN:PRGBOARD:2026-06-11",
            "retrieved_at": "2026-08-19T11:29:20Z",
            "detail": "Sponsor stated no further re-baselining before the December gate",
        },
    ],
    "alternatives": [
        {
            "option": "Re-baseline the integration test window",
            "rejected_because": "Sponsor position of 2026-06-11 rules out re-baselining before the December gate, and the contingency covers the exposure.",
            "rejection_kind": "judgement",
        },
        {
            "option": "Reject the change request",
            "rejected_because": "The two environments are a stated precondition of the security workstream sign-off recorded in RISK-PRG7-0031.",
            "rejection_kind": "factual",
        },
        {
            "option": "Defer the decision to the December gate",
            "rejected_because": "Procurement lead time for the environments is 14 weeks, so deferral pushes delivery past the March milestone.",
            "rejection_kind": "factual",
        },
    ],
    "confidence_and_failure_mode": {
        "confidence": 0.78,
        "failure_mode": "If the 340k exposure excludes the licence uplift for the second environment, contingency cover is insufficient and the absorption recommendation is wrong. Detectable when the vendor quote lands, expected 2026-08-29.",
        "calibration_basis": "Reliability measured on 96 labelled impact assessments, 2026-H1. Brier score 0.14, over-confident above 0.9 so the reported figure is shrunk.",
        "detectable_at": "2026-08-29T00:00:00Z",
    },
    "reversal": {
        "how": "Withdraw the assessment from the change queue, re-run with the corrected cost basis, and re-notify the change authority chair.",
        "cost_hours": 2.0,
        "cheap_until": "2026-09-05T00:00:00Z",
        "cheap_until_reason": "Change authority decision meeting; after approval the procurement commitment starts.",
    },
    "owner": {
        "person_id": "u-1180",
        "name": "S. Lindqvist",
        "role": "change_authority_chair",
        "resolved_at": "2026-08-19T11:31:07Z",
    },
    "precedent_cases": [
        {
            "case_id": "CR:PRG4-0077",
            "outcome": "Absorbed into contingency, no re-baseline, delivered on the original date",
            "relevance": "Same sponsor, same objection to re-baselining, comparable exposure of 290k",
        },
        {
            "case_id": "CR:PRG7-0088",
            "outcome": "Rejected, security workstream escalated, reinstated six weeks later at higher cost",
            "relevance": "Shows the cost of rejecting a security precondition on this programme",
        },
    ],
    "stakeholder_positions": [
        {
            "stakeholder": "Programme sponsor",
            "position": "No re-baselining before the December gate",
            "source_id": "MIN:PRGBOARD:2026-06-11",
        },
        {
            "stakeholder": "Security workstream lead",
            "position": "Both environments required for sign-off",
            "source_id": "RISK:PRG7-0031",
        },
        {
            "stakeholder": "Finance business partner",
            "position": "Contingency available but reportable above 250k",
            "source_id": "FIN:PRG7:policy:2026",
        },
    ],
    "second_order_impacts": [
        {
            "impact": "Q4 contingency headroom falls below the 40 percent policy floor",
            "affected_id": "FIN:PRG7:contingency:2026Q4",
            "magnitude": "610k to 270k, 44 percent of original",
        },
        {
            "impact": "Integration test window compresses, reducing defect-fix float",
            "affected_id": "P6:PRG7:WBS-4.3",
            "magnitude": "14d to 9d",
        },
    ],
}

ARTIFACT_D_PREP: Json = {
    "artifact_id": "da-2026-0819-1044",
    "artifact_kind": "class_d_preparation",
    "decision_type": "workstream_cancellation_preparation",
    "decision_class": "C",
    "agent_id": "change-impact-01",
    "agent_version": "0.9.2",
    "timestamp": "2026-08-19T14:02:55Z",
    "decides_class_d": "workstream_cancellation",
    "recommendation": "Recommend cancelling the PRG7 legacy-migration workstream at the October gate, subject to the vendor exit terms in section 4 of this pack.",
    "options_with_costs": [
        {
            "option": "Cancel at the October gate",
            "cost": "Sunk 2.1m, exit fee 180k, forward saving 3.4m",
            "reversal_cost_hours": 400.0,
        },
        {
            "option": "Continue to the December gate and re-assess",
            "cost": "Additional 620k spend, exit fee unchanged, decision deferred 8 weeks",
            "reversal_cost_hours": 0.0,
        },
        {
            "option": "Descope to the regulatory minimum and continue",
            "cost": "Additional 1.1m, delivers 40 percent of the benefit case",
            "reversal_cost_hours": 160.0,
        },
    ],
    "basis": [
        {
            "source_id": "FIN:PRG7:WS-LEG:actuals:2026-07",
            "retrieved_at": "2026-08-19T13:58:12Z",
            "detail": "Spend to date 2.1m against a 2.6m approved budget, 38 percent of scope delivered",
        },
        {
            "source_id": "BEN:PRG7:case:v4",
            "retrieved_at": "2026-08-19T13:58:31Z",
            "detail": "Benefit case restated 2026-05, NPV now 0.4m against 3.9m at approval",
        },
        {
            "source_id": "SUP:NORTHRIDGE:MSA:2024-03",
            "retrieved_at": "2026-08-19T13:59:02Z",
            "detail": "Clause 11.4, exit fee 180k with 60 days notice",
        },
    ],
    "alternatives": {
        "forced": True,
        "reason": "The October gate is the last point at which the 60-day notice period clears the contract year end, so the option set is fixed by clause 11.4.",
    },
    "confidence_and_failure_mode": {
        "confidence": 0.71,
        "failure_mode": "If the regulatory deadline referenced in the benefit case moves left, the descope option becomes mandatory rather than optional and the cancellation recommendation is wrong. Detectable from the regulator's Q3 consultation response, due 2026-09-15.",
        "calibration_basis": "Reliability measured on 41 labelled preparation packs, 2025-2026. Brier score 0.19, small sample, treat the figure as indicative.",
        "detectable_at": "2026-09-15T00:00:00Z",
    },
    "reversal": {
        "how": "Withdraw the pack from the change authority agenda and re-issue with the revised regulatory position.",
        "cost_hours": 6.0,
        "cheap_until": "2026-09-26T00:00:00Z",
        "cheap_until_reason": "Change authority papers issue two weeks before the October gate.",
    },
    "owner": {
        "person_id": "u-1180",
        "name": "S. Lindqvist",
        "role": "change_authority_chair",
        "resolved_at": "2026-08-19T14:02:55Z",
    },
    "precedent_cases": [
        {
            "case_id": "PRG3:WS-DATA",
            "outcome": "Cancelled at gate, exit fee absorbed, forward saving realised",
            "relevance": "Same vendor, same MSA clause, comparable scope completion at cancellation",
        }
    ],
    "stakeholder_positions": [
        {
            "stakeholder": "Programme sponsor",
            "position": "Open to cancellation if the exit fee is contained",
            "source_id": "MIN:PRGBOARD:2026-08-06",
        }
    ],
    "second_order_impacts": [
        {
            "impact": "Two downstream workstreams lose their data-migration dependency and need re-planning",
            "affected_id": "PRG7:WS-REPORTING",
            "magnitude": "Re-plan of roughly 6 weeks",
        }
    ],
}

ARTIFACT_VERIFIER: Json = {
    "artifact_id": "vv-2026-0819-3310",
    "artifact_kind": "verifier_verdict",
    "decision_type": "verification_verdict",
    "decision_class": "A",
    "agent_id": "schedule-verifier-01",
    "agent_version": "2.1.0",
    "timestamp": "2026-08-19T09:14:31Z",
    "decision": "Pass decision artifact da-2026-0819-0447; all four slip-categorisation assertions hold.",
    "verdict": "pass",
    "proof_object": {
        "assertions": [
            {
                "check": "basis.source_ids all resolve",
                "expected": 3,
                "observed": 3,
                "passed": True,
            },
            {
                "check": "supplier notification within SLA clause 7.2 window",
                "expected": "<= 5 working days",
                "observed": "3 working days",
                "passed": True,
            },
            {
                "check": "float after absorption matches P6 network",
                "expected": 3.0,
                "observed": 3.0,
                "passed": True,
            },
            {
                "check": "no approved change request in the slip window",
                "expected": 0,
                "observed": 0,
                "passed": True,
            },
        ],
        "recheck_command": "vb gates --artifact da-2026-0819-0447 --gate evidence",
    },
    "calibration_record_ref": "CAL:schedule-verifier-01:2026-07-30",
    "basis": [
        {
            "source_id": "ART:da-2026-0819-0447",
            "retrieved_at": "2026-08-19T09:14:25Z",
            "detail": "Slip categorisation artifact under verification, 4 checkable assertions extracted",
        },
        {
            "source_id": "SUP:ACME:SLA:2025-11",
            "retrieved_at": "2026-08-19T09:14:27Z",
            "detail": "Clause 7.2 notification window is 5 working days",
        },
    ],
    "alternatives": [
        {
            "option": "Return the artifact as cannot_decide",
            "rejected_because": "All four assertions evaluated deterministically against resolvable sources, so no human judgement is required.",
            "rejection_kind": "factual",
        }
    ],
    "confidence_and_failure_mode": {
        "confidence": 0.98,
        "failure_mode": "If the SLA document was superseded after 2025-11, the notification-window assertion uses a stale threshold and a late notification would be passed. Detectable by comparing the contract register version on the nightly sync.",
        "calibration_basis": "Gate 3 run 2026-07-30 on 240 labelled decisions, 38 known-bad. FNR 0.021, containment CI95 [0.652, 0.762].",
    },
    "reversal": {
        "how": "Withdraw the pass verdict, return the artifact to the human review queue, and re-run the assertions against the current contract register.",
        "cost_hours": 0.02,
        "cheap_until": "2026-08-22T00:00:00Z",
        "cheap_until_reason": "Weekly slip report distribution to programme leads.",
    },
    "owner": {
        "person_id": "u-2291",
        "name": "R. Okonjo",
        "role": "portfolio_scheduler",
        "resolved_at": "2026-08-19T09:14:31Z",
    },
}


# --------------------------------------------------------------------------
# Valid agent contracts
# --------------------------------------------------------------------------

MANDATORY_ESCALATIONS = [
    {
        "id": "unclassified_type",
        "test": "decision_type not in scope.in_scope",
        "to_role": "pmo_lead",
    },
    {
        "id": "evidence_unavailable",
        "test": "any required evidence field cannot be produced",
        "to_role": "portfolio_scheduler",
    },
    {
        "id": "class_d_detected",
        "test": "classification result == D",
        "to_role": "change_authority_chair",
    },
]

SIX_FIELDS = [
    "decision",
    "basis",
    "alternatives",
    "confidence_and_failure_mode",
    "reversal",
    "owner",
]

CONTRACT_SCHEDULE_INTEGRITY: Json = {
    "agent_id": "schedule-integrity-01",
    "name": "Schedule Integrity Agent",
    "version": "1.4.0",
    "owner_role": "pmo_lead",
    "agent_kind": "agent",
    "scope": {
        "in_scope": [
            {
                "decision_type": "critical_path_recalculation",
                "decision_class": "A",
                "authority": "decide",
                "rate_limit_per_period": 200,
            },
            {
                "decision_type": "dependency_cycle_flagging",
                "decision_class": "A",
                "authority": "decide",
                "rate_limit_per_period": 120,
            },
            {
                "decision_type": "float_erosion_alert",
                "decision_class": "A",
                "authority": "decide",
                "rate_limit_per_period": 160,
            },
            {
                "decision_type": "milestone_slip_categorisation",
                "decision_class": "B",
                "authority": "decide",
                "sampling_rate": 0.15,
                "rate_limit_per_period": 160,
            },
        ],
        "excluded": [
            {
                "decision_type": "schedule_rebaselining",
                "reason": "Class C. Proposed by change-impact-01. This agent does not decide it.",
            },
            {
                "decision_type": "milestone_removal",
                "reason": "Class D. Requires change authority.",
            },
            {
                "decision_type": "baseline_approval",
                "reason": "Class D. Requires programme board.",
            },
        ],
        "unlisted_types": "escalate",
    },
    "evidence": {
        "required_fields": SIX_FIELDS,
        "artifact_schema": "schema/decision-artifact.schema.json",
        "on_evidence_failure": "escalate",
        "retention_days": 730,
    },
    "escalation": {
        "conditions": MANDATORY_ESCALATIONS
        + [
            {
                "id": "low_confidence",
                "test": "confidence < 0.80",
                "to_role": "portfolio_scheduler",
            },
            {
                "id": "cross_programme_impact",
                "test": "affected_programmes > 1",
                "to_role": "pmo_lead",
            },
            {
                "id": "critical_path_change",
                "test": "critical_path_changed and slip_days > 5",
                "to_role": "portfolio_scheduler",
            },
        ],
        "target_resolution": "named_person_at_decision_time",
        "max_response_hours": 8,
    },
    "revocation": {
        "who": ["pmo_lead", "head_of_delivery"],
        "method": "Set status to REVOKED in the agent registry. Single action, no approval chain.",
        "max_time_to_effect_minutes": 15,
        "in_flight_work": "halt_and_mark_unverified",
        "rollback": "Decisions from the last 24h flagged for human re-review. Class A decisions auto-revalidated by their deterministic check, which clears most of them without consuming budget.",
        "notify": ["portfolio_scheduler", "change_authority_chair"],
        "last_tested": "2026-07-14",
        "last_tested_seconds": 190,
    },
}

CONTRACT_CHANGE_IMPACT: Json = {
    "agent_id": "change-impact-01",
    "name": "Change Impact Agent",
    "version": "0.9.2",
    "owner_role": "change_authority_chair",
    "agent_kind": "agent",
    "scope": {
        "in_scope": [
            {
                "decision_type": "change_request_impact_assessment",
                "decision_class": "C",
                "authority": "propose",
                "rate_limit_per_period": 30,
            },
            {
                "decision_type": "schedule_rebaselining_proposal",
                "decision_class": "C",
                "authority": "propose",
                "rate_limit_per_period": 12,
            },
            {
                "decision_type": "workstream_cancellation_preparation",
                "decision_class": "C",
                "authority": "prepare",
                "rate_limit_per_period": 4,
                "prepares_class_d": "workstream_cancellation",
            },
        ],
        "excluded": [
            {
                "decision_type": "workstream_cancellation",
                "reason": "Class D. Prepared here, decided by change authority. Rule R2.",
            },
            {
                "decision_type": "contract_termination",
                "reason": "Class D. Legal and commercial. Not prepared here either.",
            },
            {
                "decision_type": "change_request_approval",
                "reason": "Class D. Change authority only.",
            },
        ],
        "unlisted_types": "escalate",
    },
    "evidence": {
        "required_fields": SIX_FIELDS,
        "artifact_schema": "schema/decision-artifact.schema.json",
        "on_evidence_failure": "escalate",
        "retention_days": 2555,
        "class_c_additions": [
            "precedent_cases",
            "stakeholder_positions",
            "second_order_impacts",
        ],
        "class_d_preparation_additions": [
            "recommendation",
            "options_with_costs",
            "reversal_cost_of_each_option",
        ],
    },
    "escalation": {
        "conditions": MANDATORY_ESCALATIONS
        + [
            {
                "id": "low_confidence",
                "test": "confidence < 0.85",
                "to_role": "change_authority_chair",
            },
            {
                "id": "contractual_exposure",
                "test": "commercial_impact > 250000 or contract_clause_triggered",
                "to_role": "commercial_lead",
            },
            {
                "id": "no_precedent",
                "test": "precedent_cases.length == 0",
                "to_role": "change_authority_chair",
            },
            {
                "id": "budget_pressure",
                "test": "class_c_overdraft_ratio > 1.0",
                "to_role": "pmo_lead",
            },
        ],
        "target_resolution": "named_person_at_decision_time",
        "max_response_hours": 24,
    },
    "revocation": {
        "who": ["change_authority_chair", "pmo_lead"],
        "method": "Set status to REVOKED in the agent registry.",
        "max_time_to_effect_minutes": 30,
        "in_flight_work": "halt_and_mark_unverified",
        "rollback": "All proposals from the last 7 days withdrawn from the change queue and re-submitted for human preparation. Any change request already approved on the basis of a withdrawn proposal is flagged to the change authority chair individually.",
        "notify": [
            "change_authority_chair",
            "pmo_lead",
            "commercial_lead",
            "head_of_delivery",
        ],
        "last_tested": "2026-08-02",
        "last_tested_seconds": 410,
    },
}

CONTRACT_VERIFIER: Json = {
    "agent_id": "schedule-verifier-01",
    "name": "Schedule Verifier",
    "version": "2.1.0",
    "owner_role": "pmo_lead",
    "agent_kind": "verifier",
    "verifies": {
        "agent_ids": ["schedule-integrity-01"],
        "decision_types": [
            "critical_path_recalculation",
            "dependency_cycle_flagging",
            "float_erosion_alert",
            "milestone_slip_categorisation",
        ],
    },
    "scope": {
        "in_scope": [
            {
                "decision_type": "verification_verdict",
                "decision_class": "A",
                "authority": "decide",
                "rate_limit_per_period": 640,
            }
        ],
        "excluded": [
            {
                "decision_type": "verification_verdict_class_c",
                "reason": "This verifier has no calibration on Class C. Uncalibrated means k = 0, so there is no point running it.",
            }
        ],
        "unlisted_types": "escalate",
    },
    "evidence": {
        "required_fields": SIX_FIELDS,
        "artifact_schema": "schema/decision-artifact.schema.json",
        "on_evidence_failure": "escalate",
        "retention_days": 730,
        "verifier_additions": ["verdict", "proof_object", "calibration_record_ref"],
    },
    "calibration": {
        "labelled_set_size": 240,
        "known_bad_count": 38,
        "measured_at": "2026-07-30",
        "false_negative_rate": 0.021,
        "false_positive_rate": 0.094,
        "containment_point_estimate": 0.71,
        "containment_ci95": [0.652, 0.762],
        "containment_used_in_budget": 0.652,
        "c_a_hours": 0.008,
        "gate_3_status": "pass",
        "next_recalibration_due": "2026-10-30",
    },
    "escalation": {
        "conditions": [
            {
                "id": "unclassified_type",
                "test": "decision_type not in verifies.decision_types",
                "to_role": "pmo_lead",
            },
            {
                "id": "evidence_unavailable",
                "test": "proof_object cannot be constructed",
                "to_role": "portfolio_scheduler",
            },
            {
                "id": "class_d_detected",
                "test": "classification result == D",
                "to_role": "change_authority_chair",
            },
            {
                "id": "cannot_decide",
                "test": "verdict == cannot_decide",
                "to_role": "portfolio_scheduler",
            },
            {
                "id": "calibration_stale",
                "test": "now > calibration.next_recalibration_due",
                "to_role": "pmo_lead",
            },
            {
                "id": "fnr_drift",
                "test": "rolling_30d_false_negative_rate > 0.05",
                "to_role": "pmo_lead",
            },
        ],
        "target_resolution": "named_person_at_decision_time",
        "max_response_hours": 4,
    },
    "revocation": {
        "who": ["pmo_lead", "head_of_delivery"],
        "method": "Set status to REVOKED. Containment k drops to 0 for all classes this verifier covered.",
        "max_time_to_effect_minutes": 5,
        "in_flight_work": "halt_and_mark_unverified",
        "rollback": "Decisions closed by this verifier in the last 72h re-enter the human review queue. This is a budget event: VB for Class A and B falls by roughly two thirds at the moment of revocation.",
        "notify": ["pmo_lead", "portfolio_scheduler", "head_of_delivery"],
        "last_tested": "2026-08-05",
        "last_tested_seconds": 95,
    },
}


VALID_ARTIFACTS: dict[str, Json] = {
    "artifact-class-a": ARTIFACT_A,
    "artifact-class-b": ARTIFACT_B,
    "artifact-class-c": ARTIFACT_C,
    "artifact-class-d-preparation": ARTIFACT_D_PREP,
    "artifact-verifier-verdict": ARTIFACT_VERIFIER,
}

VALID_CONTRACTS: dict[str, Json] = {
    "contract-schedule-integrity": CONTRACT_SCHEDULE_INTEGRITY,
    "contract-change-impact": CONTRACT_CHANGE_IMPACT,
    "contract-schedule-verifier": CONTRACT_VERIFIER,
}


# --------------------------------------------------------------------------
# Invalid fixtures, one broken rule each
# --------------------------------------------------------------------------


def _drop(base: Json, *path: str) -> Json:
    out = copy.deepcopy(base)
    node: Any = out
    for key in path[:-1]:
        node = node[key]
    node.pop(path[-1], None)
    return out


def _set(base: Json, value: Any, *path: str) -> Json:
    out = copy.deepcopy(base)
    node: Any = out
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return out


def build_invalid() -> list[dict[str, Any]]:
    """Return [{name, schema, doc, rule, why}] for every invalid fixture."""
    cases: list[dict[str, Any]] = []

    def art(name: str, doc: Json, rule: str, why: str) -> None:
        cases.append(
            {"name": name, "schema": "decision-artifact", "doc": doc, "rule": rule, "why": why}
        )

    def con(name: str, doc: Json, rule: str, why: str) -> None:
        cases.append(
            {"name": name, "schema": "agent-contract", "doc": doc, "rule": rule, "why": why}
        )

    # --- decision artifacts -------------------------------------------------
    art(
        "artifact-missing-owner",
        _drop(ARTIFACT_B, "owner"),
        "evidence-plane field 6",
        "No owner. An artifact missing any of the six fields is an output, not a decision.",
    )
    art(
        "artifact-missing-basis",
        _drop(ARTIFACT_B, "basis"),
        "evidence-plane field 2",
        "No basis. The reviewer has to re-gather every input, which is 40 to 60 percent of c.",
    )
    art(
        "artifact-basis-not-resolvable",
        _set(
            ARTIFACT_B,
            [
                {
                    "source_id": "the project plan",
                    "retrieved_at": "2026-08-19T09:14:22Z",
                    "detail": "Reviewed the schedule and supplier correspondence",
                }
            ],
            "basis",
        ),
        "B1",
        "source_id is free text, not a resolvable identifier.",
    )
    art(
        "artifact-empty-basis",
        _set(ARTIFACT_B, [], "basis"),
        "B1",
        "basis present but empty. Same effect as absent.",
    )
    art(
        "artifact-empty-alternatives",
        _set(ARTIFACT_B, [], "alternatives"),
        "A1",
        "No alternatives and no forced declaration. The review question stays unbounded.",
    )
    art(
        "artifact-hedged-failure-mode",
        _set(
            ARTIFACT_B,
            "The categorisation may be inaccurate if the underlying data is incorrect or incomplete.",
            "confidence_and_failure_mode",
            "failure_mode",
        ),
        "C3",
        "Prohibited hedging phrase. Carries no information and trains reviewers to skip the field.",
    )
    art(
        "artifact-confidence-out-of-range",
        _set(ARTIFACT_B, 1.4, "confidence_and_failure_mode", "confidence"),
        "C1",
        "Confidence outside the range 0 to 1, so it is not a probability and cannot be calibrated.",
    )
    art(
        "artifact-reversal-as-sentiment",
        _set(ARTIFACT_B, "Can be revisited", "reversal", "how"),
        "R1",
        "Reversal states a sentiment, not a procedure.",
    )
    art(
        "artifact-owner-role-not-person",
        _drop(ARTIFACT_B, "owner", "person_id"),
        "O1",
        "Owner is a role with no resolved person. Accountability diffuses and review becomes optional.",
    )
    art(
        "artifact-class-b-missing-batch",
        _drop(ARTIFACT_B, "batch_id"),
        "class B additions",
        "No batch_id. Sampling cannot bound a batch that cannot be identified.",
    )
    art(
        "artifact-class-c-missing-precedent",
        _drop(ARTIFACT_C, "precedent_cases"),
        "class C additions",
        "No precedent_cases. The reviewer redoes the retrieval the field exists to remove.",
    )
    art(
        "artifact-class-d-preparation-with-decision",
        _set(
            ARTIFACT_D_PREP,
            "Cancel the PRG7 legacy-migration workstream at the October gate.",
            "decision",
        ),
        "Class D rule",
        "A preparation pack containing a decision field is an agent that made a Class D decision.",
    )
    art(
        "artifact-class-d-decided",
        _set(_set(ARTIFACT_C, "D", "decision_class"), "decision", "artifact_kind"),
        "Class D rule",
        "A Class D artifact that is not a preparation pack. Class D is never delegated.",
    )
    art(
        "artifact-verifier-prose-proof",
        _set(
            ARTIFACT_VERIFIER,
            {"recheck_command": "read the reasoning below"},
            "proof_object",
        ),
        "E4",
        "Verifier proof object with no machine re-checkable assertions. Supplies an opinion, not containment.",
    )
    art(
        "artifact-verifier-missing-calibration-ref",
        _drop(ARTIFACT_VERIFIER, "calibration_record_ref"),
        "E3",
        "Verifier verdict with no calibration reference. Uncalibrated verifiers contribute k = 0.",
    )

    # --- agent contracts ----------------------------------------------------
    base = CONTRACT_SCHEDULE_INTEGRITY

    bad = copy.deepcopy(base)
    bad["scope"]["in_scope"].append(
        {
            "decision_type": "milestone_removal",
            "decision_class": "D",
            "authority": "decide",
        }
    )
    con(
        "contract-class-d-in-scope",
        bad,
        "R2",
        "Class D in scope. A Class D decision has no finite c, so no quantity of it is affordable.",
    )

    con(
        "contract-unlisted-not-escalate",
        _set(base, "allow", "scope", "unlisted_types"),
        "R1",
        "Unlisted decision types permitted. This is the back door the default exists to close.",
    )

    bad = copy.deepcopy(CONTRACT_CHANGE_IMPACT)
    bad["scope"]["in_scope"][0]["authority"] = "decide"
    con(
        "contract-class-c-authority-decide",
        bad,
        "R3",
        "Agent given authority to decide a Class C decision type. Class C is proposed, never decided.",
    )

    bad = copy.deepcopy(base)
    del bad["scope"]["in_scope"][3]["sampling_rate"]
    con(
        "contract-class-b-no-sampling-rate",
        bad,
        "R4",
        "Class B without a sampling rate is not sample-checked, so its c is unknown.",
    )

    con(
        "contract-evidence-failure-not-escalate",
        _set(base, "proceed", "evidence", "on_evidence_failure"),
        "E1",
        "Agent permitted to decide without evidence. There is no configuration under which this is acceptable.",
    )

    bad = copy.deepcopy(base)
    bad["evidence"]["required_fields"] = [
        f for f in SIX_FIELDS if f != "alternatives"
    ] + ["timestamp"]
    con(
        "contract-evidence-missing-alternatives",
        bad,
        "evidence-plane field 3",
        "alternatives not required, so the review question stays unbounded and c stays high.",
    )

    bad = copy.deepcopy(base)
    bad["escalation"]["conditions"] = [
        c for c in bad["escalation"]["conditions"] if c["id"] != "class_d_detected"
    ]
    con(
        "contract-missing-mandatory-escalation",
        bad,
        "S2",
        "No class_d_detected escalation. The agent has no defined stop on the one class it must never decide.",
    )

    con(
        "contract-escalation-to-unresolved-role",
        _set(base, "role_only", "escalation", "target_resolution"),
        "S3",
        "Escalation to a role that never resolves to a person is an escalation to nobody.",
    )

    con(
        "contract-single-revoker",
        _set(base, ["pmo_lead"], "revocation", "who"),
        "V1",
        "One revoker. Revocation depends on one person's availability.",
    )

    con(
        "contract-no-revocation",
        _drop(base, "revocation"),
        "field 4",
        "No revocation clause. Every other field is decoration.",
    )

    bad = copy.deepcopy(CONTRACT_CHANGE_IMPACT)
    bad["revocation"]["in_flight_work"] = "complete_then_halt"
    con(
        "contract-complete-then-halt-non-class-a",
        bad,
        "V3",
        "In-flight Class C work allowed to complete after revocation. That work is unverified.",
    )

    con(
        "contract-verifier-without-calibration",
        _drop(CONTRACT_VERIFIER, "calibration"),
        "E3",
        "Verifier claiming containment with no calibration record. k must be 0.",
    )

    bad = copy.deepcopy(CONTRACT_VERIFIER)
    bad["calibration"]["false_negative_rate"] = 0.14
    con(
        "contract-verifier-fnr-above-gate",
        bad,
        "Gate 3.1",
        "False-negative rate above 0.05. Bad decisions reach production wearing a green tick.",
    )

    bad = copy.deepcopy(CONTRACT_VERIFIER)
    bad["scope"]["in_scope"][0]["decision_class"] = "C"
    con(
        "contract-verifier-output-not-class-a",
        bad,
        "E4 and Gate 3.2",
        "Verifier output is Class C, so checking the verifier costs what checking the original cost. The cost moved, it did not go away.",
    )

    con(
        "contract-bad-version",
        _set(base, "1.4", "version"),
        "lifecycle",
        "Version is not semantic, so a material change cannot be distinguished from a patch.",
    )

    return cases


# --------------------------------------------------------------------------


def _write(path: Path, doc: Json) -> None:
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    VALID.mkdir(parents=True, exist_ok=True)
    INVALID.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "description": (
            "Fixtures for the VERB schemas. Every file under valid/ must validate. "
            "Every file under invalid/ must fail, for the stated reason. "
            "Regenerate with: python schema/fixtures/build_fixtures.py"
        ),
        "valid": [],
        "invalid": [],
    }

    for name, doc in VALID_ARTIFACTS.items():
        _write(VALID / f"{name}.json", doc)
        manifest["valid"].append({"file": f"valid/{name}.json", "schema": "decision-artifact"})

    for name, doc in VALID_CONTRACTS.items():
        _write(VALID / f"{name}.json", doc)
        manifest["valid"].append({"file": f"valid/{name}.json", "schema": "agent-contract"})

    for case in build_invalid():
        _write(INVALID / f"{case['name']}.json", case["doc"])
        manifest["invalid"].append(
            {
                "file": f"invalid/{case['name']}.json",
                "schema": case["schema"],
                "rule": case["rule"],
                "why": case["why"],
            }
        )

    _write(HERE / "manifest.json", manifest)

    print(f"valid:   {len(manifest['valid'])}")
    print(f"invalid: {len(manifest['invalid'])}")


if __name__ == "__main__":
    main()
