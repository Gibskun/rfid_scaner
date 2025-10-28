#!/usr/bin/env python3
"""
Direct RFID Test - Skip frame parsing and read raw data
"""

from transport import SerialTransport
import time

def raw_inventory_test():
    print("🔍 Raw RFID Inventory Test")
    print("=" * 40)
    
    try:
        transport = SerialTransport("COM5", 57600, timeout=2)
        
        print("📤 Sending inventory command...")
        # Send inventory command: 04 FF 01 1B B4
        command = bytes([0x04, 0xFF, 0x01, 0x1B, 0xB4])
        transport.write_bytes(command)
        
        print("📥 Reading raw response...")
        # Read all available data
        all_data = b''
        for i in range(20):  # Try to read up to 20 bytes
            chunk = transport.read_bytes(1)
            if chunk:
                all_data += chunk
                print(f"   Byte {i+1}: 0x{chunk[0]:02X}")
            else:
                print(f"   Byte {i+1}: timeout")
                break
        
        print(f"\n📋 Complete response:")
        print(f"   Length: {len(all_data)} bytes")
        print(f"   Hex: {' '.join([f'{b:02X}' for b in all_data])}")
        
        # Try to find the real frame
        print(f"\n🔍 Looking for valid frames:")
        for i in range(len(all_data)):
            if i < len(all_data) - 4:  # Need at least 5 bytes for a frame
                potential_length = all_data[i]
                if 5 <= potential_length <= 50:  # Reasonable frame size
                    if i + potential_length <= len(all_data):
                        frame = all_data[i:i+potential_length]
                        print(f"   Possible frame at byte {i}: length={potential_length}")
                        print(f"      Data: {' '.join([f'{b:02X}' for b in frame])}")
                        
                        # Parse as response
                        if len(frame) >= 4:
                            print(f"      Reader addr: 0x{frame[1]:02X}")
                            print(f"      Command: 0x{frame[2]:02X}")
                            print(f"      Status: 0x{frame[3]:02X}")
                            if len(frame) > 4:
                                data_part = frame[4:-2] if len(frame) > 6 else frame[4:]
                                print(f"      Data: {' '.join([f'{b:02X}' for b in data_part])}")
        
        transport.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    raw_inventory_test()