import pytest

from tinyshop.pricing import total


@pytest.mark.xfail(strict=True, reason="PRICE-3 bug: total goes negative instead of 0")
def test_PRICE_3_coupon_larger_than_subtotal_makes_order_free():
    cases = [
        ([(1000, 1)], 5000),
        ([(6000, 1)], 7000),
    ]
    assert [total(items, coupon) for items, coupon in cases] == [0, 0]


def test_PRICE_4_shipping_free_from_5000_subtotal_before_coupons():
    cases = [
        ([(100, 1)], 0),
        ([(4999, 1)], 0),
        ([(5000, 1)], 0),
        ([(2500, 2)], 0),
        ([(6000, 1)], 2000),
    ]
    assert [total(items, coupon) for items, coupon in cases] == [
        599,
        5498,
        5000,
        5000,
        4000,
    ]
