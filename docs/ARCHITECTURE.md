# Architecture Directory
## BDD → Robot Framework Test Suite Generator

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Agent Architecture](#2-agent-architecture)
3. [MCP Server Layer](#3-mcp-server-layer)
4. [Kilo Code Configuration](#4-kilo-code-configuration)

---

## 1. Project Structure
```
project-root/
│
├── .kilo/                              
│   ├── rules/                          # Global agent rules
│   │   └── global.md                   
│   ├── agents/                         # Named agent specializations
│   │   ├── bdd-ir-builder.md
│   │   ├── suite-builder.md
│   │   └── robocop-validator.md        # New: validator agent spec
│   └── kilo.jsonc                      # Kilo code configuration 
│
├── mcp/                                # MCP server definitions
│   ├── mcp.json                     
│   └── servers/
│       ├── gherkin-server/             # Parse gherkin files
│       │   └── server.py
│       ├── rf-runner-server/           # Execute Robot Framework
│       │   └── server.py
│       ├── rf-docs-server/             # RF keyword library documentation lookup
│       │   └── server.py
│       └── robocop-server/             # robocop linter
│           └── server.py
│
├── bdd/                                # Input: BDD feature files
│   └── features/
│       ├── login.feature
│       ├── checkout.feature
│       └── ...   
│
├── robot/                              # Output: Generated Robot Framework suites and resources
│   ├── suites/
│   │   ├── login_suite.robot
│   │   ├── checkout_suite.robot
│   │   └── ...
│   ├── resources/
│   │   └── keywords/
│   │       └── generated/              # Auto-generated keyword resources
│   └── results/                        # RF execution reports
│
├── pipeline/                           # Pipeline orchestration scripts and prompts
│   ├── run_pipeline.sh                 # Entry point: shell wrapper
│   ├── run_pipeline.py                 # Python orchestrator
│   ├── prompts/                        # Structured prompt templates per agent
│   │   ├── build_bdd_ir_task.md
│   │   ├── build_suite_task.md
│   │   └── validate_suite_task.md      # Robocop validator prompt
│   ├── schemas/                        # Intermediate data contracts
│   │   └── bdd-ir.schema.json
│   ├── run_summary.json                # Pipeline execution summary
│   └── robocop_report.json             # Output: combined Robocop report (validator)
│
└── docs/
    └── ARCHITECTURE.md                 
```

---

## 2. Agent Architecture

The system defines **two specialized agents**, each scoped to a single responsibility in the transformation pipeline. Kilo Code routes tasks to agents using **Subagents** delegation based on the rules file.

### 2.1 BDD IR agent (`bdd-ir-builder`)

**Responsibility:** Ingest a `.feature` file and produce a structured intermediate representation composed of the structure of the BDD file parsed with gherkin MCP and a Keyword mapping .

| Property | Value |
|---|---|
| Rules file | `.kilo/agents/bdd-ir-builder.md` |
| Input | `bdd/features/*.feature` |
| Output | `bdd/ir/bdd-ir.json` |
| MCP tools used | `gherkin:parse_feature_file`, `rf-docs:lookup_keyword` |
| Delegates to | `suite-builder` | 

**Key behaviors:**
- Parse Gherkin strictly: Feature, Background, Scenario, Scenario Outline, Examples.
- Normalize tags and scenario metadata into a structured IR.
- Produce a **structured BDD representation** plus a per-step keyword mapping.
- Mark unresolved steps explicitly instead of guessing.

---

### 2.2 Suite Builder Agent (`suite-builder`)

**Responsibility:** Consume the BDD IR and produce the final `.robot` test suite file from the keyword map, following RF best practices and project conventions. The agent performs three ordered steps: IR coherence analysis, suite generation using RF docs, and linting with Robocop.

| Property | Value |
|---|---|
| Rules file | `.kilo/agents/suite-builder.md` |
| Input | `pipeline/schemas/bdd-ir.json` |
| Output | `robot/suites/<name>_suite.robot` |
| MCP tools used | `rf-docs:lookup_keyword` |
| Delegates to | `robocop-validator` (validation is performed by a dedicated agent) |

**Key behaviors**
- Emit `*** Settings ***`, `*** Variables ***`, `*** Test Cases ***`, `*** Keywords ***` sections in that order
- Use `TITLE CASE` for test case names derived from Scenario titles
- Respect the variable naming convention: `${SCREAMING_SNAKE_CASE}`
- Never emit hardcoded credentials or environment-specific URLs — use variables

**Step 1 — Coherence analysis**
- Check that the BDD IR is structurally complete.
- Detect missing background references, unresolved step mappings, inconsistent scenario outlines, and duplicated semantics.
- Refuse generation or flag errors when the IR is incoherent.

**Step 2 — Suite generation**
- Generate Robot Framework sections in canonical order.
- Resolve keywords using RF docs and project resources.
- Preserve tags, variables, and scenario titles consistently.

**Step 3 — Emit artefacts**
- Write final `.robot` and `.resource` files to the `robot/` tree and return their paths to the orchestrator.

Note: Robocop linting/fixing is handled by a dedicated `robocop-validator` agent. The orchestrator will optionally invoke `robocop-validator` after `suite-builder` completes; this allows running generation and validation as separate pipeline stages.

---

### 2.3 Robocop Validator Agent (`robocop-validator`)

**Responsibility:** Validate and (optionally) format generated Robot Framework `.robot` and `.resource` files using Robocop. The agent performs iterative lint+format cycles (up to a configured limit) and produces a combined JSON report consumed by the orchestrator.

| Property | Value |
|---|---|
| Rules file | `.kilo/agents/robocop-validator.md` |
| Input | Newline-separated list of `.robot` and/or `.resource` file paths |
| Output | `pipeline/robocop_report.json` |
| MCP tools used | `robocop:get_robocop_report`, `robocop:run_robocop_format` |

**Key behaviors**
- Run a Robocop report for each supplied file and aggregate results.
- If errors/warnings are present, call the formatter and re-run the report, up to 3 cycles.
- Do not modify test semantics — only run non-destructive formatting fixes.
- Return `clean: true` in the report when there are zero errors and zero warnings across all files.

Delegation: None — this is a terminal validation step; the orchestrator records the report and marks the feature as validated or requiring manual review.


---

## 3. MCP Server Layer

All agent-to-environment interaction is mediated through MCP servers. Agents **never** call shell commands directly — they use MCP tools exclusively.


### 3.1 `rf-docs-server`

Serves Robot Framework standard library documentation for keyword lookup.

| Tool | Description | Parameters |
|---|---|---|
| `lookup_keyword` | Find a keyword by name in RF libs | `name: string, library?: string` |
| `search_keywords` | Full-text search across all RF libs | `query: string` |
| `list_libraries` | List all available RF libraries | — |

Backed by a local snapshot of RF 7.x documentation.

---

### 3.2 `robocop-server`

Wraps `robocop` for static analysis of `.robot` files.

| Tool | Description | Parameters |
|---|---|---|
| `lint_file` | Run robocop on a single file | `path: string, rules?: string[]` |

---

### 3.3 `rf-runner-server`

Optional execution validation

| Tool | Description | Parameters |
|---|---|---|
| `run` | Execute `robot` on a suite file | `suite_path: string` |
| `get_output` | Retrieve stdout/stderr from last run | — |

Returns: `{ exit_code: number, stdout: string, stderr: string }`

---

## 4. Kilo Code Configuration

### 4.1 Global Rules (`.kilo/rules/global.md`)

Applied to every agent in the system. Defines:

- **Language:** All generated Robot Framework files must be in English
- **No hallucination policy:** Never invent a keyword that hasn't been verified via `rf-docs` or found in `robot/resources/`
- **Schema compliance:** Every agent must validate its output against the relevant JSON schema before delegating
- **Error surfacing:** Agents must propagate errors up rather than silently skipping steps
- **Idempotency:** Re-running the same input must produce identical output

### 4.2. Agent Rules & Specializations

Each agent's rules file (`.kilo/agents/<name>.md`) follows this structure:

```markdown
# Agent: <name>
## Role
One-line description of the agent's single responsibility.

## Input Contract
- What files/data it receives
- Schema reference

## Output Contract
- What files/data it must produce
- Schema reference

## Tool Permissions
Exhaustive list of MCP tools this agent may call.
Agents MUST NOT call tools outside this list.

## Behavioral Rules
Numbered, testable rules governing the agent's decisions.
Example:
  1. Never create a keyword whose name matches an RF built-in.
  2. Always write `NEEDS_GENERATION` if a step cannot be mapped.

## Delegation
Which agent to call next under what condition.

## Forbidden Actions
Explicit prohibitions (e.g., "Never write directly to bdd/").
```

### 4.3 Orchestrator & Stage Execution

The Python orchestrator (`pipeline/run_pipeline.py`) supports explicit stage execution to allow running parts of the pipeline independently. Use the `--stage` flag with values `full`, `ir`, `suite`, or `validate` to run:

- `ir` — run only the `bdd-ir-builder` stage and produce IR files under `bdd/ir/`
- `suite` — run only the `suite-builder` stage (input: IR files)
- `validate` — run only the `robocop-validator` stage (input: generated `.robot`/`.resource` files)
- `full` — default: run the end-to-end flow for provided feature files

The shell entrypoint `pipeline/run_pipeline.sh` remains as a convenience wrapper but delegates to the Python orchestrator. New files introduced as part of this staged flow include:

- `pipeline/run_pipeline.py` — Python orchestrator (supports `--stage`)
- `pipeline/prompts/validate_suite_task.md` — prompt template for the validator
- `.kilo/agents/robocop-validator.md` — agent spec for validation
- `pipeline/robocop_report.json` — location where the validator writes its combined report
