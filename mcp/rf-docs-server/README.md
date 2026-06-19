# rf-docs-server

MCP server that serves Robot Framework keyword documentation, per
`ARCHITECTURE.md` §3.1. Used by `bdd-ir-builder` (keyword resolution while
building the BDD IR) and `suite-builder` (keyword resolution + builtin-name
collision checks while generating `.robot` suites).

Backed entirely by a **local snapshot** (`specs/*.json`) generated offline
via Robot Framework's own `libdoc`. The server never imports `robot`
libraries live and never makes network calls at query time — this is what
makes `lookup_keyword` / `search_keywords` results reproducible across runs,
per the idempotency rule in `.kilo/rules/global.md`.

## Setup

```bash
uv sync
python build_specs.py
```

This generates `specs/<LibraryName>.json` for the Robot Framework standard
libraries (BuiltIn, Collections, String, OperatingSystem, DateTime, Process,
XML, Screenshot, Telnet, Dialogs) plus `specs/_meta.json` recording the RF
version the snapshot was built against.

To also index project-specific keywords (so suite-builder can tell "verified
project keyword" apart from "verified RF builtin", and so collisions between
the two are flagged instead of silently resolved):

```bash
python build_specs.py --resources ../../../robot/resources
```

Re-run `build_specs.py` whenever:
- the pinned Robot Framework version changes, or
- files under `robot/resources/` are added/changed.

## Run

```bash
uv run server.py
```

Eagerly loads all specs at startup and logs a warning (not a crash) if the
`specs/` directory is empty — run `build_specs.py` first.

## Tools

| Tool | Description | Parameters |
|---|---|---|
| `lookup_keyword` | Exact/normalized lookup by name. Returns `ambiguous: true` if the name exists in multiple libraries and no `library` filter was given — callers must not silently pick one. | `name: string, library?: string` |
| `search_keywords` | Token-overlap search over keyword names + short docs, with substring-match boosting and an optional rapidfuzz fallback. | `query: string, limit?: int` |
| `list_libraries` | Enumerate loaded libraries/resources with version + keyword counts, for sanity-checking the snapshot against the project's pinned RF version. | — |

All three return `found: false` / empty `results` / `matches: []` rather
than guessing when nothing matches — consistent with the "no hallucination
policy" in `.kilo/rules/global.md`: an unresolved keyword must be surfaced
as `NEEDS_GENERATION`, never invented.

## Files

```
rf-docs-server/
├── server.py        # MCP server: tool definitions + in-memory index
├── config.py         # logging, path resolution, env-var driven Config
├── build_specs.py    # offline snapshot generator (run manually, not at server start)
├── pyproject.toml
├── specs/            # generated JSON libspecs (gitignore-able; rebuildable)
│   ├── BuiltIn.json
│   ├── Collections.json
│   ├── ...
│   └── _meta.json
└── README.md
```

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `RF_DOCS_SPECS_DIR` | `<server_dir>/specs` | Where to load libspec JSON from |
| `RF_DOCS_LOG_LEVEL` | `INFO` | Logger level |
| `RF_DOCS_FUZZY_SEARCH` | `1` | Set `0` to disable rapidfuzz fallback in `search_keywords` |
