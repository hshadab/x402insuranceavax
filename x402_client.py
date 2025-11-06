"""
x402 payment verification
For MVP, this is a simple mock implementation
TODO: Implement real x402 protocol verification
"""


def verify_x402_payment(payment_header: str, expected_amount: int) -> dict:
    """
    Verify x402 payment header

    Args:
        payment_header: X-Payment header value (format: "token=...,amount=...,signature=...")
        expected_amount: Expected payment amount in USDC (6 decimals)

    Returns:
        {
            "valid": bool,
            "sender": str,  # Agent's address
            "amount": int,
            "error": str | None
        }
    """

    # Parse payment header
    try:
        parts = dict(p.split("=") for p in payment_header.split(","))

        token = parts.get("token")
        amount = int(parts.get("amount", 0))
        signature = parts.get("signature")

        if not token or not signature:
            return {
                "valid": False,
                "sender": None,
                "amount": 0,
                "error": "Missing token or signature"
            }

        if amount < expected_amount:
            return {
                "valid": False,
                "sender": None,
                "amount": amount,
                "error": f"Insufficient amount: {amount} < {expected_amount}"
            }

        # TODO: Verify JWT token with x402 protocol
        # TODO: Verify signature
        # TODO: Extract real sender from token

        # Mock sender address
        sender = "0x" + "1234567890abcdef" * 2 + "12345678"

        return {
            "valid": True,
            "sender": sender,
            "amount": amount,
            "error": None
        }

    except Exception as e:
        return {
            "valid": False,
            "sender": None,
            "amount": 0,
            "error": f"Payment parsing failed: {str(e)}"
        }
