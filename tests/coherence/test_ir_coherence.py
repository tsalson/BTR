import json
from pathlib import Path

from tests.conftest import SAMPLE_IR


def test_sample_ir_is_coherent_with_feature_and_steps():
    ir = json.loads(SAMPLE_IR.read_text(encoding="utf-8"))

    assert ir["source_file"] == "bdd/features/sample.feature"
    assert ir["feature"]["name"] == "User Login"
    assert len(ir["feature"]["scenarios"]) == 2

    all_steps = []
    for scenario in ir["feature"]["scenarios"]:
        all_steps.extend(scenario["steps"])

    unresolved_steps = [
        step for step in all_steps if step.get("resolution", {}).get("status") == "NEEDS_GENERATION"
    ]

    assert ir["unresolved_count"] == len(unresolved_steps)
    assert ir["unresolved_count"] == 11
    assert ir["parse_errors"] == []