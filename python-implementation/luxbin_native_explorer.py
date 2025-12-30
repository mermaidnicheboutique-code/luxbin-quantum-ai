#!/usr/bin/env python3
"""
LUXBIN NATIVE BLOCKCHAIN EXPLORER
Web-based explorer for LUXBIN blockchain with genetic sequences
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="LUXBIN Native Explorer")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock LUXBIN chain data (will be replaced with real chain connection)
class LuxbinBlock:
    def __init__(self, index: int, timestamp: float, genomes: List, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.genomes = genomes
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        import hashlib
        block_string = f"{self.index}{self.timestamp}{len(self.genomes)}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def total_value(self):
        return sum(g.get('value', 0) for g in self.genomes)

class LuxbinChain:
    def __init__(self):
        self.chain = []
        self._create_genesis_block()
        self._create_sample_blocks()

    def _create_genesis_block(self):
        genesis = LuxbinBlock(0, datetime.now().timestamp(), [], "0")
        self.chain.append(genesis)

    def _create_sample_blocks(self):
        # Create sample blocks with genetic sequences
        for i in range(1, 11):
            genomes = [
                {
                    'hash': f'genome_{i}_{j}',
                    'sequence': f'ATCG' * (10 + i + j),
                    'type': 'DETECTOR' if j % 3 == 0 else 'DEFENDER' if j % 3 == 1 else 'MEMORY',
                    'from': f'0xLUXBIN{i:03d}',
                    'to': f'0xLUXBIN{(i+1):03d}',
                    'value': (i + j) * 100,
                    'timestamp': datetime.now().timestamp() - (10 - i) * 60
                }
                for j in range(3)
            ]
            block = LuxbinBlock(
                i,
                datetime.now().timestamp() - (10 - i) * 60,
                genomes,
                self.chain[-1].hash
            )
            self.chain.append(block)

# Initialize chain
chain = LuxbinChain()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LUXBIN Native Blockchain Explorer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card h3 {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .block, .tx {
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            transition: all 0.3s;
        }
        .block:hover, .tx:hover {
            background: #e9ecef;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .block h3, .tx h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .block p, .tx p {
            margin: 8px 0;
            color: #495057;
        }
        .block strong, .tx strong {
            color: #212529;
            display: inline-block;
            min-width: 120px;
        }
        .genome-sequence {
            font-family: 'Courier New', monospace;
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
            font-size: 0.9em;
            margin: 10px 0;
        }
        .cell-type {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }
        .cell-type.DETECTOR {
            background: #28a745;
            color: white;
        }
        .cell-type.DEFENDER {
            background: #dc3545;
            color: white;
        }
        .cell-type.MEMORY {
            background: #007bff;
            color: white;
        }
        .cell-type.REGULATORY {
            background: #ffc107;
            color: #333;
        }
        .refresh-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            color: #6c757d;
        }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 LUXBIN Native Blockchain Explorer</h1>
            <p><span class="live-indicator"></span>Real-time Genetic Blockchain Monitoring</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Total Blocks</h3>
                <div class="value" id="total-blocks">-</div>
            </div>
            <div class="stat-card">
                <h3>Total Transactions</h3>
                <div class="value" id="total-txs">-</div>
            </div>
            <div class="stat-card">
                <h3>Total Supply</h3>
                <div class="value" id="total-supply">-</div>
            </div>
            <div class="stat-card">
                <h3>24h Volume</h3>
                <div class="value" id="volume">-</div>
            </div>
        </div>

        <div class="section">
            <h2>📦 Latest Blocks</h2>
            <div id="blocks-container"></div>
        </div>

        <div class="section">
            <h2>🧬 Latest Genetic Transactions</h2>
            <div id="txs-container"></div>
        </div>

        <div class="footer">
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
            <p style="margin-top: 15px;">LUXBIN Native Explorer v1.0 | Powered by Genetic Blockchain Technology</p>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                // Load stats
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();

                document.getElementById('total-blocks').textContent = stats.total_blocks;
                document.getElementById('total-txs').textContent = stats.total_transactions;
                document.getElementById('total-supply').textContent = stats.total_supply.toLocaleString();
                document.getElementById('volume').textContent = stats.volume_24h.toLocaleString();

                // Load blocks
                const blocksRes = await fetch('/api/blocks?limit=5');
                const blocksData = await blocksRes.json();
                const blocksContainer = document.getElementById('blocks-container');

                blocksContainer.innerHTML = blocksData.blocks.map(block => `
                    <div class="block">
                        <h3>Block #${block.index}</h3>
                        <p><strong>Hash:</strong> ${block.hash}</p>
                        <p><strong>Timestamp:</strong> ${new Date(block.timestamp).toLocaleString()}</p>
                        <p><strong>Genomes:</strong> ${block.transactions}</p>
                        <p><strong>Total Value:</strong> ${block.total_value.toLocaleString()}</p>
                    </div>
                `).join('');

                // Load transactions
                const txsRes = await fetch('/api/transactions?limit=10');
                const txsData = await txsRes.json();
                const txsContainer = document.getElementById('txs-container');

                txsContainer.innerHTML = txsData.transactions.map(tx => `
                    <div class="tx">
                        <h3>Genome Transaction <span class="cell-type ${tx.type}">${tx.type}</span></h3>
                        <p><strong>Hash:</strong> ${tx.hash}</p>
                        <p><strong>Block:</strong> #${tx.block}</p>
                        <p><strong>From:</strong> ${tx.from}</p>
                        <p><strong>To:</strong> ${tx.to}</p>
                        <p><strong>Value:</strong> ${tx.value.toLocaleString()}</p>
                        <p><strong>Sequence:</strong></p>
                        <div class="genome-sequence">${tx.sequence.substring(0, 80)}...</div>
                        <p><strong>Time:</strong> ${new Date(tx.timestamp * 1000).toLocaleString()}</p>
                    </div>
                `).join('');

            } catch (error) {
                console.error('Error loading data:', error);
            }
        }

        // Load data on page load
        loadData();

        // Auto-refresh every 10 seconds
        setInterval(loadData, 10000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the explorer HTML"""
    return HTML_TEMPLATE

@app.get("/api/stats")
async def get_stats():
    """Get blockchain statistics"""
    total_txs = sum(len(block.genomes) for block in chain.chain)
    total_supply = sum(block.total_value() for block in chain.chain)

    # Calculate 24h volume (mock - last 5 blocks)
    volume_24h = sum(block.total_value() for block in chain.chain[-5:])

    return {
        "total_blocks": len(chain.chain),
        "total_transactions": total_txs,
        "total_supply": total_supply,
        "volume_24h": volume_24h
    }

@app.get("/api/blocks")
async def get_blocks(limit: int = 10):
    """Get latest blocks"""
    blocks = []
    for block in chain.chain[-limit:]:
        blocks.append({
            "index": block.index,
            "hash": block.hash,
            "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
            "transactions": len(block.genomes),
            "total_value": block.total_value(),
        })
    return {"blocks": list(reversed(blocks))}

@app.get("/api/transactions")
async def get_transactions(limit: int = 10):
    """Get latest transactions"""
    all_txs = []
    for block in chain.chain:
        for genome in block.genomes:
            all_txs.append({
                "hash": genome.get('hash'),
                "block": block.index,
                "sequence": genome.get('sequence'),
                "type": genome.get('type'),
                "from": genome.get('from'),
                "to": genome.get('to'),
                "value": genome.get('value'),
                "timestamp": genome.get('timestamp')
            })

    # Return latest transactions
    return {"transactions": list(reversed(all_txs[-limit:]))}

@app.get("/api/block/{index}")
async def get_block(index: int):
    """Get specific block by index"""
    if 0 <= index < len(chain.chain):
        block = chain.chain[index]
        return {
            "index": block.index,
            "hash": block.hash,
            "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
            "previous_hash": block.previous_hash,
            "genomes": block.genomes,
            "total_value": block.total_value()
        }
    return {"error": "Block not found"}

@app.get("/api/transaction/{tx_hash}")
async def get_transaction(tx_hash: str):
    """Get specific transaction by hash"""
    for block in chain.chain:
        for genome in block.genomes:
            if genome.get('hash') == tx_hash:
                return {
                    "hash": genome.get('hash'),
                    "block": block.index,
                    "sequence": genome.get('sequence'),
                    "type": genome.get('type'),
                    "from": genome.get('from'),
                    "to": genome.get('to'),
                    "value": genome.get('value'),
                    "timestamp": genome.get('timestamp')
                }
    return {"error": "Transaction not found"}

if __name__ == "__main__":
    print("=" * 80)
    print("🧬 LUXBIN NATIVE BLOCKCHAIN EXPLORER")
    print("=" * 80)
    print()
    print("🌐 Frontend:  http://localhost:8000")
    print("📚 API Docs:  http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
