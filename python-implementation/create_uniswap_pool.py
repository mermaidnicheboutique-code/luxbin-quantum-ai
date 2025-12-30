#!/usr/bin/env python3
"""
Create Uniswap V3 pool for LUX token on Base
"""

from web3 import Web3
import json
import os
from pathlib import Path

# Connect to Base
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# Your wallet
PRIVATE_KEY = "0x8e991e125ec36d7077d12358e836cb82a53ddba6272f60afd0340bb4d4b6fd49"
account = w3.eth.account.from_key(PRIVATE_KEY)
YOUR_ADDRESS = account.address

print(f"Using wallet: {YOUR_ADDRESS}")
print()

# Contract addresses on Base
LUX_TOKEN = '0x5ea9Cd079461F988E5A8FFc20A2922DFeB66f673'
WETH = '0x4200000000000000000000000000000000000006'
USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'

# Uniswap V3 on Base
UNISWAP_V3_FACTORY = '0x33128a8fC17869897dcE68Ed026d694621f6FDfD'
POSITION_MANAGER = '0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1'
SWAP_ROUTER = '0x2626664c2603336E57B271c5C0b26F421741e481'

# ABIs
FACTORY_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"}
        ],
        "name": "createPool",
        "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"}
        ],
        "name": "getPool",
        "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

POOL_ABI = [
    {
        "inputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

POSITION_MANAGER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "token0", "type": "address"},
                    {"internalType": "address", "name": "token1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickLower", "type": "int24"},
                    {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                    {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "internalType": "struct INonfungiblePositionManager.MintParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "mint",
        "outputs": [
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"}
        ],
        "stateMutability": "payable",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

def main():
    print("=" * 60)
    print("🦄 Creating Uniswap V3 Pool for LUX")
    print("=" * 60)
    print()

    # Choose pair
    print("📊 Setting up LUX/WETH pool...")
    print(f"   LUX Token: {LUX_TOKEN}")
    print(f"   WETH: {WETH}")
    print()

    # Fee tier: 1% (10000) for new tokens
    FEE_TIER = 10000

    # Sort tokens (Uniswap requires token0 < token1)
    if int(LUX_TOKEN, 16) < int(WETH, 16):
        token0, token1 = LUX_TOKEN, WETH
        token0_name, token1_name = "LUX", "WETH"
    else:
        token0, token1 = WETH, LUX_TOKEN
        token0_name, token1_name = "WETH", "LUX"

    print(f"   Token0: {token0_name} ({token0})")
    print(f"   Token1: {token1_name} ({token1})")
    print(f"   Fee Tier: {FEE_TIER / 10000}%")
    print()

    # Check if pool exists
    factory = w3.eth.contract(address=UNISWAP_V3_FACTORY, abi=FACTORY_ABI)
    pool_address = factory.functions.getPool(token0, token1, FEE_TIER).call()

    if pool_address == '0x0000000000000000000000000000000000000000':
        print("🆕 Pool doesn't exist yet. Creating it...")

        # Create pool
        nonce = w3.eth.get_transaction_count(YOUR_ADDRESS)
        gas_price = w3.eth.gas_price

        create_pool_txn = factory.functions.createPool(
            token0, token1, FEE_TIER
        ).build_transaction({
            'from': YOUR_ADDRESS,
            'nonce': nonce,
            'gas': 5000000,
            'gasPrice': int(gas_price * 1.2),
        })

        signed_txn = account.sign_transaction(create_pool_txn)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        print(f"   Transaction: {tx_hash.hex()}")
        print("   Waiting for confirmation...")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

        if receipt['status'] == 1:
            pool_address = factory.functions.getPool(token0, token1, FEE_TIER).call()
            print(f"   ✅ Pool created: {pool_address}")
        else:
            print("   ❌ Pool creation failed!")
            return

        print()
        print("📍 Initializing pool price...")

        # Initialize pool at 1 LUX = 0.0001 ETH ($0.30 if ETH = $3000)
        # sqrtPriceX96 = sqrt(price) * 2^96
        # price = (amount of token1) / (amount of token0)

        if token0_name == "LUX":
            # LUX is token0, so price = WETH/LUX = 0.0001
            # sqrtPrice = sqrt(0.0001) = 0.01
            import math
            sqrt_price = math.sqrt(0.0001)
        else:
            # WETH is token0, so price = LUX/WETH = 10000
            # sqrtPrice = sqrt(10000) = 100
            import math
            sqrt_price = math.sqrt(10000)

        sqrtPriceX96 = int(sqrt_price * (2 ** 96))

        pool = w3.eth.contract(address=pool_address, abi=POOL_ABI)

        nonce = w3.eth.get_transaction_count(YOUR_ADDRESS)

        init_txn = pool.functions.initialize(sqrtPriceX96).build_transaction({
            'from': YOUR_ADDRESS,
            'nonce': nonce,
            'gas': 500000,
            'gasPrice': int(gas_price * 1.2),
        })

        signed_txn = account.sign_transaction(init_txn)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        print(f"   Transaction: {tx_hash.hex()}")
        print("   Waiting for confirmation...")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

        if receipt['status'] == 1:
            print(f"   ✅ Pool initialized at 1 LUX = 0.0001 ETH")
        else:
            print("   ❌ Pool initialization failed!")
            return
    else:
        print(f"✅ Pool already exists: {pool_address}")

    print()
    print("=" * 60)
    print("💰 Adding Liquidity")
    print("=" * 60)
    print()

    # How much to add?
    # Let's add 1,000,000 LUX + equivalent WETH
    lux_amount = 1_000_000 * 10**18  # 1M LUX
    weth_amount = int(lux_amount * 0.0001)  # 100 WETH at initial price

    print(f"   Adding: 1,000,000 LUX + ~0.1 WETH")
    print(f"   Value: ~$300 (if ETH = $3000)")
    print()

    # Approve tokens
    lux_token = w3.eth.contract(address=LUX_TOKEN, abi=ERC20_ABI)

    print("📝 Approving LUX...")
    nonce = w3.eth.get_transaction_count(YOUR_ADDRESS)
    gas_price = w3.eth.gas_price

    approve_lux = lux_token.functions.approve(
        POSITION_MANAGER, lux_amount
    ).build_transaction({
        'from': YOUR_ADDRESS,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': int(gas_price * 1.2),
    })

    signed = account.sign_transaction(approve_lux)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

    if receipt['status'] == 1:
        print("   ✅ LUX approved")
    else:
        print("   ❌ Approval failed!")
        return

    print()
    print("💵 Adding liquidity position...")

    # Mint position
    # Full range: tick -887220 to 887220
    tick_lower = -887220
    tick_upper = 887220

    if token0_name == "LUX":
        amount0_desired = lux_amount
        amount1_desired = weth_amount
    else:
        amount0_desired = weth_amount
        amount1_desired = lux_amount

    position_manager = w3.eth.contract(address=POSITION_MANAGER, abi=POSITION_MANAGER_ABI)

    deadline = w3.eth.get_block('latest')['timestamp'] + 1200  # 20 minutes

    nonce = w3.eth.get_transaction_count(YOUR_ADDRESS)

    mint_params = {
        'token0': token0,
        'token1': token1,
        'fee': FEE_TIER,
        'tickLower': tick_lower,
        'tickUpper': tick_upper,
        'amount0Desired': amount0_desired,
        'amount1Desired': amount1_desired,
        'amount0Min': 0,
        'amount1Min': 0,
        'recipient': YOUR_ADDRESS,
        'deadline': deadline
    }

    mint_txn = position_manager.functions.mint(mint_params).build_transaction({
        'from': YOUR_ADDRESS,
        'value': weth_amount if token1_name == "WETH" else weth_amount,  # Send ETH
        'nonce': nonce,
        'gas': 5000000,
        'gasPrice': int(gas_price * 1.2),
    })

    signed = account.sign_transaction(mint_txn)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    print(f"   Transaction: {tx_hash.hex()}")
    print("   Waiting for confirmation...")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

    if receipt['status'] == 1:
        print("   ✅ Liquidity added!")
        print()
        print("=" * 60)
        print("🎉 SUCCESS!")
        print("=" * 60)
        print()
        print(f"Pool Address: {pool_address}")
        print(f"View on BaseScan:")
        print(f"https://basescan.org/address/{pool_address}")
        print()
        print(f"Trade on Uniswap:")
        print(f"https://app.uniswap.org/#/swap?chain=base&inputCurrency=ETH&outputCurrency={LUX_TOKEN}")
        print()
        print("✅ LUX is now tradable on Uniswap!")
    else:
        print("   ❌ Failed to add liquidity")
        print(f"   Error: {receipt}")

if __name__ == "__main__":
    main()
