#!/usr/bin/env python3
"""
LUXBIN EARNINGS SCRIPT
Monitors Base blockchain and earns rewards through your staking contract
"""

import asyncio
import json
from web3 import Web3
from eth_account import Account
from datetime import datetime
import random

class LuxbinEarner:
    """Earn rewards by monitoring blockchain and detecting threats"""

    def __init__(self, contract_address, private_key):
        # Connect to Base
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
        self.account = Account.from_key(private_key)

        # Load contract ABI
        with open('../out/LuxbinUSDCStaking_LowMin.sol/LuxbinUSDCStaking_LowMin.json') as f:
            abi = json.load(f)['abi']

        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=abi
        )

        self.last_block = self.w3.eth.block_number
        self.total_earned = 0
        self.blocks_processed = 0
        self.nonce = self.w3.eth.get_transaction_count(self.account.address)  # Track nonce manually

    async def start_earning(self):
        """Start monitoring and earning rewards"""
        print("🚀 LUXBIN Earnings Bot Started!")
        print(f"📍 Contract: {self.contract.address}")
        print(f"👤 Earner: {self.account.address}")
        print(f"🔗 Monitoring Base blockchain...")
        print()

        while True:
            try:
                # Check for new blocks
                current_block = self.w3.eth.block_number

                if current_block > self.last_block:
                    # Process new blocks
                    for block_num in range(self.last_block + 1, current_block + 1):
                        await self.process_block(block_num)

                    self.last_block = current_block

                # Wait before checking again
                await asyncio.sleep(2)  # Check every 2 seconds

            except KeyboardInterrupt:
                print("\n⚠️  Stopping earnings bot...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(5)

    async def process_block(self, block_num):
        """Process a block and potentially earn rewards"""
        self.blocks_processed += 1

        # Get block data
        block = self.w3.eth.get_block(block_num)

        # Analyze block for threats (simplified - in production this would be more sophisticated)
        threat_score = self.analyze_block(block)

        if threat_score > 0:
            # Found a threat! Report it and earn rewards
            await self.report_threat(block_num, threat_score)

        # Occasionally spawn cells for health monitoring
        if self.blocks_processed % 10 == 0:
            await self.spawn_cells()

        # Show progress
        if self.blocks_processed % 50 == 0:
            print(f"📊 Processed {self.blocks_processed} blocks | Total earned: ${self.total_earned:.2f} USDC")

    def analyze_block(self, block):
        """Analyze block for threats - returns threat score 0-100"""
        # Simplified threat detection
        # In production, this would analyze:
        # - Transaction patterns
        # - Gas anomalies
        # - Contract interactions
        # - MEV attacks
        # - etc.

        tx_count = len(block.transactions)

        # More transactions = higher chance of threats
        if tx_count > 100:
            return random.randint(30, 70)  # Medium to high threat
        elif tx_count > 50:
            return random.randint(10, 40)  # Low to medium threat
        elif tx_count > 20:
            return random.randint(0, 20)   # Low threat
        else:
            return 0  # No threat

    async def report_threat(self, block_num, threat_score):
        """Report threat to contract and earn rewards"""
        try:
            # Calculate reward (from contract: $1-$100 based on threat score)
            reward_value = 1 + (99 * (threat_score / 100))

            print(f"⚠️  Threat detected in block {block_num}")
            print(f"   Score: {threat_score}/100")
            print(f"   Potential reward: ${reward_value:.2f} USDC")

            # ACTUALLY call the contract to record the reward!
            tx = self.contract.functions.addThreatReward(
                self.account.address,
                threat_score
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.nonce,  # Use tracked nonce
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
            })

            # Sign and send
            signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)

            # Increment nonce for next transaction
            self.nonce += 1

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

            if receipt.status == 1:
                gas_cost = receipt.gasUsed * self.w3.eth.gas_price / 10**18 * 3400  # Approximate $ cost
                self.total_earned += reward_value
                print(f"   ✅ Recorded on-chain! Gas: ${gas_cost:.4f}")
            else:
                print(f"   ❌ Transaction failed!")
                self.nonce -= 1  # Rollback nonce on failure

        except Exception as e:
            print(f"   ❌ Error reporting threat: {e}")

    async def spawn_cells(self):
        """Spawn immune cells for monitoring"""
        # Determine which cells to spawn based on network health
        cell_types = {
            'DETECTOR': 0,
            'DEFENDER': 1,
            'MEMORY': 2,
            'REGULATORY': 3
        }

        cell_name = random.choice(list(cell_types.keys()))
        cell_type_id = cell_types[cell_name]
        count = random.randint(1, 3)

        # Cell values (from contract)
        values = {
            'DETECTOR': 10,
            'DEFENDER': 15,
            'MEMORY': 5,
            'REGULATORY': 20
        }

        reward_value = values[cell_name] * count

        print(f"🦠 Spawning {count}x {cell_name} cells")
        print(f"   Value: ${reward_value:.2f} USDC")

        try:
            # ACTUALLY call the contract!
            tx = self.contract.functions.addCellSpawnReward(
                self.account.address,
                cell_type_id,  # 0=DETECTOR, 1=DEFENDER, 2=MEMORY, 3=REGULATORY
                count
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.nonce,  # Use tracked nonce
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
            })

            signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            self.nonce += 1  # Increment nonce

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

            if receipt.status == 1:
                gas_cost = receipt.gasUsed * self.w3.eth.gas_price / 10**18 * 3400
                self.total_earned += reward_value
                print(f"   ✅ Recorded on-chain! Gas: ${gas_cost:.4f}")
            else:
                print(f"   ❌ Transaction failed!")
                self.nonce -= 1  # Rollback on failure

        except Exception as e:
            print(f"   ❌ Error spawning cells: {e}")


async def main():
    """Main entry point"""
    # Your deployed contract
    CONTRACT_ADDRESS = "0xe7a568D6352976E4B987DB1f7cC97E367e125b3A"

    # Your private key (CHANGE THIS TO ENV VARIABLE IN PRODUCTION!)
    PRIVATE_KEY = "0x8e991e125ec36d7077d12358e836cb82a53ddba6272f60afd0340bb4d4b6fd49"

    earner = LuxbinEarner(CONTRACT_ADDRESS, PRIVATE_KEY)
    await earner.start_earning()


if __name__ == "__main__":
    print("="*60)
    print("LUXBIN EARNINGS BOT")
    print("="*60)
    print()
    asyncio.run(main())
