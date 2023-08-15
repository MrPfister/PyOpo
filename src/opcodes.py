import opcode_handlers.qcode_var
import opcode_handlers.qcode_cmp
import opcode_handlers.qcode_graphics
import opcode_handlers.qcode_screen
import opcode_handlers.qcode_gen
import opcode_handlers.qcode_str
import opcode_handlers.qcode_maths
import opcode_handlers.qcode_dbf
import opcode_handlers.qcode_datetime
import opcode_handlers.qcode_filesystem
import opcode_handlers.qcode_dialog
import opcode_handlers.qcode_menu
import opcode_handlers.qcode_kernel
import opcode_handlers.qcode_memory
import opcode_handlers.qcode_modules
import opl_exceptions

import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG) 


def qcode_invalid_opcode(procedure, data_stack, stack):
    opcode = procedure.get_executed_opcode()

    _logger.Error(f"Invalid Opcode - {hex(opcode)}")
    _logger.Warning("Opcode is not present in OPL runtime. Revtran bypass or fault detected. Stopping execution")

    # Stop Execution of the program
    procedure.flag_stop = True


opcode_handler = {
    0x00: opcode_handlers.qcode_var.qcode_push_var,
    0x01: opcode_handlers.qcode_var.qcode_push_var,
    0x02: opcode_handlers.qcode_var.qcode_push_var,
    0x03: opcode_handlers.qcode_var.qcode_push_var,
    0x04: opcode_handlers.qcode_var.qcode_push_addr,
    0x05: opcode_handlers.qcode_var.qcode_push_addr,
    0x06: opcode_handlers.qcode_var.qcode_push_addr,
    0x07: opcode_handlers.qcode_var.qcode_push_addr,
    0x08: opcode_handlers.qcode_var.qcode_push_ee_value,
    0x09: opcode_handlers.qcode_var.qcode_push_ee_value,
    0x0A: opcode_handlers.qcode_var.qcode_push_ee_value,
    0x0B: opcode_handlers.qcode_var.qcode_push_ee_value,
    0x0C: opcode_handlers.qcode_var.qcode_push_ee_addr,
    0x0D: opcode_handlers.qcode_var.qcode_push_ee_addr,
    0x0E: opcode_handlers.qcode_var.qcode_push_ee_addr,
    0x0F: opcode_handlers.qcode_var.qcode_push_ee_addr,
    0x10: opcode_handlers.qcode_var.qcode_push_var_array,
    0x11: opcode_handlers.qcode_var.qcode_push_var_array,
    0x12: opcode_handlers.qcode_var.qcode_push_var_array,
    0x13: opcode_handlers.qcode_var.qcode_push_var_array,
    0x14: opcode_handlers.qcode_var.qcode_push_addr_array,
    0x15: opcode_handlers.qcode_var.qcode_push_addr_array,
    0x16: opcode_handlers.qcode_var.qcode_push_addr_array,
    0x17: opcode_handlers.qcode_var.qcode_push_addr_array,
    0x18: opcode_handlers.qcode_var.qcode_push_ee_array_val,
    0x19: opcode_handlers.qcode_var.qcode_push_ee_array_val,
    0x1A: opcode_handlers.qcode_var.qcode_push_ee_array_val,
    0x1B: opcode_handlers.qcode_var.qcode_push_ee_array_val,
    0x1C: opcode_handlers.qcode_var.qcode_push_ee_array_addr,
    0x1D: opcode_handlers.qcode_var.qcode_push_ee_array_addr,
    0x1E: opcode_handlers.qcode_var.qcode_push_ee_array_addr,
    0x1F: opcode_handlers.qcode_var.qcode_push_ee_array_addr,
    0x20: opcode_handlers.qcode_var.qcode_push_value_field,
    0x21: opcode_handlers.qcode_var.qcode_push_value_field,
    0x22: opcode_handlers.qcode_var.qcode_push_value_field,
    0x23: opcode_handlers.qcode_var.qcode_push_value_field,
    0x24: opcode_handlers.qcode_var.qcode_push_addr_field,
    0x25: opcode_handlers.qcode_var.qcode_push_addr_field,
    0x26: opcode_handlers.qcode_var.qcode_push_addr_field,
    0x27: opcode_handlers.qcode_var.qcode_push_addr_field,
    0x28: opcode_handlers.qcode_var.qcode_push_vv_plus,
    0x29: opcode_handlers.qcode_var.qcode_push_vv_plus,
    0x2A: opcode_handlers.qcode_var.qcode_push_vv_plus,
    0x2B: opcode_handlers.qcode_var.qcode_push_vv_plus,
    0x2C: qcode_invalid_opcode,
    0x2D: qcode_invalid_opcode,
    0x2E: qcode_invalid_opcode,
    0x2F: qcode_invalid_opcode,
    0x30: opcode_handlers.qcode_cmp.qcode_cmp_less_than,
    0x31: opcode_handlers.qcode_cmp.qcode_cmp_less_than,
    0x32: opcode_handlers.qcode_cmp.qcode_cmp_less_than,
    0x33: opcode_handlers.qcode_cmp.qcode_cmp_less_than,
    0x34: opcode_handlers.qcode_cmp.qcode_cmp_less_than_equal,
    0x35: opcode_handlers.qcode_cmp.qcode_cmp_less_than_equal,
    0x36: opcode_handlers.qcode_cmp.qcode_cmp_less_than_equal,
    0x37: opcode_handlers.qcode_cmp.qcode_cmp_less_than_equal,
    0x38: opcode_handlers.qcode_cmp.qcode_cmp_greater,
    0x39: opcode_handlers.qcode_cmp.qcode_cmp_greater,
    0x3A: opcode_handlers.qcode_cmp.qcode_cmp_greater,
    0x3B: opcode_handlers.qcode_cmp.qcode_cmp_greater,
    0x3C: opcode_handlers.qcode_cmp.qcode_cmp_greater_equal,
    0x3D: opcode_handlers.qcode_cmp.qcode_cmp_greater_equal,
    0x3E: opcode_handlers.qcode_cmp.qcode_cmp_greater_equal,
    0x3F: opcode_handlers.qcode_cmp.qcode_cmp_greater_equal,
    0x40: opcode_handlers.qcode_cmp.qcode_cmp_equals,
    0x41: opcode_handlers.qcode_cmp.qcode_cmp_equals,
    0x42: opcode_handlers.qcode_cmp.qcode_cmp_equals,
    0x43: opcode_handlers.qcode_cmp.qcode_cmp_equals,
    0x44: opcode_handlers.qcode_cmp.qcode_cmp_not_equals,
    0x45: opcode_handlers.qcode_cmp.qcode_cmp_not_equals,
    0x46: opcode_handlers.qcode_cmp.qcode_cmp_not_equals,
    0x47: opcode_handlers.qcode_cmp.qcode_cmp_not_equals,
    0x48: opcode_handlers.qcode_maths.qcode_cmp_plus,
    0x49: opcode_handlers.qcode_maths.qcode_cmp_plus,
    0x4A: opcode_handlers.qcode_maths.qcode_cmp_plus,
    0x4B: opcode_handlers.qcode_maths.qcode_cmp_plus,
    0x4C: opcode_handlers.qcode_maths.qcode_cmp_minus,
    0x4D: opcode_handlers.qcode_maths.qcode_cmp_minus,
    0x4E: opcode_handlers.qcode_maths.qcode_cmp_minus,
    0x4F: opcode_handlers.qcode_var.qcode_push_vv_word,
    0x50: opcode_handlers.qcode_maths.qcode_cmp_mult,
    0x51: opcode_handlers.qcode_maths.qcode_cmp_mult,
    0x52: opcode_handlers.qcode_maths.qcode_cmp_mult,
    # 0x53: call procedure EE:
    0x54: opcode_handlers.qcode_maths.qcode_cmp_div,
    0x55: opcode_handlers.qcode_maths.qcode_cmp_div,
    0x56: opcode_handlers.qcode_maths.qcode_cmp_div,
    # 0x57 [[Additional sub calls]]
    0x58: opcode_handlers.qcode_maths.qcode_pow,
    0x59: opcode_handlers.qcode_maths.qcode_pow,
    0x5A: opcode_handlers.qcode_maths.qcode_pow,
    0x5B: opcode_handlers.qcode_cmp.qcode_cmp_if,
    0x5C: opcode_handlers.qcode_cmp.qcode_cmp_and,
    0x5D: opcode_handlers.qcode_cmp.qcode_cmp_and,
    0x5E: opcode_handlers.qcode_cmp.qcode_cmp_and,
    0x5F: opcode_handlers.qcode_var.qcode_push_vv_long,
    0x60: opcode_handlers.qcode_cmp.qcode_cmp_or,
    0x61: opcode_handlers.qcode_cmp.qcode_cmp_or,
    0x62: opcode_handlers.qcode_cmp.qcode_cmp_or,
    0x63: opcode_handlers.qcode_var.qcode_push_vv_word_to_long,
    0x64: opcode_handlers.qcode_cmp.qcode_cmp_not,
    0x65: opcode_handlers.qcode_cmp.qcode_cmp_not,
    0x66: opcode_handlers.qcode_cmp.qcode_cmp_not,
    0x67: qcode_invalid_opcode,
    0x68: opcode_handlers.qcode_maths.qcode_negate,                 # COMPLETE
    0x69: opcode_handlers.qcode_maths.qcode_negate,                 # COMPLETE
    0x6A: opcode_handlers.qcode_maths.qcode_negate,                 # COMPLETE
    # 0x6B [[ @ Operator ]]
    0x6C: opcode_handlers.qcode_maths.qcode_less_percent,
    0x6D: opcode_handlers.qcode_maths.qcode_greater_percent,
    0x6E: opcode_handlers.qcode_maths.qcode_plus_percent,
    0x6F: opcode_handlers.qcode_maths.qcode_minus_percent,
    0x70: opcode_handlers.qcode_maths.qcode_mult_percent,
    0x71: opcode_handlers.qcode_maths.qcode_div_percent,
    0x72: qcode_invalid_opcode,
    0x73: qcode_invalid_opcode,
    # 0x74 - 0x77 [[ RETURN no value ]]
    0x78: opcode_handlers.qcode_var.qcode_push_word_pop,            # COMPLETE
    0x79: opcode_handlers.qcode_var.qcode_push_word_pop,            # COMPLETE
    0x7A: opcode_handlers.qcode_var.qcode_push_long_pop,            # COMPLETE
    0x7B: opcode_handlers.qcode_var.qcode_push_long_pop,            # COMPLETE
    0x7C: opcode_handlers.qcode_var.qcode_push_real_pop,            # COMPLETE
    0x7D: opcode_handlers.qcode_var.qcode_push_real_pop,            # COMPLETE
    0x7E: qcode_invalid_opcode,
    0x7F: qcode_invalid_opcode,
    0x80: opcode_handlers.qcode_var.qcode_pop_discard,              # COMPLETE
    0x81: opcode_handlers.qcode_var.qcode_pop_discard,              # COMPLETE
    0x82: opcode_handlers.qcode_var.qcode_pop_discard,              # COMPLETE
    0x83: opcode_handlers.qcode_var.qcode_pop_discard,              # COMPLETE
    0x84: opcode_handlers.qcode_var.qcode_store_pop1_in_pop2,
    0x85: opcode_handlers.qcode_var.qcode_store_pop1_in_pop2,
    0x86: opcode_handlers.qcode_var.qcode_store_pop1_in_pop2,
    0x87: opcode_handlers.qcode_var.qcode_store_pop1_in_pop2,
    0x88: opcode_handlers.qcode_screen.qcode_print_semi,
    0x89: opcode_handlers.qcode_screen.qcode_print_semi,
    0x8A: opcode_handlers.qcode_screen.qcode_print_semi,
    0x8B: opcode_handlers.qcode_screen.qcode_print_semi,

    0x92: opcode_handlers.qcode_screen.qcode_print,

    0x98: opcode_handlers.qcode_memory.qcode_poke,
    0x99: opcode_handlers.qcode_memory.qcode_poke,
    0x9A: opcode_handlers.qcode_memory.qcode_poke,
    0x9B: opcode_handlers.qcode_memory.qcode_poke,
    0x9C: opcode_handlers.qcode_memory.qcode_pokeb,
    0x9D: opcode_handlers.qcode_dbf.qcode_append,
    0x9E: opcode_handlers.qcode_screen.qcode_at,

    0xA0: opcode_handlers.qcode_gen.qcode_beep,                     # NOT IMPLEMENTED
    0xA1: opcode_handlers.qcode_dbf.qcode_close, # STUB
    0xA2: opcode_handlers.qcode_screen.qcode_cls, # STUB

    0xA5: opcode_handlers.qcode_dbf.qcode_create, # STUB
    0xA6: opcode_handlers.qcode_screen.qcode_cursor, # STUB
    0xA7: opcode_handlers.qcode_filesystem.qcode_delete_file,

    0xA9: opcode_handlers.qcode_gen.qcode_escape,

    0xAB: opcode_handlers.qcode_gen.qcode_vector,

    0xAE: opcode_handlers.qcode_modules.qcode_loadm,

    0xB1: opcode_handlers.qcode_gen.qcode_onerr,

    0xB4: opcode_handlers.qcode_dbf.qcode_open,
    0xB5: opcode_handlers.qcode_gen.qcode_pause,

    0xB7: opcode_handlers.qcode_filesystem.qcode_iosignal, # STUB

    0xB9: opcode_handlers.qcode_gen.qcode_randomize,                    # COMPLETE

    0xBB: opcode_handlers.qcode_gen.qcode_stop,
    0xBC: opcode_handlers.qcode_gen.qcode_trap,                         # COMPLETE
    0xBD: opcode_handlers.qcode_dbf.qcode_update, # STUB
    0xBE: opcode_handlers.qcode_dbf.qcode_use,
    0xBF: opcode_handlers.qcode_gen.qcode_goto,
    # C0 RETURN pop+ (type popped depends on procedure type)

    0xC5: opcode_handlers.qcode_graphics.qcode_gsavebit, # PARTIAL
    0xC6: opcode_handlers.qcode_graphics.qcode_gclose,
    0xC7: opcode_handlers.qcode_graphics.qcode_guse,
    0xC8: opcode_handlers.qcode_graphics.qcode_gsetwin,
    0xC9: opcode_handlers.qcode_graphics.qcode_gvisible,                # COMPLETE
    0xCA: opcode_handlers.qcode_graphics.qcode_gfont,

    0xCC: opcode_handlers.qcode_graphics.qcode_ggmode,
    0xCD: opcode_handlers.qcode_graphics.qcode_gtmode,  # STUB
    0xCE: opcode_handlers.qcode_graphics.qcode_gstyle,
    0xCF: opcode_handlers.qcode_graphics.qcode_gorder,
    0xD0: opcode_handlers.qcode_graphics.qcode_ginfo,   # PARTIAL
    0xD1: opcode_handlers.qcode_graphics.qcode_gcls,
    0xD2: opcode_handlers.qcode_graphics.qcode_gat,
    0xD3: opcode_handlers.qcode_graphics.qcode_gmove,
    0xD4: opcode_handlers.qcode_graphics.qcode_gprint,
    0xD5: opcode_handlers.qcode_graphics.qcode_gprint,
    0xD6: opcode_handlers.qcode_graphics.qcode_gprint,
    0xD7: opcode_handlers.qcode_graphics.qcode_gprint,
    0xD8: opcode_handlers.qcode_graphics.qcode_gprint_comma,
    0xD9: opcode_handlers.qcode_graphics.qcode_gprintb,
    0xDA: opcode_handlers.qcode_graphics.qcode_glineby,
    0xDB: opcode_handlers.qcode_graphics.qcode_gbox,

    0xDE: opcode_handlers.qcode_graphics.qcode_gpoly,
    0xDF: opcode_handlers.qcode_graphics.qcode_gfill,
    0xE0: opcode_handlers.qcode_graphics.qcode_gpatt,   # PARTIAL
    0xE1: opcode_handlers.qcode_graphics.qcode_gcopy,
    0xE2: opcode_handlers.qcode_graphics.qcode_gscroll,
    0xE3: opcode_handlers.qcode_graphics.qcode_gupdate,
    0xE4: opcode_handlers.qcode_gen.qcode_getevent,
    0xE5: opcode_handlers.qcode_graphics.qcode_glineto,
    0xE6: opcode_handlers.qcode_graphics.qcode_gpeekline,
    0xE7: opcode_handlers.qcode_screen.qcode_screen_4,      # STUB
    0xE8: opcode_handlers.qcode_filesystem.qcode_iowaitstat,

    0xEA: opcode_handlers.qcode_menu.qcode_minit,
    0xEB: opcode_handlers.qcode_menu.qcode_mcard,
    0xEC: opcode_handlers.qcode_dialog.qcode_dinit,
    # ED [[Additional sub calls]]
    0xEE: opcode_handlers.qcode_graphics.qcode_setname,
    0xEF: opcode_handlers.qcode_gen.qcode_statuswin,
    0xF0: opcode_handlers.qcode_gen.qcode_busy,                 # STUB
    0xF1: opcode_handlers.qcode_gen.qcode_lock,                 # NOT IMPLEMENTED
    0xF2: opcode_handlers.qcode_graphics.qcode_ginvert,
    0xF3: opcode_handlers.qcode_graphics.qcode_gxprint,         # STUB to gPRINT
    0xF4: opcode_handlers.qcode_graphics.qcode_gborder,
    0xF5: opcode_handlers.qcode_graphics.qcode_gclock,

    0xF8: opcode_handlers.qcode_filesystem.qcode_mkdir,

    0xFA: opcode_handlers.qcode_filesystem.qcode_setpath,
    0xFB: opcode_handlers.qcode_datetime.qcode_secstodate,

    0xFC: opcode_handlers.qcode_gen.qcode_giprint
}

opcode_0x57_handler = {
    0x00: opcode_handlers.qcode_var.qcode_addr,
    0x01: opcode_handlers.qcode_str.qcode_asc,
    0x02: opcode_handlers.qcode_kernel.qcode_call,      # PARTIAL

    0x04: opcode_handlers.qcode_datetime.qcode_day,

    0x07: opcode_handlers.qcode_gen.qcode_err_virt,
    0x08: opcode_handlers.qcode_filesystem.qcode_exist,

    0x0A: opcode_handlers.qcode_gen.qcode_get,
    0x0B: opcode_handlers.qcode_filesystem.qcode_ioa,

    0x0D: opcode_handlers.qcode_filesystem.qcode_ioopen,
    0x0E: opcode_handlers.qcode_filesystem.qcode_iowrite,
    0x0F: opcode_handlers.qcode_filesystem.qcode_ioread,
    0x10: opcode_handlers.qcode_filesystem.qcode_ioclose,
    0x11: opcode_handlers.qcode_filesystem.qcode_iowait,            # STUB
    0x12: opcode_handlers.qcode_datetime.qcode_hour,
    0x13: opcode_handlers.qcode_gen.qcode_key,
    0x14: opcode_handlers.qcode_str.qcode_len,                      # COMPLETE
    0x15: opcode_handlers.qcode_str.qcode_loc,
    0x16: opcode_handlers.qcode_datetime.qcode_minute,
    0x17: opcode_handlers.qcode_datetime.qcode_month,
    0x18: opcode_handlers.qcode_memory.qcode_peekb,
    0x19: opcode_handlers.qcode_memory.qcode_peekw,    

    0x1C: opcode_handlers.qcode_datetime.qcode_second,
    0x1D: opcode_handlers.qcode_gen.qcode_usr,                      # Can not implement!!
    0x1E: opcode_handlers.qcode_datetime.qcode_year,
    0x1F: opcode_handlers.qcode_var.qcode_addr_str,

    0x21: opcode_handlers.qcode_filesystem.qcode_ioseek,
    0x22: opcode_handlers.qcode_gen.qcode_kmod, # STUB

    0x26: opcode_handlers.qcode_graphics.qcode_gcreate_5,
    0x27: opcode_handlers.qcode_graphics.qcode_gcreatebit,
    0x28: opcode_handlers.qcode_graphics.qcode_gloadbit,

    0x2B: opcode_handlers.qcode_graphics.qcode_gidentity,
    0x2C: opcode_handlers.qcode_graphics.qcode_gx,
    0x2D: opcode_handlers.qcode_graphics.qcode_gy,
    0x2E: opcode_handlers.qcode_graphics.qcode_gwidth,
    0x2F: opcode_handlers.qcode_graphics.qcode_gheight,
    0x30: opcode_handlers.qcode_graphics.qcode_goriginx,
    0x31: opcode_handlers.qcode_graphics.qcode_goriginy,
    0x32: opcode_handlers.qcode_graphics.qcode_gtwidth,             # COMPLETE

    0x34: opcode_handlers.qcode_gen.qcode_testevent,                # STUB
    0x35: opcode_handlers.qcode_kernel.qcode_OS,                    # PARTIAL
    0x36: opcode_handlers.qcode_menu.qcode_menu,
    0x37: opcode_handlers.qcode_dialog.qcode_dialog,
    0x38: opcode_handlers.qcode_dialog.qcode_alert,                 # PARTIAL
    0x39: opcode_handlers.qcode_graphics.qcode_gcreate_6,
    0x3A: opcode_handlers.qcode_menu.qcode_menu_var,
    0x3B: opcode_handlers.qcode_graphics.qcode_createsprite,

    0x40: opcode_handlers.qcode_datetime.qcode_days,

    0x42: opcode_handlers.qcode_maths.qcode_int,                    # COMPLETE

    0x45: opcode_handlers.qcode_datetime.qcode_datetosecs,

    0x4B: opcode_handlers.qcode_memory.qcode_alloc,                 # COMPLETE

    0x50: opcode_handlers.qcode_var.qcode_uadd,                     # COMPLETE
    0x51: opcode_handlers.qcode_var.qcode_usub,                     # COMPLETE

    0x53: opcode_handlers.qcode_gen.qcode_statuswininfo,            # STUB
    
    0x59: qcode_invalid_opcode,

    0x7F: qcode_invalid_opcode,
    0x80: opcode_handlers.qcode_maths.qcode_abs,                    # COMPLETE
    0x81: opcode_handlers.qcode_maths.qcode_acos,                   # COMPLETE
    0x82: opcode_handlers.qcode_maths.qcode_asin,                   # COMPLETE
    0x83: opcode_handlers.qcode_maths.qcode_atan,                   # COMPLETE
    0x84: opcode_handlers.qcode_maths.qcode_cos,                    # COMPLETE
    0x85: opcode_handlers.qcode_maths.qcode_deg,                    # COMPLETE
    0x86: opcode_handlers.qcode_maths.qcode_exp,                    # COMPLETE
    0x87: opcode_handlers.qcode_maths.qcode_flt,                    # COMPLETE
    0x88: opcode_handlers.qcode_maths.qcode_intf,                   # COMPLETE
    0x89: opcode_handlers.qcode_maths.qcode_ln,                     # COMPLETE
    0x8A: opcode_handlers.qcode_maths.qcode_log10,                  # COMPLETE
    0x8B: opcode_handlers.qcode_memory.qcode_peekf,                 # COMPLETE
    0x8C: opcode_handlers.qcode_maths.qcode_pi,                     # COMPLETE
    0x8D: opcode_handlers.qcode_maths.qcode_rad,                    # COMPLETE
    0x8E: opcode_handlers.qcode_gen.qcode_rnd,                      # COMPLETE
    0x8F: opcode_handlers.qcode_maths.qcode_sin,                    # COMPLETE
    0x90: opcode_handlers.qcode_maths.qcode_sqr,                    # COMPLETE
    0x91: opcode_handlers.qcode_maths.qcode_tan,                    # COMPLETE
    0x92: opcode_handlers.qcode_str.qcode_val,                      # COMPLETE
    0x93: opcode_handlers.qcode_cmp.qcode_max,                      # COMPLETE
    0x94: opcode_handlers.qcode_cmp.qcode_mean,                     # COMPLETE
    0x95: opcode_handlers.qcode_cmp.qcode_min,                      # COMPLETE
    0x96: opcode_handlers.qcode_cmp.qcode_std,                      # COMPLETE
    0x97: opcode_handlers.qcode_cmp.qcode_sum,                      # COMPLETE
    0x98: opcode_handlers.qcode_cmp.qcode_var,                      # COMPLETE
    0x99: opcode_handlers.qcode_gen.qcode_eval,
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
    0xC0: opcode_handlers.qcode_str.qcode_chr,                      # COMPLETE
    0xC1: opcode_handlers.qcode_datetime.qcode_datim,               # COMPLETE
    0xC2: opcode_handlers.qcode_datetime.qcode_dayname,
    0xC3: opcode_handlers.qcode_filesystem.qcode_dir,
    0xC4: opcode_handlers.qcode_gen.qcode_err_str,                  # STUB
    0xC5: opcode_handlers.qcode_str.qcode_fix,
    0xC6: opcode_handlers.qcode_str.qcode_gen,
    0xC7: opcode_handlers.qcode_gen.qcode_get_str,
    0xC8: opcode_handlers.qcode_str.qcode_hex,                      # COMPLETE

    0xCA: opcode_handlers.qcode_str.qcode_left,
    0xCB: opcode_handlers.qcode_str.qcode_lower,                    # COMPLETE
    0xCC: opcode_handlers.qcode_str.qcode_mid,                      # COMPLETE
    0xCD: opcode_handlers.qcode_datetime.qcode_month_str,
    0xCE: opcode_handlers.qcode_str.qcode_num,
    0xCF: opcode_handlers.qcode_memory.qcode_peek_str,
    0xD0: opcode_handlers.qcode_str.qcode_rept,
    0xD1: opcode_handlers.qcode_str.qcode_right,                    # COMPLETE
    0xD2: opcode_handlers.qcode_str.qcode_sci,
    0xD3: opcode_handlers.qcode_str.qcode_upper,                    # COMPLETE
    0xD4: opcode_handlers.qcode_gen.qcode_usr,                      # Can not implement!
    
    0xD6: opcode_handlers.qcode_gen.qcode_cmd,
    0xD7: opcode_handlers.qcode_gen.qcode_parse
}

opcode_0xED_handler = {
    0x00: opcode_handlers.qcode_dialog.qcode_dtext,
    0x01: opcode_handlers.qcode_dialog.qcode_dchoice,
    0x02: opcode_handlers.qcode_dialog.qcode_dlong,
    0x03: opcode_handlers.qcode_dialog.qcode_dfloat,

    0x06: opcode_handlers.qcode_dialog.qcode_dedit_2,
    0x07: opcode_handlers.qcode_dialog.qcode_dedit_3,

    0x09: opcode_handlers.qcode_dialog.qcode_dfile,
    0x0A: opcode_handlers.qcode_dialog.qcode_dbuttons,
    0x0B: opcode_handlers.qcode_dialog.qcode_dposition
}

opcode_0xFF_handler = {
    0x00: opcode_handlers.qcode_graphics.qcode_ggrey,
    0x01: opcode_handlers.qcode_graphics.qcode_defaultwin,
    0x02: opcode_handlers.qcode_gen.qcode_diaminit,             # NOT IMPLEMENTED
    0x03: opcode_handlers.qcode_gen.qcode_diampos,              # NOT IMPLEMENTED
    0x04: opcode_handlers.qcode_screen.qcode_font, # STUB
    0x05: opcode_handlers.qcode_screen.qcode_style, # STUB

    0x07: opcode_handlers.qcode_graphics.qcode_appendsprite,
    0x08: opcode_handlers.qcode_graphics.qcode_drawsprite,
    
    0x0A: opcode_handlers.qcode_graphics.qcode_posssprite,

    0x0E: opcode_handlers.qcode_gen.qcode_cache,                # NOT IMPLEMENTED
    0x0F: opcode_handlers.qcode_graphics.qcode_gbutton,

    0x10: opcode_handlers.qcode_graphics.qcode_gxborder, # STUB - uses gBORDER
    0x14: opcode_handlers.qcode_screen.qcode_screeninfo
}