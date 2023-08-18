from pyopo.opcode_handlers import (
    qcode_var,
    qcode_cmp,
    qcode_maths,
    qcode_screen,
    qcode_memory,
    qcode_graphics,
    qcode_gen,
    qcode_menu,
    qcode_filesystem,
    qcode_dbf,
    qcode_modules,
    qcode_str,
    qcode_datetime,
    qcode_kernel,
    qcode_dialog
)

from .opl_exceptions import *

from pyopo.heap import data_stack
from pyopo.var_stack import stack

import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG) 


def qcode_invalid_opcode(procedure, data_stack: data_stack, stack: stack):
    opcode = procedure.get_executed_opcode()

    _logger.Error(f"Invalid Opcode - {hex(opcode)}")
    _logger.Warning("Opcode is not present in OPL runtime. Revtran bypass or fault detected. Stopping execution")

    # Stop Execution of the program
    procedure.flag_stop = True


opcode_handler = {
    0x00: qcode_var.qcode_push_var,
    0x01: qcode_var.qcode_push_var,
    0x02: qcode_var.qcode_push_var,
    0x03: qcode_var.qcode_push_var,
    0x04: qcode_var.qcode_push_addr,
    0x05: qcode_var.qcode_push_addr,
    0x06: qcode_var.qcode_push_addr,
    0x07: qcode_var.qcode_push_addr,
    0x08: qcode_var.qcode_push_ee_value,
    0x09: qcode_var.qcode_push_ee_value,
    0x0A: qcode_var.qcode_push_ee_value,
    0x0B: qcode_var.qcode_push_ee_value,
    0x0C: qcode_var.qcode_push_ee_addr,
    0x0D: qcode_var.qcode_push_ee_addr,
    0x0E: qcode_var.qcode_push_ee_addr,
    0x0F: qcode_var.qcode_push_ee_addr,
    0x10: qcode_var.qcode_push_var_array,
    0x11: qcode_var.qcode_push_var_array,
    0x12: qcode_var.qcode_push_var_array,
    0x13: qcode_var.qcode_push_var_array,
    0x14: qcode_var.qcode_push_addr_array,
    0x15: qcode_var.qcode_push_addr_array,
    0x16: qcode_var.qcode_push_addr_array,
    0x17: qcode_var.qcode_push_addr_array,
    0x18: qcode_var.qcode_push_ee_array_val,
    0x19: qcode_var.qcode_push_ee_array_val,
    0x1A: qcode_var.qcode_push_ee_array_val,
    0x1B: qcode_var.qcode_push_ee_array_val,
    0x1C: qcode_var.qcode_push_ee_array_addr,
    0x1D: qcode_var.qcode_push_ee_array_addr,
    0x1E: qcode_var.qcode_push_ee_array_addr,
    0x1F: qcode_var.qcode_push_ee_array_addr,
    0x20: qcode_var.qcode_push_value_field,
    0x21: qcode_var.qcode_push_value_field,
    0x22: qcode_var.qcode_push_value_field,
    0x23: qcode_var.qcode_push_value_field,
    0x24: qcode_var.qcode_push_addr_field,
    0x25: qcode_var.qcode_push_addr_field,
    0x26: qcode_var.qcode_push_addr_field,
    0x27: qcode_var.qcode_push_addr_field,
    0x28: qcode_var.qcode_push_vv_plus,
    0x29: qcode_var.qcode_push_vv_plus,
    0x2A: qcode_var.qcode_push_vv_plus,
    0x2B: qcode_var.qcode_push_vv_plus,
    0x2C: qcode_invalid_opcode,
    0x2D: qcode_invalid_opcode,
    0x2E: qcode_invalid_opcode,
    0x2F: qcode_invalid_opcode,
    0x30: qcode_cmp.qcode_cmp_less_than,
    0x31: qcode_cmp.qcode_cmp_less_than,
    0x32: qcode_cmp.qcode_cmp_less_than,
    0x33: qcode_cmp.qcode_cmp_less_than,
    0x34: qcode_cmp.qcode_cmp_less_than_equal,
    0x35: qcode_cmp.qcode_cmp_less_than_equal,
    0x36: qcode_cmp.qcode_cmp_less_than_equal,
    0x37: qcode_cmp.qcode_cmp_less_than_equal,
    0x38: qcode_cmp.qcode_cmp_greater,
    0x39: qcode_cmp.qcode_cmp_greater,
    0x3A: qcode_cmp.qcode_cmp_greater,
    0x3B: qcode_cmp.qcode_cmp_greater,
    0x3C: qcode_cmp.qcode_cmp_greater_equal,
    0x3D: qcode_cmp.qcode_cmp_greater_equal,
    0x3E: qcode_cmp.qcode_cmp_greater_equal,
    0x3F: qcode_cmp.qcode_cmp_greater_equal,
    0x40: qcode_cmp.qcode_cmp_equals,
    0x41: qcode_cmp.qcode_cmp_equals,
    0x42: qcode_cmp.qcode_cmp_equals,
    0x43: qcode_cmp.qcode_cmp_equals,
    0x44: qcode_cmp.qcode_cmp_not_equals,
    0x45: qcode_cmp.qcode_cmp_not_equals,
    0x46: qcode_cmp.qcode_cmp_not_equals,
    0x47: qcode_cmp.qcode_cmp_not_equals,
    0x48: qcode_maths.qcode_cmp_plus,
    0x49: qcode_maths.qcode_cmp_plus,
    0x4A: qcode_maths.qcode_cmp_plus,
    0x4B: qcode_maths.qcode_cmp_plus,
    0x4C: qcode_maths.qcode_cmp_minus,
    0x4D: qcode_maths.qcode_cmp_minus,
    0x4E: qcode_maths.qcode_cmp_minus,
    0x4F: qcode_var.qcode_push_vv_word,
    0x50: qcode_maths.qcode_cmp_mult,
    0x51: qcode_maths.qcode_cmp_mult,
    0x52: qcode_maths.qcode_cmp_mult,
    # 0x53: call procedure EE:
    0x54: qcode_maths.qcode_cmp_div,
    0x55: qcode_maths.qcode_cmp_div,
    0x56: qcode_maths.qcode_cmp_div,
    # 0x57 [[Additional sub calls]]
    0x58: qcode_maths.qcode_pow,
    0x59: qcode_maths.qcode_pow,
    0x5A: qcode_maths.qcode_pow,
    0x5B: qcode_cmp.qcode_cmp_if,
    0x5C: qcode_cmp.qcode_cmp_and,
    0x5D: qcode_cmp.qcode_cmp_and,
    0x5E: qcode_cmp.qcode_cmp_and,
    0x5F: qcode_var.qcode_push_vv_long,
    0x60: qcode_cmp.qcode_cmp_or,
    0x61: qcode_cmp.qcode_cmp_or,
    0x62: qcode_cmp.qcode_cmp_or,
    0x63: qcode_var.qcode_push_vv_word_to_long,
    0x64: qcode_cmp.qcode_cmp_not,
    0x65: qcode_cmp.qcode_cmp_not,
    0x66: qcode_cmp.qcode_cmp_not,
    0x67: qcode_invalid_opcode,
    0x68: qcode_maths.qcode_negate,                 # COMPLETE
    0x69: qcode_maths.qcode_negate,                 # COMPLETE
    0x6A: qcode_maths.qcode_negate,                 # COMPLETE
    # 0x6B [[ @ Operator ]]
    0x6C: qcode_maths.qcode_less_percent,
    0x6D: qcode_maths.qcode_greater_percent,
    0x6E: qcode_maths.qcode_plus_percent,
    0x6F: qcode_maths.qcode_minus_percent,
    0x70: qcode_maths.qcode_mult_percent,
    0x71: qcode_maths.qcode_div_percent,
    0x72: qcode_invalid_opcode,
    0x73: qcode_invalid_opcode,
    # 0x74 - 0x77 [[ RETURN no value ]]
    0x78: qcode_var.qcode_push_word_pop,            # COMPLETE
    0x79: qcode_var.qcode_push_word_pop,            # COMPLETE
    0x7A: qcode_var.qcode_push_long_pop,            # COMPLETE
    0x7B: qcode_var.qcode_push_long_pop,            # COMPLETE
    0x7C: qcode_var.qcode_push_real_pop,            # COMPLETE
    0x7D: qcode_var.qcode_push_real_pop,            # COMPLETE
    0x7E: qcode_invalid_opcode,
    0x7F: qcode_invalid_opcode,
    0x80: qcode_var.qcode_pop_discard,              # COMPLETE
    0x81: qcode_var.qcode_pop_discard,              # COMPLETE
    0x82: qcode_var.qcode_pop_discard,              # COMPLETE
    0x83: qcode_var.qcode_pop_discard,              # COMPLETE
    0x84: qcode_var.qcode_store_pop1_in_pop2,
    0x85: qcode_var.qcode_store_pop1_in_pop2,
    0x86: qcode_var.qcode_store_pop1_in_pop2,
    0x87: qcode_var.qcode_store_pop1_in_pop2,
    0x88: qcode_screen.qcode_print_semi,
    0x89: qcode_screen.qcode_print_semi,
    0x8A: qcode_screen.qcode_print_semi,
    0x8B: qcode_screen.qcode_print_semi,

    0x92: qcode_screen.qcode_print,

    0x98: qcode_memory.qcode_poke,
    0x99: qcode_memory.qcode_poke,
    0x9A: qcode_memory.qcode_poke,
    0x9B: qcode_memory.qcode_poke,
    0x9C: qcode_memory.qcode_pokeb,
    0x9D: qcode_dbf.qcode_append,
    0x9E: qcode_screen.qcode_at,

    0xA0: qcode_gen.qcode_beep,                     # NOT IMPLEMENTED
    0xA1: qcode_dbf.qcode_close, # STUB
    0xA2: qcode_screen.qcode_cls, # STUB

    0xA5: qcode_dbf.qcode_create, # STUB
    0xA6: qcode_screen.qcode_cursor, # STUB
    0xA7: qcode_filesystem.qcode_delete_file,

    0xA9: qcode_gen.qcode_escape,

    0xAB: qcode_gen.qcode_vector,

    0xAE: qcode_modules.qcode_loadm,

    0xB1: qcode_gen.qcode_onerr,

    0xB4: qcode_dbf.qcode_open,
    0xB5: qcode_gen.qcode_pause,

    0xB7: qcode_filesystem.qcode_iosignal, # STUB

    0xB9: qcode_gen.qcode_randomize,                    # COMPLETE

    0xBB: qcode_gen.qcode_stop,
    0xBC: qcode_gen.qcode_trap,                         # COMPLETE
    0xBD: qcode_dbf.qcode_update, # STUB
    0xBE: qcode_dbf.qcode_use,
    0xBF: qcode_gen.qcode_goto,
    # C0 RETURN pop+ (type popped depends on procedure type)

    0xC5: qcode_graphics.qcode_gsavebit, # PARTIAL
    0xC6: qcode_graphics.qcode_gclose,
    0xC7: qcode_graphics.qcode_guse,
    0xC8: qcode_graphics.qcode_gsetwin,
    0xC9: qcode_graphics.qcode_gvisible,                # COMPLETE
    0xCA: qcode_graphics.qcode_gfont,

    0xCC: qcode_graphics.qcode_ggmode,
    0xCD: qcode_graphics.qcode_gtmode,  # STUB
    0xCE: qcode_graphics.qcode_gstyle,
    0xCF: qcode_graphics.qcode_gorder,
    0xD0: qcode_graphics.qcode_ginfo,   # PARTIAL
    0xD1: qcode_graphics.qcode_gcls,
    0xD2: qcode_graphics.qcode_gat,
    0xD3: qcode_graphics.qcode_gmove,
    0xD4: qcode_graphics.qcode_gprint,
    0xD5: qcode_graphics.qcode_gprint,
    0xD6: qcode_graphics.qcode_gprint,
    0xD7: qcode_graphics.qcode_gprint,
    0xD8: qcode_graphics.qcode_gprint_comma,
    0xD9: qcode_graphics.qcode_gprintb,
    0xDA: qcode_graphics.qcode_glineby,
    0xDB: qcode_graphics.qcode_gbox,

    0xDE: qcode_graphics.qcode_gpoly,
    0xDF: qcode_graphics.qcode_gfill,
    0xE0: qcode_graphics.qcode_gpatt,   # PARTIAL
    0xE1: qcode_graphics.qcode_gcopy,
    0xE2: qcode_graphics.qcode_gscroll,
    0xE3: qcode_graphics.qcode_gupdate,
    0xE4: qcode_gen.qcode_getevent,
    0xE5: qcode_graphics.qcode_glineto,
    0xE6: qcode_graphics.qcode_gpeekline,
    0xE7: qcode_screen.qcode_screen_4,      # STUB
    0xE8: qcode_filesystem.qcode_iowaitstat,

    0xEA: qcode_menu.qcode_minit,
    0xEB: qcode_menu.qcode_mcard,
    0xEC: qcode_dialog.qcode_dinit,
    # ED [[Additional sub calls]]
    0xEE: qcode_graphics.qcode_setname,
    0xEF: qcode_gen.qcode_statuswin,
    0xF0: qcode_gen.qcode_busy,                 # STUB
    0xF1: qcode_gen.qcode_lock,                 # NOT IMPLEMENTED
    0xF2: qcode_graphics.qcode_ginvert,
    0xF3: qcode_graphics.qcode_gxprint,         # STUB to gPRINT
    0xF4: qcode_graphics.qcode_gborder,
    0xF5: qcode_graphics.qcode_gclock,

    0xF8: qcode_filesystem.qcode_mkdir,

    0xFA: qcode_filesystem.qcode_setpath,
    0xFB: qcode_datetime.qcode_secstodate,

    0xFC: qcode_gen.qcode_giprint
}

opcode_0x57_handler = {
    0x00: qcode_var.qcode_addr,
    0x01: qcode_str.qcode_asc,
    0x02: qcode_kernel.qcode_call,      # PARTIAL

    0x04: qcode_datetime.qcode_day,

    0x07: qcode_gen.qcode_err_virt,
    0x08: qcode_filesystem.qcode_exist,

    0x0A: qcode_gen.qcode_get,
    0x0B: qcode_filesystem.qcode_ioa,

    0x0D: qcode_filesystem.qcode_ioopen,
    0x0E: qcode_filesystem.qcode_iowrite,
    0x0F: qcode_filesystem.qcode_ioread,
    0x10: qcode_filesystem.qcode_ioclose,
    0x11: qcode_filesystem.qcode_iowait,            # STUB
    0x12: qcode_datetime.qcode_hour,
    0x13: qcode_gen.qcode_key,
    0x14: qcode_str.qcode_len,                      # COMPLETE
    0x15: qcode_str.qcode_loc,
    0x16: qcode_datetime.qcode_minute,
    0x17: qcode_datetime.qcode_month,
    0x18: qcode_memory.qcode_peekb,
    0x19: qcode_memory.qcode_peekw,    

    0x1C: qcode_datetime.qcode_second,
    0x1D: qcode_gen.qcode_usr,                      # Can not implement!!
    0x1E: qcode_datetime.qcode_year,
    0x1F: qcode_var.qcode_addr_str,

    0x21: qcode_filesystem.qcode_ioseek,
    0x22: qcode_gen.qcode_kmod, # STUB

    0x26: qcode_graphics.qcode_gcreate_5,
    0x27: qcode_graphics.qcode_gcreatebit,
    0x28: qcode_graphics.qcode_gloadbit,

    0x2B: qcode_graphics.qcode_gidentity,
    0x2C: qcode_graphics.qcode_gx,
    0x2D: qcode_graphics.qcode_gy,
    0x2E: qcode_graphics.qcode_gwidth,
    0x2F: qcode_graphics.qcode_gheight,
    0x30: qcode_graphics.qcode_goriginx,
    0x31: qcode_graphics.qcode_goriginy,
    0x32: qcode_graphics.qcode_gtwidth,             # COMPLETE

    0x34: qcode_gen.qcode_testevent,                # STUB
    0x35: qcode_kernel.qcode_OS,                    # PARTIAL
    0x36: qcode_menu.qcode_menu,
    0x37: qcode_dialog.qcode_dialog,
    0x38: qcode_dialog.qcode_alert,                 # PARTIAL
    0x39: qcode_graphics.qcode_gcreate_6,
    0x3A: qcode_menu.qcode_menu_var,
    0x3B: qcode_graphics.qcode_createsprite,

    0x40: qcode_datetime.qcode_days,

    0x42: qcode_maths.qcode_int,                    # COMPLETE

    0x45: qcode_datetime.qcode_datetosecs,

    0x4B: qcode_memory.qcode_alloc,                 # COMPLETE

    0x50: qcode_var.qcode_uadd,                     # COMPLETE
    0x51: qcode_var.qcode_usub,                     # COMPLETE

    0x53: qcode_gen.qcode_statuswininfo,            # STUB
    
    0x59: qcode_invalid_opcode,

    0x7F: qcode_invalid_opcode,
    0x80: qcode_maths.qcode_abs,                    # COMPLETE
    0x81: qcode_maths.qcode_acos,                   # COMPLETE
    0x82: qcode_maths.qcode_asin,                   # COMPLETE
    0x83: qcode_maths.qcode_atan,                   # COMPLETE
    0x84: qcode_maths.qcode_cos,                    # COMPLETE
    0x85: qcode_maths.qcode_deg,                    # COMPLETE
    0x86: qcode_maths.qcode_exp,                    # COMPLETE
    0x87: qcode_maths.qcode_flt,                    # COMPLETE
    0x88: qcode_maths.qcode_intf,                   # COMPLETE
    0x89: qcode_maths.qcode_ln,                     # COMPLETE
    0x8A: qcode_maths.qcode_log10,                  # COMPLETE
    0x8B: qcode_memory.qcode_peekf,                 # COMPLETE
    0x8C: qcode_maths.qcode_pi,                     # COMPLETE
    0x8D: qcode_maths.qcode_rad,                    # COMPLETE
    0x8E: qcode_gen.qcode_rnd,                      # COMPLETE
    0x8F: qcode_maths.qcode_sin,                    # COMPLETE
    0x90: qcode_maths.qcode_sqr,                    # COMPLETE
    0x91: qcode_maths.qcode_tan,                    # COMPLETE
    0x92: qcode_str.qcode_val,                      # COMPLETE
    0x93: qcode_cmp.qcode_max,                      # COMPLETE
    0x94: qcode_cmp.qcode_mean,                     # COMPLETE
    0x95: qcode_cmp.qcode_min,                      # COMPLETE
    0x96: qcode_cmp.qcode_std,                      # COMPLETE
    0x97: qcode_cmp.qcode_sum,                      # COMPLETE
    0x98: qcode_cmp.qcode_var,                      # COMPLETE
    0x99: qcode_gen.qcode_eval,
    0x9A: qcode_invalid_opcode,
    0x9B: qcode_invalid_opcode,
    0x9C: qcode_invalid_opcode,
    0x9D: qcode_invalid_opcode,
    0x9E: qcode_invalid_opcode,
    0x9F: qcode_invalid_opcode,
    0xA0: qcode_invalid_opcode,
    0xA1: qcode_invalid_opcode,
    0xA2: qcode_invalid_opcode,
    0xA3: qcode_invalid_opcode,
    0xA4: qcode_invalid_opcode,
    0xA5: qcode_invalid_opcode,
    0xA6: qcode_invalid_opcode,
    0xA7: qcode_invalid_opcode,
    0xA8: qcode_invalid_opcode,
    0xA9: qcode_invalid_opcode,
    0xAA: qcode_invalid_opcode,
    0xAB: qcode_invalid_opcode,
    0xAC: qcode_invalid_opcode,
    0xAD: qcode_invalid_opcode,
    0xAE: qcode_invalid_opcode,
    0xAF: qcode_invalid_opcode,
    0xB0: qcode_invalid_opcode,
    0xB1: qcode_invalid_opcode,
    0xB2: qcode_invalid_opcode,
    0xB3: qcode_invalid_opcode,
    0xB4: qcode_invalid_opcode,
    0xB5: qcode_invalid_opcode,
    0xB6: qcode_invalid_opcode,
    0xB7: qcode_invalid_opcode,
    0xB8: qcode_invalid_opcode,
    0xB9: qcode_invalid_opcode,
    0xBA: qcode_invalid_opcode,
    0xBB: qcode_invalid_opcode,
    0xBC: qcode_invalid_opcode,
    0xBD: qcode_invalid_opcode,
    0xBE: qcode_invalid_opcode,
    0xBF: qcode_invalid_opcode,
    0xC0: qcode_str.qcode_chr,                      # COMPLETE
    0xC1: qcode_datetime.qcode_datim,               # COMPLETE
    0xC2: qcode_datetime.qcode_dayname,
    0xC3: qcode_filesystem.qcode_dir,
    0xC4: qcode_gen.qcode_err_str,                  # STUB
    0xC5: qcode_str.qcode_fix,
    0xC6: qcode_str.qcode_gen,
    0xC7: qcode_gen.qcode_get_str,
    0xC8: qcode_str.qcode_hex,                      # COMPLETE

    0xCA: qcode_str.qcode_left,
    0xCB: qcode_str.qcode_lower,                    # COMPLETE
    0xCC: qcode_str.qcode_mid,                      # COMPLETE
    0xCD: qcode_datetime.qcode_month_str,
    0xCE: qcode_str.qcode_num,
    0xCF: qcode_memory.qcode_peek_str,
    0xD0: qcode_str.qcode_rept,
    0xD1: qcode_str.qcode_right,                    # COMPLETE
    0xD2: qcode_str.qcode_sci,
    0xD3: qcode_str.qcode_upper,                    # COMPLETE
    0xD4: qcode_gen.qcode_usr,                      # Can not implement!
    
    0xD6: qcode_gen.qcode_cmd,
    0xD7: qcode_gen.qcode_parse
}

opcode_0xED_handler = {
    0x00: qcode_dialog.qcode_dtext,
    0x01: qcode_dialog.qcode_dchoice,
    0x02: qcode_dialog.qcode_dlong,
    0x03: qcode_dialog.qcode_dfloat,

    0x06: qcode_dialog.qcode_dedit_2,
    0x07: qcode_dialog.qcode_dedit_3,

    0x09: qcode_dialog.qcode_dfile,
    0x0A: qcode_dialog.qcode_dbuttons,
    0x0B: qcode_dialog.qcode_dposition
}

opcode_0xFF_handler = {
    0x00: qcode_graphics.qcode_ggrey,
    0x01: qcode_graphics.qcode_defaultwin,
    0x02: qcode_gen.qcode_diaminit,             # NOT IMPLEMENTED
    0x03: qcode_gen.qcode_diampos,              # NOT IMPLEMENTED
    0x04: qcode_screen.qcode_font, # STUB
    0x05: qcode_screen.qcode_style, # STUB

    0x07: qcode_graphics.qcode_appendsprite,
    0x08: qcode_graphics.qcode_drawsprite,
    
    0x0A: qcode_graphics.qcode_posssprite,

    0x0E: qcode_gen.qcode_cache,                # NOT IMPLEMENTED
    0x0F: qcode_graphics.qcode_gbutton,

    0x10: qcode_graphics.qcode_gxborder, # STUB - uses gBORDER
    0x14: qcode_screen.qcode_screeninfo
}