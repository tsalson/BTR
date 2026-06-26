#!/usr/bin/env python3
"""
BDD → Robot Framework Pipeline Orchestrator

Usage:
    python pipeline/run_pipeline.py bdd/features/login.feature
    python pipeline/run_pipeline.py --all
    python pipeline/run_pipeline.py --from-file feature_list.txt
    python pipeline/run_pipeline.py --dry-run bdd/features/login.feature
    python pipeline/run_pipeline.py --stage ir|suite|validate [FILES]
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
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.bdd_features_dir = project_root / "bdd" / "features"
        self.bdd_ir_dir = project_root / "bdd" / "ir"
        self.pipeline_dir = project_root / "pipeline"
        self.prompts_dir = self.pipeline_dir / "prompts"
        self.robot_suites_dir = project_root / "robot" / "suites"
        self.robot_resources_dir = project_root / "robot" / "resources" / "keywords"

        for d in [self.bdd_ir_dir, self.robot_suites_dir, self.robot_resources_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.summary: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feature_files": [],
            "summary": {
                "total_files": 0,
                "successful_features": 0,
                "failed_features": 0,
                "total_unresolved_keywords": 0,
                "all_robocop_clean": True,
            },
        }

    def _rel(self, path: Path) -> str:
        return str(path.relative_to(self.project_root))

    # ── Validation helpers ────────────────────────────────────────────────────

    def _validate_paths(self, paths: List[str], prefix: str, suffixes: set) -> List[Path]:
        seen, validated = set(), []
        for raw in paths:
            path = Path(raw).resolve()
            key = str(path)
            if key in seen:
                print(f"Skipping duplicate: {raw}", file=sys.stderr)
                continue
            seen.add(key)

            rel = self._rel(path) if path.is_relative_to(self.project_root) else ""
            if not rel.startswith(prefix):
                print(f"Must be under {prefix}: {raw}", file=sys.stderr)
            elif path.suffix not in suffixes:
                print(f"Expected {suffixes}, got {path.suffix}: {raw}", file=sys.stderr)
            elif not path.exists():
                print(f"Not found: {raw}", file=sys.stderr)
            else:
                print(f"OK: {raw}")
                validated.append(path)
        return validated

    def validate_feature_files(self, paths: List[str]) -> List[Path]:
        return self._validate_paths(paths, "bdd/features/", {".feature"})

    def validate_ir_files(self, paths: List[str]) -> List[Path]:
        return self._validate_paths(paths, "bdd/ir/", {".json"})

    def validate_suite_files(self, paths: List[str]) -> List[Path]:
        return self._validate_paths(paths, "robot/", {".robot", ".resource"})

    # ── Discovery ─────────────────────────────────────────────────────────────

    def get_all_feature_files(self) -> List[Path]:
        if not self.bdd_features_dir.exists():
            print(f"Not found: {self.bdd_features_dir}", file=sys.stderr)
            return []
        files = sorted(self.bdd_features_dir.glob("*.feature"))
        print(f"Found {len(files)} feature file(s) in {self.bdd_features_dir}")
        return files

    def load_feature_list_from_file(self, list_file: str) -> List[str]:
        path = Path(list_file)
        if not path.exists():
            print(f"Not found: {list_file}", file=sys.stderr)
            return []
        return [l.strip() for l in path.read_text().splitlines()
                if l.strip() and not l.startswith("#")]

    # ── Prompt building ───────────────────────────────────────────────────────

    PROMPT_FILES = {
        "bdd-ir-builder": "build_bdd_ir_task.md",
        "suite-builder": "build_suite_task.md",
        "robocop-validator": "validate_suite_task.md",
    }

    def _build_prompt(self, agent: str, **kwargs) -> str:
        tmpl = (self.prompts_dir / self.PROMPT_FILES[agent]).read_text()
        for key, val in kwargs.items():
            tmpl = tmpl.replace(f"{{{key.upper()}}}", str(val))
        return tmpl

    def _prompt_for(self, agent: str, **kwargs) -> str:
        if agent == "bdd-ir-builder":
            return self._build_prompt(agent, feature_file=kwargs["feature_file"])
        if agent == "suite-builder":
            ir_file = kwargs["ir_file"]
            return self._build_prompt(agent, ir_file=ir_file,
                                      feature_name=ir_file.stem.replace("-ir", ""))
        if agent == "robocop-validator":
            files_str = "\n".join(str(p) for p in kwargs.get("file_paths", []))
            return self._build_prompt(agent, file_paths=files_str)
        raise ValueError(f"Unknown agent: {agent}")

    # ── Agent invocation ──────────────────────────────────────────────────────

    def invoke_agent(self, agent: str, dry_run: bool = False, **kwargs) -> bool:
        print(f"\n{'='*50}\n Agent: {agent}\n{'='*50}")
        prompt = self._prompt_for(agent, **kwargs)

        if dry_run:
            print(f"[DRY RUN] Prompt:\n{prompt}")
            return True

        kilo = shutil.which("kilo")
        if not kilo:
            print(prompt)
            print("\n[NOTE] kilo CLI not found. Run manually or use --dry-run.")
            return False

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as tf:
            tf.write(prompt)
            tf_path = tf.name

        try:
            cmd = [kilo, "run", "--agent", agent, "-f", tf_path, "--auto", "run"] 
            print(f"> {' '.join(cmd)}\n")
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
                for line in proc.stdout or []:
                    print(line, end="")
                ret = proc.wait()
            if ret != 0:
                print(f"kilo exited {ret}", file=sys.stderr)
                return False
        finally:
            os.unlink(tf_path)

        return True

    # ── Result recording ──────────────────────────────────────────────────────

    def _record(self, feature_file: Path, feature_name: str, status: str,
                ir_path=None, suite_path=None, resource_path=None,
                unresolved=0, robocop_clean=False, errors=None):
        self.summary["feature_files"].append({
            "file": self._rel(feature_file),
            "feature_name": feature_name,
            "ir_path": self._rel(ir_path) if ir_path else None,
            "suite_path": self._rel(suite_path) if suite_path else None,
            "resource_path": self._rel(resource_path) if resource_path else None,
            "status": status,
            "unresolved_count": unresolved,
            "robocop_clean": robocop_clean,
            "errors": errors or [],
        })
        s = self.summary["summary"]
        if status == "success":
            s["successful_features"] += 1
            s["total_unresolved_keywords"] += unresolved
            if not robocop_clean:
                s["all_robocop_clean"] = False
        else:
            s["failed_features"] += 1
            s["all_robocop_clean"] = False

    # ── Per-file pipeline ─────────────────────────────────────────────────────

    def process_feature_file(self, feature_file: Path, dry_run: bool = False) -> bool:
        print(f"\n {self._rel(feature_file)}")
        stem = feature_file.stem
        ir_file = self.bdd_ir_dir / f"{stem}-ir.json"
        suite_file = self.robot_suites_dir / f"{stem}_suite.robot"
        resource_file = self.robot_resources_dir / "generated" / f"{stem}_keywords.resource"

        def fail(msg, **kw):
            self._record(feature_file, kw.pop("feature_name", stem), "failed", errors=[msg], **kw)
            return False

        # Stage 1: IR
        if not self.invoke_agent("bdd-ir-builder", dry_run, feature_file=feature_file):
            return fail("bdd-ir-builder failed")

        if dry_run:
            feature_name, unresolved = stem, 0
        else:
            if not ir_file.exists():
                return fail("IR file not generated")
            try:
                ir_data = json.loads(ir_file.read_text())
                feature_name = ir_data.get("feature", {}).get("name", stem)
                unresolved = ir_data.get("unresolved_count", 0)
            except Exception as e:
                return fail(f"Failed to read IR: {e}", ir_path=ir_file)

        # Stage 2: Suite
        if not self.invoke_agent("suite-builder", dry_run, ir_file=ir_file):
            return fail("suite-builder failed", feature_name=feature_name, ir_path=ir_file)

        if not dry_run:
            if not suite_file.exists():
                return fail("Suite file not generated", feature_name=feature_name, ir_path=ir_file)

            # Stage 3: Validate
            val_files = [suite_file] + ([resource_file] if resource_file.exists() else [])
            if not self.invoke_agent("robocop-validator", dry_run, file_paths=val_files):
                return fail("Robocop validation failed", feature_name=feature_name,
                            ir_path=ir_file, suite_path=suite_file,
                            resource_path=resource_file if resource_file.exists() else None,
                            unresolved=unresolved)

        self._record(feature_file, feature_name, "success",
                     ir_path=ir_file, suite_path=suite_file,
                     resource_path=resource_file if unresolved else None,
                     unresolved=unresolved, robocop_clean=True)
        print(f"OK: {stem}")
        return True

    # ── Full run ──────────────────────────────────────────────────────────────

    def run(self, feature_files: List[Path], dry_run: bool = False) -> bool:
        print(f"\n{'='*50}\n BTR Pipeline — {len(feature_files)} file(s)\n{'='*50}")
        if not feature_files:
            print("No feature files to process", file=sys.stderr)
            return False

        if dry_run:
            print("DRY RUN — no agents will be executed")

        self.summary["summary"]["total_files"] = len(feature_files)
        for f in feature_files:
            self.process_feature_file(f, dry_run)

        summary_file = self.pipeline_dir / "run_summary.json"
        summary_file.write_text(json.dumps(self.summary, indent=2))

        s = self.summary["summary"]
        print(f"\n{'='*50}\n Summary\n{'='*50}")
        print(f"Total: {s['total_files']}  OK: {s['successful_features']}  KO: {s['failed_features']}")
        print(f"Unresolved keywords: {s['total_unresolved_keywords']}")
        print(f"Robocop clean: {s['all_robocop_clean']}")
        print(f"Report: {self._rel(summary_file)}")

        return s["failed_features"] == 0


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BDD → Robot Framework pipeline")
    parser.add_argument("feature_files", nargs="*")
    parser.add_argument("--all", action="store_true", help="Process all features")
    parser.add_argument("--from-file", metavar="FILE")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage", choices=["full", "ir", "suite", "validate"], default="full")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent)
    args = parser.parse_args()

    orch = PipelineOrchestrator(args.project_root)
    positional = args.feature_files

    if args.stage == "ir":
        files = orch.validate_feature_files(positional)
        if not files:
            return 1
        ok = all(orch.invoke_agent("bdd-ir-builder", args.dry_run, feature_file=f) for f in files)
        return 0 if ok else 1

    if args.stage == "suite":
        ir_files = orch.validate_ir_files(positional)
        if not ir_files:
            return 1
        ok = all(orch.invoke_agent("suite-builder", args.dry_run, ir_file=ir) for ir in ir_files)
        return 0 if ok else 1

    if args.stage == "validate":
        suite_files = orch.validate_suite_files(positional)
        if not suite_files:
            return 1
        ok = orch.invoke_agent("robocop-validator", args.dry_run, file_paths=suite_files)
        return 0 if ok else 1

    # full pipeline
    if args.all:
        files = orch.get_all_feature_files()
    elif args.from_file:
        files = orch.validate_feature_files(orch.load_feature_list_from_file(args.from_file))
    elif positional:
        files = orch.validate_feature_files(positional)
    else:
        parser.print_help()
        return 1

    return 0 if orch.run(files, args.dry_run) else 1


if __name__ == "__main__":
    sys.exit(main())