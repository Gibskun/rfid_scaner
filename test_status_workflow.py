#!/usr/bin/env python3
"""
Test Status Workflow System
Tests the status cycling functionality without hardware
"""

import sys
import os
from database import get_database
from shared_data import STATUS_WORKFLOW, add_tag_detection

def test_status_workflow():
    """Test the status workflow system"""
    print("🔄 Testing Status Workflow System")
    print("=" * 50)
    
    # Connect to database
    try:
        db = get_database()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Generate a unique test tag hex (simulate a tag)
    import random
    import time
    timestamp = int(time.time()) & 0xFFFFFF  # Keep only 24 bits
    random_part = random.randint(0x1000, 0xFFFF)
    test_tag_hex = f"E20034121314151617181900{timestamp:06X}{random_part:04X}"
    test_tag_data = bytes.fromhex(test_tag_hex.replace(' ', ''))
    
    print(f"\n📋 Test Tag: {test_tag_hex}")
    
    # Always create a fresh test tag
    print("Creating a fresh test tag with 'active' status...")
    
    # Create a test tag
    try:
        # Insert test tag
        success = db.add_or_update_tag(
            tag_id=test_tag_hex,
            rf_id=f"TEST-{test_tag_hex[:8]}",
            palette_number=999,
            name="Test Status Workflow Tag"
        )
        
        if success:
            # Update status to active to start the workflow
            db.update_tag_status(test_tag_hex, 'active')
            print("✅ Test tag created with 'active' status")
        else:
            print("❌ Failed to create test tag")
            return False
    except Exception as e:
        print(f"❌ Error creating test tag: {e}")
        return False
    
    print("\n🔄 Status Workflow Test:")
    print(f"Workflow: {' → '.join(list(STATUS_WORKFLOW.keys()) + ['done'])}")
    
    # Test the workflow by simulating tag detections
    for cycle in range(4):  # Should go through: active → available → on production → done
        print(f"\n--- Cycle {cycle + 1} ---")
        
        # Get current status
        current_info = db.get_tag_info(test_tag_hex)
        if current_info:
            current_status = current_info.get('status', 'unknown')
            print(f"Current status: {current_status}")
            
            # Simulate tag detection (this should trigger status cycling)
            print("Simulating tag detection...")
            add_tag_detection(test_tag_hex, test_tag_data, db)
            
            # Check new status
            updated_info = db.get_tag_info(test_tag_hex)
            if updated_info:
                new_status = updated_info.get('status', 'unknown')
                print(f"New status: {new_status}")
                
                if new_status != current_status:
                    print(f"✅ Status changed: {current_status} → {new_status}")
                else:
                    print(f"ℹ️  Status unchanged: {current_status}")
                    if current_status == 'done':
                        print("✅ Workflow complete (status is 'done')")
                        break
            else:
                print("❌ Failed to get updated tag info")
        else:
            print("❌ Failed to get current tag info")
            break
    
    print("\n🧹 Cleaning up test tag...")
    try:
        # Delete the test tag
        db.delete_tag(test_tag_hex)
        print("✅ Test tag cleaned up")
    except Exception as e:
        print(f"⚠️  Could not clean up test tag: {e}")
    
    print("\n✅ Status workflow test completed!")
    return True

if __name__ == "__main__":
    success = test_status_workflow()
    sys.exit(0 if success else 1)