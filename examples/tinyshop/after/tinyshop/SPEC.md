# tinyshop spec

Governs: `tinyshop/**`
Sources: README#pricing, README#payments, testectomy pass (2026-11-18)

## Purpose

Checkout library: computes an order's total in cents (`total()`) and charges
it through a caller-supplied payment provider (`charge()`).

## Pricing rules

### PRICE-1: Money is integer cents, never floats
Prices, coupons, shipping and totals are integer cents.
Check: read
Source: README#pricing

### PRICE-2: A coupon reduces the subtotal
Total = subtotal (sum of price × quantity over all lines) − coupon + shipping.
Check: read (exercised by the PRICE-4 test)
Source: README#pricing

| Items (price × qty) | Coupon | Total |
|---------------------|--------|-------|
| 100 × 2, 50 × 1     | 0      | 749   |
| 1000 × 1            | 200    | 1299  |

### PRICE-3: A coupon worth more than the subtotal makes the order free
The total is 0, shipping included, and never negative.
Check: test (keep bar 2: money). Test: `tests/test_pricing.py › test_PRICE_3_coupon_larger_than_subtotal_makes_order_free`
Source: README#pricing

| Items (price × qty) | Coupon | Total |
|---------------------|--------|-------|
| 1000 × 1            | 5000   | 0     |
| 6000 × 1            | 7000   | 0     |

### PRICE-4: Shipping is 499, free when the subtotal before coupons is ≥ 5000
Check: test (keep bar 2: money). Test: `tests/test_pricing.py › test_PRICE_4_shipping_free_from_5000_subtotal_before_coupons`
Source: README#pricing

| Items (price × qty) | Coupon | Total |
|---------------------|--------|-------|
| 100 × 1             | 0      | 599   |
| 4999 × 1            | 0      | 5498  |
| 5000 × 1            | 0      | 5000  |
| 2500 × 2            | 0      | 5000  |
| 6000 × 1            | 2000   | 4000  |

## Payment rules

### PAY-1: Provider timeouts are retried twice, then `PaymentFailed`
`charge()` makes at most 3 provider attempts for the same order and amount.
If all 3 time out it raises `PaymentFailed`; any earlier success is returned.
Check: test (keep bar 1: external boundary). Test: `tests/test_payments.py › test_PAY_1_timeouts_retry_twice_then_payment_failed`
Source: README#payments

| Provider behavior            | Attempts | Outcome         |
|------------------------------|----------|-----------------|
| succeeds                     | 1        | receipt         |
| times out 2×, then succeeds  | 3        | receipt         |
| times out 3×                 | 3        | `PaymentFailed` |

### PAY-2: The same order id is never charged twice
A second `charge()` for an order that was already charged successfully does
not call the provider.
Check: test (keep bar 2: money). Test: `tests/test_payments.py › test_PAY_2_same_order_never_charged_twice`
Source: README#payments

### PAY-3: The same order id is never charged twice, even concurrently
While a charge for an order is in flight, another `charge()` for the same
order id does not call the provider.
Check: test (keep bar 2: money; keep bar 3: concurrency). Test: `tests/test_payments.py › test_PAY_3_concurrent_charges_for_same_order_hit_provider_once`
Source: README#payments

### PAY-4: `charge()` returns the provider's receipt
Check: test (keep bar 6: public contract). Test: `tests/test_payments.py › test_PAY_4_charge_returns_provider_receipt`
Source: current behavior (unconfirmed)

## Non-goals

- None stated in the README. Don't add behavior (tax, currencies, validation)
  without a source.

## Open questions

- PRICE-3: a coupon exactly equal to the subtotal isn't "worth more than the
  subtotal". Is the total 0 or 499 (shipping)? Code gives 499 (found during
  testectomy pass, 2026-11-18).
- PRICE-1: should `total()` reject float prices or coupons, or is "never use
  floats" only a caller convention? Code accepts floats silently.
- Negative prices, quantities or coupons: rejected, or caller's problem? Code
  accepts them.
- PAY-4: what `charge()` returns is not documented; current behavior is the
  provider's receipt. Confirm this is a contract.
- PAY-2: what does a duplicate `charge()` return? Code returns the string
  `"already-charged"` instead of the original receipt or an error. Nothing
  documents it.
- PAY-2/PAY-3: "never charged twice" is tracked in process memory only, so a
  restart or a second process forgets it. Is in-process enough?
- PAY-3: what should the second concurrent caller get: wait for the first
  result, an error, or `"already-charged"`?
- PAY-1 vs PAY-2: a provider timeout doesn't prove the charge failed. Retrying
  after a timeout can charge twice unless the provider dedupes by order id.
  Does the provider guarantee idempotency per order id?
- PAY-1: provider errors other than timeouts: propagate immediately, or retry?
  Code propagates them without retrying.
- After `PaymentFailed`, may the same order id be charged again later? Code
  allows it.
