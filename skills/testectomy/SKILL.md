---
name: testectomy
description: >-
  Rebuilds a repo's test surface around intent: writes Markdown spec files
  (SPEC.md) that state what each area must do, keeps only the executable tests
  a reader cannot replace (external boundaries, money, security, parsers,
  concurrency, real regressions), converts brittle assertions to expect tests,
  and deletes tests that re-encode the implementation. Use when the user asks
  for spec tests, Markdown specs, a test audit, to cut tests down to the
  essential ones, to replace tests with specs, or to reduce test time and token
  cost.
disable-model-invocation: true
---

# Testectomy

Tests that restate the implementation are a second, worse copy of the logic.
Intent is not: it lives in requirements, not in code, and nothing in the code
can validate it. This skill moves intent into `SPEC.md` files that humans own
and agents read, and keeps executable tests only where reading code cannot
replace running it.

Three layers, cheapest first:

| Layer | What it holds | Who checks it |
|-------|---------------|---------------|
| `SPEC.md` | Rules, examples, non-goals, open questions | Agent reads it before and after every change |
| Types / schemas | Shapes, exhaustiveness, nullability | Compiler |
| Executable tests | Only rules that pass the [keep bar](#keep-bar) | Test runner, scoped to touched rules |

For the spec file format, read [spec-format.md](spec-format.md). For expect-test
tooling per language, read [expect-tests.md](expect-tests.md).

## Ground rules

- **Specs come from intent, never from the code.** Sources: README, docs, issues,
  PR descriptions, commit messages, public API docs, product copy, the user.
  Reading the code to learn *what it does* is fine; copying that into a spec as
  *what it must do* is how tests end up blessing bugs.
- **Where code and intent disagree, never encode the code's behavior.** If the
  intent is unambiguous, the code has a bug: write the rule from intent, add its
  test as an expected failure (`pytest.mark.xfail(strict=True)`, `test.fails`,
  `#[should_panic]`-style, or a skip that names the rule ID), and report it under
  Bugs. Don't fix production code unless the user asked. If the intent is only
  partly clear, split it: the firm part becomes a rule ("never negative"), and
  the unclear part goes under `## Open questions` ("0 or 499?").
- **Unsourced behavior on a public contract isn't deletable.** If only the code
  says what a public API returns, keep the test, mark the rule
  `Source: current behavior (unconfirmed)`, and list it as an open question.
- **Don't add a framework.** If the repo already uses Cucumber, Gauge, specdown
  or similar, write specs in that format. Otherwise use plain Markdown plus the
  repo's existing test runner.
- **Fewer, stronger tests at public boundaries.** One test per rule, at the
  boundary where callers meet it. It must survive any refactor that keeps the
  behavior.

## Workflow

Copy this checklist and track it:

```
- [ ] 1. Baseline
- [ ] 2. Inventory
- [ ] 3. Gather intent
- [ ] 4. Write SPEC.md per area
- [ ] 5. Classify every test
- [ ] 6. Apply: delete, convert, fill gaps
- [ ] 7. Prove kept tests bite
- [ ] 8. Write the test policy into AGENTS.md
- [ ] 9. Verify and report
```

### 1. Baseline

Read the root and scoped `AGENTS.md`/`CLAUDE.md`, the CI config and the
package scripts. Run the full suite once and record: pass/fail counts, wall
time, flaky tests. A red baseline is a finding: report it, don't delete your
way to green.

### 2. Inventory

```bash
bash scripts/inventory.sh [repo-root]   # from this skill's folder
```

It prints every test file with its line count and approximate number of cases,
grouped by directory. Then choose the areas from the production code, not from
the test layout: an area is one cohesive behavior (pricing, payments, auth).
Several areas can share one `SPEC.md` with different ID prefixes when they
live in the same module. On large repos, run one area per pass and land each
separately.

### 3. Gather intent

For each area, collect intent sources *before* opening its tests. Write down
the source of each rule (`README#pricing`, `#412`, `commit a1b2c3`, `user`).
A rule with no source except the current code goes under
`## Open questions`, not `## Rules`. The one exception is a public contract
with an existing test (see Ground rules): that becomes a rule marked
unconfirmed *and* an open question. One sentence of intent may yield several
rules when it has distinct failure modes ("never charge twice": sequential and
concurrent).

When intent is thin, ask the user a short batch of concrete questions
("Should a discount larger than the subtotal give 0 or an error?").
Don't guess.

### 4. Write SPEC.md per area

Put it next to the code it governs (`src/billing/SPEC.md`), unless the repo
already has a `specs/` convention. Follow [spec-format.md](spec-format.md).
Every rule gets an ID (`BILL-3`) and a `Check:` level:

- `type`: the type system or a schema already enforces it.
- `read`: an agent verifies it by reading the diff against the rule.
- `test`: it passes the keep bar and needs an executable test.

Default to `read`. Promote to `test` only through the keep bar.

### 5. Classify every test

Read each test in full and give it exactly one verdict:

| Verdict | When | Action |
|---------|------|--------|
| **KEEP** | Guards a `Check: test` rule at its public boundary, even if it needs a rename or a mock swapped for a fake | Put the rule ID in the test name |
| **CONVERT** | Guards a keep-bar rule, but through many hand-written field asserts, mocks or private calls | Rewrite as one expect test at the boundary |
| **FOLD** | Its input → output pair illustrates a sourced `read` rule well | Move the example into that rule's table, then delete the test |
| **DELETE** | Restates implementation, duplicates another test, or tests the framework, mocks or trivia | Delete |

Test names carry the rule ID in a form the runner accepts and can filter on:
`"BILL-3: …"` with `-t BILL-3` (Vitest, Jest, Bun), `test_BILL_3_…` with
`-k BILL_3` (pytest), `TestBILL3…` with `-run BILL3` (Go).

When unsure between KEEP and DELETE, keep it and list it in the report with the
reason. Deletion count is not the goal.

### 6. Apply

- Delete DELETE/FOLD tests, then their now-unused fixtures, helpers, mocks, and
  any test-only exports or flags in production code.
- Rewrite CONVERT tests per [expect-tests.md](expect-tests.md).
- **Gaps:** every `Check: test` rule with no test gets one: an expect test at
  the boundary, named with the rule ID.
- Keep each area's change coherent: spec, test changes and seam removals land
  together.

### 7. Prove kept tests bite

For every new or converted test, and a sample of the KEEP ones: break the
behavior the rule describes in production code (flip a condition, drop a
branch), run that test, confirm it fails *for that reason*, then revert.
It has to be an assertion failure: a syntax, import or setup error proves
nothing. A test that stays green guards nothing: fix it or delete it. For an
expected-failure test, the bite check runs the other way: temporarily fix the
bug and confirm the test passes (strict mode then reports XPASS). Then run
`git diff` on production code to make sure every mutation was reverted.

### 8. Write the test policy into AGENTS.md

Add or replace the testing section with this, adjusted to the repo's commands:

```markdown
## Tests and specs

- Each area's intent lives in its `SPEC.md`. Read it before changing that area.
- After a change, check every rule your diff touches. For `Check: read` rules,
  state in your summary that you re-checked them. For `Check: test` rules, run
  only the tests that cite those rule IDs (`<runner filter> BILL-3`).
- A new test needs a `Check: test` rule that meets at least one of: external
  boundary, money/auth/data-loss/security, concurrency/time/ordering, large
  input space (parsers, formatters), a real past regression, or a public
  contract others depend on. Everything else is checked by reading. No tests
  for private helpers, restated constants, or mock call arguments.
- Behavior changes start in the spec: update the rule, then the code.
- If code and spec disagree, stop and ask. Don't edit the spec to match the code.
```

### 9. Verify and report

Run the remaining suite, the typecheck and the linter. Compare against the
baseline. Report in this format:

```markdown
## testectomy: <repo or area>

Before → after: <N> tests / <T>s → <N> tests (<x> expected-failure) / <T>s, test-file LOC <a> → <b>
(LOC can go up when gaps outnumber deletions; that's fine)
Baseline: <green/red, flaky tests, typecheck/lint state>
Specs written: <paths> (<n> rules: <x> test, <y> read, <z> type)

Bugs (<n>): <rule ID: intent vs actual behavior>, test marked expected-failure
Kept (<n>): <rule ID → test>, one line each with the keep-bar reason
Converted (<n>): <old tests → new expect test>
Gaps filled (<n>): <rule ID → new test>
Bite check: <n> mutations, all failed on an assertion and were reverted (git diff clean)
Deleted (<n>): grouped by reason, with counts
Open questions: <code vs intent disagreements needing a human call>
Production cleanup: <test-only seams removed>
AGENTS.md: <added / updated test policy, filter command>
```

## Keep bar

A rule gets `Check: test` only if at least one of these holds. Write which one
next to the rule.

1. **External boundary**: a provider, API, DB, file format, wire protocol or OS
   behavior that you don't control and that can change underneath the code.
   Use recorded real responses or a small scripted fake that behaves like the
   provider (times out, errors, succeeds). Asserting what the code did *to* the
   fake is fine when that is the rule ("3 attempts", "never charged twice").
2. **Costly or irreversible failure**: money, auth and permissions, data
   deletion, migrations, security, privacy.
3. **Hard to verify by reading**: concurrency, ordering, time zones and clocks,
   floating point, caching and invalidation, retries.
4. **Large input space**: parsers, serializers, formatters, compilers,
   renderers, validators. Use expect tests or property tests.
5. **A regression that actually happened**: link the incident or issue, and keep
   the test if the failure can plausibly come back.
6. **Public contract others depend on**: a library API, CLI output, plugin SDK,
   config format.

Everything else is `read`.

## Delete signals

- Asserts that a mock was called with arguments the code under test built,
  when no rule is about that interaction.
- Expected value computed by the same helper or logic under test.
- Tests a private function the boundary test already covers.
- Re-states constants, enums, exports, config or default values verbatim.
- Getters/setters, constructors, framework behavior, language features.
- Same contract asserted again at another layer with no new failure mode.
- A large snapshot nobody reviews (it gets updated blindly with `-u`).
- Breaks on renames or reorganizations that keep the behavior.

For the full junk-pattern checklist and the evidence bar for each deletion,
the `test-audit` skill applies. Use it alongside this one on large or shared
codebases.
