#!/usr/bin/env python3
"""
Performance test for the optimized RFID system
"""

import time
from rfid_fast_scanner import FastRFIDScanner

def main():
    print("🚀 Testing Optimized RFID Performance")
    print("=" * 50)
    
    scanner = FastRFIDScanner()
    
    try:
        print("📡 Connecting to RFID reader...")
        scanner.connect()
        
        print("⏱️  Running 30-second performance test...")
        start_time = time.time()
        
        # Run for 10 seconds test
        test_start = time.time()
        scan_count = 0
        
        try:
            while (time.time() - test_start) < 10:  # 10 second test
                tags = scanner.scan_tags_fast()
                if tags is not None:
                    scanner.process_tags(tags)
                    scan_count += 1
                time.sleep(0.1)  # Fast scanning
        except:
            pass
        
        end_time = time.time()
        total_time = end_time - test_start
        
        print(f"\n📊 Performance Results:")
        print(f"   Duration: {total_time:.1f} seconds")
        print(f"   Total Scans: {scan_count}")
        print(f"   Scan Rate: {scan_count / total_time:.2f} scans/sec")
        print(f"   Total Detections: {scanner.total_detections}")
        
        if scanner.active_tags:
            print(f"\n🏷️  Active Tags:")
            for tag_id, tag_info in scanner.active_tags.items():
                print(f"   Tag {tag_id[:20]}...: {tag_info['count']} detections")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scanner.close()
        print("✅ Test completed")

if __name__ == "__main__":
    main()