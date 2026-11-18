# Field notes

What went wrong in real campaigns, and what changed in the skill because of it.

## Campaign 1: a SwiftUI app, 2,859 XCTest cases (November 2026)

The suite had already been pruned with earlier test-audit skills, so the cut was small: 291 cases and 3,707 lines of test code, about 10% of cases. An unpruned suite should give much more.

### Discovery and baseline

- **A pattern-based inventory script was the wrong tool.** It missed XCTest's `func testX()`, counted a vendored package as the app's tests, and grouped a flat 308-file folder into one useless "area". The skill now ships no scripts: the agent finds tests through the runner config, the CI job, build files and the runner's own listing.
- **The repo's own test script ran zero tests and exited 0.** A simulator name resolved to an OS where that device didn't exist. The baseline step now treats zero or suspiciously few cases as a failed baseline.
- **Runtime wasn't the cost.** Tests ran in 70 s inside a 288 s run; the rest was compiling. The baseline step now splits build time from run time and warns against promising faster runs.
- **Seven tests were skipped on every run.** Now a baseline finding of its own.
- **The repo had its own agent budget** (max agents, banned models, one full run per batch). Campaign mode now reads and obeys repo rules before planning.

### Audit

- **One agent per 12,800-line lane rubber-stamped.** It kept 431 of 439 tests, invented a rule with no source to justify keeping debug-seed tests, and judged 106 tests by name. The fix: chunks of at most ~3,500 lines, 2-3 calibration verdicts from the same repo, evidence that names a regression, rule IDs only with a non-code source, and UNREAD instead of guessing.
- **With that brief, 24 cheap agents in parallel worked.** Every chunk came back fully read, with concrete evidence in most rows.
- **Auditors over-deleted in predictable places.** 49 of 246 DELETEs were wrong: analytics event names (a contract with dashboards), date and formatter tables, rows in a formally specified area, and tests the auditor's own evidence called the last proof of a behavior. The keep bar now names telemetry contracts, and a DELETE whose evidence says nothing else covers it is invalid.
- **Names lie.** Files named after a plan phase or "leftover" held real behavior. They now CONVERT into owner suites instead of being judged by name.
- **New junk patterns:** tests of debug-only seed data, layout and motion constants, nil checks for removed UI, and opt-in screenshot harnesses that never run.

### Apply

- **Parallel agents appending to one shared file lost most of the writes.** Each agent now writes its own file, and the parent rebuilds the move list from the tree.
- **A brief named `MOVES.md` silently clashed with `moves.md`** on a case-insensitive disk. File names now differ by more than case.
- **Moved tests lost their setup and teardown**, leaking a debug locale and pending deep links into later tests, and one rewritten helper crashed on an unparseable date. Moves now carry fixtures and copy helpers verbatim, and the parent checks setup and teardown after the move pass.
- **A collapsed table test gained invented rows** (time zones with expected values from nowhere). Collapsing now keeps exactly the original cases.
- **Deleted functions left orphaned attributes** that broke the build. The parent now runs a build-only compile loop before any test run.
- **One account-deletion test failed only under load**, on a different case each time, and passed alone on both branch and base. The skill now says how to prove a flaky test is pre-existing.
- **A single cold build per side said the smaller branch was slower.** Timing now needs repeated cold builds in alternating order.

### Result

| | Before | After |
|---|---|---|
| Test cases | 2,859 | 2,568, all passing |
| Test code | 66,246 lines, 319 files | 62,539 lines, 304 files |
| Production code | | −27 lines of test-only seams |
| Specs | none | 8 area specs, 442 rules |
| Bite checks on collapsed tests | | 3 of 3 failed on a deliberate mutation |
| Build and run time | | not measurable: in two pairs of cold builds, whichever side ran second was 20-100 s slower |
