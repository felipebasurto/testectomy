from unittest import mock

import pytest

from tinyshop import payments


@pytest.fixture(autouse=True)
def reset():
    payments._charged.clear()


def test_charge_calls_provider():
    provider = mock.Mock()
    provider.charge.return_value = "r1"
    payments.charge(provider, "o1", 100)
    provider.charge.assert_called_once_with("o1", 100)


def test_charge_returns_receipt():
    provider = mock.Mock()
    provider.charge.return_value = "r1"
    assert payments.charge(provider, "o1", 100) == "r1"


def test_retries_then_fails():
    provider = mock.Mock()
    provider.charge.side_effect = payments.ProviderTimeout()
    with pytest.raises(payments.PaymentFailed):
        payments.charge(provider, "o2", 100)
    assert provider.charge.call_count == 3


def test_payment_failed_is_exception():
    assert issubclass(payments.PaymentFailed, Exception)
