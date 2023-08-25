from typing import Optional, Any, Self
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


class data_stack:
    def __init__(self, size: int, debugger: Optional[DebuggerDSF] = None):
        # Cache struct pack
        self._struct_unpacker_uint16 = struct.Struct("<H")
        self._struct_unpacker_int16 = struct.Struct("<h")
        self._struct_unpacker_float = struct.Struct("<d")
        self._struct_unpacker_long = struct.Struct("<i")

        self.free_blocks = [{"start": 0, "length": size, "end": size - 1}]

        self.frames = []

        # Underlying memory
        self.memory = bytearray(size)

        self.debugger = debugger

    def allocate_frame(self, size: int):
        # Find free block within the data stack
        free_block_index = -1
        for i in range(len(self.free_blocks)):
            if self.free_blocks[i]["length"] >= size:
                free_block_index = i
                break

        if free_block_index == -1:
            raise ("No available memory")

        # Construct Data Stack Frame
        entry = {"size": size, "offset": self.free_blocks[free_block_index]["start"]}
        _logger.info(f"Allocating DSF Size: {size} at Offset: {entry['offset']}")

        if self.debugger:
            self.debugger.store_alloc_block(
                entry["offset"], entry["offset"] + entry["size"]
            )

        if self.free_blocks[free_block_index]["length"] == size:
            # Remove block
            self.free_blocks.pop(free_block_index)
        else:
            # Resize block
            self.free_blocks[free_block_index]["start"] += size
            self.free_blocks[free_block_index]["length"] -= size

        self.frames.append(entry)

        # Reinitialise the frame
        self.memory[entry["offset"] : entry["offset"] + entry["size"]] = (
            b"\x00" * entry["size"]
        )

        return entry["offset"]

    def free_frame(self, offset: int):
        block_index = -1
        for i in range(len(self.frames)):
            if self.frames[i]["offset"] >= offset:
                block_index = i
                break

        if block_index == -1:
            # _logger.warning(f'DSF Frame not found, Offset: {offset} in frames {self.frames}')
            # raise ("Data Stack Frame entry not found")
            return

        if self.debugger:
            self.debugger.free_alloc_block(
                offset, offset + self.frames[block_index]["size"]
            )
            self.debugger.free_proc_vars(
                offset, offset + self.frames[block_index]["size"]
            )

        self.free_blocks.append(
            {
                "start": offset,
                "length": self.frames[block_index]["size"],
                "end": offset + self.frames[block_index]["size"] - 1,
            }
        )

        self.frames.pop(block_index)

    def write(self, type, value, offset):
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

    def read(self, type, offset, array_index=1) -> Any:  # OPL arrays start at 1
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
