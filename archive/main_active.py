#!/usr/bin/env python3
"""
RFID Reader - Active Mode Continuous Scanner
Optimized for HW-VX6330K in Active Mode

The reader is configured to Active Mode, which means:
- Tags are detected automatically without sending commands
- Reader continuously sends tag data when tags are in range
- No need to send inventory commands
"""

from typing import Iterator, Set
import time
import serial
import serial.tools.list_ports
from datetime import datetime

from response import hex_readable, Response, WorkMode, InventoryWorkMode, InventoryMemoryBank
from transport import SerialTransport, TcpTransport
from reader import Reader

def find_rfid_reader_port():
    """Find and connect to RFID reader COM port"""
    print("🔍 Scanning for RFID reader...")
    
    # Look for CH340 USB-Serial devices (common for RFID readers)
    for port_info in serial.tools.list_ports.comports():
        if "CH340" in port_info.description or "1A86:7523" in port_info.hwid:
            print(f"📡 Found CH340 device on {port_info.device}")
            try:
                # Test connection
                test_serial = serial.Serial(port_info.device, 57600, timeout=0.5)
                test_serial.close()
                print(f"✅ Successfully tested {port_info.device}")
                return port_info.device
            except Exception as e:
                print(f"❌ Cannot use {port_info.device}: {e}")
    
    # Fallback to common Windows COM ports
    common_ports = ['COM5', 'COM4', 'COM3', 'COM6', 'COM7', 'COM8']
    for port in common_ports:
        try:
            test_serial = serial.Serial(port, 57600, timeout=0.5)
            test_serial.close()
            print(f"✅ Found working COM port: {port}")
            return port
        except:
            continue
    
    return None

def format_epc_readable(epc_bytes):
    """Format EPC bytes into readable format"""
    if not epc_bytes or len(epc_bytes) == 0:
        return "No EPC data"
    
    # Convert to hex string
    hex_str = hex_readable(epc_bytes)
    
    # Try to identify EPC structure (this is a basic example)
    if len(epc_bytes) >= 12:  # Standard 96-bit EPC
        # EPC-96 structure: Header(8) + Filter(3) + Partition(3) + Company(20-40) + Item(24-4) + Check(12)
        epc_hex = ''.join([f'{b:02X}' for b in epc_bytes])
        return f"EPC-96: {hex_str}\n       Full: {epc_hex}"
    else:
        return f"EPC: {hex_str}"

def display_tag_info(tag_data, tag_count, first_seen_time):
    """Display formatted tag information"""
    current_time = datetime.now()
    duration = (current_time - first_seen_time).total_seconds()
    
    print("=" * 60)
    print(f"📱 RFID TAG DETECTED #{tag_count}")
    print(f"🕒 Time: {current_time.strftime('%H:%M:%S')}")
    print(f"⏱️  Duration in range: {duration:.1f}s")
    print(f"📊 Data Length: {len(tag_data)} bytes")
    print(f"🔖 {format_epc_readable(tag_data)}")
    print("=" * 60)

def main():
    """Main application for Active Mode RFID scanning"""
    print("🚀 RFID Reader - Active Mode Scanner")
    print("📖 Reader configured in Active Mode - continuous scanning")
    print("=" * 60)
    
    # Find and connect to RFID reader
    com_port = find_rfid_reader_port()
    if not com_port:
        print("❌ No RFID reader found!")
        print("🔧 Troubleshooting:")
        print("   1. Check USB cable connection")
        print("   2. Ensure reader is powered on")
        print("   3. Install CH340 USB driver if needed")
        print("   4. Close other programs using COM ports")
        return

    reader = None
    try:
        # Connect to reader
        print(f"🔌 Connecting to RFID reader on {com_port}...")
        transport = SerialTransport(com_port, 57600)
        reader = Reader(transport)
        
        print("✅ Connected successfully!")
        print("📡 Reader is in Active Mode - waiting for RFID tags...")
        print("🏷️  Place RFID tags near the reader antenna")
        print("⏹️  Press Ctrl+C to stop\n")
        
        # Active Mode - Continuous scanning
        seen_tags: Set[str] = set()  # Track unique tags
        tag_count = 0
        tag_timers = {}  # Track when tags were first seen
        
        responses: Iterator[Response] = reader.inventory_active_mode()
        
        for response in responses:
            try:
                # Get tag data from response
                tag_data: bytes = response.data
                
                if len(tag_data) > 0:
                    # Create unique identifier for tag
                    tag_id = hex_readable(tag_data)
                    current_time = datetime.now()
                    
                    # Check if this is a new tag or repeated detection
                    if tag_id not in seen_tags:
                        # New tag detected
                        tag_count += 1
                        seen_tags.add(tag_id)
                        tag_timers[tag_id] = current_time
                        
                        display_tag_info(tag_data, tag_count, current_time)
                        
                    else:
                        # Tag still in range - update quietly every 5 seconds
                        if tag_id in tag_timers:
                            duration = (current_time - tag_timers[tag_id]).total_seconds()
                            if duration % 5.0 < 0.5:  # Print update every ~5 seconds
                                print(f"📍 Tag still in range: {tag_id[:20]}... ({duration:.0f}s)")
                
                else:
                    # No tag data in response - might be status or empty response
                    if response.status != 0:
                        print(f"⚠️  Reader status: 0x{response.status:02X}")
                        
            except Exception as e:
                print(f"⚠️  Error processing response: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Check:")
        print("   1. Reader power and connection")
        print("   2. COM port availability") 
        print("   3. Reader work mode (should be Active)")
        
    finally:
        try:
            if reader:
                reader.close()
                print("🔌 Connection closed")
        except:
            pass

if __name__ == "__main__":
    main()