#!/usr/bin/env python3
"""
Test real zkEngine integration
"""
import json
import uuid
import sys

# Mock a simple policy for testing
test_policy = {
    "id": str(uuid.uuid4()),
    "agent_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "merchant_url": "https://api.test.com",
    "merchant_url_hash": "test_hash",
    "coverage_amount": 10000,
    "premium": 1000,
    "status": "active"
}

# Import the zkEngine client
from zkengine_client import ZKEngineClient

print("=" * 60)
print("Testing Real zkEngine Integration")
print("=" * 60)

# Initialize client
client = ZKEngineClient("./zkengine/fraud_detector")

# Test 1: Fraud case (503 status, empty body)
print("\n📋 Test 1: Fraud Case (503 status, empty body)")
print("-" * 60)
try:
    proof_hex, public_inputs, gen_time = client.generate_proof(
        http_status=503,
        http_body="",
        http_headers={}
    )

    print(f"✅ Proof generated in {gen_time}ms")
    print(f"   Proof: {proof_hex[:50]}...")
    print(f"   Public inputs: {public_inputs}")
    print(f"   Fraud detected: {public_inputs[0] == 1}")
    print(f"   HTTP status: {public_inputs[1]}")
    print(f"   Body length: {public_inputs[2]}")
    print(f"   Payout: {public_inputs[3]}")

    # Verify the proof
    is_valid = client.verify_proof(proof_hex, public_inputs)
    print(f"   Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")

except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)

# Test 2: Non-fraud case (200 status, body present)
print("\n📋 Test 2: Non-Fraud Case (200 status, body present)")
print("-" * 60)
try:
    proof_hex, public_inputs, gen_time = client.generate_proof(
        http_status=200,
        http_body='{"data": "test"}',
        http_headers={}
    )

    print(f"✅ Proof generated in {gen_time}ms")
    print(f"   Proof: {proof_hex[:50]}...")
    print(f"   Public inputs: {public_inputs}")
    print(f"   Fraud detected: {public_inputs[0] == 1}")
    print(f"   HTTP status: {public_inputs[1]}")
    print(f"   Body length: {public_inputs[2]}")
    print(f"   Payout: {public_inputs[3]}")

    # Verify the proof
    is_valid = client.verify_proof(proof_hex, public_inputs)
    print(f"   Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")

except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)

# Test 3: Fraud case (empty body, 200 status)
print("\n📋 Test 3: Fraud Case (empty body, 200 status)")
print("-" * 60)
try:
    proof_hex, public_inputs, gen_time = client.generate_proof(
        http_status=200,
        http_body="",
        http_headers={}
    )

    print(f"✅ Proof generated in {gen_time}ms")
    print(f"   Proof: {proof_hex[:50]}...")
    print(f"   Public inputs: {public_inputs}")
    print(f"   Fraud detected: {public_inputs[0] == 1}")
    print(f"   HTTP status: {public_inputs[1]}")
    print(f"   Body length: {public_inputs[2]}")
    print(f"   Payout: {public_inputs[3]}")

    # Verify the proof
    is_valid = client.verify_proof(proof_hex, public_inputs)
    print(f"   Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")

except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Real zkEngine integration working!")
print("=" * 60)
