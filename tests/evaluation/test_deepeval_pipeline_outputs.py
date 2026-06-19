import json
import os
from pathlib import Path

os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")

from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase, SingleTurnParams

from tests.conftest import SAMPLE_IR, SUMMARY_PATH, run_pipeline


class PipelineSummaryContractMetric(BaseMetric):
    _required_params = [SingleTurnParams.ACTUAL_OUTPUT]

    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""

    def measure(self, test_case: LLMTestCase) -> float:
        payload = json.loads(test_case.actual_output)
        feature_files = payload.get("feature_files", [])
        summary = payload.get("summary", {})

        checks = {
            "summary_keys_present": all(
                key in payload for key in ("timestamp", "feature_files", "summary")
            ),
            "counts_match": summary.get("total_files") == len(feature_files),
            "successful_count_matches": summary.get("successful_features")
            == sum(1 for item in feature_files if item.get("status") == "success"),
            "failed_count_matches": summary.get("failed_features")
            == sum(1 for item in feature_files if item.get("status") == "failed"),
            "traceability_present": all(
                {"file", "status", "ir_path", "suite_path"}.issubset(item)
                for item in feature_files
            ),
        }

        self.score = 1.0 if all(checks.values()) else 0.0
        self.success = self.score >= self.threshold
        self.reason = (
            "Pipeline summary contract satisfied."
            if self.success
            else f"Pipeline contract checks failed: {checks}"
        )
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success


class IRContractMetric(BaseMetric):
    _required_params = [SingleTurnParams.ACTUAL_OUTPUT]

    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""

    def measure(self, test_case: LLMTestCase) -> float:
        payload = json.loads(test_case.actual_output)
        feature = payload.get("feature", {})
        scenarios = feature.get("scenarios", [])
        all_steps = [step for scenario in scenarios for step in scenario.get("steps", [])]
        unresolved_steps = [
            step
            for step in all_steps
            if step.get("resolution", {}).get("status") == "NEEDS_GENERATION"
        ]

        checks = {
            "source_file_present": payload.get("source_file") == "bdd/features/sample.feature",
            "feature_name_present": feature.get("name") == "User Login",
            "scenario_count_correct": len(scenarios) == 2,
            "parse_errors_empty": payload.get("parse_errors") == [],
            "unresolved_count_matches": payload.get("unresolved_count") == len(unresolved_steps),
        }

        self.score = 1.0 if all(checks.values()) else 0.0
        self.success = self.score >= self.threshold
        self.reason = (
            "IR contract satisfied."
            if self.success
            else f"IR contract checks failed: {checks}"
        )
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success


def test_deepeval_summary_contract_on_pipeline_output(sample_feature: Path):
    result = run_pipeline("--dry-run", str(sample_feature))
    assert result.returncode == 0, result.stderr

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    test_case = LLMTestCase(
        input="Validate the pipeline run summary JSON output.",
        actual_output=json.dumps(summary, sort_keys=True),
    )

    assert_test(
        test_case,
        [PipelineSummaryContractMetric()],
        run_async=False,
    )


def test_deepeval_ir_contract_on_pipeline_output():
    ir = json.loads(SAMPLE_IR.read_text(encoding="utf-8"))
    test_case = LLMTestCase(
        input="Validate the generated BDD IR JSON output.",
        actual_output=json.dumps(ir, sort_keys=True),
    )

    assert_test(
        test_case,
        [IRContractMetric()],
        run_async=False,
    )
