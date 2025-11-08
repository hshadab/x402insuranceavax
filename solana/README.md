# x402 Insurance on Solana

**Solana x402 Hackathon Submission**

Zero-knowledge proof verified insurance for x402 micropayments on Solana. Protect AI agents from merchant failures with cryptographically verified refunds in 400ms.

---

## 🎯 Hackathon Submission

- **Category:** Best x402 Agent Application ($20,000)
- **Deadline:** November 11, 2025
- **Status:** In Development (3 days remaining)

See [HACKATHON_STRATEGY.md](./HACKATHON_STRATEGY.md) for complete submission plan.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Solana CLI installed
- Solana devnet wallet with SOL + USDC

### Installation

```bash
# Install dependencies
pip install solana spl-token anchorpy

# Create Solana keypair (if needed)
solana-keygen new --outfile ~/.config/solana/devnet-keypair.json

# Get devnet SOL
solana airdrop 2 --url devnet

# Get devnet USDC from Circle faucet
# Visit: https://faucet.circle.com/
```

### Configuration

```bash
# Copy and configure environment
cp .env.solana.example .env.solana

# Edit .env.solana with your settings
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_CLUSTER=devnet
WALLET_KEYPAIR_PATH=~/.config/solana/devnet-keypair.json
USDC_MINT=4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU  # Devnet USDC
```

### Run Server

```bash
python server_solana.py
```

Server runs on `http://localhost:8000`

---

## 📖 API Endpoints

### Create Insurance Policy
```bash
POST /insure?network=solana

{
  "merchant_url": "https://api.example.com/data",
  "coverage_amount": 0.01
}
```

### Submit Claim
```bash
POST /claim?network=solana

{
  "policy_id": "uuid",
  "http_response": {
    "status": 503,
    "body": "",
    "headers": {}
  }
}
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│         AI Agent (Solana)            │
│  - Solana wallet (ed25519)           │
│  - USDC on Solana devnet             │
└──────────┬───────────────────────────┘
           │
           │ x402 Payment (Solana sig)
           ▼
┌──────────────────────────────────────┐
│      x402 Insurance API              │
│  - Flask server                      │
│  - Payment verification (Solana)     │
│  - Policy management                 │
└──────────┬───────────────────────────┘
           │
           │ Claim submission
           ▼
┌──────────────────────────────────────┐
│         zkEngine Prover              │
│  - Nova/Arecibo SNARKs               │
│  - HTTP response fraud detection     │
│  - Generate cryptographic proof      │
└──────────┬───────────────────────────┘
           │
           │ Valid proof
           ▼
┌──────────────────────────────────────┐
│      Solana Blockchain               │
│  - SPL Token program                 │
│  - USDC refund (400ms finality)      │
│  - Transaction on devnet             │
└──────────────────────────────────────┘
```

---

## 🔑 Key Features

### ⚡ Solana Advantages
- **400ms finality** - Instant refunds vs 2-5s on Base
- **$0.00005 fees** - Cheaper than Base EVM
- **High throughput** - 65,000 TPS capacity
- **Native x402** - Solana is primary x402 network

---

## 📁 File Structure

```
solana/
├── README.md                         # This file
├── HACKATHON_STRATEGY.md            # 3-day submission plan
├── .env.solana.example              # Configuration template
├── blockchain_solana.py             # Solana blockchain client
├── payment_verifier_solana.py       # Solana payment verification
├── server_solana.py                 # Flask API server
├── examples/
│   ├── agent_buy_policy_solana.py   # Example: Buy insurance
│   └── agent_claim_solana.py        # Example: File claim
└── tests/
    └── test_blockchain_solana.py
```

---

## 🏆 Hackathon Submission

### Why This Wins:
- First zkp-based insurance on Solana
- Solves real problem: agents lose money to downtime
- Production-ready (v2.2.0 on Base)
- Deep x402 protocol integration

---

**Built for the Solana x402 Hackathon - November 2025** 🚀
