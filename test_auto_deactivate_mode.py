#!/usr/bin/env python3
"""
Test Auto-Deactivation Mode Implementation
"""

from shared_data import set_page_mode, get_page_mode, shared_rfid_data, add_tag_detection
from database import get_database
import time

def test_mode_switching():
    """Test that mode switching works correctly"""
    print("🧪 Testing mode switching...")
    
    # Test initial mode
    initial_mode = get_page_mode()
    print(f"   Initial mode: {initial_mode}")
    
    # Test setting auto-deactivation mode
    set_page_mode("auto_deactivate")
    current_mode = get_page_mode()
    print(f"   After setting auto_deactivate: {current_mode}")
    assert current_mode == "auto_deactivate", "Mode should be auto_deactivate"
    
    # Test setting normal mode
    set_page_mode("normal")
    current_mode = get_page_mode()
    print(f"   After setting normal: {current_mode}")
    assert current_mode == "normal", "Mode should be normal"
    
    print("✅ Mode switching test passed!")

def test_auto_deactivation_simulation():
    """Test auto-deactivation logic with a simulated tag"""
    print("\n🧪 Testing auto-deactivation logic...")
    
    try:
        # Get database connection
        db = get_database()
        print(f"   Database connected: {db}")
        
        # Set auto-deactivation mode
        set_page_mode("auto_deactivate")
        print(f"   Mode set to: {get_page_mode()}")
        
        # Check if we have any registered tags in the database to test with
        all_tags = db.get_all_tags(limit=5, include_inactive=False)
        if not all_tags:
            print("   ⚠️ No registered tags found in database to test with")
            print("   Creating a test tag for simulation...")
            
            # Create a test tag
            test_tag_hex = "E200001A75123456789ABCDE"
            test_rf_id = "TEST001"
            test_name = "Test Auto-Deactivation Tag"
            test_palette = 999
            
            success = db.add_or_update_tag(test_tag_hex, test_rf_id, test_palette, test_name)
            if success:
                print(f"   Test tag created: {test_rf_id}")
                # Set it to 'available' status for testing
                db.update_tag_status(test_tag_hex, 'available')
                print(f"   Test tag status set to 'available'")
                
                # Now simulate detection
                print(f"   Simulating detection of tag: {test_tag_hex[:20]}...")
                
                # Check tag status before
                tag_info_before = db.get_tag_info(test_tag_hex)
                print(f"   Status before detection: {tag_info_before.get('status', 'unknown')}")
                
                # Simulate tag detection with auto-deactivation
                add_tag_detection(test_tag_hex, bytes.fromhex(test_tag_hex), db)
                
                # Check tag status after
                time.sleep(0.1)  # Small delay to ensure processing
                tag_info_after = db.get_tag_info(test_tag_hex)
                print(f"   Status after detection: {tag_info_after.get('status', 'unknown')}")
                
                if tag_info_after.get('status') == 'non_active':
                    print("✅ Auto-deactivation test PASSED!")
                    print(f"   Description: {tag_info_after.get('description', 'N/A')}")
                else:
                    print("❌ Auto-deactivation test FAILED!")
                    print("   Tag was not automatically deactivated")
            else:
                print("   ❌ Failed to create test tag")
        else:
            print(f"   Found {len(all_tags)} registered tags in database")
            # Find a tag that's not non_active
            test_tag = None
            for tag in all_tags:
                if tag.get('status') != 'non_active':
                    test_tag = tag
                    break
            
            if test_tag:
                tag_hex = test_tag['tag_id']
                print(f"   Using existing tag for test: {tag_hex[:20]}...")
                print(f"   Current status: {test_tag.get('status', 'unknown')}")
                
                # Simulate tag detection
                print(f"   Simulating detection...")
                add_tag_detection(tag_hex, bytes.fromhex(tag_hex), db)
                
                # Check status after
                time.sleep(0.1)
                tag_info_after = db.get_tag_info(tag_hex)
                print(f"   Status after detection: {tag_info_after.get('status', 'unknown')}")
                
                if tag_info_after.get('status') == 'non_active':
                    print("✅ Auto-deactivation test PASSED!")
                    print(f"   Description: {tag_info_after.get('description', 'N/A')}")
                else:
                    print("❌ Auto-deactivation test FAILED!")
            else:
                print("   ⚠️ All tags are already non_active - cannot test auto-deactivation")
        
        # Reset to normal mode
        set_page_mode("normal")
        print(f"   Mode reset to: {get_page_mode()}")
        
    except Exception as e:
        print(f"   ❌ Database test error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 Testing Auto-Deactivation Mode Implementation")
    print("=" * 50)
    
    test_mode_switching()
    test_auto_deactivation_simulation()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()