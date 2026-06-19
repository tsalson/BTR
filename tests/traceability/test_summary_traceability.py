import json

from tests.conftest import SUMMARY_PATH


def test_summary_contains_traceable_file_paths():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    assert "feature_files" in summary
    assert "summary" in summary

    feature_entry = summary["feature_files"][0]
    assert feature_entry["file"] == "bdd/features/sample.feature"
    assert feature_entry["status"] == "success"
    assert feature_entry["feature_name"] == "sample"
    assert feature_entry["ir_path"] == "bdd/ir/sample-ir.json"
    assert feature_entry["suite_path"] == "robot/suites/sample_suite.robot"
    assert feature_entry["resource_path"] is None
    assert feature_entry["unresolved_count"] == 0
