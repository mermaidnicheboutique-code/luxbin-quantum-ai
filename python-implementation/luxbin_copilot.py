#!/usr/bin/env python3
"""
LUXBIN COPILOT - AI Coding Expert
Your personal coding assistant powered by Claude + GPT-4

Helps with:
- Writing code
- Debugging
- Code review
- Smart contracts
- Blockchain monitoring
- Code execution
- Architecture decisions
- And more!
"""

import asyncio
import os
from pathlib import Path
from typing import List
import anthropic
import openai
import subprocess
import tempfile
import web3
import requests
from flask import Flask, render_template_string, request
from circle_api import LuxbinCircleAPI

class LuxbinCopilot:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.conversation = []

        # Initialize APIs
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY', 'your-key-here'))
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY', 'your-key-here'))
        self.grok_client = openai.OpenAI(
            api_key=os.getenv('GROK_API_KEY', 'your-key-here'),
            base_url="https://api.x.ai/v1"
        )
        self.circle_api = LuxbinCircleAPI()

    async def chat(self, message: str, use_gpt: bool = False) -> str:
        """Chat with the copilot

        Args:
            message: User message
            use_gpt: Use GPT-4 instead of Claude

        Returns:
            AI response
        """
        system_prompt = """You are LUXBIN Copilot, an expert AI coding assistant.
        Help with Python, Solidity, blockchain development, and LUXBIN project tasks.
        Be concise but thorough. Give actual code, not just descriptions."""

        # Try Claude first (better for coding), fall back to GPT-4, then Grok
        for attempt in range(3):
            try:
                if attempt == 0 and not use_gpt:
                    # Try Claude first
                    response = await asyncio.to_thread(
                        self.claude.messages.create,
                        model="claude-sonnet-4-5-20250929",
                        max_tokens=4096,
                        system=system_prompt,
                        messages=self.conversation + [{"role": "user", "content": message}]
                    )
                    reply = response.content[0].text
                elif attempt == 1 or use_gpt:
                    # Try GPT-4
                    response = await asyncio.to_thread(
                        self.openai_client.chat.completions.create,
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *self.conversation,
                            {"role": "user", "content": message}
                        ],
                        max_tokens=4096
                    )
                    reply = response.choices[0].message.content
                else:
                    # Try Grok
                    response = await asyncio.to_thread(
                        self.grok_client.chat.completions.create,
                        model="grok-2-1212",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *self.conversation,
                            {"role": "user", "content": message}
                        ],
                        max_tokens=4096
                    )
                    reply = response.choices[0].message.content

                # Add to history
                self.conversation.append({"role": "user", "content": message})
                self.conversation.append({"role": "assistant", "content": reply})

                return reply

            except Exception as e:
                error_msg = str(e)[:100]
                if attempt < 2:
                    # Try next service
                    continue
                else:
                    # All failed
                    return f"Error: All AI services failed. Last error: {error_msg}..."

        return "Error: Unable to connect to AI services"

    async def read_file(self, filepath: str) -> str:
        """Read a file from the project"""
        try:
            full_path = self.project_root / filepath
            if not full_path.exists():
                return f"File not found: {filepath}"

            with open(full_path, 'r') as f:
                content = f.read()

            return content
        except Exception as e:
            return f"Error reading file: {e}"

    async def write_file(self, filepath: str, content: str) -> str:
        """Write content to a file"""
        try:
            full_path = self.project_root / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(content)

            return f"Written to {filepath}"
        except Exception as e:
            return f"Error writing file: {e}"

    async def run_python_code(self, code: str) -> str:
        """Execute Python code locally and return output"""
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # Run the code
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=self.project_root
            )

            # Clean up
            os.unlink(temp_file)

            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr

            if result.returncode != 0:
                output += f"\nExit code: {result.returncode}"

            return output or "Code executed successfully (no output)"

        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out (30 seconds)"
        except Exception as e:
            return f"Error executing code: {e}"

    async def get_blockchain_status(self) -> str:
        """Get current blockchain status"""
        try:
            w3 = web3.Web3(web3.Web3.HTTPProvider('https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))

            if not w3.is_connected():
                return "Unable to connect to Ethereum mainnet"

            latest_block = w3.eth.get_block('latest')
            gas_price = w3.eth.gas_price
            block_number = w3.eth.block_number

            # Get ETH price from CoinGecko
            try:
                price_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd', timeout=5)
                eth_price = price_response.json()['ethereum']['usd'] if price_response.status_code == 200 else 'N/A'
            except:
                eth_price = 'N/A'

            status = f"""
Ethereum Mainnet Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Block: #{block_number:,}
Latest Block Time: {latest_block.timestamp}
Gas Price: {w3.from_wei(gas_price, 'gwei'):.2f} gwei
ETH Price: ${eth_price} USD
Network: Connected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            return status

        except Exception as e:
            return f"Error getting blockchain status: {e}"

    async def build_blockchain_explorer(self) -> str:
        """Generate a simple blockchain explorer Flask app"""
        explorer_code = '''#!/usr/bin/env python3
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
    print("LUXBIN Blockchain Explorer starting...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

        # Write the explorer code to a file
        result = await self.write_file('blockchain_explorer.py', explorer_code)
        return f"{result}\n\nTo run the explorer:\n1. python3 blockchain_explorer.py\n2. Open http://localhost:5000 in your browser\n\nThe explorer provides:\n• Real-time blockchain stats\n• Block search by number\n• Transaction lookup\n• Address balance checking"

    async def list_files(self, directory: str = "") -> List[str]:
        """List files in a directory"""
        try:
            target_dir = self.project_root / directory if directory else self.project_root
            files = []

            for item in target_dir.iterdir():
                if item.is_file():
                    files.append(str(item.relative_to(self.project_root)))
                elif item.is_dir() and not item.name.startswith('.'):
                    files.append(f"{item.relative_to(self.project_root)}/")

            return sorted(files)
        except Exception as e:
            return [f"Error: {e}"]

    async def review_code(self, filepath: str) -> str:
        """Get AI code review of a file"""
        content = await self.read_file(filepath)

        if "Error" in content or "not found" in content:
            return content

        prompt = f"""Review this code from {filepath}:

```
{content}
```

Provide:
1. Overall quality rating (1-10)
2. Security issues (if any)
3. Performance improvements
4. Best practice violations
5. Suggestions for improvement

Be specific and actionable."""

        return await self.chat(prompt)

    async def explain_code(self, filepath: str) -> str:
        """Get detailed explanation of code"""
        content = await self.read_file(filepath)

        if "Error" in content or "not found" in content:
            return content

        prompt = f"""Explain this code in detail:

File: {filepath}

```
{content}
```

Explain:
- What it does
- How it works
- Key concepts
- Dependencies
- How it fits in the LUXBIN project"""

        return await self.chat(prompt)

    async def debug_help(self, error_message: str, filepath: str = None) -> str:
        """Get help debugging an error"""
        context = ""
        if filepath:
            content = await self.read_file(filepath)
            context = f"\n\nCode from {filepath}:\n```\n{content}\n```"

        prompt = f"""Help me debug this error:

Error: {error_message}{context}

Provide:
1. What's causing the error
2. How to fix it
3. Code example of the fix
4. How to prevent it in future"""

        return await self.chat(prompt)

    async def write_code(self, description: str, language: str = "python") -> str:
        """Generate code based on description"""
        prompt = f"""Write {language} code for:

{description}

Requirements:
- Working, production-ready code
- Proper error handling
- Comments for complex parts
- Follows LUXBIN project style
- Security best practices

Provide complete, runnable code."""

        return await self.chat(prompt)

    async def improve_code(self, code: str) -> str:
        """Get suggestions to improve code"""
        prompt = f"""Improve this code:

```
{code}
```

Provide:
1. Refactored version
2. What was improved
3. Why it's better
4. Performance impact"""

        return await self.chat(prompt)

    async def interactive_mode(self):
        """Interactive copilot mode"""

        print("LUXBIN Copilot - Interactive Mode\n")
        print("Commands:")
        print("  • Chat naturally for coding help")
        print("  • 'read <file>' - Read a file")
        print("  • 'write <file>' - Write a file (will prompt for content)")
        print("  • 'review <file>' - Get code review")
        print("  • 'explain <file>' - Explain code")
        print("  • 'debug <error>' - Help with debugging")
        print("  • 'write code <description>' - Generate code")
        print("  • 'improve <code>' - Improve code snippet")
        print("  • 'run <code>' - Run Python code")
        print("  • 'execute <file>' - Execute a Python file")
        print("  • 'status' - Get blockchain status")
        print("  • 'build explorer' - Build a blockchain explorer")
        print("  • 'list [dir]' - List files")
        print("  • 'clear' - Clear conversation history")
        print("  • 'exit' - Quit")
        print()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    print("\nGoodbye!")
                    break

                elif user_input.lower() == 'clear':
                    self.conversation = []
                    print("Conversation history cleared\n")

                elif user_input.lower().startswith('read '):
                    filepath = user_input[5:].strip()
                    content = await self.read_file(filepath)
                    print(f"\n{filepath}:\n")
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print()

                elif user_input.lower().startswith('write '):
                    filepath = user_input[6:].strip()
                    print(f"\nEnter content for {filepath} (Ctrl+D when done):")
                    lines = []
                    try:
                        while True:
                            line = input()
                            lines.append(line)
                    except EOFError:
                        pass
                    content = '\n'.join(lines)
                    result = await self.write_file(filepath, content)
                    print(f"\n{result}\n")

                elif user_input.lower().startswith('review '):
                    filepath = user_input[7:].strip()
                    print(f"\nReviewing {filepath}...\n")
                    review = await self.review_code(filepath)
                    print(f"Copilot:\n{review}\n")

                elif user_input.lower().startswith('explain '):
                    filepath = user_input[8:].strip()
                    print(f"\nExplaining {filepath}...\n")
                    explanation = await self.explain_code(filepath)
                    print(f"Copilot:\n{explanation}\n")

                elif user_input.lower().startswith('debug '):
                    error = user_input[6:].strip()
                    print(f"\nDebugging...\n")
                    help_text = await self.debug_help(error)
                    print(f"Copilot:\n{help_text}\n")

                elif user_input.lower().startswith('write code '):
                    description = user_input[11:].strip()
                    print(f"\nWriting code...\n")
                    code = await self.write_code(description)
                    print(f"Copilot:\n{code}\n")

                elif user_input.lower().startswith('improve '):
                    code_snippet = user_input[8:].strip()
                    print(f"\nImproving code...\n")
                    improvements = await self.improve_code(code_snippet)
                    print(f"Copilot:\n{improvements}\n")

                elif user_input.lower().startswith('run '):
                    code = user_input[4:].strip()
                    print(f"\nRunning Python code...\n")
                    result = await self.run_python_code(code)
                    print(f"Output:\n{result}\n")

                elif user_input.lower().startswith('execute '):
                    filepath = user_input[8:].strip()
                    content = await self.read_file(filepath)
                    if "Error" in content or "not found" in content:
                        print(f"\n{content}\n")
                    else:
                        print(f"\nExecuting {filepath}...\n")
                        result = await self.run_python_code(content)
                        print(f"Output:\n{result}\n")

                elif user_input.lower() == 'status':
                    print(f"\nGetting blockchain status...\n")
                    status = await self.get_blockchain_status()
                    print(status)
                    print()

                elif user_input.lower() == 'build explorer':
                    print(f"\nBuilding blockchain explorer...\n")
                    result = await self.build_blockchain_explorer()
                    print(result)
                    print()

                elif user_input.lower().startswith('list'):
                    parts = user_input.split(maxsplit=1)
                    directory = parts[1] if len(parts) > 1 else ""
                    files = await self.list_files(directory)
                    print(f"\nFiles in {directory or 'project root'}:")
                    for f in files[:30]:  # Limit to 30
                        print(f"   {f}")
                    if len(files) > 30:
                        print(f"   ... and {len(files) - 30} more")
                    print()

                else:
                    # General coding question
                    print(f"\nCopilot:\n")
                    response = await self.chat(user_input, use_gpt=True)  # Use GPT-4 by default
                    print(response)
                    print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


async def main():
    """Main entry point"""

    copilot = LuxbinCopilot()

    print("Welcome to LUXBIN Copilot!\n")
    print("I can help you with:")
    print("  • Writing Python and Solidity code")
    print("  • Debugging issues")
    print("  • Reviewing your code")
    print("  • Explaining complex code")
    print("  • Running code locally")
    print("  • Blockchain status and exploration")
    print("  • Architecture decisions")
    print("  • LUXBIN project development")
    print("  • AI assistance via Claude, GPT-4, or Grok")
    print()

    # Quick examples
    print("Quick examples:")
    print("  'How do I deploy a smart contract?'")
    print("  'review python-implementation/organism_builder.py'")
    print("  'write code Create a function to validate Ethereum addresses'")
    print("  'run print(\"Hello, LUXBIN!\")'")
    print("  'execute test_mac_node.py'")
    print("  'status'")
    print("  'build explorer'")
    print("  'debug NameError: name config_env is not defined'")
    print()

    await copilot.interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")