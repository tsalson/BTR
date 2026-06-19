# BTR Pipeline Guide — BDD to Robot Framework

## Overview

The **BTR (BDD to Robot Framework) Pipeline** is a multi-agent system that transforms Gherkin BDD feature files into production-ready Robot Framework test suites.

### Architecture

```
Gherkin Feature Files
       ↓
[bdd-ir-builder agent]    → Parses Gherkin, resolves keywords
  ↓
BDD Intermediate Representation (JSON)
  ↓
[suite-builder agent]     → Generates RF suites and resources
  ↓
[robocop-validator agent] → Validates generated artefacts with Robocop
  ↓
Robot Framework Test Suites (.robot files)
```

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Kilo Code CLI installed and configured
- MCP servers configured in `.kilo/kilo.jsonc` (already done)
- Feature files in `bdd/features/`

### 2. Run the Pipeline

```bash
# Process a single feature file
./pipeline/run_pipeline.sh bdd/features/login.feature

# Run only IR generation stage
./pipeline/run_pipeline.sh --stage ir bdd/features/login.feature

# Run only suite generation from IR (pass bdd/ir/*.json)
./pipeline/run_pipeline.sh --stage suite bdd/ir/login-ir.json

# Run only Robocop validation (pass generated suite/resource paths)
./pipeline/run_pipeline.sh --stage validate robot/suites/login_suite.robot robot/resources/keywords/generated/login_keywords.resource

# Process all feature files
./pipeline/run_pipeline.sh --all

# Dry run (preview without executing)
./pipeline/run_pipeline.sh --dry-run bdd/features/login.feature

# Process from a file list
./pipeline/run_pipeline.sh --from-file feature_list.txt
```

### 3. Review Results

```bash
# View pipeline summary
cat pipeline/run_summary.json

# View generated test suite
cat robot/suites/login_suite.robot

# View intermediate representation
cat bdd/ir/login-ir.json
```

### 4. Implement Unresolved Keywords

If the IR shows `unresolved_count > 0`, implement the stubs:

```bash
cat robot/resources/keywords/generated/login_keywords.resource
# Edit and implement the stubs (they currently call Fail)
```

### 5. Run Tests

```bash
robot robot/suites/
# or with specific tag
robot --include smoke robot/suites/
```

---

## Directory Structure

```
project-root/
├── bdd/
│   ├── features/               ← Input: Gherkin .feature files
│   └── ir/                     ← Output: BDD IR JSON files
│
├── robot/
│   ├── suites/                 ← Output: Generated .robot test suites
│   ├── resources/keywords/
│   │   └── generated/          ← Output: Generated keyword stubs
│   └── results/                ← RF execution reports
│
├── pipeline/
│   ├── run_pipeline.sh         ← Entry point (shell script)
│   ├── run_pipeline.py         ← Orchestrator script (Python)
│   ├── prompts/                ← Agent task prompts
│   │   ├── orchestrator_task.md
│   │   ├── build_bdd_ir_task.md
│   │   └── build_suite_task.md
│   ├── schemas/                ← JSON schemas
│   │   └── bdd-ir.schema.json
│   └── run_summary.json        ← Output: Pipeline execution summary
│
└── .kilo/
    ├── kilo.jsonc              ← MCP server configuration
    ├── rules/
    │   └── global.md           ← Global agent rules
    └── agents/
        ├── orchestrator.md      ← Orchestrator agent definition
        ├── bdd-ir-builder.md    ← BDD IR builder agent definition
        └── suite-builder.md     ← Suite builder agent definition
```

---

## Agent Roles

### 1. bdd-ir-builder Agent

**What it does:**
- Parses Gherkin `.feature` files using the gherkin MCP server
- Resolves each step to a Robot Framework keyword (project resource, standard library, or needs generation)
- Outputs a structured JSON intermediate representation (BDD IR)

**Input:** `bdd/features/*.feature`
**Output:** `bdd/ir/*-ir.json`

**Task prompt:** `pipeline/prompts/build_bdd_ir_task.md`

### 2. suite-builder Agent

**What it does:**
- Consumes the BDD IR and generates complete `.robot` test suite files
- Creates `.resource` files with stubs for any unresolved keywords
- Returns generated artefact paths to the orchestrator for optional validation

**Input:** `bdd/ir/*-ir.json`
**Outputs:**
- `robot/suites/*_suite.robot`
- `robot/resources/keywords/generated/*_keywords.resource` (if needed)

**Robocop validation:** Performed by the `robocop-validator` agent. See `pipeline/prompts/validate_suite_task.md` and `.kilo/agents/robocop-validator.md`.

**Task prompt:** `pipeline/prompts/build_suite_task.md`

### 3. orchestrator Agent (Optional)

**What it does:**
- Manages sequential delegation of multiple feature files
- Aggregates results from all features
- Produces a unified summary report

**Input:** List of feature file paths
**Output:** `pipeline/run_summary.json`

**Invocation:** Via the `run_pipeline.py` script

---

## Understanding the BDD IR

The BDD Intermediate Representation (IR) is a JSON file that serves as the contract between `bdd-ir-builder` and `suite-builder`.

### IR Structure

```json
{
  "source_file": "bdd/features/login.feature",
  "feature": {
    "name": "User Login",
    "description": "...",
    "tags": ["smoke", "auth"],
    "background": {
      "steps": [
        {
          "keyword": "Given",
          "text": "the application is running",
          "resolution": {
            "status": "RESOLVED_PROJECT",
            "keyword_name": "Start Application",
            "source_file": "robot/resources/keywords/common.resource"
          }
        }
      ]
    },
    "scenarios": [ ... ]
  },
  "resource_imports": ["robot/resources/keywords/common.resource"],
  "library_imports": ["SeleniumLibrary"],
  "unresolved_count": 2,
  "parse_errors": [],
  "warnings": []
}
```

### Resolution Statuses

- **RESOLVED_PROJECT**: Keyword found in a project `.resource` file
- **RESOLVED_LIBRARY**: Keyword found in RF standard library (e.g., SeleniumLibrary)
- **RESOLVED_GENERATED**: Keyword generated in a previous IR
- **NEEDS_GENERATION**: Step will become a new keyword stub (requires human implementation)
- **UNRESOLVED**: Step could not be parsed or resolved (error case)

---

## Handling Unresolved Keywords

When `bdd-ir-builder` cannot find a matching keyword, it marks the step as `NEEDS_GENERATION` and provides a generation hint.

### Example

```gherkin
# Feature: login.feature
Then the user is redirected to the dashboard
```

If no matching keyword exists:

```json
{
  "status": "NEEDS_GENERATION",
  "keyword_name": "Verify Dashboard Is Displayed",
  "source_file": "robot/resources/keywords/generated/login_keywords.resource",
  "generation_hint": "Should verify the dashboard page title or a unique element is visible after login."
}
```

### Generated Stub

The `suite-builder` will create:

```robot
# robot/resources/keywords/generated/login_keywords.resource

*** Keywords ***
Verify Dashboard Is Displayed
    [Documentation]    Should verify the dashboard page title or a unique element is visible after login.
    # TODO: Implement — generated stub
    Log    Executing: Verify Dashboard Is Displayed    level=DEBUG
    Fail    msg=NOT IMPLEMENTED: Verify Dashboard Is Displayed
```

### Implementation

1. Edit the stub in `robot/resources/keywords/generated/login_keywords.resource`
2. Replace the `Fail` line with actual implementation
3. Example:

```robot
Verify Dashboard Is Displayed
    [Documentation]    Should verify the dashboard page title or a unique element is visible after login.
    Page Should Contain Element    id:dashboard-header
    Wait Until Element Is Visible    id:welcome-message    timeout=5s
```

---

## Pipeline Execution Summary

After running the pipeline, review `pipeline/run_summary.json`:

```json
{
  "timestamp": "2025-06-16T14:23:45Z",
  "feature_files": [
    {
      "file": "bdd/features/login.feature",
      "feature_name": "User Login",
      "ir_path": "bdd/ir/login-ir.json",
      "suite_path": "robot/suites/login_suite.robot",
      "resource_path": "robot/resources/keywords/generated/login_keywords.resource",
      "status": "success",
      "unresolved_count": 2,
      "robocop_clean": true,
      "errors": []
    }
  ],
  "summary": {
    "total_files": 1,
    "successful_features": 1,
    "failed_features": 0,
    "total_unresolved_keywords": 2,
    "all_robocop_clean": true
  }
}
```

### Status Meanings

- **success**: Feature fully processed, suite generated, Robocop clean
- **partial**: IR generated but suite generation incomplete (human review needed)
- **failed**: Feature processing failed (check `errors[]` for details)

---

## Troubleshooting

### Issue: Pipeline script not found

```bash
chmod +x pipeline/run_pipeline.sh
```

### Issue: Python not found

```bash
# Check Python installation
python3 --version

# Install dependencies
pip install -r requirements.txt  # or use uv run
```

### Issue: Kilo Code not found

```bash
# Check Kilo Code installation
kilo --version

# Install Kilo Code
# Follow instructions at https://kilo.ai/docs/installation
```

### Issue: MCP servers fail to start

```bash
# Check MCP server configuration
cat .kilo/kilo.jsonc

# Test individual servers
uv run mcp/gherkin-sever/server.py
uv run mcp/rf-docs-server/server.py
```

### Issue: Gherkin parsing errors

Check the feature file syntax. Common issues:
- Missing Feature keyword
- Incorrect indentation
- Invalid step keywords (must be Given, When, Then, And, But, or *)

### Issue: Keyword not resolved

Either:
1. Implement the keyword in a project `.resource` file
2. Let `suite-builder` generate a stub and implement it
3. Add the keyword to a library import

---

## Advanced Usage

### Process Specific Features

Create a file `features_to_process.txt`:

```
bdd/features/login.feature
bdd/features/checkout.feature
bdd/features/admin.feature
```

Run:

```bash
./pipeline/run_pipeline.sh --from-file features_to_process.txt
```

### Dry Run

Preview what the pipeline will do without executing:

```bash
./pipeline/run_pipeline.sh --dry-run --all
```

### Re-run Failed Features

Edit `pipeline/run_summary.json`, extract failed features, create a file with their paths, and re-run:

```bash
./pipeline/run_pipeline.sh --from-file failed_features.txt
```

---

## Customization

### Add Project-Specific Keywords

Create a resource file in `robot/resources/keywords/` and they will be automatically discovered by `bdd-ir-builder`:

```robot
# robot/resources/keywords/app.resource

*** Keywords ***
Open Login Page
    [Documentation]    Navigate to the login page and verify it is loaded.
    Go To    ${LOGIN_URL}
    Page Should Contain Element    id:login-form
```

### Customize Agent Behavior

Edit agent rules files:
- `.kilo/rules/global.md` — applies to all agents
- `.kilo/agents/bdd-ir-builder.md` — IR builder behavior
- `.kilo/agents/suite-builder.md` — suite builder behavior
- `.kilo/agents/orchestrator.md` — orchestrator behavior

### Add MCP Tools

Add more MCP servers to `.kilo/kilo.jsonc`:

```jsonc
{
  "mcp": {
    "my-custom-server": {
      "type": "local",
      "command": ["uv", "run", "mcp/my-server/server.py"],
      "enabled": true
    }
  }
}
```

---

## Best Practices

### 1. Keep Feature Files Focused

```gherkin
# ✅ Good: One feature, clear scenarios
Feature: User Login
  Scenario: Successful login

# ❌ Avoid: Multiple unrelated features in one file
Feature: Everything
  Scenario: Login
  Scenario: Checkout
  Scenario: Admin Panel
```

### 2. Use Descriptive Scenario Names

```gherkin
# ✅ Good
Scenario: User logs in with valid credentials and sees dashboard

# ❌ Avoid
Scenario: Test login
```

### 3. Use Data Outlines for Multiple Cases

```gherkin
# ✅ Good
Scenario Outline: Login fails with invalid credentials
  When user enters "<username>" and "<password>"
  Then error message is "<message>"

  Examples:
    | username | password | message |
    | invalid  | wrong    | Invalid credentials |

# ❌ Avoid
Scenario: Invalid user
Scenario: Invalid password
Scenario: Empty username
```

### 4. Use Tags for Grouping and Filtering

```gherkin
@smoke @auth
Feature: User Authentication
  
  @high-priority
  Scenario: Successful login
  
  @low-priority
  Scenario: Forgotten password
```

Then run tests by tag:

```bash
robot --include smoke robot/suites/
```

---

## Pipeline Rules

### Global Rules (Apply to all agents)

See `.kilo/rules/global.md`:
- All output must be in English
- No hallucination of keywords — verify everything
- Schema compliance is mandatory
- Errors must be reported explicitly, never silently skipped
- Files use snake_case naming
- Robot Framework style standards strictly enforced

### Agent-Specific Rules

- **bdd-ir-builder** (`.kilo/agents/bdd-ir-builder.md`): Parse once, resolve once, mark everything
- **suite-builder** (`.kilo/agents/suite-builder.md`): Generate once, lint until clean (max 3 passes)
- **orchestrator** (`.kilo/agents/orchestrator.md`): Never halt early; process all files; aggregate results

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: BDD Pipeline

on:
  push:
    paths:
      - 'bdd/features/**'

jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: ./pipeline/run_pipeline.sh --all
      - run: robot robot/suites/
      - uses: actions/upload-artifact@v3
        with:
          name: pipeline-results
          path: pipeline/run_summary.json
```

---

## Support & Debugging

### Enable Verbose Logging

```bash
export KILO_DEBUG=1
./pipeline/run_pipeline.sh --all
```

### Check Individual Agent Execution

```bash
# Run bdd-ir-builder on a single feature
kilo agent run bdd-ir-builder --prompt "Process bdd/features/login.feature"

# Run suite-builder on an IR
kilo agent run suite-builder --prompt "Build suite from bdd/ir/login-ir.json"
```

### Inspect Generated Files

```bash
# Pretty-print BDD IR
python3 -m json.tool bdd/ir/login-ir.json

# Validate RF syntax
robot --dryrun robot/suites/login_suite.robot

# Run Robocop manually
robocop robot/suites/login_suite.robot
```

---

## Next Steps

1. **Write feature files** in `bdd/features/`
2. **Run the pipeline**: `./pipeline/run_pipeline.sh --all`
3. **Review IR files**: Check `bdd/ir/` for intermediate representations
4. **Implement stubs**: Edit `robot/resources/keywords/generated/` files
5. **Run tests**: `robot robot/suites/`
6. **Iterate**: Refine feature files and implementations

---

## References

- [Gherkin Syntax](https://cucumber.io/docs/gherkin/)
- [Robot Framework Documentation](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Kilo Code Documentation](https://kilo.ai/docs)
- [BDD Best Practices](https://cucumber.io/docs/bdd/)

---

**Questions?** Check the agent rules files (`.kilo/agents/*.md`) or the pipeline code (`pipeline/run_pipeline.py`).
