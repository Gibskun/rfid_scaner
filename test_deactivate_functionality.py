#!/usr/bin/env python3
"""
Test Deactivate Functionality
Tests the deactivate function that changes any status to non_active with description
"""

import sys
import os
from database import get_database

def test_deactivate_functionality():
    """Test the deactivate functionality"""
    print("🚫 Testing Deactivate Functionality")
    print("=" * 50)
    
    # Connect to database
    try:
        db = get_database()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test tag hex (simulate a tag)
    import random
    import time
    timestamp = int(time.time()) & 0xFFFFFF
    random_part = random.randint(0x1000, 0xFFFF)
    test_tag_hex = f"E2003412131415161718190{timestamp:06X}{random_part:04X}"
    
    print(f"\n📋 Test Tag: {test_tag_hex}")
    
    # Test deactivation for each status
    test_statuses = ['active', 'available', 'on production', 'done']
    
    for test_status in test_statuses:
        print(f"\n--- Testing deactivation from status: {test_status} ---")
        
        # Create a test tag with specific status
        try:
            # Insert test tag
            success = db.add_or_update_tag(
                tag_id=test_tag_hex,
                rf_id=f"TEST-DEACT-{test_tag_hex[:8]}",
                palette_number=888,
                name=f"Test Deactivate Tag ({test_status})"
            )
            
            if success:
                # Update status to the test status
                db.update_tag_status(test_tag_hex, test_status)
                print(f"✅ Test tag created with '{test_status}' status")
                
                # Check current status
                current_info = db.get_tag_info(test_tag_hex)
                if current_info:
                    current_status = current_info.get('status', 'unknown')
                    print(f"📊 Current status: {current_status}")
                    
                    # Test deactivation
                    print("🚫 Testing deactivation...")
                    deactivate_success = db.deactivate_tag(test_tag_hex)
                    
                    if deactivate_success:
                        # Check new status
                        updated_info = db.get_tag_info(test_tag_hex)
                        if updated_info:
                            new_status = updated_info.get('status', 'unknown')
                            description = updated_info.get('description', 'No description')
                            deleted = updated_info.get('deleted')
                            
                            print(f"✅ Deactivation successful!")
                            print(f"   📊 Status: {current_status} → {new_status}")
                            print(f"   📝 Description: {description}")
                            print(f"   🕒 Deleted timestamp: {deleted}")
                            
                            # Verify status is non_active
                            if new_status == 'non_active':
                                print(f"✅ Status correctly changed to non_active")
                            else:
                                print(f"❌ Status is {new_status}, expected non_active")
                                return False
                            
                            # Verify description contains old status
                            if test_status in description:
                                print(f"✅ Description correctly contains old status")
                            else:
                                print(f"❌ Description doesn't contain old status: {description}")
                                return False
                        else:
                            print("❌ Failed to get updated tag info")
                            return False
                    else:
                        print("❌ Deactivation failed")
                        return False
                else:
                    print("❌ Failed to get current tag info")
                    return False
            else:
                print("❌ Failed to create test tag")
                return False
        except Exception as e:
            print(f"❌ Error testing status {test_status}: {e}")
            return False
    
    print("\n--- Testing deactivation of already non_active tag ---")
    
    # Test deactivating already non_active tag
    deactivate_again = db.deactivate_tag(test_tag_hex)
    if not deactivate_again:
        print("✅ Correctly rejected deactivation of already non_active tag")
    else:
        print("❌ Should not have succeeded deactivating already non_active tag")
    
    print("\n🧹 Cleaning up test tag...")
    try:
        # Delete the test tag
        db.delete_tag(test_tag_hex)
        print("✅ Test tag cleaned up")
    except Exception as e:
        print(f"⚠️  Could not clean up test tag: {e}")
    
    print("\n✅ Deactivate functionality test completed!")
    return True

if __name__ == "__main__":
    success = test_deactivate_functionality()
    sys.exit(0 if success else 1)