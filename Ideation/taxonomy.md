# Taxonomy: Long-Context Reasoning Scenarios

To effectively challenge the Gemini CLI, the dataset tasks must explicitly test the agent's ability to retain and synthesize information across thousands of lines of disparate code. We classify the testing parameters into the following taxonomy of long-context reasoning failure modes:

## 1. Cross-Boundary Dependency Resolution
- **Description**: The agent must modify a downstream consumer file entirely disconnected from the root source fix. A change in a core utility or interface necessitates finding and updating all distant callers in decoupled modules.
- **Example**: Changing the signature of an interface in `core/utils/parser.go`, requiring synchronous updates to 15 different files in the `pkg/controllers/` module.

## 2. Deep State-Management Refactoring
- **Description**: Variables or state objects are threaded deeply through multiple class hierarchies or functional compositions. The agent must trace the entire lifetime of a variable across files to fix a race condition or state corruption.
- **Example**: Unwinding how React component props or Redux state in a large TS mono-repo are mutated asynchronously across multiple hooks, thunks, and middleware layers.

## 3. Distributed Architectural Integrations
- **Description**: Features that span entirely different tiers of the application architecture, demanding context shifting.
- **Example**: Adding a new property to a database model in Rust/Go, which subsequently requires migrating the schema, updating the internal gRPC definitions, and surfacing the change through the REST API layer controllers simultaneously.

## 4. Unstructured Semantic Mapping (Knowledge Synthesis)
- **Description**: Resolving an issue by reading expansive documentation blocks natively within the codebase (e.g., Markdown files or inline JSDoc/Sphinx) and perfectly synthesizing it into a code fix.
- **Example**: A bug caused by violating a highly specific internal architectural constraint described only in a densely written `docs/ARCHITECTURE.md` file located in the root repository.

## 5. Non-Local Type Inheritance & Abstraction Tracking
- **Description**: Complex Object-Oriented or Interface-heavy structures where the logic isn't explicit in a single function, but inherited dynamically at runtime from abstract parent classes deeply nested elsewhere in the `src/` folder.
- **Example**: Python Mixins or Java Abstract Factory classes where the method being debugged is 4 inheritance layers deep.

By categorizing our dataset tasks using this taxonomy, the final Gemini CLI evaluation report will precisely pinpoint the CLI's weaknesses, showing not merely a "pass/fail" score, but rather exactly *what kind* of context the model is struggling to hold onto.