#!/usr/bin/env python3
"""
RFID Web Interface - Real-time monitoring dashboard
Reads from shared RFID data and broadcasts to web clients
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
from shared_data import get_web_data, get_statistics

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rfid_monitor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global broadcasting control
update_thread = None
broadcasting = False
last_broadcast_data = None

def broadcast_updates():
    """Continuously broadcast updates from shared data to web clients"""
    global last_broadcast_data, broadcasting
    
    while broadcasting:
        try:
            # Get current data from shared system
            current_data = get_web_data()
            stats = current_data.get('statistics', {})
            
            # Only broadcast if data has changed significantly
            should_broadcast = False
            
            if last_broadcast_data is None:
                should_broadcast = True
            else:
                # Check if statistics changed
                old_stats = last_broadcast_data.get('statistics', {})
                
                if (old_stats.get('total_scans', 0) != stats.get('total_scans', 0) or
                    old_stats.get('total_detections', 0) != stats.get('total_detections', 0) or
                    old_stats.get('active_tag_count', 0) != stats.get('active_tag_count', 0) or
                    old_stats.get('connection_status', '') != stats.get('connection_status', '')):
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
                print(f"📡 Broadcasted update: {stats.get('total_scans', 0)} scans, {stats.get('active_tag_count', 0)} tags")
            
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
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    return jsonify(get_web_data())

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('🔗 Client connected to web interface')
    
    # Send initial data immediately
    initial_data = get_web_data()
    emit('initial_data', initial_data)
    
    # Start broadcasting if not already started
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

def main():
    """Run the web interface"""
    print("🌐 RFID Web Interface Starting...")
    print("📱 Dashboard will be available at: http://localhost:5000")
    print("🔄 Real-time updates from shared RFID data")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Start the web server
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == "__main__":
    main()