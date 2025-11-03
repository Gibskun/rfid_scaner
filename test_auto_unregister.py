#!/usr/bin/env python3
"""
Test Auto-Unregistration Feature
This script tests the automatic unregistration functionality
"""

from database import get_database
from shared_data import add_tag_detection
import time

def test_auto_unregistration():
    """Test the auto-unregistration feature"""
    print("🧪 Testing Auto-Unregistration Feature")
    print("=" * 50)
    
    # Connect to database
    try:
        db = get_database()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Create a test tag
    test_tag_hex = "E2 00 34 12 01 70 14 01 23 45 67 89"
    test_tag_bytes = bytes([0xE2, 0x00, 0x34, 0x12, 0x01, 0x70, 0x14, 0x01, 0x23, 0x45, 0x67, 0x89])
    
    print(f"🏷️  Test Tag: {test_tag_hex}")
    
    # Step 1: Register the tag
    print("\n📝 Step 1: Registering test tag...")
    success = db.add_or_update_tag(
        tag_id=test_tag_hex,
        rf_id="TEST001",
        palette_number=123,
        name="Test Tag for Auto-Unregistration"
    )
    
    if success:
        print("✅ Test tag registered successfully")
        
        # Verify it's active
        tag_info = db.get_tag_info(test_tag_hex)
        if tag_info and tag_info.get('status') == 'active':
            print(f"✅ Tag status confirmed as 'active'")
            print(f"   📋 RFID: {tag_info['rf_id']}")
            print(f"   📦 Palette: {tag_info['palette_number']}")
            print(f"   🏷️  Name: {tag_info['name']}")
        else:
            print("❌ Tag registration failed or status not active")
            return
    else:
        print("❌ Failed to register test tag")
        return
    
    # Step 2: Test auto-unregistration
    print("\n🤖 Step 2: Testing auto-unregistration...")
    print("Simulating tag detection (this should trigger auto-unregistration)...")
    
    # Simulate tag detection - this should trigger auto-unregistration
    add_tag_detection(test_tag_hex, test_tag_bytes, db)
    
    # Check if tag was auto-unregistered
    print("\n🔍 Step 3: Verifying auto-unregistration...")
    time.sleep(0.5)  # Give it a moment
    
    tag_info_after = db.get_tag_info(test_tag_hex)
    if tag_info_after:
        final_status = tag_info_after.get('status', 'unknown')
        print(f"📊 Final tag status: {final_status}")
        
        if final_status == 'non_active':
            print("✅ AUTO-UNREGISTRATION SUCCESSFUL!")
            print("🎉 The tag was automatically unregistered upon detection!")
            
            if tag_info_after.get('deleted'):
                print(f"📅 Unregistered timestamp: {tag_info_after['deleted']}")
        else:
            print("❌ Auto-unregistration failed - tag is still active")
    else:
        print("❌ Could not retrieve tag info after test")
    
    print("\n🧹 Cleanup: Removing test tag from database...")
    try:
        db.delete_tag(test_tag_hex)
        print("✅ Test tag cleaned up")
    except:
        print("⚠️  Could not clean up test tag")
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    test_auto_unregistration()