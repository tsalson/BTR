# Test Architecture

This repository uses `pytest` to validate the BDD → Robot Framework pipeline at different levels of confidence. The tests are organized by concern so that each layer answers a different question:

- **Unit tests** check isolated logic.
- **Integration tests** check the pipeline end to end.
- **Evaluation tests** check output contracts.
- **Traceability tests** check that generated metadata stays consistent.
- **Coherence tests** check that intermediate data matches the source inputs.
- **Determinism tests** check that reruns are stable.
- **Performance tests** guard timing expectations.

---

## 1. Test entry points

The test suite is configured in [pyproject.toml](../pyproject.toml):

- `testpaths = ["tests"]`
- `addopts = "-ra -q"`

That means `pytest` will discover tests under the `tests/` directory and print a concise summary.

---

## 2. Shared test helpers

The central helpers live in [tests/conftest.py](../tests/conftest.py).

### Important fixtures

- `project_root`: points to the repository root.
- `sample_feature`: points to the sample Gherkin input.
- `sample_ir`: points to the expected sample IR JSON.
- `run_pipeline_cmd`: defines the command used to invoke the orchestrator.

### Helper functions

- `run_pipeline(*args)`: runs the pipeline script with the requested arguments.
- `load_json(path)`: reads JSON from disk for reuse in tests.

These helpers keep the individual tests focused on assertions rather than shell setup.

---

## 3. Test suite map

| Folder | Purpose | What it verifies |
|---|---|---|
| [tests/unit](../tests/unit) | Unit coverage | Path validation and orchestration logic in isolation |
| [tests/integration](../tests/integration) | End-to-end behavior | The pipeline can run in dry-run mode and produce expected summary output |
| [tests/evaluation](../tests/evaluation) | Contract/evaluation checks | JSON outputs satisfy semantic rules using DeepEval metrics |
| [tests/traceability](../tests/traceability) | Traceability checks | Summary metadata correctly links inputs to outputs |
| [tests/coherence](../tests/coherence) | Data consistency | The IR matches the source feature structure |
| [tests/determinism](../tests/determinism) | Repeatability checks | Running the pipeline twice yields the same normalized results |
| [tests/perf](../tests/perf) | Performance guardrails | The pipeline stays within reasonable runtime limits |

---

## 4. What each test does

### Unit tests

File: [tests/unit/test_orchestrator.py](../tests/unit/test_orchestrator.py)

These tests validate the `PipelineOrchestrator` class without needing a full pipeline run.

#### Covered cases

1. `test_validate_feature_files_accepts_expected_layout`
   - Creates a temporary `bdd/features/*.feature` file.
   - Calls `validate_feature_files(...)`.
   - Asserts that valid feature paths are accepted and resolved correctly.

2. `test_validate_ir_files_rejects_non_json_path`
   - Creates a fake `.txt` file under `bdd/ir/`.
   - Asserts that the validator rejects it because only `.json` is allowed.

3. `test_validate_suite_files_accepts_robot_and_resource_paths`
   - Creates temporary `.robot` and `.resource` files.
   - Verifies the validator accepts both expected output formats.

### Why this matters
These tests confirm the orchestrator’s basic rules for accepting and rejecting files.

---

### Integration tests

File: [tests/integration/test_pipeline_dry_run.py](../tests/integration/test_pipeline_dry_run.py)

This is the main end-to-end verification for the pipeline.

#### Covered case

1. `test_pipeline_dry_run_generates_summary`
   - Runs `run_pipeline("--dry-run", sample_feature)`.
   - Asserts the process exits successfully.
   - Verifies that the summary file exists.
   - Reads the summary JSON and asserts key counts:
     - `total_files == 1`
     - `successful_features == 1`
     - `failed_features == 0`
     - `all_robocop_clean is True`
     - the feature entry points to `bdd/features/sample.feature`

### Why this matters
This test proves the pipeline can complete a real run path without actually needing to fully execute all downstream actions.

---

### Evaluation tests

File: [tests/evaluation/test_deepeval_pipeline_outputs.py](../tests/evaluation/test_deepeval_pipeline_outputs.py)

These tests use DeepEval metrics to validate that outputs satisfy contracts, not just shape assumptions.

#### Custom metrics

- `PipelineSummaryContractMetric`
  - Checks that the summary JSON contains the expected top-level structure.
  - Verifies counts are internally consistent.
  - Confirms each feature entry has the required traceability fields.

- `IRContractMetric`
  - Checks that the sample IR has the expected feature name, scenario count, parse error state, and unresolved-step count.

#### Covered cases

1. `test_deepeval_summary_contract_on_pipeline_output`
   - Runs the pipeline.
   - Loads the generated summary.
   - Builds a `LLMTestCase` from the JSON output.
   - Uses `assert_test(...)` with the summary contract metric.

2. `test_deepeval_ir_contract_on_pipeline_output`
   - Reads the sample IR file.
   - Validates it using the IR contract metric.

### Why this matters
These tests check semantic correctness: the data is not just present, but also logically valid.

---

### Traceability tests

File: [tests/traceability/test_summary_traceability.py](../tests/traceability/test_summary_traceability.py)

These tests make sure the pipeline summary preserves traceable links between inputs and outputs.

#### Covered case

1. `test_summary_contains_traceable_file_paths`
   - Loads the summary JSON.
   - Asserts that the first feature entry has:
     - source file path
     - status
     - feature name
     - IR path
     - suite path
     - resource path
     - unresolved count

### Why this matters
This is the “can I follow the artifact chain?” check.

---

### Coherence tests

File: [tests/coherence/test_ir_coherence.py](../tests/coherence/test_ir_coherence.py)

These tests verify that the IR is internally consistent with the sample feature definition.

#### Covered case

1. `test_sample_ir_is_coherent_with_feature_and_steps`
   - Loads the sample IR JSON.
   - Confirms the source file and feature name.
   - Verifies the number of scenarios.
   - Traverses all steps and counts unresolved entries.
   - Asserts that `unresolved_count` matches the actual unresolved-step count.

### Why this matters
The IR is a contract boundary between parsing and generation. This test ensures the contract is honored.

---

### Determinism tests

File: [tests/determinism/test_repeatability.py](../tests/determinism/test_repeatability.py)

These tests check that the pipeline output is stable across reruns.

#### Covered case

1. `test_dry_run_summary_is_repeatable_for_same_input`
   - Runs the pipeline twice on the same feature.
   - Loads both summaries.
   - Removes the timestamp from both payloads.
   - Asserts the normalized outputs are equal.

### Why this matters
The pipeline should not produce different results just because it is run again.

---

### Performance tests

File: [tests/perf/test_generation_time.py](../tests/perf/test_generation_time.py)

These tests catch obvious regressions in runtime.

#### Covered case

1. `test_dry_run_pipeline_completes_within_threshold`
   - Times the dry-run command.
   - Asserts the command succeeds.
   - Verifies runtime stays below a threshold (`5.0` seconds).

### Why this matters
This protects the developer workflow from slowdowns that would make the pipeline harder to use.

---

## 5. How the tests interact

The test architecture is intentionally layered:

1. **Unit tests** check rule enforcement.
2. **Integration tests** validate real pipeline execution.
3. **Traceability and coherence tests** inspect the correctness of the generated artifacts.
4. **Evaluation tests** apply semantic contract checks.
5. **Determinism and performance tests** protect reliability and speed.

A good way to read the suite is:

- “Does the orchestrator accept correct inputs?” → unit
- “Does the pipeline actually run?” → integration
- “Does the output make sense?” → coherence/evaluation
- “Can I trace the artifacts back to the source?” → traceability
- “Is the output stable and fast?” → determinism/performance

---

## 6. Practical testing advice

When adding new tests, prefer the same layering pattern:

- Put isolated logic checks under `tests/unit`.
- Put end-to-end checks under `tests/integration`.
- Put semantic/contract checks under `tests/evaluation`.
- Put data consistency checks under `tests/coherence` or `tests/traceability`.

This keeps the suite readable and makes failures easier to diagnose.
