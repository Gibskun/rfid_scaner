#!/usr/bin/env python3
"""
🚀 RFID System - Final Entry Point
Clean and organized RFID reader system with fast detection capabilities

Usage:
  python START_HERE.py     # Run the optimized system
  
For specific scanners:
  python rfid_fast_scanner.py      # Fast scanner (recommended)
  python rfid_adaptive_scanner.py  # Auto-tuning scanner
  python rfid_working.py           # Basic stable scanner
"""

def main():
    print("🚀 RFID System - Organized Project")
    print("=" * 50)
    print()
    print("🎯 Quick Start Options:")
    print()
    print("1. 🚀 FAST SCANNER (Recommended)")
    print("   python rfid_fast_scanner.py")
    print("   • 7+ scans per second")
    print("   • Distance estimation")
    print("   • Advanced noise filtering")
    print()
    print("2. 🔄 ADAPTIVE SCANNER")
    print("   python rfid_adaptive_scanner.py")
    print("   • Auto power adjustment")
    print("   • Self-tuning optimization")
    print()
    print("3. 🔧 BASIC SCANNER") 
    print("   python rfid_working.py")
    print("   • Simple and stable")
    print("   • Good for testing")
    print()
    print("4. 📊 PERFORMANCE TEST")
    print("   python test_performance.py")
    print("   • 10-second benchmark")
    print()
    print("═" * 50)
    
    choice = input("Choose scanner (1-4) or Enter for fast scanner: ").strip()
    
    if choice == "1" or choice == "":
        print("🚀 Starting Fast Scanner...")
        from rfid_fast_scanner import main as fast_main
        fast_main()
    elif choice == "2":
        print("🔄 Starting Adaptive Scanner...")
        from rfid_adaptive_scanner import main as adaptive_main
        adaptive_main()
    elif choice == "3":
        print("🔧 Starting Basic Scanner...")
        from rfid_working import main as working_main
        working_main()
    elif choice == "4":
        print("📊 Running Performance Test...")
        from test_performance import main as test_main
        test_main()
    else:
        print("❌ Invalid choice. Starting fast scanner...")
        from rfid_fast_scanner import main as fast_main
        fast_main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")