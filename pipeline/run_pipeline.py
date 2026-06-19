#!/usr/bin/env python3
"""
BDD → Robot Framework Pipeline Orchestrator

Coordinates the transformation of Gherkin feature files into Robot Framework test suites
using a chain of specialized agents via Kilo Code.

Usage:
    python pipeline/run_pipeline.py [OPTIONS] [FEATURE_FILES]

Examples:
    # Process a single feature file
    python pipeline/run_pipeline.py bdd/features/login.feature

    # Process multiple feature files
    python pipeline/run_pipeline.py bdd/features/login.feature bdd/features/checkout.feature

    # Process all feature files in a directory
    python pipeline/run_pipeline.py --all

    # Process from a file list
    python pipeline/run_pipeline.py --from-file feature_list.txt

    # Dry run (validate without executing)
    python pipeline/run_pipeline.py --dry-run bdd/features/login.feature
"""

import argparse
import json
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


class PipelineOrchestrator:
    """Manages the BDD → RF pipeline execution."""

    def __init__(self, project_root: Path):
        """Initialize the orchestrator with project paths."""
        self.project_root = project_root
        self.bdd_features_dir = project_root / "bdd" / "features"
        self.bdd_ir_dir = project_root / "bdd" / "ir"
        self.pipeline_dir = project_root / "pipeline"
        self.prompts_dir = self.pipeline_dir / "prompts"
        self.schemas_dir = self.pipeline_dir / "schemas"
        self.robot_suites_dir = project_root / "robot" / "suites"
        self.robot_resources_dir = project_root / "robot" / "resources" / "keywords"
        self.robocop_report = self.pipeline_dir / "robocop_report.json"
        self.kilo_config = project_root / ".kilo" / "kilo.jsonc"

        # Create output directories
        self.bdd_ir_dir.mkdir(parents=True, exist_ok=True)
        self.robot_suites_dir.mkdir(parents=True, exist_ok=True)
        self.robot_resources_dir.mkdir(parents=True, exist_ok=True)

        self.run_summary: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feature_files": [],
            "summary": {
                "total_files": 0,
                "successful_features": 0,
                "failed_features": 0,
                "total_unresolved_keywords": 0,
                "all_robocop_clean": True,
            }
        }

    def validate_ir_files(self, file_paths: List[str]) -> List[Path]:
        """Validate and normalize IR file paths."""
        validated = []
        duplicates_seen = set()

        for file_path in file_paths:
            path = Path(file_path).resolve()
            if str(path) in duplicates_seen:
                print(f"⚠️  Skipping duplicate: {file_path}", file=sys.stderr)
                continue
            duplicates_seen.add(str(path))

            if not str(path.relative_to(self.project_root)).startswith("bdd/ir/"):
                print(f"❌ Invalid path pattern: {file_path}", file=sys.stderr)
                print(f"   Must be in bdd/ir/ directory", file=sys.stderr)
                continue

            if not path.suffix == ".json":
                print(f"❌ Invalid file extension: {file_path}", file=sys.stderr)
                print(f"   Must be a .json file", file=sys.stderr)
                continue

            if not path.exists():
                print(f"❌ File not found: {file_path}", file=sys.stderr)
                continue

            validated.append(path)
            print(f"✓ Validated: {file_path}")

        return validated

    def validate_suite_files(self, file_paths: List[str]) -> List[Path]:
        """Validate and normalize generated suite/resource file paths."""
        validated = []
        duplicates_seen = set()

        for file_path in file_paths:
            path = Path(file_path).resolve()
            if str(path) in duplicates_seen:
                print(f"⚠️  Skipping duplicate: {file_path}", file=sys.stderr)
                continue
            duplicates_seen.add(str(path))

            if not str(path.relative_to(self.project_root)).startswith("robot/"):
                print(f"❌ Invalid path pattern: {file_path}", file=sys.stderr)
                print(f"   Must be under robot/ directory", file=sys.stderr)
                continue

            if path.suffix not in {".robot", ".resource"}:
                print(f"❌ Invalid file extension: {file_path}", file=sys.stderr)
                print(f"   Must be a .robot or .resource file", file=sys.stderr)
                continue

            if not path.exists():
                print(f"❌ File not found: {file_path}", file=sys.stderr)
                continue

            validated.append(path)
            print(f"✓ Validated: {file_path}")

        return validated

    def validate_feature_files(self, feature_files: List[str]) -> List[Path]:
        """Validate and normalize feature file paths."""
        validated = []
        duplicates_seen = set()

        for file_path in feature_files:
            # Normalize path
            path = Path(file_path).resolve()

            # Check if path is duplicated
            if str(path) in duplicates_seen:
                print(f"⚠️  Skipping duplicate: {file_path}", file=sys.stderr)
                continue
            duplicates_seen.add(str(path))

            # Check path pattern
            if not str(path.relative_to(self.project_root)).startswith("bdd/features/"):
                print(f"❌ Invalid path pattern: {file_path}", file=sys.stderr)
                print(f"   Must be in bdd/features/ directory", file=sys.stderr)
                continue

            if not path.suffix == ".feature":
                print(f"❌ Invalid file extension: {file_path}", file=sys.stderr)
                print(f"   Must be a .feature file", file=sys.stderr)
                continue

            # Check existence
            if not path.exists():
                print(f"❌ File not found: {file_path}", file=sys.stderr)
                continue

            validated.append(path)
            print(f"✓ Validated: {file_path}")

        return validated

    def validate_ir_files(self, file_paths: List[str]) -> List[Path]:
        """Validate and normalize IR file paths."""
        validated = []
        duplicates_seen = set()

        for file_path in file_paths:
            path = Path(file_path).resolve()
            if str(path) in duplicates_seen:
                print(f"⚠️  Skipping duplicate: {file_path}", file=sys.stderr)
                continue
            duplicates_seen.add(str(path))

            if not str(path.relative_to(self.project_root)).startswith("bdd/ir/"):
                print(f"❌ Invalid IR path pattern: {file_path}", file=sys.stderr)
                print(f"   Must be in bdd/ir/ directory", file=sys.stderr)
                continue

            if path.suffix != ".json":
                print(f"❌ Invalid IR extension: {file_path}", file=sys.stderr)
                print(f"   Must be a .json file", file=sys.stderr)
                continue

            if not path.exists():
                print(f"❌ IR file not found: {file_path}", file=sys.stderr)
                continue

            validated.append(path)
            print(f"✓ Validated IR: {file_path}")

        return validated

    def validate_suite_files(self, file_paths: List[str]) -> List[Path]:
        """Validate suite/resource file paths for validation stage."""
        validated = []
        duplicates_seen = set()

        for file_path in file_paths:
            path = Path(file_path).resolve()
            if str(path) in duplicates_seen:
                print(f"⚠️  Skipping duplicate: {file_path}", file=sys.stderr)
                continue
            duplicates_seen.add(str(path))

            if not str(path.relative_to(self.project_root)).startswith("robot/"):
                print(f"❌ Invalid suite/resource path: {file_path}", file=sys.stderr)
                print(f"   Must be under robot/ directory", file=sys.stderr)
                continue

            if path.suffix not in {".robot", ".resource"}:
                print(f"❌ Invalid file extension: {file_path}", file=sys.stderr)
                print(f"   Must be a .robot or .resource file", file=sys.stderr)
                continue

            if not path.exists():
                print(f"❌ File not found: {file_path}", file=sys.stderr)
                continue

            validated.append(path)
            print(f"✓ Validated suite/resource: {file_path}")

        return validated

    def get_all_feature_files(self) -> List[Path]:
        """Get all .feature files in bdd/features/."""
        if not self.bdd_features_dir.exists():
            print(f"❌ Features directory not found: {self.bdd_features_dir}", file=sys.stderr)
            return []

        feature_files = sorted(self.bdd_features_dir.glob("*.feature"))
        print(f"Found {len(feature_files)} feature files in {self.bdd_features_dir}")
        return feature_files

    def load_feature_list_from_file(self, list_file: str) -> List[str]:
        """Load feature file list from a text file."""
        list_path = Path(list_file)
        if not list_path.exists():
            print(f"❌ List file not found: {list_file}", file=sys.stderr)
            return []

        with open(list_path, "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return lines

    def build_task_prompt(self, task_type: str, **kwargs) -> str:
        """Build a task prompt by loading template and substituting parameters."""
        if task_type == "bdd_ir_builder":
            prompt_file = self.prompts_dir / "build_bdd_ir_task.md"
            feature_file = kwargs.get("feature_file")
            with open(prompt_file, "r") as f:
                content = f.read()
            content = content.replace("{FEATURE_FILE}", str(feature_file))
            return content

        elif task_type == "suite_builder":
            prompt_file = self.prompts_dir / "build_suite_task.md"
            ir_file = kwargs.get("ir_file")
            with open(prompt_file, "r") as f:
                content = f.read()
            content = content.replace("{IR_FILE}", str(ir_file))
            # Extract feature name for resource/suite naming
            ir_name = ir_file.stem.replace("-ir", "")
            content = content.replace("{FEATURE_NAME}", ir_name)
            return content

        elif task_type == "robocop_validator":
            prompt_file = self.prompts_dir / "validate_suite_task.md"
            file_paths = kwargs.get("file_paths", [])
            with open(prompt_file, "r") as f:
                content = f.read()
            content = content.replace("{FILE_PATHS}", "\n".join(str(p) for p in file_paths))
            return content

        elif task_type == "orchestrator":
            prompt_file = self.prompts_dir / "orchestrator_task.md"
            feature_files = kwargs.get("feature_files", [])
            file_list_str = "\n".join(str(f) for f in feature_files)
            with open(prompt_file, "r") as f:
                content = f.read()
            content = content.replace("{FEATURE_FILES}", file_list_str)
            return content

        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def invoke_kilo_agent(
        self,
        agent_name: str,
        feature_file: Optional[Path] = None,
        ir_file: Optional[Path] = None,
        file_paths: Optional[List[Path]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Invoke a Kilo Code agent via CLI or API."""
        print(f"\n{'='*60}")
        print(f"🔄 Delegating to agent: {agent_name}")
        print(f"{'='*60}")

        if agent_name == "bdd-ir-builder":
            prompt = self.build_task_prompt("bdd_ir_builder", feature_file=feature_file)
            print(f"Feature file: {feature_file}")
        elif agent_name == "suite-builder":
            prompt = self.build_task_prompt("suite_builder", ir_file=ir_file)
            print(f"IR file: {ir_file}")
        elif agent_name == "robocop-validator":
            file_paths = file_paths or []
            prompt = self.build_task_prompt("robocop_validator", file_paths=file_paths)
            print("Files to validate:")
            for p in file_paths:
                print(f"  - {p}")
        else:
            print(f"❌ Unknown agent: {agent_name}", file=sys.stderr)
            return False

        if dry_run:
            print(f"\n[DRY RUN] Would execute agent: {agent_name}")
            print(f"Prompt:\n{prompt}\n")
            return True

        kilo_path = shutil.which("kilo")
        if kilo_path:
            # write prompt to a temporary file and call kilo run --agent <agent> -f <file> --auto
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as tf:
                tf.write(prompt)
                tf_path = tf.name

            # kilo requires a message positional; pass a short marker message at the end
            cmd = [kilo_path, "run", "--agent", agent_name, "-f", tf_path, "--auto", "run"]
            try:
                print(f"\n▶ Running: {' '.join(cmd)}\n")
                # Stream kilo output in real-time so the user sees progress
                with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True) as proc:
                    try:
                        if proc.stdout is not None:
                            for line in proc.stdout:
                                print(line, end='')
                    except KeyboardInterrupt:
                        proc.kill()
                        proc.wait()
                        raise
                    ret = proc.wait()
                    if ret != 0:
                        print(f"❌ kilo run returned {ret}", file=sys.stderr)
                        return False
            finally:
                try:
                    os.unlink(tf_path)
                except Exception:
                    pass

            return True

        # Fallback: print the prompt and instruct the user to run Kilo manually
        print(f"\n📋 Task Prompt:\n")
        print(prompt)
        print(f"\n[NOTE] Kilo CLI not found; please run the agent using the Kilo CLI or use --dry-run to preview.")
        return False

    def record_feature_result(
        self,
        feature_file: Path,
        feature_name: str,
        status: str,
        ir_path: Optional[Path] = None,
        suite_path: Optional[Path] = None,
        resource_path: Optional[Path] = None,
        unresolved_count: int = 0,
        robocop_clean: bool = False,
        errors: Optional[List[str]] = None,
    ) -> None:
        """Record results for a processed feature file."""
        result = {
            "file": str(feature_file.relative_to(self.project_root)),
            "feature_name": feature_name,
            "ir_path": str(ir_path.relative_to(self.project_root)) if ir_path else None,
            "suite_path": str(suite_path.relative_to(self.project_root)) if suite_path else None,
            "resource_path": str(resource_path.relative_to(self.project_root)) if resource_path else None,
            "status": status,
            "unresolved_count": unresolved_count,
            "robocop_clean": robocop_clean,
            "errors": errors or [],
        }
        self.run_summary["feature_files"].append(result)

        # Update summary statistics
        if status == "success":
            self.run_summary["summary"]["successful_features"] += 1
            self.run_summary["summary"]["total_unresolved_keywords"] += unresolved_count
            if not robocop_clean:
                self.run_summary["summary"]["all_robocop_clean"] = False
        elif status == "failed":
            self.run_summary["summary"]["failed_features"] += 1
            self.run_summary["summary"]["all_robocop_clean"] = False

    def process_feature_file(
        self,
        feature_file: Path,
        dry_run: bool = False,
    ) -> bool:
        """Process a single feature file through the pipeline."""
        print(f"\n📄 Processing: {feature_file.relative_to(self.project_root)}")

        # Derive IR file path
        ir_name = feature_file.stem
        ir_file = self.bdd_ir_dir / f"{ir_name}-ir.json"
        suite_file = self.robot_suites_dir / f"{ir_name}_suite.robot"
        resource_file = self.robot_resources_dir / "generated" / f"{ir_name}_keywords.resource"

        # Step 1: Invoke bdd-ir-builder
        if not self.invoke_kilo_agent("bdd-ir-builder", feature_file=feature_file, dry_run=dry_run):
            self.record_feature_result(
                feature_file=feature_file,
                feature_name=feature_file.stem,
                status="failed",
                errors=["Failed to invoke bdd-ir-builder agent"],
            )
            return False

        # In real execution, check if IR file was created
        if not dry_run:
            if not ir_file.exists():
                self.record_feature_result(
                    feature_file=feature_file,
                    feature_name=feature_file.stem,
                    status="failed",
                    errors=["IR file not generated by bdd-ir-builder"],
                )
                return False

            # Read IR to get metadata
            try:
                with open(ir_file, "r") as f:
                    ir_data = json.load(f)
                feature_name = ir_data.get("feature", {}).get("name", feature_file.stem)
                unresolved_count = ir_data.get("unresolved_count", 0)
                parse_errors = ir_data.get("parse_errors", [])
            except Exception as e:
                self.record_feature_result(
                    feature_file=feature_file,
                    feature_name=feature_file.stem,
                    status="failed",
                    ir_path=ir_file,
                    errors=[f"Failed to read IR: {str(e)}"],
                )
                return False
        else:
            feature_name = feature_file.stem
            unresolved_count = 0

        # Step 2: Invoke suite-builder
        if not self.invoke_kilo_agent("suite-builder", ir_file=ir_file, dry_run=dry_run):
            self.record_feature_result(
                feature_file=feature_file,
                feature_name=feature_name,
                status="failed",
                ir_path=ir_file,
                errors=["Failed to invoke suite-builder agent"],
            )
            return False

        # In real execution, check if suite file was created
        if not dry_run:
            if not suite_file.exists():
                self.record_feature_result(
                    feature_file=feature_file,
                    feature_name=feature_name,
                    status="failed",
                    ir_path=ir_file,
                    errors=["Suite file not generated by suite-builder"],
                )
                return False

            # Step 3: Validate generated artefacts with Robocop
            validation_files = [suite_file]
            if resource_file.exists():
                validation_files.append(resource_file)

            if not self.invoke_kilo_agent(
                "robocop-validator",
                file_paths=validation_files,
                dry_run=dry_run,
            ):
                self.record_feature_result(
                    feature_file=feature_file,
                    feature_name=feature_name,
                    status="failed",
                    ir_path=ir_file,
                    suite_path=suite_file,
                    resource_path=resource_file if resource_file.exists() else None,
                    unresolved_count=unresolved_count,
                    robocop_clean=False,
                    errors=["Robocop validation failed for generated artefacts"],
                )
                return False

        # Record success
        self.record_feature_result(
            feature_file=feature_file,
            feature_name=feature_name,
            status="success",
            ir_path=ir_file,
            suite_path=suite_file,
            resource_path=resource_file if unresolved_count > 0 else None,
            unresolved_count=unresolved_count,
            robocop_clean=True,  # Assumed clean if suite-builder succeeded
        )

        print(f"✅ Successfully processed: {feature_file.stem}")
        return True

    def run(
        self,
        feature_files: List[Path],
        dry_run: bool = False,
    ) -> bool:
        """Execute the pipeline on the given feature files."""
        print(f"\n{'='*60}")
        print(f"🚀 BTR Pipeline Orchestrator")
        print(f"{'='*60}")

        if not feature_files:
            print("❌ No feature files to process", file=sys.stderr)
            return False

        self.run_summary["summary"]["total_files"] = len(feature_files)
        print(f"\n📋 Processing {len(feature_files)} feature file(s)...")
        for f in feature_files:
            print(f"   • {f.relative_to(self.project_root)}")

        if dry_run:
            print("\n🔍 [DRY RUN MODE] - No actual execution will occur")

        # Process each feature file
        for feature_file in feature_files:
            self.process_feature_file(feature_file, dry_run=dry_run)

        # Write summary
        summary_file = self.pipeline_dir / "run_summary.json"
        with open(summary_file, "w") as f:
            json.dump(self.run_summary, f, indent=2)

        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 Pipeline Summary")
        print(f"{'='*60}")
        print(f"Total files: {self.run_summary['summary']['total_files']}")
        print(f"Successful: {self.run_summary['summary']['successful_features']}")
        print(f"Failed: {self.run_summary['summary']['failed_features']}")
        print(f"Unresolved keywords: {self.run_summary['summary']['total_unresolved_keywords']}")
        print(f"All Robocop clean: {self.run_summary['summary']['all_robocop_clean']}")
        print(f"\n📄 Summary written to: {summary_file.relative_to(self.project_root)}")

        return self.run_summary["summary"]["failed_features"] == 0


def main():
    parser = argparse.ArgumentParser(
        description="BTR Pipeline: Transform BDD features into Robot Framework test suites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Input source options
    parser.add_argument(
        "feature_files",
        nargs="*",
        help="One or more .feature file paths (e.g., bdd/features/login.feature)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all .feature files in bdd/features/"
    )
    parser.add_argument(
        "--from-file",
        metavar="FILE",
        help="Load feature file paths from a text file (one per line)"
    )

    # Execution options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and preview without executing agents"
    )
    parser.add_argument(
        "--stage",
        choices=["full", "ir", "suite", "validate"],
        default="full",
        help="Which pipeline stage to run (default: full)"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory (default: parent of pipeline/)"
    )

    args = parser.parse_args()

    # Determine feature files to process
    orchestrator = PipelineOrchestrator(args.project_root)
    files_to_process = []

    if args.all:
        files_to_process = orchestrator.get_all_feature_files()
    elif args.from_file:
        file_list = orchestrator.load_feature_list_from_file(args.from_file)
        files_to_process = orchestrator.validate_feature_files(file_list)
    elif args.feature_files:
        files_to_process = orchestrator.validate_feature_files(args.feature_files)
    else:
        parser.print_help()
        return 1

    # Stage runner
    stage = args.stage
    if stage == "ir":
        if not files_to_process:
            print("❌ No feature files provided for IR generation", file=sys.stderr)
            return 1
        ok = True
        for f in files_to_process:
            if not orchestrator.invoke_kilo_agent("bdd-ir-builder", feature_file=f, dry_run=args.dry_run):
                ok = False
        return 0 if ok else 1

    if stage == "suite":
        # Treat positional arguments as IR files (user must pass bdd/ir/*.json paths)
        ir_paths = [str(p) for p in args.feature_files] if args.feature_files else []
        ir_valid = orchestrator.validate_ir_files(ir_paths)
        if not ir_valid:
            print("❌ No valid IR files provided for suite generation", file=sys.stderr)
            return 1
        ok = True
        for ir in ir_valid:
            if not orchestrator.invoke_kilo_agent("suite-builder", ir_file=ir, dry_run=args.dry_run):
                ok = False
        return 0 if ok else 1

    if stage == "validate":
        # Treat positional args as suite/resource files to validate
        suite_paths = [str(p) for p in args.feature_files] if args.feature_files else []
        validated = orchestrator.validate_suite_files(suite_paths)
        if not validated:
            print("❌ No valid suite/resource files provided for validation", file=sys.stderr)
            return 1
        # invoke robocop-validator
        ok = orchestrator.invoke_kilo_agent("robocop-validator", file_paths=validated, dry_run=args.dry_run)
        return 0 if ok else 1

    # Run full pipeline
    success = orchestrator.run(files_to_process, dry_run=args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
