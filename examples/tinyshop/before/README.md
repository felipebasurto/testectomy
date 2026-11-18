# tinyshop

Checkout library.

## Pricing

- Prices are in cents (integers). Never use floats for money.
- A coupon reduces the subtotal. If the coupon is worth more than the subtotal,
  the order is free: the total is 0, never negative.
- Shipping is 499 cents, free when the subtotal is 5000 cents or more
  (before coupons).

## Payments

`charge()` calls the payment provider. If the provider times out, retry up to
2 more times, then raise `PaymentFailed`. Never charge twice for the same
order id.
