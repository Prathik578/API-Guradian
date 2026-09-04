from typing import Any

import stripe


def create_payment(amount: int, currency: str, token: str) -> dict[str, Any]:
    """Creates a payment charge using the deprecated `source` parameter."""
    charge = stripe.Charge.create(
        amount=amount,
        currency=currency,
        source=token,
        description="Payment via API Guardian test repository",
    )
    return {"id": charge.id, "status": charge.status}


def refund_payment(charge_id: str) -> dict[str, Any]:
    """Refunds a charge."""
    refund = stripe.Refund.create(charge=charge_id)
    return {"id": refund.id, "status": refund.status}
