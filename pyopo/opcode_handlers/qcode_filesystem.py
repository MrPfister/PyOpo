import struct
import time
import random
import json
import os
from pyopo.filehandler_filesystem import *
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

SPECIAL_IO_HANDLES = ['TIM:']


def qcode_dir(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xC3 - push$ DIR$ pop$")

    d = stack.pop()

    if d != '':
        # Generate new Directory listing
        translated_d = translate_path_from_sibo(d, procedure.executable)
        files_in_dir = os.listdir(translated_d)

        procedure.dir_responses = list(
            map(lambda f: translate_path_to_sibo(f, procedure.executable), files_in_dir))

    if len(procedure.dir_responses) == 0:
        dir_response = ''
    else:
        dir_response = procedure.dir_responses.pop()

    print(f" - DIR$({d}) = {dir_response}")
    input()

    stack.push(3, dir_response)


def qcode_trap(procedure, data_stack, stack):
    #_logger.debug(f"0xBC - TRAP")

    # Not used by itself, sets the trap flag for the follow on command
    procedure.set_trap(True)


def qcode_setpath(procedure, data_stack, stack):
    #_logger.debug(f"0xFA - SETPATH pop$1")

    new_path = stack.pop()

    procedure.executable.current_path = new_path

    translated_d = translate_path_from_sibo(new_path, procedure.executable)

    print(f" - SETPATH {new_path} Translated: {translated_d}")
    input()


def qcode_mkdir(procedure, data_stack, stack):
    #_logger.debug(f"0xF8 - MKDIR pop$1")

    d = stack.pop()

    translated_d = translate_path_from_sibo(d, procedure.executable)

    print(f" - MKDIR {d} Translated: {translated_d}")

    os.mkdir(translated_d)
    procedure.set_trap(False)


def qcode_exist(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x08 - push% EXIST pop$")

    d = stack.pop()

    translated_d = translate_path_from_sibo(d, procedure.executable)

    exists = -1 if os.path.exists(translated_d) else 0

    print(f" - EXIST {d} Translated: {translated_d} = {exists}")

    stack.push(0, exists)  # False


def qcode_delete_file(procedure, data_stack, stack):
    print(f"0xA7 - DELETE pop$")

    d = stack.pop()

    translated_d = translate_path_from_sibo(d, procedure.executable)

    print(f" - DELETE {d} Translated: {translated_d}")
    print("stub")
    input()
    
    procedure.set_trap(False)


def qcode_ioa(procedure, data_stack, stack):
    print(f"0x57 0x0B - IOA")

    # handle%,func%,var status%,var arg1,var arg2

    arg2_addr = stack.pop()
    arg1_addr = stack.pop()
    status_addr = stack.pop()
    func = stack.pop()
    handle = stack.pop()

    print(f" - IOA {handle}, {func}, {status_addr}, {arg1_addr}, {arg2_addr}")

    ret = 0

    for io_obj in procedure.executable.io_handles:
        if handle == io_obj['io_handle']:

            if io_obj['sibo_filename'] == 'TIM:':
                print('IO operation on TimeServer')

                if func == 1:
                    # Timer request
                    procedure.executable.io_hals["TIM:"].add_timer(
                        status_addr, arg1_addr)

                    # Signal is set to -46 to start with
                    ret = -46
                elif func == 2:
                    # Alarm request
                    print("TIM: Alarm request - Not yet implemented")
                    input()

            break

    stack.push(0, ret)


def qcode_iowaitstat(procedure, data_stack, stack):
    print(f"0xE8 - IOWAITSTAT")

    status_addr = stack.pop()

    print(f" - IOWAITSTAT {status_addr}")

    found_entry = False
    for hal_io_obj in procedure.executable.io_hals:
        if procedure.executable.io_hals[hal_io_obj].has_handle(status_addr):
            print('IO operation on TimeServer')

            procedure.executable.io_hals["TIM:"].iowaitstat(status_addr)
            found_entry = True
            break

    if not found_entry:
        print('Could not find corresponding status var in io')
        input()


def qcode_iosignal(procedure, data_stack, stack):
    print(f"0xB7 - IOSIGNAL")

    print(f" - IOSIGNAL - STUB")


def qcode_iowait(procedure, data_stack, stack):
    #_logger.debug("0x57 0x11 - IOWAIT - STUB")
    pass


def qcode_ioopen(procedure, data_stack, stack):
    print(f"0x57 0x0D- push% IOOPEN pop_ADDR%,pop$,pop%1")

    # ret%=IOOPEN(var handle%,name$,mode%)

    mode = stack.pop()
    filename = stack.pop()
    addr = stack.pop()

    # Generate an io_handle_value, as the latest entry in the handle list
    io_handle = 1024 + len(procedure.executable.io_handles)

    # Create default struct for io object
    io_obj = {
        'random_access': False,
        'sharable': False,
        'read_only': True,
        'var_length_records': False,
        'open_mode': 0,
        'io_handle_addr': addr,
        'io_handle': io_handle,
        'sibo_filename': filename
    }

    # Unpack mode

    # Mode Category 3: Access Flags
    if mode >= 0x0400:
        # Open for sharing - This is ignored for this runtime as only one executuble can run concurrently
        io_obj['sharable'] = True
        mode -= 0x0400

    if mode >= 0x0200:
        io_obj['random_access'] = True
        mode -= 0x0200

    if mode >= 0x0100:
        io_obj['read_only'] = True
        mode -= 0x0100

    # Mode Category 2: File Format
    if mode >= 0x0020:
        io_obj['var_length_records'] = True
        mode -= 0x0020

    # Mode Category 1: Open Mode
    if mode >= 0x0004:
        raise ('Invalid IOOPEN Mode')
    else:
        io_obj['open_mode'] = mode

    translated_name = translate_path_from_sibo(filename, procedure.executable)

    io_obj['io_filename'] = translated_name

    print(io_obj)

    print(
        f" - IOOPEN handle={addr}, Translated File={translated_name}, {mode}")

    ret = 0  # Default result state

    # Perform additional validation checks dependent on the open mode
    open_mode = "r+"
    if io_obj['sibo_filename'] not in SPECIAL_IO_HANDLES:
        # Special IO Handles e.g. TIM: do not check existence
        if io_obj['open_mode'] == 0:
            # Open an existing file
            if not os.path.exists(translated_name):
                # The file does not exist
                ret = -1
        elif io_obj['open_mode'] == 1:
            # Create a file that does not exist
            if os.path.exists(translated_name):
                # The file already exists
                ret = -1

            open_mode = "w+"
        elif io_obj['open_mode'] == 2:
            # Create a new file or replace an existing file
            open_mode = "w+"

        elif io_obj['open_mode'] == 3:
            # Append to an existing file
            open_mode = "a+"

    open_mode = 'b' + open_mode  # Requires byte access to the file

    if ret != -1:
        print(filename)
        print(json.dumps(io_obj, indent=4))

        # Handle to the underlying obj, not what is returnend
        if io_obj['sibo_filename'] not in SPECIAL_IO_HANDLES:
            # Standard file
            io_obj['handle'] = open(translated_name, open_mode)
        elif io_obj['sibo_filename'] == 'TIM:':
            # User is trying to access time
            io_obj['handle'] = 0

        procedure.executable.io_handles.append(io_obj)

        # Write out the io handle to the handle addr specified
        data_stack.write(0, io_obj['io_handle'], addr)

    stack.push(0, ret)


def qcode_ioread(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x0F - push% IOREAD pop%,pop%,pop%)")

    maxlen = stack.pop()
    addr = stack.pop()
    handle = stack.pop()

    print(f" - IOREAD h%={handle}, addr%={addr}, len%={maxlen}")

    ret = -1  # Error occured, invalid handle
    for io_obj in procedure.executable.io_handles:
        if handle == io_obj['io_handle']:

            read_chars = io_obj['handle'].read(maxlen)

            # Replace null characters
            # read_chars = read_chars.decode().replace('\0', '')

            print(
                f" - IOREAD {len(read_chars)} characters read: '{read_chars}'")
            # input()
            ret = len(read_chars)

            data_stack.memory[addr:addr+len(read_chars)] = read_chars
            break

    stack.push(0, ret)

    if ret == -1:
        print('Invalid Handle')
        input()


def qcode_iowrite(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x0E - push% IOWRITE pop%,pop%,pop%)")

    write_len = stack.pop()
    addr = stack.pop()
    handle = stack.pop()

    print(f" - IOWRITE h%={handle}, addr%={addr}, len%={write_len}")

    ret = -1  # Error occured, invalid handle
    for io_obj in procedure.executable.io_handles:
        if handle == io_obj['io_handle']:
            bytes_to_write = data_stack.memory[addr:addr+write_len]

            io_obj['handle'].write(bytes_to_write)

            print(f" - IOWRITE {write_len} characters written")
            print(bytes_to_write.decode())
            ret = 0
            break

    stack.push(0, ret)


def qcode_ioclose(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x10 - push% IOCLOSE pop%")

    handle = stack.pop()

    print(f" - IOCLOSE h%={handle}")

    ret = -1  # Error occured, invalid handle
    for i in range(len(procedure.executable.io_handles)):
        if handle == procedure.executable.io_handles[i]['io_handle']:

            procedure.executable.io_handles[i]['handle'].close()

            # Free up the entry
            del procedure.executable.io_handles[i]

            ret = 0  # Successfully closed
            break

    stack.push(0, ret)


def qcode_ioseek(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x21 - push% IOSEEK pop%")

    offset_addr = stack.pop()
    mode = stack.pop()
    handle = stack.pop()

    # ret%=IOSEEK(handle%,mode%,var offset&)

    # Find the requested offset from the offset var
    offset = data_stack.read(1, offset_addr)

    print(f" - IOSEEK h%={handle} mode={mode} offset={offset}")

    ret = -1  # Error occured, invalid handle
    for i in range(len(procedure.executable.io_handles)):
        if handle == procedure.executable.io_handles[i]['io_handle']:

            # Convert Psion ioseek mode to Python FP seek mode
            if mode == 1:
                # Absolute position
                from_what = 0
            elif mode == 2:
                # Relative to EOF
                from_what = 2
            elif mode == 3:
                # Relative to current position
                from_what = 1
            elif mode == 6:
                # Rewind to first record
                from_what = 0
                offset = 0

            procedure.executable.io_handles[i]['handle'].seek(
                offset, from_what)

            new_position = procedure.executable.io_handles[i]['handle'].tell()

            data_stack.write(0, new_position, offset_addr)

            ret = 0  # Successfully closed
            break

    if ret != 0:
        print('IOSEEK error')
        input()

    stack.push(0, ret)
