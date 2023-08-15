from filehandler_filesystem import *
from loader import *
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)


def qcode_loadm(procedure, data_stack, stack):

    module_name = stack.pop()
    translated_name = translate_path_from_sibo(module_name, procedure.executable) 
    
    loadm_module = loader.load_executable(translated_name)
    procedure.executable.loadm(loadm_module)

    print(f"0xAE - LOADM {module_name} -> {translated_name}")
    procedure.set_trap(False)