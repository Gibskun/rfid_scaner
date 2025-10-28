from typing import Iterator

from transport import Transport
from command import Command
from response import Response


class Reader:
    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    def close(self) -> None:
        self.transport.close()

    def __send_request(self, command: Command) -> None:
        self.transport.write_bytes(command.serialize())

    def __get_response(self) -> bytes:
        return self.transport.read_frame()

    def work_mode(self):
        """Get current work mode"""
        command = Command(0x36)  # CMD_WORK_MODE
        self.__send_request(command)
        response_data = self.__get_response()
        if response_data:
            response = Response(response_data)
            return response
        raise Exception("Failed to get work mode")

    def set_power(self, power: int):
        """Set reader power (0-30)"""
        command = Command(0x2F, data=bytearray([power]))  # CMD_SET_POWER
        self.__send_request(command)
        response_data = self.__get_response()
        if response_data:
            return Response(response_data)
        return None

    def inventory_answer_mode(self, start_address_tid: int = None, len_tid: int = None) -> Iterator[bytes]:
        """Inventory tags in Answer Mode"""
        if start_address_tid is not None and len_tid is not None:
            command = Command(0x01, data=bytearray([start_address_tid, len_tid]))  # CMD_INVENTORY
        else:
            command = Command(0x01)  # CMD_INVENTORY
        self.__send_request(command)
        
        response_data = self.__get_response()
        if not response_data:
            return
            
        try:
            response = Response(response_data)
            
            if response.status != 0x00:
                return
                
            if response.command == 0x01 and len(response.data) >= 1:  # CMD_INVENTORY
                tag_count = response.data[0]
                
                if tag_count == 0:
                    return
                    
                tags_data = response.data[1:]
                
                data_pointer = 0
                for tag_num in range(tag_count):
                    if data_pointer >= len(tags_data):
                        break
                        
                    tag_length = tags_data[data_pointer]
                    tag_start = data_pointer + 1
                    tag_end = tag_start + tag_length
                    
                    if tag_end <= len(tags_data):
                        tag_data = tags_data[tag_start:tag_end]
                        yield tag_data
                        data_pointer = tag_end
                    else:
                        break
                        
        except Exception as e:
            print(f"⚠️  Inventory parsing error: {e}")

    def inventory_active_mode(self) -> Iterator[Response]:
        while True:
            try:
                raw_response = self.__get_response()
                if raw_response is None:
                    continue
                    
                response = Response(raw_response)
                yield response
                
            except Exception as e:
                print(f"⚠️  Unexpected error in active mode: {e}")
                continue

    def read_memory(self, epc: bytes, memory_bank: int, start_address: int, length: int, access_password: bytes = bytes(4)) -> Response:
        request_data = bytearray()
        request_data.extend(bytearray([int(len(epc) / 2)]))  # EPC Length in word
        request_data.extend(epc)
        request_data.extend(bytearray([memory_bank, start_address, length]))
        request_data.extend(access_password)
        command = Command(0x02, data=request_data)  # CMD_READ_MEMORY
        self.__send_request(command)
        return Response(self.__get_response())

    def write_memory(self, epc: bytes, memory_bank: int, start_address: int, data_to_write: bytes, access_password: bytes = bytes(4)) -> Response:
        request_data = bytearray()
        request_data.extend(bytearray([int(len(data_to_write) / 2)]))  # Data length in word
        request_data.extend(bytearray([int(len(epc) / 2)]))  # EPC Length in word
        request_data.extend(epc)
        request_data.extend(bytearray([memory_bank, start_address]))
        request_data.extend(data_to_write)
        request_data.extend(access_password)
        command = Command(0x04, data=request_data)  # CMD_WRITE_MEMORY
        self.__send_request(command)
        return Response(self.__get_response())

    def lock(self, epc: bytes, select: int, set_protect: int, access_password: bytes) -> Response:
        parameter = bytearray([int(len(epc) / 2)]) + epc + bytearray([select, set_protect]) + access_password
        command = Command(0x06, data=parameter)  # CMD_SET_LOCK
        self.__send_request(command)
        return Response(self.__get_response())

    def set_reader_power(self, power: int) -> Response:
        assert 0 <= power <= 30
        command = Command(0x2F, data=bytearray([power]))  # CMD_SET_READER_POWER
        self.__send_request(command)
        return Response(self.__get_response())

    def get_work_mode(self):
        command = Command(0x36)  # CMD_GET_WORK_MODE
        self.__send_request(command)
        return Response(self.__get_response())

    def set_work_mode(self, work_mode: int) -> Response:
        command = Command(0x35, data=bytearray([work_mode]))  # CMD_SET_WORK_MODE
        self.__send_request(command)
        return Response(self.__get_response())