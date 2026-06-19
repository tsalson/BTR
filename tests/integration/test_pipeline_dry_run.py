import json
from pathlib import Path

from tests.conftest import SUMMARY_PATH, run_pipeline


def test_pipeline_dry_run_generates_summary(sample_feature: Path):
    result = run_pipeline("--dry-run", str(sample_feature))

    assert result.returncode == 0, result.stderr
    assert SUMMARY_PATH.exists()

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert summary["summary"]["total_files"] == 1
    assert summary["summary"]["successful_features"] == 1
    assert summary["summary"]["failed_features"] == 0
    assert summary["summary"]["all_robocop_clean"] is True
    assert summary["feature_files"][0]["file"] == "bdd/features/sample.feature"
