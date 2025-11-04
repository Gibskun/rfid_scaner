#!/usr/bin/env python3
"""
Test script to verify RFID system status transitions work correctly after fixes
Tests:
1. Database clearing ✓
2. Registration prevention for active/production tags ✓  
3. Status cycling: active → on production
4. Unregister: any status → non_active
5. Re-registration prevention
"""
import sys
import os
sys.path.append('c:\\RFID Config\\Reader')

from database import RFIDDatabase
from shared_data import register_tag, add_tag_detection_with_status_cycling

def test_status_transitions():
    """Test all status transition scenarios"""
    print("="*60)
    print("RFID SYSTEM STATUS TRANSITION TESTS")
    print("="*60)
    
    # Initialize database
    print("\n1. Testing database connection...")
    db = RFIDDatabase()
    print("   Database connected successfully")
    
    # Test data
    test_tag_hex = "E28011700000020A2165A07F"  # Example tag
    test_rf_id = "RF001"
    test_name = "Test Tag"
    test_palette = 123
    
    print(f"\n2. Testing with tag: {test_tag_hex[:20]}...")
    
    # Test 1: Initial registration (should work)
    print("\n--- Test 1: Initial Registration ---")
    
    # First clear any existing data for this tag
    try:
        db.delete_tag_completely(test_tag_hex)
        print("   Cleared any existing test data")
    except:
        print("   No existing data to clear")
    
    # Register the tag first (simulate pending registration workflow)
    print("   Adding tag to pending registration manually...")
    from shared_data import shared_rfid_data, _shared_data_lock
    with _shared_data_lock:
        shared_rfid_data.pending_registration[test_tag_hex] = {
            'tag_hex': test_tag_hex,
            'tag_data': list(bytes(24)),
            'first_detected': '12:00:00',
            'awaiting_input': True,
            'item_name': ''
        }
        if test_tag_hex not in shared_rfid_data.registration_queue:
            shared_rfid_data.registration_queue.append(test_tag_hex)
    
    print("   Attempting initial registration...")
    success = register_tag(test_tag_hex, test_name, db, test_rf_id, test_palette)
    
    if success:
        print("   ✓ Initial registration successful")
        
        # Check status
        tag_info = db.get_tag_info(test_tag_hex)
        if tag_info:
            print(f"   Status: {tag_info.get('status')}")
            print(f"   RF ID: {tag_info.get('rf_id')}")
            print(f"   Name: {tag_info.get('name')}")
    else:
        print("   ✗ Initial registration failed")
        return False
    
    # Test 2: Status cycling (active → on production)
    print("\n--- Test 2: Status Cycling (active → on production) ---")
    print("   Simulating tag detection to trigger status cycling...")
    add_tag_detection_with_status_cycling(test_tag_hex, bytes(24), db)
    
    # Check new status
    tag_info = db.get_tag_info(test_tag_hex)
    if tag_info and tag_info.get('status') == 'on production':
        print("   ✓ Status cycling successful: active → on production")
    else:
        print(f"   ✗ Status cycling failed. Current status: {tag_info.get('status') if tag_info else 'None'}")
        return False
    
    # Test 3: Registration prevention for production tag
    print("\n--- Test 3: Registration Prevention (production tag) ---")
    print("   Attempting to re-register tag with 'on production' status...")
    success = register_tag(test_tag_hex, "New Name", db, "RF002", 999)
    
    if not success:
        print("   ✓ Registration correctly blocked for production tag")
    else:
        print("   ✗ Registration should have been blocked for production tag")
        return False
    
    # Test 4: Unregister (on production → non_active)
    print("\n--- Test 4: Unregistration (on production → non_active) ---")
    print("   Unregistering production tag...")
    success = db.unregister_tag(test_tag_hex)
    
    if success:
        print("   ✓ Unregistration successful")
        
        # Check status
        tag_info = db.get_tag_info(test_tag_hex)
        if tag_info and tag_info.get('status') == 'non_active':
            print("   ✓ Status correctly changed to non_active")
        else:
            print(f"   ✗ Status should be non_active, got: {tag_info.get('status') if tag_info else 'None'}")
            return False
    else:
        print("   ✗ Unregistration failed")
        return False
    
    # Test 5: Re-registration of non_active tag (should work)
    print("\n--- Test 5: Re-registration of non_active tag ---")
    print("   Attempting to re-register non_active tag...")
    success = register_tag(test_tag_hex, "Reregistered Tag", db, "RF003", 555)
    
    if success:
        print("   ✓ Re-registration of non_active tag successful")
        
        # Check status
        tag_info = db.get_tag_info(test_tag_hex)
        if tag_info and tag_info.get('status') == 'active':
            print("   ✓ Status correctly changed back to active")
        else:
            print(f"   ✗ Status should be active, got: {tag_info.get('status') if tag_info else 'None'}")
            return False
    else:
        print("   ✗ Re-registration of non_active tag failed")
        return False
    
    # Test 6: Registration prevention for active tag  
    print("\n--- Test 6: Registration Prevention (active tag) ---")
    print("   Attempting to re-register tag with 'active' status...")
    success = register_tag(test_tag_hex, "Should Fail", db, "RF004", 888)
    
    if not success:
        print("   ✓ Registration correctly blocked for active tag")
    else:
        print("   ✗ Registration should have been blocked for active tag")
        return False
    
    # Clean up test data
    print("\n--- Cleanup ---")
    try:
        db.delete_tag_completely(test_tag_hex)
        print("   Test data cleaned up")
    except Exception as e:
        print(f"   Warning: Could not clean up test data: {e}")
    
    db.close()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        success = test_status_transitions()
        if success:
            print("\n✓ All status transition tests completed successfully")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)