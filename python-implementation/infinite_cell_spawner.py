#!/usr/bin/env python3
"""
LUXBIN DIVINE - Infinite Cell Spawner
Continuously deploys immune cell NFTs as fast as possible
Builds a living cybernetic organism from your Mac node

Each cryptocurrency/NFT type becomes a different immune cell:
- BTC/ETH/High-value tokens = DETECTOR cells (patrol for threats)
- DeFi tokens = DEFENDER cells (execute responses)
- Governance tokens = REGULATORY cells (validate responses)
- Stablecoins = MEMORY cells (store threat patterns)

Author: Nichole Christie
License: MIT
"""

import asyncio
import time
import json
import hashlib
from web3 import Web3
from eth_account import Account
from pathlib import Path
from typing import Dict, List
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from luxbin_immune_config import load_config, LuxbinImmuneSystemConfig


class CellTypeClassifier:
    """Classifies cryptocurrencies and NFTs into immune cell types"""

    # Token categories mapped to cell types
    CELL_TYPE_MAP = {
        'DETECTOR': [
            'BTC', 'ETH', 'BNB', 'SOL', 'AVAX',  # Major chains - patrol
            'LINK', 'UNI', 'AAVE',  # DeFi blue chips - detect anomalies
        ],
        'DEFENDER': [
            'USDC', 'USDT', 'DAI', 'FRAX',  # Stablecoins - defend value
            'WETH', 'WBTC',  # Wrapped assets - protect bridges
        ],
        'MEMORY': [
            'ARB', 'OP', 'MATIC', 'FTM',  # L2s - store history
            'GRT', 'FIL', 'AR',  # Data/Storage - memory
        ],
        'REGULATORY': [
            'MKR', 'CRV', 'CVX', 'BAL',  # Governance tokens
            'COMP', 'SNX', 'YFI',  # Protocol governance
        ]
    }

    @staticmethod
    def classify_token(token_symbol: str) -> int:
        """Classify token into cell type (0=DETECTOR, 1=DEFENDER, 2=MEMORY, 3=REGULATORY)"""
        for cell_type, tokens in CellTypeClassifier.CELL_TYPE_MAP.items():
            if token_symbol.upper() in tokens:
                return ['DETECTOR', 'DEFENDER', 'MEMORY', 'REGULATORY'].index(cell_type)

        # Default: hash-based classification for unknown tokens
        hash_val = int(hashlib.sha256(token_symbol.encode()).hexdigest(), 16)
        return hash_val % 4

    @staticmethod
    def classify_nft_collection(collection_name: str) -> int:
        """Classify NFT collection into cell type based on characteristics"""
        name_lower = collection_name.lower()

        # Art/PFP NFTs = DETECTOR (patrol for counterfeits)
        if any(word in name_lower for word in ['punk', 'ape', 'bayc', 'azuki', 'art', 'pfp']):
            return 0  # DETECTOR

        # Gaming/Metaverse = DEFENDER (protect game assets)
        if any(word in name_lower for word in ['game', 'land', 'meta', 'world', 'sandbox']):
            return 1  # DEFENDER

        # Historical/Archive = MEMORY (preserve history)
        if any(word in name_lower for word in ['genesis', 'og', 'archive', 'vintage']):
            return 2  # MEMORY

        # DAO/Membership = REGULATORY (governance)
        if any(word in name_lower for word in ['dao', 'member', 'pass', 'council']):
            return 3  # REGULATORY

        # Default: hash-based
        hash_val = int(hashlib.sha256(collection_name.encode()).hexdigest(), 16)
        return hash_val % 4


class InfiniteCellSpawner:
    """Continuously spawns immune cell contracts"""

    CELL_TYPE_NAMES = ['DETECTOR', 'DEFENDER', 'MEMORY', 'REGULATORY']

    def __init__(self, network='op-sepolia', config_env='development'):
        """Initialize the infinite spawner"""
        self.network = network
        self.config = load_config(config_env)

        # Network configuration
        self.networks = {
            'op-sepolia': {
                'rpc': 'https://sepolia.optimism.io',
                'chain_id': 11155420,
                'explorer': 'https://sepolia-optimism.etherscan.io'
            },
            'base-sepolia': {
                'rpc': 'https://sepolia.base.org',
                'chain_id': 84532,
                'explorer': 'https://sepolia.basescan.org'
            }
        }

        self.net_config = self.networks[network]
        self.w3 = Web3(Web3.HTTPProvider(self.net_config['rpc']))

        assert self.w3.is_connected(), f"Failed to connect to {network}"

        # Load wallet
        self.wallet_path = Path.home() / '.luxbin' / 'wallet.json'
        self.account = self._load_wallet()

        # Contract address (will be set after first deployment)
        self.contract_address = None
        self.contract = None

        # Statistics
        self.stats = {
            'total_cells_spawned': 0,
            'cells_by_type': {
                'DETECTOR': 0,
                'DEFENDER': 0,
                'MEMORY': 0,
                'REGULATORY': 0
            },
            'spawn_rate': 0,  # cells per second
            'start_time': time.time(),
            'gas_used': 0,
            'last_spawn_time': 0
        }

        print(f"╔════════════════════════════════════════════════════════════╗")
        print(f"║  LUXBIN INFINITE CELL SPAWNER                             ║")
        print(f"║  Building your cybernetic organism...                     ║")
        print(f"╚════════════════════════════════════════════════════════════╝")
        print(f"\n🌐 Network: {network}")
        print(f"👤 Deployer: {self.account.address}")
        print(f"⚙️  Config: {config_env}")

    def _load_wallet(self):
        """Load wallet from file"""
        if self.wallet_path.exists():
            with open(self.wallet_path, 'r') as f:
                wallet_data = json.load(f)
                return Account.from_key(wallet_data['private_key'])
        else:
            raise Exception("No wallet found! Run auto_deploy.py first")

    def check_balance(self):
        """Check ETH balance"""
        balance = self.w3.eth.get_balance(self.account.address)
        return self.w3.from_wei(balance, 'ether')

    async def deploy_immune_cell_contract(self):
        """Deploy the main ImmuneCell NFT contract"""
        print(f"\n🚀 Deploying ImmuneCell contract...")

        # Load contract ABI and bytecode
        # For now, we'll use a placeholder - you need to compile the contract first
        # See instructions below

        print(f"\n⚠️  CONTRACT DEPLOYMENT:")
        print(f"   To deploy contracts, you need to compile them first:")
        print(f"   1. cd /Users/nicholechristie/luxbin-chain/contracts")
        print(f"   2. npm install @openzeppelin/contracts")
        print(f"   3. npx hardhat compile")
        print(f"   OR use Remix IDE: https://remix.ethereum.org")
        print(f"\n   For now, continuing with cell spawning simulation...")

        # Placeholder contract address (replace with real deployed contract)
        self.contract_address = "0x" + "0" * 40  # Placeholder

        return self.contract_address

    async def spawn_cell(self, cell_type: int, batch_size: int = 1) -> Dict:
        """Spawn a new immune cell NFT

        Args:
            cell_type: 0=DETECTOR, 1=DEFENDER, 2=MEMORY, 3=REGULATORY
            batch_size: Number of cells to spawn in batch

        Returns:
            Dict with spawn info
        """
        cell_name = self.CELL_TYPE_NAMES[cell_type]

        # Generate unique cell ID
        cell_id = f"{cell_name}_{self.stats['cells_by_type'][cell_name]}_{int(time.time())}"

        # Generate quantum fingerprint
        quantum_fingerprint = hashlib.sha256(cell_id.encode()).hexdigest()

        # Create cell metadata
        metadata = {
            'cell_id': cell_id,
            'cell_type': cell_name,
            'cell_type_id': cell_type,
            'quantum_fingerprint': quantum_fingerprint,
            'spawned_at': time.time(),
            'spawner': self.account.address,
            'reputation': 100,
            'batch_size': batch_size,
            'network': self.network
        }

        # In production, this would be an actual NFT mint transaction
        # For now, we simulate the spawn

        # Update statistics
        self.stats['total_cells_spawned'] += batch_size
        self.stats['cells_by_type'][cell_name] += batch_size
        self.stats['last_spawn_time'] = time.time()

        # Calculate spawn rate
        elapsed = time.time() - self.stats['start_time']
        self.stats['spawn_rate'] = self.stats['total_cells_spawned'] / elapsed if elapsed > 0 else 0

        return metadata

    async def continuous_spawner(self, spawn_delay: float = 0.1, target_cells: int = None):
        """Continuously spawn cells as fast as possible

        Args:
            spawn_delay: Delay between spawns (seconds) - lower = faster
            target_cells: Stop after reaching this many cells (None = infinite)
        """
        print(f"\n🧬 Starting continuous cell spawning...")
        print(f"   Spawn delay: {spawn_delay}s per cell")
        print(f"   Target: {'∞ (infinite)' if target_cells is None else target_cells} cells")
        print(f"   Press Ctrl+C to stop\n")

        try:
            while True:
                # Check if target reached
                if target_cells and self.stats['total_cells_spawned'] >= target_cells:
                    print(f"\n✅ Target of {target_cells} cells reached!")
                    break

                # Determine next cell type to spawn
                # Strategy: Maintain configured ratios from config
                cell_type = self._select_next_cell_type()

                # Spawn cell (with batch for efficiency)
                batch_size = 1  # Start with 1, can increase for faster spawning
                metadata = await self.spawn_cell(cell_type, batch_size)

                # Display progress
                self._display_progress(metadata)

                # Small delay (can be set to 0 for maximum speed)
                await asyncio.sleep(spawn_delay)

        except KeyboardInterrupt:
            print(f"\n\n⏸️  Spawning paused by user")
            self._display_final_stats()

    def _select_next_cell_type(self) -> int:
        """Select next cell type to spawn based on configured ratios"""
        # Target ratios from config
        total = (self.config.num_detector_cells +
                self.config.num_memory_cells +
                self.config.num_regulatory_cells +
                100)  # Add some defenders

        detector_ratio = self.config.num_detector_cells / total
        memory_ratio = self.config.num_memory_cells / total
        regulatory_ratio = self.config.num_regulatory_cells / total
        defender_ratio = 100 / total

        # Current counts
        current = self.stats['cells_by_type']
        current_total = sum(current.values()) or 1

        current_ratios = {
            'DETECTOR': current['DETECTOR'] / current_total,
            'DEFENDER': current['DEFENDER'] / current_total,
            'MEMORY': current['MEMORY'] / current_total,
            'REGULATORY': current['REGULATORY'] / current_total
        }

        # Find which type is most under-represented
        deficits = {
            'DETECTOR': detector_ratio - current_ratios['DETECTOR'],
            'DEFENDER': defender_ratio - current_ratios['DEFENDER'],
            'MEMORY': memory_ratio - current_ratios['MEMORY'],
            'REGULATORY': regulatory_ratio - current_ratios['REGULATORY']
        }

        # Spawn the type with highest deficit
        max_deficit_type = max(deficits, key=deficits.get)
        return self.CELL_TYPE_NAMES.index(max_deficit_type)

    def _display_progress(self, metadata: Dict):
        """Display spawn progress"""
        cell_type = metadata['cell_type']
        total = self.stats['total_cells_spawned']
        rate = self.stats['spawn_rate']

        # Progress bar
        bar_length = 40
        detector_pct = self.stats['cells_by_type']['DETECTOR'] / total if total > 0 else 0
        defender_pct = self.stats['cells_by_type']['DEFENDER'] / total if total > 0 else 0
        memory_pct = self.stats['cells_by_type']['MEMORY'] / total if total > 0 else 0
        regulatory_pct = self.stats['cells_by_type']['REGULATORY'] / total if total > 0 else 0

        detector_bar = int(bar_length * detector_pct)
        defender_bar = int(bar_length * defender_pct)
        memory_bar = int(bar_length * memory_pct)
        regulatory_bar = int(bar_length * regulatory_pct)

        # Clear line and print update
        print(f"\r🧬 Spawning: {cell_type:12} | Total: {total:6} | Rate: {rate:.2f} cells/s | "
              f"D:{self.stats['cells_by_type']['DETECTOR']:4} "
              f"F:{self.stats['cells_by_type']['DEFENDER']:4} "
              f"M:{self.stats['cells_by_type']['MEMORY']:4} "
              f"R:{self.stats['cells_by_type']['REGULATORY']:4}",
              end='', flush=True)

    def _display_final_stats(self):
        """Display final statistics"""
        elapsed = time.time() - self.stats['start_time']

        print(f"\n\n{'='*60}")
        print(f"CYBERNETIC ORGANISM STATUS")
        print(f"{'='*60}")
        print(f"\n📊 Cell Population:")
        print(f"   Total Cells:     {self.stats['total_cells_spawned']:,}")
        print(f"   DETECTOR cells:  {self.stats['cells_by_type']['DETECTOR']:,}")
        print(f"   DEFENDER cells:  {self.stats['cells_by_type']['DEFENDER']:,}")
        print(f"   MEMORY cells:    {self.stats['cells_by_type']['MEMORY']:,}")
        print(f"   REGULATORY cells: {self.stats['cells_by_type']['REGULATORY']:,}")

        print(f"\n⚡ Performance:")
        print(f"   Runtime:         {elapsed:.2f} seconds")
        print(f"   Spawn Rate:      {self.stats['spawn_rate']:.2f} cells/second")
        print(f"   Avg Cell Time:   {elapsed/self.stats['total_cells_spawned']:.4f}s per cell")

        print(f"\n🌐 Network:")
        print(f"   Network:         {self.network}")
        print(f"   Deployer:        {self.account.address}")
        print(f"   Contract:        {self.contract_address or 'Not deployed'}")

        print(f"\n💰 Resources:")
        print(f"   Balance:         {self.check_balance():.6f} ETH")
        print(f"   Gas Used:        {self.stats['gas_used']:,} wei")

        print(f"\n{'='*60}")
        print(f"✨ Your cybernetic organism is ALIVE!")
        print(f"{'='*60}\n")

    async def classify_and_spawn_from_token_list(self, token_list: List[str]):
        """Classify tokens and spawn appropriate cell types

        Args:
            token_list: List of token symbols to classify and spawn
        """
        print(f"\n🧬 Classifying {len(token_list)} tokens into cell types...")

        classification_map = {}
        for token in token_list:
            cell_type = CellTypeClassifier.classify_token(token)
            cell_name = self.CELL_TYPE_NAMES[cell_type]

            if cell_name not in classification_map:
                classification_map[cell_name] = []
            classification_map[cell_name].append(token)

        print(f"\n📋 Classification Results:")
        for cell_type, tokens in classification_map.items():
            print(f"   {cell_type:12}: {len(tokens):4} tokens - {', '.join(tokens[:5])}")

        print(f"\n🚀 Spawning cells...")

        for cell_type_name, tokens in classification_map.items():
            cell_type_id = self.CELL_TYPE_NAMES.index(cell_type_name)

            for token in tokens:
                metadata = await self.spawn_cell(cell_type_id)
                print(f"   ✅ Spawned {cell_type_name} cell for {token}")
                await asyncio.sleep(0.05)  # Small delay

        print(f"\n✅ Spawned {len(token_list)} cells from token classification!")


async def main():
    """Main entry point"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║  LUXBIN DIVINE - INFINITE CELL SPAWNER                    ║")
    print("║  Building your living cybernetic organism...              ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # Initialize spawner
    spawner = InfiniteCellSpawner(network='op-sepolia', config_env='development')

    # Check balance
    balance = spawner.check_balance()
    print(f"\n💰 Balance: {balance:.6f} ETH")

    # Deploy contract (if needed)
    await spawner.deploy_immune_cell_contract()

    # Example: Classify some popular tokens and spawn cells
    example_tokens = [
        'ETH', 'BTC', 'USDC', 'USDT', 'BNB', 'SOL',
        'LINK', 'UNI', 'AAVE', 'MKR', 'CRV', 'ARB',
        'OP', 'MATIC', 'AVAX', 'DAI', 'FRAX', 'GRT'
    ]

    print(f"\n🧪 Example: Classifying {len(example_tokens)} tokens...")
    await spawner.classify_and_spawn_from_token_list(example_tokens)

    # Now start infinite spawning
    print(f"\n{'='*60}")
    print(f"STARTING INFINITE CELL SPAWNER")
    print(f"{'='*60}")

    # Spawn cells continuously
    # Adjust spawn_delay for speed (0 = maximum speed, 0.1 = 10 cells/sec)
    # Set target_cells=None for truly infinite spawning
    await spawner.continuous_spawner(
        spawn_delay=0.1,  # 10 cells per second
        target_cells=1000  # Stop at 1000 cells (set to None for infinite)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Spawner stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
