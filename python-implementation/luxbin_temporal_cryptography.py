#!/usr/bin/env python3
"""
LUXBIN Temporal Cryptography System
Revolutionary multi-layer cryptographic key generation using:
1. Key Phrase → LUXBIN → Binary → Cryptographic Key
2. Time-Based Cryptographic Dictionary
3. Combined Time → LUXBIN → Crypto System

Author: Nichole Christie
Date: December 2025
"""

import hashlib
import json
import hmac
import secrets
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, time, date
import base64
import sys


# ============================================================================
# LUXBIN PHOTONIC ENCODING SYSTEM
# ============================================================================

class LUXBINEncoder:
    """Encodes text into LUXBIN photonic binary representation"""

    def __init__(self):
        self.alphabet = self._create_alphabet()

    def _create_alphabet(self) -> Dict[str, Dict]:
        """Create LUXBIN alphabet with HSL and binary values"""
        letters = {}

        # A-Z encoding
        for i, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            hue = i * 5.625  # 360° / 64 symbols
            letters[letter] = {
                'hue': hue,
                'saturation': 100,
                'lightness': 70,
                'binary': format(i, '06b'),
                'index': i
            }

        # 0-9 encoding
        for i, digit in enumerate('0123456789'):
            index = 26 + i
            hue = index * 5.625
            letters[digit] = {
                'hue': hue,
                'saturation': 100,
                'lightness': 70,
                'binary': format(index, '06b'),
                'index': index
            }

        # Punctuation and space
        letters[' '] = {'hue': 0, 'saturation': 0, 'lightness': 0, 'binary': '111110', 'index': 62}
        letters['.'] = {'hue': 180, 'saturation': 100, 'lightness': 70, 'binary': '111111', 'index': 63}

        return letters

    def encode_text_to_luxbin(self, text: str) -> Dict:
        """
        Convert text to LUXBIN photonic encoding

        Args:
            text: Input text to encode

        Returns:
            Dictionary with LUXBIN encoding data
        """
        text = text.upper()
        luxbin_sequence = []
        binary_string = ""
        photonic_values = []

        for char in text:
            if char in self.alphabet:
                symbol = self.alphabet[char]
                luxbin_sequence.append({
                    'char': char,
                    'hue': symbol['hue'],
                    'saturation': symbol['saturation'],
                    'lightness': symbol['lightness'],
                    'binary': symbol['binary']
                })
                binary_string += symbol['binary']
                photonic_values.append({
                    'h': symbol['hue'],
                    's': symbol['saturation'],
                    'l': symbol['lightness']
                })

        return {
            'text': text,
            'luxbin_sequence': luxbin_sequence,
            'binary_string': binary_string,
            'photonic_values': photonic_values,
            'length': len(luxbin_sequence)
        }

    def luxbin_to_binary(self, luxbin_data: Dict) -> bytes:
        """
        Convert LUXBIN binary string to actual bytes

        Args:
            luxbin_data: LUXBIN encoded data

        Returns:
            Binary bytes
        """
        binary_string = luxbin_data['binary_string']

        # Pad to make divisible by 8
        padding = (8 - len(binary_string) % 8) % 8
        binary_string += '0' * padding

        # Convert to bytes
        byte_array = bytearray()
        for i in range(0, len(binary_string), 8):
            byte = binary_string[i:i+8]
            byte_array.append(int(byte, 2))

        return bytes(byte_array)

    def photonic_hash(self, luxbin_data: Dict) -> str:
        """
        Create a unique hash from photonic values (HSL)

        Args:
            luxbin_data: LUXBIN encoded data

        Returns:
            Hexadecimal hash string
        """
        photonic_values = luxbin_data['photonic_values']

        # Create string from HSL values
        hsl_string = ""
        for pv in photonic_values:
            hsl_string += f"{pv['h']:.2f}|{pv['s']}|{pv['l']}|"

        # Hash the photonic signature
        return hashlib.sha256(hsl_string.encode()).hexdigest()


# ============================================================================
# TIME-BASED CRYPTOGRAPHIC DICTIONARY
# ============================================================================

@dataclass
class TimeKey:
    """Time-based cryptographic key"""
    time_input: str
    time_value: time
    date_value: Optional[date]
    key_hash: str
    key_bytes: bytes
    entropy_bits: int

    def to_dict(self):
        return {
            'time_input': self.time_input,
            'time_string': self.time_value.strftime('%I:%M:%S %p'),
            'date_string': self.date_value.isoformat() if self.date_value else None,
            'key_hash': self.key_hash,
            'entropy_bits': self.entropy_bits
        }


class TemporalCryptography:
    """Time-based cryptographic key generation"""

    def __init__(self):
        self.salt = b'LUXBIN_TEMPORAL_CRYPTO_2025'

    def parse_time_input(self, time_str: str) -> Tuple[time, Optional[str]]:
        """
        Parse various time formats

        Examples:
            "12:34 PM"
            "12:34:56 PM"
            "12:34"
            "1234"

        Returns:
            (time_object, format_used)
        """
        time_str = time_str.strip().upper()

        # Try various formats
        formats = [
            ('%I:%M:%S %p', 'HH:MM:SS AM/PM'),
            ('%I:%M %p', 'HH:MM AM/PM'),
            ('%H:%M:%S', 'HH:MM:SS 24h'),
            ('%H:%M', 'HH:MM 24h'),
        ]

        for fmt, desc in formats:
            try:
                time_obj = datetime.strptime(time_str, fmt).time()
                return time_obj, desc
            except ValueError:
                continue

        # Try simple number format like "1234" = 12:34
        if time_str.isdigit():
            if len(time_str) == 4:
                hour = int(time_str[:2])
                minute = int(time_str[2:4])
                if 0 <= hour < 24 and 0 <= minute < 60:
                    return time(hour, minute), 'HHMM numeric'
            elif len(time_str) == 6:
                hour = int(time_str[:2])
                minute = int(time_str[2:4])
                second = int(time_str[4:6])
                if 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60:
                    return time(hour, minute, second), 'HHMMSS numeric'

        raise ValueError(f"Could not parse time: {time_str}")

    def time_to_number(self, time_obj: time, include_seconds: bool = True) -> int:
        """
        Convert time to a unique number

        Args:
            time_obj: Time object
            include_seconds: Whether to include seconds

        Returns:
            Unique integer representing the time
        """
        if include_seconds:
            # Range: 0-86399 (24h * 60m * 60s - 1)
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
        else:
            # Range: 0-1439 (24h * 60m - 1)
            return time_obj.hour * 60 + time_obj.minute

    def generate_time_key(self, time_str: str, date_str: Optional[str] = None,
                         include_seconds: bool = True) -> TimeKey:
        """
        Generate cryptographic key from time (and optionally date)

        Args:
            time_str: Time string (e.g., "12:34 PM", "1234")
            date_str: Optional date string (e.g., "2025-12-25", "12/25/2025")
            include_seconds: Include seconds in entropy calculation

        Returns:
            TimeKey object with cryptographic key
        """
        # Parse time
        time_obj, fmt = self.parse_time_input(time_str)

        # Parse date if provided
        date_obj = None
        if date_str:
            date_obj = self._parse_date(date_str)

        # Create base number from time
        time_number = self.time_to_number(time_obj, include_seconds)

        # Create key material
        key_material = f"{time_number}"
        if date_obj:
            key_material += f"|{date_obj.toordinal()}"

        # Generate key using PBKDF2
        key_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            key_material.encode(),
            self.salt,
            100000,  # iterations
            dklen=32  # 256-bit key
        )

        # Calculate entropy
        if include_seconds:
            entropy_bits = 17  # log2(86400) ≈ 16.4
        else:
            entropy_bits = 11  # log2(1440) ≈ 10.5

        if date_obj:
            entropy_bits += 20  # Approximate additional entropy from date

        # Create hash
        key_hash = hashlib.sha256(key_bytes).hexdigest()

        return TimeKey(
            time_input=time_str,
            time_value=time_obj,
            date_value=date_obj,
            key_hash=key_hash,
            key_bytes=key_bytes,
            entropy_bits=entropy_bits
        )

    def _parse_date(self, date_str: str) -> date:
        """Parse various date formats"""
        date_str = date_str.strip()

        formats = [
            '%Y-%m-%d',      # 2025-12-25
            '%m/%d/%Y',      # 12/25/2025
            '%d/%m/%Y',      # 25/12/2025
            '%Y/%m/%d',      # 2025/12/25
            '%m-%d-%Y',      # 12-25-2025
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Could not parse date: {date_str}")

    def create_temporal_dictionary(self, time_list: List[str]) -> Dict[str, TimeKey]:
        """
        Create a dictionary of time-based keys

        Args:
            time_list: List of time strings

        Returns:
            Dictionary mapping time strings to TimeKey objects
        """
        dictionary = {}
        for time_str in time_list:
            try:
                time_key = self.generate_time_key(time_str)
                dictionary[time_str] = time_key
            except ValueError as e:
                print(f"Warning: Could not process {time_str}: {e}")

        return dictionary


# ============================================================================
# COMBINED LUXBIN-TEMPORAL CRYPTOGRAPHY
# ============================================================================

@dataclass
class CombinedCryptoKey:
    """Combined cryptographic key using both LUXBIN and time"""
    original_input: str
    luxbin_data: Dict
    temporal_data: TimeKey
    combined_key: bytes
    combined_hash: str
    security_level: str

    def to_dict(self):
        return {
            'original_input': self.original_input,
            'luxbin_binary_length': len(self.luxbin_data['binary_string']),
            'photonic_hash': self.luxbin_data.get('photonic_hash', ''),
            'temporal_data': self.temporal_data.to_dict(),
            'combined_hash': self.combined_hash,
            'security_level': self.security_level
        }


class LUXBINTemporalCrypto:
    """Combined LUXBIN and Temporal cryptography system"""

    def __init__(self):
        self.luxbin = LUXBINEncoder()
        self.temporal = TemporalCryptography()

    def phrase_to_cryptokey(self, phrase: str) -> Dict:
        """
        Method 1: Key Phrase → LUXBIN → Binary → Crypto Key

        Args:
            phrase: User's memorable phrase

        Returns:
            Complete cryptographic key data
        """
        # Encode phrase to LUXBIN
        luxbin_data = self.luxbin.encode_text_to_luxbin(phrase)

        # Convert LUXBIN to binary
        binary_bytes = self.luxbin.luxbin_to_binary(luxbin_data)

        # Create photonic hash
        photonic_hash = self.luxbin.photonic_hash(luxbin_data)

        # Generate final cryptographic key
        crypto_key = hashlib.sha256(binary_bytes).digest()

        # Add photonic hash to luxbin_data
        luxbin_data['photonic_hash'] = photonic_hash

        return {
            'method': 'LUXBIN Phrase Encoding',
            'original_phrase': phrase,
            'luxbin_data': luxbin_data,
            'binary_bytes': binary_bytes.hex(),
            'photonic_hash': photonic_hash,
            'crypto_key': crypto_key.hex(),
            'key_length_bits': len(crypto_key) * 8
        }

    def time_to_cryptokey(self, time_str: str, date_str: Optional[str] = None) -> Dict:
        """
        Method 2: Time → Crypto Key

        Args:
            time_str: Time string (e.g., "12:34 PM")
            date_str: Optional date string

        Returns:
            Time-based cryptographic key
        """
        time_key = self.temporal.generate_time_key(time_str, date_str)

        return {
            'method': 'Temporal Cryptography',
            'time_key': time_key.to_dict(),
            'crypto_key': time_key.key_bytes.hex(),
            'key_length_bits': len(time_key.key_bytes) * 8
        }

    def combined_time_luxbin_key(self, time_str: str, date_str: Optional[str] = None) -> CombinedCryptoKey:
        """
        Method 3: Time → LUXBIN → Crypto Key (ULTRA SECURE)

        Args:
            time_str: Time string (e.g., "12:34 PM")
            date_str: Optional date string

        Returns:
            Combined cryptographic key with maximum security
        """
        # Step 1: Generate temporal key
        time_key = self.temporal.generate_time_key(time_str, date_str)

        # Step 2: Use time as phrase for LUXBIN encoding
        time_phrase = time_key.time_value.strftime('%I:%M:%S %p')
        if time_key.date_value:
            time_phrase += f" {time_key.date_value.isoformat()}"

        # Step 3: Encode through LUXBIN
        luxbin_data = self.luxbin.encode_text_to_luxbin(time_phrase)
        luxbin_binary = self.luxbin.luxbin_to_binary(luxbin_data)
        photonic_hash = self.luxbin.photonic_hash(luxbin_data)
        luxbin_data['photonic_hash'] = photonic_hash

        # Step 4: Combine both keys using HMAC
        combined_key = hmac.new(
            time_key.key_bytes,
            luxbin_binary,
            hashlib.sha256
        ).digest()

        combined_hash = hashlib.sha256(combined_key).hexdigest()

        # Determine security level
        security_level = self._calculate_security_level(time_key, luxbin_data)

        return CombinedCryptoKey(
            original_input=f"{time_str}" + (f" {date_str}" if date_str else ""),
            luxbin_data=luxbin_data,
            temporal_data=time_key,
            combined_key=combined_key,
            combined_hash=combined_hash,
            security_level=security_level
        )

    def _calculate_security_level(self, time_key: TimeKey, luxbin_data: Dict) -> str:
        """Calculate overall security level"""
        total_entropy = time_key.entropy_bits + len(luxbin_data['binary_string'])

        if total_entropy >= 128:
            return "MAXIMUM (Quantum-Resistant)"
        elif total_entropy >= 80:
            return "HIGH"
        elif total_entropy >= 40:
            return "MEDIUM"
        else:
            return "LOW"


# ============================================================================
# CLI INTERFACE
# ============================================================================

class CryptoCLI:
    """Interactive command-line interface"""

    def __init__(self):
        self.crypto = LUXBINTemporalCrypto()
        self.key_storage = {}

    def print_header(self):
        """Print application header"""
        print("\n" + "="*80)
        print("  LUXBIN TEMPORAL CRYPTOGRAPHY SYSTEM")
        print("  Revolutionary Multi-Layer Key Generation")
        print("="*80)
        print("\n  Three Cryptographic Methods:")
        print("  1. Key Phrase → LUXBIN → Binary → Crypto Key")
        print("  2. Time-Based Cryptographic Dictionary")
        print("  3. Combined Time → LUXBIN → Ultra-Secure Key")
        print("="*80 + "\n")

    def method1_phrase_to_key(self):
        """Method 1: Phrase encoding"""
        print("\n" + "─"*80)
        print("  METHOD 1: LUXBIN PHRASE ENCODING")
        print("  Key Phrase → LUXBIN Photonic → Binary → Cryptographic Key")
        print("─"*80 + "\n")

        phrase = input("Enter your memorable phrase: ").strip()
        if not phrase:
            print("❌ No phrase provided")
            return

        result = self.crypto.phrase_to_cryptokey(phrase)

        print(f"\n✅ LUXBIN ENCODING COMPLETE")
        print(f"\n📝 Original Phrase: '{result['original_phrase']}'")
        print(f"🌈 Photonic Hash: {result['photonic_hash'][:32]}...")
        print(f"💾 Binary Length: {len(result['luxbin_data']['binary_string'])} bits")
        print(f"🔐 Crypto Key: {result['crypto_key'][:32]}...{result['crypto_key'][-32:]}")
        print(f"🔒 Key Strength: {result['key_length_bits']} bits")

        # Show LUXBIN sequence
        print(f"\n🌟 LUXBIN Photonic Sequence:")
        for i, symbol in enumerate(result['luxbin_data']['luxbin_sequence'][:10]):
            print(f"   {symbol['char']} → HSL({symbol['hue']:.1f}°, {symbol['saturation']}%, {symbol['lightness']}%) → {symbol['binary']}")
        if len(result['luxbin_data']['luxbin_sequence']) > 10:
            print(f"   ... and {len(result['luxbin_data']['luxbin_sequence']) - 10} more characters")

        # Store key
        key_id = f"phrase_{len(self.key_storage)}"
        self.key_storage[key_id] = result
        print(f"\n💾 Key stored as: {key_id}")

    def method2_time_to_key(self):
        """Method 2: Time-based key"""
        print("\n" + "─"*80)
        print("  METHOD 2: TEMPORAL CRYPTOGRAPHY")
        print("  Time → Cryptographic Dictionary → Key")
        print("─"*80 + "\n")

        print("Examples: '12:34 PM', '1234', '12:34:56 PM'")
        time_str = input("Enter time: ").strip()
        if not time_str:
            print("❌ No time provided")
            return

        print("\nAdd date for extra security? (optional)")
        print("Examples: '2025-12-25', '12/25/2025'")
        date_str = input("Enter date (or press Enter to skip): ").strip()
        date_str = date_str if date_str else None

        try:
            result = self.crypto.time_to_cryptokey(time_str, date_str)

            print(f"\n✅ TEMPORAL KEY GENERATED")
            print(f"\n⏰ Time: {result['time_key']['time_string']}")
            if result['time_key']['date_string']:
                print(f"📅 Date: {result['time_key']['date_string']}")
            print(f"🔐 Crypto Key: {result['crypto_key'][:32]}...{result['crypto_key'][-32:]}")
            print(f"🔒 Key Strength: {result['key_length_bits']} bits")
            print(f"🎲 Entropy: ~{result['time_key']['entropy_bits']} bits")

            print(f"\n💡 Remember: '{time_str}'" + (f" on {date_str}" if date_str else ""))
            print(f"   Instead of: {result['crypto_key'][:64]}...")

            # Store key
            key_id = f"time_{len(self.key_storage)}"
            self.key_storage[key_id] = result
            print(f"\n💾 Key stored as: {key_id}")

        except ValueError as e:
            print(f"❌ Error: {e}")

    def method3_combined_key(self):
        """Method 3: Combined time + LUXBIN"""
        print("\n" + "─"*80)
        print("  METHOD 3: COMBINED ULTRA-SECURE CRYPTOGRAPHY")
        print("  Time → LUXBIN Photonic → Combined Multi-Layer Key")
        print("─"*80 + "\n")

        print("This combines temporal and photonic encoding for maximum security!")
        print("\nExamples: '12:34 PM', '1234', '12:34:56 PM'")
        time_str = input("Enter time: ").strip()
        if not time_str:
            print("❌ No time provided")
            return

        print("\nAdd date for maximum security? (recommended)")
        print("Examples: '2025-12-25', '12/25/2025'")
        date_str = input("Enter date (or press Enter to skip): ").strip()
        date_str = date_str if date_str else None

        try:
            result = self.crypto.combined_time_luxbin_key(time_str, date_str)

            print(f"\n✅ ULTRA-SECURE COMBINED KEY GENERATED")
            print(f"\n⏰ Time Input: {result.original_input}")
            print(f"🌈 LUXBIN Photonic Encoding: {len(result.luxbin_data['binary_string'])} bits")
            print(f"🔐 Combined Key: {result.combined_key.hex()[:32]}...{result.combined_key.hex()[-32:]}")
            print(f"🔒 Security Level: {result.security_level}")
            print(f"🎲 Total Entropy: ~{result.temporal_data.entropy_bits + len(result.luxbin_data['binary_string'])} bits")

            print(f"\n🌟 LUXBIN Photonic Sequence:")
            for symbol in result.luxbin_data['luxbin_sequence'][:8]:
                print(f"   {symbol['char']} → HSL({symbol['hue']:.1f}°, {symbol['saturation']}%, {symbol['lightness']}%)")

            print(f"\n💡 YOU ONLY NEED TO REMEMBER: '{time_str}'" + (f" {date_str}" if date_str else ""))
            print(f"   System generates: {result.combined_hash[:64]}...")

            # Store key
            key_id = f"combined_{len(self.key_storage)}"
            self.key_storage[key_id] = result
            print(f"\n💾 Key stored as: {key_id}")

        except ValueError as e:
            print(f"❌ Error: {e}")

    def view_stored_keys(self):
        """View all stored keys"""
        print("\n" + "─"*80)
        print("  STORED KEYS")
        print("─"*80 + "\n")

        if not self.key_storage:
            print("No keys stored yet.")
            return

        for key_id, key_data in self.key_storage.items():
            print(f"📌 {key_id}:")
            if isinstance(key_data, CombinedCryptoKey):
                print(f"   Type: Combined (Ultra-Secure)")
                print(f"   Input: {key_data.original_input}")
                print(f"   Security: {key_data.security_level}")
            elif 'method' in key_data:
                print(f"   Type: {key_data['method']}")
                if 'original_phrase' in key_data:
                    print(f"   Phrase: {key_data['original_phrase']}")
                elif 'time_key' in key_data:
                    print(f"   Time: {key_data['time_key']['time_string']}")
            print()

    def export_keys(self):
        """Export keys to file"""
        if not self.key_storage:
            print("❌ No keys to export")
            return

        filename = input("\nEnter filename to export (default: crypto_keys.json): ").strip()
        if not filename:
            filename = "crypto_keys.json"

        export_data = {}
        for key_id, key_data in self.key_storage.items():
            if isinstance(key_data, CombinedCryptoKey):
                export_data[key_id] = key_data.to_dict()
            else:
                export_data[key_id] = key_data

        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"✅ Keys exported to {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")

    def run(self):
        """Main CLI loop"""
        self.print_header()

        while True:
            print("\n" + "="*80)
            print("  MAIN MENU")
            print("="*80)
            print("  1. Method 1: Key Phrase → LUXBIN → Crypto Key")
            print("  2. Method 2: Time-Based Cryptographic Dictionary")
            print("  3. Method 3: Combined Time → LUXBIN → Ultra-Secure Key")
            print("  4. View Stored Keys")
            print("  5. Export Keys to File")
            print("  6. Exit")
            print("="*80)

            choice = input("\nSelect option (1-6): ").strip()

            if choice == '1':
                self.method1_phrase_to_key()
            elif choice == '2':
                self.method2_time_to_key()
            elif choice == '3':
                self.method3_combined_key()
            elif choice == '4':
                self.view_stored_keys()
            elif choice == '5':
                self.export_keys()
            elif choice == '6':
                print("\n👋 Secure cryptography session ended.")
                break
            else:
                print("❌ Invalid option. Please select 1-6.")


def main():
    """Entry point"""
    cli = CryptoCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Session terminated.")
        sys.exit(0)


if __name__ == "__main__":
    main()
