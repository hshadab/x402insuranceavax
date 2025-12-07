#!/bin/bash
# Production Setup Script for x402 Insurance
# This script helps automate production deployment

set -e  # Exit on error

echo "🚀 x402 Insurance Production Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo -e "${RED}❌ Please do not run this script as root${NC}"
   exit 1
fi

# Step 1: Check Python version
echo "📋 Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$PYTHON_VERSION" == "3.11" ] || [ "$PYTHON_VERSION" == "3.12" ]; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
else
    echo -e "${RED}❌ Python 3.11 or 3.12 required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo "📦 Step 2: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Step 3: Install dependencies
echo ""
echo "📥 Step 3: Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 4: Check for .env file
echo ""
echo "⚙️  Step 4: Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    read -p "Create .env from .env.example? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env with your production values before continuing${NC}"
        echo ""
        echo "Required values:"
        echo "  - AVAX_RPC_URL (Alchemy or Infura)"
        echo "  - BACKEND_WALLET_PRIVATE_KEY (your wallet's private key)"
        echo "  - BACKEND_WALLET_ADDRESS (your wallet's address)"
        echo "  - DATABASE_URL (PostgreSQL - optional)"
        echo ""
        read -p "Press Enter after editing .env file..."
    else
        echo -e "${RED}❌ Cannot proceed without .env file${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

# Load environment variables
set -a
source .env
set +a

# Step 5: Verify wallet configuration
echo ""
echo "🔑 Step 5: Verifying wallet configuration..."
if [ -z "$BACKEND_WALLET_PRIVATE_KEY" ] || [ "$BACKEND_WALLET_PRIVATE_KEY" == "your_private_key_here" ]; then
    echo -e "${RED}❌ BACKEND_WALLET_PRIVATE_KEY not configured${NC}"
    exit 1
fi

if [ -z "$BACKEND_WALLET_ADDRESS" ] || [ "$BACKEND_WALLET_ADDRESS" == "0xYourWalletAddressHere" ]; then
    echo -e "${RED}❌ BACKEND_WALLET_ADDRESS not configured${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Wallet configured: $BACKEND_WALLET_ADDRESS${NC}"

# Step 6: Check blockchain connectivity
echo ""
echo "⛓️  Step 6: Checking blockchain connectivity..."
python3 << EOF
import os
import sys
from blockchain import BlockchainClient

try:
    blockchain = BlockchainClient(
        rpc_url=os.getenv('AVAX_RPC_URL'),
        usdc_address=os.getenv('USDC_CONTRACT_ADDRESS'),
        private_key=os.getenv('BACKEND_WALLET_PRIVATE_KEY')
    )

    if blockchain.w3.is_connected():
        print("✅ Connected to blockchain")
        chain_id = blockchain.w3.eth.chain_id
        print(f"   Chain ID: {chain_id}")
        if chain_id == 43114:
            print("   Network: Avalanche Mainnet")
        elif chain_id == 43113:
            print("   Network: Avalanche Fuji (Testnet)")
        else:
            print(f"   Network: Unknown (Chain ID {chain_id})")
    else:
        print("❌ Failed to connect to blockchain")
        sys.exit(1)
except Exception as e:
    print(f"❌ Blockchain connection error: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Blockchain connectivity check failed${NC}"
    exit 1
fi

# Step 7: Check wallet balances
echo ""
echo "💰 Step 7: Checking wallet balances..."
python3 << EOF
import os
import sys
from blockchain import BlockchainClient

try:
    blockchain = BlockchainClient(
        rpc_url=os.getenv('AVAX_RPC_URL'),
        usdc_address=os.getenv('USDC_CONTRACT_ADDRESS'),
        private_key=os.getenv('BACKEND_WALLET_PRIVATE_KEY')
    )

    eth_balance = blockchain.get_eth_balance()
    usdc_balance = blockchain.get_balance()

    eth_formatted = blockchain.w3.from_wei(eth_balance, 'ether')
    usdc_formatted = usdc_balance / 1_000_000

    print(f"   ETH:  {eth_formatted:.6f} ETH")
    print(f"   USDC: {usdc_formatted:.2f} USDC")

    # Check minimum balances
    if eth_balance < blockchain.w3.to_wei(0.001, 'ether'):
        print("⚠️  WARNING: ETH balance is very low. You need ETH for gas fees.")
        print("   Recommended: At least 0.01 ETH")

    if usdc_balance < 10_000_000:  # 10 USDC
        print("⚠️  WARNING: USDC balance is low.")
        print("   Recommended: At least 100 USDC for production reserves")

except Exception as e:
    print(f"❌ Error checking balances: {e}")
    sys.exit(1)
EOF

# Step 8: Test database connection (if configured)
echo ""
echo "🗄️  Step 8: Testing database connection..."
if [ -n "$DATABASE_URL" ] && [ "$DATABASE_URL" != "postgresql://user:password@localhost:5432/x402insurance" ]; then
    python3 << EOF
import os
import sys
from database import DatabaseClient

try:
    db = DatabaseClient(database_url=os.getenv('DATABASE_URL'))
    print("✅ Database connection successful")
    print("   Using: PostgreSQL")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("   Falling back to JSON file storage")
EOF
else
    echo -e "${YELLOW}⚠️  No DATABASE_URL configured - using JSON file storage${NC}"
    echo "   For production, PostgreSQL is recommended"
fi

# Step 9: Run tests
echo ""
echo "🧪 Step 9: Running tests..."
read -p "Run unit tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pytest tests/unit/ -v --cov=. --cov-report=term-missing
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed${NC}"
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⏭️  Skipping tests"
fi

# Step 10: Start server (test mode)
echo ""
echo "🚀 Step 10: Ready to start server"
echo ""
echo "Configuration Summary:"
echo "  Environment: ${ENV:-development}"
echo "  Wallet: $BACKEND_WALLET_ADDRESS"
echo "  Database: ${DATABASE_URL:+PostgreSQL}"${DATABASE_URL:-JSON files}
echo "  Rate Limiting: ${RATE_LIMIT_ENABLED:-true}"
echo "  Payment Mode: ${PAYMENT_VERIFICATION_MODE:-simple}"
echo ""
echo -e "${GREEN}✅ Production setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review configuration in .env"
echo "  2. Fund wallet with USDC reserves"
echo "  3. Start server: python3 server.py"
echo "  4. Test endpoints: curl http://localhost:8000/health"
echo "  5. Deploy to production server"
echo ""
read -p "Start server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting server..."
    python3 server.py
else
    echo "Setup complete. Start server with: python3 server.py"
fi
