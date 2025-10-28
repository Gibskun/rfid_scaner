#!/usr/bin/env python3
"""
RFID Tag Simulator - Test the system with simulated tags
This allows testing the web interface and shared data without physical RFID tags
"""

import time
import threading
from datetime import datetime
from shared_data import add_tag_detection, update_scanning_status, update_connection_status

class TagSimulator:
    def __init__(self):
        self.running = False
        self.thread = None
        
        # Sample RFID tag data (different types and formats)
        self.test_tags = [
            # EPC tags (12 bytes)
            bytes([0x30, 0x00, 0x9C, 0x57, 0x2E, 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD]),
            bytes([0x30, 0x00, 0x9C, 0x57, 0x2E, 0xFF, 0xEE, 0xDD, 0xCC, 0xBB, 0xAA, 0x99]),
            
            # TID tags (8 bytes)  
            bytes([0xE2, 0x80, 0x11, 0x60, 0x20, 0x00, 0x01, 0x23]),
            bytes([0xE2, 0x80, 0x11, 0x60, 0x20, 0x00, 0x04, 0x56]),
            
            # Short format tags (4 bytes)
            bytes([0x12, 0x34, 0x56, 0x78]),
            bytes([0xAB, 0xCD, 0xEF, 0x01]),
            
            # Variable length tags
            bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66]),
            bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x11, 0x22])
        ]
        
        self.tag_names = [
            "Asset Tag #001",
            "Asset Tag #002", 
            "Employee Badge A",
            "Employee Badge B",
            "Access Card 1",
            "Access Card 2",
            "Inventory Item X",
            "Inventory Item Y"
        ]
    
    def start_simulation(self, duration=60):
        """Start simulating RFID tags for testing"""
        if self.running:
            return
        
        print("🎯 Starting RFID Tag Simulation...")
        print(f"⏱️  Will simulate tags for {duration} seconds")
        print("📡 This will test the web interface and shared data system")
        
        # Update status
        update_connection_status(True, "Simulating tags")
        update_scanning_status(True)
        
        self.running = True
        self.thread = threading.Thread(target=self._simulate_tags, args=(duration,))
        self.thread.daemon = True
        self.thread.start()
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("🛑 Tag simulation stopped")
    
    def _simulate_tags(self, duration):
        """Internal method to simulate tag detections"""
        start_time = time.time()
        tag_cycle = 0
        
        try:
            while self.running and (time.time() - start_time) < duration:
                # Simulate different scenarios
                current_time = time.time() - start_time
                
                if current_time < 10:
                    # First 10 seconds: Single tag
                    tag = self.test_tags[0]
                    tag_hex = ' '.join([f'{b:02X}' for b in tag])
                    add_tag_detection(tag_hex, tag)
                    print(f"🏷️  Simulated: {self.tag_names[0]} - {tag_hex}")
                    
                elif current_time < 25:
                    # Next 15 seconds: Two tags alternating
                    tag_idx = tag_cycle % 2
                    tag = self.test_tags[tag_idx]
                    tag_hex = ' '.join([f'{b:02X}' for b in tag])
                    add_tag_detection(tag_hex, tag)
                    if tag_cycle % 5 == 0:
                        print(f"🏷️  Simulated: {self.tag_names[tag_idx]} - {tag_hex}")
                    
                elif current_time < 40:
                    # Next 15 seconds: Multiple tags quickly
                    for i in range(min(4, len(self.test_tags))):
                        tag = self.test_tags[i]
                        tag_hex = ' '.join([f'{b:02X}' for b in tag])
                        add_tag_detection(tag_hex, tag)
                    
                    if tag_cycle % 10 == 0:
                        print(f"🏷️  Simulated: Multiple tags (4 tags)")
                
                elif current_time < 50:
                    # Next 10 seconds: Random single tags
                    tag_idx = tag_cycle % len(self.test_tags)
                    tag = self.test_tags[tag_idx]
                    tag_hex = ' '.join([f'{b:02X}' for b in tag])
                    add_tag_detection(tag_hex, tag)
                    if tag_cycle % 8 == 0:
                        print(f"🏷️  Simulated: {self.tag_names[tag_idx]} - {tag_hex}")
                
                else:
                    # Last 10 seconds: Gradually remove tags (simulate tags moving away)
                    if tag_cycle % 3 == 0:  # Less frequent detections
                        tag = self.test_tags[0]
                        tag_hex = ' '.join([f'{b:02X}' for b in tag])
                        add_tag_detection(tag_hex, tag)
                
                tag_cycle += 1
                time.sleep(0.5)  # Detect every 500ms
                
        except Exception as e:
            print(f"❌ Simulation error: {e}")
        
        finally:
            self.running = False
            print("✅ Tag simulation completed")

def main():
    """Run the tag simulator"""
    print("🎯 RFID Tag Simulator")
    print("=" * 50)
    print("This tool simulates RFID tag detections for testing")
    print("Run this while the main RFID system is running to see:")
    print("  • Tags appearing in the web interface")
    print("  • Real-time updates and statistics")
    print("  • Activity logs and signal strength")
    print("=" * 50)
    
    simulator = TagSimulator()
    
    try:
        # Run simulation for 60 seconds
        simulator.start_simulation(60)
        
        # Keep main thread alive
        while simulator.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user")
        simulator.stop_simulation()
    
    print("👋 Tag simulation finished!")

if __name__ == "__main__":
    main()