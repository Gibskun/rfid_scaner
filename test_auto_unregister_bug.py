"""
Test Auto-Unregister Status Description Bug Fix
Tests that active tags show correct status in description when auto-unregistered
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import shared_data
import database

def test_auto_unregister_status_description():
    """Test that auto-unregister shows correct status descriptions"""
    print("🔄 Testing Auto-Unregister Status Description Bug Fix")
    print("="*60)
    
    # Initialize database
    try:
        db = database.RFIDDatabase()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Test tag
    test_tag_hex = "E28011700000020A2165ABCD"
    test_rf_id = "RF999"
    test_name = "Auto-Unregister Test Tag"
    test_palette = 999
    
    print(f"\n📋 Test Tag: {test_tag_hex[:20]}...")
    
    # Clean up any existing data
    try:
        cursor = db.connection_pool.getconn().cursor()
        cursor.execute("DELETE FROM rfid_tags WHERE tag_id = %s", (test_tag_hex,))
        cursor.connection.commit()
        db.connection_pool.putconn(cursor.connection)
        print("   Cleared any existing test data")
    except:
        pass
    
    # Test 1: Create active tag
    print("\n--- Test 1: Creating Active Tag ---")
    try:
        db.add_or_update_tag(
            tag_id=test_tag_hex,
            rf_id=test_rf_id,
            palette_number=test_palette,
            name=test_name
        )
        db.update_tag_status(test_tag_hex, 'active')
        print("✅ Created active tag")
        
        # Verify status
        tag_info = db.get_tag_info(test_tag_hex)
        current_status = tag_info.get('status')
        print(f"   Status: {current_status}")
        
        if current_status != 'active':
            print("❌ Test failed: Tag should be 'active'")
            return
            
    except Exception as e:
        print(f"❌ Failed to create test tag: {e}")
        return
    
    # Test 2: Set auto-unregister mode and detect tag
    print("\n--- Test 2: Auto-Unregister with Status Description Check ---")
    try:
        # Set auto-unregister mode
        shared_data.shared_rfid_data.current_page_mode = "auto_unregister"
        print("✅ Set mode to auto_unregister")
        
        # Store original status before detection
        original_tag_info = db.get_tag_info(test_tag_hex)
        original_status = original_tag_info.get('status')
        print(f"   Original status before detection: {original_status}")
        
        # Simulate tag detection (this should NOT cycle status in auto-unregister mode)
        tag_data = bytes.fromhex(test_tag_hex.replace(' ', ''))
        print("   Simulating tag detection in auto-unregister mode...")
        
        # This should call auto-unregister logic
        shared_data.add_tag_detection_with_status_cycling(test_tag_hex, tag_data, db)
        
        # Check if tag was auto-unregistered
        updated_tag_info = db.get_tag_info(test_tag_hex)
        updated_status = updated_tag_info.get('status')
        print(f"   Status after detection: {updated_status}")
        
        if updated_status == 'non_active':
            print("✅ Tag was auto-unregistered successfully")
            
            # Check the description in the database
            cursor = db.connection_pool.getconn().cursor()
            cursor.execute(
                "SELECT description FROM rfid_tags WHERE tag_id = %s ORDER BY created DESC LIMIT 1",
                (test_tag_hex,)
            )
            result = cursor.fetchone()
            db.connection_pool.putconn(cursor.connection)
            
            if result:
                description = result[0]
                print(f"   Description: {description}")
                
                # Check if description contains correct original status
                if "Deactivated from status: active" in description:
                    print("✅ CORRECT: Description shows original 'active' status")
                    print("✅ BUG FIXED: Auto-unregister preserves original status")
                elif "Deactivated from status: on production" in description:
                    print("❌ BUG STILL EXISTS: Description shows cycled 'on production' status")
                    print("❌ This means status cycling happened before auto-unregister")
                else:
                    print(f"❓ Unexpected description format: {description}")
            else:
                print("❌ Could not find description in database")
        else:
            print(f"❌ Tag was not auto-unregistered (status: {updated_status})")
            
    except Exception as e:
        print(f"❌ Auto-unregister test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Reset mode
    print("\n--- Test 3: Cleanup ---")
    try:
        shared_data.shared_rfid_data.current_page_mode = "registration"
        print("✅ Reset mode to registration")
        
        # Clean up test data
        cursor = db.connection_pool.getconn().cursor()
        cursor.execute("DELETE FROM rfid_tags WHERE tag_id = %s", (test_tag_hex,))
        db.connection_pool.getconn().commit()
        db.connection_pool.putconn(cursor.connection)
        print("✅ Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("\n" + "="*60)
    print("🔍 Auto-Unregister Status Description Test Complete")

if __name__ == "__main__":
    test_auto_unregister_status_description()