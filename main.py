#!/usr/bin/env python3
"""
RFID Reader - All-in-One System
Runs both terminal scanner AND web interface simultaneously
Single command: python main.py
Includes database integration for tag storage and rewriting
"""

from transport import SerialTransport
from reader import Reader
from response import Response, WorkMode, InventoryWorkMode
from database import get_database
import time
import threading
import webbrowser
import subprocess
import sys
import os
from typing import Dict, Set
from datetime import datetime
from shared_data import (
    update_connection_status, update_scanning_status, add_tag_detection,
    cleanup_old_tags, update_scan_statistics, get_statistics
)

class FastRFIDScanner:
    def __init__(self, port: str = "COM5", baud_rate: int = 57600):
        self.port = port
        self.baud_rate = baud_rate
        self.reader = None
        self.transport = None
        self.connected = False
        
        # Database integration
        try:
            self.db = get_database()
            print("✅ Database connected successfully")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("   System will continue without database features")
            self.db = None
        
        # Tag tracking with signal strength estimation
        self.active_tags: Dict[str, dict] = {}  # tag_id -> {first_seen, last_seen, count, data}
        self.total_detections = 0
        
        # Performance settings
        self.fast_scan_interval = 0.1  # 100ms between scans for fast detection
        self.cleanup_interval = 5.0    # Remove tags not seen for 5 seconds
        self.max_scan_failures = 5     # Max consecutive failures before reconnect
        
        # Interactive mode control (write functionality removed)
        self.pause_scanning = False
        
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
            update_connection_status(True, "Connected")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            update_connection_status(False, f"Connection failed: {e}")
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
            return tags if tags else []
        except Exception as e:
            # Only log unexpected errors, not normal "no tags" responses
            error_msg = str(e)
            if ("Response data is too short" not in error_msg and 
                "No tags found" not in error_msg):
                print(f"⚠️  Scan error: {e}")
            return []
    
    def process_tags(self, tags: list):
        """Process detected tags - prompt to write new tags not in database"""
        current_time = datetime.now()
        
        if tags:
            self.total_detections += len(tags)
            
            for tag in tags:
                # Ensure tag is valid and has data
                if not tag or len(tag) == 0:
                    continue
                    
                tag_hex = ' '.join([f'{b:02X}' for b in tag])
                
                # Check if this is a new tag for terminal display
                is_new_tag = tag_hex not in self.active_tags
                
                # Update shared data system (for web interface)
                add_tag_detection(tag_hex, tag, self.db)
                
                # Update local tracking
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
                    # New tag detected - add to local tracking
                    self.active_tags[tag_hex] = {
                        'first_seen': current_time,
                        'last_seen': current_time,
                        'count': 1,
                        'data': tag,
                        'prompted': False  # Track if user was already prompted
                    }
                    
                    print("=" * 60)
                    print(f"🆕 NEW TAG DETECTED!")
                    print(f"🕒 Time: {current_time.strftime('%H:%M:%S.%f')[:-3]}")
                    print(f"📊 Length: {len(tag)} bytes")
                    print(f"🔖 Data: {tag_hex}")
                    print(f"🔢 Raw bytes: {[hex(b) for b in tag]}")
                    
                    # Check if tag is in database
                    tag_in_database = False
                    if self.db:
                        try:
                            tag_info_db = self.db.get_tag_info(tag_hex)
                            if tag_info_db:
                                tag_in_database = True
                                print(f"💾 Database: ✅ REGISTERED TAG")
                                print(f"   🆔 RFID: {tag_info_db.get('rf_id', 'N/A')}")
                                if tag_info_db.get('palette_number'):
                                    print(f"   📦 Palette: #{tag_info_db['palette_number']}")
                                if tag_info_db.get('name'):
                                    print(f"   🏷️  Name: {tag_info_db['name']}")
                                print(f"   📊 Status: {tag_info_db.get('status', 'unknown')}")
                                if tag_info_db.get('created'):
                                    print(f"   📅 Created: {tag_info_db['created']}")
                            else:
                                print(f"💾 Database: ⚠️  NEW TAG - Not in database!")
                                print(f"   🔄 This tag needs to be registered on the web interface.")
                        except Exception as e:
                            print(f"⚠️  Database lookup failed: {e}")
                    
                    # Write functionality removed - just log new tags
                    if self.db and not tag_in_database:
                        print("📝 Note: This is a new unregistered tag")
                    
                    # Try to parse as EPC
                    if len(tag) >= 12:
                        epc_full = ''.join([f'{b:02X}' for b in tag])
                        print(f"🏷️  EPC: {epc_full}")
                    elif len(tag) >= 4:
                        # Shorter tag, might be TID or partial EPC
                        short_id = ''.join([f'{b:02X}' for b in tag])
                        print(f"🏷️  Short ID: {short_id}")
                    
                    print("=" * 60)
    
    def cleanup_old_tags(self):
        """Remove tags that haven't been seen recently"""
        # Use shared cleanup function
        removed_tags = cleanup_old_tags(self.cleanup_interval)
        
        # Remove from local tracking and print messages
        for tag_id in removed_tags:
            if tag_id in self.active_tags:
                del self.active_tags[tag_id]
                print(f"👋 Tag removed: {tag_id[:20]}... (not seen for {self.cleanup_interval}s)")
    
    def run_continuous_scan(self):
        """Run continuous fast scanning with shared data updates"""
        print("🚀 Starting fast continuous scanning...")
        print("📡 Optimized for quick detection and distance tracking")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        last_cleanup = time.time()
        scan_count = 0
        consecutive_failures = 0
        start_time = time.time()
        
        # Update shared scanning status
        update_scanning_status(True)
        
        try:
            # Optimize reader settings
            self.optimize_reader_settings()
            
            while True:
                # Check if scanning is paused (waiting for user input)
                if self.pause_scanning:
                    time.sleep(0.1)
                    continue
                
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
                
                # Update shared scan statistics
                update_scan_statistics(scan_count)
                
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
            update_connection_status(False, f"Scanning error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            update_scanning_status(False)
    
    def get_statistics(self):
        """Get scanning statistics"""
        return get_statistics()
    
    def close(self):
        """Close connection"""
        try:
            if self.reader:
                self.reader.close()
                self.connected = False
                print("🔌 Connection closed")
        except:
            pass
    


def run_terminal_scanner():
    """Run the terminal scanner in a separate thread"""
    print("\n🖥️  TERMINAL SCANNER")
    print("=" * 40)
    
    scanner = FastRFIDScanner()
    
    # Share the database instance with web interface
    if scanner.db:
        print("🔗 Sharing database instance with web interface...")
        from web_interface import set_database_instance
        set_database_instance(scanner.db)
    
    try:
        print("🔌 Terminal: Connecting to RFID reader...")
        if not scanner.connect():
            print("❌ Terminal: Failed to connect to RFID reader")
            return
        
        print("✅ Terminal: Connection successful! Starting scan...")
        scanner.run_continuous_scan()
        
    finally:
        stats = scanner.get_statistics()
        print(f"\n📊 Terminal Scanner Final Statistics:")
        print(f"   Active Tags: {stats['active_tags']}")
        print(f"   Total Detections: {stats['total_detections']}")
        
        scanner.close()

def run_web_interface():
    """Run the web interface in same terminal (no new window)"""
    try:
        print("\n🌐 WEB INTERFACE")
        print("=" * 40)
        print("🚀 Starting web server in background...")
        print("📱 Dashboard will be available at: http://localhost:5000")
        print("🔄 Web interface will auto-start scanning when browser connects")
        
        # Import and run web interface directly in this process
        from web_interface import app, socketio
        
        # Start web server in background thread (no new terminal)
        def start_web_server():
            socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
        web_server_thread = threading.Thread(target=start_web_server)
        web_server_thread.daemon = True
        web_server_thread.start()
        
        # Wait a moment then open browser
        time.sleep(2)
        try:
            webbrowser.open("http://localhost:5000")
            print("🌍 Opened web browser - Main Dashboard loaded!")
            print("🏷️  Click 'Enter RFID Registration System' to start scanning!")
        except:
            print("⚠️  Could not auto-open browser. Please visit: http://localhost:5000")
            
    except Exception as e:
        print(f"❌ Web interface error: {e}")

def main():
    """All-in-One RFID System - Terminal + Web Interface (Single Terminal)"""
    print("🚀 RFID ALL-IN-ONE SYSTEM")
    print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🎯 Dashboard-First Architecture - Professional Entry System")
    print("=" * 60)
    print("🏠 Main Dashboard: Professional landing page with system overview")
    print("🏷️  Registration System: Accessible via 'Register' button")
    print("🖥️  Terminal Scanner: Real-time tag detection in console")
    print("🌐 Web Interface: Dashboard at http://localhost:5000")
    print("🚀 System starts with main dashboard first!")
    print("🌍 Web browser will open automatically to main dashboard!")
    print("=" * 60)
    
    try:
        # Start web interface immediately in background (same terminal)
        print("⏳ Starting web interface...")
        web_thread = threading.Thread(target=run_web_interface)
        web_thread.daemon = True
        web_thread.start()
        
        # Start terminal scanner in background thread
        print("⏳ Starting terminal scanner...")
        terminal_thread = threading.Thread(target=run_terminal_scanner)
        terminal_thread.daemon = True
        terminal_thread.start()
        
        # Give both systems a moment to initialize
        time.sleep(1)
        
        # Keep main thread alive to handle both systems
        print("✅ Both systems are running! Press Ctrl+C to stop everything.")
        print("� Main Dashboard: http://localhost:5000")
        print("🏷️  Registration System: http://localhost:5000/register")
        print("🖥️  Terminal logs will appear below:")
        print("=" * 60)
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n🛑 All systems stopped by user")
        print("👋 Thank you for using RFID All-in-One System!")
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()