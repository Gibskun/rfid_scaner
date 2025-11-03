#!/usr/bin/env python3
"""
Test script to demonstrate historical data preservation
Tests the workflow: register -> unregister -> re-register -> check history
"""

from database import get_database
import time

def test_historical_data_preservation():
    """Test that historical data is preserved when re-registering tags"""
    print("🧪 Testing Historical Data Preservation")
    print("=" * 50)
    
    # Get database instance
    db = get_database()
    
    # Test tag ID
    test_tag_id = "0C FC E3 56 A3 28 A7 C3 D8 52 C1 9A"
    
    print(f"📍 Test Tag: {test_tag_id}")
    print()
    
    # Step 1: Register tag for first time
    print("1️⃣ First Registration")
    success = db.add_or_update_tag(
        tag_id=test_tag_id,
        rf_id="TEST001",
        palette_number=100,
        name="First Registration Test"
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Wait a moment to ensure different timestamps
    time.sleep(1)
    
    # Step 2: Unregister the tag
    print("\n2️⃣ Unregistering Tag")
    success = db.unregister_tag(test_tag_id)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Wait a moment
    time.sleep(1)
    
    # Step 3: Re-register with different data
    print("\n3️⃣ Re-registration with Different Data")
    success = db.add_or_update_tag(
        tag_id=test_tag_id,
        rf_id="TEST002",
        palette_number=200,
        name="Second Registration Test"
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Step 4: Check history
    print("\n4️⃣ Checking Complete History")
    history = db.get_tag_history(test_tag_id)
    
    if history:
        print(f"   📊 Found {len(history)} records in history:")
        for i, record in enumerate(history, 1):
            print(f"\n   Record {i}:")
            print(f"      ID: {record['id']}")
            print(f"      RF ID: {record['rf_id']}")
            print(f"      Palette: {record['palette_number']}")
            print(f"      Name: {record['name']}")
            print(f"      Status: {record['status']}")
            print(f"      Created: {record['created']}")
            print(f"      Deleted: {record['deleted']}")
    else:
        print("   ❌ No history found!")
    
    # Step 5: Get current tag info
    print("\n5️⃣ Current Tag Information")
    current_info = db.get_tag_info(test_tag_id)
    
    if current_info:
        print("   📋 Current (most recent) record:")
        print(f"      RF ID: {current_info['rf_id']}")
        print(f"      Palette: {current_info['palette_number']}")
        print(f"      Name: {current_info['name']}")
        print(f"      Status: {current_info['status']}")
    else:
        print("   ❌ No current record found!")
    
    # Step 6: Database statistics
    print("\n6️⃣ Database Statistics")
    stats = db.get_statistics()
    print(f"   Unique Tags: {stats['unique_tags']}")
    print(f"   Total Records: {stats['total_records']}")
    print(f"   Active Tags: {stats['active_tags']}")
    print(f"   Non-Active Tags: {stats['non_active_tags']}")
    print(f"   Can Re-register: {stats['can_reregister']}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    
    # Verify historical preservation
    if len(history) >= 2:
        print("✅ SUCCESS: Historical data preserved - multiple records found!")
        
        # Check if we have both registrations
        rf_ids = [r['rf_id'] for r in history]
        if 'TEST001' in rf_ids and 'TEST002' in rf_ids:
            print("✅ SUCCESS: Both registration records preserved!")
        else:
            print("⚠️  WARNING: Not all expected registration data found")
            
        # Check if we have an unregistered record
        statuses = [r['status'] for r in history]
        if 'non_active' in statuses:
            print("✅ SUCCESS: Unregister record preserved!")
        else:
            print("⚠️  WARNING: Unregister record not found")
            
    else:
        print("❌ FAILED: Historical data not preserved properly")

if __name__ == "__main__":
    test_historical_data_preservation()