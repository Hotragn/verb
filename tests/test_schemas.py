"""The JSON Schemas, and every fixture.

Every file under schema/fixtures/valid must validate. Every file under
schema/fixtures/invalid must fail, for the reason recorded in manifest.json.
The manifest ties each invalid fixture to the rule it breaks, so a fixture that
starts passing points at a specific rule that stopped being enforced.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema", reason="jsonschema is a dev dependency")

from jsonschema import Draft202012Validator, FormatChecker  # noqa: E402

SCHEMAS = ("decision-artifact", "agent-contract")


@pytest.fixture(scope="module")
def validators(schema_dir):
    built = {}
    for name in SCHEMAS:
        schema = json.loads((schema_dir / f"{name}.schema.json").read_text(encoding="utf-8"))
        built[name] = Draft202012Validator(schema, format_checker=FormatChecker())
    return built


@pytest.fixture(scope="module")
def manifest(schema_dir):
    return json.loads((schema_dir / "fixtures" / "manifest.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The schemas themselves
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", SCHEMAS)
def test_schema_is_a_valid_draft_2020_12_schema(schema_dir, name):
    schema = json.loads((schema_dir / f"{name}.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("name", SCHEMAS)
def test_schema_declares_an_id_and_a_title(schema_dir, name):
    schema = json.loads((schema_dir / f"{name}.schema.json").read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["$id"].startswith("https://github.com/hotragn/verb/schema/")
    assert schema["title"].startswith("VERB")


def test_the_artifact_schema_requires_all_six_evidence_fields(schema_dir):
    schema = json.loads((schema_dir / "decision-artifact.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])
    for field in ("basis", "alternatives", "confidence_and_failure_mode", "reversal", "owner"):
        assert field in required
    # decision is conditionally required, because Class D preparation packs must not carry one.
    assert "decision" not in required
    assert any("class_d_preparation" in json.dumps(rule) for rule in schema["allOf"])


def test_the_contract_schema_forbids_class_d_in_scope(schema_dir):
    schema = json.loads((schema_dir / "agent-contract.schema.json").read_text(encoding="utf-8"))
    assert schema["$defs"]["decisionClassNonD"]["enum"] == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def test_the_manifest_covers_every_fixture_file(schema_dir, manifest):
    listed = {entry["file"] for entry in manifest["valid"] + manifest["invalid"]}
    on_disk = {
        f"{path.parent.name}/{path.name}"
        for path in (schema_dir / "fixtures").rglob("*.json")
        if path.parent.name in ("valid", "invalid")
    }
    assert listed == on_disk


def test_there_are_fixtures_for_both_schemas(manifest):
    schemas_used = {entry["schema"] for entry in manifest["valid"]}
    assert schemas_used == set(SCHEMAS)
    assert len(manifest["valid"]) >= 8
    assert len(manifest["invalid"]) >= 25


def _valid_cases(manifest_path: Path):
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [(e["file"], e["schema"]) for e in data["valid"]]


def _invalid_cases(manifest_path: Path):
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [(e["file"], e["schema"], e["rule"]) for e in data["invalid"]]


_MANIFEST = Path(__file__).resolve().parent.parent / "schema" / "fixtures" / "manifest.json"


@pytest.mark.parametrize("filename,schema_name", _valid_cases(_MANIFEST))
def test_valid_fixtures_validate(schema_dir, validators, filename, schema_name):
    document = json.loads((schema_dir / "fixtures" / filename).read_text(encoding="utf-8"))
    errors = sorted(validators[schema_name].iter_errors(document), key=lambda e: list(e.path))
    assert not errors, "\n".join(f"{list(e.path)}: {e.message}" for e in errors[:5])


@pytest.mark.parametrize("filename,schema_name,rule", _invalid_cases(_MANIFEST))
def test_invalid_fixtures_are_rejected(schema_dir, validators, filename, schema_name, rule):
    document = json.loads((schema_dir / "fixtures" / filename).read_text(encoding="utf-8"))
    assert not validators[schema_name].is_valid(document), (
        f"{filename} should fail rule {rule} and did not. "
        "Either the schema stopped enforcing that rule, or the fixture drifted."
    )


def test_every_invalid_fixture_records_why(manifest):
    for entry in manifest["invalid"]:
        assert entry["rule"], entry["file"]
        assert len(entry["why"]) > 30, entry["file"]


# ---------------------------------------------------------------------------
# Regeneration
# ---------------------------------------------------------------------------


def test_the_fixture_builder_is_reproducible(repo_root, schema_dir):
    before = {
        path: path.read_bytes()
        for path in sorted((schema_dir / "fixtures").rglob("*.json"))
    }
    result = subprocess.run(
        [sys.executable, str(schema_dir / "fixtures" / "build_fixtures.py")],
        capture_output=True,
        cwd=repo_root,
    )
    assert result.returncode == 0, result.stderr.decode()
    after = {
        path: path.read_bytes()
        for path in sorted((schema_dir / "fixtures").rglob("*.json"))
    }
    assert before == after


# ---------------------------------------------------------------------------
# The schemas agree with the structural validator in vb.gates
# ---------------------------------------------------------------------------


def test_structural_validator_agrees_with_the_schema_on_valid_artifacts(schema_dir, manifest):
    from vb.gates import validate_artifact_structure

    for entry in manifest["valid"]:
        if entry["schema"] != "decision-artifact":
            continue
        document = json.loads((schema_dir / "fixtures" / entry["file"]).read_text(encoding="utf-8"))
        assert validate_artifact_structure(document) == [], entry["file"]


def test_structural_validator_also_rejects_the_artifact_fixtures_it_covers(schema_dir, manifest):
    """The two checks are deliberately separate: one runs with no dependencies
    inside a decision pipeline, the other runs in CI. They must not disagree on
    the cases both can see."""
    from vb.gates import validate_artifact_structure

    # Cases the structural validator is not designed to catch: it does not check
    # string patterns for timestamps or the numeric range of confidence values
    # that the schema handles with format assertions.
    not_covered = {"invalid/artifact-basis-not-resolvable.json"}
    checked = 0
    for entry in manifest["invalid"]:
        if entry["schema"] != "decision-artifact" or entry["file"] in not_covered:
            continue
        document = json.loads((schema_dir / "fixtures" / entry["file"]).read_text(encoding="utf-8"))
        assert validate_artifact_structure(document), f"{entry['file']} ({entry['rule']})"
        checked += 1
    assert checked >= 10
