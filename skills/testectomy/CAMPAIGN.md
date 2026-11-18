# Campaign mode

A campaign prunes one subsystem's whole test surface in one PR: a plugin, an
integration, or one core area of a large repo. Everything in
[SKILL.md](SKILL.md) applies to every lane: ground rules, keep bar, verdicts,
junk patterns, bite check, validation. This file adds the order of work. Each
step ends on its completion criterion; don't start the next one early.

Steps: 1 Baseline, 2 Lanes, 3 Ledger per chunk, 4 Layer plan per lane,
5 Cutover, 6 Preservation review, 7 Product defects, 8 Reconcile and hand off.

## 1. Baseline

Pin a default-branch SHA. Run the baseline checks in SKILL.md step 1 (case
count, build and run time, skipped tests). Record the subsystem's test,
test-support and production line counts, and every in-scope test file's
pass/fail state. Keep
baseline failures in their own list: they are often real bugs, not stale
tests.

Done when every in-scope test file has a recorded baseline result.

## 2. Lanes

Split the surface into **lanes** along production owner boundaries, not file
prefixes: accounts, commands, inbound, outbound, persistence, transport,
shared, harness, live or QA scenarios. Include the subsystem's cases at shared
core boundaries and its QA and live-proof harness tests. Each lane gets one
`SPEC.md` (or one ID prefix in a shared one), written per steps 3 and 4 of the
pass workflow.

Done when every test file and QA scenario the subsystem owns belongs to exactly
one lane, and every lane has its spec rules with `Check:` levels.

## 3. Ledger per chunk

Split each lane into **chunks** of at most ~3,500 test lines. An auditor given
a whole 12,000-line lane skims: it judges tests by name and invents rules to
justify keeping them. Chunk size and brief quality matter more than model size;
many cheap agents in parallel work well once the brief is strict.

Write one brief file all auditors read, with file paths, not pasted plans:

- the skill files, the repo's `AGENTS.md`, and the intent sources in order;
- **calibration**: 2-3 verdicts you already settled in this repo by hand (one
  junk, one misleading name that hides good tests, one clear keep);
- the evidence rules from SKILL.md (named regression, sourced rule IDs, UNREAD
  instead of guessing);
- signals specific to the repo (its debug seeds, its naming habits);
- the ledger shape: one table per chunk with File, Test, Verdict, Rule or keep
  bar, Evidence, one row per test declaration, then sections for draft spec
  rules, suspected bugs, test-only seams, keep-on-purpose and open questions;
- the auditor's final message: counts per verdict and anything unclear, under
  15 lines (the full report comes from the parent at hand-off).

Each auditor reads every assigned test in full, including parameter tables,
plus the production owners, entry points, callers, history and CI routing, and
writes its own ledger file. Each test declaration gets one verdict from
SKILL.md (KEEP, FIX, CONVERT, FOLD, DELETE) and one evidence line:

- KEEP: the rule ID and the bug it catches. A test that only moves to a
  better-named file stays KEEP with the move noted.
- FIX: the assertion that can't fail and how to repair it.
- CONVERT: the owner that absorbs the assertion: a sibling table case, a
  stronger boundary suite, or the shared owner in another package.
- FOLD: the `read` rule whose example table takes it.
- DELETE: the proof that remains, or why no contract exists.

Pilot the brief on one chunk before launching the rest, then check every
ledger before trusting it:

- **Spot check:** re-derive ~10 random verdicts against the code. More than 2
  disagreements and the chunk is redone.
- **Evidence scan:** count KEEP rows with short or generic evidence (no "fails
  if"). A high count means missed cuts; give that chunk a second pass.
- **DELETE review:** read every DELETE yourself, grouped by file. Auditors
  over-delete in predictable places: telemetry names, date and formatter
  tables, formally specified areas, and tests their own evidence calls the last
  proof of a behavior. Overrides go in a review file next to the ledgers, with
  the reason.

Done when every declaration in the lane has a verdict and an evidence line, and
the ledger passed the checks above.

## 4. Layer plan per lane

The ledger is input, not the edit list. A second read-only pass, starting from
the ledger, looks for the redundant **layer**: whole suites that replay a
shared component through a mock around a stronger real-transport suite. Name
the **keeper** suite for each rule. Prefer the real transport boundary with a
fake network over a mocked collaborator. Correct any ledger errors this pass
finds.

Done when each lane plan names its retired files, its keeper per rule, the
assertions to carry into keepers, and the test-only production seams unlocked.

## 5. Cutover

Edit in two passes. Implementing agents don't build or run tests; the parent
builds once after both passes.

- **Pass A, in parallel, one agent per chunk:** DELETE, FOLD, FIX, and CONVERT
  when the target is in the same chunk. A CONVERT into another chunk's file
  stays in place and goes into that agent's own moves file. Never let parallel
  agents append to one shared file: concurrent writes overwrite each other.
- **Pass B, one agent alone:** the cross-chunk moves, copying each test into
  its target before deleting it from the source.
- Rebuild the move list from the verdicts and the tree after pass A, not from
  what agents reported: check, test by test, whether it is still in its source,
  already in its target, or gone.
- Give brief and output files names that differ by more than case; some file
  systems treat `MOVES.md` and `moves.md` as one file.

When moving a test, it carries everything it depends on: its `setUp` and
`tearDown` (or the equivalent fixtures), and the original helpers copied as
they are. Agents tend to rewrite helpers from memory and drop cleanup, which
leaks state into every test that runs after the moved one. After pass B, check
each moved test's original class for setup and teardown and confirm the target
has the same.

When collapsing tests into one table test, keep exactly the original cases.
New rows are new tests and need a sourced rule.

After both passes, the parent builds and fixes compile errors in a loop with a
build-only command that reports every error (for example `xcodebuild
build-for-testing`, `tsc --noEmit`, `cargo check`), before running any tests. Expect leftovers:
attributes and annotations orphaned by deleted functions, helpers missing in
the target, helpers declared on the wrong type.

Serialize changes to shared harnesses and support files through one owner.
With each lane, remove the production seams it unlocks.
Register moved suites in CI routing and test inventories, and update
shrink-only line-cap baselines. Write the test policy into the subsystem's
`AGENTS.md`, adding ownership rules drawn from mistakes this campaign actually
found.

Done when every lane plan is applied and each lane's keepers pass.

## 6. Preservation review

Before claiming completion, have independent reviewers compare deleted coverage
against the keepers, one reviewer per boundary group. They look for rules that
lost their only proof, and for new assertions that can't fail, such as a
rejection row the production code never reaches.

For each restored rule, bite-check it: one deliberate mutation of the
production owner turns the keeper red, then restore the source byte for byte.
Also bite-check every table test created by collapsing. Several independent
mutations can share one run; confirm each one actually applied (`git diff`)
before reading the result, since a mutation that didn't apply looks like a
test that doesn't bite.

A test that fails only in the full run and passes alone on both the branch and
the base is a pre-existing flaky test, not a regression. Prove it by running it
alone on both before blaming the campaign, and list it in the report.

Measure time with cold builds on both sides, more than once and in alternating
order. A single cold build per side varies by tens of seconds, enough to hide
or invent the effect of a few thousand lines.

Done when every reported gap is restored or rejected with source evidence, and
every restored rule has a caught mutation.

## 7. Product defects

A baseline failure that survives into a keeper is a bug. With the user's go-ahead,
fix it at its owner as a separate commit and prove it through the real user
flow, with a **control** run that reverts the fix and shows the old behavior.
Without it, mark the keeper as an expected failure and report it. Record
unrelated discrepancies as follow-ups instead of fixing them in the campaign.

Done when each defect is either repaired (failing control, passing candidate on
the same harness) or reported with an expected-failure keeper.

## 8. Reconcile and hand off

Campaigns outlive many default-branch commits. Merge rather than rebase a long,
many-commit campaign. When the default branch modified a file the campaign
deleted, keep the deletion, port the new contract into the keeper, and confirm
every new regression has a home. Rerun the whole subsystem suite and any live
proof on the merged head.

Expect review tooling to see a truncated file list on a diff this large.
Record maintainer decisions for compatibility flags in the PR description
instead of editing gates.

Hand off with the SKILL.md report, plus:

- baseline and final test, test-support and production line counts;
- lanes, retired layers and keepers;
- preservation gaps found and their mutations;
- product defects with control and candidate proof, or their expected-failure
  keepers.
