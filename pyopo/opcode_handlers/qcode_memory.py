import logging
import logging.config

from pyopo.heap import data_stack
from pyopo.var_stack import stack

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


def qcode_pokeb(procedure, data_stack: data_stack, stack: stack):
    val = stack.pop()
    addr = stack.pop()

    _logger.debug(f"0x9C - POKEB {addr}, {val}")

    # Push a byte directly into memory
    data_stack.memory[addr] = val


def qcode_poke(procedure, data_stack: data_stack, stack: stack):
    op_code = procedure.get_executed_opcode()
    opcode_type = op_code - 0x98
    val = stack.pop()
    addr = stack.pop()

    _logger.debug(f"{hex(op_code)} - POKE {addr}, {val}")

    # Push a byte directly into memory
    data_stack.write(opcode_type, val, addr)


def qcode_peekb(procedure, data_stack: data_stack, stack: stack):
    addr = stack.pop()
    val = data_stack.memory[addr]

    _logger.debug(f"0x57 0x1B - PEEKB({addr}) -> {val}")
    stack.push(0, val)


def qcode_peekw(procedure, data_stack: data_stack, stack: stack):
    addr = stack.pop()
    val = data_stack.read(0, addr)

    _logger.debug(f"0x57 0x19 - PEEKW({addr}) -> {val}")
    stack.push(0, val)


def qcode_peekf(procedure, data_stack: data_stack, stack: stack):
    addr = stack.pop()
    val = data_stack.read(2, addr)

    _logger.debug(f"0x57 0x8B - PEEKF({addr}) -> {val}")
    stack.push(0, val)


def qcode_alloc(procedure, data_stack: data_stack, stack: stack):
    size = stack.pop()

    # Allocate Dynamic Storage on the heap
    offset = data_stack.allocate_frame(size)

    _logger.debug(f"0x57 0x4B - ALLOC({size}) -> {offset}")

    stack.push(0, offset)


def qcode_peek_str(procedure, data_stack: data_stack, stack: stack):
    addr = stack.pop()
    val = data_stack.read(3, addr)

    _logger.debug(f"0x57 0xCF - PEEK$({addr}) -> {val}")

    stack.push(3, val)
