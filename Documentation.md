# Gemini CLI Benchmark: Project Documentation

This document serves as the central reference guide for understanding how the Gemini CLI Benchmark Dataset Curation project is built, the methodologies applied, and the technologies used throughout its development lifecycle.

## Overview
As current agent evaluation benchmarks (like SWE-bench Pro) saturate, the Gemini CLI requires a highly challenging, novel dataset comprising 30-50 massive, multi-language repositories. This project curates these extensive codebases and strategically extracts real-world engineering problems demanding complex, multi-step reasoning across expansive context windows.

## Technology Stack
- **Data Scraping & Mining Pipeline**: Python 3.10+
  - `requests`: Direct GitHub GraphQL/REST API interaction.
  - `PyGithub`: Convenient GitHub REST API wrapper.
  - `python-dotenv`: Managing GitHub PAT (Personal Access Tokens).
- **Evaluation Environments**: Docker, Docker-in-Docker (DinD) for sandboxed, reproducible repository testing.
- **Dataset Schema**: JSON/YAML.
- **Languages Tested**: Python, TypeScript/Node.js, Go (Core Priority), plus Java, Rust, C++.

## Architecture & Project Structure

1. **`Ideation/`**: Contains the theoretical foundations and strategy documents.
   - `selection_criteria.md`: The metrics defining what makes a repository or task "hard enough".
   - `taxonomy.md`: Categorization of failure modes (cross-boundary resolution, deep state-management, etc.).
   - `mining_pipeline.md`: The logical flow of how we extract tasks from GitHub.
   - `schema_draft.json`: The standardized schema for a single benchmark task.

2. **`src/`**: The automated data mining and curation pipeline.
   - Scripts designed to interface with GitHub, filter Pull Requests based on cyclomatic complexity/file counts, and format them into the dataset schema.

## Development Workflow
### 1. Ingestion Engine
Python scripts query the GitHub GraphQL API to find merged Pull Requests in the targeted 30-50 repositories. The scripts specifically look for issues closed by PRs that have a high file-touch count across disparate directory structures.

### 2. Heuristic Filtering
The raw data is filtered heavily. We exclude PRs that are purely documentation (`.md`), simple config updates, or localized to a single file. We mandate a minimum context spread to ensure the Gemini CLI is tested on its ability to traverse complex architectural bounds.

### 3. Harness Verification
Each candidate task must undergo a 'dry run' in an isolated Docker container:
- Checkout the `commit_hash_base`.
- Apply the extracted `test_patch` (must fail).
- Apply the extracted `gold_patch` (must pass).
Only verified tasks are persistently added to the final benchmark dataset.

---
*This file will be updated continuously as the implementation of the dataset curation pipeline evolves.*