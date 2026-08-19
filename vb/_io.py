"""Loading a VERB bundle from disk.

A bundle is a directory. The only required file is ``config.json``; everything
else is optional and the tools degrade to whatever is present.

    config.json        class inputs, floors, period length. Required.
    decision_log.jsonl one decision per line. Needed for metrics, drift, gates.
    reviewers.csv      the roster. Informational; config carries the counts.
    projects.csv       the portfolio. Informational.
    timing.csv         the c-hat calibration sample and drift baseline.
    gate_data.json     Gate 1 classifier pairs, Gate 3 labelled set, Gate 4 replay.

See examples/pmo40 for a worked bundle, and examples/generate_pmo40.py for how
it is produced.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

__all__ = ["Bundle", "BundleError", "load_bundle", "read_jsonl"]


class BundleError(RuntimeError):
    """Raised when a bundle is missing or malformed."""


@dataclass
class Bundle:
    """A loaded bundle."""

    path: Path
    config: dict[str, Any]
    events: list[dict[str, Any]] = field(default_factory=list)
    reviewers: list[dict[str, str]] = field(default_factory=list)
    projects: list[dict[str, str]] = field(default_factory=list)
    timing: list[dict[str, str]] = field(default_factory=list)
    gate_data: dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return str(self.config.get("name", self.path.name))

    @property
    def synthetic(self) -> bool:
        return bool(self.config.get("synthetic", False))

    @property
    def periods(self) -> int:
        value = int(self.config.get("periods", 1))
        if value < 1:
            raise BundleError(f"{self.path}: config periods must be at least 1")
        return value

    @property
    def period_name(self) -> str:
        return str(self.config.get("period", "period"))

    @property
    def class_config(self) -> dict[str, dict[str, Any]]:
        classes = self.config.get("classes")
        if not isinstance(classes, dict) or not classes:
            raise BundleError(f"{self.path}: config has no 'classes' block")
        return classes

    def events_for(self, decision_class: str) -> list[dict[str, Any]]:
        return [e for e in self.events if e.get("decision_class") == decision_class]

    def timing_for(self, decision_class: str, genuine_only: bool = True) -> list[dict[str, str]]:
        rows = [r for r in self.timing if r.get("decision_class") == decision_class]
        if genuine_only:
            rows = [r for r in rows if _truthy(r.get("genuinely_checked"))]
        return rows


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield one dict per non-blank line. Reports the line number on a parse error."""
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise BundleError(f"{path}:{number}: {exc}") from exc
            if not isinstance(record, dict):
                raise BundleError(f"{path}:{number}: expected an object, got {type(record).__name__}")
            yield record


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_bundle(path: str | Path) -> Bundle:
    """Load a bundle directory.

    Raises:
        BundleError: if the directory or config.json is missing.
    """
    root = Path(path)
    if not root.exists():
        raise BundleError(f"no such bundle: {root}")
    if not root.is_dir():
        raise BundleError(f"bundle must be a directory, got a file: {root}")

    config_path = root / "config.json"
    if not config_path.exists():
        raise BundleError(
            f"{root}: no config.json. A bundle needs at least the class inputs. "
            "See examples/pmo40/config.json for the shape."
        )
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BundleError(f"{config_path}: {exc}") from exc

    bundle = Bundle(path=root, config=config)

    log_path = root / "decision_log.jsonl"
    if log_path.exists():
        bundle.events = list(read_jsonl(log_path))

    for attr, filename in (
        ("reviewers", "reviewers.csv"),
        ("projects", "projects.csv"),
        ("timing", "timing.csv"),
    ):
        csv_path = root / filename
        if csv_path.exists():
            setattr(bundle, attr, _read_csv(csv_path))

    gate_path = root / "gate_data.json"
    if gate_path.exists():
        try:
            bundle.gate_data = json.loads(gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise BundleError(f"{gate_path}: {exc}") from exc

    return bundle
