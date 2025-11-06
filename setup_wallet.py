#!/usr/bin/env python3
"""
Automated wallet setup script for x402 Insurance Service
Securely configures wallet address and private key in .env
"""

import os
import sys
import re
from pathlib import Path

def validate_address(address: str) -> bool:
    """Validate Ethereum address format"""
    if not address.startswith('0x'):
        return False
    if len(address) != 42:
        return False
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    return True

def validate_private_key(key: str) -> bool:
    """Validate private key format"""
    if not key.startswith('0x'):
        return False
    if len(key) != 66:
        return False
    if not re.match(r'^0x[a-fA-F0-9]{64}$', key):
        return False
    return True

def update_env_file(address: str, private_key: str):
    """Update .env file with wallet credentials"""
    env_path = Path('.env')

    if not env_path.exists():
        print("❌ .env file not found!")
        sys.exit(1)

    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Update lines
    updated_lines = []
    address_updated = False
    key_updated = False

    for line in lines:
        if line.startswith('BACKEND_WALLET_ADDRESS='):
            updated_lines.append(f'BACKEND_WALLET_ADDRESS={address}\n')
            address_updated = True
        elif line.startswith('BACKEND_WALLET_PRIVATE_KEY='):
            updated_lines.append(f'BACKEND_WALLET_PRIVATE_KEY={private_key}\n')
            key_updated = True
        else:
            updated_lines.append(line)

    # Add lines if they don't exist
    if not address_updated:
        # Find blockchain section and add
        for i, line in enumerate(updated_lines):
            if 'USDC_CONTRACT_ADDRESS' in line:
                updated_lines.insert(i + 1, f'BACKEND_WALLET_ADDRESS={address}\n')
                break

    if not key_updated:
        for i, line in enumerate(updated_lines):
            if 'BACKEND_WALLET_ADDRESS' in line:
                updated_lines.insert(i + 1, f'BACKEND_WALLET_PRIVATE_KEY={private_key}\n')
                break

    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)

    print(f"✅ Updated .env file")

def test_wallet_connection(address: str, private_key: str):
    """Test wallet connection to Base Sepolia"""
    try:
        from web3 import Web3

        # Connect to Base Sepolia
        w3 = Web3(Web3.HTTPProvider('https://sepolia.base.org'))

        if not w3.is_connected():
            print("⚠️  Warning: Could not connect to Base Sepolia RPC")
            return False

        # Test account
        account = w3.eth.account.from_key(private_key)

        if account.address.lower() != address.lower():
            print(f"❌ Error: Private key does not match address!")
            print(f"   Expected: {address}")
            print(f"   Got: {account.address}")
            return False

        # Get balance
        balance = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance, 'ether')

        print(f"✅ Wallet connected successfully!")
        print(f"   Address: {address}")
        print(f"   Balance: {balance_eth} ETH on Base Sepolia")

        if balance == 0:
            print(f"\n⚠️  Warning: Wallet has 0 ETH!")
            print(f"   Get test ETH from:")
            print(f"   • https://portal.cdp.coinbase.com/products/faucet")
            print(f"   • https://www.alchemy.com/faucets/base-sepolia")

        return True

    except ImportError:
        print("⚠️  web3.py not available, skipping connection test")
        return True
    except Exception as e:
        print(f"❌ Error testing wallet: {e}")
        return False

def main():
    print("=" * 70)
    print("x402 Insurance Service - Wallet Setup")
    print("=" * 70)
    print()

    # Check if running in correct directory
    if not Path('.env').exists():
        print("❌ Error: .env file not found!")
        print("   Please run this script from /home/hshadab/x402insurance/")
        sys.exit(1)

    print("This script will securely configure your Base Sepolia wallet.")
    print()
    print("⚠️  SECURITY WARNINGS:")
    print("   • NEVER share your private key with anyone")
    print("   • NEVER commit .env to git")
    print("   • Only use testnet funds for development")
    print("   • Consider using a hardware wallet for mainnet")
    print()

    # Get wallet address
    print("Step 1: Wallet Address")
    print("-" * 70)
    while True:
        address = input("Enter your Base Sepolia wallet address (0x...): ").strip()

        if not address:
            print("❌ Address cannot be empty")
            continue

        if not validate_address(address):
            print("❌ Invalid address format!")
            print("   Address must start with 0x and be 42 characters long")
            print("   Example: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
            continue

        print(f"✅ Valid address: {address}")
        break

    print()

    # Get private key
    print("Step 2: Private Key")
    print("-" * 70)
    print("⚠️  Your private key will NOT be displayed on screen")
    while True:
        # Use getpass for secure input
        import getpass
        private_key = getpass.getpass("Enter your private key (0x...): ").strip()

        if not private_key:
            print("❌ Private key cannot be empty")
            continue

        if not validate_private_key(private_key):
            print("❌ Invalid private key format!")
            print("   Private key must start with 0x and be 66 characters long")
            continue

        print(f"✅ Valid private key received")
        break

    print()

    # Confirm
    print("Step 3: Confirmation")
    print("-" * 70)
    print(f"Address: {address}")
    print(f"Private key: {'*' * 60} (hidden)")
    print()

    confirm = input("Update .env file with these credentials? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("❌ Setup cancelled")
        sys.exit(0)

    print()

    # Update .env
    print("Step 4: Updating Configuration")
    print("-" * 70)
    update_env_file(address, private_key)

    print()

    # Test connection
    print("Step 5: Testing Connection")
    print("-" * 70)
    test_wallet_connection(address, private_key)

    print()
    print("=" * 70)
    print("✅ Wallet setup complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Restart the server:")
    print("   pkill -f 'python server.py'")
    print("   source venv/bin/activate && python server.py")
    print()
    print("2. Check server status:")
    print("   curl http://localhost:8000/health")
    print()
    print("3. The server will now use real USDC refunds on Base Sepolia!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
