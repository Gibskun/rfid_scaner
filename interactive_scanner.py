#!/usr/bin/env python3
"""
RFID Interactive Scanner with Auto-Write Prompting
Detects tags and prompts user to write/register new tags not in database
"""

from transport import SerialTransport
from reader import Reader
from database import get_database
import time
from datetime import datetime
import threading
import queue

class InteractiveRFIDScanner:
    """Interactive scanner that prompts to write new tags"""
    
    def __init__(self, port: str = "COM5", baud_rate: int = 57600):
        self.port = port
        self.baud_rate = baud_rate
        self.reader = None
        self.transport = None
        self.connected = False
        
        # Database connection
        try:
            self.db = get_database()
            print("✅ Database connected successfully")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            self.db = None
        
        # Track tags
        self.detected_tags = {}  # tag_hex -> {data, last_seen, prompted}
        self.pending_write_queue = queue.Queue()
        
        # Scanning control
        self.scanning = True
        self.paused = False
    
    def connect(self) -> bool:
        """Connect to RFID reader"""
        try:
            print(f"🔌 Connecting to RFID reader on {self.port}...")
            self.transport = SerialTransport(self.port, self.baud_rate, timeout=1)
            self.reader = Reader(self.transport)
            
            # Verify connection
            work_mode = self.reader.work_mode()
            print(f"✅ Connected! Mode: {work_mode.inventory_work_mode.name}")
            
            # Set maximum power
            self.reader.set_power(30)
            print("⚡ Set reader power to maximum")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            return False
    
    def check_tag_in_database(self, tag_hex: str) -> bool:
        """Check if tag exists in database"""
        if not self.db:
            return False
        
        try:
            tag_info = self.db.get_tag_info(tag_hex)
            return tag_info is not None
        except:
            return False
    
    def log_unregistered_tag(self, tag_hex: str, tag_data: bytes):
        """Log unregistered tag detection (write functionality removed)"""
        print("\n" + "=" * 70)
        print("🏷️  UNREGISTERED TAG DETECTED!")
        print("=" * 70)
        print(f"📌 Tag ID: {tag_hex}")
        print(f"📊 Length: {len(tag_data)} bytes")
        print("\n⚠️  This tag is NOT in the database.")
        print("📝 Note: Write functionality has been removed from this system.")
        print("=" * 70)
        return False
    

    
    def scan_loop(self):
        """Main scanning loop"""
        print("\n🚀 Interactive RFID Scanner (Read-Only Mode)")
        print("=" * 70)
        print("📡 Scanning for tags...")
        print("🏷️  New unregistered tags will be logged")
        print("💾 Database tracks tag detections")
        print("⚠️  Note: Write functionality has been removed")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 70)
        
        try:
            while self.scanning:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Scan for tags
                tags = list(self.reader.inventory_answer_mode())
                
                if tags:
                    current_time = datetime.now()
                    
                    for tag in tags:
                        if not tag:
                            continue
                        
                        tag_hex = ' '.join([f'{b:02X}' for b in tag])
                        
                        # Check if we've seen this tag recently
                        if tag_hex in self.detected_tags:
                            # Update last seen
                            self.detected_tags[tag_hex]['last_seen'] = current_time
                            continue
                        
                        # New tag detected
                        self.detected_tags[tag_hex] = {
                            'data': tag,
                            'last_seen': current_time,
                            'prompted': False
                        }
                        
                        print(f"\n📍 Tag detected: {tag_hex[:30]}...")
                        
                        # Check if in database
                        in_database = self.check_tag_in_database(tag_hex)
                        
                        if in_database:
                            # Tag is already registered
                            print("   ✅ Tag is in database")
                            if self.db:
                                try:
                                    tag_info = self.db.get_tag_info(tag_hex)
                                    if tag_info and tag_info.get('item_name'):
                                        print(f"   📦 Item: {tag_info['item_name']}")
                                except:
                                    pass
                        else:
                            # Tag NOT in database - just log it
                            if not self.detected_tags[tag_hex]['prompted']:
                                self.detected_tags[tag_hex]['prompted'] = True
                                self.log_unregistered_tag(tag_hex, tag)
                
                # Clean up old tags (not seen for 10 seconds)
                cutoff_time = datetime.now()
                to_remove = []
                for tag_id, info in self.detected_tags.items():
                    if (cutoff_time - info['last_seen']).total_seconds() > 10:
                        to_remove.append(tag_id)
                
                for tag_id in to_remove:
                    del self.detected_tags[tag_id]
                
                # Short delay
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Scanning stopped by user")
        finally:
            self.scanning = False
    
    def run(self):
        """Main entry point"""
        if not self.connect():
            print("❌ Failed to connect to reader")
            return
        
        try:
            self.scan_loop()
        finally:
            if self.reader:
                self.reader.close()
                print("🔌 Disconnected from reader")

def main():
    """Main function"""
    print("🏷️  RFID Interactive Scanner with Auto-Registration")
    print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    print("💾 Database: PostgreSQL (localhost:5432/rfid_system)")
    print("📡 Default Port: COM5")
    print("=" * 70)
    
    # Get port from user
    port = input("\nEnter COM port (default: COM5): ").strip() or "COM5"
    
    scanner = InteractiveRFIDScanner(port=port)
    scanner.run()

if __name__ == "__main__":
    main()
