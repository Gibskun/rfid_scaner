#!/usr/bin/env python3
"""
Quick Database Status Check
Shows current database contents
"""

from database import get_database
from datetime import datetime

def show_database_status():
    """Show current database status"""
    print("=" * 70)
    print("📊 RFID DATABASE STATUS")
    print("=" * 70)
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        db = get_database()
        print("✅ Database connected")
        print()
        
        # Get statistics
        stats = db.get_statistics()
        
        print("📈 STATISTICS:")
        print("─" * 70)
        print(f"  Total Tags:        {stats['total_tags']}")
        print(f"  Written Tags:      {stats['written_tags']}")
        print(f"  Unwritten Tags:    {stats['unwritten_tags']}")
        print(f"  Total Detections:  {stats['total_detections']}")
        print(f"  Recent (24h):      {stats['recent_detections_24h']}")
        print()
        
        # Get all tags
        tags = db.get_all_tags(limit=20)
        
        if tags:
            print(f"📋 REGISTERED TAGS (showing {len(tags)}):")
            print("─" * 70)
            for i, tag in enumerate(tags, 1):
                item_name = tag['item_name'] or "(No name)"
                tag_id_short = tag['tag_id'][:30] + "..." if len(tag['tag_id']) > 30 else tag['tag_id']
                status = "✅ Written" if tag['is_written'] else "⏳ Not written"
                
                print(f"\n{i}. {item_name}")
                print(f"   Tag: {tag_id_short}")
                print(f"   Status: {status}")
                print(f"   Detections: {tag['detection_count']}")
                if tag['write_date']:
                    print(f"   Written: {tag['write_date']}")
        else:
            print("📭 DATABASE IS EMPTY")
            print("─" * 70)
            print("No tags registered yet.")
            print()
            print("To register tags:")
            print("  1. Run: python interactive_scanner.py")
            print("  2. Or: python tag_writer.py")
        
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure PostgreSQL is running and database is configured.")

if __name__ == "__main__":
    show_database_status()
