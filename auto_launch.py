#!/usr/bin/env python3
"""
RFID Auto-Launch System
Automatically starts either terminal scanning or web interface with auto-scanning
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading

def launch_terminal_scanner():
    """Launch terminal scanner with auto-start"""
    print("🖥️  Launching Terminal Scanner with Auto-Start...")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Terminal scanner stopped!")

def launch_web_interface():
    """Launch web interface with auto-start"""
    print("🌐 Launching Web Interface with Auto-Start...")
    print("=" * 60)
    print("📱 Dashboard URL: http://localhost:5000")
    print("🚀 Scanning will start automatically when you connect")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Auto-open browser after a delay
    def open_browser():
        time.sleep(3)  # Give server time to start
        try:
            webbrowser.open("http://localhost:5000")
            print("🌍 Opened web browser automatically")
        except:
            print("⚠️  Could not auto-open browser. Please visit: http://localhost:5000")
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the web interface
    try:
        subprocess.run([sys.executable, "web_interface.py"])
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped!")

def main():
    """Main launcher with auto-start options"""
    print("🚀 RFID Auto-Launch System")
    print("=" * 50)
    print("🔄 Both options feature AUTO-START - no manual clicking required!")
    print()
    print("Choose your interface:")
    print("1. 🖥️  Terminal Scanner (Auto-start)")
    print("2. 🌐 Web Dashboard (Auto-start)")
    print("3. 📊 All-in-One Web (Single file)")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                launch_terminal_scanner()
                break
            elif choice == "2":
                launch_web_interface()
                break
            elif choice == "3":
                print("🔥 Launching All-in-One Web Interface...")
                try:
                    subprocess.run([sys.executable, "rfid_web_auto.py"])
                except KeyboardInterrupt:
                    print("\n👋 All-in-one interface stopped!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("main.py") or not os.path.exists("web_interface.py"):
        print("❌ Error: Required files not found!")
        print("   Please run this from the RFID Config\\Reader directory")
        input("Press Enter to exit...")
        sys.exit(1)
    
    main()