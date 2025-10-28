#!/usr/bin/env python3
"""
Command Checksum Analysis
Figure out the correct checksum for commands
"""

def analyze_command_checksum():
    print("🔍 Command Checksum Analysis")
    print("=" * 40)
    
    # Working command from our analysis: 04 FF 36 27 F1
    working_data = [0x04, 0xFF, 0x36]  # Length, Address, Command
    working_checksum = [0x27, 0xF1]   # Expected checksum
    working_16bit = (0xF1 << 8) | 0x27  # 0xF127
    
    print(f"Working command data: {' '.join([f'{b:02X}' for b in working_data])}")
    print(f"Working checksum: {' '.join([f'{b:02X}' for b in working_checksum])} (0x{working_16bit:04X})")
    print()
    
    # Test different algorithms
    print("Testing different checksum algorithms:")
    
    # 1. Simple sum
    sum_val = sum(working_data) & 0xFFFF
    sum_lsb = sum_val & 0xFF
    sum_msb = (sum_val >> 8) & 0xFF
    match1 = [sum_lsb, sum_msb] == working_checksum
    match2 = [sum_msb, sum_lsb] == working_checksum
    print(f"1. Sum: 0x{sum_val:04X} ({sum_lsb:02X} {sum_msb:02X}) {'✅ LSB-MSB' if match1 else '✅ MSB-LSB' if match2 else '❌'}")
    
    # 2. Two's complement
    neg_sum = (~sum(working_data) + 1) & 0xFFFF
    neg_lsb = neg_sum & 0xFF
    neg_msb = (neg_sum >> 8) & 0xFF
    match1 = [neg_lsb, neg_msb] == working_checksum
    match2 = [neg_msb, neg_lsb] == working_checksum
    print(f"2. 2's complement: 0x{neg_sum:04X} ({neg_lsb:02X} {neg_msb:02X}) {'✅ LSB-MSB' if match1 else '✅ MSB-LSB' if match2 else '❌'}")
    
    # 3. CRC16 variants
    def crc16(data, poly=0x8408, init=0xFFFF):
        crc = init
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ poly
                else:
                    crc = crc >> 1
        return crc
    
    # Test the original CRC algorithm in utils
    crc_result = crc16(working_data)
    crc_lsb = crc_result & 0xFF
    crc_msb = (crc_result >> 8) & 0xFF
    match1 = [crc_lsb, crc_msb] == working_checksum
    match2 = [crc_msb, crc_lsb] == working_checksum
    print(f"3. CRC16 (0x8408): 0x{crc_result:04X} ({crc_lsb:02X} {crc_msb:02X}) {'✅ LSB-MSB' if match1 else '✅ MSB-LSB' if match2 else '❌'}")
    
    # If it's CRC, let's confirm by testing the frame_length calculation
    print()
    print("🔧 Checking if frame length includes checksum:")
    
    # Current calculation: frame_length = 4 + len(data) = 4 + 0 = 4
    # But maybe it should be 6 (including 2-byte checksum)?
    
    test_data_with_length_4 = [0x04, 0xFF, 0x36]  # Length=4 (current)
    test_data_with_length_6 = [0x06, 0xFF, 0x36]  # Length=6 (if including checksum)
    
    for name, data in [("Length=4 (current)", test_data_with_length_4), ("Length=6 (with checksum)", test_data_with_length_6)]:
        crc_result = crc16(data)
        crc_lsb = crc_result & 0xFF
        crc_msb = (crc_result >> 8) & 0xFF
        match1 = [crc_lsb, crc_msb] == working_checksum
        match2 = [crc_msb, crc_lsb] == working_checksum
        print(f"   {name}: 0x{crc_result:04X} ({crc_lsb:02X} {crc_msb:02X}) {'✅ LSB-MSB' if match1 else '✅ MSB-LSB' if match2 else '❌'}")

if __name__ == "__main__":
    analyze_command_checksum()