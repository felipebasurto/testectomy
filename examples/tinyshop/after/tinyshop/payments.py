class PaymentFailed(Exception):
    pass


class ProviderTimeout(Exception):
    pass


_charged = set()


def charge(provider, order_id, amount_cents):
    if order_id in _charged:
        return "already-charged"
    for _ in range(3):
        try:
            receipt = provider.charge(order_id, amount_cents)
            _charged.add(order_id)
            return receipt
        except ProviderTimeout:
            continue
    raise PaymentFailed(order_id)
