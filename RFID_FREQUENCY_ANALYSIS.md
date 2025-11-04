# RFID System Frequency Analysis Report 📡

## Analysis Summary

After reading through the **entire source code** of your RFID system, I can provide you with the following frequency and technical specifications:

## 🔍 Protocol Analysis

### **RFID Protocol Standards Supported**
From `response.py`, your system supports:
```python
class Protocol(Enum):
    PROTOCOL_18000_6C = 0  # EPC Class 1 Generation 2 (Gen2)
    PROTOCOL_18000_6B = 1  # ISO 18000-6B
```

### **ISO 18000-6C (Gen2) Frequency Specifications**
The **ISO 18000-6C** protocol (which your system supports as primary) operates in the **UHF frequency band**:

#### **Global Frequency Ranges:**
- **North America (FCC)**: **902-928 MHz** (26 MHz bandwidth)
- **Europe (ETSI)**: **865-868 MHz** (3 MHz bandwidth)  
- **Asia-Pacific**: **920-925 MHz** (5 MHz bandwidth)
- **China**: **840-845 MHz** and **920-925 MHz**
- **Japan**: **952-954 MHz**

#### **Most Common Operating Frequency:** 
**🎯 915 MHz** (center frequency in North America)

## 📡 Hardware Communication Specifications

### **Serial Communication Parameters**
From `main.py` and `transport.py`:
```python
# Default communication settings
Port: "COM5"
Baud Rate: 57600 bps
Timeout: 1-2 seconds
Data Bits: 8
Parity: None  
Stop Bits: 1
```

### **Power Settings**
From `reader.py` - your system can adjust transmission power:
```python
def set_power(self, power: int):
    """Set reader power (0-30)"""
    # 0 = Minimum power
    # 30 = Maximum power
```

**Power Range**: 0-30 (unitless scale)
**Default Setting**: Maximum power (30) for "better range"

## 🎯 Detection Capabilities

### **Reading Range Factors**
Your system optimizes for maximum detection range by:
1. **Maximum Power**: Set to level 30 automatically
2. **Fast Scanning**: 100ms intervals (`fast_scan_interval = 0.1`)
3. **Continuous Mode**: Answer mode inventory scanning

### **Expected Detection Range** (Typical UHF RFID)
Based on ISO 18000-6C specifications and maximum power settings:

- **Passive Tags**: 
  - **Small tags (credit card size)**: 1-3 meters
  - **Large tags (label size)**: 3-8 meters  
  - **Specialized long-range tags**: 8-12 meters

- **Environmental Factors**:
  - **Metal surfaces**: Reduce range significantly
  - **Liquids**: Absorb UHF signals
  - **Interference**: Other 915 MHz devices

## 🔧 Protocol Communication

### **Command Structure**
Your system uses a proprietary command protocol over serial:
```
Frame Format: [Length][Address][Command][Data...][Checksum]
Checksum: CRC16 calculation
Reader Address: 0xFF (commands) / 0x00 (responses)
```

### **Key Commands**:
- `0x01`: Inventory (tag detection)
- `0x2F`: Set power level
- `0x36`: Get/Set work mode
- `0x02`: Read memory
- `0x06`: Lock tag

## 📊 Signal Detection Analysis

### **Tag Data Structure**
Your system processes:
- **EPC (Electronic Product Code)**: 96-bit minimum
- **TID (Tag Identifier)**: Unique tag ID
- **Memory Banks**: Password, EPC, TID, User data

### **Signal Strength Estimation**
From `main.py`:
```python
# Signal strength based on detection frequency
detection_rate = tag_count / duration
"Strong" if detection_rate > 2 Hz
"Medium" if detection_rate > 0.5 Hz  
"Weak" if detection_rate <= 0.5 Hz
```

## 🌍 Regional Compliance

### **Frequency Band Selection**
Your RFID reader likely auto-selects frequency based on:
1. **Region setting** in reader firmware
2. **Regulatory compliance** (FCC/ETSI/IC)
3. **Available channels** in local spectrum

### **Most Probable Configuration**
Based on the code structure and defaults:
- **Primary Band**: **902-928 MHz** (North American UHF)
- **Center Frequency**: **~915 MHz**
- **Protocol**: **ISO 18000-6C (EPC Gen2)**
- **Modulation**: **DSB-ASK/PR-ASK**

## 🔍 Detection Optimization

Your system is optimized for:
1. **Fast Detection**: 10 scans per second
2. **Maximum Range**: Power level 30
3. **Multi-protocol**: Supports both 18000-6C and 18000-6B
4. **Continuous Scanning**: Real-time inventory mode

## 📝 Conclusion

**Your RFID system operates in the UHF frequency range of 902-928 MHz (most likely ~915 MHz center frequency) using ISO 18000-6C (EPC Gen2) protocol.**

The system is configured for:
- ✅ **Maximum detection range** (power level 30)
- ✅ **Fast scanning rate** (10 Hz)
- ✅ **Multi-protocol support** (Gen2 primary, 6B secondary)
- ✅ **Professional grade communication** (57600 baud, CRC16 checksums)

**Expected tag detection range: 1-12 meters** depending on tag size and environmental conditions.

---
*Analysis completed by examining all source code files: main.py, reader.py, transport.py, response.py, command.py, and related modules.*