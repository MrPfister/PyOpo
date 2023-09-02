from typing import Optional, Any, Self, List
import struct

# Debuggers
from .debugger.debugger_dsf import DebuggerDSF
from .debugger.debugger_profiler import DebuggerProfiler

# Logging
import logging
import logging.config

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


class free_block:
    """Meta class to store locations of contiguous sections of free memory in the heap"""

    def __init__(self, start: int, length: int):
        self.start = start
        self.length = length
        self.end = start + length - 1


class data_frame:
    """Meta class to store locations of allocated sections of memory in the heap"""

    def __init__(self, start: int, length: int):
        self.start = start
        self.length = length

    def in_frame(self, offset: int) -> bool:
        """Return whether a heap offset resides inside the frame"""
        if offset >= self.start and offset < self.start + self.length:
            return True

        return False


class data_stack:
    def __init__(self, size: int, debugger: Optional[DebuggerDSF] = None):
        # Cache struct pack
        self._struct_unpacker_uint16 = struct.Struct("<H")
        self._struct_unpacker_int16 = struct.Struct("<h")
        self._struct_unpacker_float = struct.Struct("<d")
        self._struct_unpacker_long = struct.Struct("<i")

        self.free_blocks: List[free_block] = [free_block(start=0, length=size)]
        self.frames: List[data_frame] = []

        # Underlying memory
        self.memory = bytearray(size)

        self.debugger = debugger

    def allocate_frame(self, size: int) -> int:
        """Allocates a section of specified size in the heap.

        Returns the start offset of the allocated frame"""

        # Find an available free block large enough
        free_block_entry = next((b for b in self.free_blocks if b.length >= size), None)

        if not free_block_entry:
            raise ("No available memory")

        # Construct Data Stack Frame
        entry = data_frame(start=free_block_entry.start, length=size)
        _logger.info(f"Allocating DSF Size: {size} at Offset: {entry.start}")

        if self.debugger:
            self.debugger.store_alloc_block(entry.start, entry.start + entry.length)

        if free_block_entry.length == size:
            self.free_blocks.remove(free_block_entry)
        else:
            # Resize free block instead of just removing it
            free_block_entry.start += size
            free_block_entry.length -= size

        self.frames.append(entry)

        # Reinitialise the frame
        self.memory[entry.start : entry.start + entry.length] = b"\x00" * entry.length

        return entry.start

    def free_frame(self, offset: int) -> None:
        # Find if there is a frame where the offset resides
        frame_to_free = next((f for f in self.frames if f.in_frame(offset)), None)

        if not frame_to_free:
            _logger.warning(
                f"DSF Frame not found, Offset: {offset} in frames {self.frames}"
            )
            # raise ("Data Stack Frame entry not found")
            return

        if self.debugger:
            self.debugger.free_alloc_block(offset, offset + frame_to_free.length)
            self.debugger.free_proc_vars(offset, offset + frame_to_free.length)

        self.free_blocks.append(free_block(start=offset, length=frame_to_free.length))

        self.frames.remove(frame_to_free)

    def write(self, type: int, value: Any, offset: int) -> None:
        if type == 0:
            # 2 Byte Word
            data_bytes = self._struct_unpacker_int16.pack(value)
        elif type == 1:
            # 4 Byte Long
            data_bytes = self._struct_unpacker_long.pack(value)
        elif type == 2:
            # Float
            data_bytes = self._struct_unpacker_float.pack(value)
        elif type == 3:
            # QStr
            data_bytes = bytearray([len(value)]) + value.encode("utf-8")
        elif type == 4:
            # 2 byte unsigned word (addr)
            data_bytes = self._struct_unpacker_uint16.pack(value)
        else:
            raise ("Invalid data type - dsf write")

        if self.debugger:
            self.debugger.store_var(type, offset, "Unknown", value, len(data_bytes))

        # Update memory in place
        self.memory[offset : offset + len(data_bytes)] = data_bytes

    def read(
        self, type: int, offset: int, array_index: int = 1
    ) -> Any:  # OPL arrays start at 1
        if type == 0:
            # 2 Byte Word
            return self._struct_unpacker_int16.unpack_from(
                self.memory, offset + 2 * (array_index - 1)
            )[0]
        elif type == 1:
            # 4 Byte Long
            return self._struct_unpacker_long.unpack_from(
                self.memory, offset + 4 * (array_index - 1)
            )[0]
        elif type == 2:
            # 8 Byte Float
            return self._struct_unpacker_float.unpack_from(
                self.memory, offset + 8 * (array_index - 1)
            )[0]
        elif type == 3:
            # Read the string control entry on maximum length
            string_length = self.memory[offset - 1]

            # QStr (read the current length)
            l = self.memory[offset + string_length * (array_index - 1)]
            if l == 0:
                return ""

            return self.memory[
                offset
                + 1
                + string_length * (array_index - 1) : offset
                + 1
                + string_length * (array_index - 1)
                + l
            ].decode("utf-8", "replace")

        raise ("Invalid data type - dsf read")
