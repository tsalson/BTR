#!/usr/bin/env python3
"""
rf-docs-server

Serves Robot Framework keyword documentation to agents over MCP, per
ARCHITECTURE.md §3.1. Backed entirely by a local snapshot of libdoc JSON
specs (see build_specs.py) — no network access and no live RF parsing at
query time, so results are deterministic and reproducible (idempotency
rule in .kilo/rules/global.md).

Tools:
  lookup_keyword(name, library?) -> exact/normalized keyword lookup
  search_keywords(query)         -> fuzzy/full-text search across all libs
  list_libraries()                -> enumerate loaded libraries + versions

Run:
  uv run mcp/servers/rf-docs-server/server.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from mcp.server.fastmcp import FastMCP

from config import get_config, logger, resolve_path

try:
    from rapidfuzz import fuzz

    _HAS_RAPIDFUZZ = True
except ImportError:
    _HAS_RAPIDFUZZ = False


# ---------------------------------------------------------------------------
# In-memory index
# ---------------------------------------------------------------------------


def _normalize(name: str) -> str:
    """
    RF keyword names are case-insensitive and whitespace/underscore-
    insensitive ("Should Be Equal" == "should_be_equal" == "ShouldBeEqual").
    Normalize to a canonical form for dict lookup.
    """
    return re.sub(r"[\s_]+", "", name).lower()


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9]*", text.lower()))


@dataclass
class KeywordRecord:
    name: str
    library: str
    kind: str  # "stdlib" | "resource"
    args: list
    arg_repr: str
    doc: str
    short_doc: str
    tags: list
    deprecated: bool
    source: Optional[str]

    def to_public_dict(self) -> dict:
        return {
            "name": self.name,
            "library": self.library,
            "kind": self.kind,
            "args": self.arg_repr,
            "doc": self.doc,
            "short_doc": self.short_doc,
            "tags": self.tags,
            "deprecated": self.deprecated,
            "source": self.source,
        }


@dataclass
class LibraryIndex:
    libraries: dict = field(default_factory=dict)  # name -> meta dict
    # normalized keyword name -> list[KeywordRecord] (multiple if ambiguous across libs)
    by_name: dict = field(default_factory=dict)
    # normalized keyword name -> tokens of name+doc, for search
    search_tokens: dict = field(default_factory=dict)
    all_records: list = field(default_factory=list)

    def add_spec(self, spec: dict) -> None:
        lib_name = spec["name"]
        self.libraries[lib_name] = {
            "name": lib_name,
            "kind": spec.get("kind", "stdlib"),
            "version": spec.get("version"),
            "type": spec.get("type"),
            "scope": spec.get("scope"),
            "keyword_count": len(spec.get("keywords", [])),
        }
        for kw in spec.get("keywords", []):
            record = KeywordRecord(
                name=kw["name"],
                library=lib_name,
                kind=spec.get("kind", "stdlib"),
                args=kw.get("args", []),
                arg_repr=kw.get("arg_repr", ""),
                doc=kw.get("doc", ""),
                short_doc=kw.get("short_doc", ""),
                tags=kw.get("tags", []),
                deprecated=kw.get("deprecated", False),
                source=kw.get("source"),
            )
            key = _normalize(record.name)
            self.by_name.setdefault(key, []).append(record)
            self.search_tokens[id(record)] = _tokenize(record.name) | _tokenize(record.short_doc)
            self.all_records.append(record)

    def lookup(self, name: str, library: Optional[str] = None) -> list:
        key = _normalize(name)
        candidates = self.by_name.get(key, [])
        if library:
            lib_key = library.strip().lower()
            candidates = [c for c in candidates if c.library.lower() == lib_key]
        return candidates

    def search(self, query: str, limit: int = 10, fuzzy: bool = True) -> list:
        query_tokens = _tokenize(query)
        scored = []

        for record in self.all_records:
            rec_tokens = self.search_tokens.get(id(record), set())
            overlap = query_tokens & rec_tokens
            score = len(overlap) / max(len(query_tokens), 1)
            # exact substring match in the keyword name is a strong signal
            if query.strip().lower() in record.name.lower():
                score += 1.0
            if score > 0:
                scored.append((score, record))

        if not scored and fuzzy and _HAS_RAPIDFUZZ:
            for record in self.all_records:
                s = fuzz.token_sort_ratio(query.lower(), record.name.lower()) / 100.0
                if s >= 0.6:
                    scored.append((s, record))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [record for _, record in scored[:limit]]


_index: Optional[LibraryIndex] = None


def load_index() -> LibraryIndex:
    """Load every *.json spec from the configured specs directory into memory."""
    cfg = get_config()
    idx = LibraryIndex()

    if not cfg.specs_dir.exists():
        logger.warning(
            "Specs directory %s does not exist. Run build_specs.py first.", cfg.specs_dir
        )
        return idx

    spec_files = sorted(cfg.specs_dir.glob("*.json"))
    spec_files = [f for f in spec_files if f.name != "_meta.json"]

    if not spec_files:
        logger.warning(
            "No libspec JSON files found in %s. Run build_specs.py first.", cfg.specs_dir
        )
        return idx

    for f in spec_files:
        try:
            spec = json.loads(f.read_text())
            idx.add_spec(spec)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load spec %s: %s", f, exc)

    logger.info(
        "Loaded %d library/resource spec(s), %d total keyword(s) from %s",
        len(idx.libraries),
        len(idx.all_records),
        cfg.specs_dir,
    )
    return idx


def get_index() -> LibraryIndex:
    global _index
    if _index is None:
        _index = load_index()
    return _index


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP("rf-docs-server")


@mcp.tool()
def lookup_keyword(name: str, library: Optional[str] = None) -> dict:
    """
    Find a Robot Framework keyword by name.

    Args:
        name: Keyword name, e.g. "Should Be Equal". Matching is
              case-insensitive and ignores spaces/underscores.
        library: Optional library name to disambiguate when the same
                 keyword name exists in multiple libraries (e.g. "Run
                 Keyword" defined identically nowhere, but generically
                 ambiguous names do occur across stdlib + resources).

    Returns:
        {
          "found": bool,
          "ambiguous": bool,            # true if multiple libraries define this name
                                          # and `library` was not provided to disambiguate
          "matches": [ {name, library, kind, args, doc, short_doc, tags,
                         deprecated, source}, ... ],
        }

        If nothing matches, "found" is false and "matches" is empty —
        callers (bdd-ir-builder, suite-builder) should treat this as an
        unresolved step per the no-hallucination policy, not invent a
        keyword.
    """
    idx = get_index()
    matches = idx.lookup(name, library=library)

    if not matches:
        logger.debug("lookup_keyword: no match for %r (library=%r)", name, library)
        return {"found": False, "ambiguous": False, "matches": []}

    distinct_libs = {m.library for m in matches}
    ambiguous = len(distinct_libs) > 1 and library is None

    return {
        "found": True,
        "ambiguous": ambiguous,
        "matches": [m.to_public_dict() for m in matches],
    }


@mcp.tool()
def search_keywords(query: str, limit: int = 10) -> dict:
    """
    Full-text search for keywords across all loaded libraries and resources.

    Useful when the exact keyword name from a BDD step is unknown — e.g.
    searching "click button" to find Browser/SeleniumLibrary-style
    keywords, or "read file" to find OperatingSystem keywords.

    Args:
        query: Free-text search query.
        limit: Maximum number of results to return (default 10).

    Returns:
        { "query": str, "results": [ {name, library, kind, args, doc,
                                       short_doc, tags, deprecated, source}, ... ] }

        Results are ranked by token overlap with keyword name + short doc,
        with substring matches on the name boosted, falling back to fuzzy
        string matching if rapidfuzz is installed and no token overlap is
        found. An empty "results" list means no reasonable candidate
        exists — surface this as an unresolved step rather than guessing.
    """
    idx = get_index()
    cfg = get_config()
    results = idx.search(query, limit=limit, fuzzy=cfg.fuzzy_search)
    return {
        "query": query,
        "results": [r.to_public_dict() for r in results],
    }


@mcp.tool()
def list_libraries() -> dict:
    """
    List all libraries and resource files currently loaded into the index.

    Returns:
        { "robot_framework_version": str | None,
          "libraries": [ {name, kind, version, type, scope, keyword_count}, ... ] }

        Use this to sanity-check that the snapshot matches the RF version
        pinned in the project, and to see which project resource files
        (robot/resources/*) are indexed alongside the standard libraries.
    """
    idx = get_index()
    cfg = get_config()
    meta_path = cfg.specs_dir / "_meta.json"
    rf_version = None
    if meta_path.exists():
        try:
            rf_version = json.loads(meta_path.read_text()).get("robot_framework_version")
        except Exception:  # noqa: BLE001
            pass

    return {
        "robot_framework_version": rf_version,
        "libraries": sorted(idx.libraries.values(), key=lambda l: l["name"]),
    }


if __name__ == "__main__":
    cfg = get_config()
    logger.info("Starting rf-docs-server (specs_dir=%s)", cfg.specs_dir)
    get_index()  # eager-load at startup so first tool call isn't slow / silently empty
    mcp.run()
