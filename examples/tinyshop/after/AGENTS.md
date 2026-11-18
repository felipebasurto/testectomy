# AGENTS.md

## Tests and specs

- Each area's intent lives in its `SPEC.md` (`tinyshop/SPEC.md`: `PRICE-*`
  pricing rules, `PAY-*` payment rules). Read it before changing that area.
- After a change, check every rule your diff touches. For `Check: read` rules,
  state in your summary that you re-checked them. For `Check: test` rules, run
  only the tests that cite those rule IDs (`python3 -m pytest -q -k PRICE_4`).
- A new test needs a `Check: test` rule that meets at least one of: external
  boundary, money/auth/data-loss/security, concurrency/time/ordering, large
  input space (parsers, formatters), a real past regression, or a public
  contract others depend on. Everything else is checked by reading. No tests
  for private helpers, restated constants, or mock call arguments.
- Behavior changes start in the spec: update the rule, then the code.
- If code and spec disagree, stop and ask. Don't edit the spec to match the code.
- Tests marked `xfail(strict=True)` are known bugs against a spec rule. When you
  fix one, remove the marker in the same change.
