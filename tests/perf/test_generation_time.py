import time

from tests.conftest import run_pipeline


def test_dry_run_pipeline_completes_within_threshold(sample_feature):
    start = time.perf_counter()
    result = run_pipeline("--dry-run", str(sample_feature))
    elapsed = time.perf_counter() - start

    assert result.returncode == 0, result.stderr
    assert elapsed < 5.0, f"Pipeline dry-run took too long: {elapsed:.3f}s"
