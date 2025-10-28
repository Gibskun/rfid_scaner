# RFID Reader System - Organized Project Structure

## 📁 Project Overview
This is an optimized RFID reader system for the HW-VX6330K reader with fast and reliable tag detection capabilities, including distance estimation based on detection frequency.

## 🚀 Main Application Files

### Primary Scanner (Recommended)
- **`rfid_fast_scanner.py`** - **Main application with optimized fast scanning**
  - 🎯 **Fast detection**: 100ms scan intervals (20x faster than original)
  - 📡 **Distance estimation**: Uses detection frequency as signal strength indicator
  - 🔧 **Noise filtering**: Advanced frame synchronization handles communication noise
  - 📊 **Real-time statistics**: Shows scan rate, active tags, and detection counts
  - ⚡ **Performance**: 7+ scans per second with reliable tag detection

### Alternative Scanners
- **`rfid_adaptive_scanner.py`** - Self-optimizing scanner with automatic power adjustment
- **`rfid_working.py`** - Simple, stable version for basic tag detection

## 🔧 Core System Files (Essential)

### Communication Layer
- **`transport.py`** - Serial communication with intelligent frame sync and noise filtering
- **`reader.py`** - High-level RFID operations (inventory, work mode queries)
- **`response.py`** - Response parsing and validation with fixed checksum handling
- **`command.py`** - Command construction and serialization
- **`utils.py`** - Checksum calculation and helper functions

### Configuration
- **`requirements.txt`** - Python dependencies (pyserial)
- **`.venv/`** - Python virtual environment

## 📊 Performance Achievements

### Speed Improvements
- **Original system**: 0.5 scans/second (2-second delays)
- **Optimized system**: 7+ scans/second (100ms intervals)
- **Improvement**: **14x faster detection**

### Reliability Fixes
- ✅ Fixed frame synchronization issues with noise filtering
- ✅ Corrected tag data parsing (no more truncated "00 00 00" data)
- ✅ Enhanced error handling and automatic recovery
- ✅ Proper Answer Mode operation for HW-VX6330K

### Distance Detection
- 🎯 **Signal strength estimation** based on detection frequency
- 📍 **Distance correlation**: Higher detection rate = closer distance
- 🏷️ **Tag tracking**: Monitors tags over time with first/last seen timestamps

## 🎛️ Usage Instructions

### Quick Start
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the main optimized scanner
python rfid_fast_scanner.py
```

### Performance Testing
```bash
# Run 10-second performance test
python test_performance.py
```

### Basic Operation
```bash
# Simple stable scanner
python rfid_working.py
```

## 🔧 System Requirements

- **Hardware**: HW-VX6330K RFID reader
- **Connection**: COM5 at 57600 baud (configurable)
- **Mode**: Answer Mode operation
- **Protocol**: ISO 18000-6C
- **Python**: 3.7+ with pyserial

## 📈 Key Features

1. **Fast Detection**: 100ms scan intervals for near real-time response
2. **Distance Estimation**: Detection frequency indicates tag proximity
3. **Noise Filtering**: Robust frame synchronization handles communication issues
4. **Error Recovery**: Automatic reconnection and failure handling
5. **Real-time Feedback**: Live statistics and tag tracking
6. **Signal Strength**: Higher detection counts = stronger signal/closer distance

## 🛠️ Troubleshooting

- **No tags detected**: Check Answer Mode configuration in reader settings
- **Communication errors**: Verify COM port and baud rate (57600)
- **Slow detection**: Use `rfid_fast_scanner.py` for optimized performance
- **Distance issues**: Detection frequency correlates with tag proximity

## 📝 Technical Notes

- System uses Answer Mode (not Active Mode) for optimal performance
- Frame sync handles noise bytes (0x3D, 0xA7, 0xCE, 0xF0, etc.)
- CRC16 checksum validation with LSB-MSB byte order
- Tag data extraction fixed to show complete EPC information
- Distance estimation: 30+ detections = close, 10-20 = medium, <10 = far