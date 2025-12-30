#!/usr/bin/env python3
"""
LUXBIN DIVINE - Web3 Bridge
Connects Python immune system to blockchain smart contracts

Author: Nichole Christie
License: MIT
"""

import json
import os
import asyncio
from typing import Dict, List, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
import hashlib


class Web3Bridge:
    """Bridge between Python immune system and blockchain contracts"""

    def __init__(self, network='base-sepolia', private_key=None, deployment_file='deployment_report.json'):
        """Initialize Web3 bridge

        Args:
            network: Network name
            private_key: Private key for signing transactions
            deployment_file: Path to deployment report JSON
        """
        # Load deployment configuration
        with open(deployment_file, 'r') as f:
            self.deployment = json.load(f)

        # Connect to blockchain
        rpc_url = self.deployment['network_config']['rpc']
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # Add PoA middleware for some testnets
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        assert self.w3.is_connected(), "Failed to connect to blockchain"

        # Set up account
        if private_key:
            self.account: LocalAccount = Account.from_key(private_key)
        else:
            # Use environment variable
            key = os.getenv('IMMUNE_SYSTEM_PRIVATE_KEY')
            if not key:
                raise ValueError("No private key provided and IMMUNE_SYSTEM_PRIVATE_KEY not set")
            self.account = Account.from_key(key)

        print(f"✅ Connected to {self.deployment['network']}")
        print(f"👤 Account: {self.account.address}")

        # Load contract instances
        self.load_contracts()

    def load_contracts(self):
        """Load smart contract instances"""
        contracts_dir = '.'  # Directory containing ABIs

        self.contracts = {}

        for name, info in self.deployment['contracts'].items():
            abi_file = f"{contracts_dir}/{name}.abi.json"

            if os.path.exists(abi_file):
                with open(abi_file, 'r') as f:
                    abi = json.load(f)

                self.contracts[name] = self.w3.eth.contract(
                    address=info['address'],
                    abi=abi
                )
                print(f"   Loaded {name} contract")

    async def report_threat_detection(self, cell_id: int, threat_data: Dict) -> str:
        """Report a threat detection to the blockchain

        Args:
            cell_id: Token ID of the detector cell
            threat_data: Threat information

        Returns:
            Transaction hash
        """
        staking_contract = self.contracts['ImmuneStaking']

        # Create threat hash
        threat_hash = self._create_threat_hash(threat_data)

        # Build transaction
        txn = staking_contract.functions.reportThreat(
            cell_id,
            threat_hash
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
        })

        # Sign and send
        signed_txn = self.account.sign_transaction(txn)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        print(f"🔍 Threat reported - TX: {txn_hash.hex()}")

        # Wait for confirmation (in background)
        asyncio.create_task(self._wait_for_receipt(txn_hash, "Threat detection"))

        return txn_hash.hex()

    async def report_false_positive(self, cell_id: int) -> str:
        """Report a false positive

        Args:
            cell_id: Token ID of the detector cell

        Returns:
            Transaction hash
        """
        staking_contract = self.contracts['ImmuneStaking']

        txn = staking_contract.functions.reportFalsePositive(
            cell_id
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price,
        })

        signed_txn = self.account.sign_transaction(txn)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        print(f"⚠️  False positive reported - TX: {txn_hash.hex()}")

        asyncio.create_task(self._wait_for_receipt(txn_hash, "False positive"))

        return txn_hash.hex()

    async def record_memory_storage(self, cell_id: int) -> str:
        """Record memory storage on-chain

        Args:
            cell_id: Token ID of the memory cell

        Returns:
            Transaction hash
        """
        staking_contract = self.contracts['ImmuneStaking']

        txn = staking_contract.functions.recordMemoryStorage(
            cell_id
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price,
        })

        signed_txn = self.account.sign_transaction(txn)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        print(f"🧠 Memory stored - TX: {txn_hash.hex()}")

        asyncio.create_task(self._wait_for_receipt(txn_hash, "Memory storage"))

        return txn_hash.hex()

    async def record_regulatory_approval(self, cell_id: int) -> str:
        """Record regulatory approval on-chain

        Args:
            cell_id: Token ID of the regulatory cell

        Returns:
            Transaction hash
        """
        staking_contract = self.contracts['ImmuneStaking']

        txn = staking_contract.functions.recordRegulatoryApproval(
            cell_id
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price,
        })

        signed_txn = self.account.sign_transaction(txn)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        print(f"⚖️  Regulatory approval - TX: {txn_hash.hex()}")

        asyncio.create_task(self._wait_for_receipt(txn_hash, "Regulatory approval"))

        return txn_hash.hex()

    async def record_defense_execution(self, cell_id: int, target_address: str) -> str:
        """Record defense execution on-chain

        Args:
            cell_id: Token ID of the defender cell
            target_address: Address that was defended against

        Returns:
            Transaction hash
        """
        staking_contract = self.contracts['ImmuneStaking']

        target_hash = self._hash_address(target_address)

        txn = staking_contract.functions.recordDefense(
            cell_id,
            target_hash
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price,
        })

        signed_txn = self.account.sign_transaction(txn)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        print(f"⚔️  Defense executed - TX: {txn_hash.hex()}")

        asyncio.create_task(self._wait_for_receipt(txn_hash, "Defense execution"))

        return txn_hash.hex()

    def get_validator_info(self, address: str) -> Dict:
        """Get validator information from blockchain

        Args:
            address: Validator address

        Returns:
            Validator information dictionary
        """
        staking_contract = self.contracts['ImmuneStaking']

        info = staking_contract.functions.getValidator(address).call()

        return {
            'staked_amount': info[0],
            'staked_at': info[1],
            'rewards_earned': info[2],
            'penalties_paid': info[3],
            'is_active': info[4],
            'cell_count': info[5]
        }

    def get_staked_cells(self, address: str) -> List[int]:
        """Get staked cells for a validator

        Args:
            address: Validator address

        Returns:
            List of cell token IDs
        """
        staking_contract = self.contracts['ImmuneStaking']
        return staking_contract.functions.getStakedCells(address).call()

    def get_cell_data(self, token_id: int) -> Dict:
        """Get immune cell data from blockchain

        Args:
            token_id: Cell token ID

        Returns:
            Cell data dictionary
        """
        immune_cell_contract = self.contracts['ImmuneCell']

        cell = immune_cell_contract.functions.getCell(token_id).call()

        return {
            'cell_type': ['DETECTOR', 'DEFENDER', 'MEMORY', 'REGULATORY'][cell[0]],
            'reputation': cell[1],
            'true_positives': cell[2],
            'false_positives': cell[3],
            'threats_detected': cell[4],
            'responses_executed': cell[5],
            'created_at': cell[6],
            'last_active_at': cell[7],
            'is_active': cell[8],
            'quantum_fingerprint': cell[9]
        }

    def _create_threat_hash(self, threat_data: Dict) -> bytes:
        """Create a hash of threat data

        Args:
            threat_data: Threat information

        Returns:
            32-byte hash
        """
        threat_str = json.dumps(threat_data, sort_keys=True)
        hash_hex = hashlib.sha256(threat_str.encode()).hexdigest()
        return bytes.fromhex(hash_hex)

    def _hash_address(self, address: str) -> bytes:
        """Hash an address

        Args:
            address: Ethereum address

        Returns:
            32-byte hash
        """
        return Web3.keccak(text=address)

    async def _wait_for_receipt(self, txn_hash: bytes, action_name: str):
        """Wait for transaction receipt in background

        Args:
            txn_hash: Transaction hash
            action_name: Name of the action for logging
        """
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=120)
            if receipt['status'] == 1:
                print(f"   ✅ {action_name} confirmed - Block: {receipt['blockNumber']}")
            else:
                print(f"   ❌ {action_name} failed")
        except Exception as e:
            print(f"   ❌ {action_name} error: {e}")


class ImmuneSystemWithBlockchain:
    """Immune system with blockchain integration"""

    def __init__(self, web3_bridge: Web3Bridge, detector_cells: List[int]):
        """Initialize immune system with blockchain

        Args:
            web3_bridge: Web3 bridge instance
            detector_cells: List of detector cell token IDs owned by this instance
        """
        self.bridge = web3_bridge
        self.detector_cells = detector_cells
        self.current_detector_index = 0

    async def process_transaction(self, transaction: Dict) -> Optional[Dict]:
        """Process transaction with blockchain rewards

        Args:
            transaction: Transaction data

        Returns:
            Result dictionary if threat detected
        """
        # Get next detector cell (round-robin)
        cell_id = self.detector_cells[self.current_detector_index]
        self.current_detector_index = (self.current_detector_index + 1) % len(self.detector_cells)

        # Simulate threat detection (replace with actual quantum scan)
        is_threat = transaction.get('suspicious', False)

        if is_threat:
            # Report to blockchain (earns rewards!)
            txn_hash = await self.bridge.report_threat_detection(cell_id, transaction)

            return {
                'action': 'QUARANTINE',
                'cell_id': cell_id,
                'transaction_hash': txn_hash,
                'threat_score': 0.95
            }

        return None


# Example usage
async def demo():
    """Demo blockchain integration"""
    print("🦠 LUXBIN DIVINE - Blockchain Integration Demo\n")

    # Initialize bridge
    bridge = Web3Bridge(
        network='base-sepolia',
        deployment_file='deployment_report.json'
    )

    # Get validator info
    validator_info = bridge.get_validator_info(bridge.account.address)
    print(f"\n📊 Validator Status:")
    print(f"   Staked: {Web3.from_wei(validator_info['staked_amount'], 'ether')} LUX")
    print(f"   Rewards: {Web3.from_wei(validator_info['rewards_earned'], 'ether')} LUX")
    print(f"   Active: {validator_info['is_active']}")
    print(f"   Cells: {validator_info['cell_count']}")

    # Get staked cells
    cells = bridge.get_staked_cells(bridge.account.address)
    print(f"\n🧬 Staked Cells: {cells}")

    if cells:
        # Initialize immune system
        immune_system = ImmuneSystemWithBlockchain(bridge, cells)

        # Process a suspicious transaction
        suspicious_tx = {
            'hash': '0xabc123',
            'from': '0xmalicious',
            'suspicious': True,
            'threat_score': 0.95
        }

        result = await immune_system.process_transaction(suspicious_tx)

        if result:
            print(f"\n⚠️  Threat detected and reported!")
            print(f"   Cell ID: {result['cell_id']}")
            print(f"   TX Hash: {result['transaction_hash']}")
            print(f"   💰 Reward: 10 LUX tokens earned!")


if __name__ == "__main__":
    asyncio.run(demo())
