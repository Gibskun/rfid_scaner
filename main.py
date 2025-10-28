#!/usr/bin/env python3
"""
RFID Reader - Optimized Fast Scanner
Improved version with faster detection and better distance handling
"""

from transport import SerialTransport
from reader import Reader
from response import Response, WorkMode, InventoryWorkMode
import time
from typing import Dict, Set
from datetime import datetime

class FastRFIDScanner:
    def __init__(self, port: str = "COM5", baud_rate: int = 57600):
        self.port = port
        self.baud_rate = baud_rate
        self.reader = None
        self.transport = None
        self.connected = False
        
        # Tag tracking with signal strength estimation
        self.active_tags: Dict[str, dict] = {}  # tag_id -> {first_seen, last_seen, count, data}
        self.total_detections = 0
        
        # Performance settings
        self.fast_scan_interval = 0.1  # 100ms between scans for fast detection
        self.cleanup_interval = 5.0    # Remove tags not seen for 5 seconds
        self.max_scan_failures = 5     # Max consecutive failures before reconnect
        
    def connect(self) -> bool:
        """Connect to RFID reader with optimized settings"""
        try:
            print(f"🔌 Connecting to RFID reader on {self.port}...")
            
            # Use shorter timeout for faster scanning
            self.transport = SerialTransport(self.port, self.baud_rate, timeout=1)
            self.reader = Reader(self.transport)
            
            # Verify connection
            work_mode = self.reader.work_mode()
            print(f"✅ Connected! Mode: {work_mode.inventory_work_mode.name}")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def optimize_reader_settings(self):
        """Optimize reader for fast detection"""
        try:
            # Try to increase power for better range
            print("⚡ Optimizing reader settings...")
            
            # Set maximum power (0-30, where 30 is max)
            response = self.reader.set_power(30)
            if response.status == 0:
                print("   ✅ Set power to maximum (30)")
            else:
                print(f"   ⚠️  Power setting failed: status 0x{response.status:02X}")
                
        except Exception as e:
            print(f"   ⚠️  Optimization failed: {e}")
    
    def scan_tags_fast(self) -> list:
        """Fast tag scanning with minimal delay"""
        try:
            tags = list(self.reader.inventory_answer_mode())
            return tags
        except Exception as e:
            if "Response data is too short" not in str(e):
                print(f"⚠️  Scan error: {e}")
            return []
    
    def process_tags(self, tags: list):
        """Process detected tags with distance estimation"""
        current_time = datetime.now()
        
        if tags:
            self.total_detections += len(tags)
            
            for tag in tags:
                tag_hex = ' '.join([f'{b:02X}' for b in tag])
                
                if tag_hex in self.active_tags:
                    # Update existing tag
                    tag_info = self.active_tags[tag_hex]
                    tag_info['last_seen'] = current_time
                    tag_info['count'] += 1
                    
                    # Estimate signal strength based on detection frequency
                    detection_rate = tag_info['count'] / max(1, (current_time - tag_info['first_seen']).total_seconds())
                    
                    # Only print periodic updates for known tags
                    if tag_info['count'] % 10 == 0:  # Every 10th detection
                        duration = (current_time - tag_info['first_seen']).total_seconds()
                        signal_strength = "Strong" if detection_rate > 2 else "Medium" if detection_rate > 0.5 else "Weak"
                        print(f"📍 Tag {tag_hex[:20]}... - {signal_strength} signal ({tag_info['count']} detections, {duration:.1f}s)")
                
                else:
                    # New tag detected
                    self.active_tags[tag_hex] = {
                        'first_seen': current_time,
                        'last_seen': current_time,
                        'count': 1,
                        'data': tag
                    }
                    
                    print("=" * 60)
                    print(f"🆕 NEW TAG DETECTED!")
                    print(f"🕒 Time: {current_time.strftime('%H:%M:%S.%f')[:-3]}")
                    print(f"📊 Length: {len(tag)} bytes")
                    print(f"🔖 Data: {tag_hex}")
                    
                    # Try to parse as EPC
                    if len(tag) >= 12:
                        epc_full = ''.join([f'{b:02X}' for b in tag])
                        print(f"🏷️  EPC: {epc_full}")
                    
                    print("=" * 60)
    
    def cleanup_old_tags(self):
        """Remove tags that haven't been seen recently"""
        current_time = datetime.now()
        to_remove = []
        
        for tag_id, tag_info in self.active_tags.items():
            time_since_last = (current_time - tag_info['last_seen']).total_seconds()
            if time_since_last > self.cleanup_interval:
                to_remove.append(tag_id)
                print(f"👋 Tag removed: {tag_id[:20]}... (not seen for {time_since_last:.1f}s)")
        
        for tag_id in to_remove:
            del self.active_tags[tag_id]
    
    def run_continuous_scan(self):
        """Run continuous fast scanning"""
        print("🚀 Starting fast continuous scanning...")
        print("📡 Optimized for quick detection and distance tracking")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        last_cleanup = time.time()
        scan_count = 0
        consecutive_failures = 0
        start_time = time.time()
        
        try:
            # Optimize reader settings
            self.optimize_reader_settings()
            
            while True:
                scan_start = time.time()
                scan_count += 1
                
                # Perform fast scan
                tags = self.scan_tags_fast()
                
                if tags is not None:
                    consecutive_failures = 0
                    self.process_tags(tags)
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= self.max_scan_failures:
                        print("⚠️  Multiple scan failures, attempting to reconnect...")
                        if not self.connect():
                            break
                        consecutive_failures = 0
                
                # Periodic cleanup
                current_time = time.time()
                if current_time - last_cleanup > self.cleanup_interval:
                    self.cleanup_old_tags()
                    last_cleanup = current_time
                
                # Status update every 100 scans
                if scan_count % 100 == 0:
                    elapsed = current_time - start_time
                    scans_per_sec = scan_count / elapsed
                    print(f"📊 Status: {scan_count} scans, {len(self.active_tags)} active tags, {scans_per_sec:.1f} scans/sec")
                
                # Fast scanning - minimal delay
                scan_duration = time.time() - scan_start
                sleep_time = max(0, self.fast_scan_interval - scan_duration)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Scanning stopped by user")
        
        except Exception as e:
            print(f"❌ Scanning error: {e}")
            import traceback
            traceback.print_exc()
    
    def get_statistics(self):
        """Get scanning statistics"""
        return {
            'active_tags': len(self.active_tags),
            'total_detections': self.total_detections,
            'connected': self.connected
        }
    
    def close(self):
        """Close connection"""
        try:
            if self.reader:
                self.reader.close()
                self.connected = False
                print("🔌 Connection closed")
        except:
            pass

def main():
    """Main application"""
    print("🚀 RFID Fast Scanner - Optimized Detection")
    print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    scanner = FastRFIDScanner()
    
    try:
        if not scanner.connect():
            print("❌ Failed to connect to RFID reader")
            return
        
        scanner.run_continuous_scan()
        
    finally:
        stats = scanner.get_statistics()
        print(f"\n📊 Final Statistics:")
        print(f"   Active Tags: {stats['active_tags']}")
        print(f"   Total Detections: {stats['total_detections']}")
        
        scanner.close()

if __name__ == "__main__":
    main()