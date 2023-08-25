import struct
import time
import logging
import logging.config

from pyopo import loader

from pyopo.heap import data_stack
from pyopo.var_stack import stack

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


def qcode_open(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0x84 - OPEN pop$1")

    filename = stack.pop()

    # Retrieve DBF D index
    d = procedure.read_qcode_byte()

    _logger.debug(f" - OPEN {d} {filename}")

    dbf_vars = []

    while True:
        type_code = procedure.read_qcode_byte()
        if type_code == 0xFF:
            # End of the list
            break

        pc = procedure.get_program_counter()
        type_name = loader.loader._read_qstr(pc, procedure.procedure["qcode"])
        procedure.set_program_counter_delta(len(type_name) + 1)

        dbf_vars.append((type_code, type_name))
        _logger.debug(f"{type_code} - {type_name}")

    procedure.executable.open_dbf(filename=filename, d=d, vars=dbf_vars, readonly=False)
    procedure.set_trap(False)


def qcode_close(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0xA1 - CLOSE ")
    procedure.executable.close_dbf()
    procedure.set_trap(False)


def qcode_create(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0xA5 - CREATE pop$1")

    filename = stack.pop()

    # Retrieve DBF D Index
    d = procedure.read_qcode_byte()

    _logger.debug(f" - CREATE {d} {filename}")

    dbf_vars = []

    while True:
        type_code = procedure.read_qcode_byte()
        if type_code == 0xFF:
            # End of the list
            break

        pc = procedure.get_program_counter()
        type_name = loader.loader._read_qstr(pc, procedure.procedure["qcode"])
        procedure.set_program_counter_delta(len(type_name) + 1)

        dbf_vars.append((type_code, type_name))
        _logger.debug(f"{type_code} - {type_name}")

    procedure.executable.create_dbf(filename=filename, d=d, vars=dbf_vars)

    procedure.set_trap(False)


def qcode_append(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0x9D - APPEND ")

    for db in procedure.executable.databases:
        if db["d"] == procedure.executable.current_database:
            db["handler"].append()
            break

    procedure.set_trap(False)


def qcode_update(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0xBD - UPDATE ")

    for db in procedure.executable.databases:
        if db["d"] == procedure.executable.current_database:
            db["handler"].update()
            break

    procedure.set_trap(False)


def qcode_use(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0xBE - USE ")

    # Retrieve DBF D Index
    d = procedure.read_qcode_byte()

    procedure.executable.current_database = d
    procedure.set_trap(False)
