# Task: Validate generated Robot Framework artefacts with Robocop

## Objective
Validate one or more generated `.robot` or `.resource` files using Robocop and produce a combined JSON report.

## Input Parameters

- File list: one file path per line

{FILE_PATHS}

## Execution Steps

1. For each file listed above:
   - Run `robocop:get_robocop_report` (or equivalent MCP tool) to collect lint issues.
   - Optionally run `robocop:run_robocop_format` to apply non-destructive formatting fixes.
2. Repeat lint+format up to 3 times or until the combined report shows zero errors and zero warnings.
3. Write the final combined report to `pipeline/robocop_report.json` and return success status.

## Output

- `pipeline/robocop_report.json` — combined Robocop report for all supplied files

## Notes

- Do not alter test semantics; only formatting and structural fixes are permitted when applying formatter fixes.
- If any file still has errors/warnings after 3 attempts, return a non-zero status and include the report.
