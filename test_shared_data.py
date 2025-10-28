#!/usr/bin/env python3
"""
Test script to verify shared data functionality
"""

from shared_data import get_web_data, update_scan_statistics, update_connection_status
import json

def test_shared_data():
    """Test shared data functionality"""
    print("🧪 Testing Shared Data System")
    print("=" * 50)
    
    # Update connection status
    update_connection_status('Connected')
    
    # Update some scan statistics
    update_scan_statistics(100)
    
    # Get web data
    data = get_web_data()
    
    print("📊 Current shared data:")
    print(json.dumps(data, indent=2, default=str))
    
    print("\n✅ Field mapping verification:")
    stats = data.get('statistics', {})
    print(f"- total_scans: {stats.get('total_scans', 'MISSING')}")
    print(f"- total_detections: {stats.get('total_detections', 'MISSING')}")
    print(f"- active_tag_count: {stats.get('active_tag_count', 'MISSING')}")
    print(f"- scan_rate: {stats.get('scan_rate', 'MISSING')}")
    print(f"- connection_status: {stats.get('connection_status', 'MISSING')}")
    
    print(f"\n🏷️  active_tags: {len(data.get('active_tags', {}))}")
    print(f"📝 recent_activity: {len(data.get('recent_activity', []))}")

if __name__ == "__main__":
    test_shared_data()