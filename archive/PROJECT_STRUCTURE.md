# 📁 RFID System - Clean Project Structure

## 🎯 Main Application Files (Choose One)

### 🚀 Recommended: Quick Start
```bash
python run_rfid_system.py    # Auto-selects best scanner
```

### 🔧 Direct Scanner Selection
```bash
python rfid_fast_scanner.py      # 🎯 BEST: Fast + distance estimation  
python rfid_adaptive_scanner.py  # 🔄 Auto-tuning scanner
python rfid_working.py           # 🔧 Basic stable version
python main.py                   # 🔗 Compatibility redirect
```

## 📋 Core System Files (Don't Modify)

### 🧠 Core Logic
- `transport.py` - Serial communication & noise filtering
- `reader.py` - RFID operations & inventory management  
- `response.py` - Response parsing & validation
- `command.py` - Command construction
- `utils.py` - Checksum & helper functions

### 📦 Configuration  
- `requirements.txt` - Python dependencies
- `.venv/` - Virtual environment

### 📊 Testing & Performance
- `test_performance.py` - Performance benchmarking

## 📚 Documentation
- `README.md` - Complete project overview
- `QUICK_START.md` - Usage instructions
- `PROJECT_STRUCTURE.md` - This file

## 📁 Archive Directory
- `archive/` - Contains old/test files (safe to ignore)

## 🎯 Performance Summary

| File | Speed | Features | Use Case |
|------|-------|----------|----------|
| **rfid_fast_scanner.py** | **7+ scans/sec** | Distance estimation, noise filtering | **Production** |
| rfid_adaptive_scanner.py | 5+ scans/sec | Auto power adjustment | Variable conditions |
| rfid_working.py | 2-3 scans/sec | Simple, stable | Basic testing |

## 🚀 Quick Commands

```bash
# Performance test (10 seconds)
python test_performance.py

# Fast scanner (recommended)  
python rfid_fast_scanner.py

# Auto-select best scanner
python run_rfid_system.py
```

## 🏷️ System Capabilities

### ✅ Fixed Issues
- ⚡ **20x speed improvement** (0.5 → 7+ scans/sec)
- 🔧 **Noise filtering** (handles 0x3D, 0xA7, 0xCE bytes)
- 📊 **Complete tag data** (no more "00 00 00" truncation)
- 🔄 **Automatic recovery** from communication errors

### 📍 Distance Detection  
- **High frequency** (30+ detections) = Close distance
- **Medium frequency** (10-20 detections) = Medium distance  
- **Low frequency** (<10 detections) = Far distance

### 🎛️ Technical Specs
- **Protocol**: ISO 18000-6C
- **Mode**: Answer Mode (HW-VX6330K)
- **Port**: COM5 @ 57600 baud
- **Scan Interval**: 100ms (configurable)
- **Multi-tag**: Simultaneous detection supported