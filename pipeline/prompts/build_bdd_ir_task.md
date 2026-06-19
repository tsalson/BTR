# Task: Build BDD Intermediate Representation

## Objective
Parse a Gherkin `.feature` file and produce a structured BDD Intermediate Representation (IR) with keyword resolution.

## Input Parameters

### Feature File
**Path**: `{FEATURE_FILE}`

This is the feature file to be parsed and analyzed.

## Execution Steps

1. **Pre-flight Validation**
   - Confirm the file path is `{FEATURE_FILE}`
   - Confirm it starts with `bdd/features/` and ends with `.feature`
   - Confirm the file exists
   - If validation fails, halt and report the specific error

2. **Parse Gherkin File**
   - Call `gherkin:parse_feature_file` with path `{FEATURE_FILE}`
   - Extract structured AST including Feature, Background, Scenarios, Examples, Tags
   - Preserve all line numbers and original text

3. **Resolve Keywords**
   - For each step (Background and Scenarios):
     - Search project resources in `robot/resources/keywords/` (excluding `generated/`)
     - Check Robot Framework standard library using `rf-docs:lookup_keyword`
     - Mark resolution status: `RESOLVED_PROJECT`, `RESOLVED_LIBRARY`, or `NEEDS_GENERATION`
     - Extract argument patterns and signatures

4. **Generate IR**
   - Build a structured JSON object conforming to `pipeline/schemas/bdd-ir.schema.json`
   - Include:
     - Parsed feature structure with all scenarios
     - Keyword resolutions for every step
     - Lists of imported libraries and resources
     - Count of unresolved keywords
     - Any parse errors or warnings

5. **Validate & Write**
   - Validate the IR against the JSON schema
   - Fix any schema violations before writing
   - Write to `bdd/ir/{FEATURE_NAME}-ir.json` (snake_case feature name)
   - Pretty-print with 2-space indentation

6. **Delegate (if successful)**
   - If IR generated successfully: delegate to `suite-builder` with the IR file path
   - If IR has errors: return the IR with errors noted for human review

## Expected Output

- **Path**: `bdd/ir/{FEATURE_NAME}-ir.json`
- **Format**: JSON conforming to `pipeline/schemas/bdd-ir.schema.json`
- **Content**: Complete AST with keyword resolution map

### Example Output Structure
```json
{
  "source_file": "bdd/features/login.feature",
  "feature": {
    "name": "User Login",
    "description": "...",
    "tags": ["smoke"],
    "background": { ... },
    "scenarios": [ ... ]
  },
  "resource_imports": ["robot/resources/keywords/common.resource"],
  "library_imports": ["SeleniumLibrary"],
  "unresolved_count": 2,
  "parse_errors": [],
  "warnings": []
}
```

## Key Rules

- **No hallucination**: Never invent keywords; always verify via MCP tools
- **Complete keyword map**: Every step must have a resolution status
- **Accurate arguments**: Extract arguments from parameterized steps
- **Placeholder normalization**: Convert `<placeholder>` to `${PLACEHOLDER}`
- **Generate hints**: For NEEDS_GENERATION steps, provide clear implementation guidance

## Clean Success Criteria

✅ IR file written to `bdd/ir/{FEATURE_NAME}-ir.json`
✅ IR conforms to JSON schema
✅ All steps have resolution status
✅ No hallucinated keywords
✅ Delegate to suite-builder with IR path
