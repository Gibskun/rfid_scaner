#!/usr/bin/env python3
"""
Advanced Checksum Test - Try CRC16 with different polynomials
"""

def crc16(data, poly=0x8408, init=0xFFFF):
    """CRC16 with configurable polynomial"""
    crc = init
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ poly
            else:
                crc = crc >> 1
    return crc

def test_crc_variants():
    # Response: 11 00 36 00 00 01 0A 0F 00 00 01 02 01 00 08 05 60
    response = [0x11, 0x00, 0x36, 0x00, 0x00, 0x01, 0x0A, 0x0F, 0x00, 0x00, 0x01, 0x02, 0x01, 0x00, 0x08, 0x05, 0x60]
    expected_checksum = [0x05, 0x60]
    expected_16bit = (0x60 << 8) | 0x05  # 0x6005
    
    # Different data ranges to test
    data_ranges = [
        ("Full except checksum", response[0:-2]),
        ("From byte 1", response[1:-2]),
        ("From byte 2", response[2:-2]),
        ("Without length", response[1:-2]),
    ]
    
    # Different CRC polynomials
    polynomials = [
        ("CRC16-CCITT", 0x1021, 0xFFFF),
        ("CRC16-IBM", 0x8005, 0x0000),
        ("CRC16-Modbus", 0x8005, 0xFFFF),
        ("CRC16-XMODEM", 0x1021, 0x0000),
        ("CRC16-ARC", 0x8005, 0x0000),
        ("Standard (used in code)", 0x8408, 0xFFFF),
    ]
    
    print("🧮 Advanced CRC Analysis")
    print("=" * 50)
    print(f"Expected: 0x{expected_16bit:04X} (bytes: {expected_checksum[0]:02X} {expected_checksum[1]:02X})")
    print()
    
    for data_name, data in data_ranges:
        print(f"📊 Testing {data_name}:")
        print(f"   Data: {' '.join([f'{b:02X}' for b in data])}")
        
        for poly_name, poly, init in polynomials:
            crc_result = crc16(data, poly, init)
            crc_lsb = crc_result & 0xFF
            crc_msb = (crc_result >> 8) & 0xFF
            
            # Test both byte orders
            match1 = [crc_lsb, crc_msb] == expected_checksum
            match2 = [crc_msb, crc_lsb] == expected_checksum
            
            status = "✅" if (match1 or match2) else "❌"
            order = "LSB-MSB" if match1 else "MSB-LSB" if match2 else "no match"
            
            print(f"   {poly_name:20}: 0x{crc_result:04X} ({crc_lsb:02X} {crc_msb:02X}) {order} {status}")
        print()

    # Also test if it's some other simple algorithm
    print("🔧 Simple algorithms on full data:")
    data = response[0:-2]
    
    # Checksum as used in some protocols
    checksum_8bit = sum(data) & 0xFF
    checksum_complement = (0x100 - checksum_8bit) & 0xFF
    
    print(f"   8-bit sum: 0x{checksum_8bit:02X}")
    print(f"   8-bit complement: 0x{checksum_complement:02X}")
    
    # Maybe it's BCC (Block Check Character)
    bcc = 0
    for b in data:
        bcc ^= b
    print(f"   BCC (XOR): 0x{bcc:02X}")

if __name__ == "__main__":
    test_crc_variants()