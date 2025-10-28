#!/usr/bin/env python3
"""
RFID Web Interface - Real-time monitoring dashboard
Web-based interface for monitoring RFID tag detection in real-time
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
from main import FastRFIDScanner

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rfid_monitor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global scanner instance and data
scanner = None
scanner_thread = None
scanner_running = False
web_data = {
    'active_tags': {},
    'statistics': {
        'total_scans': 0,
        'total_detections': 0,
        'active_tag_count': 0,
        'scan_rate': 0.0,
        'uptime': 0,
        'connection_status': 'Disconnected'
    },
    'recent_activity': []
}

class WebRFIDScanner(FastRFIDScanner):
    """Extended scanner class for web interface"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scan_count = 0
        self.start_time = None
        self.last_status_time = time.time()
        
    def connect(self) -> bool:
        """Connect with web status updates"""
        success = super().connect()
        web_data['statistics']['connection_status'] = 'Connected' if success else 'Failed'
        self.broadcast_status_update()
        return success
        
    def process_tags(self, tags: list):
        """Process tags with web updates"""
        current_time = datetime.now()
        
        if tags:
            self.total_detections += len(tags)
            
            for tag in tags:
                tag_hex = ' '.join([f'{b:02X}' for b in tag])
                
                # Create web-friendly tag data
                tag_display_id = tag_hex[:20] + "..." if len(tag_hex) > 20 else tag_hex
                
                if tag_hex in self.active_tags:
                    # Update existing tag
                    tag_info = self.active_tags[tag_hex]
                    tag_info['last_seen'] = current_time
                    tag_info['count'] += 1
                    
                    # Calculate signal strength
                    detection_rate = tag_info['count'] / max(1, (current_time - tag_info['first_seen']).total_seconds())
                    signal_strength = "Strong" if detection_rate > 2 else "Medium" if detection_rate > 0.5 else "Weak"
                    
                    # Update web data
                    web_data['active_tags'][tag_hex] = {
                        'id': tag_display_id,
                        'full_id': tag_hex,
                        'first_seen': tag_info['first_seen'].strftime('%H:%M:%S'),
                        'last_seen': current_time.strftime('%H:%M:%S.%f')[:-3],
                        'count': tag_info['count'],
                        'signal_strength': signal_strength,
                        'duration': (current_time - tag_info['first_seen']).total_seconds()
                    }
                    
                else:
                    # New tag detected
                    self.active_tags[tag_hex] = {
                        'first_seen': current_time,
                        'last_seen': current_time,
                        'count': 1,
                        'data': tag
                    }
                    
                    # Add to web data
                    web_data['active_tags'][tag_hex] = {
                        'id': tag_display_id,
                        'full_id': tag_hex,
                        'first_seen': current_time.strftime('%H:%M:%S'),
                        'last_seen': current_time.strftime('%H:%M:%S.%f')[:-3],
                        'count': 1,
                        'signal_strength': 'New',
                        'duration': 0
                    }
                    
                    # Add to recent activity
                    activity = {
                        'time': current_time.strftime('%H:%M:%S'),
                        'type': 'new_tag',
                        'message': f'New tag detected: {tag_display_id}',
                        'tag_id': tag_hex
                    }
                    web_data['recent_activity'].insert(0, activity)
                    
                    # Keep only last 20 activities
                    if len(web_data['recent_activity']) > 20:
                        web_data['recent_activity'] = web_data['recent_activity'][:20]
                    
                    # Broadcast new tag event
                    socketio.emit('new_tag', {
                        'tag': web_data['active_tags'][tag_hex],
                        'activity': activity
                    })
    
    def cleanup_old_tags(self):
        """Remove old tags with web updates"""
        current_time = datetime.now()
        to_remove = []
        
        for tag_id, tag_info in self.active_tags.items():
            time_since_last = (current_time - tag_info['last_seen']).total_seconds()
            if time_since_last > self.cleanup_interval:
                to_remove.append(tag_id)
                
                # Add removal activity
                tag_display_id = tag_id[:20] + "..." if len(tag_id) > 20 else tag_id
                activity = {
                    'time': current_time.strftime('%H:%M:%S'),
                    'type': 'tag_removed',
                    'message': f'Tag removed: {tag_display_id} (inactive for {time_since_last:.1f}s)',
                    'tag_id': tag_id
                }
                web_data['recent_activity'].insert(0, activity)
                
                # Broadcast tag removal
                socketio.emit('tag_removed', {
                    'tag_id': tag_id,
                    'activity': activity
                })
        
        # Remove from both internal and web data
        for tag_id in to_remove:
            if tag_id in self.active_tags:
                del self.active_tags[tag_id]
            if tag_id in web_data['active_tags']:
                del web_data['active_tags'][tag_id]
    
    def broadcast_status_update(self):
        """Broadcast status update to web clients"""
        current_time = time.time()
        
        # Update statistics
        web_data['statistics'].update({
            'total_scans': self.scan_count,
            'total_detections': self.total_detections,
            'active_tag_count': len(self.active_tags),
            'uptime': current_time - self.start_time if self.start_time else 0,
            'connection_status': 'Connected' if self.connected else 'Disconnected'
        })
        
        # Calculate scan rate
        if self.start_time:
            elapsed = current_time - self.start_time
            web_data['statistics']['scan_rate'] = self.scan_count / elapsed if elapsed > 0 else 0
        
        # Broadcast to all connected clients
        socketio.emit('status_update', {
            'statistics': web_data['statistics'],
            'active_tags': web_data['active_tags']
        })
    
    def run_web_scan(self):
        """Run scanning for web interface"""
        global scanner_running
        
        print("🌐 Starting RFID scanner for web interface...")
        self.start_time = time.time()
        last_cleanup = time.time()
        consecutive_failures = 0
        
        try:
            # Connect to scanner
            if not self.connect():
                print("❌ Failed to connect to RFID reader")
                return
            
            # Optimize reader settings
            self.optimize_reader_settings()
            
            while scanner_running:
                scan_start = time.time()
                self.scan_count += 1
                
                # Perform scan
                tags = self.scan_tags_fast()
                
                if tags is not None:
                    consecutive_failures = 0
                    self.process_tags(tags)
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= self.max_scan_failures:
                        print("⚠️  Multiple scan failures, attempting to reconnect...")
                        if not self.connect():
                            break
                        consecutive_failures = 0
                
                # Periodic cleanup
                current_time = time.time()
                if current_time - last_cleanup > self.cleanup_interval:
                    self.cleanup_old_tags()
                    last_cleanup = current_time
                
                # Status update every 50 scans (more frequent for web)
                if self.scan_count % 50 == 0 or (current_time - self.last_status_time) > 2:
                    self.broadcast_status_update()
                    self.last_status_time = current_time
                
                # Fast scanning with minimal delay
                scan_duration = time.time() - scan_start
                sleep_time = max(0, self.fast_scan_interval - scan_duration)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except Exception as e:
            print(f"❌ Scanning error: {e}")
            web_data['statistics']['connection_status'] = f'Error: {str(e)}'
            self.broadcast_status_update()
        
        finally:
            print("🛑 Web scanner stopped")
            scanner_running = False
            self.close()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    return jsonify({
        'statistics': web_data['statistics'],
        'active_tags': list(web_data['active_tags'].values()),
        'recent_activity': web_data['recent_activity'][:10]
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('🔗 Client connected to web interface')
    emit('initial_data', {
        'statistics': web_data['statistics'],
        'active_tags': web_data['active_tags'],
        'recent_activity': web_data['recent_activity'][:10]
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('🔌 Client disconnected from web interface')

@socketio.on('start_scanning')
def handle_start_scanning():
    """Start RFID scanning"""
    global scanner, scanner_thread, scanner_running
    
    if not scanner_running:
        scanner_running = True
        scanner = WebRFIDScanner()
        scanner_thread = threading.Thread(target=scanner.run_web_scan)
        scanner_thread.daemon = True
        scanner_thread.start()
        emit('scan_status', {'status': 'started'})

@socketio.on('stop_scanning')
def handle_stop_scanning():
    """Stop RFID scanning"""
    global scanner_running
    
    scanner_running = False
    web_data['statistics']['connection_status'] = 'Stopped'
    emit('scan_status', {'status': 'stopped'})

def main():
    """Run the web interface"""
    print("🌐 RFID Web Interface Starting...")
    print("📱 Dashboard will be available at: http://localhost:5000")
    print("🔌 Connect your RFID reader and click 'Start Scanning' on the web page")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Start the web server
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()