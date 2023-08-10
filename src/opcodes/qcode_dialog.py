import struct
import loader
import datetime
import dialog_manager

from filehandler_filesystem import *
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

def qcode_dinit(procedure, data_stack, stack):
    #_logger.debug(f"0xEC - dINIT")

    arg_count = procedure.read_qcode_byte()

    flags = 0
    if arg_count == 2:
        flags = stack.pop()
    
    title = ""
    if arg_count > 0:
        title = stack.pop()

    print(f" - dINIT '{title}' {flags}")

    # Initialise new Dialog
    procedure.executable.dialog_manager = dialog_manager.Dialog(title, flags)
    

def qcode_dtext(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x00 - dTEXT")

    arg_count = procedure.read_qcode_byte()

    text_align = 0
    if arg_count == 1:
        text_align = stack.pop()

    body = stack.pop()
    p = stack.pop()

    print(f" - dTEXT '{p}', '{body}', {text_align}")
    
    procedure.executable.dialog_manager.dTEXT(p, body, text_align)
    

def qcode_dedit_3(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x06 - dEDIT pop=3, pop$2, pop%1")

    max_len = stack.pop()
    prompt = stack.pop()
    addr = stack.pop()

    # Get the current (start value)
    addr_start_val=data_stack.read(3, addr)

    print(f" - dEDIT {addr} = '{addr_start_val}', '{prompt}', {max_len}")
    
    procedure.executable.dialog_manager.dEDIT(addr, addr_start_val, prompt, max_len)

    
def qcode_dlong(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x02 - dLONG pop=4, pop$3, pop&2 pop&1")

    max = stack.pop()
    min = stack.pop()
    prompt = stack.pop()
    addr = stack.pop()

    # Get the current (start value)
    addr_start_val=data_stack.read(1, addr)

    print(f" - dLONG {addr} = {addr_start_val}, '{prompt}', {min} {max}")
    
    procedure.executable.dialog_manager.dLONG(addr, addr_start_val, prompt, min, max)


def qcode_dfloat(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x03 - dFLOAT pop=4, pop$3, pop&2 pop&1")

    max = stack.pop()
    min = stack.pop()
    prompt = stack.pop()
    addr = stack.pop()

    # Get the current (start value)
    addr_start_val=data_stack.read(2, addr)

    print(f" - dFLOAT {addr} = {addr_start_val}, '{prompt}', {min} {max}")
    
    procedure.executable.dialog_manager.dFLOAT(addr, addr_start_val, prompt, min, max)


def qcode_dedit_2(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x06 - dEDIT pop=2, pop$1")

    prompt = stack.pop()
    addr = stack.pop()

    # Get the current (start value)
    addr_start_val=data_stack.read(3, addr)

    print(f" - dEDIT {addr} = '{addr_start_val}', '{prompt}'")
    
    procedure.executable.dialog_manager.dEDIT(addr, addr_start_val, prompt, 255)


def qcode_dchoice(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x01 - dCHOICE pop=3, pop$2, pop$1")

    choice_list = stack.pop()
    prompt = stack.pop()
    addr = stack.pop()

    # Get the current (start value)
    addr_start_val=data_stack.read(0, addr)

    print(f" - dCHOICE {addr} = '{addr_start_val}', '{prompt}', {choice_list}")
    
    procedure.executable.dialog_manager.dCHOICE(addr, addr_start_val, prompt, choice_list)


def qcode_dfile(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x09 - dFILE pop=3, pop$2, pop%1")

    flags = stack.pop()
    prompt = stack.pop()
    addr = stack.pop()

    # Get the current (start value)
    addr_start_val=data_stack.read(3, addr)
    translated_file_path = translate_path_from_sibo(addr_start_val,procedure.executable)

    # Rejoin the paths to the found files and translate back to SIBO
    full_file_paths = list(map(lambda f: translate_path_to_sibo(os.path.join(translated_file_path, f), procedure.executable), os.listdir(translated_file_path)))
    file_selection = ','.join(full_file_paths)

    print(f" - dFILE {addr} = '{addr_start_val}', '{prompt}', {flags}")
    
    addr_start_val = full_file_paths[-1]

    procedure.executable.dialog_manager.dFILE(addr, addr_start_val, file_selection, prompt, flags)

def qcode_dbuttons(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x0A - dBUTTONS")

    arg_count = procedure.read_qcode_byte()

    buttons = []
    for i in range(arg_count):
        char = stack.pop()
        text = stack.pop()
        buttons.append((text, char))
    
    procedure.executable.dialog_manager.dBUTTONS(buttons)


def qcode_dialog(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x37 - DIALOG")

    procedure.executable.dialog_manager.DIALOG()


def qcode_dposition(procedure, data_stack, stack):
    #_logger.debug(f"0xED 0x08 - dPOSITION  pop%2, pop%1")

    y = stack.pop()
    x = stack.pop()

    print(f" - dPOSITION {x}, {y}")
    
    procedure.executable.dialog_manager.dPOSITION(x, y)


def qcode_alert(procedure, data_stack, stack):
    print(f"0x57 0x38 - ALERT")

    n = procedure.read_qcode_byte()
    
    # Defaults
    b3 = None
    b2 = None
    b1 = None
    m2 = None

    if n == 5:
        b3 = stack.pop()
    
    if n >= 4:
        b2 = stack.pop()
        
    if n >= 3:
        b1 = stack.pop()
        
    if n >= 2:
        m2 = None
    m1 = stack.pop()

    # Instead of writing a whole new dialog engine for this one opcode, construct a dialog

    # Initialise new Dialog
    procedure.executable.dialog_manager = dialog_manager.Dialog(m1, 0)

    if m2:
        procedure.executable.dialog_manager.dTEXT(m2, "", 0)

    if b3:
        # Three buttons
        pass
    elif b2:
        # Two buttons
        pass
    elif b1:
        # One button
        pass

    procedure.executable.dialog_manager.DIALOG()