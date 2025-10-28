#!/usr/bin/env python3
"""
RFID Reader - Final Working Version
Handles Answer Mode operation with proper error handling
"""

from transport import SerialTransport
from reader import Reader
from response import Response, WorkMode, InventoryWorkMode
import time

def main():
    print("🚀 RFID Reader - Final Working Version")
    print("📅 Answer Mode Operation")
    print("=" * 50)
    
    try:
        # Connect to COM5 
        print("📡 Connecting to RFID reader on COM5...")
        transport = SerialTransport("COM5", 57600, timeout=3)
        reader = Reader(transport)
        
        # Get work mode to confirm configuration
        print("🔧 Checking reader configuration...")
        work_mode = reader.work_mode()
        print(f"✅ Work Mode: {work_mode.inventory_work_mode.name}")
        print(f"   Protocol: {work_mode.work_mode_state.protocol.name}")
        print(f"   Buzzer: {'Enabled' if work_mode.work_mode_state.beep else 'Disabled'}")
        
        if work_mode.inventory_work_mode != InventoryWorkMode.ANSWER_MODE:
            print("⚠️  Reader is not in Answer Mode!")
            print("   Please configure reader to Answer Mode using the built-in app")
        
        print("\n🏷️  Starting inventory scanning...")
        print("   Place RFID tags near the antenna")
        print("   Press Ctrl+C to stop")
        print()
        
        scan_count = 0
        total_tags_found = 0
        
        while True:
            try:
                scan_count += 1
                print(f"🔍 Scan #{scan_count}...")
                
                # Perform inventory
                tags = list(reader.inventory_answer_mode())
                
                if tags:
                    print(f"✅ Found {len(tags)} tag(s):")
                    total_tags_found += len(tags)
                    
                    for i, tag in enumerate(tags, 1):
                        tag_hex = ' '.join([f'{b:02X}' for b in tag])
                        print(f"   Tag {i}: {tag_hex}")
                        
                        # Try to format as EPC
                        if len(tag) >= 12:
                            epc_str = ''.join([f'{b:02X}' for b in tag])
                            print(f"           EPC: {epc_str}")
                
                else:
                    print("   No tags found")
                
                # Wait before next scan
                time.sleep(2)
                
            except KeyboardInterrupt:
                break
                
            except Exception as e:
                print(f"⚠️  Scan error: {e}")
                time.sleep(1)
                continue
    
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("🔧 Troubleshooting:")
        print("   1. Check reader power and USB connection")
        print("   2. Ensure reader is configured in Answer Mode") 
        print("   3. Verify COM5 is the correct port")
        print("   4. Close other programs using the COM port")
        
    finally:
        try:
            if 'reader' in locals():
                reader.close()
                print("🔌 Connection closed")
        except:
            pass
        
        if 'total_tags_found' in locals():
            print(f"📊 Session summary: {scan_count} scans, {total_tags_found} total tags detected")

if __name__ == "__main__":
    main()