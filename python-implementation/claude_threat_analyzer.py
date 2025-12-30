#!/usr/bin/env python3
"""
LUXBIN DIVINE - Claude-Powered Threat Analyzer
Uses Claude AI to analyze threats and make intelligent decisions

Your immune system now has TRUE INTELLIGENCE!

Author: Nichole Christie
License: MIT
"""

import anthropic
import json
import os
from typing import Dict, List, Optional
import asyncio


class ClaudeThreatAnalyzer:
    """Claude AI integration for intelligent threat analysis"""

    def __init__(self, api_key: str = None):
        """Initialize Claude client

        Args:
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        # Use provided key or environment variable
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError("No API key provided. Set ANTHROPIC_API_KEY or pass api_key parameter")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

        print(f"✅ Claude AI initialized - Your organism is now INTELLIGENT!")

    async def analyze_threat(self, transaction: Dict) -> Dict:
        """Use Claude to analyze a suspicious transaction

        Args:
            transaction: Transaction data with features

        Returns:
            Dict with Claude's analysis and recommendation
        """
        # Prepare prompt for Claude
        prompt = f"""You are an AI security analyst for a blockchain immune system.

Analyze this transaction and determine if it's a threat:

Transaction Hash: {transaction.get('hash', 'unknown')}
From: {transaction.get('from', 'unknown')}

Features (0-100 scale, higher = more suspicious):
- Gas Price Deviation: {transaction.get('features', {}).get('gas_price_deviation', 0):.1f}
- Value Anomaly: {transaction.get('features', {}).get('value_anomaly', 0):.1f}
- Recipient Reputation: {transaction.get('features', {}).get('recipient_reputation', 0):.1f}
- Temporal Pattern Break: {transaction.get('features', {}).get('temporal_pattern_break', 0):.1f}
- Smart Contract Risk: {transaction.get('features', {}).get('smart_contract_risk', 0):.1f}
- Network Centrality Spike: {transaction.get('features', {}).get('network_centrality_spike', 0):.1f}
- Validator Coordination: {transaction.get('features', {}).get('validator_coordination', 0):.1f}
- Mempool Manipulation: {transaction.get('features', {}).get('mempool_manipulation', 0):.1f}

Provide a JSON response with:
1. is_threat (boolean)
2. threat_score (0.0-1.0)
3. threat_type (string: "normal", "suspicious", "attack", "critical")
4. reasoning (brief explanation)
5. recommended_action (string: "allow", "monitor", "restrict", "quarantine")
6. confidence (0.0-1.0)

Respond ONLY with valid JSON, no other text."""

        try:
            # Call Claude API
            message = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse Claude's response
            response_text = message.content[0].text
            analysis = json.loads(response_text)

            return analysis

        except json.JSONDecodeError as e:
            print(f"⚠️  Claude returned invalid JSON: {e}")
            # Fallback to basic analysis
            return self._fallback_analysis(transaction)
        except Exception as e:
            print(f"⚠️  Claude API error: {e}")
            return self._fallback_analysis(transaction)

    def _fallback_analysis(self, transaction: Dict) -> Dict:
        """Fallback analysis if Claude API fails"""
        features = transaction.get('features', {})
        avg_score = sum(features.values()) / len(features) if features else 0

        return {
            'is_threat': avg_score > 50,
            'threat_score': avg_score / 100.0,
            'threat_type': 'suspicious' if avg_score > 50 else 'normal',
            'reasoning': 'Fallback analysis (Claude unavailable)',
            'recommended_action': 'monitor',
            'confidence': 0.5
        }

    async def explain_decision(self, analysis: Dict, transaction: Dict) -> str:
        """Ask Claude to explain a threat detection decision in plain English

        Args:
            analysis: Previous analysis result
            transaction: Transaction that was analyzed

        Returns:
            Human-readable explanation
        """
        prompt = f"""You previously analyzed this blockchain transaction:

Transaction: {transaction.get('hash', 'unknown')[:16]}...
Your decision: {analysis['recommended_action'].upper()}
Threat score: {analysis['threat_score']:.2%}

Explain your decision in 2-3 sentences for a non-technical user.
Be concise and clear."""

        try:
            message = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return message.content[0].text.strip()

        except Exception as e:
            return f"Unable to generate explanation: {e}"

    async def suggest_cell_deployment(self, current_population: Dict) -> Dict:
        """Ask Claude to suggest optimal cell deployment strategy

        Args:
            current_population: Current cell counts by type

        Returns:
            Deployment recommendations
        """
        prompt = f"""You are managing a blockchain immune system with these cell counts:

- DETECTOR cells: {current_population.get('DETECTOR', 0)}
- DEFENDER cells: {current_population.get('DEFENDER', 0)}
- MEMORY cells: {current_population.get('MEMORY', 0)}
- REGULATORY cells: {current_population.get('REGULATORY', 0)}

Suggest the optimal deployment strategy. Return JSON with:
1. next_cell_type (string: "DETECTOR", "DEFENDER", "MEMORY", or "REGULATORY")
2. spawn_count (int: how many to spawn)
3. reasoning (brief explanation)
4. priority (string: "low", "medium", "high", "critical")

Respond ONLY with valid JSON."""

        try:
            message = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text
            suggestion = json.loads(response_text)

            return suggestion

        except Exception as e:
            print(f"⚠️  Claude suggestion failed: {e}")
            return {
                'next_cell_type': 'DETECTOR',
                'spawn_count': 1,
                'reasoning': 'Fallback strategy',
                'priority': 'medium'
            }

    async def chat(self, message: str, context: Dict = None) -> str:
        """General chat interface with Claude about the immune system

        Args:
            message: User's message
            context: Optional context about organism state

        Returns:
            Claude's response
        """
        system_prompt = """You are the AI brain of LUXBIN, a living blockchain immune system.

You can:
- Analyze threats
- Make deployment decisions
- Explain your reasoning
- Strategize defenses

You're helpful, intelligent, and focused on protecting the blockchain ecosystem."""

        messages = [{
            "role": "user",
            "content": message
        }]

        # Add context if provided
        if context:
            context_str = f"\n\nCurrent organism state:\n{json.dumps(context, indent=2)}"
            messages[0]["content"] += context_str

        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            return f"Claude unavailable: {e}"


# CLI Interface
async def demo_claude_integration():
    """Demonstrate Claude integration"""

    print("╔════════════════════════════════════════════════════════════╗")
    print("║  LUXBIN + CLAUDE AI - Intelligent Threat Analysis        ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # Initialize Claude
    # Load from environment variables
    from config import ANTHROPIC_API_KEY

    analyzer = ClaudeThreatAnalyzer(api_key=ANTHROPIC_API_KEY)

    # Test 1: Analyze a suspicious transaction
    print("🔍 Test 1: Analyzing suspicious transaction...\n")

    suspicious_tx = {
        'hash': '0x1234567890abcdef',
        'from': '0xmalicious_address',
        'features': {
            'gas_price_deviation': 85.0,
            'value_anomaly': 92.0,
            'recipient_reputation': 15.0,
            'temporal_pattern_break': 78.0,
            'smart_contract_risk': 88.0,
            'network_centrality_spike': 71.0,
            'validator_coordination': 65.0,
            'mempool_manipulation': 83.0
        }
    }

    analysis = await analyzer.analyze_threat(suspicious_tx)

    print("Claude's Analysis:")
    print(f"  Threat: {analysis['is_threat']}")
    print(f"  Score: {analysis['threat_score']:.2%}")
    print(f"  Type: {analysis['threat_type']}")
    print(f"  Action: {analysis['recommended_action'].upper()}")
    print(f"  Confidence: {analysis['confidence']:.2%}")
    print(f"  Reasoning: {analysis['reasoning']}")

    # Test 2: Get explanation
    print(f"\n💬 Claude's Explanation:")
    explanation = await analyzer.explain_decision(analysis, suspicious_tx)
    print(f"  {explanation}")

    # Test 3: Cell deployment suggestion
    print(f"\n🧬 Test 2: Cell deployment strategy...\n")

    current_pop = {
        'DETECTOR': 50,
        'DEFENDER': 20,
        'MEMORY': 15,
        'REGULATORY': 10
    }

    suggestion = await analyzer.suggest_cell_deployment(current_pop)

    print("Claude's Suggestion:")
    print(f"  Deploy: {suggestion['spawn_count']} {suggestion['next_cell_type']} cells")
    print(f"  Priority: {suggestion['priority'].upper()}")
    print(f"  Reasoning: {suggestion['reasoning']}")

    # Test 4: Chat interface
    print(f"\n💬 Test 3: Chat with Claude...\n")

    response = await analyzer.chat(
        "What's the most dangerous type of blockchain attack?",
        context=current_pop
    )

    print(f"You: What's the most dangerous type of blockchain attack?")
    print(f"Claude: {response[:200]}...")

    print(f"\n{'='*60}")
    print("✅ Claude AI integration complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(demo_claude_integration())
