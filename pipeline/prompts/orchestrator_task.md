# Orchestrator Task: Process BDD Features to Robot Framework

## Objective
Execute the complete BDD → Robot Framework pipeline on the provided feature files.

## Input Parameters

### Feature Files
The following feature files will be processed:
```
{FEATURE_FILES}
```

Where `{FEATURE_FILES}` is replaced by the pipeline script with a newline-separated list of `bdd/features/*.feature` paths.

## Execution Steps

1. **Validate Input**
   - Confirm each file path starts with `bdd/features/` and ends with `.feature`
   - Check file existence
   - Deduplicate paths

2. **Process Each Feature File**
   - For each valid feature file:
     - Delegate to `bdd-ir-builder` agent with the feature file path
     - Wait for IR generation
     - Record the IR path and any warnings/errors

3. **Generate Test Suites**
   - For each successful IR file:
     - Delegate to `suite-builder` agent with the IR path
     - Wait for suite generation and Robocop linting
     - Record the suite path, resource path, and linting results

4. **Aggregate Results**
   - Compile all results into `pipeline/run_summary.json`
   - Include timestamps, file counts, error summaries

5. **Report Summary**
   - Return the execution summary to the human caller
   - List all generated files
   - Highlight any failures or warnings

## Expected Outputs

- `bdd/ir/*.json` — One or more BDD IR files
- `robot/suites/*.robot` — One or more test suite files
- `robot/resources/keywords/generated/*.resource` — Generated keyword resource files (as needed)
- `pipeline/run_summary.json` — Execution summary with results for all files

## Error Handling

- **Validation errors**: Report immediately; do not process invalid files
- **Parse errors**: Capture in IR; continue to suite generation if possible
- **Generation failures**: Record in summary; continue with next file
- **Robocop failures**: Halt that file's processing; record error in summary

## Partial Success Policy

- It is acceptable for some files to fail while others succeed
- Always process all input files; do not halt early
- Report all failures clearly in the summary

## Clean Success Criteria

✅ All feature files processed without validation errors
✅ All IR files generated (with or without unresolved keywords)
✅ All suite files generated
✅ All suite files pass Robocop linting (unless human review is needed)

## Next Steps After Success

1. Human reviews `pipeline/run_summary.json`
2. For unresolved keywords, developer implements keyword stubs in `robot/resources/keywords/generated/`
3. Run Robot Framework tests: `robot robot/suites/`
4. Iterate as needed
