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
    
    # Unregistered tags awaiting user input
    pending_registration: Dict[str, dict] = field(default_factory=dict)
    registration_queue: List[str] = field(default_factory=list)

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

def add_tag_detection(tag_hex: str, tag_data: bytes, db_connection=None):
    """Add new tag detection safely"""
    current_time = datetime.now()
    
    with _shared_data_lock:
        # Initialize variables
        is_in_database = False
        item_name = None
        
        # Update internal active tags
        if tag_hex in shared_rfid_data.active_tags:
            # Existing tag - check if it's already registered
            tag_info = shared_rfid_data.active_tags[tag_hex]
            tag_info['last_seen'] = current_time
            tag_info['count'] += 1
            is_in_database = tag_info.get('is_registered', False)
            item_name = tag_info.get('item_name', None)
        else:
            # New tag - check if it's in database
            if db_connection:
                try:
                    tag_info_db = db_connection.get_tag_info(tag_hex)
                    if tag_info_db:
                        # Tag exists in database - check its status
                        tag_status = tag_info_db.get('status', 'unknown')
                        if tag_status == 'active':
                            is_in_database = True
                            item_name = tag_info_db.get('name') or tag_info_db.get('rf_id')
                        elif tag_status == 'non_active':
                            # Tag is unregistered but exists in database
                            is_in_database = False  # Treat as unregistered for display
                            item_name = f"[UNREGISTERED] {tag_info_db.get('rf_id', 'Unknown')}"
                except Exception as e:
                    print(f"⚠️ Database lookup error: {e}")
            
            # Add to active tags
            shared_rfid_data.active_tags[tag_hex] = {
                'first_seen': current_time,
                'last_seen': current_time,
                'count': 1,
                'data': tag_data,
                'item_name': item_name,
                'is_registered': is_in_database
            }
            
            # If not in database, add to pending registration
            if not is_in_database:
                shared_rfid_data.pending_registration[tag_hex] = {
                    'tag_hex': tag_hex,
                    'tag_data': list(tag_data),  # Convert bytes to list for JSON serialization
                    'first_detected': current_time.strftime('%H:%M:%S'),  # Convert datetime to string
                    'awaiting_input': True,
                    'item_name': ''
                }
                
                # Add to registration queue if not already there
                if tag_hex not in shared_rfid_data.registration_queue:
                    shared_rfid_data.registration_queue.append(tag_hex)
            
            # Add to recent activity
            tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
            
            if is_in_database:
                # Build detailed message for registered tags
                message_parts = [f'Registered tag: {tag_display_id}']
                if db_connection:
                    try:
                        tag_info_db = db_connection.get_tag_info(tag_hex)
                        if tag_info_db:
                            details = []
                            if tag_info_db.get('rf_id'):
                                details.append(f"RFID: {tag_info_db['rf_id']}")
                            if tag_info_db.get('palette_number'):
                                details.append(f"Palette: #{tag_info_db['palette_number']}")
                            if tag_info_db.get('name'):
                                details.append(f"Name: {tag_info_db['name']}")
                            if details:
                                message_parts.append(f"({', '.join(details)})")
                    except Exception as e:
                        print(f"⚠️ Error building activity message: {e}")
                
                message = ' '.join(message_parts)
            else:
                message = f'New tag detected: {tag_display_id} - NEEDS REGISTRATION'
            
            activity = {
                'time': current_time.strftime('%H:%M:%S'),
                'type': 'new_tag' if not is_in_database else 'registered_tag',
                'message': message,
                'tag_id': tag_hex,
                'needs_registration': not is_in_database
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
        
        # Get additional database info for registered tags
        rf_id = None
        palette_number = None
        name = tag_info.get('item_name', None)
        status = 'unregistered'
        
        if is_in_database and db_connection:
            try:
                tag_info_db = db_connection.get_tag_info(tag_hex)
                if tag_info_db:
                    rf_id = tag_info_db.get('rf_id')
                    palette_number = tag_info_db.get('palette_number')
                    name = tag_info_db.get('name')
                    status = tag_info_db.get('status', 'active')
            except Exception as e:
                print(f"⚠️ Error getting additional tag info: {e}")
        
        shared_rfid_data.web_active_tags[tag_hex] = {
            'id': tag_display_id,
            'full_id': tag_hex,
            'first_seen': tag_info['first_seen'].strftime('%H:%M:%S'),
            'last_seen': current_time.strftime('%H:%M:%S.%f')[:-3],
            'count': tag_info['count'],
            'signal_strength': signal_strength,
            'duration': (current_time - tag_info['first_seen']).total_seconds(),
            'rf_id': rf_id,
            'palette_number': palette_number,
            'name': name,
            'status': status,
            'is_registered': tag_info.get('is_registered', False)
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
        # Ensure pending registrations have JSON-serializable data
        pending_regs = {}
        for tag_hex, reg_data in shared_rfid_data.pending_registration.items():
            pending_regs[tag_hex] = {
                'tag_hex': reg_data['tag_hex'],
                'tag_data': list(reg_data.get('tag_data', [])) if isinstance(reg_data.get('tag_data'), bytes) else reg_data.get('tag_data', []),
                'first_detected': reg_data['first_detected'] if isinstance(reg_data['first_detected'], str) else reg_data['first_detected'].strftime('%H:%M:%S'),
                'awaiting_input': reg_data['awaiting_input'],
                'item_name': reg_data['item_name']
            }
        
        return {
            'statistics': {
                'total_scans': shared_rfid_data.total_scans,
                'total_detections': shared_rfid_data.total_detections,
                'active_tag_count': len(shared_rfid_data.active_tags),
                'scan_rate': shared_rfid_data.scan_rate,
                'uptime': shared_rfid_data.uptime,
                'connection_status': shared_rfid_data.connection_status,
                'scanning': shared_rfid_data.scanning,
                'pending_registrations': len(shared_rfid_data.pending_registration)
            },
            'active_tags': dict(shared_rfid_data.web_active_tags),
            'recent_activity': list(shared_rfid_data.recent_activity[:20]),
            'pending_registrations': pending_regs,
            'registration_queue': list(shared_rfid_data.registration_queue)
        }

def get_statistics():
    """Get basic statistics safely"""
    with _shared_data_lock:
        return {
            'active_tags': len(shared_rfid_data.active_tags),
            'total_detections': shared_rfid_data.total_detections,
            'total_scans': shared_rfid_data.total_scans,
            'connected': shared_rfid_data.connected,
            'scanning': shared_rfid_data.scanning,
            'pending_registrations': len(shared_rfid_data.pending_registration)
        }

def get_pending_registrations():
    """Get tags awaiting registration"""
    with _shared_data_lock:
        # Ensure pending registrations have JSON-serializable data
        pending_regs = {}
        for tag_hex, reg_data in shared_rfid_data.pending_registration.items():
            pending_regs[tag_hex] = {
                'tag_hex': reg_data['tag_hex'],
                'tag_data': list(reg_data.get('tag_data', [])) if isinstance(reg_data.get('tag_data'), bytes) else reg_data.get('tag_data', []),
                'first_detected': reg_data['first_detected'] if isinstance(reg_data['first_detected'], str) else reg_data['first_detected'].strftime('%H:%M:%S'),
                'awaiting_input': reg_data['awaiting_input'],
                'item_name': reg_data['item_name']
            }
        
        return {
            'pending_tags': pending_regs,
            'queue': list(shared_rfid_data.registration_queue)
        }

def register_tag(tag_hex: str, name: str = None, db_connection=None, rf_id: str = None, palette_number: int = None):
    """Register a tag with RF ID and optional name and palette number"""
    
    with _shared_data_lock:
        # Check if tag is in pending registration OR if it's a re-registration of non_active tag
        is_pending = tag_hex in shared_rfid_data.pending_registration
        is_reregistration = False
        
        if not is_pending and db_connection:
            # Check if this is a re-registration of a non_active tag
            try:
                existing_tag = db_connection.get_tag_info(tag_hex)
                if existing_tag and existing_tag.get('status') == 'non_active':
                    is_reregistration = True
                    print(f"🔄 Re-registering non_active tag: {tag_hex[:20]}...")
            except Exception as e:
                print(f"⚠️ Error checking tag status for re-registration: {e}")
        
        if is_pending or is_reregistration:
            # Save to database with new schema - rf_id is required
            if db_connection and rf_id:
                try:
                    success = db_connection.add_or_update_tag(
                        tag_id=tag_hex, 
                        rf_id=rf_id, 
                        palette_number=palette_number, 
                        name=name.strip() if name else None
                    )
                    
                    if success:
                        # Build success message
                        message_parts = [f"RFID: {rf_id}"]
                        if palette_number:
                            message_parts.append(f"Palette: #{palette_number}")
                        if name:
                            message_parts.append(f"Name: {name.strip()}")
                        
                        registration_type = "re-registered" if is_reregistration else "registered"
                        print(f"✅ Tag {registration_type}: {tag_hex[:20]}... → {', '.join(message_parts)}")
                        
                        # Update active tags
                        if tag_hex in shared_rfid_data.active_tags:
                            shared_rfid_data.active_tags[tag_hex]['item_name'] = name.strip() if name else rf_id
                            shared_rfid_data.active_tags[tag_hex]['is_registered'] = True
                        
                        # Remove from pending registration if it was pending
                        if is_pending:
                            del shared_rfid_data.pending_registration[tag_hex]
                            
                            # Remove from queue
                            if tag_hex in shared_rfid_data.registration_queue:
                                shared_rfid_data.registration_queue.remove(tag_hex)
                        
                        # Add activity
                        current_time = datetime.now()
                        tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
                        activity_message = f'Tag {registration_type}: {tag_display_id} → {", ".join(message_parts)}'
                        activity_type = 'tag_reregistered' if is_reregistration else 'tag_registered'
                        activity = {
                            'time': current_time.strftime('%H:%M:%S'),
                            'type': activity_type,
                            'message': activity_message,
                            'tag_id': tag_hex
                        }
                        shared_rfid_data.recent_activity.insert(0, activity)
                        
                        return True
                    else:
                        print(f"❌ Database registration failed for tag: {tag_hex[:20]}...")
                except Exception as e:
                    print(f"❌ Error registering tag: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                missing = []
                if not db_connection:
                    missing.append("database connection")
                if not rf_id:
                    missing.append("RFID (RF ID)")
                print(f"❌ Registration failed - missing: {', '.join(missing)}")
        else:
            print(f"❌ Tag not found in pending registrations and not a re-registerable tag: {tag_hex[:20]}...")
        return False

def skip_tag_registration(tag_hex: str):
    """Skip registration for a tag"""
    with _shared_data_lock:
        if tag_hex in shared_rfid_data.pending_registration:
            # Remove from pending registration
            del shared_rfid_data.pending_registration[tag_hex]
            
            # Remove from queue
            if tag_hex in shared_rfid_data.registration_queue:
                shared_rfid_data.registration_queue.remove(tag_hex)
            
            # Add activity
            current_time = datetime.now()
            tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
            activity = {
                'time': current_time.strftime('%H:%M:%S'),
                'type': 'tag_skipped',
                'message': f'Tag registration skipped: {tag_display_id}',
                'tag_id': tag_hex
            }
            shared_rfid_data.recent_activity.insert(0, activity)
            
            return True
        return False

def delete_tag_from_shared_data(tag_hex: str, db_connection=None):
    """Delete a tag from database and remove from shared data"""
    with _shared_data_lock:
        # Delete from database
        success = False
        if db_connection:
            try:
                success = db_connection.delete_tag(tag_hex)
            except Exception as e:
                print(f"❌ Error deleting tag from database: {e}")
                return False
        
        if success:
            # Remove from active tags
            if tag_hex in shared_rfid_data.active_tags:
                del shared_rfid_data.active_tags[tag_hex]
            
            # Remove from web active tags
            if tag_hex in shared_rfid_data.web_active_tags:
                del shared_rfid_data.web_active_tags[tag_hex]
            
            # Remove from pending registration if present
            if tag_hex in shared_rfid_data.pending_registration:
                del shared_rfid_data.pending_registration[tag_hex]
            
            # Remove from registration queue
            if tag_hex in shared_rfid_data.registration_queue:
                shared_rfid_data.registration_queue.remove(tag_hex)
            
            # Add activity
            current_time = datetime.now()
            tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
            activity = {
                'time': current_time.strftime('%H:%M:%S'),
                'type': 'tag_deleted',
                'message': f'Tag deleted from database: {tag_display_id}',
                'tag_id': tag_hex
            }
            shared_rfid_data.recent_activity.insert(0, activity)
            
            return True
        return False

def unregister_tag_from_shared_data(tag_hex: str):
    """Update shared data when a tag is unregistered"""
    with _shared_data_lock:
        # Update active tags status if present
        if tag_hex in shared_rfid_data.active_tags:
            shared_rfid_data.active_tags[tag_hex]['is_registered'] = False
            shared_rfid_data.active_tags[tag_hex]['item_name'] = None
        
        # Update web active tags status if present
        if tag_hex in shared_rfid_data.web_active_tags:
            shared_rfid_data.web_active_tags[tag_hex]['status'] = 'non_active'
            shared_rfid_data.web_active_tags[tag_hex]['is_registered'] = False
            shared_rfid_data.web_active_tags[tag_hex]['name'] = None
        
        # Add activity
        current_time = datetime.now()
        tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
        activity = {
            'time': current_time.strftime('%H:%M:%S'),
            'type': 'tag_unregistered',
            'message': f'Tag unregistered: {tag_display_id} (status: active → non_active)',
            'tag_id': tag_hex
        }
        shared_rfid_data.recent_activity.insert(0, activity)
        
        return True