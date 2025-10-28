#!/usr/bin/env python3
"""
Shared RFID Data System
Provides synchronized data sharing between terminal scanner and web interface
"""

import threading
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, field

# Global shared data structure
_shared_data_lock = threading.RLock()

@dataclass
class SharedRFIDData:
    """Shared data structure for RFID system"""
    # Scanner state
    connected: bool = False
    scanning: bool = False
    connection_status: str = "Disconnected"
    
    # Tag data
    active_tags: Dict[str, dict] = field(default_factory=dict)
    recent_activity: List[dict] = field(default_factory=list)
    
    # Statistics
    total_scans: int = 0
    total_detections: int = 0
    scan_rate: float = 0.0
    start_time: float = 0.0
    uptime: float = 0.0
    
    # Web-specific data
    web_active_tags: Dict[str, dict] = field(default_factory=dict)

# Global shared data instance
shared_rfid_data = SharedRFIDData()

def update_connection_status(connected: bool, status: str = ""):
    """Update connection status safely"""
    with _shared_data_lock:
        shared_rfid_data.connected = connected
        if status:
            shared_rfid_data.connection_status = status
        else:
            shared_rfid_data.connection_status = "Connected" if connected else "Disconnected"

def update_scanning_status(scanning: bool):
    """Update scanning status safely"""
    with _shared_data_lock:
        shared_rfid_data.scanning = scanning
        if scanning and shared_rfid_data.start_time == 0:
            shared_rfid_data.start_time = time.time()

def add_tag_detection(tag_hex: str, tag_data: bytes):
    """Add new tag detection safely"""
    current_time = datetime.now()
    
    with _shared_data_lock:
        # Update internal active tags
        if tag_hex in shared_rfid_data.active_tags:
            # Existing tag
            tag_info = shared_rfid_data.active_tags[tag_hex]
            tag_info['last_seen'] = current_time
            tag_info['count'] += 1
        else:
            # New tag
            shared_rfid_data.active_tags[tag_hex] = {
                'first_seen': current_time,
                'last_seen': current_time,
                'count': 1,
                'data': tag_data
            }
            
            # Add to recent activity
            tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
            activity = {
                'time': current_time.strftime('%H:%M:%S'),
                'type': 'new_tag',
                'message': f'New tag detected: {tag_display_id}',
                'tag_id': tag_hex
            }
            shared_rfid_data.recent_activity.insert(0, activity)
            
            # Keep only last 50 activities
            if len(shared_rfid_data.recent_activity) > 50:
                shared_rfid_data.recent_activity = shared_rfid_data.recent_activity[:50]
        
        # Update web-friendly data
        tag_info = shared_rfid_data.active_tags[tag_hex]
        tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
        
        # Calculate signal strength
        if tag_info['count'] > 1:
            detection_rate = tag_info['count'] / max(1, (current_time - tag_info['first_seen']).total_seconds())
            signal_strength = "Strong" if detection_rate > 2 else "Medium" if detection_rate > 0.5 else "Weak"
        else:
            signal_strength = "New"
        
        shared_rfid_data.web_active_tags[tag_hex] = {
            'id': tag_display_id,
            'full_id': tag_hex,
            'first_seen': tag_info['first_seen'].strftime('%H:%M:%S'),
            'last_seen': current_time.strftime('%H:%M:%S.%f')[:-3],
            'count': tag_info['count'],
            'signal_strength': signal_strength,
            'duration': (current_time - tag_info['first_seen']).total_seconds()
        }
        
        shared_rfid_data.total_detections += 1

def cleanup_old_tags(cleanup_interval: float = 5.0):
    """Remove old tags safely"""
    current_time = datetime.now()
    
    with _shared_data_lock:
        to_remove = []
        
        for tag_id, tag_info in shared_rfid_data.active_tags.items():
            time_since_last = (current_time - tag_info['last_seen']).total_seconds()
            if time_since_last > cleanup_interval:
                to_remove.append(tag_id)
                
                # Add removal activity
                tag_display_id = tag_id[:20] + "..." if len(tag_id) > 20 else tag_id
                activity = {
                    'time': current_time.strftime('%H:%M:%S'),
                    'type': 'tag_removed',
                    'message': f'Tag removed: {tag_display_id} (inactive for {time_since_last:.1f}s)',
                    'tag_id': tag_id
                }
                shared_rfid_data.recent_activity.insert(0, activity)
        
        # Remove from both active and web data
        for tag_id in to_remove:
            if tag_id in shared_rfid_data.active_tags:
                del shared_rfid_data.active_tags[tag_id]
            if tag_id in shared_rfid_data.web_active_tags:
                del shared_rfid_data.web_active_tags[tag_id]
        
        return to_remove

def update_scan_statistics(scan_count: int):
    """Update scanning statistics safely"""
    with _shared_data_lock:
        shared_rfid_data.total_scans = scan_count
        
        # Calculate scan rate and uptime
        if shared_rfid_data.start_time > 0:
            current_time = time.time()
            elapsed = current_time - shared_rfid_data.start_time
            shared_rfid_data.uptime = elapsed
            shared_rfid_data.scan_rate = scan_count / elapsed if elapsed > 0 else 0

def get_web_data():
    """Get web-friendly data safely"""
    with _shared_data_lock:
        return {
            'statistics': {
                'total_scans': shared_rfid_data.total_scans,
                'total_detections': shared_rfid_data.total_detections,
                'active_tag_count': len(shared_rfid_data.active_tags),
                'scan_rate': shared_rfid_data.scan_rate,
                'uptime': shared_rfid_data.uptime,
                'connection_status': shared_rfid_data.connection_status,
                'scanning': shared_rfid_data.scanning
            },
            'active_tags': dict(shared_rfid_data.web_active_tags),
            'recent_activity': list(shared_rfid_data.recent_activity[:20])
        }

def get_statistics():
    """Get basic statistics safely"""
    with _shared_data_lock:
        return {
            'active_tags': len(shared_rfid_data.active_tags),
            'total_detections': shared_rfid_data.total_detections,
            'total_scans': shared_rfid_data.total_scans,
            'connected': shared_rfid_data.connected,
            'scanning': shared_rfid_data.scanning
        }