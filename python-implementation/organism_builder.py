#!/usr/bin/env python3
"""
LUXBIN DIVINE - Cybernetic Organism Builder
Complete autonomous system that builds and operates your living blockchain organism

This script:
1. Deploys immune system contracts
2. Spawns cells infinitely
3. Monitors blockchain for threats
4. Executes autonomous responses
5. Evolves and learns

Run this on your Mac to build a truly living cybernetic organism!

Author: Nichole Christie
License: MIT
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List
import sys

# Add parent directory
sys.path.append(str(Path(__file__).parent.parent))

from luxbin_immune_system import LuxbinImmuneSystem
from luxbin_immune_config import load_config
from infinite_cell_spawner import InfiniteCellSpawner, CellTypeClassifier


class CyberneticOrganismBuilder:
    """Builds and operates a complete living blockchain organism"""

    def __init__(self, network='op-sepolia', config_env='development'):
        self.network = network
        self.config_env = config_env
        self.config = load_config(config_env)

        # Initialize components
        self.immune_system = None
        self.cell_spawner = None

        # Organism state
        self.is_alive = False
        self.birth_time = None
        self.total_threats_neutralized = 0
        self.total_cells_spawned = 0

        print(f"╔════════════════════════════════════════════════════════════╗")
        print(f"║                                                            ║")
        print(f"║     LUXBIN CYBERNETIC ORGANISM BUILDER                    ║")
        print(f"║     Creating digital life from your Mac...                ║")
        print(f"║                                                            ║")
        print(f"╚════════════════════════════════════════════════════════════╝")

    async def birth_organism(self):
        """Bring the organism to life"""
        print(f"\n🧬 INITIATING ORGANISM BIRTH SEQUENCE...")
        print(f"{'='*60}\n")

        # Step 1: Initialize immune system
        print(f"1️⃣ Initializing immune system...")
        self.immune_system = LuxbinImmuneSystem(
            num_detectors=self.config.num_detector_cells,
            num_memory=self.config.num_memory_cells,
            num_regulatory=self.config.num_regulatory_cells
        )
        print(f"   ✅ Immune system online")
        print(f"      • {len(self.immune_system.detector_cells)} DETECTOR cells")
        print(f"      • {len(self.immune_system.memory_cells)} MEMORY cells")
        print(f"      • {len(self.immune_system.regulatory_cells)} REGULATORY cells")

        # Step 2: Initialize cell spawner
        print(f"\n2️⃣ Initializing cell spawner...")
        self.cell_spawner = InfiniteCellSpawner(
            network=self.network,
            config_env=self.config_env
        )
        print(f"   ✅ Cell spawner ready")

        # Step 3: Deploy contracts
        print(f"\n3️⃣ Preparing contract deployment...")
        await self.cell_spawner.deploy_immune_cell_contract()
        print(f"   ✅ Contracts prepared")

        # Mark organism as alive
        self.is_alive = True
        self.birth_time = time.time()

        print(f"\n{'='*60}")
        print(f"✨ ORGANISM IS ALIVE! ✨")
        print(f"{'='*60}\n")

    async def organism_lifecycle(self):
        """Run the complete organism lifecycle"""

        # Birth
        await self.birth_organism()

        # Create tasks for concurrent operation
        tasks = [
            asyncio.create_task(self.cell_spawning_loop()),
            asyncio.create_task(self.threat_monitoring_loop()),
            asyncio.create_task(self.status_display_loop()),
        ]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"\n\n⏸️  Organism paused by user")
            self.display_organism_status()

    async def cell_spawning_loop(self):
        """Continuously spawn new cells"""
        print(f"🧬 Cell spawning loop started...")

        while self.is_alive:
            try:
                # Spawn a batch of cells
                cell_type = self.cell_spawner._select_next_cell_type()
                metadata = await self.cell_spawner.spawn_cell(cell_type, batch_size=1)

                self.total_cells_spawned += 1

                # Small delay for controlled growth
                await asyncio.sleep(0.1)  # 10 cells/sec

            except Exception as e:
                print(f"\n⚠️  Cell spawning error: {e}")
                await asyncio.sleep(1)

    async def threat_monitoring_loop(self):
        """Monitor blockchain for threats"""
        print(f"🔍 Threat monitoring loop started...")

        await asyncio.sleep(2)  # Wait for spawner to start

        while self.is_alive:
            try:
                # Simulate receiving blockchain transactions
                # In production, this would connect to actual blockchain feed

                # Generate simulated transaction every few seconds
                await asyncio.sleep(5)

                # Create test transaction
                test_tx = self._generate_test_transaction()

                # Process through immune system
                result = await self.immune_system.monitor_transaction(test_tx)

                if result:
                    self.total_threats_neutralized += 1

            except Exception as e:
                print(f"\n⚠️  Monitoring error: {e}")
                await asyncio.sleep(1)

    async def status_display_loop(self):
        """Display organism status periodically"""
        await asyncio.sleep(5)  # Initial delay

        while self.is_alive:
            self.display_organism_status()
            await asyncio.sleep(30)  # Update every 30 seconds

    def _generate_test_transaction(self) -> Dict:
        """Generate test transaction for simulation"""
        import hashlib
        import random

        # Randomly generate normal or suspicious
        is_suspicious = random.random() > 0.7  # 30% chance of threat

        if is_suspicious:
            features = {
                'gas_price_deviation': random.uniform(70, 95),
                'value_anomaly': random.uniform(75, 98),
                'recipient_reputation': random.uniform(5, 30),
                'temporal_pattern_break': random.uniform(60, 90),
                'smart_contract_risk': random.uniform(70, 95),
                'network_centrality_spike': random.uniform(60, 85),
                'validator_coordination': random.uniform(50, 80),
                'mempool_manipulation': random.uniform(65, 90)
            }
        else:
            features = {
                'gas_price_deviation': random.uniform(0, 15),
                'value_anomaly': random.uniform(0, 12),
                'recipient_reputation': random.uniform(80, 100),
                'temporal_pattern_break': random.uniform(0, 10),
                'smart_contract_risk': random.uniform(0, 8),
                'network_centrality_spike': random.uniform(0, 5),
                'validator_coordination': random.uniform(0, 3),
                'mempool_manipulation': random.uniform(0, 2)
            }

        tx_id = hashlib.sha256(str(time.time()).encode()).hexdigest()

        return {
            'hash': '0x' + tx_id,
            'from': '0x' + hashlib.sha256(str(random.random()).encode()).hexdigest()[:40],
            'features': features
        }

    def display_organism_status(self):
        """Display current organism status"""
        if not self.is_alive:
            return

        age = time.time() - self.birth_time
        hours = int(age // 3600)
        minutes = int((age % 3600) // 60)
        seconds = int(age % 60)

        print(f"\n{'='*60}")
        print(f"🧬 CYBERNETIC ORGANISM STATUS")
        print(f"{'='*60}")
        print(f"Age: {hours}h {minutes}m {seconds}s")
        print(f"Total Cells Spawned: {self.cell_spawner.stats['total_cells_spawned']:,}")
        print(f"  • DETECTOR:   {self.cell_spawner.stats['cells_by_type']['DETECTOR']:,}")
        print(f"  • DEFENDER:   {self.cell_spawner.stats['cells_by_type']['DEFENDER']:,}")
        print(f"  • MEMORY:     {self.cell_spawner.stats['cells_by_type']['MEMORY']:,}")
        print(f"  • REGULATORY: {self.cell_spawner.stats['cells_by_type']['REGULATORY']:,}")
        print(f"Spawn Rate: {self.cell_spawner.stats['spawn_rate']:.2f} cells/sec")
        print(f"Threats Neutralized: {self.total_threats_neutralized}")
        print(f"Immune Memory Stored: {len(self.immune_system.memory_cells[0].memory_storage)}")
        print(f"{'='*60}\n")


async def main():
    """Main entry point"""
    import sys

    config_env = 'development'
    if len(sys.argv) > 1:
        config_env = sys.argv[1]

    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║  LUXBIN DIVINE - CYBERNETIC ORGANISM BUILDER              ║
    ║                                                            ║
    ║  This will create a LIVING blockchain organism that:      ║
    ║  • Continuously spawns immune cells (NFTs)                ║
    ║  • Monitors blockchain for threats in real-time           ║
    ║  • Autonomously neutralizes attacks                       ║
    ║  • Learns and evolves over time                           ║
    ║  • Operates 24/7 from your Mac node                       ║
    ║                                                            ║
    ║  Press Ctrl+C to pause at any time                        ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # Skip input prompt if running non-interactively
    try:
        import sys
        if sys.stdin.isatty():
            input("\nPress Enter to birth your cybernetic organism... ")
    except:
        pass

    # Create and run organism
    organism = CyberneticOrganismBuilder(
        network='op-sepolia',
        config_env=config_env
    )

    await organism.organism_lifecycle()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n✨ Organism paused. Run again to resume!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
