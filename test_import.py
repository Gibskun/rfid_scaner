#!/usr/bin/env python3
"""
Test Import - Check if importing from main.py triggers RFID scanning
"""

print("🧪 Testing import from main.py...")

try:
    from main import FastRFIDScanner
    print("✅ Successfully imported FastRFIDScanner from main.py")
    print("🔍 No RFID scanning should have started")
except Exception as e:
    print(f"❌ Error importing from main.py: {e}")

print("✅ Test completed - no scanning should be active")