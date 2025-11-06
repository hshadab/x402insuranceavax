# x402 Insurance Service - Production Documentation

**Status:** Production Ready (Base Mainnet)
**Version:** 1.0.0
**Date:** 2025-11-06

---

## Overview

ZKP-verified insurance service for x402 merchant fraud protection.

**What it does:**
- Accepts x402 payments for insurance premiums
- Generates zero-knowledge proofs for fraud claims
- Issues USDC refunds on Base Mainnet
- Provides public proof verification

---

## Quick Start

### 1. Install Dependencies

```bash
cd /home/hshadab/x402insurance
source venv/bin/activate
pip install -r requirements.txt
pip install /tmp/x402/python/x402
```

### 2. Configure Environment

Your `.env` is already configured for **Base Mainnet**:

```bash
# Blockchain - BASE MAINNET (PRODUCTION)
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/7OimkSMssMZr7nYzzenak
USDC_CONTRACT_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
BACKEND_WALLET_ADDRESS=0xba72eD392dB9d67813D68D562D2d67c36fFF566b
BACKEND_WALLET_PRIVATE_KEY=0x4cf2a14bdc2051d8b7422ef1c21dc7f51b2ce9055c71bd0004712ceeb2a35612

# zkEngine
ZKENGINE_BINARY_PATH=./zkengine/fraud_detector

# Insurance
DEFAULT_PREMIUM_USDC=1000
MAX_COVERAGE_USDC=1000000
POLICY_DURATION_HOURS=24
```

### 3. Fund Your Wallet

Your wallet needs:
- **ETH** for gas fees (~0.001 ETH per transaction)
- **USDC** for refunds (amount depends on expected claims)

**Wallet Address:** `0xba72eD392dB9d67813D68D562D2d67c36fFF566b`

**How to fund:**
1. Send ETH to your wallet on Base Mainnet
2. Send USDC to your wallet on Base Mainnet
3. Or bridge from Ethereum: https://bridge.base.org

### 4. Run Server

```bash
pkill -f "python server.py"  # Kill old instances
source venv/bin/activate
python server.py
```

Server runs on: **http://localhost:8000**

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Agent)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              x402 Flask Middleware                       │
│  • Intercepts /insure requests                          │
│  • Verifies x402 payment (1000 USDC)                    │
│  • Returns 402 if no payment                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Flask Server (server.py)                   │
│                                                          │
│  POST /insure  - Create insurance policy                │
│  POST /claim   - Submit fraud claim                     │
│  POST /verify  - Verify proof (public)                  │
│  GET  /proofs  - Download proof (public)                │
└──────┬──────────────────────┬──────────────────┬────────┘
       │                      │                  │
       ▼                      ▼                  ▼
┌─────────────┐    ┌──────────────────┐  ┌─────────────┐
│ zkEngine    │    │ Blockchain       │  │ JSON        │
│ (Proofs)    │    │ (USDC Refunds)   │  │ Storage     │
│             │    │                  │  │             │
│ Nova/       │    │ Base Mainnet     │  │ policies/   │
│ Arecibo     │    │ via Alchemy      │  │ claims      │
└─────────────┘    └──────────────────┘  └─────────────┘
```

---

## API Endpoints

### 1. Create Insurance Policy

**Endpoint:** `POST /insure`

**Requires:** x402 payment (1000 USDC)

**Request:**
```bash
curl -X POST http://localhost:8000/insure \
  -H "X-PAYMENT: <base64-encoded-payment>" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_url": "https://api.example.com",
    "coverage_amount": 10000
  }'
```

**Response (Success):**
```json
{
  "policy_id": "uuid",
  "agent_address": "0x...",
  "coverage_amount": 10000,
  "premium": 1000,
  "status": "active",
  "expires_at": "2025-11-07T10:00:00"
}
```

**Response (No Payment):**
```json
{
  "x402Version": 1,
  "accepts": [{
    "network": "base",
    "maxAmountRequired": "1000000000",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "payTo": "0xba72eD392dB9d67813D68D562D2d67c36fFF566b"
  }],
  "error": "No X-PAYMENT header provided"
}
```

### 2. Submit Fraud Claim

**Endpoint:** `POST /claim`

**Request:**
```bash
curl -X POST http://localhost:8000/claim \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "uuid",
    "http_response": {
      "status": 503,
      "body": "",
      "headers": {}
    }
  }'
```

**Response:**
```json
{
  "claim_id": "uuid",
  "proof": "0xabc...",
  "public_inputs": [1, 503, 0, 10000],
  "payout_amount": 10000,
  "refund_tx_hash": "0x...",
  "status": "paid",
  "proof_url": "/proofs/uuid"
}
```

### 3. Verify Proof (Public)

**Endpoint:** `POST /verify`

**Request:**
```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "proof": "0xabc...",
    "public_inputs": [1, 503, 0, 10000]
  }'
```

**Response:**
```json
{
  "valid": true,
  "fraud_detected": true,
  "payout_amount": 10000
}
```

### 4. Download Proof (Public)

**Endpoint:** `GET /proofs/<claim_id>`

**Request:**
```bash
curl http://localhost:8000/proofs/<claim_id>
```

**Response:**
```json
{
  "claim_id": "uuid",
  "proof": "0xabc...",
  "public_inputs": [1, 503, 0, 10000],
  "http_status": 503,
  "payout_amount": 10000,
  "refund_tx_hash": "0x...",
  "verification_result": true
}
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Flask 3.0 | HTTP server |
| Payment Protocol | x402 (Coinbase) | Decentralized payments |
| ZK Proofs | zkEngine (Nova/Arecibo) | Fraud verification |
| Blockchain | Base Mainnet | USDC refunds |
| RPC Provider | Alchemy | Reliable Base access |
| Storage | JSON files | Simple persistence |

---

## Zero-Knowledge Proofs

### What Gets Proven

The zkEngine proof cryptographically proves:
1. **Execution correctness:** WASM fraud detection executed correctly
2. **Input/output binding:** Given status + body_length → fraud result
3. **Fraud logic:** Detection rules applied correctly

### Fraud Detection Rules

Fraud is detected when:
- HTTP status >= 500 (server errors)
- HTTP body length == 0 (empty responses)

### Performance

- **Proof generation:** ~10-20 seconds
- **Proof size:** Several KB
- **Algorithm:** Nova IVC + Spartan SNARK
- **Curve:** Bn256 with IPA commitments

### Public Inputs

Anyone can verify these are in the proof:
- `is_fraud` - Whether fraud detected (1/0)
- `http_status` - HTTP status code
- `body_length` - Response body length
- `payout_amount` - Refund amount

### Private Data

NOT revealed in proof:
- Actual HTTP response content
- HTTP headers
- Merchant URL

---

## USDC Refunds

### Contract

**USDC on Base Mainnet:** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

### Process

1. Fraud claim submitted
2. zkEngine generates proof (~10-20s)
3. Proof verified automatically
4. USDC transfer executed
5. Transaction hash returned

### Gas Costs

- **Per refund:** ~21,000 gas (ERC20 transfer)
- **Cost:** ~$0.10-1.00 depending on Base gas price
- **Paid from:** Your wallet's ETH balance

### Verification

View transactions on Base block explorer:
```
https://basescan.org/address/0xba72eD392dB9d67813D68D562D2d67c36fFF566b
```

---

## File Structure

```
/home/hshadab/x402insurance/
├── server.py                   # Main Flask application
├── zkengine_client.py         # zkEngine proof generation
├── blockchain.py              # USDC refund execution
├── requirements.txt           # Python dependencies
├── .env                       # Configuration (DO NOT COMMIT!)
│
├── zkengine/
│   └── fraud_detector         # zkEngine binary (11MB)
│
├── data/
│   ├── policies.json          # Insurance policies
│   └── claims.json            # Fraud claims with proofs
│
├── setup_wallet.py            # Wallet configuration tool
├── test_zkengine.py           # zkEngine integration tests
│
└── PRODUCTION_README.md       # This file
```

---

## Security

### Private Keys

⚠️ **CRITICAL:** Never commit .env to git

Your private key is stored in `.env` - protect it!

### Network

🟢 **Base Mainnet** - Real money in production

### Audit Trail

All transactions visible on Base block explorer:
- Policy creation (x402 payment)
- USDC refunds (blockchain transaction)
- Proofs (downloadable JSON)

---

## Monitoring

### Check Wallet Balance

```bash
python -c "
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_RPC_URL')))
addr = os.getenv('BACKEND_WALLET_ADDRESS')

eth = w3.from_wei(w3.eth.get_balance(addr), 'ether')
print(f'ETH: {eth}')
"
```

### Check Server Health

```bash
curl http://localhost:8000/health
```

### View Logs

Server outputs to stdout. For production, redirect to file:

```bash
python server.py > server.log 2>&1 &
tail -f server.log
```

---

## Testing

### Test zkEngine

```bash
python test_zkengine.py
```

Expected output:
```
✅ Test 1: Fraud case (503) - Proof generated in 10s
✅ Test 2: Non-fraud (200) - Proof generated in 20s
✅ Test 3: Fraud case (empty) - Proof generated in 19s
```

### Test x402 Payment

```bash
curl -X POST http://localhost:8000/insure \
  -H "Content-Type: application/json" \
  -d '{"merchant_url": "https://api.test.com", "coverage_amount": 10000}'
```

Should return 402 Payment Required.

---

## Deployment

### Current: Local

Server runs on localhost:8000

### Production: Render.com

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "x402 insurance production"
   git push
   ```

2. **Deploy to Render:**
   - New Web Service
   - Connect repository
   - Set environment variables from .env
   - Deploy

**Cost:** $7-25/month

---

## Troubleshooting

### "Insufficient funds for gas"

**Cause:** No ETH in wallet

**Fix:** Send ETH to `0xba72eD392dB9d67813D68D562D2d67c36fFF566b`

### "Cannot connect to RPC"

**Cause:** Alchemy RPC issue

**Fix:** Check Alchemy dashboard, verify API key

### "zkEngine proof generation failed"

**Cause:** Binary not found or WASM missing

**Fix:**
```bash
ls zkengine/fraud_detector  # Should exist
ls /tmp/zkEngine_dev/wasm/fraud_detector.wat  # Should exist
```

### "USDC transfer failed"

**Cause:** Insufficient USDC balance

**Fix:** Send USDC to your wallet

---

## Performance Optimization

### Current Limitations

1. **Proof generation:** 10-20s blocks HTTP request
2. **JSON storage:** Not suitable for high volume
3. **Synchronous processing:** No background jobs

### Recommended Improvements

1. **Async proof generation:**
   - Use Celery + Redis
   - Return claim ID immediately
   - Generate proof in background
   - Webhook notification when ready

2. **Database:**
   - Migrate to PostgreSQL
   - Better query performance
   - ACID guarantees

3. **Caching:**
   - Redis for session data
   - Cache zkEngine setup parameters

---

## Support

**Wallet:** `0xba72eD392dB9d67813D68D562D2d67c36fFF566b`
**Network:** Base Mainnet (Chain ID: 8453)
**USDC Contract:** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

**Block Explorer:**
- https://basescan.org
- https://basescan.org/address/0xba72eD392dB9d67813D68D562D2d67c36fFF566b

---

## License

MIT

---

## Version History

**v1.0.0** (2025-11-06)
- ✅ x402 payment integration (Base Mainnet)
- ✅ zkEngine zero-knowledge proofs
- ✅ USDC refunds on Base Mainnet
- ✅ Public proof verification
- ✅ Production ready
