import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "simulation/timeline_emitter/run_replay.py"
FIXTURES = ROOT / "simulation/fixtures"


def run_replay(*args, cwd=ROOT):
    return subprocess.run(
        [sys.executable, str(RUNNER), *map(str, args)],
        cwd=cwd, text=True, capture_output=True, timeout=30,
    )


@pytest.mark.parametrize("fixture,allocated,unallocated", [
    ("mock_data.json", 2, 0),
    ("capacity_shortage.json", 1, 1),
    ("platform_mismatch.json", 0, 1),
])
def test_selectable_scenarios_have_expected_counts(fixture, allocated, unallocated):
    result = run_replay("--fixture", FIXTURES / fixture)
    assert result.returncode == 0, result.stderr
    assert f"Allocation summary: {allocated} allocated, {unallocated} unallocated." in result.stdout
    assert result.stdout.count("-> ActionState.ACCEPTED") == allocated
    assert "placeholder" in result.stdout
    assert ("CONFLICT DETECTED" in result.stdout) is bool(unallocated)


def test_default_fixture_is_independent_of_working_directory(tmp_path):
    result = run_replay(cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Allocation summary: 2 allocated, 0 unallocated." in result.stdout


def test_as_of_override_can_expire_all_slots():
    result = run_replay("--as-of", "2030-01-01T00:00:00Z")
    assert result.returncode == 0, result.stderr
    assert "Allocation summary: 0 allocated, 2 unallocated." in result.stdout


def test_missing_fixture_reports_clear_error(tmp_path):
    result = run_replay("--fixture", tmp_path / "missing.json")
    assert result.returncode == 2
    assert "cannot load fixture" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("content", ["{", "[]", "{}", '{"candidates": {}, "slots": []}', '{"candidates": [], "slots": [], "evaluation_time": "bad"}'])
def test_malformed_fixture_reports_clear_error(tmp_path, content):
    path = tmp_path / "invalid.json"
    path.write_text(content, encoding="utf-8")
    result = run_replay("--fixture", path)
    assert result.returncode == 2
    assert "cannot load fixture" in result.stderr
    assert "Traceback" not in result.stderr


def test_model_validation_failure_reports_field(tmp_path):
    data = json.loads((FIXTURES / "mock_data.json").read_text(encoding="utf-8"))
    data["candidates"][0]["target_dose_count"] = 0
    path = tmp_path / "invalid-model.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = run_replay("--fixture", path)
    assert result.returncode == 2
    assert "target_dose_count" in result.stderr
    assert "Traceback" not in result.stderr


def test_invalid_as_of_is_an_argument_error():
    result = run_replay("--as-of", "yesterday")
    assert result.returncode == 2
    assert "ISO 8601" in result.stderr
