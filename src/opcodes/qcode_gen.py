import struct
import time
import random

from filehandler_filesystem import *
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

def qcode_usr(procedure, data_stack, stack):
    op_code = procedure.get_executed_opcode()

    #_logger.warning(f'{hex(op_code)} - USR / USR$ - Can not emulate!')
    #_logger.warning(f'USR executes compiled assembly machine code, this can not currently be executed')
    raise('Can not emulate')

def qcode_pause(procedure, data_stack, stack):
    # print(f"{hex(op_code)} - PAUSE pop+1")

    timcode = stack.pop()

    print(f" - PAUSE {timcode}")

    if timcode == 0:
        # Await for keypress
        print(f" - AWAITING KeyPress")
        procedure.executable.pause_await = True
    elif timcode < 0:
        # Await till the sleep period is complete
        print('-PAUSE value, STUB')
        pass
    else:
        # The PAUSE function argument is expressed in 1/20 of a second intervals
        time.sleep(1.0 / 20.0 * float(timcode))

    
def qcode_get(procedure, data_stack, stack):
    #_logger.debug("0x57 0x0A - GET")

    print(f" - AWAITING KeyPress")

    # Getting and storing the keypress is done via the main execution loop
    procedure.executable.get_await = True
    procedure.executable.get_await_str = False
    

def qcode_get_str(procedure, data_stack, stack):
    #_logger.debug("0x57 0xC7 - GET$")

    print(f" - AWAITING KeyPress")

    # Getting and storing the keypress is done via the main execution loop
    procedure.executable.get_await = True
    procedure.executable.get_await_str = True


def qcode_key(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x13 - KEY")

    print(f" - Last Keypress = {procedure.executable.last_keypress}")
    
    stack.push(0,procedure.executable.last_keypress)
    procedure.executable.last_keypress = 0
    
    # Force composition
    procedure.executable.window_manager.composite(procedure.executable, True)


def qcode_cmd(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xD6 - push$ CMD$ pop%")

    cmd_flag = stack.pop()
    cmd_res = ''

    if cmd_flag == 1 or cmd_flag == 2:
        # Full path name used to start the running program (includes loc::)
        print(procedure.executable.file)
        cmd_res = translate_path_to_sibo(procedure.executable.file, procedure.executable, True)
    elif cmd_flag == 3:
        # Launch flags, will return 'O' when launched from the system screen
        cmd_res = "O"
    elif cmd_flag == 4:
        # Alias information, empty string
        pass
    elif cmd_flag == 5:
        # The application name, as declared with the APP keyword.
        cmd_res = 'RunOpl' # For SIBO

    print(f" - CMD({cmd_flag}) = {cmd_res}")

    stack.push(0,cmd_res)


def qcode_goto(procedure, data_stack, stack):
    #_logger.debug("0xBF - GOTO JJ")

    # jmp offset is from the start of the opcode, so negate opcode and opand len
    jmp_offset = procedure.read_qcode_int16() - 3
    
    procedure.set_program_counter_delta(jmp_offset)


def qcode_vector(procedure, data_stack, stack):
    #_logger.debug("0xAB - VECTOR")
    
    pc = procedure.get_program_counter()
    label_count = struct.unpack_from("<H", procedure.procedure["qcode"], pc)[0]
    index = stack.pop()

    if index == 0 or index > label_count:
        # Out of range
        procedure.set_program_counter_delta(2 + 2 * label_count)
    else:
        jmp_offset = struct.unpack_from("<H", procedure.procedure["qcode"], pc + 2 + 2 * (index-1))[0]
        procedure.set_program_counter_delta(jmp_offset -1)
    

def qcode_onerr(procedure, data_stack, stack):
    #_logger.debug(f"0xB1 - ONERR")

    pc = procedure.get_program_counter()
    jmp_offset = struct.unpack_from("<h", procedure.procedure["qcode"], pc)[0]

    if jmp_offset == 0:
        print (' - ONERR OFF')
    else:
        print(f" - ONERR JMP Offset: {jmp_offset}")

    procedure.error_handler_offset = pc + (jmp_offset - 1)
    
    procedure.set_program_counter_delta(2)


def qcode_parse(procedure, data_stack, stack):
    #_logger.debug("0x57 0xD7 - p$=PARSE$(f$,rel$,var off%())")

    off_addr = stack.pop()
    rel = stack.pop()
    f = stack.pop()

    print(f" - PARSE('{f}', '{rel}' -> {off_addr})")

    # Example
    # p$=PARSE$(“NEW”,“LOC::M:\ODB\*.ODB”,x%())
    # sets p$ to LOC::M:\ODB\NEW.ODB and x%() to (1,6,8,13,16,0)

    # off%(1) filing system offset (1 always)
    data_stack.write(0, 1, off_addr)

    if f.startswith('\\'):
        # f resets path
        rel = f"LOC::{procedure.executable.current_drive}:\\{f}"

    # off%(2) device offset (1 always on Series 5 since filing system is not a component of filenames on the Series 5)
    if rel.startswith('LOC::'):
        data_stack.write(0, 6, off_addr + 2)
    else:
        data_stack.write(0, 1, off_addr + 2)

    # off%(3) path offset
    path_offset = rel.find('\\')
    data_stack.write(0, path_offset + 1, off_addr + 4)

    filename = rel.split('\\')[-1]
    file_name = filename.split('.')[0]
    file_ext = filename.split('.')[-1]


    # off%(4) filename offset
    data_stack.write(0, rel.find(file_name) + 1, off_addr + 6)

    # off%(5) file extension offset
    data_stack.write(0, rel.find(file_ext), off_addr + 8)

    # off%(6) flags for wildcards in returned string
    data_stack.write(0, 0, off_addr + 10)

    stack.push(3, rel)


def qcode_giprint(procedure, data_stack, stack):
    #_logger.debug(f"0xFC - GIPRINT")

    pc = procedure.get_program_counter()
    arg_count = int(procedure.procedure["qcode"][pc]) # N' format
    procedure.set_program_counter_delta(1)

    loc = 3 # Bottom Right, default
    if arg_count == 1:
        # gIPRINT str$, c%
        loc = stack.pop()
        
    str_val = stack.pop()
    #_logger.debug(f" - GIPRINT '{str_val}', {loc}")
    
    procedure.executable.window_manager.GIPRINT(str_val, loc)

    
def qcode_cache(procedure, data_stack, stack):
    #_logger.debug("0xFF 0x0E - CACHE")

    cache_arg = procedure.read_qcode_byte() # Qa format

    if cache_arg == 2:
        cache_max = stack.pop()
        cache_min = stack.pop()
        #_logger.debug(f" - CACHE min%={cache_min}, max%={cache_max} - Not implemented")
    else:
        # CACHE ON / OFF
        #_logger.debug(f" - CACHE {bool(cache_arg)} - Not implemented")
        pass

    
def qcode_testevent(procedure, data_stack, stack):

    # GETEVENT returns a limited subset in the emulator
    # e.g. no pen events, no device on/off etc.

    event = -1 if procedure.executable.last_keypress != 0 else 0

    #_logger.debug(f"0x34 - TESTEVENT {event}")
    stack.push(0, event)


def qcode_getevent(procedure, data_stack, stack):
    #_logger.debug("0xE4 - GETEVENT")
    
    addr = stack.pop()
    # GETEVENT returns a limited subset in the emulator
    # e.g. no pen events, no device on/off etc.

    getevent = [procedure.executable.last_keypress, 0]
    
    #_logger.debug(f" - GETEVENT DSF Offset={addr} -> {getevent}")

    data_stack.write(0, getevent[0], addr)
    data_stack.write(0, getevent[1], addr + 2)

    
def qcode_escape(procedure, data_stack, stack):
    #_logger.debug(f"0xA9 - ESCAPE")

    q = procedure.read_qcode_byte() # N' format
    #_logger.warning(f" - ESCAPE {q} - Not Implemented")


def qcode_lock(procedure, data_stack, stack):
    #_logger.debug("0xF1 - LOCK")

    q = procedure.read_qcode_byte() # N' format
    #_logger.warning(f" - LOCK {q} - Not Implemented")


def qcode_busy(procedure, data_stack, stack):
    #_logger.debug("0xF0 - BUSY")

    args = procedure.read_qcode_byte() # N' format

    for i in range(args):
        stack.pop()

    #_logger.warning(f" - BUSY {args} - STUB")


def qcode_statuswin(procedure, data_stack, stack):
    #_logger.debug(f"0xEF - STATUSWIN")

    args = procedure.read_qcode_byte() # N' format

    if args > 1:
        for i in range(args - 1):
            stack.pop()

    #_logger.warning(f" - STATUSWIN {args} - Not Implemented")


def qcode_randomize(procedure, data_stack, stack):
    #_logger.debug("0xB9 - RANDOMIZE pop&1")
    random.seed = stack.pop()
    

def qcode_kmod(procedure, data_stack, stack):
    #_logger.debug("0x57 0x22 - KMOD")

    #_logger.warning(f" - KMOD - Not Implemented")
    input()
    stack.push(0,0)


def qcode_rnd(procedure, data_stack, stack):
    #_logger.debug("0x57 0x8E - push&1 RND")
    stack.push(2, random.random())


def qcode_trap(procedure, data_stack, stack):
    #_logger.debug("0xBC - TRAP")

    # Not used by itself, sets the trap flag for the follow on command
    # Set the flag to newly raised
    procedure.set_trap(True)


def qcode_err_virt(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x07 - ERR")

    # Pushes the virtual flag for ERR

    #_logger.warning(f" - Push virtual ERR value (9999)")
    stack.push(0, 9999)

    
def qcode_beep(procedure, data_stack, stack):
    #_logger.debug("0xA0 - BEEP pop%2 pop% - NOT IMPLEMENTED")

    stack.pop()
    stack.pop()

    
def qcode_eval(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x99 - EVAL pop$1")

    s = stack.pop()

    print(f" - EVAL {s}")

    res = 0.0

    # Check if requesting specific values
    if s in procedure.executable.calc_mem:
        res = procedure.executable.calc_mem[s]
        print(f" - Calculator Memory requested: {s} = {res}")
        input()
    else:
        raise("Unable to EVAL statement")

    stack.push(2,res)


def qcode_err_str(procedure, data_stack, stack):
    #_logger.debug("0x57 0xC4 - push$ ERR$ pop%1 - STUB")

    stack.pop()

    stack.push(3, "An Error has occured")


def qcode_stop(procedure, data_stack, stack):
    #_logger.debug(f"0xBB - STOP")

    # Stop Execution of the program
    procedure.flag_stop = True


def qcode_raise(procedure, data_stack, stack):
    #_logger.debug(f"0xB8 - RAISE")

    err_code = stack.pop()
    #_logger.warning(f"User Error Raised! {err_code}")

    # Stop Execution of the program
    procedure.flag_stop = True


def qcode_diaminit(procedure, data_stack, stack):
    #_logger.debug(f"0xFF 0x02 - DIAMINIT - Not Implemented")

    args = procedure.read_qcode_byte() # DBF D Byte

    for i in range(args):
        stack.pop()


def qcode_diampos(procedure, data_stack, stack):
    #_logger.debug(f"0xFF 0x03 - DIAMPOS - Not Implemented")

    stack.pop()


def qcode_statuswininfo(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x53 - STATWININFO - STUB")

    stack.push(0, 0)