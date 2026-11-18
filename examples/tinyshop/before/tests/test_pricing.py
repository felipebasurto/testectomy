from unittest import mock

from tinyshop import pricing


def test_shipping_constant():
    assert pricing.SHIPPING_CENTS == 499


def test_threshold_constant():
    assert pricing.FREE_SHIPPING_THRESHOLD == 5000


def test_subtotal_helper():
    assert pricing._subtotal([(100, 2), (50, 1)]) == 250


def test_shipping_helper_below():
    assert pricing._shipping(100) == 499


def test_shipping_helper_above():
    assert pricing._shipping(6000) == 0


def test_total_calls_helpers():
    with mock.patch.object(pricing, "_subtotal", return_value=100) as sub, \
         mock.patch.object(pricing, "_shipping", return_value=499) as ship:
        pricing.total([(100, 1)])
        sub.assert_called_once()
        ship.assert_called_once_with(100)


def test_total_with_coupon():
    items = [(1000, 1)]
    expected = pricing._subtotal(items) - 200 + pricing._shipping(pricing._subtotal(items))
    assert pricing.total(items, coupon_cents=200) == expected


def test_total_big_coupon():
    assert pricing.total([(1000, 1)], coupon_cents=5000) == -3501


def test_free_shipping_at_threshold():
    assert pricing.total([(5000, 1)]) == 5000
