import struct
import json
import sys
import os
import time
import pygame
from pygame.locals import *
from typing import Optional, Any, Self, Dict

from .loader import *


from .opcodes import *
from .window_manager import WindowManager
from .dialog_manager import *
from .filehandler_dbf import *
from .filehandler_filesystem import *

from .hals import *

from .heap import *

# Debuggers
from .debugger.debugger_dsf import DebuggerDSF
from .debugger.debugger_profiler import DebuggerProfiler

DATA_STACK_FRAME_SIZE = 64 * 1024

import logging
import logging.config

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)

PROFILE_DUMP_TIMESPAN = 120

UI_FPS = 15

KEY_TRANSLATION = {
    pygame.K_LALT: 290,  # Menu
    pygame.K_RALT: 291,  # Help
    pygame.K_UP: 256,
    pygame.K_DOWN: 257,
    pygame.K_RIGHT: 258,
    pygame.K_LEFT: 259,
    pygame.K_BACKSPACE: 8,  # Psion did not have a backspace, treat as delete
    pygame.K_DELETE: 8,
}


class executable:
    def __init__(
        self,
        file: str,
        binary: bytes,
        header: opo_header,
        procedure_table,
        embedded_files,
    ):
        self.file = file
        self.binary = binary
        self.header = header
        self.procedure_table = procedure_table

        # Create a ref cache of the proc table for faster lookups
        self.update_procedure_call_cache()

        # Modules (LOADM)
        self.modules = []

        # Databases
        self.current_database = None
        self.databases = []

        # Information on the internal location and type of embedded files.
        self.embedded_files = embedded_files

        # Debugging Tools
        self.memory_debugger = None
        self.profiler_debugger = None

        # Graphical Emulation Layers
        self.window_manager = WindowManager(executable=self)
        self.dialog_manager = None
        self.menu_manager = None

        # Drive Abstraction
        self.drive_path = os.path.join(os.path.dirname(str(__file__)), "DRIVE")

        self.current_drive = "M"
        self.current_path = "APP"

        # Stores the character code of the last key that was pressed, Dialogs, Menus and other commands will reset this to 0
        self.last_keypress = 0

        # If true, we pause execution until the user presses a key
        self.get_await = False
        self.get_await_str = (
            False  # If True, the character is stored, else the character code
        )

        # Awaiting for a pause event
        self.pause_await = False

        # Runtime information
        self.proc_stack = []

        # Cached ref to current executing procedure
        self._current_proc: stack_entry = None

        self.stack = stack()
        self.data_stack = data_stack(
            DATA_STACK_FRAME_SIZE, debugger=self.memory_debugger
        )  # 32kb base memory

        # io handles
        self.io_handles = []

        # Abstraction layers for io functionality to specific resources
        self.io_hals = {"TIM:": hal_tim(self.data_stack)}

        # Calculator Memory
        self.calc_mem = {
            "m0": 0.0,
            "m1": 0.0,
            "m2": 0.0,
            "m3": 0.0,
            "m4": 0.0,
            "m5": 0.0,
            "m6": 0.0,
            "m7": 0.0,
            "m8": 0.0,
            "m9": 0.0,
        }

    def update_procedure_call_cache(self) -> None:
        """Caches procedures to the first instance of each name"""

        self.procedure_table_caller_lookup = {}

        for proc in self.procedure_table:
            proc_name = proc["name"].upper()

            if proc_name not in self.procedure_table_caller_lookup:
                self.procedure_table_caller_lookup[proc_name] = proc

    @staticmethod
    def load_executable(file: str) -> Self:
        """Loads a .OPO or .OPA file, returning its runtime environment"""

        binary = None
        with open(file, "rb") as f:
            binary = f.read()

        header = loader._readheader(binary)

        embedded_files = []
        embedded_files_offset = 20 + 1 + len(header.source_filename)
        if header.second_header_offset != embedded_files_offset:
            # If the Second Header Offset is more than offset 20 + QStr, then there is embedded files
            _logger.info(f"{embedded_files_offset} vs {header.second_header_offset}")
            embedded_files = loader._readembeddedfiles(
                binary, embedded_files_offset, header.second_header_offset
            )

        procedure_table = loader._read_procedure_table(
            header.procedure_table_offset, header.translator_version, binary, file
        )

        return executable(file, binary, header, procedure_table, embedded_files)

    def set_filesystem_path(self, path: str) -> None:
        """Sets the local filesystem location to the base of the emulated Psion filesystem"""
        self.drive_path = path

    def attach_dsf_debugger(self) -> None:
        """Attach debug and analysis tooling to the Heap and Data Stack Frames contained therein"""
        self.memory_debugger = DebuggerDSF(
            executable=self, dsf_size=DATA_STACK_FRAME_SIZE
        )

    def attach_profiler(self) -> None:
        """Attach a performance profiling tool to the interpreter"""
        self.profiler_debugger = DebuggerProfiler()

    def __str__(self):
        return self.file

    def loadm(self, module: Self) -> None:
        """Runtime support for the LOADM OPL Command"""
        self.modules.append(module)

        self.procedure_table.extend(module.procedure_table)

        # Rebuild the caller cache
        self.update_procedure_call_cache()

    def unloadm(self, module: Self) -> None:
        """Runtime support for the UNLOADM OPL Command"""
        raise NotImplementedError()

    def get_proc_name(self) -> str:
        if len(self.proc_stack) == 0:
            return ""

        return self._current_proc.procedure["name"]

    def get_top_proc_instance_for_name(self, proc_name: str):
        for proc in reversed(self.proc_stack):
            if proc.procedure["name"] is proc_name:
                return proc

        raise ValueError

    def execute(self):
        # Add first procedure to the stack
        self.proc_stack.append(stack_entry(self.procedure_table[0].copy(), self))
        self._current_proc = self.proc_stack[-1]  # Cache ref

        profiling_starttime = time.time()

        while True:
            # Process the PyGame inputs in the event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _logger.info("User has triggered App exit")
                    pygame.quit()
                    return

                # checking if keydown event happened or not
                if event.type == pygame.KEYDOWN:
                    # if keydown event happened
                    # than printing a string to output

                    # Translate certain keys
                    if event.key in KEY_TRANSLATION:
                        # Left Alt = MENU
                        _logger.info(
                            f" - Translating {pygame.key.name(event.key)} to {KEY_TRANSLATION[event.key]}"
                        )
                        self.last_keypress = KEY_TRANSLATION[event.key]
                    elif event.key < 255:
                        # Only store the values of the keys that are in range
                        _logger.info(f"A key has been pressed: {event.key}")
                        self.last_keypress = event.key
                    else:
                        continue

                    if self.dialog_manager and self.dialog_manager.show:
                        # Handle the Keypress in respect to the dialog

                        if event.key == pygame.K_ESCAPE:
                            # Exit the dialog
                            _logger.info("User has quit the dialog, not saving results")
                            self.stack.push(0, 0)

                            self.dialog_manager = None  # Clean up dialog

                            # The KEY value (last keypress) is result on dialog completion
                            self.last_keypress = 0
                            self.window_manager.composite(self, True)

                        elif (
                            event.key == pygame.K_RETURN
                            or event.key in self.dialog_manager.get_button_keycodes()
                        ):
                            # Exit the dialog

                            _logger.debug("Store results of dialog")
                            dialog_return_val = self.dialog_manager.handle_DIALOG(
                                self.data_stack
                            )

                            if dialog_return_val == None:
                                dialog_return_val = int(event.key)

                            # Add the dialog return to the stack
                            self.stack.push(0, dialog_return_val)

                            self.dialog_manager = None  # Clean up dialog

                            # The KEY value (last keypress) is result on dialog completion
                            self.last_keypress = 0
                            self.window_manager.composite(self, True)
                        else:
                            # Pass over the keypress to the dialog manager
                            self.dialog_manager.handle_keypress(self.last_keypress)
                    elif self.menu_manager and self.menu_manager.show:
                        if event.key == pygame.K_ESCAPE:
                            # Exit the dialog
                            _logger.info("User has quit the menu, not saving results")
                            self.stack.push(0, 0)

                            self.menu_manager = None  # Clean up menu

                            # The KEY value (last keypress) is result on dialog completion
                            self.last_keypress = 0
                        elif event.key == pygame.K_RETURN:
                            # Exit the menu

                            _logger.info("Store results of menu")
                            menu_return_val = self.menu_manager.handle_MENU()

                            # Add the char of the selected menu option
                            self.stack.push(0, menu_return_val)

                            self.menu_manager = None  # Clean up Menu

                            # The KEY value (last keypress) is result on menu completion
                            self.last_keypress = 0
                        else:
                            self.menu_manager.handle_keypress(event.key)
                    elif self.get_await:
                        # The program has paused execution while awaiting for a key to be pressed, this is now complete
                        self.get_await = False

                        # Push the last character to the stack for consumption
                        if self.get_await_str:
                            _logger.debug(f" - GET$ = {self.last_keypress}")
                            self.stack.push(3, chr(self.last_keypress))
                        else:
                            _logger.debug(f" - GET = {self.last_keypress}")
                            self.stack.push(0, self.last_keypress)

                        self.last_keypress = 0

                        # Force composition
                        self.window_manager.composite(self, True)
                    elif self.pause_await:
                        self.pause_await = False

            # Determine if we need to pause execution while awaiting a key press or action
            awaiting_action = self.get_await or self.pause_await
            awaiting_action = (
                awaiting_action
                or (self.dialog_manager and self.dialog_manager.show)
                or (self.menu_manager and self.menu_manager.show)
            )

            if awaiting_action:
                self.window_manager.composite(self)

                _logger.debug(" - AWAITING KEYPRESS")

                time.sleep(1.0 / UI_FPS)  # Simulate 30FPS
                continue

            # Handle any awaiting IO actions
            for hal_ref in self.io_hals.values():
                hal_ref.process_io()

            # Execute instruction from the topmost procedure
            check_flags = self._current_proc.execute_instruction()

            # Composite the applications graphics
            last_render_delta = (
                datetime.datetime.now() - self.window_manager.last_render_time
            )
            if last_render_delta.microseconds > 1000000 / UI_FPS:
                self.window_manager.composite(self)

            if check_flags:
                # The execution resulted in flags being set

                if self._current_proc.flag_stop:
                    _logger.info(" - User has requested application STOP")
                    break
                elif self._current_proc.flag_callproc:
                    # The Callee Procedure has flagged it is calling another procedure

                    # Via LOADM there may be more than 1 instance of a procedure with the same name.

                    proc_call = self.procedure_table_caller_lookup.get(
                        self._current_proc.flag_callproc.upper(), None
                    )

                    if not proc_call:
                        # Unable to find named procedure
                        raise ("Procedure not found")

                    """
                    proc_call = list(
                        filter(
                            lambda p: p["name"].upper()
                            == self._current_proc.flag_callproc.upper(),
                            self.procedure_table,
                        )
                    )
                    if len(proc_call) == 0:
                        # Unable to find named procedure
                        proc_names = list(
                            map(lambda p: p["name"].upper(), self.procedure_table)
                        )
                        _logger.warn("Unable to determine CALLEE PROC")
                        _logger.warn(proc_names)
                        raise ("Procedure not found")
                    elif len(proc_call) > 0:
                        _logger.warning(
                            f"More than one procedure entry exists for {self._current_proc.flag_callproc.upper()}"
                        )
                    """

                    # Reset the procedure calling flag
                    self._current_proc.flag_callproc = None

                    # Add the called procedure to the stack
                    self.proc_stack.append(stack_entry(proc_call, self))
                    self._current_proc = self.proc_stack[-1]

                    # OPO adds 2 stack entries per param when calling, verify type codes and remove them
                    for param in self._current_proc.procedure["parameters"]:
                        param["value"], callee_type = self.stack.pop_2()

                        if param["type"] != callee_type:
                            raise ("Invalid PROC call, type mismatch")

                elif self._current_proc.flag_return:
                    # The procedure is being returned, or has completed execution

                    # Free procedure memory
                    self.data_stack.free_frame(
                        self._current_proc.data_stack_frame_offset
                    )

                    # Remove the procedure from the stack, carry on previous procedure
                    self.proc_stack.pop()

                    if len(self.proc_stack) == 0:
                        _logger.info("Application has completed execution")
                        break

                    self._current_proc = self.proc_stack[-1]  # Cache new ref

                    _logger.info(
                        f" - Returning execution to PROC {self._current_proc.procedure['name']}"
                    )
                else:
                    # Other Flag occured
                    break

            if time.time() - profiling_starttime > PROFILE_DUMP_TIMESPAN:
                break

        if self.profiler_debugger:
            # Dump out debug information if the profiler is attached
            self.profiler_debugger.dump_timings()

    def open_dbf(self, filename: str, d: int, vars, readonly):
        self.databases.append(
            {
                "handler": dbf(executable=self, filename=filename),
                "d": d,
                "vars": vars,
                "readonly": readonly,
            }
        )

        # Load the DBF header information
        self.databases[-1]["handler"].load()

        # Set the current active database to that which has just loaded
        self.current_database = d

    def create_dbf(self, filename, d, vars):
        self.databases.append(
            {
                "handler": dbf(executable=self, filename=filename),
                "d": d,
                "vars": vars,
                "readonly": False,
            }
        )

        self.databases[-1]["handler"].create()
        self.databases[-1]["handler"].create_record_header(vars)

        # Set the current active database to that which has just loaded
        self.current_database = d

    def close_dbf(self):
        # Perform cleanup

        # Free up database resources of that which is currently active
        active_db = None
        for db in self.databases:
            if db["d"] == self.current_database:
                active_db = db
                break

        self.databases.remove(active_db)


class stack_entry:
    STRUCT_UNPACKER_UINT16 = struct.Struct("<H")
    STRUCT_UNPACKER_INT16 = struct.Struct("<h")
    STRUCT_UNPACKER_INT32 = struct.Struct("<i")
    STRUCT_UNPACKER_FLOAT64 = struct.Struct("<d")

    def __init__(self, procedure_table_entry, executable):
        # Cache for EE references used by the procedure
        self.ee_dsf_cache: Dict[int, int] = {}

        # Link to the parent executable
        self.executable = executable

        self.procedure = procedure_table_entry

        # The program counter, the iterator of the current qcode offset
        self._program_counter = 0

        # The bytecode for the procedure entry
        self._qcode: bytes = self.procedure["qcode"]
        self._qcode_len = len(self._qcode)

        self._last_executed_opcode = None

        # DIR$ returns an iterator, which is stored to the procedure
        self.dir_responses = []

        # TRAP is an error handling command to wrap an individual op_code
        self._op_code_trapped = False

        # Procedure Flags
        self.flag_stop = False
        self.flag_return = False
        self.flag_error = False
        self.flag_callproc = None

        # Error Handling
        self.error_handler_offset = 0

        # Allocate Procedure Memory
        self.data_stack_frame_offset = self.executable.data_stack.allocate_frame(
            size=self.procedure["data_stack_frame_size"]
        )

        # Populate Data Stack Frame with array/string information
        for str_dec in self.procedure["string_declarations"]:
            self.executable.data_stack.memory[
                self.data_stack_frame_offset + str_dec
            ] = self.procedure["string_declarations"][str_dec]["length"]

        for arr_dec in self.procedure["array_declarations"]:
            self.executable.data_stack.write(
                0,
                arr_dec["length"],
                self.data_stack_frame_offset + arr_dec["data_stack_frame_offset"],
            )

    def set_program_counter(self, index: int) -> None:
        self._program_counter = index

    def set_program_counter_delta(self, delta: int) -> None:
        self._program_counter += delta

    def get_program_counter(self) -> int:
        return self._program_counter

    def get_executed_opcode(self) -> int:
        return self._last_executed_opcode

    def set_trap(self, value) -> None:
        self._op_code_trapped = value

    def get_graphics_context(self):
        return self.executable.window_manager.cursor()

    def get_window_manager(self):
        return self.executable.window_manager

    def get_data_stack_context(self):
        return self.executable.data_stack

    def read_qcode_byte(self) -> int:
        """Read the next byte in the qcode sequence and iterate the program counter"""
        val = self._qcode[self._program_counter]
        self._program_counter += 1
        return int(val)

    def read_qcode_int16(self) -> int:
        """Read the next signed 16bit integer from the qcode sequence and iterate the program counter accordingly"""
        val = stack_entry.STRUCT_UNPACKER_INT16.unpack_from(
            self._qcode, self._program_counter
        )[0]
        self._program_counter += 2
        return val

    def read_qcode_uint16(self) -> int:
        """Read the next unsigned 16bit integer from the qcode sequence and iterate the program counter accordingly"""
        val = stack_entry.STRUCT_UNPACKER_UINT16.unpack_from(
            self._qcode, self._program_counter
        )[0]
        self._program_counter += 2
        return val

    def read_qcode_long(self) -> int:
        """Read the next signed 32bit integer (OPL Long) from the qcode sequence and iterate the program counter accordingly"""
        val = stack_entry.STRUCT_UNPACKER_INT32.unpack_from(
            self._qcode, self._program_counter
        )[0]
        self._program_counter += 4
        return val

    def read_qcode_float(self) -> int:
        """Read the next 64bit IEEE Float from the qcode sequence and iterate the program counter accordingly"""
        val = stack_entry.STRUCT_UNPACKER_FLOAT64.unpack_from(
            self._qcode, self._program_counter
        )[0]
        self._program_counter += 8
        return val

    def execute_instruction(self) -> bool:
        if self._program_counter >= self._qcode_len:
            # Finished execution of the procedure by hitting the end of the QCode
            _logger.info("Procedure Execution Complete")
            self.flag_return = True
            return True

        op_code = self.read_qcode_byte()
        opcode_hint = None

        op_code_handler = None

        if op_code == 0x53:
            # Call a procedure
            ee = self.read_qcode_uint16()

            cp_match = self.procedure["cached_cp"].get(ee, None)
            if not cp_match:
                _logger.warning("Failed to determine called procedure")
                self.flag_error = True
                return True

            self.flag_callproc = cp_match["name"]
            _logger.info(
                f" - PROCEDURE CALL! EE Ref {ee} - Calling PROC {self.flag_callproc}:"
            )

            return True
        elif op_code == 0x6B:
            # @(...) operator - Call a procedure
            args = self.read_qcode_byte()
            return_type = self.read_qcode_byte()
            _logger.info(f"Return Type: {return_type}")

            for _ in range(args):
                # Retrieve the arguments
                type_code = self.executable.stack.pop()
                arg_name = self.executable.stack.pop()

            # We do not currently use the arguments to validate the callee

            self.flag_callproc = self.executable.stack.pop()

            # Add in the type code to the calling proc name, return type 0 is float
            if return_type != 0:
                # Floats don't have a return type character as they do not have a symbol
                self.flag_callproc += chr(return_type)

            _logger.info(
                f" - Calling @ PROC {self.flag_callproc}(args = {args}) Return type = {return_type}:"
            )

            return True

        elif op_code == 0x57:
            # Opcode subset with 0x57 hint
            opcode_hint = 0x57
            op_code = self.read_qcode_byte()
            _logger.debug(
                f"Opcode: 0x57 {hex(op_code)} - {self._program_counter-1} / {self.procedure['qcode_len']}"
            )

            op_code_handler = opcode_0x57_handler.get(op_code)
        elif op_code in [0x74, 0x75, 0x76, 0x77]:
            _logger.info(" - 0x74 - 0x77 RETURN called")

            # Store default values (none provided)
            if op_code == 0x74:
                self.executable.stack.push(0, 0)
            elif op_code == 0x75:
                self.executable.stack.push(1, 0)
            elif op_code == 0x76:
                self.executable.stack.push(2, 0.0)
            elif op_code == 0x77:
                self.executable.stack.push(3, "")

            self.flag_return = True
            return True
        elif op_code == 0xC0:
            _logger.info(
                f" - 0xCO RETURN pop+ called - {self._program_counter} / {self.procedure['qcode_len']} / {len(self.executable.stack.stack_frame)}"
            )
            self.flag_return = True
            return True
        elif op_code == 0xED:
            # Opcode subset with 0xED hint
            opcode_hint = 0xED
            op_code = self.read_qcode_byte()
            _logger.debug(
                f"Opcode: 0xED {hex(op_code)} - {self._program_counter-1} / {self.procedure['qcode_len']} / {len(self.executable.stack.stack_frame)}"
            )

            op_code_handler = opcode_0xED_handler.get(op_code)

        elif op_code == 0xFF:
            # Opcode subset with 0xFF hint
            opcode_hint = 0xFF
            op_code = self.read_qcode_byte()
            _logger.debug(
                f"Opcode: 0xFF {hex(op_code)} - {self._program_counter-1} / {self.procedure['qcode_len']} / {len(self.executable.stack.stack_frame)}"
            )

            op_code_handler = opcode_0xFF_handler.get(op_code)

        elif op_code in opcode_handler:
            # Execute the Opcode

            _logger.debug(
                f"Opcode: {hex(op_code)} - {self._program_counter} / {self.procedure['qcode_len']} / {len(self.executable.stack.stack_frame)}"
            )
            op_code_handler = opcode_handler[op_code]

        if op_code_handler:
            try:
                opcode_starttime = time.time()
                self._last_executed_opcode = op_code
                op_code_handler(self, self.executable.data_stack, self.executable.stack)
                opcode_endtime = time.time()
                opcode_duration = opcode_endtime - opcode_starttime

                if self.executable.profiler_debugger:
                    self.executable.profiler_debugger.store_timing(
                        opcode_duration, self._last_executed_opcode, opcode_hint
                    )
            except Exception as e:
                if self._op_code_trapped:
                    # _logger.warning(f" - Error Occured and Trapped: {e}")
                    pass
                else:
                    # No error handling was present
                    raise (e)
        else:
            # _logger.error(f"Opcode not yet implemented: {hex(opcode_hint) if opcode_hint else ''} {hex(op_code)}")
            self.flag_error = True
            return True

        return self.flag_stop
