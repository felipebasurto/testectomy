# Campaign mode

A campaign prunes one subsystem's whole test surface in one PR: a plugin, an
integration, or one core area of a large repo. Everything in
[SKILL.md](SKILL.md) applies to every lane: ground rules, keep bar, verdicts,
junk patterns, bite check, validation. This file adds the order of work and
the lessons of real campaigns. Each step ends on its completion criterion;
don't start the next one early.

Steps: 1 Baseline, 2 Lanes, 3 Ledger per lane, 4 Layer plan per lane,
5 Cutover, 6 Preservation review, 7 Product defects, 8 Reconcile and hand off.

## 1. Baseline

Pin a default-branch SHA. Record the subsystem's test, test-support and
production line counts, and every in-scope test file's pass/fail state. Keep
baseline failures in their own list: in one messaging-integration campaign,
all three baseline failures were real delivery bugs, not stale tests.

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

## 3. Ledger per lane

Give each lane to its own read-only agent when you can run agents in parallel.
The agent reads every assigned test in full, including parameter tables, plus
the production owners, entry points, callers, history and CI routing. Each
test declaration goes into a written **ledger** with one verdict from SKILL.md
(KEEP, FIX, CONVERT, FOLD, DELETE) and one evidence line:

- KEEP: the rule ID and the bug it catches. A test that only moves to a
  better-named file stays KEEP with the move noted.
- FIX: the assertion that can't fail and how to repair it.
- CONVERT: the owner that absorbs the assertion: a sibling table case, a
  stronger boundary suite, or the shared owner in another package.
- FOLD: the `read` rule whose example table takes it.
- DELETE: the proof that remains, or why no contract exists.

Done when every declaration in the lane has a verdict and an evidence line.

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

Edit lane by lane. Serialize changes to shared harnesses and support files
through one owner. With each lane, remove the production seams it unlocks.
Register moved suites in CI routing and test inventories, and update
shrink-only line-cap baselines. Write the test policy into the subsystem's
`AGENTS.md`, adding ownership rules drawn from mistakes this campaign actually
found.

Done when every lane plan is applied and each lane's keepers pass.

## 6. Preservation review

Before claiming completion, have independent reviewers compare deleted coverage
against the keepers, one reviewer per boundary group. They look for rules that
lost their only proof, and for new assertions that can't fail, such as a
rejection row the production code never reaches. One review of this kind found
nine real gaps and one unreachable assertion.

For each restored rule, bite-check it: one deliberate mutation of the
production owner turns the keeper red, then restore the source byte for byte.

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
