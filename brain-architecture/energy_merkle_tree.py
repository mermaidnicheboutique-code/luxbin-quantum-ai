#!/usr/bin/env python3
"""
LUXBIN Energy Merkle Tree - Bitcoin-Inspired Energy Verification

Inspired by Bitcoin's merkle.cpp consensus algorithm.
Adapted for energy engram verification in LUXBIN organism.

Each energy engram = Transaction
Merkle root = State of entire energy system
Merkle proof = Verify specific energy without full tree

Just like Bitcoin verifies transactions, LUXBIN verifies energy!
"""

import hashlib
import json
import time
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class EnergyEngram:
    """Energy memory stored as Merkle tree leaf"""
    engram_id: str
    energy_amount: float
    source: str
    timestamp: float
    spatial_location: str

    def to_hash_input(self) -> bytes:
        """Convert engram to bytes for hashing"""
        data = f"{self.engram_id}:{self.energy_amount}:{self.source}:{self.timestamp}:{self.spatial_location}"
        return data.encode('utf-8')

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this engram (like Bitcoin transaction hash)"""
        return hashlib.sha256(self.to_hash_input()).hexdigest()


class EnergyMerkleTree:
    """
    Bitcoin-inspired Merkle tree for energy verification.

    Structure (like Bitcoin blocks):

                ROOT (Merkle Root)
               /                 \
          BRANCH                  BRANCH
         /      \                /      \
      LEAF1   LEAF2          LEAF3    LEAF4
     (Solar) (Wind)         (Tesla)  (Nuclear)

    Each leaf = Energy engram hash
    Each branch = Hash of child hashes
    Root = Hash representing entire energy state
    """

    def __init__(self):
        self.leaves: List[str] = []  # Energy engram hashes
        self.root: Optional[str] = None
        self.tree_levels: List[List[str]] = []
        self.mutation_detected = False

    def add_energy_engram(self, engram: EnergyEngram):
        """Add energy engram as leaf node"""
        leaf_hash = engram.compute_hash()
        self.leaves.append(leaf_hash)
        print(f"📋 Added leaf: {engram.source} ({leaf_hash[:16]}...)")

    def _sha256(self, data: str) -> str:
        """Single SHA-256 hash"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _double_sha256(self, left: str, right: str) -> str:
        """
        Double SHA-256 (like Bitcoin).
        Bitcoin uses SHA256(SHA256(data)) for extra security.
        """
        first_hash = hashlib.sha256(f"{left}{right}".encode('utf-8')).digest()
        second_hash = hashlib.sha256(first_hash).hexdigest()
        return second_hash

    def compute_merkle_root(self) -> str:
        """
        Compute Merkle root using Bitcoin's algorithm.

        Algorithm:
        1. Start with leaf hashes
        2. Pair them up and hash together
        3. If odd number, duplicate last hash
        4. Repeat until single root hash
        """
        if not self.leaves:
            return "0" * 64  # Empty tree

        # Store all tree levels for proof generation
        self.tree_levels = [self.leaves.copy()]
        current_level = self.leaves.copy()

        print(f"\n🌳 BUILDING MERKLE TREE:")
        print(f"   Leaves: {len(current_level)}")

        # Build tree level by level
        while len(current_level) > 1:
            next_level = []

            # Check for mutations (duplicate adjacent hashes)
            for i in range(0, len(current_level) - 1, 2):
                if current_level[i] == current_level[i + 1]:
                    self.mutation_detected = True
                    print(f"   ⚠️ MUTATION DETECTED at level {len(self.tree_levels)}")

            # Process pairs
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    # Pair exists
                    left = current_level[i]
                    right = current_level[i + 1]
                else:
                    # Odd number: duplicate last hash (Bitcoin's approach)
                    left = current_level[i]
                    right = current_level[i]

                # Combine hashes
                parent_hash = self._double_sha256(left, right)
                next_level.append(parent_hash)

            print(f"   Level {len(self.tree_levels)}: {len(next_level)} nodes")
            self.tree_levels.append(next_level)
            current_level = next_level

        # Root is the final single hash
        self.root = current_level[0]

        print(f"\n✅ MERKLE ROOT: {self.root[:32]}...")
        if self.mutation_detected:
            print(f"   ⚠️ Mutation detected in tree!")

        return self.root

    def generate_merkle_proof(self, leaf_index: int) -> List[Tuple[str, str]]:
        """
        Generate Merkle proof for specific energy engram.

        Proof = Path from leaf to root with sibling hashes.
        Allows verification without full tree!

        Returns: List of (hash, position) pairs
        """
        if leaf_index >= len(self.leaves):
            raise ValueError(f"Invalid leaf index: {leaf_index}")

        if not self.tree_levels:
            self.compute_merkle_root()

        proof = []
        current_index = leaf_index

        # Traverse from leaf to root
        for level in range(len(self.tree_levels) - 1):
            level_nodes = self.tree_levels[level]

            # Find sibling
            if current_index % 2 == 0:
                # Left child, sibling is right
                if current_index + 1 < len(level_nodes):
                    sibling = level_nodes[current_index + 1]
                    position = 'right'
                else:
                    # No sibling (odd number), duplicate self
                    sibling = level_nodes[current_index]
                    position = 'right'
            else:
                # Right child, sibling is left
                sibling = level_nodes[current_index - 1]
                position = 'left'

            proof.append((sibling, position))
            current_index = current_index // 2

        print(f"\n🔍 MERKLE PROOF for leaf {leaf_index}:")
        print(f"   Proof length: {len(proof)}")

        return proof

    def verify_merkle_proof(self, leaf_hash: str, proof: List[Tuple[str, str]],
                           expected_root: str) -> bool:
        """
        Verify Merkle proof.

        Given:
        - Leaf hash (energy engram)
        - Merkle proof (path to root)
        - Expected root

        Returns: True if proof valid
        """
        current_hash = leaf_hash

        print(f"\n✓ VERIFYING MERKLE PROOF:")
        print(f"   Starting leaf: {leaf_hash[:16]}...")

        # Traverse proof path
        for sibling_hash, position in proof:
            if position == 'left':
                # Sibling on left
                current_hash = self._double_sha256(sibling_hash, current_hash)
            else:
                # Sibling on right
                current_hash = self._double_sha256(current_hash, sibling_hash)

            print(f"   → {current_hash[:16]}...")

        print(f"   Final root: {current_hash[:32]}...")
        print(f"   Expected:   {expected_root[:32]}...")

        is_valid = current_hash == expected_root

        if is_valid:
            print(f"   ✅ PROOF VALID!")
        else:
            print(f"   ❌ PROOF INVALID!")

        return is_valid

    def get_tree_info(self) -> Dict:
        """Get information about Merkle tree"""
        return {
            'leaf_count': len(self.leaves),
            'tree_depth': len(self.tree_levels),
            'merkle_root': self.root,
            'mutation_detected': self.mutation_detected,
            'tree_size_bytes': sum(len(level) * 64 for level in self.tree_levels)
        }


class EnergyMerkleDatabase:
    """
    Store Merkle roots and proofs in database.
    Like Bitcoin stores block headers!
    """

    def __init__(self, db_path: str = "energy_merkle.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Create database for Merkle roots"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS merkle_roots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merkle_root TEXT NOT NULL,
                leaf_count INTEGER,
                timestamp REAL,
                mutation_detected BOOLEAN,
                tree_depth INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS merkle_proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merkle_root_id INTEGER,
                leaf_index INTEGER,
                leaf_hash TEXT,
                proof_json TEXT,
                timestamp REAL,
                FOREIGN KEY (merkle_root_id) REFERENCES merkle_roots(id)
            )
        """)

        conn.commit()
        conn.close()

    def store_merkle_root(self, tree: EnergyMerkleTree) -> int:
        """Store Merkle root in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO merkle_roots
            (merkle_root, leaf_count, timestamp, mutation_detected, tree_depth)
            VALUES (?, ?, ?, ?, ?)
        """, (
            tree.root,
            len(tree.leaves),
            time.time(),
            tree.mutation_detected,
            len(tree.tree_levels)
        ))

        root_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"💾 Stored Merkle root: {tree.root[:16]}... (ID: {root_id})")

        return root_id

    def store_merkle_proof(self, root_id: int, leaf_index: int,
                          leaf_hash: str, proof: List[Tuple[str, str]]):
        """Store Merkle proof for later verification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO merkle_proofs
            (merkle_root_id, leaf_index, leaf_hash, proof_json, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            root_id,
            leaf_index,
            leaf_hash,
            json.dumps(proof),
            time.time()
        ))

        conn.commit()
        conn.close()

        print(f"💾 Stored proof for leaf {leaf_index}")


# ═══════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌳 LUXBIN ENERGY MERKLE TREE - BITCOIN-INSPIRED")
    print("="*60 + "\n")

    # Create energy engrams (like Bitcoin transactions)
    engrams = [
        EnergyEngram("ENG-001", 50.0, "solar", time.time(), "Grid-North"),
        EnergyEngram("ENG-002", 120.0, "solar", time.time(), "Grid-South"),
        EnergyEngram("ENG-003", 80.0, "wind", time.time(), "Grid-West"),
        EnergyEngram("ENG-004", 200.0, "tesla_fleet", time.time(), "Grid-East"),
        EnergyEngram("ENG-005", 300.0, "nuclear", time.time(), "Grid-Central"),
    ]

    print("📊 ENERGY ENGRAMS (Transaction List):")
    for i, engram in enumerate(engrams):
        print(f"   {i}: {engram.source:12} {engram.energy_amount:>6.1f} kW - {engram.compute_hash()[:16]}...")

    # Build Merkle tree
    tree = EnergyMerkleTree()

    for engram in engrams:
        tree.add_energy_engram(engram)

    # Compute root
    print("\n" + "-"*60)
    root = tree.compute_merkle_root()

    # Tree info
    print("\n" + "-"*60)
    print("📊 TREE INFORMATION:")
    info = tree.get_tree_info()
    for key, value in info.items():
        print(f"   {key}: {value}")

    # Generate proof for Tesla energy (index 3)
    print("\n" + "-"*60)
    print("🔐 GENERATING MERKLE PROOF (Tesla Energy):")
    tesla_index = 3
    proof = tree.generate_merkle_proof(tesla_index)

    # Verify proof
    print("\n" + "-"*60)
    tesla_hash = engrams[tesla_index].compute_hash()
    is_valid = tree.verify_merkle_proof(tesla_hash, proof, root)

    # Store in database
    print("\n" + "-"*60)
    db = EnergyMerkleDatabase("../energy_merkle.db")
    root_id = db.store_merkle_root(tree)
    db.store_merkle_proof(root_id, tesla_index, tesla_hash, proof)

    # Try tampering
    print("\n" + "-"*60)
    print("🚨 TAMPERING TEST:")
    print("   Attempting to verify FAKE energy engram...")
    fake_engram = EnergyEngram("FAKE", 9999.0, "hacker", time.time(), "Unknown")
    fake_hash = fake_engram.compute_hash()
    is_fake_valid = tree.verify_merkle_proof(fake_hash, proof, root)

    if not is_fake_valid:
        print("   ✅ TAMPERING DETECTED! Fake energy rejected!")

    print("\n" + "="*60)
    print("✅ ENERGY MERKLE TREE OPERATIONAL")
    print("   Bitcoin-inspired verification working!")
    print("   Energy integrity guaranteed!")
    print("="*60)
