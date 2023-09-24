import logging
import logging.config

from pyopo.heap import data_stack
from pyopo.var_stack import stack

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


def qcode_print_semi(procedure, data_stack: data_stack, stack: stack):
    op_code = procedure.get_executed_opcode()
    _logger.debug(
        f"{hex(op_code)} - PRINT pop+ ; (i.e. with no following space or newline)"
    )

    value = stack.pop()
    _logger.debug(f" - PRINT {value} ; - STUB")


def qcode_style(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0xFF 0x05 - STYLE")

    value = stack.pop()
    procedure.executable.window_manager.text_window.STYLE(value)


def qcode_screen_4(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0xC3 - SCREEN pop%4 pop%3 pop%2 pop%1 - STUB")

    value = stack.pop()
    value = stack.pop()
    value = stack.pop()
    value = stack.pop()
    input()


def qcode_print(procedure, data_stack: data_stack, stack: stack):
    op_code = procedure.get_executed_opcode()
    _logger.debug(f"{hex(op_code)} - PRINT (i.e. newline at end of printing) - STUB")


def qcode_font(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0xFF 0x04 - FONT pop%2 pop%1 - STUB")

    pop_1 = stack.pop()
    pop_2 = stack.pop()


def qcode_at(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x9E - AT pop%2 pop%1")

    x, y = stack.pop_2()
    procedure.executable.window_manager.text_window.AT(x, y)


def qcode_cls(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0xA2 - CLS)")

    procedure.executable.window_manager.text_window.CLS()


def qcode_cursor(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0xA6 - CURSOR")

    cursor_arg = procedure.read_qcode_byte()
    if cursor_arg > 1:
        for i in range(cursor_arg):
            print(stack.pop())

    print(" - STUB")


def qcode_screeninfo(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"0xFF 0x14 - SCREENINFO var%()")

    addr = stack.pop()
    dsf_offset = data_stack.read(0, addr)

    screeninfo = [0] * 10

    """
    
    info%(1) left margin in pixels
    info%(2) top margin in pixels
    info%(3) text screen width in character units
    info%(4) text screen height in character units
    info%(5) reserved (window server id for default window)
    
    """
    screeninfo[0] = 0
    screeninfo[1] = 1
    screeninfo[2] = procedure.executable.window_manager.text_window.width_chars
    screeninfo[3] = procedure.executable.window_manager.text_window.height_chars
    screeninfo[4] = 0

    # Write out gINFO struct to memory
    for i in range(10):
        data_stack.write(0, screeninfo[i], dsf_offset + 2 * i)
