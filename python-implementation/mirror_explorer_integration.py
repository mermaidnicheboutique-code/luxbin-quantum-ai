#!/usr/bin/env python3
"""
LUXBIN MIRROR-EXPLORER INTEGRATION
Connects live blockchain mirror data to the LUXBIN Native Explorer
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="LUXBIN Mirror Explorer")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MirrorExplorerBridge:
    """Bridges live mirror data with explorer interface"""

    def __init__(self, mirror_root: str = "./luxbin_mirror", chain: str = "optimism"):
        self.mirror_root = Path(mirror_root)
        self.chain = chain
        self.chain_path = self.mirror_root / chain

        # Paths
        self.raw_blocks = self.chain_path / "raw"
        self.normalized_blocks = self.chain_path / "normalized"
        self.threat_log = self.chain_path / "quantum" / "threat_scores.jsonl"
        self.cells_log = self.chain_path / "immune" / "cells_spawned.jsonl"
        self.vibration_log = self.chain_path / "logs" / "vibration.jsonl"
        self.rhythm_log = self.chain_path / "logs" / "rhythm.jsonl"

    def get_stats(self) -> Dict:
        """Get blockchain statistics from mirror"""
        try:
            # Count blocks
            total_blocks = len(list(self.raw_blocks.glob("block_*.json"))) if self.raw_blocks.exists() else 0

            # Count transactions
            total_txs = 0
            if self.vibration_log.exists():
                with open(self.vibration_log, 'r') as f:
                    for line in f:
                        data = json.loads(line.strip())
                        total_txs += data.get('tx_count', 0)

            # Count spawned cells (total supply)
            total_cells = 0
            if self.cells_log.exists():
                with open(self.cells_log, 'r') as f:
                    for line in f:
                        data = json.loads(line.strip())
                        total_cells += data.get('count', 0)

            # Calculate 24h volume (threat activity)
            recent_threats = []
            if self.threat_log.exists():
                with open(self.threat_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-100:]:  # Last 100 blocks
                        data = json.loads(line.strip())
                        recent_threats.append(data.get('threat_score', 0))

            volume_24h = sum(recent_threats) if recent_threats else 0

            return {
                "total_blocks": total_blocks,
                "total_transactions": total_txs,
                "total_supply": total_cells,
                "volume_24h": volume_24h,
                "chain": self.chain
            }
        except Exception as e:
            return {
                "total_blocks": 0,
                "total_transactions": 0,
                "total_supply": 0,
                "volume_24h": 0,
                "chain": self.chain,
                "error": str(e)
            }

    def get_latest_blocks(self, limit: int = 10) -> List[Dict]:
        """Get latest blocks from mirror"""
        blocks = []
        try:
            if not self.raw_blocks.exists():
                return blocks

            # Get all block files
            block_files = sorted(
                self.raw_blocks.glob("block_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:limit]

            for block_file in block_files:
                with open(block_file, 'r') as f:
                    data = json.load(f)

                    # Extract block info
                    result = data.get('result', {})
                    block_hash = result.get('hash', 'N/A')
                    block_number = result.get('number', 'N/A')
                    timestamp = result.get('timestamp', 'N/A')
                    transactions = result.get('transactions', [])
                    gas_used = result.get('gasUsed', '0x0')

                    # Convert hex to decimal
                    try:
                        block_index = int(block_number, 16) if isinstance(block_number, str) else block_number
                    except:
                        block_index = 0

                    try:
                        block_timestamp = int(timestamp, 16) if isinstance(timestamp, str) else timestamp
                    except:
                        block_timestamp = int(datetime.now().timestamp())

                    try:
                        total_value = int(gas_used, 16) if isinstance(gas_used, str) else gas_used
                    except:
                        total_value = 0

                    blocks.append({
                        "index": block_index,
                        "hash": block_hash,
                        "timestamp": datetime.fromtimestamp(block_timestamp).isoformat(),
                        "transactions": len(transactions),
                        "total_value": total_value
                    })

        except Exception as e:
            print(f"Error reading blocks: {e}")

        return blocks

    def get_latest_transactions(self, limit: int = 10) -> List[Dict]:
        """Get latest transactions (as immune cell spawns)"""
        transactions = []
        try:
            if not self.cells_log.exists():
                return transactions

            with open(self.cells_log, 'r') as f:
                lines = f.readlines()

            for line in lines[-limit:]:
                data = json.loads(line.strip())

                # Get threat score for this block
                threat_score = 0
                if self.threat_log.exists():
                    with open(self.threat_log, 'r') as tf:
                        for threat_line in tf:
                            threat_data = json.loads(threat_line.strip())
                            if threat_data.get('block') == data.get('block'):
                                threat_score = threat_data.get('threat_score', 0)
                                break

                # Create transaction from cell spawn
                transactions.append({
                    "hash": f"cell_spawn_{data.get('block', 'unknown')}_{data.get('cell_type', 'unknown')}",
                    "block": data.get('block', 'unknown'),
                    "sequence": self._generate_sequence(data.get('cell_type', 'MEMORY'), threat_score),
                    "type": data.get('cell_type', 'MEMORY'),
                    "from": f"0xMIRROR_{self.chain.upper()}",
                    "to": f"0xIMMUNE_SYSTEM",
                    "value": data.get('count', 1) * 100,
                    "timestamp": data.get('timestamp', datetime.now().isoformat())
                })

        except Exception as e:
            print(f"Error reading transactions: {e}")

        return list(reversed(transactions))

    def _generate_sequence(self, cell_type: str, threat_score: int) -> str:
        """Generate genetic sequence based on cell type and threat"""
        # Base sequences for each cell type
        bases = {
            "DETECTOR": "ATCG",
            "DEFENDER": "GCTA",
            "MEMORY": "CGAT",
            "REGULATORY": "TAGC"
        }

        base = bases.get(cell_type, "ATCG")

        # Length based on threat score
        length = 40 + threat_score

        # Generate sequence
        sequence = base * (length // 4)
        return sequence[:length]

# Initialize bridge
bridge = MirrorExplorerBridge()

# Import HTML template from luxbin_native_explorer
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LUXBIN Mirror Explorer - Live Data</title>
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
        .chain-badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔮 LUXBIN Mirror Explorer</h1>
            <p>
                <span class="live-indicator"></span>
                Live Hermetic Blockchain Mirror
                <span class="chain-badge" id="chain-name">Loading...</span>
            </p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Mirrored Blocks</h3>
                <div class="value" id="total-blocks">-</div>
            </div>
            <div class="stat-card">
                <h3>Total Transactions</h3>
                <div class="value" id="total-txs">-</div>
            </div>
            <div class="stat-card">
                <h3>Immune Cells Spawned</h3>
                <div class="value" id="total-supply">-</div>
            </div>
            <div class="stat-card">
                <h3>Threat Activity</h3>
                <div class="value" id="volume">-</div>
            </div>
        </div>

        <div class="section">
            <h2>📦 Latest Mirrored Blocks</h2>
            <div id="blocks-container">
                <p style="text-align: center; color: #6c757d;">Loading blocks from live mirror...</p>
            </div>
        </div>

        <div class="section">
            <h2>🦠 Latest Immune Cell Spawns</h2>
            <div id="txs-container">
                <p style="text-align: center; color: #6c757d;">Loading immune activity...</p>
            </div>
        </div>

        <div class="footer">
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
            <p style="margin-top: 15px;">LUXBIN Mirror Explorer v1.0 | Live Hermetic Blockchain Mirroring</p>
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
                document.getElementById('chain-name').textContent = stats.chain.toUpperCase();

                // Load blocks
                const blocksRes = await fetch('/api/blocks?limit=5');
                const blocksData = await blocksRes.json();
                const blocksContainer = document.getElementById('blocks-container');

                if (blocksData.blocks.length === 0) {
                    blocksContainer.innerHTML = '<p style="text-align: center; color: #6c757d;">No blocks mirrored yet. Start the live mirror first!</p>';
                } else {
                    blocksContainer.innerHTML = blocksData.blocks.map(block => `
                        <div class="block">
                            <h3>Block #${block.index}</h3>
                            <p><strong>Hash:</strong> ${block.hash}</p>
                            <p><strong>Timestamp:</strong> ${block.timestamp}</p>
                            <p><strong>Transactions:</strong> ${block.transactions}</p>
                            <p><strong>Gas Used:</strong> ${block.total_value.toLocaleString()}</p>
                        </div>
                    `).join('');
                }

                // Load transactions
                const txsRes = await fetch('/api/transactions?limit=10');
                const txsData = await txsRes.json();
                const txsContainer = document.getElementById('txs-container');

                if (txsData.transactions.length === 0) {
                    txsContainer.innerHTML = '<p style="text-align: center; color: #6c757d;">No immune cells spawned yet. Waiting for threats...</p>';
                } else {
                    txsContainer.innerHTML = txsData.transactions.map(tx => `
                        <div class="tx">
                            <h3>Immune Cell Spawn <span class="cell-type ${tx.type}">${tx.type}</span></h3>
                            <p><strong>Hash:</strong> ${tx.hash}</p>
                            <p><strong>Block:</strong> ${tx.block}</p>
                            <p><strong>From:</strong> ${tx.from}</p>
                            <p><strong>To:</strong> ${tx.to}</p>
                            <p><strong>Cells:</strong> ${(tx.value / 100).toFixed(0)}</p>
                            <p><strong>Sequence:</strong></p>
                            <div class="genome-sequence">${tx.sequence.substring(0, 80)}...</div>
                        </div>
                    `).join('');
                }

            } catch (error) {
                console.error('Error loading data:', error);
            }
        }

        // Load data on page load
        loadData();

        // Auto-refresh every 5 seconds
        setInterval(loadData, 5000);
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
    """Get blockchain statistics from mirror"""
    return bridge.get_stats()

@app.get("/api/blocks")
async def get_blocks(limit: int = 10):
    """Get latest blocks from mirror"""
    blocks = bridge.get_latest_blocks(limit)
    return {"blocks": blocks}

@app.get("/api/transactions")
async def get_transactions(limit: int = 10):
    """Get latest transactions (cell spawns) from mirror"""
    transactions = bridge.get_latest_transactions(limit)
    return {"transactions": transactions}

if __name__ == "__main__":
    print("=" * 80)
    print("🔮 LUXBIN MIRROR EXPLORER (LIVE DATA)")
    print("=" * 80)
    print()
    print(f"📡 Mirror Root: {bridge.mirror_root}")
    print(f"⛓️  Chain: {bridge.chain}")
    print()
    print("🌐 Frontend:  http://localhost:8002")
    print("📚 API Docs:  http://localhost:8002/docs")
    print()
    print("⚠️  Make sure the live mirror is running!")
    print("   ./START_LIVE_MIRROR.sh")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
