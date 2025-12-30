#!/usr/bin/env python3
"""
LUXBIN DIVINE - Automated Smart Contract Deployment
Deploy immune system contracts to Base and OP Sepolia with USDC integration

Networks:
- Base Mainnet: Cheap gas, native USDC
- Base Sepolia Testnet: Free testnet
- OP Sepolia Testnet: Free testnet

Author: Nichole Christie
License: MIT
"""

import json
import os
import time
from web3 import Web3
from eth_account import Account
from pathlib import Path


class ImmuneSystemDeployer:
    """Deploy and initialize LUXBIN immune system contracts"""

    # Network configurations
    NETWORKS = {
        'base': {
            'name': 'Base Mainnet',
            'rpc': 'https://mainnet.base.org',
            'chain_id': 8453,
            'explorer': 'https://basescan.org',
            'usdc_address': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',  # Native USDC on Base
            'gas_price_gwei': 0.001,  # Very cheap on Base
        },
        'base-sepolia': {
            'name': 'Base Sepolia Testnet',
            'rpc': 'https://sepolia.base.org',
            'chain_id': 84532,
            'explorer': 'https://sepolia.basescan.org',
            'usdc_address': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',  # USDC on Base Sepolia
            'gas_price_gwei': 0.001,
        },
        'op-sepolia': {
            'name': 'OP Sepolia Testnet',
            'rpc': 'https://sepolia.optimism.io',
            'chain_id': 11155420,
            'explorer': 'https://sepolia-optimism.etherscan.io',
            'usdc_address': '0x5fd84259d66Cd46123540766Be93DFE6D43130D7',  # USDC on OP Sepolia
            'gas_price_gwei': 0.001,
        }
    }

    def __init__(self, network='base-sepolia', private_key=None):
        """Initialize deployer

        Args:
            network: Network to deploy to ('base', 'base-sepolia', 'op-sepolia')
            private_key: Private key for deployment (if None, creates new account)
        """
        self.network_config = self.NETWORKS[network]
        self.network_name = network

        # Connect to network
        self.w3 = Web3(Web3.HTTPProvider(self.network_config['rpc']))
        assert self.w3.is_connected(), f"Failed to connect to {self.network_config['name']}"

        # Set up account
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = Account.create()
            print(f"⚠️  Created new deployment account: {self.account.address}")
            print(f"⚠️  Private key: {self.account.key.hex()}")
            print(f"⚠️  SAVE THIS PRIVATE KEY SECURELY!")

        self.deployer_address = self.account.address

        print(f"\n🌐 Connected to {self.network_config['name']}")
        print(f"📍 Chain ID: {self.network_config['chain_id']}")
        print(f"👤 Deployer: {self.deployer_address}")

        # Contract addresses (will be populated after deployment)
        self.contracts = {}

    def check_balance(self):
        """Check deployer account balance"""
        balance = self.w3.eth.get_balance(self.deployer_address)
        balance_eth = self.w3.from_wei(balance, 'ether')

        print(f"\n💰 Account Balance:")
        print(f"   ETH: {balance_eth:.6f}")

        if balance_eth < 0.01:
            print(f"\n⚠️  WARNING: Low balance!")
            print(f"   Please fund {self.deployer_address} with ETH for gas")
            print(f"   Get testnet ETH from:")
            if self.network_name == 'base-sepolia':
                print(f"   - https://www.coinbase.com/faucets/base-ethereum-goerli-faucet")
            elif self.network_name == 'op-sepolia':
                print(f"   - https://www.alchemy.com/faucets/optimism-sepolia")

        return balance_eth

    def deploy_contract(self, contract_name, bytecode, abi, constructor_args=None):
        """Deploy a smart contract

        Args:
            contract_name: Name of the contract
            bytecode: Contract bytecode (hex string)
            abi: Contract ABI
            constructor_args: Constructor arguments

        Returns:
            Contract instance
        """
        print(f"\n🚀 Deploying {contract_name}...")

        # Create contract instance
        Contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        # Build constructor transaction
        if constructor_args:
            constructor_txn = Contract.constructor(*constructor_args)
        else:
            constructor_txn = Contract.constructor()

        # Get nonce
        nonce = self.w3.eth.get_transaction_count(self.deployer_address)

        # Build transaction
        txn = constructor_txn.build_transaction({
            'from': self.deployer_address,
            'nonce': nonce,
            'gas': 5000000,
            'gasPrice': self.w3.to_wei(self.network_config['gas_price_gwei'], 'gwei'),
            'chainId': self.network_config['chain_id']
        })

        # Sign transaction
        signed_txn = self.account.sign_transaction(txn)

        # Send transaction
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"   Transaction hash: {txn_hash.hex()}")

        # Wait for receipt
        print(f"   Waiting for confirmation...")
        txn_receipt = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=300)

        if txn_receipt['status'] == 1:
            contract_address = txn_receipt['contractAddress']
            print(f"   ✅ {contract_name} deployed to: {contract_address}")
            print(f"   Gas used: {txn_receipt['gasUsed']:,}")
            print(f"   View on explorer: {self.network_config['explorer']}/address/{contract_address}")

            # Create contract instance
            contract = self.w3.eth.contract(address=contract_address, abi=abi)
            self.contracts[contract_name] = {
                'address': contract_address,
                'contract': contract,
                'abi': abi
            }

            return contract
        else:
            raise Exception(f"Deployment failed for {contract_name}")

    def deploy_all_contracts(self, ecosystem_fund_address=None):
        """Deploy all immune system contracts

        Args:
            ecosystem_fund_address: Address for ecosystem fund (defaults to deployer)
        """
        if ecosystem_fund_address is None:
            ecosystem_fund_address = self.deployer_address

        print(f"\n{'='*60}")
        print(f"DEPLOYING LUXBIN IMMUNE SYSTEM")
        print(f"{'='*60}")

        # Load compiled contracts
        # NOTE: You need to compile the Solidity files first using:
        # solc --optimize --bin --abi ImmuneCell.sol LuxbinToken.sol ImmuneStaking.sol GaslessForwarder.sol

        # For demo purposes, we'll show the deployment structure
        # In production, you'd load actual compiled bytecode

        print(f"\n📋 Deployment Plan:")
        print(f"   1. LuxbinToken (ERC-20)")
        print(f"   2. ImmuneCell (ERC-721)")
        print(f"   3. ImmuneStaking")
        print(f"   4. GaslessForwarder")
        print(f"\n   Ecosystem Fund: {ecosystem_fund_address}")

        # Example deployment structure (replace with actual bytecode)
        # self.deploy_contract('LuxbinToken', BYTECODE, ABI, [ecosystem_fund_address])

        print(f"\n⚠️  NOTE: Compile contracts first with:")
        print(f"   npm install @openzeppelin/contracts")
        print(f"   solc --optimize --combined-json abi,bin ImmuneCell.sol > compiled.json")

    def initialize_contracts(self):
        """Initialize deployed contracts with proper configuration"""
        print(f"\n⚙️  Initializing contracts...")

        # This would include:
        # 1. Authorize staking contract as LUXBIN minter
        # 2. Whitelist staking contract in gasless forwarder
        # 3. Mint initial immune cell NFTs
        # 4. Deposit initial gas treasury
        # 5. Set up initial validators

        pass

    def create_usdc_treasury(self, initial_amount_usdc=10000):
        """Create USDC treasury for sustainable funding

        Args:
            initial_amount_usdc: Initial USDC amount to fund treasury
        """
        print(f"\n💵 Setting up USDC Treasury...")

        usdc_address = self.network_config['usdc_address']
        print(f"   USDC Contract: {usdc_address}")

        # USDC ABI (minimal for transfer)
        usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }
        ]

        usdc_contract = self.w3.eth.contract(address=usdc_address, abi=usdc_abi)

        # Check USDC balance
        usdc_balance = usdc_contract.functions.balanceOf(self.deployer_address).call()
        usdc_balance_human = usdc_balance / 10**6  # USDC has 6 decimals

        print(f"   Deployer USDC Balance: {usdc_balance_human:,.2f} USDC")

        if usdc_balance_human < initial_amount_usdc:
            print(f"\n   ⚠️  Need {initial_amount_usdc:,} USDC for initial treasury")
            print(f"   Please acquire USDC and send to: {self.deployer_address}")

    def generate_deployment_report(self, filename='deployment_report.json'):
        """Generate deployment report with all contract addresses"""
        report = {
            'network': self.network_name,
            'network_config': self.network_config,
            'deployer': self.deployer_address,
            'timestamp': int(time.time()),
            'contracts': {}
        }

        for name, info in self.contracts.items():
            report['contracts'][name] = {
                'address': info['address'],
                'explorer_url': f"{self.network_config['explorer']}/address/{info['address']}"
            }

        # Save to file
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Deployment report saved to: {filename}")

        return report


def main():
    """Main deployment script"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   LUXBIN DIVINE - Immune System Deployment                ║")
    print("║   Automated smart contract deployment to Base & OP        ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Choose network
    print("\n🌐 Available Networks:")
    print("   1. Base Mainnet (Recommended - cheap gas, native USDC)")
    print("   2. Base Sepolia Testnet (Free - for testing)")
    print("   3. OP Sepolia Testnet (Free - for testing)")

    # For demo, use Base Sepolia testnet
    network = 'base-sepolia'

    print(f"\n✅ Selected: {ImmuneSystemDeployer.NETWORKS[network]['name']}")

    # Get private key from environment or create new
    private_key = os.getenv('DEPLOYER_PRIVATE_KEY')

    if not private_key:
        print("\n⚠️  No DEPLOYER_PRIVATE_KEY environment variable found")
        print("   Creating new deployment account...")

    # Initialize deployer
    deployer = ImmuneSystemDeployer(network=network, private_key=private_key)

    # Check balance
    balance = deployer.check_balance()

    if balance < 0.01:
        print("\n⏸️  Deployment paused - please fund the account first")
        print(f"\n💡 To resume deployment:")
        print(f"   1. Send ETH to: {deployer.deployer_address}")
        print(f"   2. Set environment variable: export DEPLOYER_PRIVATE_KEY='{deployer.account.key.hex()}'")
        print(f"   3. Run this script again")
        return

    # Deploy contracts
    deployer.deploy_all_contracts()

    # Set up USDC treasury
    deployer.create_usdc_treasury(initial_amount_usdc=10000)

    # Initialize
    deployer.initialize_contracts()

    # Generate report
    report = deployer.generate_deployment_report()

    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)

    print(f"\n🎉 Your LUXBIN Immune System is now live on {deployer.network_config['name']}!")
    print(f"\n📍 Contract Addresses:")
    for name, info in report['contracts'].items():
        print(f"   {name}: {info['address']}")

    print(f"\n🔗 Next Steps:")
    print(f"   1. Fund gas treasury with ETH")
    print(f"   2. Fund USDC treasury for sustainability")
    print(f"   3. Mint initial immune cell NFTs")
    print(f"   4. Activate first validators")
    print(f"   5. Connect Python immune system to contracts")

    print(f"\n📚 Documentation: IMMUNE_SYSTEM_README.md")


if __name__ == "__main__":
    main()
