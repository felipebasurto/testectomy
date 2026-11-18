SHIPPING_CENTS = 499
FREE_SHIPPING_THRESHOLD = 5000


def _subtotal(items):
    return sum(price * qty for price, qty in items)


def _shipping(subtotal):
    return 0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_CENTS


def total(items, coupon_cents=0):
    subtotal = _subtotal(items)
    return subtotal - coupon_cents + _shipping(subtotal)
