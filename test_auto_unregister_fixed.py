#!/usr/bin/env python3
"""
Test Auto-Unregistration Feature
This script tests the automatic unregistration functionality
"""
import sys
import os
sys.path.append('c:\\RFID Config\\Reader')

from database import RFIDDatabase
from shared_data import add_tag_detection_with_status_cycling, set_page_mode, shared_rfid_data

def test_auto_unregister_functionality():
    """Test auto-unregister functionality for 'on production' tags"""
    print("="*70)
    print("TESTING AUTO-UNREGISTER FUNCTIONALITY")
    print("="*70)
    
    # Initialize database
    print("\n1. Initializing database connection...")
    db = RFIDDatabase()
    
    # Test data - create a tag with 'on production' status
    test_tag_hex = "E28011700000020A2165A07F"
    test_rf_id = "RF999"
    test_name = "Production Test Tag"
    test_palette = 999
    
    print(f"\n2. Setting up test tag with 'on production' status...")
    
    # Clear any existing test data
    try:
        db.delete_tag_completely(test_tag_hex)
        print("   Cleared existing test data")
    except:
        print("   No existing test data to clear")
    
    # Create a tag with 'active' status first
    success = db.add_or_update_tag(
        tag_id=test_tag_hex, 
        rf_id=test_rf_id, 
        palette_number=test_palette, 
        name=test_name
    )
    
    if not success:
        print("   ERROR: Failed to create test tag")
        return False
    
    # Update status to 'on production'
    success = db.update_tag_status(test_tag_hex, 'on production')
    if not success:
        print("   ERROR: Failed to set tag to 'on production' status")
        return False
    
    # Verify initial status
    tag_info = db.get_tag_info(test_tag_hex)
    if tag_info and tag_info.get('status') == 'on production':
        print(f"   Test tag created with status: {tag_info.get('status')}")
        print(f"   Tag details: RFID={tag_info.get('rf_id')}, Name={tag_info.get('name')}")
    else:
        print(f"   ERROR: Expected 'on production' status, got: {tag_info.get('status') if tag_info else 'None'}")
        return False
    
    print(f"\n3. Testing NORMAL mode (should NOT auto-unregister)...")
    
    # Set normal mode
    set_page_mode("normal")
    print(f"   Page mode set to: {shared_rfid_data.current_page_mode}")
    
    # Detect tag in normal mode
    add_tag_detection_with_status_cycling(test_tag_hex, bytes(24), db)
    
    # Check status (should still be 'on production')
    tag_info = db.get_tag_info(test_tag_hex)
    if tag_info and tag_info.get('status') == 'on production':
        print("   NORMAL mode: Tag status unchanged (correct behavior)")
    else:
        print(f"   ERROR: In normal mode, status should remain 'on production', got: {tag_info.get('status') if tag_info else 'None'}")
        return False
    
    print(f"\n4. Testing AUTO-UNREGISTER mode (should auto-unregister)...")
    
    # Set auto-unregister mode (simulating opening unregister page)
    set_page_mode("auto_unregister")
    print(f"   Page mode set to: {shared_rfid_data.current_page_mode}")
    
    # Detect tag in auto-unregister mode
    print("   Detecting tag in auto-unregister mode...")
    add_tag_detection_with_status_cycling(test_tag_hex, bytes(24), db)
    
    # Check status (should now be 'non_active')
    tag_info = db.get_tag_info(test_tag_hex)
    if tag_info and tag_info.get('status') == 'non_active':
        print("   AUTO-UNREGISTER mode: Tag status changed to non_active (SUCCESS!)")
        print(f"   Final status: {tag_info.get('status')}")
        
        # Check activity log
        if shared_rfid_data.recent_activity:
            latest_activity = shared_rfid_data.recent_activity[0]
            if latest_activity.get('type') == 'tag_auto_unregistered':
                print("   Auto-unregister activity logged correctly")
                print(f"   Activity: {latest_activity.get('message')}")
            else:
                print("   WARNING: Expected auto-unregister activity not found")
    else:
        print(f"   ERROR: Expected 'non_active' status after auto-unregister, got: {tag_info.get('status') if tag_info else 'None'}")
        return False
    
    print(f"\n5. Testing with existing active tags...")
    
    # Reset tag to 'on production' status
    db.add_or_update_tag(tag_id=test_tag_hex, rf_id=test_rf_id, palette_number=test_palette, name=test_name)
    db.update_tag_status(test_tag_hex, 'on production')
    
    # Add tag to active_tags first (simulating it was detected before)
    from datetime import datetime
    current_time = datetime.now()
    shared_rfid_data.active_tags[test_tag_hex] = {
        'first_seen': current_time,
        'last_seen': current_time,
        'count': 1,
        'data': bytes(24),
        'item_name': test_name,
        'is_registered': True,
        'status_changed': False,
        'old_status': None,
        'new_status': None
    }
    
    # Detect existing tag in auto-unregister mode
    print("   Detecting existing active tag in auto-unregister mode...")
    add_tag_detection_with_status_cycling(test_tag_hex, bytes(24), db)
    
    # Check status (should be 'non_active')
    tag_info = db.get_tag_info(test_tag_hex)
    if tag_info and tag_info.get('status') == 'non_active':
        print("   AUTO-UNREGISTER mode: Existing tag also changed to non_active (SUCCESS!)")
    else:
        print(f"   ERROR: Expected 'non_active' status for existing tag, got: {tag_info.get('status') if tag_info else 'None'}")
        return False
    
    # Clean up
    print(f"\n6. Cleaning up test data...")
    try:
        db.delete_tag_completely(test_tag_hex)
        if test_tag_hex in shared_rfid_data.active_tags:
            del shared_rfid_data.active_tags[test_tag_hex]
        print("   Test data cleaned up")
    except Exception as e:
        print(f"   Warning: Could not clean up test data: {e}")
    
    # Reset to normal mode
    set_page_mode("normal")
    
    db.close()
    
    print("\n" + "="*70)
    print("ALL AUTO-UNREGISTER TESTS PASSED!")
    print("The unregister page will now automatically change detected tags to non_active")
    print("="*70)
    return True

if __name__ == "__main__":
    try:
        success = test_auto_unregister_functionality()
        if success:
            print("\nAuto-unregister functionality is working correctly!")
            sys.exit(0)
        else:
            print("\nAuto-unregister tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)