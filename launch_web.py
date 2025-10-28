#!/usr/bin/env python3
"""
RFID Web Interface Launcher
Simple launcher for the RFID web monitoring system
"""

import subprocess
import sys
import os
import webbrowser
import time

def main():
    print("🚀 RFID Web Interface Launcher - Auto-Start Mode")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("web_interface.py"):
        print("❌ Error: web_interface.py not found!")
        print("   Please run this from the RFID Config\\Reader directory")
        input("Press Enter to exit...")
        return
    
    print("🌐 Starting RFID Web Interface with Auto-Scanning...")
    print("📱 Dashboard URL: http://localhost:5000")
    print("🚀 Scanning starts automatically - no clicking required!")
    print("⏹️  Press Ctrl+C in this window to stop the server")
    print()
    
    # Wait a moment then open browser
    def open_browser():
        time.sleep(3)  # Give server time to start
        try:
            webbrowser.open("http://localhost:5000")
            print("🌍 Opened web browser to dashboard - scanning will begin automatically")
        except:
            print("⚠️  Could not auto-open browser. Please visit: http://localhost:5000")
    
    # Start browser opening in background
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the web interface
    try:
        subprocess.run([
            sys.executable, "web_interface.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped!")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()