# testectomy spec

Governs: `skills/testectomy/scripts/inventory.sh`
Sources: SKILL.md step 2, regressions found while building it (2026-11-18)

## Purpose

Prints every test file in a repo with its line count and approximate number of
cases, so an agent can pick areas and order of work before reading any test.

## Rules

### INV-1: Lists only source files that hold tests
Data files whose names look like tests (`table_test.pdf`, `tsconfig.test.json`)
are not listed. Snapshot files and `node_modules`, `vendor`, `dist`, `build` are
skipped.
Check: test (keep bar 5: regression, data files were counted). Test: `tests/test_inventory.py › test_INV_1_INV_2_INV_3`

### INV-2: Counts cases across the common runners
`it(`/`test(` (Vitest, Jest, Bun), `def test_` (pytest), `func TestX` (Go),
`#[test]` (Rust), `@Test` (JUnit), Gherkin `Scenario:`.
Check: test (keep bar 4: one regex over many syntaxes). Test: same

### INV-3: Always ends with a TOTAL line
Including when the repo has no snapshot or spec files.
Check: test (keep bar 5: regression, the script exited early under `set -e`). Test: same

### INV-4: One header per directory
Each directory appears once, even when sibling folders sort between its files.
Check: read

### INV-5: Empty repos say so
A repo with no tests prints `No test files found under <path>` and exits 0.
Check: read

## Non-goals

- Exact case counts. Parametrized cases and table tests count once.
- Choosing areas. That's the agent's job in step 2.
