#!/usr/bin/env python3
"""
RFID Adaptive Scanner
Automatically adjusts settings based on tag detection patterns and distance
"""

from transport import SerialTransport
from reader import Reader
from response import Response
import time
from datetime import datetime
from typing import Dict, List

class AdaptiveRFIDScanner:
    def __init__(self, port: str = "COM5"):
        self.port = port
        self.reader = None
        self.transport = None
        
        # Adaptive parameters
        self.current_power = 20  # Start with medium power
        self.scan_interval = 0.2  # Start with 200ms
        self.detection_history: List[int] = []  # Track detections per scan cycle
        
        # Performance metrics
        self.successful_scans = 0
        self.failed_scans = 0
        self.total_tags_detected = 0
        
    def connect(self) -> bool:
        """Connect with adaptive timeout"""
        try:
            print(f"🔌 Connecting to adaptive RFID scanner...")
            self.transport = SerialTransport(self.port, 57600, timeout=0.5)
            self.reader = Reader(self.transport)
            
            # Test connection
            work_mode = self.reader.work_mode()
            print(f"✅ Connected! Mode: {work_mode.inventory_work_mode.name}")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def adjust_power_level(self, detection_success: bool, tag_count: int):
        """Dynamically adjust power based on detection success"""
        if detection_success and tag_count > 0:
            # Good detection - maintain or slightly reduce power to save energy
            if self.current_power > 15:
                self.current_power = max(15, self.current_power - 1)
        else:
            # Poor detection - increase power for better range
            if self.current_power < 30:
                self.current_power = min(30, self.current_power + 2)
        
        try:
            response = self.reader.set_power(self.current_power)
            if response.status == 0:
                print(f"⚡ Power adjusted to {self.current_power}")
            return True
        except:
            return False
    
    def adjust_scan_timing(self):
        """Adjust scan interval based on recent detection patterns"""
        if len(self.detection_history) >= 10:
            recent_detections = sum(self.detection_history[-10:])
            
            if recent_detections > 15:
                # High activity - scan faster
                self.scan_interval = max(0.05, self.scan_interval * 0.9)
            elif recent_detections < 3:
                # Low activity - scan slower to reduce noise
                self.scan_interval = min(1.0, self.scan_interval * 1.1)
            
            # Keep history manageable
            if len(self.detection_history) > 20:
                self.detection_history = self.detection_history[-15:]
    
    def scan_with_retry(self, max_retries: int = 3) -> List[bytes]:
        """Scan with automatic retry and adaptation"""
        for attempt in range(max_retries):
            try:
                tags = list(self.reader.inventory_answer_mode())
                self.successful_scans += 1
                return tags
                
            except Exception as e:
                self.failed_scans += 1
                if attempt < max_retries - 1:
                    # Brief pause before retry
                    time.sleep(0.05)
                    continue
                else:
                    # Final attempt failed
                    if "Response data is too short" not in str(e):
                        print(f"⚠️  Scan failed after {max_retries} attempts: {e}")
                    return []
    
    def run_adaptive_scanning(self, duration_minutes: int = None):
        """Run adaptive scanning with automatic optimization"""
        print("🧠 Starting adaptive RFID scanning...")
        print("📈 System will automatically optimize for best performance")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        start_time = time.time()
        scan_count = 0
        last_stats_time = start_time
        
        # Initial power setting
        self.adjust_power_level(False, 0)
        
        try:
            while True:
                scan_start_time = time.time()
                
                # Perform adaptive scan
                tags = self.scan_with_retry()
                tag_count = len(tags) if tags else 0
                
                # Track detection history
                self.detection_history.append(tag_count)
                self.total_tags_detected += tag_count
                
                # Process detected tags
                if tags:
                    current_time = datetime.now()
                    print(f"🏷️  Detected {tag_count} tag(s) at {current_time.strftime('%H:%M:%S.%f')[:-3]}:")
                    
                    for i, tag in enumerate(tags, 1):
                        tag_hex = ' '.join([f'{b:02X}' for b in tag])
                        print(f"   Tag {i}: {tag_hex}")
                        
                        if len(tag) >= 12:
                            epc = ''.join([f'{b:02X}' for b in tag])
                            print(f"         EPC: {epc}")
                
                # Adaptive adjustments every 10 scans
                scan_count += 1
                if scan_count % 10 == 0:
                    self.adjust_power_level(tag_count > 0, tag_count)
                    self.adjust_scan_timing()
                
                # Performance statistics every 30 seconds
                current_time = time.time()
                if current_time - last_stats_time > 30:
                    elapsed = current_time - start_time
                    success_rate = self.successful_scans / max(1, self.successful_scans + self.failed_scans) * 100
                    tags_per_minute = self.total_tags_detected / max(1, elapsed / 60)
                    
                    print(f"📊 Performance: {success_rate:.1f}% success, "
                          f"{tags_per_minute:.1f} tags/min, "
                          f"Power: {self.current_power}, "
                          f"Interval: {self.scan_interval:.2f}s")
                    
                    last_stats_time = current_time
                
                # Check duration limit
                if duration_minutes and (current_time - start_time) > duration_minutes * 60:
                    print(f"⏰ Reached {duration_minutes} minute limit")
                    break
                
                # Adaptive sleep
                scan_duration = time.time() - scan_start_time
                sleep_time = max(0, self.scan_interval - scan_duration)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Adaptive scanning stopped")
        
        # Final report
        elapsed = time.time() - start_time
        print(f"\n📈 Adaptive Scanning Report:")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"   Total Scans: {scan_count}")
        print(f"   Success Rate: {self.successful_scans / max(1, self.successful_scans + self.failed_scans) * 100:.1f}%")
        print(f"   Tags Detected: {self.total_tags_detected}")
        print(f"   Final Power Level: {self.current_power}")
        print(f"   Final Scan Interval: {self.scan_interval:.3f}s")
    
    def close(self):
        """Close connection"""
        try:
            if self.reader:
                self.reader.close()
                print("🔌 Connection closed")
        except:
            pass

def main():
    """Main adaptive scanner application"""
    print("🧠 RFID Adaptive Scanner")
    print("📅", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    
    scanner = AdaptiveRFIDScanner()
    
    try:
        if not scanner.connect():
            print("❌ Failed to connect to RFID reader")
            return
        
        # Run adaptive scanning
        scanner.run_adaptive_scanning()
        
    finally:
        scanner.close()

if __name__ == "__main__":
    main()