# Expect tests

An expect test runs the boundary, prints the output, and compares it to a
literal stored in the test. The runner writes the first value and rewrites it
on request, so nobody hand-types expected values or field-by-field asserts.
The diff is the review.

Use them for the CONVERT verdict and for gaps on keep-bar rules with structured
output: parsers, renderers, CLI output, API responses, error messages, state
after a sequence of operations.

## Tooling

Use the repo's existing runner. Prefer inline over external snapshot files.

| Stack | Tool | Update command |
|-------|------|----------------|
| Vitest | `expect(x).toMatchInlineSnapshot()` | `vitest -u` |
| Jest | `expect(x).toMatchInlineSnapshot()` | `jest -u` |
| Bun | `expect(x).toMatchInlineSnapshot()` | `bun test --update-snapshots` |
| Python | `inline-snapshot` (`assert x == snapshot()`) | `pytest --inline-snapshot=fix` |
| Rust | `insta` (`assert_snapshot!(x, @"")`) | `cargo insta review` |
| Go | `github.com/hexops/autogold/v2` (`autogold.Expect(nil).Equal(t, x)`) | `go test -update` |
| OCaml | `ppx_expect` (`[%expect {\| \|}]`) | `dune promote` |
| Swift | `swift-snapshot-testing` `assertInlineSnapshot` | `record: .all` |
| Shell / CLI | cram-style `.t` files, or `insta_cmd` / `execa` + inline snapshot | tool-specific |

If the stack has no inline tool and adding one isn't allowed, use one plain
equality assert on a table of results. Write expected values from intent (the
spec's example table or the rule's source), never by running the code and
pasting what it printed.

## Shape

```ts
test("BILL-1: discounts larger than subtotal clamp to zero", () => {
  const cases = [
    { subtotal: 10, discount: 3 },
    { subtotal: 10, discount: 15 },
  ].map((c) => ({ ...c, total: checkout(cart(c)).total }));

  expect(cases).toMatchInlineSnapshot(`
    [
      { "discount": 3, "subtotal": 10, "total": 7 },
      { "discount": 15, "subtotal": 10, "total": 0 },
    ]
  `);
});
```

- Name it with the rule ID so `-t "BILL-1"` runs exactly the tests for a rule.
- Run the public boundary (`checkout`), not the private helper (`clampTotal`).
- Table of cases in, one printed table out. It reads like the spec's example table.
- Strip noise before printing: timestamps, random IDs, absolute paths. Replace
  them with stable placeholders, otherwise the snapshot churns and people
  update it blindly.
- Keep each snapshot under ~40 lines. If it's bigger, you're asserting more
  than the rule says.

## Updating

When an expect test fails:

1. Read the diff.
2. Check it against the rule in `SPEC.md`.
3. If the spec says the new output is right, update the snapshot. If it says
   the old one is right, fix the code. If the spec doesn't cover it, add an open
   question and ask.

Never run the update command without reading the diff. Blind updates turn the
test into a recording of whatever the code does today.

## Property tests

For keep-bar rule 4 with an invariant rather than examples ("parse(print(x)) ==
x", "total is never negative"), a property test (fast-check, Hypothesis,
proptest, QCheck) beats any number of examples. Name it with the rule ID too.
