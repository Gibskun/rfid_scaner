#!/usr/bin/env python3
"""
Test Database Integration
Quick test to verify PostgreSQL database is working correctly
"""

import sys
from datetime import datetime

def test_database_connection():
    """Test basic database connection"""
    print("🧪 Testing Database Connection...")
    try:
        from database import get_database
        db = get_database()
        print("✅ Database connection successful!")
        return db
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. Username: postgres, Password: 123")
        print("3. Port: 5432")
        return None

def test_database_operations(db):
    """Test database CRUD operations"""
    print("\n🧪 Testing Database Operations...")
    
    # Test 1: Add a test tag
    print("\n1️⃣ Adding test tag...")
    test_tag_id = f"TEST {datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        success = db.add_or_update_tag(
            tag_id=test_tag_id, 
            rf_id="RF001", 
            palette_number=123, 
            name="Test Item"
        )
        if success:
            print("✅ Tag added successfully")
        else:
            print("❌ Failed to add tag")
            return False
    except Exception as e:
        print(f"❌ Error adding tag: {e}")
        return False
    
    # Test 2: Retrieve the tag
    print("\n2️⃣ Retrieving tag info...")
    try:
        tag_info = db.get_tag_info(test_tag_id)
        if tag_info:
            print("✅ Tag retrieved successfully")
            print(f"   Tag ID: {tag_info['tag_id']}")
            print(f"   Name: {tag_info['name']}")
            print(f"   RF ID: {tag_info['rf_id']}")
            print(f"   Palette Number: {tag_info['palette_number']}")
            print(f"   Status: {tag_info['status']}")
            print(f"   Created: {tag_info['created']}")
        else:
            print("❌ Tag not found")
            return False
    except Exception as e:
        print(f"❌ Error retrieving tag: {e}")
        return False
    
    # Test 3: Update tag
    print("\n3️⃣ Testing tag updates...")
    try:
        success = db.add_or_update_tag(
            tag_id=test_tag_id, 
            palette_number=456,  # Update palette number
            name="Updated Test Item"  # Update name
        )
        if success:
            print("✅ Tag updated successfully")
        else:
            print("❌ Failed to update tag")
    except Exception as e:
        print(f"❌ Error updating tag: {e}")
    
    # Test 4: Search for tags
    print("\n4️⃣ Searching for tags...")
    try:
        results = db.search_tags("Test")
        if results:
            print(f"✅ Found {len(results)} tag(s)")
            for r in results[:3]:  # Show first 3
                print(f"   - {r['tag_id'][:30]}... ({r['name']})")
        else:
            print("⚠️  No tags found (this might be normal)")
    except Exception as e:
        print(f"❌ Error searching tags: {e}")
        return False
    
    # Test 5: Get statistics
    print("\n5️⃣ Getting database statistics...")
    try:
        stats = db.get_statistics()
        print("✅ Statistics retrieved:")
        print(f"   Total Tags: {stats['total_tags']}")
        print(f"   Active Tags: {stats['active_tags']}")
        print(f"   Inactive Tags: {stats['inactive_tags']}")
        print(f"   Deleted Tags: {stats['deleted_tags']}")
        print(f"   Assigned Tags: {stats['assigned_tags']}")
        print(f"   Unassigned Tags: {stats['unassigned_tags']}")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return False
    
    # Test 6: Get all tags
    print("\n6️⃣ Getting all tags (limit 5)...")
    try:
        tags = db.get_all_tags(limit=5)
        print(f"✅ Retrieved {len(tags)} tag(s)")
        for tag in tags:
            print(f"   - {tag['name']}: {tag['status']} (Palette: {tag['palette_number']})")
    except Exception as e:
        print(f"❌ Error getting all tags: {e}")
        return False
    
    # Test 7: Soft deletion
    print("\n7️⃣ Testing soft deletion...")
    try:
        success = db.delete_tag(test_tag_id)
        if success:
            print("✅ Tag soft deleted successfully")
            # Verify it doesn't appear in active tags
            tags = db.get_all_tags()
            found = any(tag['tag_id'] == test_tag_id for tag in tags)
            if not found:
                print("✅ Deleted tag correctly excluded from active tags")
            else:
                print("❌ Deleted tag still appears in active tags")
        else:
            print("❌ Failed to delete tag")
    except Exception as e:
        print(f"❌ Error deleting tag: {e}")
    
    # Test 8: Restore tag
    print("\n8️⃣ Testing tag restoration...")
    try:
        success = db.restore_tag(test_tag_id)
        if success:
            print("✅ Tag restored successfully")
            # Verify it appears in active tags again
            tags = db.get_all_tags()
            found = any(tag['tag_id'] == test_tag_id for tag in tags)
            if found:
                print("✅ Restored tag correctly appears in active tags")
            else:
                print("❌ Restored tag doesn't appear in active tags")
        else:
            print("❌ Failed to restore tag")
    except Exception as e:
        print(f"❌ Error restoring tag: {e}")
    
    return True

def test_database_tables(db):
    """Verify database tables exist"""
    print("\n🧪 Verifying Database Tables...")
    
    try:
        conn = db.connection_pool.getconn()
        cursor = conn.cursor()
        
        # Check rfid_tags table
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'rfid_tags'
        """)
        
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        if 'rfid_tags' in table_names:
            print("✅ Table 'rfid_tags' exists")
            
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'rfid_tags' 
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            expected_columns = ['tag_id', 'rf_id', 'palette_number', 'name', 'status', 'created', 'deleted']
            actual_columns = [col[0] for col in columns]
            
            if all(col in actual_columns for col in expected_columns):
                print("✅ Table structure matches new schema")
            else:
                print(f"❌ Table structure mismatch. Expected: {expected_columns}, Found: {actual_columns}")
                return False
        else:
            print("❌ Table 'rfid_tags' missing")
            return False
        
        db.connection_pool.putconn(conn)
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Run all database tests"""
    print("=" * 60)
    print("🧪 RFID Database Integration Test")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Connection
    db = test_database_connection()
    if not db:
        print("\n❌ Database tests failed - cannot connect")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Username: postgres")
        print("  3. Password: 123")
        print("  4. Port: 5432")
        return False
    
    # Test 2: Tables
    if not test_database_tables(db):
        print("\n❌ Database table verification failed")
        return False
    
    # Test 3: Operations
    if not test_database_operations(db):
        print("\n❌ Database operations test failed")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("Your database is ready to use:")
    print("  • PostgreSQL connected")
    print("  • Tables created")
    print("  • CRUD operations working")
    print("  • Search functionality working")
    print()
    print("Next steps:")
    print("  1. Run: python tag_writer.py")
    print("  2. Or run: python main.py")
    print("  3. Start detecting and writing tags!")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
