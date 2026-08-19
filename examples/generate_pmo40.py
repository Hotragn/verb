"""Generate the synthetic PMO-40 bundle.

    python examples/generate_pmo40.py

Writes examples/pmo40/. Seeded, so it reproduces exactly. Committed to the
repository so that `vb budget --input examples/pmo40` works on a fresh clone.

THESE NUMBERS ARE SYNTHETIC. PMO-40 is an organisation that does not exist. The
bundle demonstrates that the arithmetic works and the tooling reproduces. It is
not a measurement of anything and it should never be cited as evidence. See
README limitation 8.

Design notes, because a synthetic dataset that hides its construction is worse
than useless:

* Per-class counts are structural, not random. The generator places exactly N
  decisions per class per week and exactly M below-floor approvals per week, so
  the headline figures do not depend on the random number generator's behaviour
  across Python versions. Randomness sets the texture, never the totals.

* Class C sits at 3.3x its verification budget from week 1. Genuine reviews are
  pinned at 21 per week, which is the budget. Everything approved above that line
  is drift, and everything not approved joins the queue. That is the whole
  mechanism: the overdraft becomes backlog first, then drift.

* A verifier covers Class A and Class B and not Class C. This is deliberate.
  Agentic verification supplies budget where a machine-checkable verdict is
  possible, which is exactly where checking was already cheap. It does nothing
  for the class that is drowning, which is the deployment inversion restated.
"""

from __future__ import annotations

import csv
import json
import math
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

SEED = 4242
HERE = Path(__file__).resolve().parent

# Run from anywhere, including a fresh clone with nothing installed. The floor
# arithmetic is imported from vb rather than reimplemented, so the generator
# cannot drift away from the tool that reads its output.
sys.path.insert(0, str(HERE.parent))
OUT = HERE / "pmo40"
FIXTURES = HERE.parent / "schema" / "fixtures" / "valid"

WEEKS = 8
PROJECTS = 40
START = datetime(2026, 6, 22, 8, 0, 0, tzinfo=timezone.utc)  # a Monday

# --------------------------------------------------------------------------
# Structural parameters. Changing these changes the headline figures.
# --------------------------------------------------------------------------

#: Decisions produced per week, per class. Demand is counted from the log.
DEMAND_PER_WEEK = {"A": 320, "B": 160, "C": 70, "D": 0}

#: Approvals per week, per class. Class C cannot approve everything it produces.
APPROVALS_PER_WEEK = {
    "A": [320] * WEEKS,
    "B": [160] * WEEKS,
    # Genuine reviews pinned at 21, the Class C budget. Everything above is drift.
    "C": [24, 25, 26, 28, 31, 34, 38, 44],
}

#: Below-floor approvals per week, per class. Class A and B sit at the 10 percent
#: baseline a P10 floor produces when nothing is wrong.
DRIFT_PER_WEEK = {
    "A": [30, 33, 31, 34, 30, 32, 33, 31],
    "B": [15, 17, 16, 16, 18, 15, 17, 16],
    "C": [3, 4, 5, 7, 10, 13, 17, 23],
}

CLASS_SETTINGS: dict[str, dict[str, Any]] = {
    "A": {
        "reviewers": 14,
        "hours_per_period": 8,
        "utilisation": 0.55,
        "cost_per_decision": 0.02,
        "agent_check_cost": 0.005,
        "cost_measured_at": "2026-07-08",
        "median_artifact_words": 110,
        "floor_percentile": 10.0,
        "verifier": True,
    },
    "B": {
        "reviewers": 9,
        "hours_per_period": 8,
        "utilisation": 0.55,
        "cost_per_decision": 0.15,
        "agent_check_cost": 0.010,
        "cost_measured_at": "2026-07-08",
        "median_artifact_words": 700,
        "floor_percentile": 10.0,
        "verifier": True,
    },
    "C": {
        "reviewers": 6,
        "hours_per_period": 8,
        "utilisation": 0.55,
        "cost_per_decision": 1.25,
        "agent_check_cost": 0.0,
        "cost_measured_at": "2026-07-08",
        "median_artifact_words": 2100,
        "floor_percentile": 10.0,
        "verifier": False,
    },
    "D": {
        "reviewers": 6,
        "hours_per_period": 8,
        "utilisation": 0.55,
        "cost_per_decision": None,
        "agent_check_cost": 0.0,
        "median_artifact_words": 3400,
        "verifier": False,
    },
}

#: Quantile curves for review durations, in hours. Built so that the median lands
#: on the configured c and the P10 lands on a defensible floor.
DURATION_QUANTILES: dict[str, list[tuple[float, float]]] = {
    "A": [(0.0, 0.005), (0.10, 0.008), (0.25, 0.012), (0.50, 0.020),
          (0.75, 0.031), (0.90, 0.045), (1.0, 0.070)],
    "B": [(0.0, 0.030), (0.10, 0.045), (0.25, 0.085), (0.50, 0.150),
          (0.75, 0.240), (0.90, 0.330), (1.0, 0.480)],
    "C": [(0.0, 0.220), (0.10, 0.300), (0.25, 0.850), (0.50, 1.250),
          (0.75, 2.100), (0.90, 2.900), (1.0, 3.600)],
}

CALIBRATION_SAMPLE = {"A": 44, "B": 38, "C": 34}

DECISION_TYPES: dict[str, list[str]] = {
    "A": [
        "critical_path_recalculation",
        "dependency_cycle_flagging",
        "float_erosion_alert",
        "budget_rollup_reconciliation",
        "raid_register_completeness",
        "resource_overallocation_detection",
        "invoice_to_po_match",
        "baseline_variance_threshold",
    ],
    "B": [
        "milestone_slip_categorisation",
        "status_narrative_draft",
        "meeting_action_extraction",
        "risk_rescoring_against_rubric",
        "change_request_categorisation",
        "rag_rating_proposal",
    ],
    "C": [
        "schedule_rebaselining_proposal",
        "change_request_impact_assessment",
        "resource_reallocation_across_programmes",
        "vendor_scope_dispute_position",
        "forecast_revision_beyond_tolerance",
        "dependency_renegotiation",
        "workstream_cancellation_preparation",
    ],
}

AGENTS = {
    "A": "schedule-integrity-01",
    "B": "schedule-integrity-01",
    "C": "change-impact-01",
}

PROGRAMMES = ["PRG1", "PRG3", "PRG4", "PRG7", "PRG9"]
PHASES = ["initiation", "planning", "delivery", "integration", "closure"]

REVIEWERS: list[dict[str, Any]] = [
    {"reviewer_id": "u-1180", "name": "S. Lindqvist", "role": "change_authority_chair", "classes": "A,B,C"},
    {"reviewer_id": "u-2291", "name": "R. Okonjo", "role": "portfolio_scheduler", "classes": "A,B,C"},
    {"reviewer_id": "u-3042", "name": "M. Haddad", "role": "portfolio_scheduler", "classes": "A,B,C"},
    {"reviewer_id": "u-3119", "name": "J. Whitfield", "role": "programme_manager", "classes": "A,B,C"},
    {"reviewer_id": "u-3388", "name": "A. Bergstrom", "role": "programme_manager", "classes": "A,B,C"},
    {"reviewer_id": "u-3450", "name": "P. Nakamura", "role": "pmo_lead", "classes": "A,B,C"},
    {"reviewer_id": "u-4021", "name": "D. Castellanos", "role": "project_manager", "classes": "A,B"},
    {"reviewer_id": "u-4088", "name": "L. Fitzgerald", "role": "project_manager", "classes": "A,B"},
    {"reviewer_id": "u-4133", "name": "T. Abebe", "role": "project_manager", "classes": "A,B"},
    {"reviewer_id": "u-5010", "name": "K. Sorensen", "role": "pmo_analyst", "classes": "A"},
    {"reviewer_id": "u-5044", "name": "N. Varga", "role": "pmo_analyst", "classes": "A"},
    {"reviewer_id": "u-5077", "name": "H. Osei", "role": "pmo_analyst", "classes": "A"},
    {"reviewer_id": "u-5091", "name": "C. Delacroix", "role": "pmo_analyst", "classes": "A"},
    {"reviewer_id": "u-5123", "name": "E. Novak", "role": "pmo_analyst", "classes": "A"},
]


def reviewers_for(decision_class: str) -> list[str]:
    return [r["reviewer_id"] for r in REVIEWERS if decision_class in str(r["classes"]).split(",")]


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def quantile_value(curve: Sequence[tuple[float, float]], p: float) -> float:
    """Piecewise linear inverse CDF."""
    p = min(1.0, max(0.0, p))
    for i in range(len(curve) - 1):
        p0, v0 = curve[i]
        p1, v1 = curve[i + 1]
        if p0 <= p <= p1:
            if p1 == p0:
                return v0
            return v0 + (p - p0) / (p1 - p0) * (v1 - v0)
    return curve[-1][1]


def sample_duration(rng: random.Random, decision_class: str, below_floor: float | None = None) -> float:
    """Draw a review duration.

    ``below_floor`` forces the draw beneath a floor, for a drift event. Drift
    durations sit clearly under the floor rather than just under it, because a
    reviewer who is not checking is not spending 99 percent of the floor.
    """
    curve = DURATION_QUANTILES[decision_class]
    if below_floor is not None:
        return round(below_floor * rng.uniform(0.18, 0.80), 5)
    # Draw from above P12 so a genuine review is never mistaken for drift.
    return round(quantile_value(curve, rng.uniform(0.12, 1.0)), 5)


def calibration_durations(decision_class: str, n: int) -> list[float]:
    """Deterministic calibration sample: exact quantile positions.

    Using exact positions rather than random draws means the derived floor is a
    property of the design rather than of the seed.
    """
    curve = DURATION_QUANTILES[decision_class]
    return [round(quantile_value(curve, i / (n - 1)), 5) for i in range(n)]


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def week_moment(rng: random.Random, week: int) -> datetime:
    """A plausible working moment inside the given week."""
    day = rng.randint(0, 4)
    hour = rng.choice([9, 10, 11, 13, 14, 15, 16, 16, 17])
    return START + timedelta(weeks=week - 1, days=day, hours=hour - 8, minutes=rng.randint(0, 59))


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------


def build_projects(rng: random.Random) -> list[dict[str, Any]]:
    projects = []
    for i in range(1, PROJECTS + 1):
        projects.append(
            {
                "project_id": f"P-{i:03d}",
                "name": f"Workstream {i:02d}",
                "programme": PROGRAMMES[(i - 1) % len(PROGRAMMES)],
                "phase": PHASES[(i * 3) % len(PHASES)],
                "budget_kgbp": 250 + rng.randrange(0, 60) * 25,
                "agent_enabled": "yes",
            }
        )
    return projects


def build_events(rng: random.Random) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    counters = {"A": 0, "B": 0, "C": 0}
    floors = {c: derived_floor(c) for c in ("A", "B", "C")}
    queue_depth = 0

    for week in range(1, WEEKS + 1):
        for decision_class in ("A", "B", "C"):
            demand = DEMAND_PER_WEEK[decision_class]
            approvals = APPROVALS_PER_WEEK[decision_class][week - 1]
            drift_count = DRIFT_PER_WEEK[decision_class][week - 1]
            floor = floors[decision_class]
            pool = reviewers_for(decision_class)
            settings = CLASS_SETTINGS[decision_class]

            # Which of this week's decisions get approved, and which of those drift.
            slots = list(range(demand))
            rng.shuffle(slots)
            approved = set(slots[:approvals])
            drifted = set(slots[:drift_count])  # drift is a subset of approvals

            # From week 5, some Class C drift arrives as end-of-week batches: one
            # reviewer clearing several artifacts inside a minute. This is the
            # secondary burst signal, and it appears as drift rises rather than
            # before it, which is how it shows up in practice.
            burst_plan: dict[int, tuple[str, datetime]] = {}
            if decision_class == "C" and week >= 5:
                ordered = sorted(drifted)
                for start in range(0, len(ordered), 4):
                    group = ordered[start : start + 4]
                    if len(group) < 3:
                        continue
                    anchor_reviewer = pool[(week + start) % len(pool)]
                    anchor_time = START + timedelta(
                        weeks=week - 1, days=4, hours=9, minutes=30 + start
                    )
                    for offset, slot in enumerate(group):
                        burst_plan[slot] = (
                            anchor_reviewer,
                            anchor_time + timedelta(seconds=offset * 17),
                        )

            for index in range(demand):
                counters[decision_class] += 1
                created = week_moment(rng, week)
                decision_type = rng.choice(DECISION_TYPES[decision_class])
                project = f"P-{rng.randint(1, PROJECTS):03d}"
                reviewer = rng.choice(pool)

                event: dict[str, Any] = {
                    "artifact_id": f"da-{decision_class}-{counters[decision_class]:05d}",
                    "period": week,
                    "timestamp": iso(created),
                    "project_id": project,
                    "decision_type": decision_type,
                    "decision_class": decision_class,
                    "agent_id": AGENTS[decision_class],
                    "owner_id": reviewer,
                }

                if index in approved:
                    duration = sample_duration(
                        rng, decision_class, below_floor=floor if index in drifted else None
                    )
                    if index in burst_plan:
                        reviewer, submitted = burst_plan[index]
                        event["owner_id"] = reviewer
                    else:
                        submitted = created + timedelta(
                            days=rng.randint(0, 3), hours=rng.randint(1, 8)
                        )
                    event.update(
                        {
                            "outcome": "approved",
                            "reviewer_id": reviewer,
                            "review_seconds": round(duration * 3600, 1),
                            "idle_trimmed_seconds": round(duration * 3600, 1),
                            "submitted_at": iso(submitted),
                            "submitted_at_epoch": int(submitted.timestamp()),
                            "queued_days": round((submitted - created).total_seconds() / 86400, 2),
                        }
                    )
                else:
                    event.update(
                        {
                            "outcome": "queued",
                            "reviewer_id": None,
                            "review_seconds": None,
                            "idle_trimmed_seconds": None,
                            "queued_days": None,
                        }
                    )

                # Escalations. They consume budget at the class cost, which is why
                # escalation precision is one of the six metrics.
                escalation_rate = {"A": 0.02, "B": 0.06, "C": 0.12}[decision_class]
                if rng.random() < escalation_rate:
                    event["escalated"] = True
                    event["escalation_upheld"] = rng.random() < {"A": 0.81, "B": 0.77, "C": 0.74}[decision_class]
                else:
                    event["escalated"] = False
                    event["escalation_upheld"] = None

                # Agentic verification. Class A and B only.
                if settings["verifier"]:
                    event["verifier_offered"] = True
                    target_k = {"A": 0.71, "B": 0.56}[decision_class]
                    known_bad = rng.random() < 0.025
                    event["known_bad"] = known_bad
                    if known_bad:
                        # Two verifiers, deliberately different. The Class A verifier
                        # lets roughly one in fifty known-bad decisions through and
                        # clears Gate 3. The Class B verifier lets roughly one in
                        # eleven through, lands above the 0.05 false-negative bar,
                        # and is therefore assigned k = 0 while still running as an
                        # advisory annotation. Both outcomes are designed, not drawn.
                        slip_rate = {"A": 0.020, "B": 0.090}[decision_class]
                        slipped = rng.random() < slip_rate
                        # A reject with a machine-checkable reason is still
                        # contained: it closed without human involvement. Only a
                        # pass on a known-bad decision is a false negative.
                        event["verifier_contained"] = True
                        event["verifier_verdict"] = "pass" if slipped else "reject"
                    else:
                        contained = rng.random() < target_k
                        event["verifier_contained"] = contained
                        event["verifier_verdict"] = "pass" if contained else "cannot_decide"
                else:
                    event["verifier_offered"] = False
                    event["known_bad"] = False
                    event["verifier_contained"] = False
                    event["verifier_verdict"] = None

                # Reversals. Audits the evidence plane's reversal field.
                reversal_rate = {"A": 0.004, "B": 0.018, "C": 0.043}[decision_class]
                if event["outcome"] == "approved" and rng.random() < reversal_rate:
                    cheap_until_hours = {"A": 168.0, "B": 336.0, "C": 336.0}[decision_class]
                    latency = round(rng.lognormvariate(math.log(30), 1.15), 1)
                    event["reversed"] = True
                    event["reversed_after_hours"] = latency
                    event["cheap_until_hours"] = cheap_until_hours
                    event["reversed_after_cheap_until"] = latency > cheap_until_hours
                else:
                    event["reversed"] = False
                    event["reversed_after_hours"] = None
                    event["cheap_until_hours"] = None
                    event["reversed_after_cheap_until"] = False

                events.append(event)

            if decision_class == "C":
                queue_depth += demand - approvals

    return events


def derived_floor(decision_class: str) -> float:
    """The floor this bundle's calibration sample produces, for use while generating.

    Recomputed by vb at read time from timing.csv; this is the same arithmetic so
    that the generator places drift events on the correct side of the line.
    """
    from vb._stats import percentile

    durations = calibration_durations(decision_class, CALIBRATION_SAMPLE[decision_class])
    settings = CLASS_SETTINGS[decision_class]
    baseline = percentile(durations, float(settings["floor_percentile"]))
    reading = float(settings["median_artifact_words"]) / 240.0 / 60.0
    return max(baseline, reading)


def build_timing(rng: random.Random) -> list[dict[str, Any]]:
    """The c-hat calibration sample and the drift baseline. One collection round.

    Includes observations the reviewer afterwards said were not genuine. Those are
    discarded when computing c-hat, and that discard is the step everybody skips.
    """
    rows: list[dict[str, Any]] = []
    observation = 0
    for decision_class, n in CALIBRATION_SAMPLE.items():
        durations = calibration_durations(decision_class, n)
        pool = reviewers_for(decision_class)
        for duration in durations:
            observation += 1
            raw = duration * rng.uniform(1.02, 1.35)  # before idle trimming
            rows.append(
                {
                    "observation_id": f"obs-{observation:04d}",
                    "decision_class": decision_class,
                    "reviewer_id": pool[observation % len(pool)],
                    "observed_on": "2026-07-08",
                    "raw_seconds": round(raw * 3600, 1),
                    "idle_trimmed_seconds": round(duration * 3600, 1),
                    "artifact_words": CLASS_SETTINGS[decision_class]["median_artifact_words"],
                    "genuinely_checked": "true",
                }
            )
        # Discarded observations: the reviewer said afterwards they did not check.
        for _ in range({"A": 5, "B": 4, "C": 6}[decision_class]):
            observation += 1
            duration = durations[0] * rng.uniform(0.2, 0.6)
            rows.append(
                {
                    "observation_id": f"obs-{observation:04d}",
                    "decision_class": decision_class,
                    "reviewer_id": pool[observation % len(pool)],
                    "observed_on": "2026-07-08",
                    "raw_seconds": round(duration * 3600, 1),
                    "idle_trimmed_seconds": round(duration * 3600, 1),
                    "artifact_words": CLASS_SETTINGS[decision_class]["median_artifact_words"],
                    "genuinely_checked": "false",
                }
            )
    return rows


def build_gate_data(rng: random.Random) -> dict[str, Any]:
    """Gate inputs. Sized so that all four gates pass on the reference bundle.

    Failure paths are exercised by the unit tests rather than by the example,
    because a reference bundle that fails its own gates teaches the wrong thing.
    """
    scope_types = DECISION_TYPES["A"] + DECISION_TYPES["B"] + DECISION_TYPES["C"]

    # Gate 1: 50 decisions, two classifiers, 6 disagreements, none involving D-in-scope.
    truth = (["A"] * 18) + (["B"] * 16) + (["C"] * 13) + (["D"] * 3)
    classifier_a = list(truth)
    classifier_b = list(truth)
    disagreements = [2, 9, 21, 28, 34, 41]
    shift = {"A": "B", "B": "C", "C": "B", "D": "D"}
    for index in disagreements:
        classifier_b[index] = shift[classifier_b[index]]
    # The three genuine Class D decisions must not sit on an in-scope type.
    decision_types = []
    for i, label in enumerate(truth):
        if label == "D":
            decision_types.append("workstream_cancellation")
        else:
            decision_types.append(rng.choice(DECISION_TYPES[label]))

    # Gate 2: real artifacts from the schema fixtures, re-identified.
    artifacts: list[dict[str, Any]] = []
    for path in sorted(FIXTURES.glob("artifact-*.json")):
        base = json.loads(path.read_text(encoding="utf-8"))
        for copy_index in range(5):
            clone = json.loads(json.dumps(base))
            clone["artifact_id"] = f"{base['artifact_id']}-s{copy_index}"
            artifacts.append(clone)
    substantive = [True] * 20
    substantive[7] = False  # 19 of 20, which is 0.95

    # Gate 3: 240 labelled decisions, 38 known bad, 1 false negative.
    labelled: list[dict[str, Any]] = []
    for i in range(240):
        known_bad = i < 38
        if known_bad:
            verdict = "pass" if i == 11 else "reject"  # exactly one false negative
        else:
            verdict = "pass" if rng.random() < 0.65 else "cannot_decide"
        labelled.append(
            {
                "record_id": f"cal-{i:04d}",
                "known_bad": known_bad,
                "verdict": verdict,
                "contained": verdict in ("pass", "reject"),
            }
        )

    # Gate 4: 120 replay records, point-in-time blind, no autonomous Class D.
    replay: list[dict[str, Any]] = []
    for i in range(120):
        decision_class = rng.choice(["A", "A", "B", "B", "C"])
        historical_ok = rng.random() < 0.78
        agent_ok = rng.random() < 0.85
        escalated = rng.random() < 0.15
        replay.append(
            {
                "record_id": f"rep-{i:04d}",
                "decision_type": rng.choice(DECISION_TYPES[decision_class]),
                "agent_class": decision_class,
                "agent_authority": "propose" if decision_class == "C" else "decide",
                "historical_outcome_ok": historical_ok,
                "agent_outcome_ok": agent_ok,
                "adjudication_hours": round(rng.uniform(0.1, 1.1), 2),
                "escalated": escalated,
                "escalation_upheld": (rng.random() < 0.72) if escalated else None,
            }
        )

    return {
        "classification": {
            "note": "Two qualified classifiers, independently, on 50 sampled decisions.",
            "classifier_a": classifier_a,
            "classifier_b": classifier_b,
            "decision_types": decision_types,
            "scope_types": scope_types,
            "disagreements_logged": True,
        },
        "evidence": {
            "note": "Artifacts drawn from schema/fixtures/valid. Human sample of 20, one failure.",
            "artifacts": artifacts,
            "substantive_sample": substantive,
            "measured_cost_hours": 1.31,
            "budgeted_cost_hours": 1.25,
        },
        "verifier_calibration": {
            "note": "240 labelled decisions, 38 known bad, one false negative.",
            "agent_id": "schedule-verifier-01",
            "verifier_output_class": "A",
            "cost_remeasured": True,
            "labelled_set": labelled,
        },
        "replay": {
            "note": "120 historical decisions with known outcomes, point-in-time blind.",
            "scope_types": scope_types,
            "cost_hours": 1.25,
            "records": replay,
        },
    }


def build_config() -> dict[str, Any]:
    classes: dict[str, Any] = {}
    for decision_class, settings in CLASS_SETTINGS.items():
        entry = {
            "reviewers": settings["reviewers"],
            "hours_per_period": settings["hours_per_period"],
            "utilisation": settings["utilisation"],
            "cost_per_decision": settings["cost_per_decision"],
            "agent_check_cost": settings["agent_check_cost"],
            "median_artifact_words": settings["median_artifact_words"],
        }
        if "cost_measured_at" in settings:
            entry["cost_measured_at"] = settings["cost_measured_at"]
        if "floor_percentile" in settings:
            entry["floor_percentile"] = settings["floor_percentile"]
        classes[decision_class] = entry

    return {
        "name": "PMO-40",
        "synthetic": True,
        "warning": (
            "Synthetic. PMO-40 is an organisation that does not exist. These figures "
            "demonstrate that the arithmetic works and the tooling reproduces. They are "
            "not evidence and must not be cited as evidence."
        ),
        "generated_by": "examples/generate_pmo40.py",
        "seed": SEED,
        "period": "week",
        "periods": WEEKS,
        "projects": PROJECTS,
        "reviewers_total": len(REVIEWERS),
        "classes": classes,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    projects = build_projects(rng)
    events = build_events(rng)
    timing = build_timing(rng)
    gate_data = build_gate_data(rng)

    (OUT / "config.json").write_text(
        json.dumps(build_config(), indent=2) + "\n", encoding="utf-8"
    )

    # Null-valued keys are dropped rather than written. Every reader uses .get(),
    # so absence and null are equivalent, and the log is a good deal smaller.
    with (OUT / "decision_log.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            lean = {k: v for k, v in event.items() if v is not None}
            handle.write(json.dumps(lean, separators=(",", ":")) + "\n")

    write_csv(OUT / "projects.csv", projects)
    write_csv(
        OUT / "reviewers.csv",
        [
            {
                "reviewer_id": r["reviewer_id"],
                "name": r["name"],
                "role": r["role"],
                "qualified_classes": r["classes"],
                "hours_per_period": 8,
                "utilisation": 0.55,
            }
            for r in REVIEWERS
        ],
    )
    write_csv(OUT / "timing.csv", timing)
    (OUT / "gate_data.json").write_text(
        json.dumps(gate_data, indent=2) + "\n", encoding="utf-8"
    )

    print(f"wrote {OUT}")
    print(f"  projects        {len(projects)}")
    print(f"  reviewers       {len(REVIEWERS)}")
    print(f"  decisions       {len(events)}  ({WEEKS} weeks)")
    print(f"  timing rows     {len(timing)}")
    for decision_class in ("A", "B", "C"):
        print(f"  floor {decision_class}         {derived_floor(decision_class):.5f} h")


if __name__ == "__main__":
    main()
