from typing import Iterator
import serial
import serial.tools.list_ports
from datetime import datetime

from response import hex_readable, Response, WorkMode, InventoryWorkMode, InventoryMemoryBank
from transport import SerialTransport, TcpTransport
from reader import Reader

# Auto-detect COM port (Windows compatible)
available_port = None
print("Scanning for RFID reader...")
for port_info in serial.tools.list_ports.comports():
    if "CH340" in port_info.description or "1A86:7523" in port_info.hwid:
        print(f"Found CH340 device on {port_info.device}")
        try:
            test_serial = serial.Serial(port_info.device, 57600, timeout=0.1)
            test_serial.close()
            available_port = port_info.device
            break
        except:
            continue

if not available_port:
    available_port = 'COM5'  # Fallback

print(f"Using COM port: {available_port}")
transport = SerialTransport(available_port, 57600)
reader = Reader(transport)

#########################################################

print("🚀 RFID Reader in Active Mode - Continuous Scanning")
print("📡 Place RFID tags near the reader antenna")
print("⏹️  Press Ctrl+C to stop\n")

# Active Mode - Reader continuously sends tag data
try:
    tag_count = 0
    seen_tags = set()
    
    responses: Iterator[Response] = reader.inventory_active_mode()
    for response in responses:
        tag: bytes = response.data
        
        if len(tag) > 0:
            tag_hex = hex_readable(tag)
            
            # Only show new unique tags to avoid spam
            if tag_hex not in seen_tags:
                tag_count += 1
                seen_tags.add(tag_hex)
                
                print("=" * 50)
                print(f"📱 NEW RFID TAG #{tag_count}")
                print(f"🕒 Time: {datetime.now().strftime('%H:%M:%S')}")
                print(f"🔖 EPC: {tag_hex}")
                print(f"📊 Length: {len(tag)} bytes")
                print("=" * 50)
            
        # Show status if not success
        elif response.status != 0:
            print(f"Reader status: 0x{response.status:02X}")
            
except KeyboardInterrupt:
    print("\n🛑 Stopped by user")
except Exception as e:
    print(f"Error: {e}")
finally:
    reader.close()
    print("Connection closed")