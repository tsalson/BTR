from pathlib import Path

from pipeline.run_pipeline import PipelineOrchestrator


def test_validate_feature_files_accepts_expected_layout(tmp_path: Path):
    feature = tmp_path / "bdd" / "features" / "sample.feature"
    feature.parent.mkdir(parents=True)
    feature.write_text("Feature: Sample\n", encoding="utf-8")

    orchestrator = PipelineOrchestrator(tmp_path)
    validated = orchestrator.validate_feature_files([str(feature)])

    assert len(validated) == 1
    assert validated[0] == feature.resolve()


def test_validate_ir_files_rejects_non_json_path(tmp_path: Path):
    invalid = tmp_path / "bdd" / "ir" / "sample.txt"
    invalid.parent.mkdir(parents=True)
    invalid.write_text("not json", encoding="utf-8")

    orchestrator = PipelineOrchestrator(tmp_path)
    validated = orchestrator.validate_ir_files([str(invalid)])

    assert validated == []


def test_validate_suite_files_accepts_robot_and_resource_paths(tmp_path: Path):
    robot_file = tmp_path / "robot" / "suites" / "sample_suite.robot"
    resource_file = tmp_path / "robot" / "resources" / "keywords" / "generated" / "sample.resource"
    robot_file.parent.mkdir(parents=True)
    resource_file.parent.mkdir(parents=True)
    robot_file.write_text("*** Test Cases ***\n", encoding="utf-8")
    resource_file.write_text("*** Keywords ***\n", encoding="utf-8")

    orchestrator = PipelineOrchestrator(tmp_path)
    validated = orchestrator.validate_suite_files(
        [str(robot_file), str(resource_file)]
    )

    assert len(validated) == 2
    assert robot_file.resolve() in validated
    assert resource_file.resolve() in validated
