import statistics
import logging
import logging.config

from pyopo.heap import data_stack
from pyopo.var_stack import stack

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)

# Types
T_INT_16 = 0
T_INT_32 = 1
T_FLOAT = 2
T_STRING = 3
T_ADDR = 4


def qcode_cmp_less_than(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push% pop+2 < pop+1")

    pop_2, pop_1 = stack.pop_2()

    res = -1 if pop_2 < pop_1 else 0

    # print(f" - {pop_2} < {pop_1} = {res}")

    stack.push(T_INT_16, res)


def qcode_cmp_equals(procedure, data_stack: data_stack, stack: stack):
    # _logger.debug(f"{hex(procedure.get_executed_opcode())} - push% pop+2 == pop+1  (compare, not assign)")

    res = -1 if stack.pop() == stack.pop() else 0
    stack.push(T_INT_16, res)


def qcode_cmp_not_equals(procedure, data_stack: data_stack, stack: stack):
    # _logger.debug(f"{hex(procedure.get_executed_opcode())} - push% pop+2 != pop+1")

    res = -1 if stack.pop() != stack.pop() else 0
    stack.push(T_INT_16, res)


def qcode_cmp_greater_equal(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push% pop+2 >= pop+1")

    pop_2, pop_1 = stack.pop_2()

    res = -1 if pop_2 >= pop_1 else 0
    stack.push(T_INT_16, res)


def qcode_cmp_greater(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push% pop+2 > pop+1")

    pop_2, pop_1 = stack.pop_2()

    res = -1 if pop_2 > pop_1 else 0
    stack.push(T_INT_16, res)


def qcode_cmp_less_than_equal(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push% pop+2 >= pop+1")

    pop_2, pop_1 = stack.pop_2()

    res = -1 if pop_2 <= pop_1 else 0

    # print(f" - {pop_2} <= {pop_1} = {res}")

    stack.push(T_INT_16, res)


def qcode_cmp_if(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - if pop% is zero, jump to JJ")

    jmp_offset = procedure.read_qcode_int16()

    # Jump if 0
    if stack.pop() == 0:
        # Jump offsets are relative to start of the current opcode, as we have already progressed the counter, minus 3 from it.
        procedure.set_program_counter_delta(jmp_offset - 3)


def qcode_cmp_and(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push% pop+2 AND pop+1")

    pop_2, pop_1 = stack.pop_2()

    arg_type = procedure.get_executed_opcode() - 0x5C

    if arg_type == 0 or arg_type == 1:
        # Bitwise not for word and long
        res = int(pop_2) & int(pop_1)
    else:
        # True if 0, False otherwise
        res = -1 if (pop_1 != 0 and pop_2 != 0) else 0

    # print(f" - {pop_2} AND {pop_1} = {res}")

    stack.push(T_INT_16, res)


def qcode_cmp_not(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push+ NOT pop+")

    pop_1 = stack.pop()

    arg_type = procedure.get_executed_opcode() - 0x64

    if arg_type == 0 or arg_type == 1:
        # Bitwise not for word and long
        res = ~int(pop_1)
    else:
        # True if 0, False otherwise
        res = -1 if pop_1 == 0 else 0

    # print(f" - NOT {pop_1} = {res}")

    stack.push(T_INT_16, res)


def qcode_cmp_or(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push% pop+2 OR pop+1")

    pop_2, pop_1 = stack.pop_2()

    arg_type = procedure.get_executed_opcode() - 0x60

    if arg_type == 0 or arg_type == 1:
        # Bitwise or for word and long
        res = int(pop_2) | int(pop_1)
    else:
        # True if either are non-zero, False otherwise
        res = 0 if (pop_1 == 0 and pop_2 == 0) else -1

    # print(f" - {pop_2} OR {pop_1} = {res}")

    stack.push(T_INT_16, res)


def qcode_max(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x93 - Na MAX")
    na = procedure.read_qcode_byte()

    max_value = max(get_na_array_list(na, data_stack, stack))

    stack.push(T_FLOAT, max_value)


def qcode_min(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x95 - Na MIN")
    na = procedure.read_qcode_byte()

    max_value = min(get_na_array_list(na, data_stack, stack))

    stack.push(T_FLOAT, max_value)


def qcode_mean(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x94 - Na MEAN")
    na = procedure.read_qcode_byte()

    num_list = get_na_array_list(na, data_stack, stack)
    max_value = sum(num_list) / min(1, len(num_list))

    stack.push(T_FLOAT, max_value)


def qcode_std(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x96 - Na STD")
    na = procedure.read_qcode_byte()

    max_value = statistics.stdev(get_na_array_list(na, data_stack, stack))

    stack.push(T_FLOAT, max_value)


def qcode_sum(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x97 - Na SUM")
    na = procedure.read_qcode_byte()

    max_value = sum(get_na_array_list(na, data_stack, stack))

    stack.push(T_FLOAT, max_value)


def qcode_var(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x98 - Na VAR")
    na = procedure.read_qcode_byte()

    max_value = statistics.variance(get_na_array_list(na, data_stack, stack))

    stack.push(T_FLOAT, max_value)


def get_na_array_list(na: int, data_stack: data_stack, stack: stack) -> list[float]:
    """Retrieves arguments for list operation opcodes.

    The list of float arguments is either popped from the stack given an na value, or
    retrieved from the datastack"""
    if na == 0:
        # Special case, array addr & number of elements
        element_count = stack.pop()
        addr = stack.pop()

        return [
            data_stack.read(T_FLOAT, addr + (element_count - 1) * 8)
            for _ in range(element_count)
        ]
    else:
        # Equivalent to popping the number of items
        return [stack.pop() for _ in range(na)]
