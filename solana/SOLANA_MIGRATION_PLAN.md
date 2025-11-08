# Solana x402 Hackathon Submission Plan

## Project: x402 Insurance on Solana

**Goal:** Migrate x402 Insurance from Base to Solana for hackathon submission

**Status:** Planning Phase
**Created:** 2025-11-08

---

## 1. Hackathon Research

### Key Requirements (TO BE FILLED)
- Submission deadline: TBD
- Prize categories: TBD
- Judging criteria: TBD
- Required deliverables: TBD

---

## 2. Technical Migration Overview

### Current Stack (Base)
- Network: Base Mainnet
- Token: USDC (0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913)
- Smart Contract Language: Solidity (EVM)
- RPC: Alchemy Base RPC
- Payment Protocol: x402 with EIP-712 signatures
- ZKP Engine: zkEngine (Nova/Arecibo SNARKs)

### Target Stack (Solana)
- Network: Solana Mainnet / Devnet
- Token: USDC (EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)
- Smart Contract Language: Rust (Solana programs)
- RPC: Solana RPC / Helius / QuickNode
- Payment Protocol: x402 with Solana signatures
- ZKP Engine: zkEngine (compatible with Solana)

---

## 3. Migration Scope

### 3.1 Blockchain Layer
**Current:** `blockchain.py` (Web3.py for EVM)
**New:** `solana/blockchain_solana.py`

Changes needed:
- [ ] Replace Web3.py with solana-py
- [ ] Implement Solana wallet management (Keypair)
- [ ] USDC transfers using SPL Token program
- [ ] Transaction signing with ed25519
- [ ] RPC connection to Solana cluster

### 3.2 Payment Verification
**Current:** `payment_verifier.py` (EIP-712 signatures)
**New:** `solana/payment_verifier_solana.py`

Changes needed:
- [ ] Replace EIP-712 with Solana signature verification
- [ ] Verify ed25519 signatures
- [ ] Adapt x402 payment flow for Solana
- [ ] Handle Solana transaction structure

### 3.3 Smart Contract (Optional)
**Current:** None (Python-based refunds)
**New:** `solana/programs/insurance/` (Rust)

Options:
- [ ] Option A: Keep Python backend (simpler, faster)
- [ ] Option B: Write Anchor program for on-chain logic (more native)

### 3.4 Configuration
**Current:** `.env` with Base RPC
**New:** `solana/.env.solana`

Changes needed:
- [ ] SOLANA_RPC_URL
- [ ] SOLANA_CLUSTER (mainnet-beta / devnet)
- [ ] USDC_MINT_ADDRESS (Solana USDC)
- [ ] WALLET_KEYPAIR_PATH

---

## 4. Implementation Plan

### Phase 1: Setup & Research (Day 1)
- [ ] Research Solana x402 implementation examples
- [ ] Install solana-py, anchorpy dependencies
- [ ] Set up Solana devnet wallet
- [ ] Get devnet USDC from faucet
- [ ] Test basic Solana transactions

### Phase 2: Core Migration (Days 2-3)
- [ ] Implement `blockchain_solana.py`
  - Wallet connection
  - USDC balance check
  - SPL token transfer
- [ ] Implement `payment_verifier_solana.py`
  - Solana signature verification
  - x402 payment validation
- [ ] Update `server.py` to support both Base and Solana
  - Add network parameter to endpoints
  - Dual blockchain support

### Phase 3: Testing (Day 4)
- [ ] Test policy creation on Solana devnet
- [ ] Test claim submission with Solana signatures
- [ ] Test USDC refunds on Solana
- [ ] End-to-end integration test
- [ ] Performance benchmarking (Solana vs Base)

### Phase 4: Documentation (Day 5)
- [ ] Update README with Solana instructions
- [ ] Create Solana quickstart guide
- [ ] Record demo video showing Solana workflow
- [ ] Update agent card for Solana support

### Phase 5: Submission (Day 6)
- [ ] Deploy to Solana devnet/mainnet
- [ ] Create hackathon submission
- [ ] Write project description
- [ ] Submit demo video
- [ ] Social media announcement

---

## 5. File Structure

```
solana/
├── SOLANA_MIGRATION_PLAN.md          # This file
├── README.md                         # Solana-specific docs
├── .env.solana                       # Solana configuration
├── blockchain_solana.py              # Solana blockchain client
├── payment_verifier_solana.py        # Solana payment verification
├── server_solana.py                  # Solana-enabled Flask server
├── tests/
│   ├── test_blockchain_solana.py
│   ├── test_payment_solana.py
│   └── test_e2e_solana.py
├── scripts/
│   ├── setup_solana_wallet.py       # Wallet creation helper
│   ├── fund_devnet.py               # Get devnet USDC
│   └── deploy_solana.sh             # Deployment script
├── examples/
│   ├── agent_buy_policy_solana.py   # Example: Buy insurance
│   └── agent_claim_solana.py        # Example: File claim
└── programs/                         # Optional: Rust smart contracts
    └── insurance/
        ├── Cargo.toml
        └── src/
            └── lib.rs
```

---

## 6. Key Differences: Base vs Solana

| Feature | Base (EVM) | Solana |
|---------|-----------|--------|
| **Transaction Speed** | 2-5 seconds | 400ms |
| **Gas Fees** | ~$0.0001 | ~$0.00005 |
| **Signature Scheme** | EIP-712 (secp256k1) | ed25519 |
| **USDC Contract** | ERC20 | SPL Token |
| **Account Model** | Account-based | Account-based (with rent) |
| **Smart Contracts** | Solidity | Rust (Anchor) |
| **Library** | Web3.py | solana-py |

---

## 7. Advantages for Hackathon

### Why Solana is Better for Insurance:
1. **Faster Refunds** - 400ms finality vs 2-5s on Base
2. **Cheaper Operations** - Lower gas = more profitable for small claims
3. **Higher Throughput** - Can handle more simultaneous claims
4. **Native x402 Support** - Solana is a primary x402 network
5. **Innovation Points** - zkEngine on Solana is novel

### Hackathon Pitch:
> "The first zero-knowledge proof insurance for x402 micropayments on Solana. Instant refunds in 400ms with cryptographically verified fraud detection. Agents pay 1% premium, get 100% protection against merchant failures."

---

## 8. Risk Mitigation

### Challenges & Solutions:

**Challenge 1:** zkEngine compatibility with Solana
- **Solution:** zkEngine is chain-agnostic (generates proofs off-chain)
- **Fallback:** Use same zkEngine, just change refund mechanism

**Challenge 2:** Solana account rent
- **Solution:** Insurance wallet maintains rent-exempt balance
- **Impact:** ~0.002 SOL per policy storage account

**Challenge 3:** Time constraints
- **Solution:** Minimal viable migration (Python backend only, no Rust contracts)
- **Scope:** Focus on payment + refund, reuse existing zkEngine

**Challenge 4:** Testing on mainnet
- **Solution:** Deploy to Solana devnet first, document thoroughly
- **Showcase:** Emphasize devnet testing is sufficient for hackathon

---

## 9. Success Metrics

### Minimum Viable Submission:
- [ ] Working demo on Solana devnet
- [ ] End-to-end policy purchase + claim flow
- [ ] USDC refunds processed successfully
- [ ] Documentation showing Solana integration
- [ ] 3-minute demo video

### Ideal Submission:
- [ ] Everything above +
- [ ] Deployed on Solana mainnet
- [ ] Rust Anchor program for on-chain verification
- [ ] Performance comparison (Base vs Solana)
- [ ] Agent SDK with Solana support
- [ ] Live working demo agents can test

---

## 10. Budget & Resources

### Costs:
- Solana devnet: FREE (faucet)
- Solana mainnet: ~$100-500 USDC + 0.1 SOL for testing
- RPC provider: FREE (public RPC) or $50/month (Helius/QuickNode)
- Domain/hosting: Already covered

### Development Time:
- Minimal path: 3-4 days (Python backend only)
- Full migration: 7-10 days (with Rust program)

### Recommendation:
**Go with minimal path** - Faster to market, proven zkEngine, focus on unique value prop

---

## 11. Next Steps

### Immediate Actions:
1. [ ] Read hackathon rules and deadlines
2. [ ] Set up Solana development environment
3. [ ] Create Solana devnet wallet
4. [ ] Test basic Solana transaction
5. [ ] Start implementing `blockchain_solana.py`

### Questions to Answer:
- What is the hackathon deadline?
- Are there specific prize categories we should target?
- Do judges prefer devnet or mainnet deployments?
- Are Rust smart contracts required or optional?
- What demo format do they want (video/live/slides)?

---

## 12. Competitive Advantages

### What Makes This Unique:
1. **First zkp-based insurance on Solana**
2. **Solves real problem** - Agents lose money to merchant failures
3. **Production-ready** - Already works on Base (proven)
4. **Instant payouts** - 400ms on Solana (vs 15-30s proof generation)
5. **Agent-native** - Built for autonomous agents, not humans
6. **x402-compliant** - Perfect fit for x402 hackathon theme

### Target Judging Criteria:
- Innovation: zkEngine + insurance = novel combination
- Technical Quality: Production code, comprehensive tests
- Practical Value: Solves actual agent pain point
- x402 Integration: Deep x402 protocol usage
- Solana-Native: Leverages Solana speed advantages

---

**Status:** Plan created, awaiting hackathon details
**Next Update:** After researching hackathon requirements
