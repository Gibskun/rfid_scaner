from abc import ABC, abstractmethod
import serial
from socket import socket, AF_INET, SOCK_STREAM


class Transport(ABC):
    @abstractmethod
    def read_bytes(self, length: int) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def write_bytes(self, buffer: bytes) -> None:
        raise NotImplementedError

    def read_frame(self) -> bytes | None:
        try:
            # Buffer for collecting potential frame data
            buffer = bytearray()
            max_buffer_size = 200
            
            # Read bytes until we find a valid frame or timeout
            while len(buffer) < max_buffer_size:
                byte_data = self.read_bytes(1)
                if not byte_data:
                    break
                
                buffer.extend(byte_data)
                
                # Look for valid frame starting at each position
                for start_pos in range(len(buffer)):
                    if start_pos >= len(buffer):
                        break
                        
                    potential_length = buffer[start_pos]
                    
                    # Check if this could be a valid frame start
                    if 5 <= potential_length <= 50:  # Reasonable RFID frame sizes
                        frame_end = start_pos + potential_length
                        
                        # Do we have enough data for this frame?
                        if frame_end <= len(buffer):
                            frame_data = buffer[start_pos:frame_end]
                            
                            # Validate frame structure
                            if self._validate_frame(frame_data):
                                if self.debug and start_pos > 0:
                                    noise_bytes = buffer[:start_pos]
                                    print(f"🧹 Skipped {start_pos} noise bytes: {[f'0x{b:02X}' for b in noise_bytes]}")
                                
                                if self.debug:
                                    print(f"✅ Valid frame found: {len(frame_data)} bytes")
                                
                                return bytes(frame_data)
            
            if buffer and self.debug:
                print(f"❌ No valid frame in {len(buffer)} bytes: {[f'0x{b:02X}' for b in buffer[:10]]}...")
            
            return None
            
        except Exception as e:
            if self.debug:
                print(f"❌ Error reading frame: {e}")
            return None

    def _validate_frame(self, frame_data: bytes) -> bool:
        """Validate if frame_data looks like a valid RFID response"""
        if len(frame_data) < 5:
            return False
            
        length = frame_data[0]
        if len(frame_data) != length:
            return False
            
        # Check for reasonable values
        reader_addr = frame_data[1]
        command = frame_data[2]
        status = frame_data[3]
        
        # Reader address should be 0x00 for responses
        if reader_addr != 0x00:
            return False
            
        # Common command responses: 0x01 (inventory), 0x36 (work mode)
        if command not in [0x01, 0x36, 0x02, 0x03]:
            return False
            
        # Status should be reasonable (0x00 for success, or other known codes)
        if status > 0xFF:
            return False
            
        return True

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class SerialTransport(Transport):
    def __init__(self, serial_port: str, baud_rate: int, timeout: int = 1) -> None:
        self.serial = serial.Serial(serial_port, baud_rate,
                                    timeout=timeout, write_timeout=timeout)
        self.debug = True  # Enable debugging by default to see communication issues
        if self.debug:
            print(f"📡 Opened {serial_port} at {baud_rate} baud")
            print(f"📡 Serial settings: timeout={timeout}s, write_timeout={timeout}s")

    def read_bytes(self, length: int) -> bytes:
        try:
            data = self.serial.read(length)
            if self.debug:
                if data:
                    print(f"📥 Read {len(data)}/{length} bytes: {[f'0x{b:02X}' for b in data]}")
                else:
                    print(f"📥 Read 0/{length} bytes (timeout)")
            return data
        except Exception as e:
            if self.debug:
                print(f"❌ Error reading {length} bytes: {e}")
            return b''

    def write_bytes(self, buffer: bytes) -> None:
        try:
            if self.debug:
                print(f"📤 Writing {len(buffer)} bytes: {[f'0x{b:02X}' for b in buffer]}")
            bytes_written = self.serial.write(buffer)
            if self.debug:
                print(f"📤 Successfully wrote {bytes_written} bytes")
        except Exception as e:
            if self.debug:
                print(f"❌ Error writing bytes: {e}")
            raise

    def close(self) -> None:
        if self.debug:
            print("📡 Closing serial port")
        self.serial.close()


class TcpTransport(Transport):
    def __init__(self, ip_address: str, port: int, timeout: int = 1) -> None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((ip_address, port))
        self.debug = False

    def read_bytes(self, length: int) -> bytes:
        return self.socket.recv(length)

    def write_bytes(self, buffer: bytes) -> None:
        self.socket.sendall(buffer)

    def close(self) -> None:
        self.socket.close()