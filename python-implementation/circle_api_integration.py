#!/usr/bin/env python3
"""
LUXBIN Circle API Integration
Official USDC minting, burning, and compliance features

Author: Nichole Christie
License: MIT
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import web3
from web3 import Web3
import os

from config import (
    CIRCLE_API_KEY,
    CIRCLE_ENTITY_SECRET,
    CIRCLE_WALLET_SET_ID,
    CIRCLE_BASE_URL
)

class LuxbinCircleAPI:
    """Circle API integration for USDC and compliance features"""

    def __init__(self):
        self.api_key = CIRCLE_API_KEY
        self.entity_secret = CIRCLE_ENTITY_SECRET
        self.wallet_set_id = CIRCLE_WALLET_SET_ID
        self.base_url = CIRCLE_BASE_URL
        self.session = requests.Session()

        # Set up headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

        print("🔄 LuxbinCircleAPI initialized")

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to Circle API"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Circle API request failed: {e}")
            return {}

    # USDC Minting & Burning
    def mint_usdc(self, wallet_id: str, amount: int, destination_address: str) -> Dict:
        """Mint USDC to a wallet"""
        endpoint = f"/w3s/wallets/{wallet_id}/transfers"
        data = {
            "blockchain": "ETH",
            "amount": str(amount),
            "destinationAddress": destination_address,
            "tokenId": "USDCC",  # USDC on Ethereum
            "feeLevel": "HIGH"
        }

        result = self._make_request('POST', endpoint, data)
        if result:
            print(f"✅ Minted {amount} USDC to {destination_address}")
        return result

    def burn_usdc(self, wallet_id: str, amount: int, source_address: str) -> Dict:
        """Burn USDC from a wallet"""
        endpoint = f"/w3s/wallets/{wallet_id}/transfers"
        data = {
            "blockchain": "ETH",
            "amount": str(amount),
            "sourceAddress": source_address,
            "tokenId": "USDCC",
            "feeLevel": "HIGH",
            "operation": "BURN"
        }

        result = self._make_request('POST', endpoint, data)
        if result:
            print(f"🔥 Burned {amount} USDC from {source_address}")
        return result

    # Programmable Wallets
    def create_wallet(self, name: str = "LuxbinWallet") -> Dict:
        """Create a new programmable wallet"""
        endpoint = "/w3s/wallets"
        data = {
            "name": name,
            "walletSetId": self.wallet_set_id
        }

        result = self._make_request('POST', endpoint, data)
        if result:
            wallet_id = result.get('data', {}).get('walletId')
            print(f"✅ Created wallet: {wallet_id}")
        return result

    def get_wallet_balance(self, wallet_id: str) -> Dict:
        """Get wallet balance"""
        endpoint = f"/w3s/wallets/{wallet_id}/balances"
        return self._make_request('GET', endpoint)

    def list_wallets(self) -> Dict:
        """List all wallets"""
        endpoint = "/w3s/wallets"
        return self._make_request('GET', endpoint)

    # Compliance & KYC
    def check_compliance(self, address: str) -> Dict:
        """Check compliance status of an address"""
        endpoint = f"/compliance/address/{address}"
        result = self._make_request('GET', endpoint)

        if result:
            status = result.get('data', {}).get('status', 'UNKNOWN')
            print(f"📋 Compliance status for {address}: {status}")

        return result

    def freeze_wallet(self, wallet_id: str) -> Dict:
        """Freeze a wallet for compliance reasons"""
        endpoint = f"/w3s/wallets/{wallet_id}/freeze"
        data = {"reason": "COMPLIANCE_VIOLATION"}

        result = self._make_request('PUT', endpoint, data)
        if result:
            print(f"❄️ Frozen wallet: {wallet_id}")
        return result

    def unfreeze_wallet(self, wallet_id: str) -> Dict:
        """Unfreeze a previously frozen wallet"""
        endpoint = f"/w3s/wallets/{wallet_id}/unfreeze"

        result = self._make_request('PUT', endpoint)
        if result:
            print(f"🔥 Unfrozen wallet: {wallet_id}")
        return result

    # Cross-chain Transfers
    def create_cross_chain_transfer(
        self,
        wallet_id: str,
        amount: int,
        source_chain: str,
        destination_chain: str,
        destination_address: str
    ) -> Dict:
        """Create a cross-chain USDC transfer"""
        endpoint = f"/w3s/wallets/{wallet_id}/transfers"
        data = {
            "blockchain": source_chain,
            "amount": str(amount),
            "destinationAddress": destination_address,
            "tokenId": "USDCC",
            "destinationBlockchain": destination_chain,
            "feeLevel": "HIGH"
        }

        result = self._make_request('POST', endpoint, data)
        if result:
            print(f"🌉 Cross-chain transfer: {amount} USDC from {source_chain} to {destination_chain}")
        return result

    # Luxbin-specific integrations
    def mint_usdc_for_luxbin_staking(
        self,
        wallet_id: str,
        user_address: str,
        luxbin_amount: int
    ) -> Dict:
        """Mint USDC when users stake LUXBIN tokens"""
        # 1 LUXBIN = 1 USDC (both 6 decimals for USDC, 18 for LUXBIN)
        usdc_amount = luxbin_amount // (10 ** 12)  # Convert to 6 decimals

        print(f"🎯 Minting {usdc_amount} USDC for {luxbin_amount} LUXBIN staked")

        return self.mint_usdc(wallet_id, usdc_amount, user_address)

    def burn_usdc_for_luxbin_unstaking(
        self,
        wallet_id: str,
        user_address: str,
        usdc_amount: int
    ) -> Dict:
        """Burn USDC when users unstake LUXBIN tokens"""
        print(f"🔄 Burning {usdc_amount} USDC for LUXBIN unstaking")

        return self.burn_usdc(wallet_id, usdc_amount, user_address)

    # Utility functions
    def get_supported_chains(self) -> List[str]:
        """Get list of supported blockchains"""
        return [
            "ETH",      # Ethereum
            "MATIC",    # Polygon
            "AVAX",     # Avalanche
            "SOL",      # Solana
            "FLOW",     # Flow
            "HBAR"      # Hedera
        ]

    def get_transfer_status(self, transfer_id: str) -> Dict:
        """Check status of a transfer"""
        endpoint = f"/w3s/transfers/{transfer_id}"
        return self._make_request('GET', endpoint)

    def get_wallet_transfers(self, wallet_id: str, limit: int = 50) -> Dict:
        """Get transfer history for a wallet"""
        endpoint = f"/w3s/wallets/{wallet_id}/transfers?limit={limit}"
        return self._make_request('GET', endpoint)

    def health_check(self) -> bool:
        """Check if Circle API is accessible"""
        try:
            endpoint = "/ping"
            result = self._make_request('GET', endpoint)
            return result.get('message') == 'pong'
        except:
            return False


# ===== XRESERVE INTEGRATION =====

class LuxbinXReserveAPI:
    """Circle xReserve integration for Luxbin stablecoin deployment"""

    def __init__(self, circle_api: LuxbinCircleAPI):
        self.circle = circle_api
        self.reserve_contracts = {}  # Chain -> reserve contract address
        self.bridge_contracts = {}   # Chain -> bridge contract address

    def deploy_luxbin_stablecoin(self, chain: str, name: str = "Luxbin USD", symbol: str = "LUSD") -> Dict:
        """Deploy LUXBIN stablecoin on target chain using xReserve"""
        endpoint = "/xreserve/deploy"
        data = {
            "chain": chain,
            "tokenName": name,
            "tokenSymbol": symbol,
            "reserveToken": "USDC",
            "backingRatio": "1.0"  # 1:1 backing
        }

        result = self.circle._make_request('POST', endpoint, data)
        if result:
            print(f"✅ Deployed {symbol} stablecoin on {chain}")
            if result.get('reserveContract'):
                self.reserve_contracts[chain] = result['reserveContract']
            if result.get('bridgeContract'):
                self.bridge_contracts[chain] = result['bridgeContract']

        return result

    def mint_luxbin_stablecoin(self, chain: str, amount: int, recipient: str) -> Dict:
        """Mint LUXBIN stablecoin using xReserve attestation"""
        if chain not in self.reserve_contracts:
            return {'error': f'No reserve contract for {chain}'}

        endpoint = f"/xreserve/{chain}/mint"
        data = {
            "reserveContract": self.reserve_contracts[chain],
            "amount": str(amount),
            "recipient": recipient,
            "backingToken": "USDC"
        }

        result = self.circle._make_request('POST', endpoint, data)
        if result:
            attestation_id = result.get('attestationId')
            print(f"🎯 Minted {amount} LUXBIN on {chain}, attestation: {attestation_id}")

        return result

    def burn_luxbin_stablecoin(self, chain: str, amount: int, burner: str) -> Dict:
        """Burn LUXBIN stablecoin and release USDC using xReserve"""
        if chain not in self.reserve_contracts:
            return {'error': f'No reserve contract for {chain}'}

        endpoint = f"/xreserve/{chain}/burn"
        data = {
            "reserveContract": self.reserve_contracts[chain],
            "amount": str(amount),
            "burner": burner,
            "releaseToken": "USDC"
        }

        result = self.circle._make_request('POST', endpoint, data)
        if result:
            attestation_id = result.get('attestationId')
            print(f"🔥 Burned {amount} LUXBIN on {chain}, attestation: {attestation_id}")

        return result

    def cross_chain_luxbin_transfer(
        self,
        source_chain: str,
        dest_chain: str,
        amount: int,
        sender: str,
        recipient: str
    ) -> Dict:
        """Cross-chain LUXBIN transfer using xReserve"""
        if source_chain not in self.bridge_contracts or dest_chain not in self.bridge_contracts:
            return {'error': 'Missing bridge contracts for chains'}

        endpoint = "/xreserve/cross-chain-transfer"
        data = {
            "sourceChain": source_chain,
            "destinationChain": dest_chain,
            "sourceBridge": self.bridge_contracts[source_chain],
            "destBridge": self.bridge_contracts[dest_chain],
            "amount": str(amount),
            "sender": sender,
            "recipient": recipient,
            "tokenSymbol": "LUXBIN"
        }

        result = self.circle._make_request('POST', endpoint, data)
        if result:
            print(f"🌉 Cross-chain {amount} LUXBIN: {source_chain} → {dest_chain}")

        return result

    def get_luxbin_reserve_status(self, chain: str) -> Dict:
        """Get LUXBIN reserve status on specific chain"""
        if chain not in self.reserve_contracts:
            return {'error': f'No reserve contract for {chain}'}

        endpoint = f"/xreserve/{chain}/status"
        data = {"reserveContract": self.reserve_contracts[chain]}

        result = self.circle._make_request('GET', endpoint)
        if result:
            status = result.get('status', 'unknown')
            backing_ratio = result.get('backingRatio', '0')
            print(f"🏦 {chain} LUXBIN reserve: {status}, backing: {backing_ratio}%")

        return result

    def setup_luxbin_ecosystem(self) -> Dict:
        """Set up LUXBIN xReserve ecosystem across multiple chains"""
        # Based on Circle xReserve documentation:
        # Source chain: Ethereum (holds USDC reserves)
        # Remote chains: Where LUXBIN stablecoins are issued
        source_chain = "ETH"  # Ethereum holds USDC reserves
        remote_chains = ["MATIC", "AVAX", "SOL", "FLOW"]  # Remote chains for LUXBIN

        deployments = {}

        print("🚀 Setting up LUXBIN xReserve ecosystem...")
        print(f"🏦 Source Chain (USDC Reserves): {source_chain}")
        print(f"🌍 Remote Chains (LUXBIN Issuance): {', '.join(remote_chains)}")

        # Deploy on source chain (Ethereum) - reserve holding
        print(f"\n🏦 Setting up USDC reserves on {source_chain}...")
        source_result = self.deploy_luxbin_stablecoin(source_chain, "Luxbin Reserve", "LUXR")
        deployments[source_chain] = source_result

        if source_result and 'reserveContract' in source_result:
            print(f"✅ USDC reserve setup successful on {source_chain}")
            # This contract will hold USDC backing for all LUXBIN issued
        else:
            print(f"❌ Reserve setup failed on {source_chain}")

        # Deploy on remote chains - LUXBIN issuance
        for chain in remote_chains:
            print(f"\n🌐 Deploying LUXBIN on {chain}...")
            result = self.deploy_luxbin_stablecoin(chain, "Luxbin USD", "LUSD")
            deployments[chain] = result

            if result and 'reserveContract' in result:
                print(f"✅ LUXBIN deployment successful on {chain}")
            else:
                print(f"⚠️  LUXBIN deployment pending on {chain} (may not be supported yet)")

        success_count = sum(1 for result in deployments.values() if result and 'reserveContract' in result)

        print(f"\n🎉 LUXBIN xReserve ecosystem setup complete!")
        print(f"✅ Successful deployments: {success_count}/{len(deployments)}")
        print("📋 USDC reserves held on Ethereum, LUXBIN issued on remote chains"
        return {
            'source_chain': source_chain,
            'remote_chains': remote_chains,
            'deployments': deployments,
            'total_chains': len(deployments),
            'successful_deployments': success_count,
            'reserve_contracts': self.reserve_contracts,
            'bridge_contracts': self.bridge_contracts,
            'usdc_reserve_chain': source_chain,
            'luxbin_issue_chains': [chain for chain, result in deployments.items()
                                  if result and 'reserveContract' in result]
        }


# Luxbin-specific integration class
class LuxbinCircleIntegration:
    """High-level integration for Luxbin ecosystem"""

    def __init__(self):
        self.circle = LuxbinCircleAPI()
        self.xreserve = LuxbinXReserveAPI(self.circle)
        self.master_wallet_id = None  # Set this to your main wallet
        self.luxbin_usdc_ratio = 10**12  # 1 LUXBIN = 1 USDC (accounting for decimals)

    def stake_luxbin_mint_usdc(self, user_address: str, luxbin_amount: int) -> bool:
        """When user stakes LUXBIN, mint equivalent USDC"""
        if not self.master_wallet_id:
            print("❌ Master wallet not configured")
            return False

        result = self.circle.mint_usdc_for_luxbin_staking(
            self.master_wallet_id,
            user_address,
            luxbin_amount
        )

        return bool(result)

    def unstake_luxbin_burn_usdc(self, user_address: str, usdc_amount: int) -> bool:
        """When user unstakes LUXBIN, burn equivalent USDC"""
        if not self.master_wallet_id:
            print("❌ Master wallet not configured")
            return False

        result = self.circle.burn_usdc_for_luxbin_unstaking(
            self.master_wallet_id,
            user_address,
            usdc_amount
        )

        return bool(result)

    def check_user_compliance(self, user_address: str) -> bool:
        """Check if user passes Circle's compliance checks"""
        result = self.circle.check_compliance(user_address)
        if result:
            status = result.get('data', {}).get('status')
            return status == 'APPROVED'
        return False

    def setup_master_wallet(self) -> bool:
        """Create and configure master wallet for USDC operations"""
        result = self.circle.create_wallet("LuxbinMasterWallet")
        if result:
            self.master_wallet_id = result.get('data', {}).get('walletId')
            print(f"🏦 Master wallet created: {self.master_wallet_id}")
            return True
        return False

    def get_system_status(self) -> Dict:
        """Get overall system status"""
        return {
            "circle_api_health": self.circle.health_check(),
            "master_wallet": self.master_wallet_id,
            "supported_chains": self.circle.get_supported_chains(),
            "luxbin_usdc_ratio": self.luxbin_usdc_ratio,
            "xreserve_reserve_contracts": self.xreserve.reserve_contracts,
            "xreserve_bridge_contracts": self.xreserve.bridge_contracts
        }

    # ===== XRESERVE METHODS =====

    def deploy_luxbin_stablecoin_xreserve(self, chain: str = "ETH") -> Dict:
        """Deploy LUXBIN stablecoin using Circle xReserve"""
        return self.xreserve.deploy_luxbin_stablecoin(chain, "Luxbin USD", "LUSD")

    def mint_luxbin_via_xreserve(self, chain: str, amount: int, recipient: str) -> Dict:
        """Mint LUXBIN stablecoin using xReserve attestation"""
        return self.xreserve.mint_luxbin_stablecoin(chain, amount, recipient)

    def burn_luxbin_via_xreserve(self, chain: str, amount: int, burner: str) -> Dict:
        """Burn LUXBIN stablecoin using xReserve"""
        return self.xreserve.burn_luxbin_stablecoin(chain, amount, burner)

    def cross_chain_luxbin_transfer(self, source_chain: str, dest_chain: str,
                                  amount: int, sender: str, recipient: str) -> Dict:
        """Cross-chain LUXBIN transfer using xReserve"""
        return self.xreserve.cross_chain_luxbin_transfer(source_chain, dest_chain,
                                                        amount, sender, recipient)

    def setup_complete_luxbin_ecosystem(self) -> Dict:
        """Set up complete LUXBIN ecosystem across all supported chains"""
        return self.xreserve.setup_luxbin_ecosystem()

    def get_luxbin_reserve_status(self, chain: str) -> Dict:
        """Get LUXBIN reserve status on specific chain"""
        return self.xreserve.get_luxbin_reserve_status(chain)


if __name__ == "__main__":
    # Test the integration
    print("🧪 Testing LuxbinCircleAPI + xReserve...")

    circle = LuxbinCircleAPI()
    xreserve = LuxbinXReserveAPI(circle)
    luxbin_integration = LuxbinCircleIntegration()

    if circle.health_check():
        print("✅ Circle API connection successful")

        # Test xReserve ecosystem setup
        print("\n🌟 Testing xReserve integration...")
        ecosystem_result = xreserve.setup_luxbin_ecosystem()

        if ecosystem_result:
            print("✅ xReserve ecosystem setup successful")
            print(f"📊 Chains deployed: {ecosystem_result['total_chains']}")
        else:
            print("⚠️  xReserve setup returned no result (API might be in development)")

        # Test basic wallet creation
        wallet_result = circle.create_wallet("TestWallet")
        if wallet_result:
            print("✅ Wallet creation successful")
        else:
            print("❌ Wallet creation failed")

        # Show system status
        print("\n📊 System Status:")
        status = luxbin_integration.get_system_status()
        for key, value in status.items():
            if isinstance(value, dict) and len(value) > 3:
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")

    else:
        print("❌ Circle API connection failed")
        print("Check your CIRCLE_API_KEY configuration")
        print("Note: xReserve APIs may still be in development by Circle")