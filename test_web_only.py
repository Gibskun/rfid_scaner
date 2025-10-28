#!/usr/bin/env python3
"""
Test Web Interface - No Auto-Scanning
Simple test to run only the web server without any RFID scanning
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rfid_monitor_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    """API endpoint for status check"""
    return {
        'status': 'ready',
        'message': 'Web server running - no auto-scanning'
    }

@socketio.on('connect')
def handle_connect():
    """Handle client connection - no auto-start"""
    print('🌐 Client connected to dashboard')
    emit('scan_status', {'status': 'ready', 'message': 'Ready to start scanning'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('👋 Client disconnected')

@socketio.on('start_scanning')
def handle_start_scanning():
    """Manual start scanning button (simulated)"""
    print('🚀 Start scanning button pressed')
    emit('scan_status', {'status': 'manual_start', 'message': 'Scanning would start here'})

def main():
    """Run the test web interface"""
    print("🧪 Test Web Interface Starting...")
    print("📱 Dashboard will be available at: http://localhost:5000")
    print("🔍 This version does NOT auto-start scanning")
    print("⏹️  Press Ctrl+C to stop the server")
    
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()