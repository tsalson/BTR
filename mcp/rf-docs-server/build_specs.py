#!/usr/bin/env python3
"""
build_specs.py

Offline snapshot builder for rf-docs-server.

Generates one JSON libspec per Robot Framework standard library (and,
optionally, per custom resource/library under robot/resources/) using RF's
own `libdoc` machinery. These JSON files are the "local snapshot of RF 7.x
documentation" the server loads at startup — no network access, no RF
installation required at *query* time, fully reproducible across runs
(idempotency rule in .kilo/rules/global.md).

Run this once after pinning/upgrading the Robot Framework version, and
re-run whenever robot/resources/ changes:

    python build_specs.py
    python build_specs.py --resources ../../robot/resources
    python build_specs.py --only BuiltIn Collections

Output: specs/<LibraryName>.json  (+ specs/_meta.json with RF version info)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from robot.libdocpkg import LibraryDocumentation
    from robot.version import VERSION as RF_VERSION
except ImportError:
    print(
        "robotframework is not installed in this environment. "
        "Install it (pip install robotframework) before running build_specs.py.",
        file=sys.stderr,
    )
    sys.exit(1)

# Standard libraries shipped with Robot Framework that are relevant for
# keyword lookup. Dialogs/Telnet/Screenshot are included for completeness
# but rarely used; trim with --only if you want a smaller snapshot.
DEFAULT_STD_LIBS = [
    "BuiltIn",
    "Collections",
    "String",
    "OperatingSystem",
    "DateTime",
    "Process",
    "XML",
    "Screenshot",
    "Dialogs",
]

SPECS_DIR = Path(__file__).parent / "specs"


def _type_to_str(type_info) -> str | None:
    """Collapse libdoc's nested type-info dict down to a display string."""
    if not type_info:
        return None
    return type_info.get("typedoc") or type_info.get("name")


def keyword_to_record(kw) -> dict:
    """Flatten a robot.libdocpkg keyword object into the shape the server indexes."""
    d = kw.to_dictionary()
    args = []
    for a in d.get("args", []):
        args.append(
            {
                "name": a.get("name"),
                "type": _type_to_str(a.get("type")),
                "default": a.get("defaultValue"),
                "required": a.get("required", True),
                "kind": a.get("kind"),
                "repr": a.get("repr"),
            }
        )
    return {
        "name": kw.name,
        "args": args,
        "arg_repr": ", ".join(a["repr"] for a in args if a.get("repr")),
        "doc": kw.doc or "",
        "short_doc": kw.short_doc or "",
        "tags": list(kw.tags) if kw.tags else [],
        "deprecated": bool(getattr(kw, "deprecated", False)),
        "source": str(kw.source) if kw.source else None,
        "lineno": kw.lineno,
    }


def build_one(target: str, kind: str) -> dict:
    """
    target: library name (e.g. 'BuiltIn') or filesystem path to a .resource/.robot/.py
    kind: 'stdlib' | 'resource'
    """
    libdoc = LibraryDocumentation(target)
    spec = {
        "name": libdoc.name,
        "kind": kind,
        "version": libdoc.version or None,
        "type": libdoc.type,  # LIBRARY | RESOURCE
        "scope": getattr(libdoc, "scope", None),
        "source_doc": libdoc.doc or "",
        "keywords": [keyword_to_record(kw) for kw in libdoc.keywords],
    }
    return spec


def write_spec(spec: dict) -> Path:
    SPECS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SPECS_DIR / f"{spec['name']}.json"
    out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Subset of standard library names to build (default: all of DEFAULT_STD_LIBS)",
    )
    parser.add_argument(
        "--resources",
        type=str,
        default=None,
        help="Path to a directory of project .resource/.robot files to index alongside stdlib "
        "(e.g. ../../robot/resources). Each file is built as its own spec, kind='resource'.",
    )
    parser.add_argument(
        "--skip-stdlib",
        action="store_true",
        help="Skip building standard library specs (useful when only refreshing resources).",
    )
    args = parser.parse_args()

    built = []
    failed = []

    if not args.skip_stdlib:
        libs = args.only if args.only else DEFAULT_STD_LIBS
        for lib in libs:
            try:
                spec = build_one(lib, kind="stdlib")
                path = write_spec(spec)
                built.append(spec["name"])
                print(f"  ✓ {spec['name']:<20} {len(spec['keywords']):>3} keywords -> {path.name}")
            except Exception as exc:  # noqa: BLE001
                failed.append((lib, str(exc)))
                print(f"  ✗ {lib:<20} FAILED: {exc}", file=sys.stderr)

    if args.resources:
        res_dir = Path(args.resources)
        if not res_dir.exists():
            print(f"Resources path does not exist: {res_dir}", file=sys.stderr)
        else:
            patterns = ("*.resource", "*.robot", "*.py")
            files = sorted({p for pat in patterns for p in res_dir.rglob(pat)})
            for f in files:
                try:
                    spec = build_one(str(f), kind="resource")
                    if not spec["keywords"]:
                        continue  # skip plain test suites with no reusable keywords
                    path = write_spec(spec)
                    built.append(spec["name"])
                    print(f"  ✓ {spec['name']:<20} {len(spec['keywords']):>3} keywords -> {path.name} (resource)")
                except Exception as exc:  # noqa: BLE001
                    failed.append((str(f), str(exc)))
                    print(f"  ✗ {f}  FAILED: {exc}", file=sys.stderr)

    meta = {
        "robot_framework_version": RF_VERSION,
        "built": built,
        "failed": [name for name, _ in failed],
    }
    (SPECS_DIR / "_meta.json").write_text(json.dumps(meta, indent=2))

    print(f"\nBuilt {len(built)} spec(s), {len(failed)} failure(s). RF version: {RF_VERSION}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
