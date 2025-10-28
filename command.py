def calculate_checksum(data: bytes) -> bytearray:
    """Calculate CRC16 checksum for RFID reader protocol"""
    value = 0xFFFF
    for d in data:
        value ^= d
        for _ in range(8):
            value = (value >> 1) ^ 0x8408 if value & 0x0001 else (value >> 1)
    return bytearray([value & 0xFF, (value >> 8) & 0xFF])


class Command:
    def __init__(self, command: int, reader_address: int = 0xFF, data: bytearray = None):
        self.command = command
        self.reader_address = reader_address
        self.data = data or bytearray()
        if isinstance(data, int):
            self.data = bytearray([data])
        if data is None:
            self.data = bytearray()
        self.frame_length = 4 + len(self.data)
        self.base_data = bytearray([self.frame_length, self.reader_address, self.command])
        self.base_data.extend(self.data)

    def serialize(self) -> bytes:
        serialize_data = self.base_data.copy()
        checksum = calculate_checksum(serialize_data)
        serialize_data.extend(checksum)
        return bytes(serialize_data)