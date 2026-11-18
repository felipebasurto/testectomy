import itertools
import threading

import pytest

from tinyshop.payments import PaymentFailed, ProviderTimeout, charge

_order_ids = (f"order-{n}" for n in itertools.count())


class ScriptedProvider:
    def __init__(self, timeouts=0):
        self.timeouts = timeouts
        self.calls = []

    def charge(self, order_id, amount_cents):
        self.calls.append((order_id, amount_cents))
        if len(self.calls) <= self.timeouts:
            raise ProviderTimeout()
        return f"receipt-{order_id}"


def _outcome(timeouts):
    order_id = next(_order_ids)
    provider = ScriptedProvider(timeouts)
    try:
        result = charge(provider, order_id, 1299)
    except PaymentFailed:
        result = "PaymentFailed"
    calls = [(o.replace(order_id, "<order>"), amount) for o, amount in provider.calls]
    return result.replace(order_id, "<order>"), calls


def test_PAY_1_timeouts_retry_twice_then_payment_failed():
    attempt = ("<order>", 1299)
    assert [_outcome(timeouts) for timeouts in (0, 2, 3)] == [
        ("receipt-<order>", [attempt]),
        ("receipt-<order>", [attempt] * 3),
        ("PaymentFailed", [attempt] * 3),
    ]


def test_PAY_2_same_order_never_charged_twice():
    order_id = next(_order_ids)
    provider = ScriptedProvider()
    charge(provider, order_id, 1299)
    charge(provider, order_id, 1299)
    assert len(provider.calls) == 1


class BlockingProvider:
    def __init__(self):
        self.calls = []
        self.in_flight = threading.Event()
        self.release = threading.Event()

    def charge(self, order_id, amount_cents):
        self.calls.append((order_id, amount_cents))
        if len(self.calls) == 1:
            self.in_flight.set()
            self.release.wait(timeout=5)
        return f"receipt-{order_id}"


@pytest.mark.xfail(strict=True, reason="PAY-3 bug: concurrent charges for one order both reach the provider")
def test_PAY_3_concurrent_charges_for_same_order_hit_provider_once():
    order_id = next(_order_ids)
    provider = BlockingProvider()
    first = threading.Thread(target=charge, args=(provider, order_id, 1299))
    first.start()
    assert provider.in_flight.wait(timeout=5)
    second = threading.Thread(target=charge, args=(provider, order_id, 1299))
    second.start()
    second.join(timeout=0.5)
    provider.release.set()
    first.join(timeout=5)
    second.join(timeout=5)
    assert len(provider.calls) == 1


def test_PAY_4_charge_returns_provider_receipt():
    order_id = next(_order_ids)
    assert charge(ScriptedProvider(), order_id, 1299) == f"receipt-{order_id}"
