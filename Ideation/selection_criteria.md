# Repository Selection Criteria

To ensure the Gemini CLI is stress-tested against rigorous, enterprise-grade challenges, the final 30-50 repositories must be curated using the following strict criteria:

## Core Filtering Metrics
1. **Activity & Maturity**:
   - The repository must be actively maintained (e.g., at least 500 commits in the last 12 months).
   - Must have a rich history of merged Pull Requests and closed Issues to serve as candidate tasks.
   - High community engagement (Stars > 5000, forks > 1000) to ensure code maturity.

2. **Scale & Complexity**:
   - Lines of Code (LOC) must be > 100,000 to ensure deep context windows are actually required.
   - Significant architectural complexity (e.g., deep folder structures, heavy use of abstractions/interfaces).
   - Inter-file dependencies: High degree of imports, references, and shared state across modules.

3. **Language Diversity Priorities**:
   - **Tier 1 (High Priority Segment)**: Python, TypeScript / Node.js, Go. (Targeting ~60% of the dataset).
   - **Tier 2 (Broad Regression Segment)**: Java, Rust, C/C++, Ruby. (Targeting ~40% of the dataset).
   - The selected languages must map well to real-world cloud/systems/web infrastructure development.

4. **Task Suitability**:
   - Pull Requests in the repository must frequently involve touching multiple files (ideally >= 4 files per complex task) across different sub-directories.
   - High frequency of "refactor", "architectural change", or "deep bug fix" type issues, rather than just isolated "typo fix" or "documentation".

## Methodology for Automated Selection
- We will parse GitHub metadata via the GitHub GraphQL API.
- We will measure cyclomatic complexity and abstract syntax tree (AST) depths using tools like `radon` (Python) or `escomplex` (JS/TS) on candidate repositories to filter out simplistic codebases.
- The preliminary list defined in `CompSci.md` will be evaluated against these metrics, funneling down to the hardest 30-50 repositories.
