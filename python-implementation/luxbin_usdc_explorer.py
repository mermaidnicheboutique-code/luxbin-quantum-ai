#!/usr/bin/env python3
"""
LUXBIN USDC EXPLORER
Blockchain explorer with real USDC value integration
"""

import asyncio
from pathlib import Path
from decimal import Decimal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from luxbin_usdc_integration import LuxbinUSDCEconomy, USDCIntegration

app = FastAPI(title="LUXBIN USDC Explorer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize economy with correct path
economy = LuxbinUSDCEconomy(mirror_root="../luxbin_mirror", chain="optimism")
usdc = USDCIntegration(chain="optimism")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LUXBIN USDC Explorer - Real Value</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1600px;
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
        .usdc-badge {
            display: inline-block;
            background: linear-gradient(135deg, #2775CA, #26A17B);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin: 5px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .stat-card.usdc {
            background: linear-gradient(135deg, #2775CA, #26A17B);
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
        .stat-card .subvalue {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .value-breakdown {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .value-row {
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .value-row:last-child {
            border-bottom: none;
            font-weight: bold;
            font-size: 1.2em;
            color: #26A17B;
        }
        .cell-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .cell-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .cell-card.DETECTOR { border-color: #28a745; }
        .cell-card.DEFENDER { border-color: #dc3545; }
        .cell-card.MEMORY { border-color: #007bff; }
        .cell-card.REGULATORY { border-color: #ffc107; }
        .cell-card h4 {
            margin-bottom: 10px;
        }
        .cell-card .count {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .cell-card .usdc-value {
            font-size: 1.5em;
            color: #26A17B;
            font-weight: bold;
        }
        .earnings-calculator {
            background: linear-gradient(135deg, #2775CA, #26A17B);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .earnings-calculator h3 {
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .calc-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            font-size: 1.1em;
        }
        .calc-row.highlight {
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid rgba(255,255,255,0.3);
        }
        .refresh-btn {
            background: linear-gradient(135deg, #2775CA, #26A17B);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(39, 117, 202, 0.3);
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
            <h1>💰 LUXBIN USDC Explorer</h1>
            <p>
                <span class="live-indicator"></span>
                Real-Time Blockchain Value in USDC
            </p>
            <div>
                <span class="usdc-badge">🟢 USDC Connected</span>
                <span class="usdc-badge" id="chain-name">OPTIMISM</span>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card usdc">
                <h3>💵 Total Earned</h3>
                <div class="value" id="total-earned">$0.00</div>
                <div class="subvalue">From all activities</div>
            </div>
            <div class="stat-card">
                <h3>🦠 Cell Value</h3>
                <div class="value" id="cell-value">$0.00</div>
                <div class="subvalue" id="cell-count">0 cells spawned</div>
            </div>
            <div class="stat-card">
                <h3>⚠️ Threat Rewards</h3>
                <div class="value" id="threat-value">$0.00</div>
                <div class="subvalue" id="threat-count">0 threats detected</div>
            </div>
            <div class="stat-card">
                <h3>📦 Block Rewards</h3>
                <div class="value" id="block-value">$0.00</div>
                <div class="subvalue" id="block-count">0 blocks mirrored</div>
            </div>
        </div>

        <div class="section">
            <h2>💎 Cell Value Breakdown</h2>
            <div class="cell-grid" id="cell-breakdown">
                <p style="text-align: center; color: #6c757d;">Loading cell data...</p>
            </div>
        </div>

        <div class="section">
            <h2>📊 Value Breakdown</h2>
            <div class="value-breakdown">
                <div class="value-row">
                    <span>Immune Cells Spawned</span>
                    <span id="breakdown-cells">$0.00</span>
                </div>
                <div class="value-row">
                    <span>Threat Detection Rewards</span>
                    <span id="breakdown-threats">$0.00</span>
                </div>
                <div class="value-row">
                    <span>Block Mirroring Rewards</span>
                    <span id="breakdown-blocks">$0.00</span>
                </div>
                <div class="value-row">
                    <span>TOTAL VALUE EARNED</span>
                    <span id="breakdown-total">$0.00</span>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Staking & Earnings Potential</h2>
            <div class="earnings-calculator">
                <h3>With HCT Score of 0.85</h3>
                <div class="calc-row">
                    <span>Current APY:</span>
                    <span id="calc-apy">0%</span>
                </div>
                <div class="calc-row">
                    <span>30-Day Staking Rewards:</span>
                    <span id="calc-30d">$0.00</span>
                </div>
                <div class="calc-row highlight">
                    <span>Potential 30-Day Total:</span>
                    <span id="calc-total">$0.00</span>
                </div>
                <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.9;" id="stake-status">
                    Minimum stake: $100 USDC
                </div>
            </div>
        </div>

        <div class="section">
            <h2>💰 Tokenomics</h2>
            <div class="value-breakdown">
                <div class="value-row">
                    <span>DETECTOR Cell</span>
                    <span>$10.00 USDC</span>
                </div>
                <div class="value-row">
                    <span>DEFENDER Cell</span>
                    <span>$15.00 USDC</span>
                </div>
                <div class="value-row">
                    <span>MEMORY Cell</span>
                    <span>$5.00 USDC</span>
                </div>
                <div class="value-row">
                    <span>REGULATORY Cell</span>
                    <span>$20.00 USDC</span>
                </div>
                <div class="value-row">
                    <span>Block Mirror Reward</span>
                    <span>$0.10 USDC</span>
                </div>
                <div class="value-row">
                    <span>Threat Reward Range</span>
                    <span>$1.00 - $100.00 USDC</span>
                </div>
            </div>
        </div>

        <div style="text-align: center; margin-top: 40px;">
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const res = await fetch('/api/economy');
                const data = await res.json();

                // Update main stats
                document.getElementById('total-earned').textContent = '$' + parseFloat(data.mirror_value.total_earned).toFixed(2);
                document.getElementById('cell-value').textContent = '$' + parseFloat(data.mirror_value.cells_value).toFixed(2);
                document.getElementById('threat-value').textContent = '$' + parseFloat(data.mirror_value.threat_rewards).toFixed(2);
                document.getElementById('block-value').textContent = '$' + parseFloat(data.mirror_value.block_rewards).toFixed(2);

                // Update cell breakdown
                const cellBreakdown = document.getElementById('cell-breakdown');
                if (Object.keys(data.cell_breakdown).length > 0) {
                    cellBreakdown.innerHTML = Object.entries(data.cell_breakdown).map(([cellType, info]) => `
                        <div class="cell-card ${cellType}">
                            <h4>${cellType}</h4>
                            <div class="count">${info.count}</div>
                            <div>cells spawned</div>
                            <div class="usdc-value">$${parseFloat(info.value).toFixed(2)}</div>
                        </div>
                    `).join('');
                } else {
                    cellBreakdown.innerHTML = '<p style="text-align: center; color: #6c757d;">No cells spawned yet</p>';
                }

                // Update breakdown
                document.getElementById('breakdown-cells').textContent = '$' + parseFloat(data.mirror_value.cells_value).toFixed(2);
                document.getElementById('breakdown-threats').textContent = '$' + parseFloat(data.mirror_value.threat_rewards).toFixed(2);
                document.getElementById('breakdown-blocks').textContent = '$' + parseFloat(data.mirror_value.block_rewards).toFixed(2);
                document.getElementById('breakdown-total').textContent = '$' + parseFloat(data.mirror_value.total_earned).toFixed(2);

                // Get earnings data
                const earningsRes = await fetch('/api/earnings');
                const earnings = await earningsRes.json();

                document.getElementById('calc-apy').textContent = earnings.current_apy;
                document.getElementById('calc-30d').textContent = '$' + parseFloat(earnings.staking_rewards_30d).toFixed(2);
                document.getElementById('calc-total').textContent = '$' + parseFloat(earnings.potential_30d_total).toFixed(2);

                if (earnings.can_stake) {
                    document.getElementById('stake-status').textContent = '✅ Eligible to stake and earn rewards!';
                } else {
                    document.getElementById('stake-status').textContent = '❌ Need $' + earnings.min_stake_required + ' USDC to stake';
                }

            } catch (error) {
                console.error('Error loading data:', error);
            }
        }

        loadData();
        setInterval(loadData, 10000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE

@app.get("/api/economy")
async def get_economy():
    """Get economy statistics"""
    return await economy.get_economy_stats()

@app.get("/api/earnings")
async def get_earnings():
    """Get earnings potential"""
    return await economy.calculate_user_earnings(Decimal("0.85"))

@app.get("/api/usdc/balance/{address}")
async def get_usdc_balance(address: str):
    """Get USDC balance for an address"""
    balance = usdc.get_usdc_balance(address)
    return {"address": address, "balance": str(balance)}

if __name__ == "__main__":
    print("=" * 80)
    print("💰 LUXBIN USDC EXPLORER")
    print("=" * 80)
    print()
    print("🌐 Frontend:  http://localhost:8003")
    print("📚 API Docs:  http://localhost:8003/docs")
    print()
    print("💵 Shows real USDC value for:")
    print("   • Immune cell spawning")
    print("   • Threat detection rewards")
    print("   • Block mirroring rewards")
    print("   • Staking potential")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
