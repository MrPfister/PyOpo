import struct
import time

from opl_exceptions import *

import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

def qcode_val(procedure, data_stack, stack):
    #_logger.debug("0x57 0x92 - VAL(pop$)")
    stack.push(2, float(stack.pop()))


def qcode_chr(procedure, data_stack, stack):
    #_logger.debug("0x57 0xC0 - CHR$(pop+%1)")
    stack.push(3, chr(int(stack.pop())))


def qcode_asc(procedure, data_stack, stack):
    #_logger.debug("0x57 0x01 - ASC(pop$1)")

    pop_1 = stack.pop()

    res = 0
    if len(pop_1) > 0:
        res = ord(pop_1[0])

    if res > 255:
        # Outside ASCII range
        #_logger.warning('Warning: ASC outside ASCII range - defaulting to 0')
        res = 0

    stack.push(0, res)


def qcode_len(procedure, data_stack, stack):
    #_logger.debug("0x57 0x14 - LEN(pop$1)")
    stack.push(0, len(stack.pop()))


def qcode_loc(procedure, data_stack, stack):
    #_logger.debug("0x57 0x15 - push% LOC(pop$2, pop$1)")

    # Search is case invariant
    pop_1 = stack.pop().upper()
    pop_2 = stack.pop().upper()

    # Find returns -1 if not found, or 0 based otherwise. 
    # The OPL command is 0 if not found and 1 based
    res = pop_2.find(pop_1) + 1

    #print(f" - LOC({pop_2}, {pop_1}) = {res}")

    stack.push(0, res)
    

def qcode_left(procedure, data_stack, stack):
    #_logger.debug("0x57 0xCA - push$ LEFT$(pop$2, pop%1)")

    """
    Emulator Testing Notes:

    Where l = len(x)
    a < 0 : Error - Invalid Args
    a = 0 : Empty string
    a <= l : Expected response
    a > l : l
    """

    x = stack.pop()
    a = stack.pop()

    if x < 0:
        raise(KErrInvalidArgs)
    elif x <= len(a):
        left = a[0: x]
    else:
        left = a

    stack.push(3, left)


def qcode_rept(procedure, data_stack, stack):
    #_logger.debug("0x57 0xD0 - push$ REPT$(pop$2, pop%1)")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    rept = pop_2 * pop_1

    #print(f" - REPT$({pop_2}, {pop_1}) = {rept}")

    stack.push(3, rept)


def qcode_gen(procedure, data_stack, stack):
    #_logger.debug("0x57 0xC6 - push$ GEN$(pop*2, pop%1)")

    y = stack.pop()
    x = stack.pop()
    if int(x) == x:
        x = int(x)

    #print(f" - GEN$({x}, {y})")

    int_len = len(str(int(x)))
    res = str(x)
    if len(res) != int_len:
        min_len = int_len + 2 # Needs space for decimal
    else:
        # Just requires space for int
        min_len = int_len

    if y < 0:
        # Right justify results
        y = abs(y) - len(res)
        y = max(y, 0)
        res = " " * y + res
    elif min_len > y:
        # Requested length is shorter than the minimum required length
        res = "*" * y
    else:
        # Clip the length
        res = res[:y]

    #print(f" - = '{res}'")
    
    stack.push(3, res)


def qcode_num(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xCE - push$ NUM$(pop*2, pop%1)")

    y = stack.pop()
    x = stack.pop()

    if abs(x) == x:
        #_logger.debug(f"{x} is abs(x), ignoring decimal")
        x = abs(x)

    res = str(int(x))
    if y < 0:
        # Right justify results
        y = abs(y) - len(res)
        y = max(y, 0)
        res = " " * y + res
    elif len(res) > y:
        res = "*" * y
    
    # print(f" - NUM$({x}, {y}) = {res}")

    stack.push(3, res)


def qcode_fix(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xC5 - push$ FIX$(pop*3, pop%2, pop%1)")

    z = stack.pop()
    y = stack.pop()
    x = stack.pop()

    res = str(round(x, y))
    if z < 0:
        # Right justify results
        z = abs(z)

        if len(res) >= z:
            res = res[0:z]
        else:
            res = ' ' * (z - len(res)) + res
    elif z>len(res):
        res = res
    else:
        res = res[0:z]
    
    # print(f" - FIX$({x}, {y}, {z}) = {res}")

    stack.push(3, res)

    
def qcode_mid(procedure, data_stack, stack):
    #_logger.debug("0x57 0xCC - push$ MID$ pop$3 pop%2 pop%1)")

    y = stack.pop()
    x = stack.pop()
    a = stack.pop()

    if x-1 < 0:
        raise(KErrOutOfRange)

    res = a[x-1:x-1+y] # Psion strings are +1 offset

    stack.push(3, res)


def qcode_right(procedure, data_stack, stack):
    #_logger.debug("0x57 0xD1 - push$ RIGHT$(pop*2, pop%1)")
    
    """
    Emulator Testing Notes:

    Where l = len(x)
    a < 0 : Error - Invalid Args
    a = 0 : Empty string
    a <= l : Expected response
    a > l : l
    """

    x = stack.pop()
    a = stack.pop()

    if x < 0:
        raise(KErrInvalidArgs)
    elif x <= len(a):
        right = a[-x:]
    else:
        right = a

    stack.push(3, right)


def qcode_upper(procedure, data_stack, stack):
    #_logger.debug("0x57 0xD3 - push$ UPPER$ pop$")
    stack.push(3, str(stack.pop()).upper())


def qcode_lower(procedure, data_stack, stack):
    #_logger.debug("0x57 0xCB - push$ LOWER$ pop$")
    stack.push(3, str(stack.pop()).lower())


def qcode_hex(procedure, data_stack, stack):
    #_logger.debug("0x57 0xC8 - push$ HEX$ pop&")
    stack.push(3, hex(stack.pop()))


def qcode_sci(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xD2 - push$ LOWER$ pop$")

    z = stack.pop()
    y = stack.pop()
    x = stack.pop()

    exp = y - 6
    format_str = "{:." + str(exp) + "E}"

    res = format_str.format(x)

    if z < 0:
        z = abs(z)
        diff = z - len(res)

        res = ' ' * diff + res
    elif len(res) > z:
        res = '*' * z

    # print(f" - SCI$({x}, {y}, {z}) = {res}")

    stack.push(3, res)