#!/usr/bin/env python3
"""
RFID Web Interface - Real-time monitoring dashboard
Reads from shared RFID data and broadcasts to web clients
Includes database integration for tag management
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
from shared_data import get_web_data, get_statistics, get_pending_registrations, register_tag, skip_tag_registration, set_page_mode, get_page_mode, set_scanning_enabled, is_scanning_enabled, get_active_page
from database import get_database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rfid_monitor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database instance
db = None

# Import database function
from database import get_database

def set_database_instance(database_instance):
    """Set the database instance from external code"""
    global db
    db = database_instance
    print(f"✅ Web interface: Database instance set externally: {db}")

# Global broadcasting control
update_thread = None
broadcasting = False
last_broadcast_data = None

def initialize_database():
    """Initialize database connection"""
    global db
    try:
        print("🔍 DEBUG: Attempting to get database connection...")
        db = get_database()
        print(f"🔍 DEBUG: Database instance: {db}")
        print("✅ Web interface: Database connected")
        return True
    except Exception as e:
        print(f"⚠️  Web interface: Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        db = None
        return False

def broadcast_updates():
    """Continuously broadcast updates from shared data to web clients"""
    global last_broadcast_data, broadcasting
    
    while broadcasting:
        try:
            # Get current data from shared system
            current_data = get_web_data()
            
            # Get statistics for comparison and logging
            new_stats = current_data.get('statistics', {})
            
            # Only broadcast if data has changed significantly
            should_broadcast = False
            
            if last_broadcast_data is None:
                should_broadcast = True
            else:
                # Check if statistics changed
                old_stats = last_broadcast_data.get('statistics', {})
                
                if (old_stats.get('total_scans', 0) != new_stats.get('total_scans', 0) or
                    old_stats.get('total_detections', 0) != new_stats.get('total_detections', 0) or
                    old_stats.get('active_tag_count', 0) != new_stats.get('active_tag_count', 0) or
                    old_stats.get('connection_status', '') != new_stats.get('connection_status', '')):
                    should_broadcast = True
                
                # Check if tags changed
                if (len(current_data.get('active_tags', {})) != len(last_broadcast_data.get('active_tags', {})) or
                    current_data.get('active_tags', {}) != last_broadcast_data.get('active_tags', {})):
                    should_broadcast = True
                
                # Check if recent activity changed
                if (len(current_data.get('recent_activity', [])) != len(last_broadcast_data.get('recent_activity', []))):
                    should_broadcast = True
            
            if should_broadcast:
                socketio.emit('status_update', current_data)
                last_broadcast_data = current_data.copy()
                print(f"📡 Broadcasted update: {new_stats.get('total_scans', 0)} scans, {new_stats.get('active_tag_count', 0)} tags")
            
            # Broadcast every 1 second for real-time updates
            time.sleep(1.0)
            
        except Exception as e:
            print(f"❌ Broadcast error: {e}")
            time.sleep(2)

def start_broadcasting():
    """Start the broadcasting thread"""
    global update_thread, broadcasting
    
    if not broadcasting:
        broadcasting = True
        update_thread = threading.Thread(target=broadcast_updates)
        update_thread.daemon = True
        update_thread.start()
        print("🌐 Started real-time data broadcasting")

def stop_broadcasting():
    """Stop the broadcasting thread"""
    global broadcasting
    broadcasting = False
    print("🛑 Stopped real-time data broadcasting")

@app.route('/')
def index():
    """Main system dashboard - entry point"""
    # Reset to normal mode and DISABLE scanning when on main dashboard
    set_page_mode("normal")
    set_scanning_enabled(False, "main")
    return render_template('main_dashboard.html')

@app.route('/register')
def register_dashboard():
    """RFID registration dashboard"""
    # Set normal mode and ENABLE scanning for registration
    set_page_mode("normal")
    set_scanning_enabled(True, "register")
    return render_template('dashboard.html')

@app.route('/delete')
def delete_dashboard():
    """RFID tag deletion dashboard"""
    # Set normal mode and ENABLE scanning for deletion
    set_page_mode("normal")
    set_scanning_enabled(True, "delete")
    return render_template('delete_dashboard.html')

@app.route('/production')
def production_dashboard():
    """RFID On Production dashboard - changes active tags to on production"""
    # Set normal mode and ENABLE scanning for production workflow
    set_page_mode("normal")
    set_scanning_enabled(True, "production")
    return render_template('production_dashboard.html')

@app.route('/unregister')
def unregister_dashboard():
    """RFID Tag Unregister dashboard - automatically changes all detected tags to non_active"""
    # Set automatic unregister mode and ENABLE scanning for unregistration
    set_page_mode("auto_unregister")
    set_scanning_enabled(True, "unregister")
    return render_template('unregister_dashboard.html')

@app.route('/frequency')
def frequency_dashboard():
    """RFID tag frequency analysis dashboard - displays detection frequency of tags"""
    # Set normal mode and ENABLE scanning for frequency analysis
    set_page_mode("normal")
    set_scanning_enabled(True, "frequency")
    return render_template('frequency_dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    return jsonify(get_web_data())

@app.route('/api/mode')
def api_mode():
    """API endpoint for current page mode"""
    return jsonify({'mode': get_page_mode()})

@app.route('/api/scanning-status')
def api_scanning_status():
    """API endpoint for current scanning status"""
    return jsonify({
        'scanning_enabled': is_scanning_enabled(),
        'active_page': get_active_page(),
        'page_mode': get_page_mode()
    })

@app.route('/api/database/stats')
def api_database_stats():
    """Get database statistics"""
    if db:
        try:
            stats = db.get_statistics()
            return jsonify({'success': True, 'data': stats})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Database not connected'})

@app.route('/api/database/tags')
def api_database_tags():
    """Get all tags from database"""
    if db:
        try:
            limit = int(request.args.get('limit', 100))
            offset = int(request.args.get('offset', 0))
            include_inactive = request.args.get('include_inactive', 'true').lower() == 'true'
            tags = db.get_all_tags(limit=limit, offset=offset, include_inactive=include_inactive)
            return jsonify({'success': True, 'data': tags})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Database not connected'})

@app.route('/api/database/non-active-tags')
def api_database_non_active_tags():
    """Get all non-active tags that can be re-registered"""
    if db:
        try:
            # Get most recent non_active records for each tag
            conn = db.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT ON (tag_id) 
                       id, tag_id, rf_id, palette_number, name, status, created, deleted
                FROM rfid_tags
                WHERE status = 'non_active'
                ORDER BY tag_id, created DESC
                LIMIT 50
            """)
            
            tags = []
            for row in cursor.fetchall():
                tags.append({
                    'id': row[0],
                    'tag_id': row[1],
                    'rf_id': row[2],
                    'palette_number': row[3],
                    'name': row[4],
                    'status': row[5],
                    'created': row[6].isoformat() if row[6] else None,
                    'deleted': row[7].isoformat() if row[7] else None
                })
            
            db.connection_pool.putconn(conn)
            return jsonify({'success': True, 'data': tags})
            
        except Exception as e:
            if 'conn' in locals():
                db.connection_pool.putconn(conn)
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Database not connected'})

@app.route('/api/tag-history/<path:tag_id>')
def api_tag_history(tag_id):
    """Get complete history for a specific tag"""
    if db:
        try:
            history = db.get_tag_history(tag_id)
            # Convert datetime objects to strings
            for record in history:
                if record.get('created'):
                    record['created'] = record['created'].isoformat()
                if record.get('deleted'):
                    record['deleted'] = record['deleted'].isoformat()
            
            return jsonify({'success': True, 'data': history, 'total_records': len(history)})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Database not connected'})

@app.route('/api/database/search')
def api_database_search():
    """Search tags in database"""
    if db:
        try:
            search_term = request.args.get('q', '')
            if search_term:
                results = db.search_tags(search_term)
                return jsonify({'success': True, 'data': results})
            else:
                return jsonify({'success': False, 'error': 'No search term provided'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Database not connected'})

@app.route('/api/tag/<path:tag_id>')
def api_tag_info(tag_id):
    """Get specific tag information"""
    if db:
        try:
            tag_info = db.get_tag_info(tag_id)
            if tag_info:
                # Convert datetime objects to strings
                if tag_info.get('created'):
                    tag_info['created'] = tag_info['created'].isoformat()
                if tag_info.get('deleted'):
                    tag_info['deleted'] = tag_info['deleted'].isoformat()
                return jsonify({'success': True, 'data': tag_info})
            else:
                return jsonify({'success': False, 'error': 'Tag not found'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Database not connected'})

@app.route('/api/pending-registrations')
def api_pending_registrations():
    """Get tags awaiting registration"""
    try:
        data = get_pending_registrations()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/register-tag', methods=['POST'])
def api_register_tag():
    """Register a tag with RF ID and optional palette number and name"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        rf_id = data.get('rf_id', '').strip()
        palette_number = data.get('palette_number')
        name = data.get('name', '').strip() or None
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        if not rf_id:
            return jsonify({'success': False, 'error': 'RFID (RF ID) is required'})
        
        if not palette_number and not name:
            return jsonify({'success': False, 'error': 'Either palette number or name (or both) is required'})
        
        # Convert palette_number to int if provided
        if palette_number is not None:
            try:
                palette_number = int(palette_number)
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Invalid palette number format'})
        
        success = register_tag(tag_id, name, db, rf_id, palette_number)
        
        if success:
            message_parts = [f'RFID: {rf_id}']
            if palette_number:
                message_parts.append(f'Palette: #{palette_number}')
            if name:
                message_parts.append(f'Name: {name}')
            message = f'Tag registered successfully - {", ".join(message_parts)}'
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': 'Failed to register tag'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/skip-registration', methods=['POST'])
def api_skip_registration():
    """Skip registration for a tag"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        success = skip_tag_registration(tag_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Tag registration skipped'})
        else:
            return jsonify({'success': False, 'error': 'Failed to skip tag registration'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete-tag', methods=['POST'])
def api_delete_tag():
    """Delete a tag from the database"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        # Import the delete function from shared_data
        from shared_data import delete_tag_from_shared_data
        success = delete_tag_from_shared_data(tag_id, db)
        
        if success:
            return jsonify({'success': True, 'message': f'Tag deleted successfully: {tag_id[:20]}...'})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete tag or tag not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/unregister-tag', methods=['POST'])
def api_unregister_tag():
    """Unregister a tag (set status to non_active and fill deleted timestamp)"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        if db:
            success = db.unregister_tag(tag_id)
            if success:
                # Also update shared data to reflect the change
                from shared_data import unregister_tag_from_shared_data
                unregister_tag_from_shared_data(tag_id)
                
                return jsonify({'success': True, 'message': f'Tag unregistered successfully: {tag_id[:20]}...'})
            else:
                return jsonify({'success': False, 'error': 'Failed to unregister tag or tag not found/not active'})
        else:
            return jsonify({'success': False, 'error': 'Database not connected'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update-tag-status', methods=['POST'])
def api_update_tag_status():
    """Update tag status (active, inactive, etc.)"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        status = data.get('status', '').strip()
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        if not status:
            return jsonify({'success': False, 'error': 'Status is required'})
        
        if db:
            success = db.update_tag_status(tag_id, status)
            if success:
                return jsonify({'success': True, 'message': f'Tag status updated to "{status}"'})
            else:
                return jsonify({'success': False, 'error': 'Failed to update tag status'})
        else:
            return jsonify({'success': False, 'error': 'Database not connected'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/auto-unregister-tag', methods=['POST'])
def api_auto_unregister_tag():
    """Auto-unregister a tag (change ANY status to non_active and store last status in description)"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        if db:
            success = db.deactivate_tag(tag_id)
            if success:
                # Also update shared data to reflect the change
                from shared_data import unregister_tag_from_shared_data
                unregister_tag_from_shared_data(tag_id)
                
                return jsonify({'success': True, 'message': f'Tag unregistered successfully: {tag_id[:20]}... (status changed to non_active with description)'})
            else:
                return jsonify({'success': False, 'error': 'Failed to unregister tag or tag not found/already non_active'})
        else:
            return jsonify({'success': False, 'error': 'Database not connected'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/restore-tag', methods=['POST'])
def api_restore_tag():
    """Restore a soft-deleted tag"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        if db:
            success = db.restore_tag(tag_id)
            if success:
                return jsonify({'success': True, 'message': f'Tag restored successfully'})
            else:
                return jsonify({'success': False, 'error': 'Failed to restore tag or tag not found'})
        else:
            return jsonify({'success': False, 'error': 'Database not connected'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/frequency-analysis')
def api_frequency_analysis():
    """Get frequency analysis data for detected tags"""
    try:
        data = get_web_data()
        frequency_data = []
        
        # Extract frequency information from active tags
        for tag_id, tag_info in data.get('active_tags', {}).items():
            # Calculate detection rate (frequency)
            count = tag_info.get('count', 0)
            duration = tag_info.get('duration', 1)
            detection_rate = count / max(1, duration)  # Hz (detections per second)
            
            frequency_data.append({
                'tag_id': tag_info.get('id', tag_id[:20] + "..."),
                'full_tag_id': tag_info.get('full_id', tag_id),
                'rf_id': tag_info.get('rf_id', 'N/A'),
                'name': tag_info.get('name', 'Unnamed'),
                'detection_count': count,
                'duration_seconds': round(duration, 2),
                'detection_frequency_hz': round(detection_rate, 3),
                'signal_strength': tag_info.get('signal_strength', 'Unknown'),
                'first_seen': tag_info.get('first_seen', ''),
                'last_seen': tag_info.get('last_seen', ''),
                'is_registered': tag_info.get('is_registered', False),
                'status': tag_info.get('status', 'unregistered')
            })
        
        # Sort by detection frequency (highest first)
        frequency_data.sort(key=lambda x: x['detection_frequency_hz'], reverse=True)
        
        # Calculate statistics
        total_tags = len(frequency_data)
        avg_frequency = sum(tag['detection_frequency_hz'] for tag in frequency_data) / max(1, total_tags)
        max_frequency = max((tag['detection_frequency_hz'] for tag in frequency_data), default=0)
        min_frequency = min((tag['detection_frequency_hz'] for tag in frequency_data), default=0)
        
        # Count by signal strength
        strong_count = sum(1 for tag in frequency_data if tag['signal_strength'] == 'Strong')
        medium_count = sum(1 for tag in frequency_data if tag['signal_strength'] == 'Medium')
        weak_count = sum(1 for tag in frequency_data if tag['signal_strength'] == 'Weak')
        
        return jsonify({
            'success': True,
            'data': {
                'tags': frequency_data,
                'statistics': {
                    'total_tags': total_tags,
                    'average_frequency': round(avg_frequency, 3),
                    'max_frequency': round(max_frequency, 3),
                    'min_frequency': round(min_frequency, 3),
                    'strong_signals': strong_count,
                    'medium_signals': medium_count,
                    'weak_signals': weak_count
                },
                'scan_info': {
                    'total_scans': data.get('statistics', {}).get('total_scans', 0),
                    'total_detections': data.get('statistics', {}).get('total_detections', 0),
                    'scan_rate': data.get('statistics', {}).get('scan_rate', 0)
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system-info')
def api_system_info():
    """Get system information for main dashboard"""
    try:
        stats = get_statistics()
        
        # Get database stats if available
        db_stats = {}
        if db:
            try:
                db_stats = db.get_statistics()
            except Exception as e:
                print(f"⚠️  Database stats error: {e}")
        
        return jsonify({
            'success': True,
            'data': {
                'system_status': 'ready',
                'scanner_connected': stats.get('connected', False),
                'scanning_active': stats.get('scanning', False),
                'total_scans': stats.get('total_scans', 0),
                'active_tags': stats.get('active_tags', 0),
                'pending_registrations': stats.get('pending_registrations', 0),
                'database': db_stats
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('🔗 Client connected to web interface')
    
    # Send initial data immediately
    initial_data = get_web_data()
    emit('initial_data', initial_data)
    
    # Start broadcasting if not already started (for registration page)
    # Main dashboard doesn't need real-time scanning updates
    start_broadcasting()
    
    # Send connection confirmation
    emit('scan_status', {'status': 'connected', 'message': 'Connected to RFID system'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('🔌 Client disconnected from web interface')

@socketio.on('get_status')
def handle_get_status():
    """Handle status request"""
    current_data = get_web_data()
    emit('status_update', current_data)

def main(external_db=None):
    """Run the web interface"""
    global db
    
    print("🌐 RFID Web Interface Starting...")
    print("📱 Dashboard will be available at: http://localhost:5000")
    print("🔄 Real-time updates from shared RFID data")
    print("💾 Database integration enabled")
    print("⏹️  Press Ctrl+C to stop the server")
    
    if external_db:
        print("🔍 DEBUG: Using external database connection")
        db = external_db
        print(f"🔍 DEBUG: External db instance: {db}")
    else:
        # Initialize database
        db_success = initialize_database()
        print(f"🔍 DEBUG: Database initialization result: {db_success}, db instance: {db}")
    
    # Start the web server
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == "__main__":
    main()