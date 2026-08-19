"""Validate every fixture against the schemas. Used by CI and runnable by hand.

    python scripts/validate_schemas.py

Exits non-zero if a valid fixture fails, if an invalid fixture passes, or if
either schema is not a well-formed draft 2020-12 schema. The test suite covers
the same ground; this exists so the check can run as its own CI job with a
readable report, and so a contributor can run it without pytest.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover
    sys.exit(
        "jsonschema is not installed. It is a development dependency, not a\n"
        "runtime one: the vb package itself has none.\n\n"
        "    pip install -e \".[dev]\"\n"
    )

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
FIXTURES = SCHEMA_DIR / "fixtures"

GREEN = "\033[32m" if sys.stdout.isatty() else ""
RED = "\033[31m" if sys.stdout.isatty() else ""
DIM = "\033[2m" if sys.stdout.isatty() else ""
RESET = "\033[0m" if sys.stdout.isatty() else ""


def main() -> int:
    failures: list[str] = []

    validators: dict[str, Draft202012Validator] = {}
    for name in ("decision-artifact", "agent-contract"):
        path = SCHEMA_DIR / f"{name}.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            failures.append(f"{path.name} is not a valid draft 2020-12 schema: {exc}")
            continue
        validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
        print(f"{GREEN}ok{RESET}    schema {name}")

    if failures:
        for line in failures:
            print(f"{RED}FAIL{RESET}  {line}")
        return 1

    manifest = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))

    print()
    print(f"valid fixtures ({len(manifest['valid'])}) must all validate")
    for entry in manifest["valid"]:
        document = json.loads((FIXTURES / entry["file"]).read_text(encoding="utf-8"))
        errors = sorted(
            validators[entry["schema"]].iter_errors(document), key=lambda e: list(e.path)
        )
        if errors:
            failures.append(entry["file"])
            print(f"{RED}FAIL{RESET}  {entry['file']}")
            for error in errors[:3]:
                location = "/".join(str(p) for p in error.path) or "(root)"
                print(f"        {location}: {error.message}")
        else:
            print(f"{GREEN}ok{RESET}    {entry['file']}")

    print()
    print(f"invalid fixtures ({len(manifest['invalid'])}) must all fail")
    for entry in manifest["invalid"]:
        document = json.loads((FIXTURES / entry["file"]).read_text(encoding="utf-8"))
        if validators[entry["schema"]].is_valid(document):
            failures.append(entry["file"])
            print(f"{RED}FAIL{RESET}  {entry['file']}")
            print(f"        should break rule {entry['rule']} and did not.")
            print(f"        {entry['why']}")
        else:
            print(f"{GREEN}ok{RESET}    {entry['file']}  {DIM}rule {entry['rule']}{RESET}")

    print()
    if failures:
        print(f"{RED}{len(failures)} fixture(s) behaved wrongly.{RESET}")
        print("Either a schema stopped enforcing a rule, or a fixture drifted.")
        print("Regenerate with: python schema/fixtures/build_fixtures.py")
        return 1

    total = len(manifest["valid"]) + len(manifest["invalid"])
    print(f"{GREEN}All {total} fixtures behaved as recorded.{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
