import struct
import math
import logging

import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

# Types
T_INT_16  = 0
T_INT_32  = 1
T_FLOAT   = 2
T_STRING  = 3
T_ADDR    = 4

def qcode_cmp_minus(procedure, data_stack, stack):
    # print(f"{hex(op_code)} - push+ pop+2 - pop+1")

    stack_type = procedure.get_executed_opcode() - 0x4C

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack.push(stack_type, pop_2 - pop_1)
    
    
def qcode_less_percent(procedure, data_stack, stack):
    #_logger.debug("0x6C - push* pop*2 < pop*1 %")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack.push(2, pop_2 / (100.0 + pop_1) * pop_1)


def qcode_greater_percent(procedure, data_stack, stack):
    #_logger.debug("0x6D - push* pop*2 > pop*1 %")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack.push(2, pop_2 / (100.0 + pop_1) * 100.0)
    
    
def qcode_plus_percent(procedure, data_stack, stack):
    #_logger.debug("0x6E - push* pop*2 + pop*1 %")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack.push(2, pop_2 / 100.0 * (100.0 + pop_1))
    
    
def qcode_minus_percent(procedure, data_stack, stack):
    #_logger.debug("0x6F - push* pop*2 - pop*1 %")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack.push(2, pop_2 / 100.0 * (100.0 - pop_1))
    
    
def qcode_mult_percent(procedure, data_stack, stack):
    #_logger.debug("0x70 - push* pop*2 * pop*1 %")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack.push(2, pop_2 / 100.0 * pop_1)
    
    
def qcode_div_percent(procedure, data_stack, stack):
    #_logger.debug("0x71 - push* pop*2 / pop*1 %")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack.push(2, pop_2 / pop_1* 100.0)


def qcode_negate(procedure, data_stack, stack):
    # print(f"{hex(op_code)} - push+ - pop+1")

    stack_type = procedure.get_executed_opcode() - 0x68

    stack.push(stack_type, -stack.pop())


def qcode_cmp_mult(procedure, data_stack, stack):
    # print(f"{hex(op_code)} - push+ pop+2 * pop+1")

    stack_type = procedure.get_executed_opcode() - 0x50

    stack.push(stack_type, stack.pop() * stack.pop())


def qcode_cmp_div(procedure, data_stack, stack):
    # print(f"{hex(op_code)} - push+ pop+2 / pop+1")

    stack_type = procedure.get_executed_opcode() - 0x54

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    res = pop_2 / pop_1

    if stack_type == T_INT_16 or stack_type == T_INT_32:
        # Int
        res = int(res)

    # print(f" - {pop_2} / {pop_1} = {res}")

    stack.push(stack_type, res)


def qcode_cmp_plus(procedure, data_stack, stack):
    # print(f"{hex(op_code)} - push+ pop+2 + pop+1")

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    stack_type = procedure.get_executed_opcode() - 0x48
    stack.push(stack_type, pop_2 + pop_1)


def qcode_pi(procedure, data_stack, stack):
    #_logger.debug("0x57 0xBC - push* PI")
    stack.push(T_FLOAT, 3.141592653)


def qcode_int(procedure, data_stack, stack):
    #_logger.debug("0x57 0x42 - push&1 INT pop*1")
    stack.push(T_INT_32, int(stack.pop()))


def qcode_abs(procedure, data_stack, stack):
    #_logger.debug("0x57 0x80 - push ABS pop1")
    stack.push(T_FLOAT, float(abs(stack.pop())))


def qcode_intf(procedure, data_stack, stack):
    #_logger.debug("0x57 0x88 - push INTF pop1")
    stack.push(T_FLOAT, float(int(stack.pop())))


def qcode_ln(procedure, data_stack, stack):
    #_logger.debug("0x57 0x89 - push LN pop1")
    stack.push(T_FLOAT, math.log(stack.pop()))


def qcode_log10(procedure, data_stack, stack):
    #_logger.debug("0x57 0x8A - push LOG pop1")
    stack.push(T_FLOAT, math.log10(stack.pop()))


def qcode_pow(procedure, data_stack, stack):
    # print(f"{hex(op_code)} - push+ pop+2 ** pop+1")

    stack_type = procedure.get_executed_opcode() - 0x58

    pop_1 = stack.pop()
    pop_2 = stack.pop()

    res = math.pow(pop_2, pop_1)

    # print(f" - {pop_2} ^ {pop_1} = {res}")

    stack.push(stack_type, res)


def qcode_sin(procedure, data_stack, stack):
    #_logger.debug("0x57 0x8F - push SIN pop1")
    stack.push(T_FLOAT, math.sin(stack.pop()))


def qcode_cos(procedure, data_stack, stack):
    #_logger.debug("0x57 0x84 - push COS pop1")
    stack.push(T_FLOAT, math.cos(stack.pop()))


def qcode_tan(procedure, data_stack, stack):
    #_logger.debug("0x57 0x91 - push TAN pop1")
    stack.push(T_FLOAT, math.tan(stack.pop()))


def qcode_acos(procedure, data_stack, stack):
    #_logger.debug("0x57 0x81 - push ACOS pop1")
    stack.push(T_FLOAT, math.acos(stack.pop()))


def qcode_asin(procedure, data_stack, stack):
    #_logger.debug("0x57 0x82 - push ASIN pop1")
    stack.push(T_FLOAT, math.asin(stack.pop()))


def qcode_atan(procedure, data_stack, stack):
    #_logger.debug("0x57 0x83 - push ATAN pop1")
    stack.push(T_FLOAT, math.atan(stack.pop()))


def qcode_deg(procedure, data_stack, stack):
    #_logger.debug("0x57 0x85 - push DEG pop1")
    stack.push(T_FLOAT, math.degrees(stack.pop()))


def qcode_exp(procedure, data_stack, stack):
    #_logger.debug("0x57 0x86 - push EXP pop1")
    stack.push(T_FLOAT, math.exp(stack.pop()))


def qcode_sqr(procedure, data_stack, stack):
    #_logger.debug("0x57 0x90 - push SQR pop1")
    stack.push(T_FLOAT, math.sqrt(stack.pop()))


def qcode_rad(procedure, data_stack, stack):
    #_logger.debug("0x57 0x8D - push RAD pop1")
    res = (math.pi * stack.pop())/180.0
    stack.push(T_FLOAT, res)


def qcode_flt(procedure, data_stack, stack):
    #_logger.debug("0x57 0x87 - push flt pop&1")
    stack.push(T_FLOAT, float(stack.pop()))
