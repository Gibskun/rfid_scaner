#!/usr/bin/env python3
"""
RFID Reader Test Script
Simple test to verify communication with the RFID reader

Based on the log file, the reader is communicating on COM5 at 57600 baud
and is configured for Active Mode operation.
"""

import time
import serial
import serial.tools.list_ports
from datetime import datetime

from response import hex_readable, Response, WorkMode, InventoryWorkMode
from transport import SerialTransport
from reader import Reader

def test_serial_connection():
    """Test basic serial connection to the RFID reader"""
    print("🧪 Testing RFID Reader Connection")
    print("=" * 50)
    
    # Test COM5 (from log file)
    try:
        print("📡 Testing COM5 at 57600 baud...")
        transport = SerialTransport("COM5", 57600, timeout=2)
        reader = Reader(transport)
        
        print("✅ Serial connection established!")
        
        # Test getting work mode (basic command)
        print("🔧 Testing work mode query...")
        work_mode = reader.work_mode()
        print(f"📋 Current work mode: {work_mode}")
        
        # Test inventory in active mode 
        print("🏷️  Testing active mode scanning (5 seconds)...")
        start_time = time.time()
        response_count = 0
        
        responses = reader.inventory_active_mode()
        
        for response in responses:
            response_count += 1
            print(f"📡 Response #{response_count}: status=0x{response.status:02X}, data_len={len(response.data)}")
            
            if response.data:
                print(f"📋 Data: {hex_readable(response.data)}")
            
            # Run for 5 seconds
            if time.time() - start_time > 5:
                break
        
        print(f"✅ Received {response_count} responses in 5 seconds")
        
        reader.close()
        print("🔌 Connection closed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_other_ports():
    """Test other common COM ports"""
    print("\n🔍 Scanning for RFID reader on other ports...")
    
    for port_info in serial.tools.list_ports.comports():
        print(f"📍 Found: {port_info.device} - {port_info.description}")
        
        if port_info.device != "COM5":  # Already tested COM5
            try:
                print(f"🧪 Testing {port_info.device}...")
                test_serial = serial.Serial(port_info.device, 57600, timeout=1)
                test_serial.close()
                print(f"✅ {port_info.device} is accessible")
                
                # Try connecting with our reader
                transport = SerialTransport(port_info.device, 57600, timeout=1)
                reader = Reader(transport)
                
                # Quick test - try to get work mode
                work_mode = reader.work_mode()
                print(f"🎯 {port_info.device} responds as RFID reader!")
                print(f"📋 Work mode: {work_mode}")
                
                reader.close()
                return port_info.device
                
            except Exception as e:
                print(f"❌ {port_info.device} failed: {e}")
                continue
    
    return None

def main():
    """Main test function"""
    print("🚀 RFID Reader System Test")
    print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Test primary port (COM5 from logs)
    if test_serial_connection():
        print("\n✅ Primary test passed! Reader is working on COM5.")
    else:
        print("\n❌ Primary test failed. Trying other ports...")
        
        # Test other ports
        working_port = test_other_ports()
        
        if working_port:
            print(f"\n✅ Found working RFID reader on {working_port}")
        else:
            print("\n❌ No working RFID reader found.")
            print("🔧 Troubleshooting:")
            print("   1. Check reader power")
            print("   2. Check USB cable connection") 
            print("   3. Verify reader is in Active Mode")
            print("   4. Install CH340 drivers if needed")

if __name__ == "__main__":
    main()