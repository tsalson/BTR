import json

from tests.conftest import SUMMARY_PATH, run_pipeline


def test_dry_run_summary_is_repeatable_for_same_input(sample_feature):
    first = run_pipeline("--dry-run", str(sample_feature))
    assert first.returncode == 0, first.stderr

    first_summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    first_summary_without_timestamp = {
        key: value
        for key, value in first_summary.items()
        if key != "timestamp"
    }

    second = run_pipeline("--dry-run", str(sample_feature))
    assert second.returncode == 0, second.stderr

    second_summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    second_summary_without_timestamp = {
        key: value
        for key, value in second_summary.items()
        if key != "timestamp"
    }

    assert first_summary_without_timestamp == second_summary_without_timestamp
