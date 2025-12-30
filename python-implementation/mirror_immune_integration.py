#!/usr/bin/env python3
"""
LUXBIN MIRROR-IMMUNE INTEGRATION
Bridges live blockchain mirroring with immune cell spawning

Reads threat scores from Hermetic mirror and spawns appropriate immune cells
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ThreatEvent:
    """Threat detected in mirrored blockchain data"""
    block: str
    threat_score: int
    timestamp: str
    chain: str

@dataclass
class CellSpawnEvent:
    """Immune cell spawned in response to threat"""
    block: str
    cell_type: str
    count: int
    threat_score: int
    timestamp: str

class MirrorImmuneIntegration:
    """Integrates Hermetic mirror with immune system"""

    def __init__(self, mirror_root: str = "./luxbin_mirror", chain: str = "optimism"):
        self.mirror_root = Path(mirror_root)
        self.chain = chain
        self.chain_path = self.mirror_root / chain

        # File paths
        self.threat_log = self.chain_path / "quantum" / "threat_scores.jsonl"
        self.cells_log = self.chain_path / "immune" / "cells_spawned.jsonl"
        self.vibration_log = self.chain_path / "logs" / "vibration.jsonl"
        self.rhythm_log = self.chain_path / "logs" / "rhythm.jsonl"

        # State
        self.last_processed_block = None
        self.threat_history = []
        self.cell_history = []

    async def watch_mirror(self, interval: float = 2.0):
        """
        Continuously watch mirror for new blocks and spawn cells

        Args:
            interval: How often to check for new data (seconds)
        """
        print("🔮 Starting Mirror-Immune Integration")
        print(f"   Chain: {self.chain}")
        print(f"   Mirror root: {self.mirror_root}")
        print(f"   Check interval: {interval}s")
        print()

        while True:
            try:
                await self._process_new_threats()
                await self._analyze_patterns()
                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                print("\n⚠️  Shutting down integration...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(interval)

    async def _process_new_threats(self):
        """Process new threat events from mirror"""

        if not self.threat_log.exists():
            return

        # Read all threat events
        with open(self.threat_log, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())

                    # Skip if already processed
                    if self.last_processed_block and event['block'] <= self.last_processed_block:
                        continue

                    threat = ThreatEvent(
                        block=event['block'],
                        threat_score=event['threat_score'],
                        timestamp=event['timestamp'],
                        chain=self.chain
                    )

                    await self._handle_threat(threat)
                    self.last_processed_block = event['block']

                except json.JSONDecodeError:
                    continue

    async def _handle_threat(self, threat: ThreatEvent):
        """Handle a threat by spawning appropriate cells"""

        # Threat classification
        if threat.threat_score >= 70:
            severity = "CRITICAL"
            print(f"🚨 CRITICAL THREAT detected in block {threat.block}")
            await self._spawn_critical_response(threat)

        elif threat.threat_score >= 50:
            severity = "HIGH"
            print(f"⚠️  HIGH THREAT detected in block {threat.block}")
            await self._spawn_high_response(threat)

        elif threat.threat_score >= 30:
            severity = "MEDIUM"
            print(f"⚡ MEDIUM THREAT detected in block {threat.block}")
            await self._spawn_medium_response(threat)

        else:
            severity = "LOW"
            # Low threats don't print (too noisy)
            await self._spawn_low_response(threat)

        # Record in history
        self.threat_history.append({
            'block': threat.block,
            'score': threat.threat_score,
            'severity': severity,
            'timestamp': threat.timestamp
        })

    async def _spawn_critical_response(self, threat: ThreatEvent):
        """Critical threat: Full immune response"""

        # Spawn all cell types
        cells = [
            ("DETECTOR", 5),   # Scan everywhere
            ("DEFENDER", 10),  # Maximum defense
            ("MEMORY", 3),     # Remember this
            ("REGULATORY", 2)  # Prevent overreaction
        ]

        for cell_type, count in cells:
            await self._spawn_cells(cell_type, count, threat)

        print(f"   🦠 Spawned: 5 DETECTOR + 10 DEFENDER + 3 MEMORY + 2 REGULATORY")

    async def _spawn_high_response(self, threat: ThreatEvent):
        """High threat: Strong response"""

        cells = [
            ("DETECTOR", 3),
            ("DEFENDER", 5),
            ("MEMORY", 1)
        ]

        for cell_type, count in cells:
            await self._spawn_cells(cell_type, count, threat)

        print(f"   🦠 Spawned: 3 DETECTOR + 5 DEFENDER + 1 MEMORY")

    async def _spawn_medium_response(self, threat: ThreatEvent):
        """Medium threat: Moderate response"""

        cells = [
            ("DETECTOR", 2),
            ("DEFENDER", 2)
        ]

        for cell_type, count in cells:
            await self._spawn_cells(cell_type, count, threat)

        print(f"   🦠 Spawned: 2 DETECTOR + 2 DEFENDER")

    async def _spawn_low_response(self, threat: ThreatEvent):
        """Low threat: Minimal response"""

        await self._spawn_cells("MEMORY", 1, threat)

    async def _spawn_cells(self, cell_type: str, count: int, threat: ThreatEvent):
        """Spawn immune cells (placeholder - will integrate with actual spawner)"""

        # This would call the actual immune system spawner
        # For now, just log the event

        event = CellSpawnEvent(
            block=threat.block,
            cell_type=cell_type,
            count=count,
            threat_score=threat.threat_score,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        self.cell_history.append(event)

        # In future: integrate with infinite_cell_spawner.py
        # from infinite_cell_spawner import InfiniteCellSpawner
        # spawner = InfiniteCellSpawner(...)
        # await spawner.spawn_cell(cell_type_map[cell_type], count)

    async def _analyze_patterns(self):
        """Analyze threat patterns and adjust immune response"""

        if len(self.threat_history) < 10:
            return

        # Calculate average threat over last 10 blocks
        recent_threats = self.threat_history[-10:]
        avg_threat = sum(t['score'] for t in recent_threats) / len(recent_threats)

        # Adaptive immune response
        if avg_threat > 50:
            print(f"📊 Pattern detected: High sustained threat (avg: {avg_threat:.1f})")
            print(f"   Recommendation: Increase DETECTOR cell baseline")
        elif avg_threat > 30:
            print(f"📊 Pattern detected: Moderate threat level (avg: {avg_threat:.1f})")
            print(f"   Recommendation: Maintain current immune levels")

    async def generate_report(self) -> Dict:
        """Generate immune system activity report"""

        # Count cells by type
        cell_counts = {}
        for event in self.cell_history:
            cell_type = event.cell_type
            cell_counts[cell_type] = cell_counts.get(cell_type, 0) + event.count

        # Threat statistics
        threat_scores = [t['score'] for t in self.threat_history]

        report = {
            "chain": self.chain,
            "blocks_processed": len(self.threat_history),
            "cells_spawned": cell_counts,
            "total_cells": sum(cell_counts.values()),
            "threat_stats": {
                "min": min(threat_scores) if threat_scores else 0,
                "max": max(threat_scores) if threat_scores else 0,
                "avg": sum(threat_scores) / len(threat_scores) if threat_scores else 0,
            },
            "last_block": self.last_processed_block,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return report

    def print_report(self, report: Dict):
        """Print formatted report"""

        print()
        print("═" * 80)
        print("📊 IMMUNE SYSTEM ACTIVITY REPORT")
        print("═" * 80)
        print(f"Chain: {report['chain']}")
        print(f"Blocks processed: {report['blocks_processed']}")
        print(f"Last block: {report['last_block']}")
        print()
        print("Cells spawned:")
        for cell_type, count in report['cells_spawned'].items():
            print(f"  {cell_type}: {count}")
        print(f"  TOTAL: {report['total_cells']}")
        print()
        print("Threat statistics:")
        print(f"  Min: {report['threat_stats']['min']}")
        print(f"  Max: {report['threat_stats']['max']}")
        print(f"  Avg: {report['threat_stats']['avg']:.1f}")
        print("═" * 80)
        print()

async def main():
    """Run the integration"""

    import argparse

    parser = argparse.ArgumentParser(description="LUXBIN Mirror-Immune Integration")
    parser.add_argument("--chain", default="optimism", help="Blockchain to monitor")
    parser.add_argument("--mirror-root", default="./luxbin_mirror", help="Mirror data root")
    parser.add_argument("--interval", type=float, default=2.0, help="Check interval (seconds)")
    parser.add_argument("--report-only", action="store_true", help="Generate report and exit")

    args = parser.parse_args()

    integration = MirrorImmuneIntegration(
        mirror_root=args.mirror_root,
        chain=args.chain
    )

    if args.report_only:
        # Generate and print report
        report = await integration.generate_report()
        integration.print_report(report)
    else:
        # Run continuous monitoring
        print("✨════════════════════════════════════════════════════════════✨")
        print("║                                                            ║")
        print("║       LUXBIN MIRROR-IMMUNE INTEGRATION                    ║")
        print("║       Hermetic mirror + Living immune system              ║")
        print("║                                                            ║")
        print("✨════════════════════════════════════════════════════════════✨")
        print()

        try:
            await integration.watch_mirror(interval=args.interval)
        finally:
            # Print final report
            report = await integration.generate_report()
            integration.print_report(report)

if __name__ == "__main__":
    asyncio.run(main())
