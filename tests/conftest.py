from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_PIPELINE = PROJECT_ROOT / "pipeline" / "run_pipeline.py"
SAMPLE_FEATURE = PROJECT_ROOT / "bdd" / "features" / "sample.feature"
SAMPLE_IR = PROJECT_ROOT / "bdd" / "ir" / "sample-ir.json"
SUMMARY_PATH = PROJECT_ROOT / "pipeline" / "run_summary.json"


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def sample_feature() -> Path:
    return SAMPLE_FEATURE


@pytest.fixture(scope="session")
def sample_ir() -> Path:
    return SAMPLE_IR


@pytest.fixture(scope="session")
def run_pipeline_cmd() -> list[str]:
    return [sys.executable, str(RUN_PIPELINE)]


def run_pipeline(*args: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(RUN_PIPELINE), *args]
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
