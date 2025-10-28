import struct
from dataclasses import dataclass
from enum import IntEnum, Enum


def hex_readable(data):
    """Convert bytes to hex readable format"""
    if isinstance(data, int):
        return f"{data:02X}"
    elif isinstance(data, bytes):
        return " ".join(f"{b:02X}" for b in data)
    elif isinstance(data, list):
        return " ".join(f"{b:02X}" for b in data)
    else:
        return str(data)


def calculate_checksum(data):
    """Calculate CRC16 checksum"""
    # Simple placeholder checksum calculation
    return sum(data) & 0xFFFF


class WorkMode(IntEnum):
    ACTIVE_MODE = 0x00
    ANSWER_MODE = 0x01


class InventoryWorkMode(IntEnum):
    ACTIVE_MODE = 0x00
    ANSWER_MODE = 0x01


class Response:
    def __init__(self, response_bytes: bytes):
        if response_bytes is None or len(response_bytes) < 6:
            raise ValueError(f"Response data is too short to be valid. Got {len(response_bytes) if response_bytes else 0} bytes.")
            
        self.response_bytes = response_bytes
        self.length = response_bytes[0]
        
        if len(response_bytes) < self.length:
            raise ValueError(f"Response length mismatch. Expected {self.length}, got {len(response_bytes)} bytes.")
            
        self.reader_address = response_bytes[1]
        self.command = response_bytes[2]
        self.status = response_bytes[3]  # Check 5. LIST OF COMMAND EXECUTION RESULT STATUS
        
        # Fix data extraction - should be from byte 4 to length-2 (excluding 2-byte checksum)
        self.data = response_bytes[4: self.length - 2] if self.length > 6 else b''
        
        # Fix checksum extraction - last 2 bytes
        self.checksum = response_bytes[self.length - 2: self.length]
        
        # Handle work mode response (command 0x36)
        if self.command == 0x36 and len(self.data) >= 1:
            # Parse inventory work mode from data
            self.inventory_work_mode = InventoryWorkMode.ANSWER_MODE if len(self.data) > 4 and self.data[4] == 1 else InventoryWorkMode.ACTIVE_MODE

    def __str__(self) -> str:
        lines = [
            ">>> START RESPONSE ================================",
            f"RESPONSE       >> {hex_readable(self.response_bytes)}",
            f"READER ADDRESS >> {hex_readable(self.reader_address)}",
            f"COMMAND        >> {hex_readable(self.command)}",
            f"STATUS         >> {hex_readable(self.status)}",
        ]
        
        if self.data:
            lines.append(f"DATA           >> {hex_readable(self.data)}")
            
        lines.append(f"CHECKSUM       >> {hex_readable(self.checksum)}")
        lines.append(">>> END RESPONSE   ================================")
        
        return "\n".join(lines)


class InventoryWorkMode(Enum):
    ANSWER_MODE = 0
    ACTIVE_MODE = 1
    TRIGGER_MODE_LOW = 2
    TRIGGER_MODE_HIGH = 3


class OutputInterface(Enum):
    WIEGAND = 0
    RS232_485 = 1
    SYRIS485 = 2


class Protocol(Enum):
    PROTOCOL_18000_6C = 0
    PROTOCOL_18000_6B = 1


class AddressType(Enum):
    WORD = 0
    BYTE = 1


class WiegandFormat(Enum):
    WIEGAND_26BITS = 0
    WIEGAND_34BITS = 1


class WiegandBitOrder(Enum):
    HIGH_BIT_FIRST = 0
    LOW_BIT_FIRST = 1


class InventoryMemoryBank(Enum):
    PASSWORD = 0
    EPC = 1
    TID = 2
    USER = 3
    INVENTORY_MULTIPLE = 4
    INVENTORY_SINGLE = 5
    EAS_ALARM = 6