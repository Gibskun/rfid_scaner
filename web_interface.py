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
from shared_data import get_web_data, get_statistics, get_pending_registrations, register_tag, skip_tag_registration
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
    return render_template('main_dashboard.html')

@app.route('/register')
def register_dashboard():
    """RFID registration dashboard"""
    return render_template('dashboard.html')

@app.route('/delete')
def delete_dashboard():
    """RFID tag deletion dashboard"""
    return render_template('delete_dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    return jsonify(get_web_data())

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
            tags = db.get_all_tags(limit=limit, offset=offset)
            return jsonify({'success': True, 'data': tags})
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
                if tag_info.get('write_date'):
                    tag_info['write_date'] = tag_info['write_date'].isoformat()
                if tag_info.get('unwrite_date'):
                    tag_info['unwrite_date'] = tag_info['unwrite_date'].isoformat()
                if tag_info.get('first_detected'):
                    tag_info['first_detected'] = tag_info['first_detected'].isoformat()
                if tag_info.get('last_detected'):
                    tag_info['last_detected'] = tag_info['last_detected'].isoformat()
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
    """Register a tag with an item name"""
    try:
        data = request.get_json()
        tag_id = data.get('tag_id')
        item_name = data.get('item_name', '').strip()
        
        if not tag_id:
            return jsonify({'success': False, 'error': 'Tag ID is required'})
        
        if not item_name:
            return jsonify({'success': False, 'error': 'Item name is required'})
        
        success = register_tag(tag_id, item_name, db)
        
        if success:
            return jsonify({'success': True, 'message': f'Tag registered successfully as "{item_name}"'})
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