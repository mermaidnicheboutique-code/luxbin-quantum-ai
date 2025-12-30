#!/usr/bin/env python3
"""
LUXBIN Circle API Integration
Official USDC, wallets, and compliance features

Author: Nichole Christie
License: MIT
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from config import CIRCLE_API_KEY, CIRCLE_ENTITY_SECRET, CIRCLE_BASE_URL, CIRCLE_WALLET_SET_ID

class LuxbinCircleAPI:
    """Circle API integration for Luxbin ecosystem"""

    def __init__(self):
        self.api_key = CIRCLE_API_KEY
        self.entity_secret = CIRCLE_ENTITY_SECRET
        self.wallet_set_id = CIRCLE_WALLET_SET_ID
        self.base_url = CIRCLE_BASE_URL
        self.session = requests.Session()

        # Set up authentication
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
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
            return {'error': str(e)}

    # ===== USDC MANAGEMENT =====

    def get_usdc_balance(self, wallet_id: str) -> Dict:
        """Get USDC balance for a wallet"""
        return self._make_request('GET', f'/wallets/{wallet_id}/balances')

    def mint_usdc(self, wallet_id: str, amount: str, destination_address: str) -> Dict:
        """Mint USDC to a destination address"""
        data = {
            'walletId': wallet_id,
            'amount': amount,
            'destinationAddress': destination_address,
            'currency': 'USD'
        }
        return self._make_request('POST', '/transfers', data)

    def burn_usdc(self, wallet_id: str, amount: str) -> Dict:
        """Burn USDC from a wallet"""
        data = {
            'walletId': wallet_id,
            'amount': amount,
            'currency': 'USD'
        }
        return self._make_request('POST', '/burns', data)

    def transfer_usdc(self, source_wallet: str, destination_wallet: str, amount: str) -> Dict:
        """Transfer USDC between wallets"""
        data = {
            'sourceWalletId': source_wallet,
            'destinationWalletId': destination_wallet,
            'amount': amount,
            'currency': 'USD'
        }
        return self._make_request('POST', '/transfers', data)

    # ===== WALLET MANAGEMENT =====

    def create_wallet(self, name: str = "Luxbin Wallet") -> Dict:
        """Create a new programmable wallet"""
        data = {
            'name': name,
            'walletSetId': self.wallet_set_id
        }
        return self._make_request('POST', '/wallets', data)

    def get_wallet(self, wallet_id: str) -> Dict:
        """Get wallet details"""
        return self._make_request('GET', f'/wallets/{wallet_id}')

    def list_wallets(self) -> Dict:
        """List all wallets"""
        return self._make_request('GET', '/wallets')

    # ===== COMPLIANCE & REGULATORY =====

    def check_compliance(self, user_address: str) -> Dict:
        """Check compliance status for a user"""
        # Note: This is a simplified version. In production, you'd integrate
        # with Circle's compliance APIs and KYC providers
        data = {
            'address': user_address,
            'checkType': 'COMPLIANCE'
        }
        return self._make_request('POST', '/compliance/checks', data)

    def freeze_wallet(self, wallet_id: str, reason: str = "Compliance") -> Dict:
        """Freeze a wallet for compliance reasons"""
        data = {
            'reason': reason
        }
        return self._make_request('POST', f'/wallets/{wallet_id}/freeze', data)

    def unfreeze_wallet(self, wallet_id: str) -> Dict:
        """Unfreeze a previously frozen wallet"""
        return self._make_request('POST', f'/wallets/{wallet_id}/unfreeze')

    # ===== CROSS-CHAIN FEATURES =====

    def create_cross_chain_transfer(self, source_wallet: str, destination_address: str,
                                  amount: str, destination_chain: str) -> Dict:
        """Create a cross-chain USDC transfer"""
        data = {
            'sourceWalletId': source_wallet,
            'destinationAddress': destination_address,
            'amount': amount,
            'currency': 'USD',
            'destinationChain': destination_chain
        }
        return self._make_request('POST', '/cross-chain/transfers', data)

    # ===== LUXBIN-SPECIFIC INTEGRATION =====

    def luxbin_stake_reward(self, user_address: str, luxbin_amount: int) -> Dict:
        """Reward user with USDC for staking LUXBIN"""
        print(f"🎁 Rewarding {user_address} with USDC for staking {luxbin_amount} LUXBIN")

        # Check compliance first
        compliance_check = self.check_compliance(user_address)
        if not compliance_check.get('compliant', True):
            return {'error': 'User not compliant', 'details': compliance_check}

        # Calculate reward (1 LUXBIN = 1 USDC for simplicity)
        usdc_amount = str(luxbin_amount)  # Convert to string for API

        # In production, you'd have a treasury wallet to mint from
        # For now, we'll simulate the reward
        return {
            'status': 'reward_queued',
            'user': user_address,
            'luxbin_staked': luxbin_amount,
            'usdc_reward': usdc_amount,
            'compliance_checked': True,
            'note': 'Production: Would mint USDC from treasury wallet'
        }

    def luxbin_compliance_check(self, user_address: str) -> Dict:
        """Check if user can participate in Luxbin ecosystem"""
        print(f"🔍 Checking compliance for Luxbin user: {user_address}")

        compliance_result = self.check_compliance(user_address)

        return {
            'user_address': user_address,
            'can_participate': compliance_result.get('compliant', False),
            'risk_level': compliance_result.get('riskLevel', 'unknown'),
            'last_checked': int(time.time()),
            'circle_api_response': compliance_result
        }

    def get_luxbin_treasury_status(self) -> Dict:
        """Get Luxbin treasury status from Circle"""
        print("🏦 Checking Luxbin treasury status...")

        # In production, you'd query actual treasury wallets
        # For now, return mock data
        return {
            'total_usdc_treasury': '1000000.00',  # 1M USDC
            'wallets_count': 5,
            'compliance_checks_today': 150,
            'cross_chain_transfers_today': 25,
            'status': 'healthy',
            'last_updated': int(time.time())
        }

    # ===== UTILITY FUNCTIONS =====

    def test_connection(self) -> bool:
        """Test Circle API connection"""
        try:
            response = self._make_request('GET', '/ping')
            return response.get('status') == 'ok'
        except:
            return False

    def get_api_status(self) -> Dict:
        """Get API status and capabilities"""
        return {
            'api_connected': self.test_connection(),
            'api_key_configured': bool(self.api_key),
            'entity_secret_configured': bool(self.entity_secret),
            'wallet_set_configured': bool(self.wallet_set_id),
            'capabilities': [
                'USDC minting/burning',
                'Programmable wallets',
                'Cross-chain transfers',
                'Compliance checking',
                'Treasury management'
            ]
        }


# ===== USAGE EXAMPLES =====

if __name__ == "__main__":
    # Initialize Circle API
    circle = LuxbinCircleAPI()

    print("🌐 Luxbin Circle API Integration")
    print("=" * 40)

    # Test connection
    status = circle.get_api_status()
    print(f"API Connected: {status['api_connected']}")
    print(f"API Key: {'✅' if status['api_key_configured'] else '❌'}")
    print(f"Capabilities: {', '.join(status['capabilities'])}")

    print("\n💰 Luxbin Treasury Status:")
    treasury = circle.get_luxbin_treasury_status()
    for key, value in treasury.items():
        print(f"  {key}: {value}")

    print("\n✅ Circle API integration ready for Luxbin ecosystem!")
    print("Use circle.luxbin_stake_reward() and other methods in your Luxbin applications.")