#!/usr/bin/env python3
"""
Manual Response Parser
Manually parse the inventory response to understand the format
"""

def parse_inventory_response():
    print("🔍 Manual Inventory Response Analysis")
    print("=" * 50)
    
    # What we received: 67 0B 00 01 01 01 04 00 00 00 02 84 95
    response = [0x67, 0x0B, 0x00, 0x01, 0x01, 0x01, 0x04, 0x00, 0x00, 0x00, 0x02, 0x84, 0x95]
    
    print(f"Raw response: {' '.join([f'{b:02X}' for b in response])}")
    print()
    
    # Try different interpretations
    print("🧪 Interpretation 1: First byte is noise")
    actual_response = response[1:]  # Skip first byte
    print(f"   Data: {' '.join([f'{b:02X}' for b in actual_response])}")
    
    if len(actual_response) >= 1:
        print(f"   Length: 0x{actual_response[0]:02X} ({actual_response[0]})")
    if len(actual_response) >= 4:
        print(f"   Possible frame: [{actual_response[0]:02X}] [{actual_response[1]:02X}] [{actual_response[2]:02X}] [{actual_response[3]:02X}] + data")
    
    print("\n🧪 Interpretation 2: Standard protocol")
    if len(response) >= 4:
        print(f"   Length: 0x{response[0]:02X} ({response[0]})")
        print(f"   Reader addr: 0x{response[1]:02X}")
        print(f"   Command: 0x{response[2]:02X}")
        print(f"   Status: 0x{response[3]:02X}")
    
    print("\n🧪 Interpretation 3: 0x0B as length")
    if response[1] == 0x0B:  # Length = 11
        expected_frame = response[1:1+11+2]  # Length + data + checksum
        print(f"   Expected frame length: {response[1]} bytes + 2 checksum = {response[1]+2}")
        print(f"   Available data: {len(response)-1} bytes")
        if len(response) >= response[1] + 2:
            print(f"   Complete frame: {' '.join([f'{b:02X}' for b in expected_frame])}")
            
            # Parse as standard response
            length = expected_frame[0]
            reader_addr = expected_frame[1]
            command = expected_frame[2]  
            status = expected_frame[3]
            data = expected_frame[4:length-2]
            checksum = expected_frame[length-2:length]
            
            print(f"   Length: {length}")
            print(f"   Reader addr: 0x{reader_addr:02X}")
            print(f"   Command: 0x{command:02X}")
            print(f"   Status: 0x{status:02X}")
            print(f"   Data: {' '.join([f'{b:02X}' for b in data])}")
            print(f"   Checksum: {' '.join([f'{b:02X}' for b in checksum])}")
            
            # Parse inventory data
            if len(data) > 0:
                print(f"\n📋 Inventory data analysis:")
                print(f"   Tag count: {data[0]}")
                if data[0] > 0 and len(data) > 1:
                    pointer = 1
                    for i in range(data[0]):
                        if pointer < len(data):
                            tag_len = data[pointer]
                            print(f"   Tag {i+1}: length={tag_len}")
                            if pointer + 1 + tag_len <= len(data):
                                tag_data = data[pointer+1:pointer+1+tag_len]
                                print(f"           data={' '.join([f'{b:02X}' for b in tag_data])}")
                                pointer += 1 + tag_len
                            else:
                                print(f"           data=incomplete")
                                break

if __name__ == "__main__":
    parse_inventory_response()