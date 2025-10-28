#!/usr/bin/env python3
"""
RFID System - Main Entry Point
Optimized RFID reader system for HW-VX6330K with fast detection and distance estimation

This is the main entry point that automatically runs the best available scanner.
"""

import sys
import os
from pathlib import Path

def main():
    """Main entry point - runs the optimal RFID scanner"""
    
    print("🚀 RFID System - Optimized Detection System")
    print("=" * 60)
    print("📡 HW-VX6330K RFID Reader System")
    print("⚡ Fast Detection & Distance Estimation")
    print("=" * 60)
    print()
    
    # Check if we have the fast scanner available
    fast_scanner_path = Path("rfid_fast_scanner.py")
    working_scanner_path = Path("rfid_working.py")
    
    if fast_scanner_path.exists():
        print("🎯 Starting OPTIMIZED Fast Scanner")
        print("   • 7+ scans per second")
        print("   • Distance estimation via detection frequency")
        print("   • Advanced noise filtering")
        print("   • Real-time statistics")
        print()
        
        # Import and run the fast scanner
        try:
            from rfid_fast_scanner import main as fast_main
            fast_main()
        except ImportError as e:
            print(f"❌ Error importing fast scanner: {e}")
            print("🔄 Falling back to basic scanner...")
            fallback_to_working()
            
    elif working_scanner_path.exists():
        print("🔧 Starting Basic Working Scanner")
        fallback_to_working()
        
    else:
        print("❌ No RFID scanner modules found!")
        print("🔧 Please ensure rfid_fast_scanner.py or rfid_working.py exists")
        sys.exit(1)

def fallback_to_working():
    """Run the basic working scanner as fallback"""
    try:
        from rfid_working import main as working_main
        working_main()
    except ImportError as e:
        print(f"❌ Error importing working scanner: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1)