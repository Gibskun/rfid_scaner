#!/usr/bin/env python3
"""
RFID Reader - Robust Active Mode Scanner
Improved version with enhanced error recovery and logging

This version includes:
- Better error handling and recovery
- Detailed logging and debugging
- Automatic reconnection on communication failures
- Improved tag tracking and display
"""

from typing import Iterator, Set, Dict
import time
import serial
import serial.tools.list_ports
from datetime import datetime
import traceback

from response import hex_readable, Response, WorkMode, InventoryWorkMode
from transport import SerialTransport
from reader import Reader

class RFIDScanner:
    def __init__(self, port: str = "COM5", baud_rate: int = 57600):
        self.port = port
        self.baud_rate = baud_rate
        self.reader = None
        self.transport = None
        self.connected = False
        
        # Tag tracking
        self.seen_tags: Set[str] = set()
        self.tag_count = 0
        self.tag_timers: Dict[str, datetime] = {}
        
        # Error tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 20
        self.total_responses = 0
        
    def connect(self) -> bool:
        """Connect to the RFID reader"""
        try:
            print(f"🔌 Connecting to RFID reader on {self.port} at {self.baud_rate} baud...")
            
            # Create transport and reader
            self.transport = SerialTransport(self.port, self.baud_rate, timeout=2)
            self.reader = Reader(self.transport)
            
            # Test connection by getting work mode
            print("🔧 Testing connection with work mode query...")
            work_mode = self.reader.work_mode()
            print(f"✅ Connected! Work Mode: {work_mode}")
            
            self.connected = True
            self.consecutive_errors = 0
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.cleanup()
            return False
    
    def cleanup(self):
        """Clean up connection resources"""
        try:
            if self.reader:
                self.reader.close()
                self.reader = None
            self.transport = None
            self.connected = False
        except:
            pass
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to the reader"""
        print("🔄 Attempting to reconnect...")
        self.cleanup()
        time.sleep(2)  # Wait before reconnecting
        return self.connect()
    
    def process_response(self, response: Response) -> bool:
        """Process a single response from the reader"""
        try:
            self.total_responses += 1
            self.consecutive_errors = 0  # Reset error counter on successful response
            
            # Get tag data from response
            tag_data: bytes = response.data
            current_time = datetime.now()
            
            if len(tag_data) > 0:
                # Create unique identifier for tag
                tag_id = hex_readable(tag_data)
                
                print(f"📡 Response #{self.total_responses}: status=0x{response.status:02X}, tag_id={tag_id}")
                
                # Check if this is a new tag or repeated detection
                if tag_id not in self.seen_tags:
                    # New tag detected
                    self.tag_count += 1
                    self.seen_tags.add(tag_id)
                    self.tag_timers[tag_id] = current_time
                    
                    self.display_new_tag(tag_data, tag_id, current_time)
                    
                else:
                    # Tag still in range - update quietly every 10 seconds
                    if tag_id in self.tag_timers:
                        duration = (current_time - self.tag_timers[tag_id]).total_seconds()
                        if int(duration) % 10 == 0 and duration > 5:  # Print update every 10 seconds after 5s
                            print(f"📍 Tag still in range: {tag_id[:16]}... ({duration:.0f}s)")
            
            else:
                # No tag data in response - might be status or empty response
                if response.status != 0:
                    print(f"⚠️  Reader status: 0x{response.status:02X}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error processing response: {e}")
            self.consecutive_errors += 1
            return False
    
    def display_new_tag(self, tag_data: bytes, tag_id: str, detection_time: datetime):
        """Display information about a newly detected tag"""
        print("=" * 60)
        print(f"🏷️  NEW RFID TAG DETECTED #{self.tag_count}")
        print(f"🕒 Time: {detection_time.strftime('%H:%M:%S.%f')[:-3]}")
        print(f"📊 Data Length: {len(tag_data)} bytes")
        print(f"🔖 Tag ID: {tag_id}")
        
        # Try to format as different EPC types
        if len(tag_data) >= 12:
            hex_str = ''.join([f'{b:02X}' for b in tag_data])
            print(f"🔖 EPC-96: {hex_str}")
        
        print("=" * 60)
    
    def scan_active_mode(self, duration: int = None):
        """Scan for RFID tags in active mode"""
        if not self.connected:
            print("❌ Not connected to reader!")
            return
        
        print("📡 Starting active mode scanning...")
        print("🏷️  Place RFID tags near the reader antenna")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        start_time = time.time()
        last_status_time = start_time
        
        try:
            responses: Iterator[Response] = self.reader.inventory_active_mode()
            
            for response in responses:
                # Process the response
                self.process_response(response)
                
                # Check for too many consecutive errors
                if self.consecutive_errors >= self.max_consecutive_errors:
                    print(f"❌ Too many consecutive errors ({self.consecutive_errors})")
                    if not self.reconnect():
                        break
                    responses = self.reader.inventory_active_mode()
                    continue
                
                # Print status every 30 seconds
                current_time = time.time()
                if current_time - last_status_time > 30:
                    elapsed = current_time - start_time
                    print(f"📊 Status: {self.total_responses} responses, {len(self.seen_tags)} unique tags, {elapsed:.0f}s elapsed")
                    last_status_time = current_time
                
                # Check duration limit
                if duration and (current_time - start_time) > duration:
                    print(f"⏰ Duration limit reached ({duration}s)")
                    break
                
                # Small delay to prevent overwhelming
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        
        except Exception as e:
            print(f"❌ Scanning error: {e}")
            print("🔍 Traceback:")
            traceback.print_exc()
    
    def get_status(self):
        """Get current scanner status"""
        elapsed = time.time() - (getattr(self, 'start_time', time.time()))
        return {
            'connected': self.connected,
            'total_responses': self.total_responses,
            'unique_tags': len(self.seen_tags),
            'consecutive_errors': self.consecutive_errors,
            'elapsed_time': elapsed
        }

def find_rfid_ports():
    """Find potential RFID reader ports"""
    print("🔍 Scanning for RFID reader ports...")
    
    potential_ports = []
    
    # Check all available COM ports
    for port_info in serial.tools.list_ports.comports():
        print(f"📍 Found: {port_info.device} - {port_info.description}")
        
        # Check for CH340 devices (common for RFID readers)
        if "CH340" in port_info.description or "1A86:7523" in port_info.hwid:
            print(f"🎯 CH340 device detected: {port_info.device}")
            potential_ports.insert(0, port_info.device)  # Prioritize CH340 devices
        else:
            potential_ports.append(port_info.device)
    
    # Add common ports if not found
    common_ports = ['COM5', 'COM4', 'COM3', 'COM6', 'COM7', 'COM8']
    for port in common_ports:
        if port not in potential_ports:
            potential_ports.append(port)
    
    return potential_ports

def main():
    """Main application"""
    print("🚀 RFID Reader - Enhanced Active Mode Scanner")
    print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Find potential ports
    ports = find_rfid_ports()
    
    scanner = None
    
    # Try to connect to each port
    for port in ports:
        print(f"\n🧪 Testing {port}...")
        scanner = RFIDScanner(port)
        
        if scanner.connect():
            print(f"✅ Successfully connected to {port}")
            break
        else:
            print(f"❌ Failed to connect to {port}")
    
    if not scanner or not scanner.connected:
        print("\n❌ No RFID reader found!")
        print("🔧 Troubleshooting:")
        print("   1. Check USB cable connection")
        print("   2. Ensure reader is powered on")
        print("   3. Install CH340 USB driver if needed")
        print("   4. Verify reader is in Active Mode")
        print("   5. Check if other software is using the COM port")
        return
    
    try:
        # Start scanning
        scanner.scan_active_mode()
        
    finally:
        # Cleanup
        if scanner:
            status = scanner.get_status()
            print(f"\n📊 Final Status:")
            print(f"   Total Responses: {status['total_responses']}")
            print(f"   Unique Tags: {status['unique_tags']}")
            print(f"   Errors: {status['consecutive_errors']}")
            print(f"   Runtime: {status['elapsed_time']:.1f}s")
            
            scanner.cleanup()
            print("🔌 Connection closed")

if __name__ == "__main__":
    main()