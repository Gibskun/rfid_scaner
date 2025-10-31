#!/usr/bin/env python3
"""
Test EPC generation logic
"""

def generate_suggested_epc(tag_hex: str) -> str:
    """Generate suggested new EPC (12 bytes) based on current tag"""
    tag_bytes = tag_hex.replace(' ', '')
    
    # Create suggested EPC (E2 00 prefix + tag data + padding if needed)
    if len(tag_bytes) < 24:  # Less than 12 bytes
        # Use E2 00 prefix (common for UHF RFID), then current tag, then zeros
        padding_needed = 12 - len(tag_bytes) // 2 - 2
        suggested_epc = 'E2 00 ' + tag_hex + ' 00' * padding_needed
    else:
        # Tag is already 12+ bytes, use it as-is
        suggested_epc = tag_hex[:35]  # First 12 bytes with spaces
    
    # Ensure proper spacing
    suggested_epc_bytes = suggested_epc.replace(' ', '')
    suggested_epc = ' '.join([suggested_epc_bytes[i:i+2] for i in range(0, min(24, len(suggested_epc_bytes)), 2)])
    
    return suggested_epc

# Test cases
test_tags = [
    "04 00 00 00",  # 4-byte tag (needs padding)
    "E2 00 10 70 E0 10 01 97 1D 32 43 21",  # 12-byte tag (already full EPC)
    "AA BB CC DD EE FF",  # 6-byte tag
]

print("EPC Generation Test:")
print("=" * 60)

for tag in test_tags:
    suggested = generate_suggested_epc(tag)
    print(f"\nOriginal Tag: {tag}")
    print(f"Suggested EPC: {suggested}")
    print(f"Length: {len(suggested.replace(' ', ''))} hex chars = {len(suggested.replace(' ', '')) // 2} bytes")

print("\n" + "=" * 60)
