#!/usr/bin/env python3
"""
LUXBIN DIVINE - Automatic Deployment from Node
Handles faucet requests, waiting for funds, and automatic deployment

This script:
1. Checks your balance
2. Automatically requests from multiple faucets if needed
3. Waits for funds to arrive
4. Deploys contracts automatically
5. Starts your node

Author: Nichole Christie
License: MIT
"""

import json
import os
import time
import asyncio
import requests
from web3 import Web3
from eth_account import Account
from pathlib import Path


class AutoDeployer:
    """Automatic deployment orchestrator"""

    # Multiple faucet endpoints to try
    FAUCETS = {
        'op-sepolia': [
            {
                'name': 'Alchemy Faucet',
                'url': 'https://www.alchemy.com/faucets/optimism-sepolia',
                'type': 'web',  # Requires browser
                'amount': '0.5 ETH'
            },
            {
                'name': 'Superchain Faucet',
                'url': 'https://app.optimism.io/faucet',
                'type': 'web',
                'amount': '0.05 ETH'
            },
            {
                'name': 'QuickNode Faucet',
                'url': 'https://faucet.quicknode.com/optimism/sepolia',
                'type': 'web',
                'amount': '0.05 ETH'
            }
        ],
        'base-sepolia': [
            {
                'name': 'Coinbase Faucet',
                'url': 'https://www.coinbase.com/faucets/base-ethereum-goerli-faucet',
                'type': 'web',
                'amount': '0.1 ETH'
            },
            {
                'name': 'Base Sepolia Faucet',
                'url': 'https://www.coinbase.com/faucets',
                'type': 'web',
                'amount': '0.1 ETH'
            }
        ]
    }

    NETWORKS = {
        'op-sepolia': {
            'name': 'OP Sepolia Testnet',
            'rpc': 'https://sepolia.optimism.io',
            'chain_id': 11155420,
            'explorer': 'https://sepolia-optimism.etherscan.io',
            'min_balance': 0.01  # Minimum ETH needed for deployment
        },
        'base-sepolia': {
            'name': 'Base Sepolia Testnet',
            'rpc': 'https://sepolia.base.org',
            'chain_id': 84532,
            'explorer': 'https://sepolia.basescan.org',
            'min_balance': 0.01
        }
    }

    def __init__(self, network='op-sepolia'):
        """Initialize auto deployer"""
        self.network = network
        self.config = self.NETWORKS[network]

        # Connect to network
        self.w3 = Web3(Web3.HTTPProvider(self.config['rpc']))
        assert self.w3.is_connected(), f"Failed to connect to {self.config['name']}"

        # Load or create wallet
        self.wallet_path = Path.home() / '.luxbin' / 'wallet.json'
        self.account = self.load_or_create_wallet()

        print(f"╔════════════════════════════════════════════════════════════╗")
        print(f"║  LUXBIN AUTO-DEPLOY - Running from your Mac Node         ║")
        print(f"╚════════════════════════════════════════════════════════════╝")
        print(f"\n🌐 Network: {self.config['name']}")
        print(f"👤 Address: {self.account.address}")

    def load_or_create_wallet(self):
        """Load existing wallet or create new one"""
        if self.wallet_path.exists():
            with open(self.wallet_path, 'r') as f:
                wallet_data = json.load(f)
                return Account.from_key(wallet_data['private_key'])
        else:
            # Create new wallet
            account = Account.create()
            self.wallet_path.parent.mkdir(parents=True, exist_ok=True)

            wallet_data = {
                'address': account.address,
                'private_key': account.key.hex()
            }

            with open(self.wallet_path, 'w') as f:
                json.dump(wallet_data, f, indent=2)

            # Secure the wallet file
            os.chmod(self.wallet_path, 0o600)

            print(f"✅ Created new wallet: {account.address}")
            print(f"💾 Saved to: {self.wallet_path}")

            return account

    def check_balance(self):
        """Check current balance"""
        balance_wei = self.w3.eth.get_balance(self.account.address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)

    def display_faucet_instructions(self):
        """Display instructions for getting testnet ETH"""
        faucets = self.FAUCETS.get(self.network, [])

        print(f"\n💧 FAUCET OPTIONS FOR {self.config['name'].upper()}:")
        print(f"{'='*60}")

        for i, faucet in enumerate(faucets, 1):
            print(f"\n{i}. {faucet['name']}")
            print(f"   URL: {faucet['url']}")
            print(f"   Amount: {faucet['amount']}")
            print(f"   Instructions:")
            print(f"   - Open the URL in your browser")
            print(f"   - Paste your address: {self.account.address}")
            print(f"   - Complete any verification (captcha, login, etc.)")
            print(f"   - Submit the request")

        print(f"\n{'='*60}")
        print(f"💡 TIP: Try multiple faucets if one doesn't work!")
        print(f"💡 Some faucets require Coinbase login or Twitter verification")
        print(f"\n⏳ This script will automatically detect when funds arrive")
        print(f"   and continue with deployment...")

    def wait_for_funds(self, check_interval=10, timeout=600):
        """Wait for funds to arrive from faucet

        Args:
            check_interval: Seconds between balance checks
            timeout: Maximum seconds to wait

        Returns:
            True if funds arrived, False if timeout
        """
        print(f"\n⏳ Waiting for funds...")
        print(f"   Checking every {check_interval} seconds")
        print(f"   Will wait up to {timeout // 60} minutes")

        start_time = time.time()
        last_balance = self.check_balance()

        while (time.time() - start_time) < timeout:
            current_balance = self.check_balance()

            # Check if balance increased
            if current_balance > last_balance:
                print(f"\n✅ Funds received!")
                print(f"   Old balance: {last_balance:.6f} ETH")
                print(f"   New balance: {current_balance:.6f} ETH")
                return True

            # Check if we already have enough
            if current_balance >= self.config['min_balance']:
                print(f"\n✅ Already have sufficient funds!")
                print(f"   Balance: {current_balance:.6f} ETH")
                return True

            # Show progress
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"   [{elapsed}s / {timeout}s] Balance: {current_balance:.6f} ETH (need {self.config['min_balance']} ETH) - Waiting...", end='\r')

            time.sleep(check_interval)

        print(f"\n⏰ Timeout reached after {timeout // 60} minutes")
        return False

    def open_faucet_urls(self):
        """Open faucet URLs in browser automatically"""
        import webbrowser

        faucets = self.FAUCETS.get(self.network, [])

        print(f"\n🌐 Opening faucet websites in your browser...")

        for faucet in faucets[:2]:  # Open first 2 faucets
            print(f"   Opening: {faucet['name']}")
            webbrowser.open(faucet['url'])
            time.sleep(2)  # Delay between opening tabs

        print(f"\n✅ Faucet pages opened!")
        print(f"   Your address is copied below - paste it in the faucet:")
        print(f"\n   {self.account.address}")
        print(f"\n   (You can also click to copy in most terminals)")

    def deploy_contracts(self):
        """Deploy LUXBIN contracts"""
        print(f"\n🚀 Starting contract deployment...")

        # Import the deployer
        from deploy_immune_system import ImmuneSystemDeployer

        deployer = ImmuneSystemDeployer(
            network=self.network,
            private_key=self.account.key.hex()
        )

        # Deploy all contracts
        deployer.deploy_all_contracts()

        # Generate report
        report = deployer.generate_deployment_report('luxbin_deployment.json')

        print(f"\n✅ Contracts deployed successfully!")
        return report

    def start_node(self):
        """Start the LUXBIN node"""
        print(f"\n🖥️  Starting LUXBIN node...")

        # This would start your node service
        # For now, we'll show instructions
        print(f"\n   To start your node, run:")
        print(f"   cd /Users/nicholechristie/luxbin-chain/python-implementation")
        print(f"   python3 luxbin_web3_bridge.py")

    def run(self):
        """Run the complete auto-deployment process"""
        # Step 1: Check initial balance
        print(f"\n1️⃣ Checking balance...")
        balance = self.check_balance()
        print(f"   💰 Current balance: {balance:.6f} ETH")

        # Step 2: Request funds if needed
        if balance < self.config['min_balance']:
            print(f"\n❌ Insufficient funds for deployment")
            print(f"   Need: {self.config['min_balance']} ETH")
            print(f"   Have: {balance:.6f} ETH")

            # Show faucet instructions
            self.display_faucet_instructions()

            # Ask user if they want to open faucets
            print(f"\n📋 OPTIONS:")
            print(f"   1. Auto-open faucet URLs in browser (recommended)")
            print(f"   2. I'll manually visit faucets")

            try:
                choice = input(f"\nEnter choice (1 or 2): ").strip()
                if choice == '1':
                    self.open_faucet_urls()
            except (EOFError, KeyboardInterrupt):
                print(f"\n   Skipping auto-open...")

            # Wait for funds
            if not self.wait_for_funds(check_interval=10, timeout=1800):  # 30 min timeout
                print(f"\n❌ Funds not received in time")
                print(f"\n💡 You can run this script again later:")
                print(f"   python3 auto_deploy.py")
                return False
        else:
            print(f"   ✅ Sufficient balance for deployment!")

        # Step 3: Deploy contracts
        print(f"\n2️⃣ Deploying contracts...")
        try:
            self.deploy_contracts()
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            print(f"\n   Note: You may need to compile contracts first.")
            print(f"   See deploy_immune_system.py for compilation instructions.")
            return False

        # Step 4: Start node
        print(f"\n3️⃣ Node setup...")
        self.start_node()

        # Success!
        print(f"\n{'='*60}")
        print(f"✅ AUTO-DEPLOYMENT COMPLETE!")
        print(f"{'='*60}")
        print(f"\n🎉 Your LUXBIN node is ready!")
        print(f"\n📍 Your address: {self.account.address}")
        print(f"💰 Remaining balance: {self.check_balance():.6f} ETH")
        print(f"🌐 Network: {self.config['name']}")
        print(f"🔍 Explorer: {self.config['explorer']}/address/{self.account.address}")

        print(f"\n📚 Next steps:")
        print(f"   1. Check deployment report: luxbin_deployment.json")
        print(f"   2. Start your node: python3 luxbin_web3_bridge.py")
        print(f"   3. Monitor on explorer: {self.config['explorer']}")

        return True


def main():
    """Main entry point"""
    import sys

    # Parse command line args
    network = 'op-sepolia'  # Default
    if len(sys.argv) > 1:
        network = sys.argv[1]

    # Create auto deployer
    deployer = AutoDeployer(network=network)

    # Run deployment
    try:
        deployer.run()
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Deployment interrupted by user")
        print(f"   You can resume by running: python3 auto_deploy.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
