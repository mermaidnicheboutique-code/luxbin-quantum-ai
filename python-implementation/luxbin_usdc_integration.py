#!/usr/bin/env python3
"""
LUXBIN USDC INTEGRATION
Adds real USDC value to LUXBIN immune cells and blockchain activities

Tokenomics:
- DETECTOR cells: 10 USDC each
- DEFENDER cells: 15 USDC each
- MEMORY cells: 5 USDC each
- REGULATORY cells: 20 USDC each
- Threat detection rewards: 1-100 USDC based on threat score
- Block mirroring rewards: 0.1 USDC per block
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from web3 import Web3
from web3.contract import Contract

# USDC Contract Addresses (Circle's official USDC)
USDC_ADDRESSES = {
    "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "optimism": "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
    "arbitrum": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
    "polygon": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "avalanche": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
}

# RPC Endpoints
RPC_ENDPOINTS = {
    "ethereum": "https://eth.llamarpc.com",
    "optimism": "https://mainnet.optimism.io",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "polygon": "https://polygon-rpc.com",
    "base": "https://mainnet.base.org",
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
}

# USDC has 6 decimals (not 18 like most tokens)
USDC_DECIMALS = 6

class LuxbinTokenomics:
    """LUXBIN Tokenomics - USDC values for all activities"""

    # Cell values in USDC
    CELL_VALUES = {
        "DETECTOR": Decimal("10.00"),      # $10 per detector cell
        "DEFENDER": Decimal("15.00"),      # $15 per defender cell
        "MEMORY": Decimal("5.00"),         # $5 per memory cell
        "REGULATORY": Decimal("20.00"),    # $20 per regulatory cell
    }

    # Activity rewards in USDC
    BLOCK_MIRROR_REWARD = Decimal("0.10")  # $0.10 per mirrored block
    MIN_THREAT_REWARD = Decimal("1.00")    # $1 minimum threat detection reward
    MAX_THREAT_REWARD = Decimal("100.00")  # $100 maximum threat detection reward

    # Staking parameters
    MIN_STAKE = Decimal("100.00")          # $100 minimum stake
    APY_BASE = Decimal("0.05")             # 5% base APY
    APY_BONUS_PER_HCT = Decimal("0.10")    # +10% APY per 0.1 HCT above 0.8

    # Fee structure
    SPAWN_FEE_PERCENT = Decimal("0.02")    # 2% fee on cell spawning
    THREAT_DETECTION_FEE = Decimal("0.05") # 5% fee on threat rewards

    @classmethod
    def calculate_cell_value(cls, cell_type: str, count: int) -> Decimal:
        """Calculate total USDC value for spawned cells"""
        base_value = cls.CELL_VALUES.get(cell_type, Decimal("5.00"))
        return base_value * Decimal(count)

    @classmethod
    def calculate_threat_reward(cls, threat_score: int) -> Decimal:
        """Calculate USDC reward for threat detection"""
        if threat_score <= 0:
            return Decimal("0")

        # Linear scale from MIN to MAX based on threat score (0-100)
        reward_range = cls.MAX_THREAT_REWARD - cls.MIN_THREAT_REWARD
        reward = cls.MIN_THREAT_REWARD + (reward_range * Decimal(threat_score) / Decimal(100))

        return min(reward, cls.MAX_THREAT_REWARD)

    @classmethod
    def calculate_staking_apy(cls, hct_score: Decimal) -> Decimal:
        """Calculate APY based on HCT score"""
        if hct_score < Decimal("0.5"):
            return Decimal("0")  # No rewards if HCT too low

        # Base APY + bonus for high HCT
        bonus_hct = max(Decimal("0"), hct_score - Decimal("0.8"))
        bonus_multiplier = bonus_hct * Decimal("10")  # 0.1 HCT = 1x multiplier
        bonus_apy = cls.APY_BONUS_PER_HCT * bonus_multiplier

        return cls.APY_BASE + bonus_apy

    @classmethod
    def calculate_staking_rewards(cls, stake_amount: Decimal, hct_score: Decimal, days: int) -> Decimal:
        """Calculate staking rewards in USDC"""
        apy = cls.calculate_staking_apy(hct_score)
        daily_rate = apy / Decimal("365")
        rewards = stake_amount * daily_rate * Decimal(days)
        return rewards

class USDCIntegration:
    """Integrates LUXBIN with real USDC on multiple chains"""

    def __init__(self, chain: str = "optimism"):
        self.chain = chain
        self.w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINTS[chain]))
        self.usdc_address = USDC_ADDRESSES[chain]
        self.usdc_contract = self._load_usdc_contract()
        self.tokenomics = LuxbinTokenomics()

    def _load_usdc_contract(self) -> Optional[Contract]:
        """Load USDC contract"""
        # Minimal USDC ABI (ERC20)
        usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]

        try:
            return self.w3.eth.contract(
                address=Web3.to_checksum_address(self.usdc_address),
                abi=usdc_abi
            )
        except Exception as e:
            print(f"Warning: Could not load USDC contract: {e}")
            return None

    def get_usdc_balance(self, address: str) -> Decimal:
        """Get USDC balance for an address"""
        try:
            if not self.usdc_contract:
                return Decimal("0")

            checksum_address = Web3.to_checksum_address(address)
            balance_wei = self.usdc_contract.functions.balanceOf(checksum_address).call()

            # Convert from wei (6 decimals for USDC)
            balance = Decimal(balance_wei) / Decimal(10 ** USDC_DECIMALS)
            return balance
        except Exception as e:
            print(f"Error getting USDC balance: {e}")
            return Decimal("0")

    def get_usdc_total_supply(self) -> Decimal:
        """Get total USDC supply on this chain"""
        try:
            if not self.usdc_contract:
                return Decimal("0")

            supply_wei = self.usdc_contract.functions.totalSupply().call()
            supply = Decimal(supply_wei) / Decimal(10 ** USDC_DECIMALS)
            return supply
        except Exception as e:
            print(f"Error getting USDC total supply: {e}")
            return Decimal("0")

    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        return self.w3.is_connected()

class LuxbinUSDCEconomy:
    """Complete USDC economy for LUXBIN"""

    def __init__(self, mirror_root: str = "./luxbin_mirror", chain: str = "optimism"):
        self.mirror_root = Path(mirror_root)
        self.chain = chain
        self.chain_path = self.mirror_root / chain

        # Logs
        self.threat_log = self.chain_path / "quantum" / "threat_scores.jsonl"
        self.cells_log = self.chain_path / "immune" / "cells_spawned.jsonl"
        self.economy_log = self.chain_path / "economy" / "usdc_transactions.jsonl"

        # Create economy directory
        (self.chain_path / "economy").mkdir(parents=True, exist_ok=True)

        # USDC integration
        self.usdc = USDCIntegration(chain)
        self.tokenomics = LuxbinTokenomics()

        # Balances
        self.total_earned = Decimal("0")
        self.total_spent = Decimal("0")
        self.total_staked = Decimal("0")

    async def calculate_mirror_value(self) -> Dict:
        """Calculate total USDC value of all mirror activities"""

        value_breakdown = {
            "cells_spawned_value": Decimal("0"),
            "threat_rewards": Decimal("0"),
            "block_rewards": Decimal("0"),
            "total_value": Decimal("0"),
            "cell_breakdown": {},
        }

        # Calculate cell spawn value
        if self.cells_log.exists():
            with open(self.cells_log, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        cell_type = data.get('cell_type', 'MEMORY')
                        count = data.get('count', 1)

                        cell_value = self.tokenomics.calculate_cell_value(cell_type, count)
                        value_breakdown["cells_spawned_value"] += cell_value

                        # Track by cell type
                        if cell_type not in value_breakdown["cell_breakdown"]:
                            value_breakdown["cell_breakdown"][cell_type] = {"count": 0, "value": Decimal("0")}

                        value_breakdown["cell_breakdown"][cell_type]["count"] += count
                        value_breakdown["cell_breakdown"][cell_type]["value"] += cell_value
                    except:
                        continue

        # Calculate threat detection rewards
        if self.threat_log.exists():
            with open(self.threat_log, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        threat_score = data.get('threat_score', 0)
                        reward = self.tokenomics.calculate_threat_reward(threat_score)
                        value_breakdown["threat_rewards"] += reward
                    except:
                        continue

        # Calculate block mirror rewards
        block_count = len(list(self.chain_path.glob("raw/block_*.json"))) if (self.chain_path / "raw").exists() else 0
        value_breakdown["block_rewards"] = self.tokenomics.BLOCK_MIRROR_REWARD * Decimal(block_count)

        # Total
        value_breakdown["total_value"] = (
            value_breakdown["cells_spawned_value"] +
            value_breakdown["threat_rewards"] +
            value_breakdown["block_rewards"]
        )

        return value_breakdown

    async def get_economy_stats(self) -> Dict:
        """Get complete economy statistics"""

        # Calculate mirror value
        mirror_value = await self.calculate_mirror_value()

        # Get USDC stats from chain
        usdc_connected = self.usdc.is_connected()
        usdc_total_supply = self.usdc.get_usdc_total_supply() if usdc_connected else Decimal("0")

        return {
            "chain": self.chain,
            "usdc_connected": usdc_connected,
            "usdc_total_supply": str(usdc_total_supply),
            "mirror_value": {
                "cells_value": str(mirror_value["cells_spawned_value"]),
                "threat_rewards": str(mirror_value["threat_rewards"]),
                "block_rewards": str(mirror_value["block_rewards"]),
                "total_earned": str(mirror_value["total_value"]),
            },
            "cell_breakdown": {
                cell_type: {
                    "count": data["count"],
                    "value": str(data["value"])
                }
                for cell_type, data in mirror_value["cell_breakdown"].items()
            },
            "tokenomics": {
                "cell_values": {k: str(v) for k, v in self.tokenomics.CELL_VALUES.items()},
                "block_reward": str(self.tokenomics.BLOCK_MIRROR_REWARD),
                "min_threat_reward": str(self.tokenomics.MIN_THREAT_REWARD),
                "max_threat_reward": str(self.tokenomics.MAX_THREAT_REWARD),
            },
            "timestamp": datetime.now().isoformat()
        }

    async def calculate_user_earnings(self, hct_score: Decimal = Decimal("0.85")) -> Dict:
        """Calculate potential user earnings with staking"""

        mirror_value = await self.calculate_mirror_value()
        total_earned = mirror_value["total_value"]

        # Calculate staking APY
        apy = self.tokenomics.calculate_staking_apy(hct_score)

        # Calculate 30-day staking rewards if user stakes their earnings
        if total_earned >= self.tokenomics.MIN_STAKE:
            staking_rewards_30d = self.tokenomics.calculate_staking_rewards(
                total_earned,
                hct_score,
                30
            )
        else:
            staking_rewards_30d = Decimal("0")

        return {
            "total_earned": str(total_earned),
            "hct_score": str(hct_score),
            "current_apy": str(apy * 100) + "%",
            "staking_rewards_30d": str(staking_rewards_30d),
            "potential_30d_total": str(total_earned + staking_rewards_30d),
            "min_stake_required": str(self.tokenomics.MIN_STAKE),
            "can_stake": total_earned >= self.tokenomics.MIN_STAKE
        }

    def log_transaction(self, tx_type: str, amount: Decimal, details: Dict):
        """Log USDC transaction"""
        transaction = {
            "type": tx_type,
            "amount": str(amount),
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        with open(self.economy_log, 'a') as f:
            f.write(json.dumps(transaction) + '\n')

async def main():
    """Demo LUXBIN USDC economy"""

    print("=" * 80)
    print("💰 LUXBIN USDC ECONOMY")
    print("=" * 80)
    print()

    # Initialize economy
    economy = LuxbinUSDCEconomy(chain="optimism")

    print(f"Chain: {economy.chain}")
    print(f"USDC Contract: {economy.usdc.usdc_address}")
    print(f"Connected: {economy.usdc.is_connected()}")
    print()

    # Get economy stats
    print("📊 Getting economy statistics...")
    stats = await economy.get_economy_stats()

    print()
    print("=" * 80)
    print("MIRROR VALUE BREAKDOWN")
    print("=" * 80)
    print(f"Cells Spawned Value: ${stats['mirror_value']['cells_value']}")
    print(f"Threat Rewards:      ${stats['mirror_value']['threat_rewards']}")
    print(f"Block Rewards:       ${stats['mirror_value']['block_rewards']}")
    print(f"TOTAL EARNED:        ${stats['mirror_value']['total_earned']}")
    print()

    if stats['cell_breakdown']:
        print("CELL BREAKDOWN:")
        for cell_type, data in stats['cell_breakdown'].items():
            print(f"  {cell_type}: {data['count']} cells = ${data['value']}")
        print()

    print("=" * 80)
    print("TOKENOMICS")
    print("=" * 80)
    for cell_type, value in stats['tokenomics']['cell_values'].items():
        print(f"{cell_type} cell: ${value}")
    print(f"Block mirror reward: ${stats['tokenomics']['block_reward']}")
    print(f"Threat reward range: ${stats['tokenomics']['min_threat_reward']} - ${stats['tokenomics']['max_threat_reward']}")
    print()

    # Calculate user earnings
    print("=" * 80)
    print("USER EARNING POTENTIAL (HCT = 0.85)")
    print("=" * 80)
    earnings = await economy.calculate_user_earnings(Decimal("0.85"))
    print(f"Total Earned:        ${earnings['total_earned']}")
    print(f"Current APY:         {earnings['current_apy']}")
    print(f"30-Day Staking Rewards: ${earnings['staking_rewards_30d']}")
    print(f"Potential 30-Day Total: ${earnings['potential_30d_total']}")
    stake_msg = 'Yes' if earnings['can_stake'] else f"No (need ${earnings['min_stake_required']})"
    print(f"Can Stake:           {stake_msg}")
    print()

    # Show USDC total supply
    if stats['usdc_connected']:
        print(f"USDC Total Supply on {economy.chain}: ${stats['usdc_total_supply']}")
    print()

if __name__ == "__main__":
    asyncio.run(main())
