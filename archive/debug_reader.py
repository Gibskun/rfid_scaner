#!/usr/bin/env python3
"""
RFID Reader Debug Tool - Active Mode
This will help diagnose why tags aren't showing up in the terminal
"""

from typing import Iterator
import serial
import serial.tools.list_ports
from datetime import datetime
import time

from response import hex_readable, Response
from transport import SerialTransport
from reader import Reader

def find_rfid_port():
    """Find RFID reader port"""
    print("🔍 Scanning for RFID reader...")
    
    for port_info in serial.tools.list_ports.comports():
        print(f"  Found: {port_info.device} - {port_info.description}")
        if "CH340" in port_info.description or "1A86:7523" in port_info.hwid:
            try:
                test_serial = serial.Serial(port_info.device, 57600, timeout=0.1)
                test_serial.close()
                print(f"✅ RFID reader found on {port_info.device}")
                return port_info.device
            except Exception as e:
                print(f"❌ Cannot use {port_info.device}: {e}")
    
    # Try common ports
    for port in ['COM5', 'COM4', 'COM3']:
        try:
            test_serial = serial.Serial(port, 57600, timeout=0.1)
            test_serial.close()
            print(f"✅ Found working port: {port}")
            return port
        except:
            pass
    
    return None

def debug_active_mode():
    """Debug Active Mode communication"""
    port = find_rfid_port()
    if not port:
        print("❌ No RFID reader found!")
        return
    
    print(f"\n🔌 Connecting to {port} at 57600 baud...")
    
    try:
        # Use raw serial connection first to see what's coming
        print("\n📡 RAW SERIAL DEBUG - First 30 seconds")
        print("=" * 60)
        
        ser = serial.Serial(port, 57600, timeout=1)
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < 30:  # 30 second window
            try:
                # Read any available data
                if ser.in_waiting > 0:
                    raw_data = ser.read(ser.in_waiting)
                    if raw_data:
                        data_received = True
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"[{timestamp}] Received {len(raw_data)} bytes:")
                        print(f"  Raw bytes: {[hex(b) for b in raw_data]}")
                        print(f"  Hex string: {' '.join([f'{b:02X}' for b in raw_data])}")
                        
                        # Try to parse as response
                        try:
                            if len(raw_data) >= 5:  # Minimum response length
                                response = Response(raw_data)
                                print(f"  ✅ Parsed as Response:")
                                print(f"     Status: 0x{response.status:02X}")
                                print(f"     Data length: {len(response.data)}")
                                if response.data:
                                    print(f"     Tag data: {hex_readable(response.data)}")
                                    # Convert to the format seen in log
                                    tag_str = ''.join([f'{b:02X}' for b in response.data]).lower().replace(' ', '')
                                    print(f"     Tag ID (log format): {tag_str}")
                        except Exception as e:
                            print(f"  ❌ Cannot parse as Response: {e}")
                        
                        print("-" * 40)
                
                time.sleep(0.1)  # Small delay
                
            except Exception as e:
                print(f"Error reading data: {e}")
                break
        
        ser.close()
        
        if not data_received:
            print("❌ No data received in 30 seconds!")
            print("💡 Try placing RFID tag closer to antenna")
            print("💡 Check if reader is in Active Mode")
            print("💡 Verify reader power supply")
        else:
            print("✅ Data was received and analyzed above")
        
        print("\n" + "=" * 60)
        print("🧪 TESTING WITH READER CLASS")
        print("=" * 60)
        
        # Now test with our Reader class
        transport = SerialTransport(port, 57600)
        reader = Reader(transport)
        
        print("📡 Starting Active Mode scan (10 seconds)...")
        print("🏷️  Place RFID tag near antenna now!")
        
        try:
            responses: Iterator[Response] = reader.inventory_active_mode()
            start_time = time.time()
            response_count = 0
            
            for response in responses:
                if time.time() - start_time > 10:  # 10 second test
                    break
                    
                response_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"\n[{timestamp}] Response #{response_count}:")
                print(f"  Status: 0x{response.status:02X}")
                print(f"  Data length: {len(response.data)} bytes")
                
                if len(response.data) > 0:
                    tag_hex = hex_readable(response.data)
                    tag_id = ''.join([f'{b:02X}' for b in response.data]).lower()
                    
                    print(f"  🎯 TAG FOUND!")
                    print(f"     Raw data: {tag_hex}")
                    print(f"     Tag ID: {tag_id}")
                    
                    if tag_id == "000000000000000000000004":
                        print(f"  ✅ This matches your log file tag!")
                else:
                    print(f"  ℹ️  Empty response (normal in Active Mode)")
        
        except Exception as e:
            print(f"❌ Error in Reader class: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            reader.close()
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 RFID Reader Debug Tool")
    print("📋 This will help diagnose Active Mode issues")
    print("🏷️  Have your RFID tag ready!")
    print()
    
    debug_active_mode()
    
    print("\n" + "=" * 60)
    print("🔧 TROUBLESHOOTING TIPS:")
    print("=" * 60)
    print("1. If no data received:")
    print("   - Check reader power supply")
    print("   - Verify USB connection")
    print("   - Try placing tag very close to antenna")
    print()
    print("2. If data received but not parsed:")
    print("   - Reader might be in wrong mode")
    print("   - Data format might be different")
    print()
    print("3. If Reader class fails:")
    print("   - Check timeout settings")
    print("   - Verify response parsing logic")