"""
Unit tests for payment verification
"""
import pytest
from auth.payment_verifier import SimplePaymentVerifier, PaymentDetails


class TestSimplePaymentVerifier:
    """Test simple payment verifier"""

    def setup_method(self):
        self.verifier = SimplePaymentVerifier(
            backend_address="0xTestBackend",
            usdc_address="0xTestUSDC"
        )

    def test_valid_payment(self):
        """Test valid payment verification"""
        result = self.verifier.verify_payment(
            payment_header="token=test,amount=1000,signature=abc",
            payer_address="0xTestPayer",
            required_amount=1000
        )

        assert result.is_valid is True
        assert result.amount_units == 1000
        assert result.payer == "0xTestPayer"

    def test_invalid_amount(self):
        """Test invalid payment amount"""
        result = self.verifier.verify_payment(
            payment_header="token=test,amount=500,signature=abc",
            payer_address="0xTestPayer",
            required_amount=1000
        )

        assert result.is_valid is False

    def test_missing_payment_header(self):
        """Test missing payment header"""
        result = self.verifier.verify_payment(
            payment_header="",
            payer_address="0xTestPayer",
            required_amount=1000
        )

        assert result.is_valid is False


class TestPaymentDetails:
    """Test PaymentDetails dataclass"""

    def test_payment_details_creation(self):
        """Test creating PaymentDetails"""
        details = PaymentDetails(
            payer="0xTest",
            amount_units=1000,
            asset="0xUSDC",
            pay_to="0xBackend",
            timestamp=123456,
            nonce="abc",
            signature="0xsig",
            is_valid=True
        )

        assert details.payer == "0xTest"
        assert details.amount_units == 1000
        assert details.is_valid is True
