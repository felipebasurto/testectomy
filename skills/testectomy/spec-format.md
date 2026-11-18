# SPEC.md format

One file per area, next to the code it governs. Short enough to read in full
before every change to that area. Past ~150 lines, split the area.

## Template

```markdown
# <Area> spec

Governs: `src/billing/**`
Sources: README#pricing, #412, #530, user (2026-11-18)

## Purpose

One or two sentences: what this area is for, and who calls it.

## Rules

### BILL-1: Totals are never negative
Discounts larger than the subtotal clamp the total to 0.00.
Check: test (keep bar 2: money). Test: `billing.test.ts › BILL-1`
Source: #412

| Subtotal | Discount | Total |
|----------|----------|-------|
| 10.00    | 3.00     | 7.00  |
| 10.00    | 15.00    | 0.00  |

### BILL-2: Currency is the order's currency, never the user's locale
Check: read
Source: README#pricing

### BILL-3: Line items round half-even to 2 decimals per line, then sum
Check: test (keep bar 3: floating point). Test: `billing.test.ts › BILL-3`
Source: #530

## Non-goals

- Tax calculation (lives in `src/tax`, see its SPEC.md).
- Multi-currency carts.

## Open questions

- Code rejects zero-quantity lines; nothing in docs or issues says it should.
  Intended? (found during testectomy pass, 2026-11-18)
```

## Writing rules

- **One behavior per rule**, phrased as an outcome a caller can observe, not
  as how the code does it. "Retries 3 times then surfaces the provider error",
  not "calls `retryWithBackoff`".
- **Concrete examples beat prose.** A 3-row table of input → output does more
  than a paragraph. Use real values, not `foo`/`bar`.
- **Given/When/Then is optional.** Use it when a rule needs setup state:
  ```
  Given a user with an expired session
  When they call any /api route
  Then they get 401 with code SESSION_EXPIRED, and no data is read
  ```
- **No internal names** (private functions, classes, files) in the rule text.
  They belong only on the `Test:` line. A rename must never make a spec stale.
  Public API names that callers use (`PaymentFailed`, `charge()`) are fine.
- **Rule IDs are stable.** Never renumber. A retired rule gets
  `~~BILL-4~~ removed: <reason>` so old test names and commits still resolve.
- **Non-goals are rules too.** They stop agents from "helpfully" adding behavior.
- **Open questions get resolved by a human**, then move into Rules or get
  deleted. Never resolve one by reading the code.
