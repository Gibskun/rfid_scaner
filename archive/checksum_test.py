#!/usr/bin/env python3
"""
Checksum Calculator Test
Test different checksum algorithms on the actual response
"""

def test_checksums():
    # Actual response from reader: 11 00 36 00 00 01 0A 0F 00 00 01 02 01 00 08 05 60
    response = [0x11, 0x00, 0x36, 0x00, 0x00, 0x01, 0x0A, 0x0F, 0x00, 0x00, 0x01, 0x02, 0x01, 0x00, 0x08, 0x05, 0x60]
    expected_checksum = [0x05, 0x60]  # Last 2 bytes
    
    # Data for checksum (everything except last 2 bytes)
    data_for_checksum = response[0:-2]  # [0x11, 0x00, 0x36, 0x00, 0x00, 0x01, 0x0A, 0x0F, 0x00, 0x00, 0x01, 0x02, 0x01, 0x00, 0x08]
    
    print("🧮 Checksum Analysis")
    print("=" * 40)
    print(f"Data for checksum: {' '.join([f'{b:02X}' for b in data_for_checksum])}")
    print(f"Expected checksum: {' '.join([f'{b:02X}' for b in expected_checksum])}")
    print()
    
    # Test 1: Simple sum
    sum_val = sum(data_for_checksum) & 0xFFFF
    sum_lsb = sum_val & 0xFF
    sum_msb = (sum_val >> 8) & 0xFF
    print(f"1. Simple sum: {sum_lsb:02X} {sum_msb:02X} {'✅' if [sum_lsb, sum_msb] == expected_checksum else '❌'}")
    
    # Test 2: Two's complement of sum
    neg_sum = (~sum(data_for_checksum) + 1) & 0xFFFF
    neg_lsb = neg_sum & 0xFF
    neg_msb = (neg_sum >> 8) & 0xFF
    print(f"2. 2's complement: {neg_lsb:02X} {neg_msb:02X} {'✅' if [neg_lsb, neg_msb] == expected_checksum else '❌'}")
    
    # Test 3: XOR of all bytes
    xor_val = 0
    for b in data_for_checksum:
        xor_val ^= b
    print(f"3. XOR: {xor_val:02X} {'✅' if xor_val == expected_checksum[0] else '❌'}")
    
    # Test 4: Modular arithmetic checksum
    mod_sum = sum(data_for_checksum) % 256
    mod_comp = (256 - mod_sum) % 256
    print(f"4. Modular comp: {mod_comp:02X} {'✅' if mod_comp == expected_checksum[0] else '❌'}")
    
    # Test 5: CRC16 variants
    def crc16_ccitt(data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
                crc &= 0xFFFF
        return crc
    
    crc_val = crc16_ccitt(data_for_checksum)
    crc_lsb = crc_val & 0xFF
    crc_msb = (crc_val >> 8) & 0xFF
    print(f"5. CRC16-CCITT: {crc_lsb:02X} {crc_msb:02X} {'✅' if [crc_lsb, crc_msb] == expected_checksum else '❌'}")
    
    # Test 6: Try different data ranges
    print("\n🔍 Testing different data ranges:")
    for start in range(0, 3):
        test_data = data_for_checksum[start:]
        sum_val = sum(test_data) & 0xFFFF
        sum_lsb = sum_val & 0xFF
        sum_msb = (sum_val >> 8) & 0xFF
        print(f"   From byte {start}: {sum_lsb:02X} {sum_msb:02X} {'✅' if [sum_lsb, sum_msb] == expected_checksum else '❌'}")

if __name__ == "__main__":
    test_checksums()