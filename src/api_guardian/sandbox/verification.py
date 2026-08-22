"""Verification Payload Validator."""
import hashlib
import hmac


class VerificationPayloadValidator:
    """Validates the HMAC-SHA256 signature of an execution result payload."""
    
    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verifies the cryptographically signed result from the sandbox.
        
        Args:
            payload: The raw JSON bytes received via PUT request.
            signature: The X-Guardian-Signature header value.
            secret: The original signing secret provided to the bootstrap environment.
            
        Returns:
            bool: True if the signature matches exactly.
        """
        mac = hmac.new(secret.encode(), payload, hashlib.sha256)
        expected_signature = mac.hexdigest()
        return hmac.compare_digest(expected_signature, signature)
