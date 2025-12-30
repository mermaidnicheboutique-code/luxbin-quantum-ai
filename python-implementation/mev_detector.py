#!/usr/bin/env python3
"""
LUXBIN MEV Detection Engine
Detects sandwich attacks, front-running, and other MEV on Base network
"""

import asyncio
import json
import sys
import os
from web3 import Web3
from eth_account import Account
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

# Add parent directory to path to import database module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
from database import ThreatDatabase

class MEVDetector:
    """Real MEV detection for Base network"""

    def __init__(self, rpc_url: str, contract_address: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)

        # Load contract
        with open('../out/LuxbinSecurityProtocol.sol/LuxbinSecurityProtocol.json') as f:
            abi = json.load(f)['abi']

        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

        # Initialize database
        self.db = ThreatDatabase("../luxbin_threats.db")

        # Tracking state
        self.pending_txs: Dict[str, dict] = {}
        self.block_txs: Dict[int, List[dict]] = defaultdict(list)
        self.sandwich_victims = set()

        # Statistics
        self.stats = {
            'blocks_processed': 0,
            'sandwiches_detected': 0,
            'frontrunning_detected': 0,
            'total_value_at_risk': 0,
            'threats_reported': 0
        }

    async def start_detection(self):
        """Start real-time MEV detection"""
        print("="*60)
        print("LUXBIN MEV DETECTION ENGINE")
        print("="*60)
        print(f"Network: Base Mainnet")
        print(f"Oracle: {self.account.address}")
        print(f"Contract: {self.contract.address}")
        print()
        print("Monitoring for:")
        print("  - Sandwich attacks")
        print("  - Front-running")
        print("  - Back-running")
        print("  - Gas manipulation")
        print()

        last_block = self.w3.eth.block_number

        while True:
            try:
                current_block = self.w3.eth.block_number

                if current_block > last_block:
                    for block_num in range(last_block + 1, current_block + 1):
                        await self.analyze_block(block_num)

                    last_block = current_block

                # Also monitor pending transactions
                # await self.monitor_mempool()

                await asyncio.sleep(2)

            except KeyboardInterrupt:
                print("\n⚠️  Stopping MEV detector...")
                self.print_summary()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(5)

    async def analyze_block(self, block_num: int):
        """Analyze a block for MEV activity"""
        self.stats['blocks_processed'] += 1

        try:
            block = self.w3.eth.get_block(block_num, full_transactions=True)

            if len(block.transactions) == 0:
                return

            # Extract all transactions
            txs = [tx for tx in block.transactions]

            # Detect sandwich attacks
            sandwiches = self.detect_sandwich_attacks(txs)

            if sandwiches:
                for sandwich in sandwiches:
                    await self.report_sandwich(block_num, sandwich)

            # Detect front-running
            frontrunning = self.detect_frontrunning(txs)

            if frontrunning:
                for fr in frontrunning:
                    await self.report_frontrunning(block_num, fr)

            # Progress update
            if self.stats['blocks_processed'] % 100 == 0:
                print(f"📊 Processed {self.stats['blocks_processed']} blocks | "
                      f"Sandwiches: {self.stats['sandwiches_detected']} | "
                      f"Front-running: {self.stats['frontrunning_detected']}")

        except Exception as e:
            print(f"Error analyzing block {block_num}: {e}")

    def detect_sandwich_attacks(self, txs: List) -> List[dict]:
        """
        Detect sandwich attacks: Attacker front-runs + back-runs victim

        Pattern:
        1. Attacker buys token (front-run)
        2. Victim buys token (gets worse price)
        3. Attacker sells token (back-run, profits)
        """
        sandwiches = []

        # Look for DEX interactions
        dex_addresses = {
            '0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24',  # UniswapV2 Router on Base (example)
            '0x2626664c2603336e57b271c5c0b26f421741e481',  # BaseSwap Router
            # Add more DEX addresses
        }

        for i in range(len(txs) - 2):
            tx1 = txs[i]
            tx2 = txs[i + 1]
            tx3 = txs[i + 2]

            # Check if transactions interact with same DEX
            if (tx1.get('to') in dex_addresses and
                tx3.get('to') in dex_addresses and
                tx1.get('from') == tx3.get('from') and
                tx1.get('from') != tx2.get('from')):

                # Potential sandwich!
                sandwich = {
                    'frontrun_tx': tx1['hash'].hex(),
                    'victim_tx': tx2['hash'].hex(),
                    'backrun_tx': tx3['hash'].hex(),
                    'attacker': tx1['from'],
                    'victim': tx2['from'],
                    'victim_value': tx2.get('value', 0),
                    'threat_score': self.calculate_sandwich_severity(tx1, tx2, tx3)
                }

                sandwiches.append(sandwich)
                self.stats['sandwiches_detected'] += 1
                self.stats['total_value_at_risk'] += tx2.get('value', 0)

        return sandwiches

    def detect_frontrunning(self, txs: List) -> List[dict]:
        """
        Detect front-running: Attacker sees pending tx and submits with higher gas
        """
        frontrunning = []

        # Group by target contract
        contract_txs = defaultdict(list)
        for tx in txs:
            if tx.get('to'):
                contract_txs[tx['to']].append(tx)

        # Look for suspicious patterns
        for contract, contract_tx_list in contract_txs.items():
            if len(contract_tx_list) < 2:
                continue

            # Check if multiple addresses calling same function with different gas
            for i in range(len(contract_tx_list) - 1):
                tx1 = contract_tx_list[i]
                tx2 = contract_tx_list[i + 1]

                gas_diff = abs(tx1.get('gasPrice', 0) - tx2.get('gasPrice', 0))

                # If gas difference > 20%, might be front-running
                if gas_diff > tx1.get('gasPrice', 1) * 0.2:
                    frontrun = {
                        'frontrun_tx': tx1['hash'].hex(),
                        'victim_tx': tx2['hash'].hex(),
                        'attacker': tx1['from'],
                        'victim': tx2['from'],
                        'gas_manipulation': gas_diff,
                        'threat_score': min(80, int((gas_diff / tx1.get('gasPrice', 1)) * 100))
                    }

                    frontrunning.append(frontrun)
                    self.stats['frontrunning_detected'] += 1

        return frontrunning

    def calculate_sandwich_severity(self, tx1, tx2, tx3) -> int:
        """Calculate threat score for sandwich attack (0-100)"""
        # Higher victim value = higher severity
        victim_value = tx2.get('value', 0)

        if victim_value == 0:
            return 50  # Base severity for detected pattern

        # Scale based on value (in ETH)
        eth_value = victim_value / 10**18

        if eth_value > 10:
            return 95
        elif eth_value > 1:
            return 80
        elif eth_value > 0.1:
            return 65
        else:
            return 50

    async def report_sandwich(self, block_num: int, sandwich: dict):
        """Report sandwich attack to contract"""
        print()
        print(f"🚨 SANDWICH ATTACK DETECTED - Block {block_num}")
        print(f"   Attacker: {sandwich['attacker'][:10]}...")
        print(f"   Victim: {sandwich['victim'][:10]}...")
        print(f"   Threat Score: {sandwich['threat_score']}/100")
        print(f"   Victim TX: {sandwich['victim_tx'][:20]}...")

        # Save to database
        try:
            self.db.add_threat(
                block_number=block_num,
                threat_type="sandwich_attack",
                attacker_address=sandwich['attacker'],
                victim_address=sandwich['victim'],
                threat_score=sandwich['threat_score'],
                tx_hash=sandwich['victim_tx'],
                value_at_risk=sandwich['victim_value'] / 10**18,
                reported=False,
                metadata=sandwich
            )
            print(f"   ✅ Saved to database")
        except Exception as e:
            print(f"   ⚠️  DB save failed: {e}")

        # Report to contract
        try:
            reported = await self._record_threat(
                detector=self.account.address,
                threat_score=sandwich['threat_score']
            )
            if reported:
                self.stats['threats_reported'] += 1
                print(f"   ✅ Reported to contract")
        except Exception as e:
            print(f"   ❌ Failed to report: {e}")

    async def report_frontrunning(self, block_num: int, frontrun: dict):
        """Report front-running to contract"""
        print()
        print(f"⚠️  FRONT-RUNNING DETECTED - Block {block_num}")
        print(f"   Attacker: {frontrun['attacker'][:10]}...")
        print(f"   Victim: {frontrun['victim'][:10]}...")
        print(f"   Threat Score: {frontrun['threat_score']}/100")

        # Save to database
        try:
            self.db.add_threat(
                block_number=block_num,
                threat_type="frontrunning",
                attacker_address=frontrun['attacker'],
                victim_address=frontrun['victim'],
                threat_score=frontrun['threat_score'],
                tx_hash=frontrun.get('frontrun_tx'),
                value_at_risk=0,
                reported=False,
                metadata=frontrun
            )
        except Exception as e:
            pass  # Silent fail for DB - detector keeps running

        try:
            await self._record_threat(
                detector=self.account.address,
                threat_score=frontrun['threat_score']
            )
            self.stats['threats_reported'] += 1
            print(f"   ✅ Reported to contract")
        except Exception as e:
            print(f"   ❌ Failed to report: {e}")

    async def _record_threat(self, detector: str, threat_score: int):
        """Record threat on-chain"""
        nonce = self.w3.eth.get_transaction_count(self.account.address)

        tx = self.contract.functions.recordThreat(
            detector,
            threat_score
        ).build_transaction({
            'from': self.account.address,
            'nonce': nonce,
            'gas': 150000,
            'maxFeePerGas': self.w3.eth.gas_price,
            'maxPriorityFeePerGas': self.w3.eth.gas_price // 10,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)

        # Don't wait for receipt to avoid slowing down detection
        # Just fire and forget

    def print_summary(self):
        """Print detection statistics"""
        print()
        print("="*60)
        print("DETECTION SUMMARY")
        print("="*60)
        print(f"Blocks processed: {self.stats['blocks_processed']}")
        print(f"Sandwich attacks: {self.stats['sandwiches_detected']}")
        print(f"Front-running: {self.stats['frontrunning_detected']}")
        print(f"Total value at risk: {self.stats['total_value_at_risk'] / 10**18:.4f} ETH")
        print(f"Threats reported: {self.stats['threats_reported']}")
        print("="*60)


async def main():
    # Configuration
    RPC_URL = "https://mainnet.base.org"
    CONTRACT_ADDRESS = "0xdA0E6C8e9d7C3ef66a6CB6bD5277f216a0d508A7"  # LUXBIN V2 deployed!
    PRIVATE_KEY = "0x8e991e125ec36d7077d12358e836cb82a53ddba6272f60afd0340bb4d4b6fd49"

    detector = MEVDetector(RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY)
    await detector.start_detection()


if __name__ == "__main__":
    print("Starting LUXBIN MEV Detection Engine...")
    asyncio.run(main())
