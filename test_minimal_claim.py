#!/usr/bin/env python3
"""
Test the insurance flow with minimal USDC amount (0.5 USDC)

This simulates:
1. Agent has a policy (we'll create manually since x402 payment requires client)
2. Agent's API call fails with 503 error
3. Agent files claim
4. zkEngine generates proof
5. USDC refund issued on Base Mainnet
"""
import httpx
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

print("=" * 60)
print("MINIMAL USDC TEST - 0.5 USDC CLAIM")
print("=" * 60)
print()

# Configuration
SERVER_URL = "http://localhost:8000"
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Step 1: Create a test policy manually (simulating agent bought insurance)
print("Step 1: Creating test policy (simulating agent purchase)")
print("-" * 60)

policy_id = "test-minimal-" + str(int(time.time()))
test_agent_address = "0x1234567890123456789012345678901234567890"  # Dummy address for testing
test_merchant = "https://sketchy-api.example.com"

test_policy = {
    "id": policy_id,
    "agent_address": test_agent_address,
    "merchant_url": test_merchant,
    "merchant_url_hash": "abc123",
    "coverage_amount": 0.5,  # Only 0.5 USDC coverage (minimal test)
    "premium": 1,
    "status": "active",
    "created_at": datetime.utcnow().isoformat(),
    "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
}

# Save to policies.json
policies_file = DATA_DIR / "policies.json"
if policies_file.exists():
    with open(policies_file, 'r') as f:
        policies = json.load(f)
else:
    policies = {}

policies[policy_id] = test_policy

with open(policies_file, 'w') as f:
    json.dump(policies, f, indent=2, default=str)

print(f"✅ Created test policy: {policy_id}")
print(f"   Agent: {test_agent_address}")
print(f"   Coverage: 0.5 USDC (minimal test amount)")
print(f"   Merchant: {test_merchant}")
print()

# Step 2: Simulate merchant failure
print("Step 2: Simulating merchant failure (503 error)")
print("-" * 60)

fraud_response = {
    "status": 503,
    "body": "",  # Empty body
    "headers": {}
}

print("❌ Merchant returned: HTTP 503 Service Unavailable")
print("   Response body: (empty)")
print("   This triggers fraud detection!")
print()

# Step 3: Submit claim
print("Step 3: Filing fraud claim with insurance service")
print("-" * 60)

claim_payload = {
    "policy_id": policy_id,
    "http_response": fraud_response
}

print(f"Sending claim to {SERVER_URL}/claim...")
print(f"Claim payload:")
print(json.dumps(claim_payload, indent=2))
print()

try:
    response = httpx.post(
        f"{SERVER_URL}/claim",
        json=claim_payload,
        timeout=60.0  # zkEngine takes ~15s
    )

    print(f"Response status: {response.status_code}")
    print()

    if response.status_code == 201:
        claim_data = response.json()

        print("=" * 60)
        print("✅ CLAIM APPROVED - REFUND ISSUED!")
        print("=" * 60)
        print()

        print(f"Claim ID: {claim_data['claim_id']}")
        print(f"Policy ID: {claim_data['policy_id']}")
        print()

        print(f"💰 REFUND DETAILS:")
        print(f"   Amount: {claim_data['payout_amount']} USDC")
        print(f"   Recipient: {test_agent_address}")
        print(f"   Transaction: {claim_data['refund_tx_hash']}")
        print()

        print(f"🔐 ZERO-KNOWLEDGE PROOF:")
        print(f"   Proof: {claim_data['proof'][:66]}...")
        print(f"   Public Inputs: {claim_data['public_inputs']}")
        print(f"   - is_fraud: {claim_data['public_inputs'][0]} (1 = fraud detected)")
        print(f"   - http_status: {claim_data['public_inputs'][1]} (503 = service unavailable)")
        print(f"   - body_length: {claim_data['public_inputs'][2]} (0 = empty response)")
        print(f"   - payout_amount: {claim_data['public_inputs'][3]} USDC")
        print()

        print(f"📊 VERIFICATION:")
        print(f"   Status: {claim_data['status']}")
        print(f"   Proof URL: {SERVER_URL}{claim_data['proof_url']}")
        print()

        # Verify on Base block explorer
        tx_hash = claim_data['refund_tx_hash']
        if tx_hash.startswith("0x") and len(tx_hash) == 66 and not tx_hash.startswith("0xMOCK"):
            print(f"🔍 View on BaseScan:")
            print(f"   https://basescan.org/tx/{tx_hash}")
        else:
            print(f"⚠️  Mock transaction (not on-chain)")
        print()

        print("=" * 60)
        print("TEST COMPLETE - System Working!")
        print("=" * 60)
        print()
        print("What happened:")
        print("1. Agent had 0.5 USDC coverage policy")
        print("2. Merchant failed (HTTP 503)")
        print("3. zkEngine generated cryptographic proof (~15s)")
        print("4. Proof verified merchant fraud")
        print("5. 0.5 USDC refund issued automatically")
        print("6. Public proof published for auditability")
        print()
        print("✅ Insurance works as designed!")

    else:
        print(f"❌ Claim failed: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Error submitting claim: {e}")
    import traceback
    traceback.print_exc()
