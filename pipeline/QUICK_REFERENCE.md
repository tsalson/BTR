# BTR Pipeline — Quick Reference

## ⚡ Quick Start

```bash
# Run the pipeline
./pipeline/run_pipeline.sh --all

# View results
cat pipeline/run_summary.json

# Run generated tests
robot robot/suites/
```

## 📋 Commands

### Run pipeline on all features
```bash
./pipeline/run_pipeline.sh --all
```

### Run pipeline on specific features
```bash
./pipeline/run_pipeline.sh bdd/features/login.feature bdd/features/checkout.feature
```

### Run pipeline with file list
```bash
./pipeline/run_pipeline.sh --from-file feature_list.txt
```

### Dry run (preview only)
```bash
./pipeline/run_pipeline.sh --dry-run --all
```

### Show help
```bash
./pipeline/run_pipeline.sh --help
```

## 📁 Output Files

| File | Purpose |
|------|---------|
| `bdd/ir/*.json` | BDD Intermediate Representations (parsed features + keyword map) |
| `robot/suites/*.robot` | Generated Robot Framework test suites |
| `robot/resources/keywords/generated/*.resource` | Keyword stubs (if needed) |
| `pipeline/run_summary.json` | Pipeline execution summary |

## 🔄 Pipeline Flow

```
Feature File (.feature)
    ↓
[bdd-ir-builder] → Parse, resolve keywords
  ↓
BDD IR (JSON)
  ↓
[suite-builder] → Generate suite & resources
  ↓
[robocop-validator] → Validate & format (up to 3 cycles)
  ↓
Production-ready test suite
```

## 🎯 Agent Roles

| Agent | Task | Input | Output |
|-------|------|-------|--------|
| **bdd-ir-builder** | Parse & resolve keywords | `.feature` files | `bdd/ir/*.json` |
| **suite-builder** | Generate & validate suites | `bdd/ir/*.json` | `.robot` files + stubs |
| **robocop-validator** | Validate & format generated artefacts | `.robot`/`.resource` files | `pipeline/robocop_report.json` |
| **orchestrator** | Manage pipeline | File list | `run_summary.json` |

## 📊 Pipeline Summary (run_summary.json)

```json
{
  "timestamp": "2025-06-16T14:23:45Z",
  "feature_files": [
    {
      "file": "bdd/features/login.feature",
      "status": "success",
      "suite_path": "robot/suites/login_suite.robot",
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

## 🔧 Handle Unresolved Keywords

When `unresolved_count > 0`:

1. Open generated stub file:
   ```bash
   cat robot/resources/keywords/generated/login_keywords.resource
   ```

2. Find the stub keyword:
   ```robot
   Verify Dashboard Is Displayed
       [Documentation]    Generated stub — human implementation required
       Fail    msg=NOT IMPLEMENTED
   ```

3. Replace `Fail` with actual implementation:
   ```robot
   Verify Dashboard Is Displayed
       [Documentation]    Verify user sees dashboard after login
       Page Should Contain Element    id:dashboard
   ```

4. Test:
   ```bash
   robot robot/suites/login_suite.robot
   ```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Script not found | `chmod +x pipeline/run_pipeline.sh` |
| Python not found | `python3 --version` → Install Python 3.10+ |
| Kilo not found | Install Kilo Code CLI |
| MCP server fails | Check `.kilo/kilo.jsonc` configuration |
| Parse error | Check Gherkin syntax in `.feature` files |
| Keyword not resolved | Implement in project `.resource` file or stub |

## 📚 Documentation

- **Full guide**: `pipeline/PIPELINE_GUIDE.md`
- **BDD IR schema**: `pipeline/schemas/bdd-ir.schema.json`
- **Agent rules**: `.kilo/rules/global.md`
- **Agent specs**: `.kilo/agents/*.md`

## 💡 Tips

1. **Use tags** for test selection: `@smoke`, `@high-priority`
2. **Use outlines** for data-driven tests: `Scenario Outline` with `Examples`
3. **Keep features focused** — one feature per file ideally
4. **Review IR files** — they show exactly how steps are resolved
5. **Start small** — test pipeline on one feature first

## 🚀 Next Steps

1. Write feature files in `bdd/features/`
2. Run `./pipeline/run_pipeline.sh --all`
3. Implement unresolved keywords
4. Run tests: `robot robot/suites/`
5. Iterate on feature descriptions

---

For detailed information, see `pipeline/PIPELINE_GUIDE.md`
