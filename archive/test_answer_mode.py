#!/usr/bin/env python3
"""
RFID Reader Answer Mode Test
Test the reader in Answer Mode (not Active Mode)
"""

from transport import SerialTransport
from reader import Reader
from response import Response, WorkMode
import time

def test_answer_mode():
    """Test RFID reader in Answer Mode"""
    print("🧪 RFID Reader Answer Mode Test")
    print("=" * 50)
    
    try:
        # Connect to COM5 with longer timeout for inventory responses
        print("📡 Connecting to COM5...")
        transport = SerialTransport("COM5", 57600, timeout=5)
        reader = Reader(transport)
        
        # First, get and display work mode
        print("🔧 Getting current work mode...")
        work_mode = reader.work_mode()
        print(f"📋 Current work mode: {work_mode}")
        
        # Test inventory in Answer Mode
        print("\n🏷️  Testing inventory in Answer Mode...")
        print("📍 Place RFID tags near reader and press Enter...")
        input()  # Wait for user to place tags
        
        print("🔍 Sending inventory command...")
        tags = list(reader.inventory_answer_mode())
        
        if tags:
            print(f"✅ Found {len(tags)} tags:")
            for i, tag in enumerate(tags):
                tag_hex = ' '.join([f'{b:02X}' for b in tag])
                print(f"   Tag {i+1}: {tag_hex}")
        else:
            print("❌ No tags found")
            print("🔧 Try:")
            print("   1. Place tags closer to antenna")
            print("   2. Check if reader is in Answer Mode")
            print("   3. Try different tag types")
        
        # Test multiple scans
        print("\n🔄 Testing multiple scans (5 times)...")
        for scan in range(5):
            print(f"   Scan {scan+1}/5...")
            tags = list(reader.inventory_answer_mode())
            print(f"      Found {len(tags)} tags")
            time.sleep(1)
        
        reader.close()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_answer_mode()