#!/usr/bin/env python3
"""
Clear Database - Remove all data from RFID database
Use this to reset the database before starting fresh
"""

import sys
from database import get_database

def clear_database():
    """Clear all data from the database"""
    print("⚠️  DATABASE CLEARING UTILITY")
    print("=" * 60)
    print("This will DELETE ALL data from the database!")
    print("Tables will remain, but all records will be removed.")
    print()
    
    confirm = input("Are you sure you want to continue? (type 'YES' to confirm): ").strip()
    
    if confirm.upper() != "YES":
        print("❌ Cancelled - no data was deleted")
        return False
    
    try:
        db = get_database()
        conn = db.connection_pool.getconn()
        cursor = conn.cursor()
        
        print("\n🗑️  Deleting all records...")
        
        # Delete from history table first (foreign key constraint)
        cursor.execute("DELETE FROM tag_detection_history")
        history_count = cursor.rowcount
        print(f"   ✅ Deleted {history_count} detection history records")
        
        # Delete from main tags table
        cursor.execute("DELETE FROM rfid_tags")
        tags_count = cursor.rowcount
        print(f"   ✅ Deleted {tags_count} tag records")
        
        # Reset sequences
        cursor.execute("ALTER SEQUENCE rfid_tags_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE tag_detection_history_id_seq RESTART WITH 1")
        print("   ✅ Reset ID sequences")
        
        conn.commit()
        db.connection_pool.putconn(conn)
        
        print("\n✅ Database cleared successfully!")
        print(f"   Total records deleted: {tags_count + history_count}")
        print("\n💡 The database is now empty and ready for fresh data.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error clearing database: {e}")
        if conn:
            conn.rollback()
            db.connection_pool.putconn(conn)
        return False

if __name__ == "__main__":
    try:
        success = clear_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        sys.exit(1)
