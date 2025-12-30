#!/usr/bin/env python3
"""
LUXBIN Energy Memory Storage - Biological Memory Banks

Treats energy storage like biological memory:
- Short-term storage = Working memory (RAM)
- Long-term storage = Long-term memory (SSD)
- Consolidation = Sleep-like energy transfer
- Retrieval = Context-based energy recall
- Engrams = Stored energy patterns

Just like the hippocampus stores memories, this stores energy!
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import sqlite3
import numpy as np


@dataclass
class EnergyEngram:
    """
    Engram = Physical memory trace in neurons.
    Energy Engram = Stored pattern of energy acquisition/usage.
    """
    engram_id: str
    energy_amount: float
    source: str  # Where energy came from (solar, wind, nuclear, tesla)
    timestamp: float
    context: Dict  # What was happening when energy was stored
    consolidation_strength: float  # How strongly consolidated (0-1)
    retrieval_count: int  # How many times recalled
    spatial_location: str  # Which grid node
    temporal_pattern: str  # Time of day pattern


class ShortTermEnergyMemory:
    """
    Short-term memory = Working memory = RAM

    Holds energy temporarily (seconds to minutes).
    Limited capacity (~7 items, Miller's Law).
    Quick access but volatile.
    """

    def __init__(self, capacity: int = 7):
        self.capacity = capacity  # Miller's Law: 7±2 items
        self.buffer = deque(maxlen=capacity)
        self.total_energy = 0.0

        print(f"🧠 SHORT-TERM ENERGY MEMORY INITIALIZED")
        print(f"   Capacity: {capacity} energy packets")
        print(f"   Type: Working memory (volatile)")

    def store_energy(self, engram: EnergyEngram):
        """Store energy in short-term buffer"""
        if len(self.buffer) >= self.capacity:
            # Oldest memory pushed out
            old_engram = self.buffer[0]
            print(f"   ⚠️ Buffer full! Forgetting oldest energy: {old_engram.engram_id}")

        self.buffer.append(engram)
        self.total_energy += engram.energy_amount

        print(f"💾 SHORT-TERM STORAGE:")
        print(f"   Engram: {engram.engram_id}")
        print(f"   Energy: {engram.energy_amount:.2f} kW")
        print(f"   Source: {engram.source}")
        print(f"   Buffer: {len(self.buffer)}/{self.capacity}")

    def recall_recent(self, n: int = 3) -> List[EnergyEngram]:
        """Recall N most recent energy memories"""
        return list(self.buffer)[-n:]

    def get_available_energy(self) -> float:
        """Get total energy in short-term storage"""
        return sum(engram.energy_amount for engram in self.buffer)

    def is_full(self) -> bool:
        """Check if working memory is at capacity"""
        return len(self.buffer) >= self.capacity


class LongTermEnergyMemory:
    """
    Long-term memory = Persistent storage = SSD

    Stores energy patterns indefinitely.
    Unlimited capacity.
    Slower access but permanent.
    Organized by consolidation strength.
    """

    def __init__(self, db_path: str = "energy_memory.db"):
        self.db_path = db_path
        self._init_database()
        self.engrams = {}  # ID -> Engram
        self._load_engrams()

        print(f"🧠 LONG-TERM ENERGY MEMORY INITIALIZED")
        print(f"   Database: {db_path}")
        print(f"   Type: Persistent memory")
        print(f"   Stored engrams: {len(self.engrams)}")

    def _init_database(self):
        """Create energy memory database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_engrams (
                engram_id TEXT PRIMARY KEY,
                energy_amount REAL,
                source TEXT,
                timestamp REAL,
                context TEXT,
                consolidation_strength REAL,
                retrieval_count INTEGER,
                spatial_location TEXT,
                temporal_pattern TEXT,
                created_at REAL,
                last_accessed REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consolidation_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engram_id TEXT,
                timestamp REAL,
                strength_before REAL,
                strength_after REAL,
                consolidation_type TEXT
            )
        """)

        conn.commit()
        conn.close()

    def _load_engrams(self):
        """Load all engrams from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM energy_engrams")

        for row in cursor.fetchall():
            engram = EnergyEngram(
                engram_id=row[0],
                energy_amount=row[1],
                source=row[2],
                timestamp=row[3],
                context=json.loads(row[4]),
                consolidation_strength=row[5],
                retrieval_count=row[6],
                spatial_location=row[7],
                temporal_pattern=row[8]
            )
            self.engrams[engram.engram_id] = engram

        conn.close()

    def consolidate_memory(self, engram: EnergyEngram):
        """
        Memory consolidation = Transfer from short-term to long-term.
        Happens during "sleep" (low demand periods).
        """
        initial_strength = engram.consolidation_strength

        # Strengthen based on repetition and importance
        engram.consolidation_strength = min(1.0, engram.consolidation_strength + 0.2)

        self.engrams[engram.engram_id] = engram
        self._save_to_database(engram)

        print(f"🌙 MEMORY CONSOLIDATION:")
        print(f"   Engram: {engram.engram_id}")
        print(f"   Strength: {initial_strength:.2f} → {engram.consolidation_strength:.2f}")
        print(f"   Status: {'STRONGLY CONSOLIDATED' if engram.consolidation_strength > 0.8 else 'Consolidating...'}")

        # Log consolidation event
        self._log_consolidation(engram, initial_strength)

    def recall_memory(self, engram_id: str) -> Optional[EnergyEngram]:
        """
        Recall energy memory by ID.
        Strengthens memory each time it's accessed (retrieval practice).
        """
        engram = self.engrams.get(engram_id)

        if engram:
            # Retrieval practice strengthens memory
            engram.retrieval_count += 1
            engram.consolidation_strength = min(1.0, engram.consolidation_strength + 0.05)

            print(f"🔍 MEMORY RECALL:")
            print(f"   Engram: {engram.engram_id}")
            print(f"   Retrieved: {engram.retrieval_count} times")
            print(f"   Strength: {engram.consolidation_strength:.2f}")

            # Update in database
            self._save_to_database(engram)

        return engram

    def recall_by_context(self, context_cue: Dict) -> List[EnergyEngram]:
        """
        Context-dependent memory recall.
        Similar to how smells trigger memories!
        """
        matching_engrams = []

        for engram in self.engrams.values():
            similarity = self._calculate_context_similarity(context_cue, engram.context)

            if similarity > 0.5:  # Threshold for recall
                matching_engrams.append((engram, similarity))

        # Sort by similarity
        matching_engrams.sort(key=lambda x: x[1], reverse=True)

        print(f"🔍 CONTEXT-BASED RECALL:")
        print(f"   Context cue: {context_cue}")
        print(f"   Matches found: {len(matching_engrams)}")

        return [engram for engram, _ in matching_engrams]

    def recall_by_source(self, source: str) -> List[EnergyEngram]:
        """Recall all energy from specific source"""
        return [e for e in self.engrams.values() if e.source == source]

    def recall_by_time_pattern(self, temporal_pattern: str) -> List[EnergyEngram]:
        """Recall energy from similar time patterns (e.g., 'morning', 'peak_hours')"""
        return [e for e in self.engrams.values() if e.temporal_pattern == temporal_pattern]

    def _calculate_context_similarity(self, context1: Dict, context2: Dict) -> float:
        """Calculate similarity between two contexts"""
        if not context1 or not context2:
            return 0.0

        matching_keys = set(context1.keys()) & set(context2.keys())
        if not matching_keys:
            return 0.0

        matches = sum(1 for k in matching_keys if context1[k] == context2[k])
        return matches / len(matching_keys)

    def _save_to_database(self, engram: EnergyEngram):
        """Save engram to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO energy_engrams
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            engram.engram_id,
            engram.energy_amount,
            engram.source,
            engram.timestamp,
            json.dumps(engram.context),
            engram.consolidation_strength,
            engram.retrieval_count,
            engram.spatial_location,
            engram.temporal_pattern,
            time.time(),
            time.time()
        ))

        conn.commit()
        conn.close()

    def _log_consolidation(self, engram: EnergyEngram, strength_before: float):
        """Log consolidation event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO consolidation_events
            (engram_id, timestamp, strength_before, strength_after, consolidation_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            engram.engram_id,
            time.time(),
            strength_before,
            engram.consolidation_strength,
            'sleep_consolidation' if engram.consolidation_strength > 0.5 else 'initial'
        ))

        conn.commit()
        conn.close()

    def get_total_stored_energy(self) -> float:
        """Get total energy in long-term storage"""
        return sum(e.energy_amount for e in self.engrams.values())

    def get_strongest_memories(self, n: int = 10) -> List[EnergyEngram]:
        """Get N strongest consolidated memories"""
        sorted_engrams = sorted(
            self.engrams.values(),
            key=lambda e: e.consolidation_strength,
            reverse=True
        )
        return sorted_engrams[:n]


class EnergyMemoryConsolidator:
    """
    Memory consolidation system.
    Transfers energy from short-term to long-term storage.

    Like sleep consolidation in the brain!
    """

    def __init__(self, short_term: ShortTermEnergyMemory, long_term: LongTermEnergyMemory):
        self.short_term = short_term
        self.long_term = long_term
        self.last_consolidation = time.time()
        self.consolidation_interval = 3600  # 1 hour (like REM cycles)

        print(f"🌙 CONSOLIDATION SYSTEM INITIALIZED")
        print(f"   Interval: {self.consolidation_interval/60:.0f} minutes")

    def should_consolidate(self) -> bool:
        """Check if it's time to consolidate (like entering sleep)"""
        time_since_last = time.time() - self.last_consolidation
        return time_since_last >= self.consolidation_interval or self.short_term.is_full()

    def consolidate(self):
        """
        Consolidation process (like sleep).
        Transfer memories from short-term to long-term storage.
        """
        print(f"\n{'='*60}")
        print(f"🌙 BEGINNING CONSOLIDATION (Sleep Cycle)")
        print(f"{'='*60}\n")

        consolidated_count = 0
        total_energy = 0.0

        # Transfer each engram from short-term to long-term
        for engram in list(self.short_term.buffer):
            self.long_term.consolidate_memory(engram)
            consolidated_count += 1
            total_energy += engram.energy_amount

        # Clear short-term buffer (awakening)
        self.short_term.buffer.clear()
        self.short_term.total_energy = 0.0

        self.last_consolidation = time.time()

        print(f"\n{'='*60}")
        print(f"✅ CONSOLIDATION COMPLETE")
        print(f"   Engrams consolidated: {consolidated_count}")
        print(f"   Total energy: {total_energy:.2f} kW")
        print(f"   Short-term memory: CLEARED")
        print(f"{'='*60}\n")

        return consolidated_count


class EnergyMemoryBank:
    """
    Complete energy memory system.

    Combines:
    - Short-term storage (working memory)
    - Long-term storage (persistent memory)
    - Consolidation (sleep-like transfer)
    - Retrieval (context-based recall)

    The hippocampus of the electric grid!
    """

    def __init__(self, db_path: str = "../energy_memory.db"):
        self.short_term = ShortTermEnergyMemory(capacity=7)
        self.long_term = LongTermEnergyMemory(db_path)
        self.consolidator = EnergyMemoryConsolidator(self.short_term, self.long_term)

        print(f"\n{'='*60}")
        print(f"🏦 ENERGY MEMORY BANK INITIALIZED")
        print(f"{'='*60}")
        print(f"   Short-term capacity: {self.short_term.capacity} engrams")
        print(f"   Long-term stored: {len(self.long_term.engrams)} engrams")
        print(f"   Total stored energy: {self.long_term.get_total_stored_energy():.2f} kW")
        print(f"{'='*60}\n")

    def store_energy(self, energy_amount: float, source: str,
                     spatial_location: str, context: Dict = None) -> EnergyEngram:
        """
        Store incoming energy.
        First goes to short-term, then consolidates to long-term.
        """
        # Determine temporal pattern
        hour = time.localtime().tm_hour
        if 6 <= hour < 12:
            temporal_pattern = "morning"
        elif 12 <= hour < 18:
            temporal_pattern = "afternoon"
        elif 18 <= hour < 22:
            temporal_pattern = "evening"
        else:
            temporal_pattern = "night"

        # Create energy engram
        engram = EnergyEngram(
            engram_id=f"ENG-{int(time.time()*1000)}",
            energy_amount=energy_amount,
            source=source,
            timestamp=time.time(),
            context=context or {},
            consolidation_strength=0.0,  # Weak initially
            retrieval_count=0,
            spatial_location=spatial_location,
            temporal_pattern=temporal_pattern
        )

        # Store in short-term memory
        self.short_term.store_energy(engram)

        # Check if consolidation needed
        if self.consolidator.should_consolidate():
            print(f"\n⚠️ Time to consolidate! (Working memory full or interval reached)")
            self.consolidator.consolidate()

        return engram

    def recall_energy(self, context_cue: Dict = None,
                     source: str = None,
                     temporal_pattern: str = None) -> List[EnergyEngram]:
        """
        Recall energy memories.
        Can use context, source, or time pattern as cues.
        """
        print(f"\n🔍 RECALLING ENERGY MEMORIES:")

        results = []

        # Try context-based recall
        if context_cue:
            results.extend(self.long_term.recall_by_context(context_cue))

        # Try source-based recall
        if source:
            results.extend(self.long_term.recall_by_source(source))

        # Try time-pattern recall
        if temporal_pattern:
            results.extend(self.long_term.recall_by_time_pattern(temporal_pattern))

        # If no cues, return strongest memories
        if not results:
            results = self.long_term.get_strongest_memories(10)

        print(f"   Found: {len(results)} matching memories")

        return results

    def get_total_energy(self) -> Dict:
        """Get total energy across all memory systems"""
        return {
            'short_term': self.short_term.get_available_energy(),
            'long_term': self.long_term.get_total_stored_energy(),
            'total': self.short_term.get_available_energy() + self.long_term.get_total_stored_energy()
        }

    def get_memory_status(self) -> Dict:
        """Get status of memory systems"""
        return {
            'short_term': {
                'capacity': self.short_term.capacity,
                'used': len(self.short_term.buffer),
                'energy': self.short_term.get_available_energy(),
                'is_full': self.short_term.is_full()
            },
            'long_term': {
                'total_engrams': len(self.long_term.engrams),
                'total_energy': self.long_term.get_total_stored_energy(),
                'strongest_memories': len([e for e in self.long_term.engrams.values()
                                          if e.consolidation_strength > 0.8])
            },
            'consolidation': {
                'last_consolidation': self.consolidator.last_consolidation,
                'time_until_next': self.consolidator.consolidation_interval -
                                   (time.time() - self.consolidator.last_consolidation)
            }
        }

    def sleep_cycle(self):
        """
        Manual sleep cycle trigger.
        Consolidates all short-term memories to long-term.
        """
        print(f"\n💤 INITIATING SLEEP CYCLE...")
        return self.consolidator.consolidate()


# ═══════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏦 LUXBIN ENERGY MEMORY BANK - BIOLOGICAL STORAGE")
    print("="*60 + "\n")

    # Initialize energy memory bank
    memory_bank = EnergyMemoryBank()

    # Simulate energy storage throughout a day
    print("\n--- Simulating Energy Collection Throughout Day ---\n")

    # Morning solar energy
    memory_bank.store_energy(
        energy_amount=50.0,
        source="solar",
        spatial_location="Grid-North",
        context={'weather': 'sunny', 'demand': 'low', 'hour': 8}
    )

    # Midday solar peak
    memory_bank.store_energy(
        energy_amount=120.0,
        source="solar",
        spatial_location="Grid-South",
        context={'weather': 'clear', 'demand': 'medium', 'hour': 12}
    )

    # Wind energy
    memory_bank.store_energy(
        energy_amount=80.0,
        source="wind",
        spatial_location="Grid-West",
        context={'weather': 'windy', 'demand': 'medium', 'hour': 14}
    )

    # Tesla battery discharge
    memory_bank.store_energy(
        energy_amount=200.0,
        source="tesla_fleet",
        spatial_location="Grid-East",
        context={'weather': 'clear', 'demand': 'high', 'hour': 18}
    )

    # Nuclear baseload
    memory_bank.store_energy(
        energy_amount=300.0,
        source="nuclear",
        spatial_location="Grid-Central",
        context={'weather': 'any', 'demand': 'constant', 'hour': 20}
    )

    # Evening solar (low)
    memory_bank.store_energy(
        energy_amount=30.0,
        source="solar",
        spatial_location="Grid-North",
        context={'weather': 'dusk', 'demand': 'high', 'hour': 19}
    )

    # Night wind
    memory_bank.store_energy(
        energy_amount=90.0,
        source="wind",
        spatial_location="Grid-West",
        context={'weather': 'stormy', 'demand': 'low', 'hour': 22}
    )

    # Check memory status
    print("\n--- Memory Status Before Sleep ---")
    status = memory_bank.get_memory_status()
    print(json.dumps(status, indent=2, default=str))

    # Sleep cycle (consolidation)
    print("\n--- Triggering Sleep Cycle ---")
    memory_bank.sleep_cycle()

    # Check memory status after sleep
    print("\n--- Memory Status After Sleep ---")
    status = memory_bank.get_memory_status()
    print(json.dumps(status, indent=2, default=str))

    # Test memory recall
    print("\n--- Testing Memory Recall ---\n")

    # Recall by context
    print("1. Recall high demand situations:")
    high_demand_memories = memory_bank.recall_energy(
        context_cue={'demand': 'high'}
    )
    print(f"   Found {len(high_demand_memories)} memories")
    for mem in high_demand_memories[:3]:
        print(f"   - {mem.source}: {mem.energy_amount:.2f} kW at {mem.spatial_location}")

    # Recall by source
    print("\n2. Recall all solar energy:")
    solar_memories = memory_bank.recall_energy(source='solar')
    print(f"   Found {len(solar_memories)} solar memories")
    total_solar = sum(m.energy_amount for m in solar_memories)
    print(f"   Total solar stored: {total_solar:.2f} kW")

    # Total energy
    print("\n--- Total Energy in Memory Banks ---")
    energy = memory_bank.get_total_energy()
    print(json.dumps(energy, indent=2))

    print("\n" + "="*60)
    print("✅ ENERGY MEMORY BANK OPERATIONAL")
    print("   Memories stored biologically")
    print("   Energy recalled by context")
    print("   Consolidation cycles functioning")
    print("="*60)
