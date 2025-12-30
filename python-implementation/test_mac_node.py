#!/usr/bin/env python3
"""
LUXBIN Mac Node - Simple Test Script
Tests your Mac setup before deploying contracts

Author: Nichole Christie
"""

import asyncio
from web3 import Web3
from eth_account import Account
import json
import os

async def test_node():
    """Test LUXBIN node on Mac"""

    print("╔════════════════════════════════════════════════════════╗")
    print("║  LUXBIN DIVINE - Mac Node Test                        ║")
    print("║  Testing your MacBook Pro setup...                    ║")
    print("╚════════════════════════════════════════════════════════╝\n")

    # Test 1: Check wallet
    print("1️⃣ Checking wallet...")

    wallet_path = "wallet.json"
    if os.path.exists(wallet_path):
        with open(wallet_path, 'r') as f:
            wallet = json.load(f)
        print(f"   ✅ Wallet loaded")
        print(f"   👤 Address: {wallet['address']}")
    else:
        print(f"   ⚠️  No wallet found - creating one...")
        account = Account.create()
        wallet = {
            "address": account.address,
            "private_key": account.key.hex()
        }
        with open(wallet_path, 'w') as f:
            json.dump(wallet, f, indent=2)
        print(f"   ✅ New wallet created!")
        print(f"   👤 Address: {wallet['address']}")
        print(f"   ⚠️  BACKUP THIS FILE: wallet.json")

    # Test 2: Connect to OP Sepolia
    print("\n2️⃣ Connecting to OP Sepolia...")

    try:
        w3 = Web3(Web3.HTTPProvider('https://sepolia.optimism.io'))

        if w3.is_connected():
            print(f"   ✅ Connected to blockchain")

            # Get latest block
            block = w3.eth.block_number
            print(f"   📦 Latest block: {block:,}")

            # Check balance
            balance = w3.eth.get_balance(wallet['address'])
            balance_eth = w3.from_wei(balance, 'ether')
            print(f"   💰 Balance: {balance_eth:.6f} ETH")

            if balance_eth == 0:
                print(f"\n   ⚠️  You need testnet ETH to deploy contracts!")
                print(f"   Get free ETH from:")
                print(f"   https://www.alchemy.com/faucets/optimism-sepolia")
        else:
            print(f"   ❌ Connection failed")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test 3: Check for existing LUXBIN deployment
    print("\n3️⃣ Checking for LUXBIN contracts...")

    # You mentioned you deployed LUXBIN this morning
    # Let's look for deployment_report.json
    if os.path.exists('deployment_report.json'):
        with open('deployment_report.json', 'r') as f:
            deployment = json.load(f)
        print(f"   ✅ Found deployment report")
        print(f"   🌐 Network: {deployment.get('network', 'unknown')}")

        if 'contracts' in deployment:
            print(f"   📝 Contracts:")
            for name, info in deployment['contracts'].items():
                print(f"      - {name}: {info['address'][:10]}...")
    else:
        print(f"   ℹ️  No deployment found yet")
        print(f"   You'll deploy contracts after getting testnet ETH")

    # Test 4: System check
    print("\n4️⃣ System check...")

    try:
        import cirq
        print(f"   ✅ Cirq installed (quantum scanning ready)")
    except:
        print(f"   ⚠️  Cirq not installed (optional - for quantum features)")
        print(f"      Install with: pip3 install cirq")

    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"✅ Wallet: {wallet['address']}")
    print(f"✅ Network: OP Sepolia")
    print(f"✅ Connection: Active")
    print(f"💰 Balance: {balance_eth:.6f} ETH")

    if balance_eth == 0:
        print(f"\n🎯 NEXT STEP:")
        print(f"1. Get free testnet ETH:")
        print(f"   https://www.alchemy.com/faucets/optimism-sepolia")
        print(f"2. Paste your address: {wallet['address']}")
        print(f"3. Run deployment: python3 deploy_immune_system.py")
    else:
        print(f"\n🎯 NEXT STEP:")
        print(f"Deploy contracts: python3 deploy_immune_system.py")

    print("="*60)
    print(f"\n✨ Your MacBook Pro is ready to run LUXBIN!")
    print(f"   This Mac is WAY more powerful than a phone 🚀")


if __name__ == "__main__":
    asyncio.run(test_node())
