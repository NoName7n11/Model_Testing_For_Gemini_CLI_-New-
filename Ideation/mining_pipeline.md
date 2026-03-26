# Data Mining Pipeline Architecture

This document dictates the architecture of the automated system responsible for fetching and filtering issues from the target 30-50 repositories to form the evaluation benchmark.

## Pipeline Overview

### Phase 1: Ingestion Engine (GitHub API / GraphQL)
1. **Target Identification**: Consume the list of finalized repositories (e.g., `kubernetes/kubernetes`, `vercel/next.js`).
2. **Issue Fetching via GraphQL**: Fast API call to pull *closed Issues* linked unequivocally to *merged Pull Requests* in the last 2-3 years to ensure relevance to modern paradigms.
3. **Primary Data Extraction**:
   - `Issue Body`: The problem statement representing the user request.
   - `PR Diff`: The resolution (`gold_patch`).
   - `Base Commit SHA`: State of the code before the patch.
   - `Test Diff`: Any newly added tests inside the PR (this often becomes our `test_patch`).

### Phase 2: Heuristic Filtering (Complexity Validation)
This is entirely automated and designed to drop trivial tasks.
1. **File Count Filter**: Discard PRs touching fewer than 3 files or isolated to a single directory (to enforce a minimum context spread).
2. **Exclusion Filter**: Exclude PRs heavily touching purely configuration files, translations, `yaml`, or `md` changes ONLY (unless combined with actual codebase logic).
3. **AST / Cyclomatic Deep Analysis (Optional/Secondary)**: Utilizing Python's `ast` or Go's `parser/token` module to statically ensure that the touched methods actually have cross-references outside the local file scope, meaning they demand deep agent reasoning.

### Phase 3: Test Extraction & Harness Building
This is the hardest engineering facet. The pipeline must programmatically identify *what constitutes a test* inside the given repository.
1. Isolate the test-specific changes from the `gold_patch` (e.g., separating `src/util.py` (gold) vs `tests/test_util.py` (test patch)).
2. Parse the repository's `.github/workflows` or standard testing suite commands (`npm test`, `pytest`, `go test`) to generate a reliable `success_command`.
3. Auto-populate a `tasks.json` matching the draft dataset schema.

### Phase 4: Verification Loop (The "Dry Run")
- A containerized execution environment checks out the repository at the `Base Commit SHA`.
- It dynamically applies the `test_patch` (so tests fail).
- It then dynamically applies the `gold_patch` (so tests pass).
- Only tasks that definitively switch from `FAIL -> PASS` are persisted into the final benchmark database.

## Architecture Stack (Proposed)
- **Language**: Python (for rich AST parsing, GitHub API libs, and data science tooling).
- **Automation**: Docker-in-Docker (DinD) for isolating repository test environments aggressively.
- **Storage**: JSON/YAML flat files for Git-friendliness, optionally SQLite for easier local querying during development.