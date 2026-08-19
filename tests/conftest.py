"""Shared fixtures.

The repository root goes on sys.path so the suite runs on a fresh clone without
an install, which matters because the CI workflow runs it both ways.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vb._io import Bundle, load_bundle  # noqa: E402


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def pmo40() -> Bundle:
    """The synthetic reference bundle. Loaded once; treat as read-only."""
    return load_bundle(ROOT / "examples" / "pmo40")


@pytest.fixture(scope="session")
def schema_dir() -> Path:
    return ROOT / "schema"


def valid_artifact() -> dict:
    """A minimal structurally valid Class A decision artifact.

    Built here rather than read from a fixture file so that the structural tests
    fail on the code rather than on a file move.
    """
    return {
        "artifact_id": "da-test-0001",
        "artifact_kind": "decision",
        "decision_type": "critical_path_recalculation",
        "decision_class": "A",
        "agent_id": "schedule-integrity-01",
        "timestamp": "2026-08-19T08:02:11Z",
        "decision": "Recalculate critical path for PRG7 after task T-4419 update; path unchanged.",
        "basis": [
            {
                "source_id": "P6:PRG7:network:v88",
                "retrieved_at": "2026-08-19T08:02:04Z",
                "detail": "412 activities, 3 open constraint violations",
            }
        ],
        "alternatives": [
            {
                "option": "Flag the change as a critical path shift",
                "rejected_because": "Float on T-4419 remains 9d, above the 0d threshold.",
            }
        ],
        "confidence_and_failure_mode": {
            "confidence": 0.99,
            "failure_mode": (
                "If the P6 network export is stale, the recalculation runs on a superseded "
                "logic set and the unchanged verdict is wrong. Detectable at the 09:00 sync."
            ),
            "calibration_basis": "Deterministic. Verified on 1,000 networks, 2026-Q2.",
        },
        "reversal": {
            "how": "Re-run the forward and backward pass against the corrected export.",
            "cost_hours": 0.05,
            "cheap_until": "2026-08-26T00:00:00Z",
            "cheap_until_reason": "Weekly float report distribution.",
        },
        "owner": {
            "person_id": "u-2291",
            "name": "R. Okonjo",
            "role": "portfolio_scheduler",
            "resolved_at": "2026-08-19T08:02:11Z",
        },
    }


@pytest.fixture
def artifact() -> dict:
    return valid_artifact()
