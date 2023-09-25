import logging
import logging.config

from pyopo import menu_manager

from pyopo.heap import data_stack
from pyopo.var_stack import stack

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


def qcode_minit(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0xEA - mINIT")

    # Initialise new Menu
    procedure.executable.menu_manager = menu_manager.Menu()


def qcode_mcard(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0xEB - mCARD")

    arg_count = procedure.read_qcode_byte()

    mcard_items = []
    for _ in range(arg_count):
        menu_title, menu_key_shortcut = stack.pop_2()

        mcard_items.append((menu_title, menu_key_shortcut))

        print(f"Menu entry: '{menu_title}' key={menu_key_shortcut}")

    # Reverse the menu item order to be in correct visual order
    mcard_items.reverse()

    mcard_title = stack.pop()
    print(f"Menu Title: {mcard_title}")

    procedure.executable.menu_manager.mCARD(mcard_title, mcard_items)


def qcode_menu_var(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x3A - MENU pop%")

    dsf_offset = stack.pop()
    value = data_stack.read(0, dsf_offset)

    # Init value = 256*(menu%)+item%
    item_index = value % 256
    mcard_index = int(value / 256)

    print(
        f" - Menu init%: {value} at DSF Offset: {dsf_offset} -> {mcard_index}, {item_index}"
    )

    procedure.executable.menu_manager.MENU(mcard_index, item_index)


def qcode_menu(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x36 - MENU")

    procedure.executable.menu_manager.MENU(0, 0)
