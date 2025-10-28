#!/usr/bin/env python3
"""
RFID Reader Response Analyzer
Analyze the actual response format to understand the protocol
"""

from transport import SerialTransport
from reader import Reader
import time

def analyze_response():
    """Analyze the actual response from the reader"""
    print("🔍 RFID Reader Response Analysis")
    print("=" * 50)
    
    try:
        # Connect to COM5
        print("📡 Connecting to COM5...")
        transport = SerialTransport("COM5", 57600, timeout=2)
        
        # Send work mode query and analyze raw response
        print("📤 Sending work mode query...")
        command_bytes = bytes([0x04, 0xFF, 0x36, 0x27, 0xF1])
        transport.write_bytes(command_bytes)
        
        # Read raw response
        print("📥 Reading response...")
        raw_response = transport.read_frame()
        
        if raw_response:
            print(f"📋 Raw response ({len(raw_response)} bytes):")
            print(f"    Hex: {' '.join([f'{b:02X}' for b in raw_response])}")
            print(f"    Bytes: {list(raw_response)}")
            
            # Analyze structure
            print("\n🔍 Analysis:")
            if len(raw_response) > 0:
                print(f"    Length byte: 0x{raw_response[0]:02X} ({raw_response[0]})")
            if len(raw_response) > 1:
                print(f"    Reader addr: 0x{raw_response[1]:02X}")
            if len(raw_response) > 2:
                print(f"    Command:     0x{raw_response[2]:02X}")
            if len(raw_response) > 3:
                print(f"    Status:      0x{raw_response[3]:02X}")
            
            # Try different data/checksum splits
            length = raw_response[0]
            print(f"\n🧪 Trying different interpretations (length={length}):")
            
            for i in range(max(1, len(raw_response)-3), len(raw_response)):
                data_part = raw_response[4:i]
                checksum_part = raw_response[i:]
                print(f"    Split at {i}: data={len(data_part)} bytes, checksum={len(checksum_part)} bytes")
                print(f"        Data: {' '.join([f'{b:02X}' for b in data_part])}")
                print(f"        Checksum: {' '.join([f'{b:02X}' for b in checksum_part])}")
                
                # Test different checksum calculations
                if len(checksum_part) == 2:
                    data_for_checksum = raw_response[0:i]
                    
                    # Simple sum
                    sum_checksum = sum(data_for_checksum) & 0xFFFF
                    sum_lsb = sum_checksum & 0xFF
                    sum_msb = (sum_checksum >> 8) & 0xFF
                    print(f"        Sum checksum: {sum_lsb:02X} {sum_msb:02X}")
                    
                    # XOR checksum
                    xor_checksum = 0
                    for b in data_for_checksum:
                        xor_checksum ^= b
                    print(f"        XOR checksum: {xor_checksum:02X}")
                    
                    # Two's complement
                    twos_comp = (256 - (sum(data_for_checksum) & 0xFF)) & 0xFF
                    print(f"        2's comp: {twos_comp:02X}")
        
        transport.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_response()