#!/usr/bin/env python3
"""
LUXBIN Blockchain Explorer
A simple web-based blockchain explorer built with Flask and Web3
"""

from flask import Flask, render_template_string, request
from web3 import Web3
import requests
import os

app = Flask(__name__)

# Web3 connection
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LUXBIN Blockchain Explorer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
        .search { margin-bottom: 30px; }
        input { padding: 10px; width: 300px; margin-right: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .block, .tx { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">LUXBIN Blockchain Explorer</h1>

        <div class="stats">
            <div class="stat-card">
                <h3>Current Block</h3>
                <p id="block-number">Loading...</p>
            </div>
            <div class="stat-card">
                <h3>Gas Price</h3>
                <p id="gas-price">Loading...</p>
            </div>
            <div class="stat-card">
                <h3>ETH Price</h3>
                <p id="eth-price">Loading...</p>
            </div>
        </div>

        <div class="search">
            <h3>Search</h3>
            <form method="GET">
                <input type="text" name="query" placeholder="Block number, transaction hash, or address" required>
                <button type="submit">Search</button>
            </form>
        </div>

        <div id="results"></div>
    </div>

    <script>
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();

                document.getElementById('block-number').textContent = '#' + data.block_number.toLocaleString();
                document.getElementById('gas-price').textContent = data.gas_price.toFixed(2) + ' gwei';
                document.getElementById('eth-price').textContent = '$' + data.eth_price;
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }

        updateStats();
        setInterval(updateStats, 30000); // Update every 30 seconds
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    try:
        if not w3.is_connected():
            return {'error': 'Not connected to blockchain'}

        block_number = w3.eth.block_number
        gas_price = w3.from_wei(w3.eth.gas_price, 'gwei')

        # Get ETH price
        try:
            price_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd', timeout=5)
            eth_price = price_response.json()['ethereum']['usd'] if price_response.status_code == 200 else 0
        except:
            eth_price = 0

        return {
            'block_number': block_number,
            'gas_price': float(gas_price),
            'eth_price': eth_price
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()

    if not query:
        return "No query provided"

    try:
        # Check if it's a block number
        if query.isdigit():
            block = w3.eth.get_block(int(query))
            if block:
                return f"""
                <div class="block">
                    <h3>Block #{block.number}</h3>
                    <p><strong>Hash:</strong> {block.hash.hex()}</p>
                    <p><strong>Timestamp:</strong> {block.timestamp}</p>
                    <p><strong>Transactions:</strong> {len(block.transactions)}</p>
                    <p><strong>Gas Used:</strong> {block.gasUsed}</p>
                </div>
                """

        # Check if it's a transaction hash
        if len(query) == 66 and query.startswith('0x'):
            try:
                tx = w3.eth.get_transaction(query)
                receipt = w3.eth.get_transaction_receipt(query)
                if tx:
                    return f"""
                    <div class="tx">
                        <h3>Transaction</h3>
                        <p><strong>Hash:</strong> {tx.hash.hex()}</p>
                        <p><strong>From:</strong> {tx['from']}</p>
                        <p><strong>To:</strong> {tx.to}</p>
                        <p><strong>Value:</strong> {w3.from_wei(tx.value, 'ether')} ETH</p>
                        <p><strong>Gas Price:</strong> {w3.from_wei(tx.gasPrice, 'gwei')} gwei</p>
                        <p><strong>Status:</strong> {'Success' if receipt.status == 1 else 'Failed'}</p>
                    </div>
                    """
            except:
                pass

        # Assume it's an address
        if len(query) == 42 and query.startswith('0x'):
            balance = w3.eth.get_balance(query)
            return f"""
            <div class="block">
                <h3>Address {query}</h3>
                <p><strong>Balance:</strong> {w3.from_wei(balance, 'ether')} ETH</p>
            </div>
            """

        return f"No results found for: {query}"

    except Exception as e:
        return f"Error searching: {e}"

if __name__ == '__main__':
    print("LUXBIN Ethereum Blockchain Explorer starting...")
    print("Open http://localhost:5001 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5001)
