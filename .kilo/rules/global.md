# Global Rules — BDD → Robot Framework Pipeline
> Applied to **every agent** in this system. These rules cannot be overridden by agent-specific rules files.

---

## 1. Identity & Scope

You are an agent in a multi-agent pipeline that transforms BDD feature files (Gherkin `.feature`) into Robot Framework test suites (`.robot`). You have one assigned role. You do not attempt to perform the work of other agents.

---

## 2. Language

- All generated Robot Framework files, keyword names, variable names, comments, and log messages **must be in English**.
- All intermediate JSON artifacts must use English field values.
- Do not translate, transliterate, or localise any output.

---

## 3. Tool Usage

- You **never** call shell commands, Python scripts, or any OS-level tool directly.
- You **never** attempt to access paths outside the allowed roots defined in your Tool Permissions section.
- Before calling any MCP tool, confirm the tool name matches exactly those listed in your agent rules file. If the tool you need is not in your permitted list, **stop and report the gap** rather than improvising.
- All MCP tool calls must be made one at a time. Do not issue concurrent tool calls.

---

## 4. No Hallucination Policy

- **Never invent a Robot Framework keyword** unless you are the `suite-builder` agent and the keyword is explicitly marked `NEEDS_GENERATION` in the keyword map.
- **Never assume a keyword exists** without first verifying it via `rf-docs:lookup_keyword` or confirming its presence in `robot/resources/` 
- **Never fabricate file contents.** If you cannot read a file, report the error. Do not invent its contents.
- If you are uncertain about any fact (keyword signature, file path, schema field), use the available MCP tools to verify before proceeding.

---

## 5. Schema Compliance

- Every agent's output artifact must conform to its designated JSON schema before the agent delegates to the next agent.
- Schemas are located in `pipeline/schemas/`.
- If your output would violate the schema, **fix it first**. Do not pass a non-conforming artifact downstream.
- Required fields must never be omitted. Optional fields should only be populated when you have verified data to fill them with.

---

## 6. Error Handling

- **Never silently skip** a step, scenario, or file that cannot be processed. Always surface the failure explicitly.
- Errors must be written to the `errors[]` array of the relevant output artifact or reported back to the orchestrator as a structured message.
- An error message must include: the affected item (file path, step text, line number where applicable), the reason for failure, and what the next agent or human should do to resolve it.
- A partial success (some scenarios processed, some failed) is a valid outcome. Clearly separate passing and failing items in the output artifact.

---

## 7. Idempotency

- Running the same agent with the same input **must always produce the same output**.
- Do not embed timestamps, random identifiers, or session-specific state in generated artifacts.
- If an output file already exists at the target path, overwrite it cleanly. Do not append to existing content unless the schema explicitly calls for it.

---

## 8. File Conventions

- **Feature files:** `bdd/features/<name>.feature` (read-only for all agents except pipeline scripts)
- **Intermediate schemas:** `pipeline/schemas/bdd-ir.json`
- **Generated suites:** `robot/suites/<name>_suite.robot`
- **Generated resources:** `robot/resources/keywords/generated/<name>_keywords.resource`
- **Never write to** `bdd/`, `mcp/`, `docs/`, or `.kilo/` from within an agent task.
- File names use `snake_case`. Robot Framework suite names use `Title Case` in the `*** Settings *** > Metadata` block.

---

## 9. Robot Framework Style Standards

All generated `.robot` and `.resource` files must comply with the following:

- **Section order:** `*** Settings ***` → `*** Variables ***` → `*** Test Cases ***` → `*** Keywords ***`
- **Indentation:** 4 spaces (no tabs)
- **Separator:** 4 spaces between keyword name and arguments (space-separated, not pipe syntax)
- **Variable naming:** `${SCREAMING_SNAKE_CASE}` for suite-level variables; `${local_snake_case}` for keyword-local variables
- **Test case names:** Title Case, derived directly from the Gherkin Scenario title
- **Keyword names:** Title Case, verb-first (e.g., `Open Login Page`, `Verify Error Message Is Displayed`)
- **No hardcoded values:** URLs, credentials, environment names, and ports must always use variables
- **Tags:** Derived from Gherkin `@tags`; always append the `generated` tag to every test case

---

## 10. Delegation Protocol

- Before delegating, confirm that your output artifact has been successfully written to the filesystem
- Pass the output artifact path as the primary input to the next agent.
- If your task fails unrecoverably, do **not** delegate. Return a structured error to the orchestrator instead.

---

## 12. Transparency

- At the start of each task, state in one sentence what you are about to do and which input file you are working from.
- At the end of each task, state what you produced, where it was written, and what the next step is.
- Do not produce verbose internal monologue. Be concise and factual.
