"""Deterministic FakeLLMGateway for integration tests."""
from typing import Any

from api_guardian.application.interfaces.llm import LLMGateway, LLMRole


class FakeLLMGateway(LLMGateway):
    """Returns a deterministic unified diff that replaces `source=` with `payment_method=`
    and `Charge.create` with `PaymentIntent.create`.

    The diff is pre-computed to match the fixture repository exactly.
    """

    def generate_completion(
        self,
        role: LLMRole,
        prompt_envelope: str,
        max_tokens: int | None = None,
    ) -> tuple[str, int, int]:
        response = (
            "Here is the migration patch:\n"
            "```diff\n"
            "--- a/src/payments.py\n"
            "+++ b/src/payments.py\n"
            "@@ -1,12 +1,12 @@\n"
            ' """Payment processing module using the Stripe API."""\n'
            " import stripe\n"
            " \n"
            " \n"
            "-def create_payment(amount: int, currency: str, token: str) -> dict:\n"
            '-    """Creates a payment charge using the deprecated `source` parameter."""\n'
            "-    charge = stripe.Charge.create(\n"
            "+def create_payment(amount: int, currency: str, payment_method_id: str) -> dict:\n"
            '+    """Creates a payment using PaymentIntent API."""\n'
            "+    intent = stripe.PaymentIntent.create(\n"
            "         amount=amount,\n"
            "         currency=currency,\n"
            "-        source=token,\n"
            "-        description=\"Payment via API Guardian test repository\",\n"
            "+        payment_method=payment_method_id,\n"
            "+        confirm=True,\n"
            "     )\n"
            "-    return {\"id\": charge.id, \"status\": charge.status}\n"
            "+    return {\"id\": intent.id, \"status\": intent.status}\n"
            "```\n"
        )
        # 150 prompt tokens, 80 completion tokens (deterministic fakes)
        return response, 150, 80

    def generate_structured(
        self,
        role: LLMRole,
        prompt_envelope: str,
        schema_cls: type,
        max_tokens: int | None = None,
    ) -> tuple[dict[str, Any], int, int]:
        return {}, 0, 0
