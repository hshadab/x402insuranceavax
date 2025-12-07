"""
Unit tests for blockchain client
"""
import pytest
from blockchain import BlockchainClient


class TestBlockchainClient:
    """Test blockchain client (mock mode)"""

    def setup_method(self):
        # Initialize without private key (mock mode)
        self.client = BlockchainClient(
            rpc_url="https://api.avax-test.network/ext/bc/C/rpc",  # Avalanche Fuji
            usdc_address="0x5425890298aed601595a70AB815c96711a31Bc65",  # Avalanche Fuji USDC
            private_key=None
        )

    def test_mock_refund(self):
        """Test mock refund generation"""
        tx_hash = self.client.issue_refund(
            to_address="0xTestRecipient",
            amount=10000
        )

        assert tx_hash.startswith("0x")
        assert len(tx_hash) == 66  # Standard tx hash length

    def test_has_wallet_false_in_mock_mode(self):
        """Test wallet detection in mock mode"""
        assert self.client.has_wallet is False

    def test_get_balance_mock(self):
        """Test getting balance in mock mode"""
        balance = self.client.get_balance()
        assert balance == 0
