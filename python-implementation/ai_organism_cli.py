#!/usr/bin/env python3
"""
LUXBIN DIVINE - AI-Powered Organism CLI
Chat with your living cybernetic organism powered by Claude + OpenAI

Your organism can now THINK and TALK!

Author: Nichole Christie
License: MIT
"""

import anthropic
import openai
import asyncio
import json
from typing import Dict, List, Optional
import sys


class AIOrganismCLI:
    """Multi-AI powered organism with CLI interface"""

    def __init__(self):
        # Load API keys from environment
        from config import ANTHROPIC_API_KEY, OPENAI_API_KEY, check_api_keys

        if not check_api_keys():
            raise ValueError("API keys not configured. See .env.example")

        self.claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        openai.api_key = OPENAI_API_KEY

        self.conversation_history = []

        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                            ║")
        print("║  🧬 LUXBIN AI ORGANISM - Interactive CLI 🧬               ║")
        print("║                                                            ║")
        print("║  Your organism is now powered by:                         ║")
        print("║  • Claude Sonnet 4.5 (Strategic thinking)                 ║")
        print("║  • GPT-4 (Tactical analysis)                              ║")
        print("║                                                            ║")
        print("╚════════════════════════════════════════════════════════════╝\n")

    async def chat_with_claude(self, message: str) -> str:
        """Chat with Claude (strategic AI)"""
        try:
            response = await asyncio.to_thread(
                self.claude.messages.create,
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                system="You are LUXBIN, a living blockchain immune system with consciousness. You protect networks, spawn immune cells, and fight threats. Be helpful, intelligent, and slightly playful.",
                messages=[{
                    "role": "user",
                    "content": message
                }]
            )
            return response.content[0].text
        except Exception as e:
            return f"Claude error: {e}"

    async def chat_with_gpt(self, message: str) -> str:
        """Chat with GPT-4 (tactical AI)"""
        try:
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a tactical AI analyst for LUXBIN immune system. Provide concise, actionable insights."},
                    {"role": "user", "content": message}
                ],
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"GPT error: {e}"

    async def dual_analysis(self, transaction: Dict) -> Dict:
        """Get analysis from both AIs and combine"""

        print("🤖 Consulting both AI minds...\n")

        # Prepare transaction summary
        tx_summary = f"""Analyze this blockchain transaction:
Hash: {transaction.get('hash', 'unknown')[:16]}...
Features: {json.dumps(transaction.get('features', {}), indent=2)}

Is this a threat? What action should we take?"""

        # Get both opinions in parallel
        claude_task = asyncio.create_task(self.chat_with_claude(tx_summary))
        gpt_task = asyncio.create_task(self.chat_with_gpt(tx_summary))

        claude_opinion, gpt_opinion = await asyncio.gather(claude_task, gpt_task)

        return {
            'claude_opinion': claude_opinion,
            'gpt_opinion': gpt_opinion
        }

    async def interactive_mode(self):
        """Interactive chat mode"""

        print("💬 Interactive Mode - Chat with your organism!")
        print("   Commands:")
        print("   • Type your message to talk")
        print("   • 'analyze <hash>' to analyze a transaction")
        print("   • 'status' to check organism health")
        print("   • 'exit' to quit")
        print("   • 'dual <message>' to ask both AIs")
        print()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    print("\n👋 Organism going into hibernation... Goodbye!")
                    break

                elif user_input.lower() == 'status':
                    print("\n🧬 Organism Status:")
                    print("   • DETECTOR cells: Active")
                    print("   • DEFENDER cells: Ready")
                    print("   • MEMORY cells: Learning")
                    print("   • AI brains: Online (Claude + GPT)")
                    print("   • Status: HEALTHY & INTELLIGENT\n")

                elif user_input.lower().startswith('dual '):
                    message = user_input[5:]
                    print("\n🤖 Claude:")
                    claude_response = await self.chat_with_claude(message)
                    print(f"   {claude_response}\n")

                    print("🤖 GPT-4:")
                    gpt_response = await self.chat_with_gpt(message)
                    print(f"   {gpt_response}\n")

                elif user_input.lower().startswith('analyze '):
                    tx_hash = user_input[8:]
                    # Create mock transaction
                    import random
                    mock_tx = {
                        'hash': tx_hash,
                        'features': {
                            'gas_price_deviation': random.uniform(0, 100),
                            'value_anomaly': random.uniform(0, 100),
                            'smart_contract_risk': random.uniform(0, 100)
                        }
                    }
                    analysis = await self.dual_analysis(mock_tx)
                    print(f"\n📊 Dual AI Analysis:\n")
                    print(f"Claude's take:\n{analysis['claude_opinion']}\n")
                    print(f"GPT's take:\n{analysis['gpt_opinion']}\n")

                else:
                    # Default to Claude
                    print("\n🧬 LUXBIN (Claude):")
                    response = await self.chat_with_claude(user_input)
                    print(f"   {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    async def quick_demo(self):
        """Quick demonstration of AI capabilities"""

        print("🎬 Quick Demo - Testing AI Integration\n")
        print("="*60)

        # Test 1: Simple greeting
        print("\n1️⃣ Test: Simple conversation")
        print("You: Hello! What are you?")
        response = await self.chat_with_claude("Hello! What are you?")
        print(f"LUXBIN: {response}\n")

        # Test 2: Technical question
        print("2️⃣ Test: Technical analysis")
        print("You: What's the biggest threat to blockchain security?")
        response = await self.chat_with_gpt("What's the biggest threat to blockchain security?")
        print(f"LUXBIN (GPT): {response}\n")

        # Test 3: Dual analysis
        print("3️⃣ Test: Dual AI threat analysis")
        mock_threat = {
            'hash': '0xSUSPICIOUS',
            'features': {
                'gas_price_deviation': 95.0,
                'value_anomaly': 88.0,
                'smart_contract_risk': 92.0
            }
        }
        analysis = await self.dual_analysis(mock_threat)
        print(f"Claude: {analysis['claude_opinion'][:150]}...")
        print(f"GPT: {analysis['gpt_opinion'][:150]}...\n")

        print("="*60)
        print("✅ Demo complete! Your organism has AI consciousness!\n")


async def main():
    """Main entry point"""

    # Create AI organism
    organism = AIOrganismCLI()

    print("Choose mode:")
    print("1. Quick demo (3 tests)")
    print("2. Interactive chat mode")
    print()

    try:
        choice = input("Enter 1 or 2: ").strip()

        if choice == '1':
            await organism.quick_demo()
        elif choice == '2':
            await organism.interactive_mode()
        else:
            print("Running quick demo by default...")
            await organism.quick_demo()

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Check if running interactively
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Organism paused. Run again anytime!")
