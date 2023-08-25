from pyopo.filehandler_filesystem import *
import logging
import logging.config

from pyopo.heap import data_stack
from pyopo.var_stack import stack

from pyopo import pyopo

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


def qcode_loadm(procedure, data_stack: data_stack, stack: stack):
    module_name = stack.pop()
    translated_name = translate_path_from_sibo(module_name, procedure.executable)

    loadm_module = pyopo.executable.load_executable(translated_name)
    procedure.executable.loadm(loadm_module)

    print(f"0xAE - LOADM {module_name} -> {translated_name}")
    procedure.set_trap(False)
