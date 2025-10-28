#!/usr/bin/env python3
"""
RFID Reader - Active Mode (Fixed Version)
Based on log analysis showing tag: 000000000000000000000004
"""

from typing import Iterator
import serial
import serial.tools.list_ports
from datetime import datetime
import time

from response import hex_readable, Response
from transport import SerialTransport
from reader import Reader

def find_com_port():
    """Find RFID reader COM port"""
    # First try CH340 devices
    for port_info in serial.tools.list_ports.comports():
        if "CH340" in port_info.description or "1A86:7523" in port_info.hwid:
            try:
                test_serial = serial.Serial(port_info.device, 57600, timeout=0.1)
                test_serial.close()
                return port_info.device
            except:
                continue
    
    # Fallback to COM5 (from your log)
    try:
        test_serial = serial.Serial('COM5', 57600, timeout=0.1)
        test_serial.close()
        return 'COM5'
    except:
        pass
    
    return None

def main():
    """Main RFID scanner"""
    print("🚀 RFID Active Mode Scanner (Fixed)")
    print("📋 Based on your log showing tag: 000000000000000000000004")
    print("=" * 60)
    
    # Find port
    port = find_com_port()
    if not port:
        print("❌ Cannot find RFID reader!")
        print("💡 Make sure reader is connected to COM5")
        return
    
    print(f"✅ Found RFID reader on {port}")
    
    try:
        # Connect with proper error handling
        transport = SerialTransport(port, 57600)
        reader = Reader(transport)
        
        print("📡 Connected successfully!")
        print("🔄 Active Mode - Reader will send tag data automatically")
        print("🏷️  Place RFID tag near the antenna")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        seen_tags = set()
        tag_counter = 0
        last_seen = {}
        
        # Start Active Mode scanning
        responses: Iterator[Response] = reader.inventory_active_mode()
        
        for response in responses:
            try:
                current_time = datetime.now()
                
                # Debug: Show all responses
                if hasattr(response, 'status'):
                    status_msg = f"Status: 0x{response.status:02X}"
                else:
                    status_msg = "No status"
                
                # Check for tag data
                if hasattr(response, 'data') and len(response.data) > 0:
                    # Process tag data
                    raw_hex = hex_readable(response.data)
                    
                    # Convert to format seen in your log (lowercase, no spaces)
                    tag_id = ''.join([f'{b:02X}' for b in response.data]).lower()
                    
                    # Check if this is a new tag
                    if tag_id not in seen_tags:
                        tag_counter += 1
                        seen_tags.add(tag_id)
                        last_seen[tag_id] = current_time
                        
                        print("🎯" + "=" * 50)
                        print(f"📱 RFID TAG DETECTED #{tag_counter}")
                        print(f"🕒 Time: {current_time.strftime('%H:%M:%S')}")
                        print(f"📊 Raw Data: {raw_hex}")
                        print(f"🔖 Tag ID: {tag_id}")
                        print(f"📏 Length: {len(response.data)} bytes")
                        
                        # Check if this matches your known tag
                        if tag_id == "000000000000000000000004":
                            print("✅ This is your logged tag!")
                        
                        print("🎯" + "=" * 50)
                    
                    else:
                        # Tag still present - just update timestamp quietly
                        if tag_id in last_seen:
                            duration = (current_time - last_seen[tag_id]).total_seconds()
                            if duration > 5:  # Update every 5 seconds
                                print(f"📍 Tag {tag_id[:8]}... still present ({duration:.0f}s)")
                                last_seen[tag_id] = current_time
                
                else:
                    # No tag data - this is normal in Active Mode
                    # Print a dot every 50 empty responses to show activity
                    if not hasattr(main, 'empty_count'):
                        main.empty_count = 0
                    main.empty_count += 1
                    
                    if main.empty_count % 50 == 0:
                        print(".", end="", flush=True)
                        if main.empty_count % 1000 == 0:
                            print(f" [{current_time.strftime('%H:%M:%S')}]")
            
            except Exception as e:
                print(f"⚠️  Error processing response: {e}")
                # Don't break, continue scanning
                continue
    
    except KeyboardInterrupt:
        print("\n🛑 Scanning stopped by user")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Troubleshooting:")
        print("   1. Check if another program is using COM5")
        print("   2. Verify reader power supply")
        print("   3. Make sure reader is in Active Mode")
        print("   4. Try moving tag closer to antenna")
        
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            reader.close()
            print("🔌 Connection closed")
        except:
            pass

if __name__ == "__main__":
    main()