import struct
from pyopo.filehandler_filesystem import *
from pyopo.window_manager import DrawableSprite
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)


def qcode_gcls(procedure, data_stack, stack):
    #_logger.debug("0xD1 - gCLS")
    procedure.get_graphics_context().gCLS()


def qcode_gclose(procedure, data_stack, stack):
    #_logger.debug("0xC6 - gCLOSE pop%1")
    procedure.get_window_manager().gCLOSE(stack.pop())
    procedure.set_trap(False)


def qcode_setname(procedure, data_stack, stack):
    #_logger.debug("0xEE - SETNAME pop$1")
    procedure.get_window_manager().set_window_name(stack.pop())


def qcode_ggmode(procedure, data_stack, stack):
    #_logger.debug("0xCC - gGMODE pop%1")
    procedure.get_graphics_context().gGMODE(stack.pop())


def qcode_gwidth(procedure, data_stack, stack):
    #_logger.debug("0x57 0x2E - PUSH% gWIDTH")
    stack.push(0, procedure.get_graphics_context().gWIDTH())


def qcode_gidentity(procedure, data_stack, stack):
    #_logger.debug("0x57 0x2B - PUSH% gIDENTITY")
    stack.push(0, procedure.get_graphics_context().gIDENTITY())


def qcode_gx(procedure, data_stack, stack):
    #_logger.debug("0x57 0x2C - PUSH% gX")
    stack.push(0, procedure.get_graphics_context().gX())
    

def qcode_gy(procedure, data_stack, stack):
    #_logger.debug("0x57 0x2D - PUSH% gY")
    stack.push(0, procedure.get_graphics_context().gY())

    
def qcode_goriginx(procedure, data_stack, stack):
    #_logger.debug("0x57 0x30 - PUSH% gORIGINX")
    stack.push(0, procedure.get_graphics_context().gORIGINX())
    

def qcode_goriginy(procedure, data_stack, stack):
    #_logger.debug("0x57 0x31 - PUSH% gORIGINY")
    stack.push(0, procedure.get_graphics_context().gORIGINY())


def qcode_gheight(procedure, data_stack, stack):
    #_logger.debug("0x57 0x2F - PUSH% gHEIGHT")
    stack.push(0, procedure.get_graphics_context().gHEIGHT())


def qcode_gsetwin(procedure, data_stack, stack):
    #_logger.debug("0xC8 - PUSH% gSETWIN")

    arg_count = procedure.read_qcode_byte()
    if arg_count == 4:
        height = stack.pop()
        width = stack.pop()
    else:
        height = None
        width = None

    x, y = stack.pop_2()
    procedure.get_graphics_context().gSETWIN(x, y, width, height)


def qcode_gcreate_5(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x26 - PUSH% gCREATE")

    # x%,y%,w%,h%,v%
    v = stack.pop()
    w, h = stack.pop_2()
    x, y = stack.pop_2()

    id = procedure.get_window_manager().gCREATE(x, y, w, h, v, 0)

    stack.push(0, id)


def qcode_gcreate_6(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x39 - PUSH% gCREATE")

    # 5 series: x%,y%,w%,h%,v%, flags%
    # 3 series: x%,y%,w%,h%,v%, grey%
    flags = stack.pop()
    v = stack.pop()
    w, h = stack.pop_2()
    x, y = stack.pop_2()

    id = procedure.get_window_manager().gCREATE(x, y, w, h, v, flags)

    stack.push(0, id)


def qcode_gborder(procedure, data_stack, stack) -> None:
    #_logger.debug(f"0xF4 - gBORDER")

    arg_count = procedure.read_qcode_byte()

    if arg_count == 3:
        width, height = stack.pop_2()
    else:
        height = None
        width = None

    flags = stack.pop()

    #_logger.debug(f" - gBORDER {flags}, {width}, {height}")

    procedure.get_graphics_context().gBORDER(flags, width, height)


def qcode_gat(procedure, data_stack, stack) -> None:
    #_logger.debug(f"0xD2 - gAT pop%2, pop%1")

    x, y = stack.pop_2()
    procedure.get_graphics_context().gAT(x, y)


def qcode_gmove(procedure, data_stack, stack) -> None:
    #_logger.debug("0xD3 - gMOVE pop%2, pop%1")

    x, y = stack.pop_2()
    procedure.get_graphics_context().gMOVE(x, y)


def qcode_gorder(procedure, data_stack, stack) -> None:
    #_logger.debug("0xCF - gORDER pop%2, pop%1")

    index = stack.pop()
    id = stack.pop()

    #_logger.debug(f" - gORDER {id}, {index}")
    procedure.get_window_manager().gORDER(id, index)


def qcode_glineto(procedure, data_stack, stack):
    #_logger.debug("0xE5 - gLINETO pop%2, pop%1")

    x, y = stack.pop_2()
    procedure.get_graphics_context().gLINETO(x, y)


def qcode_gpoly(procedure, data_stack, stack) -> None:
    dsf_offset = stack.pop()

    x = data_stack.read(0, dsf_offset)
    y = data_stack.read(0, dsf_offset + 2)
    operations = data_stack.read(0, dsf_offset + 4)

    #_logger.debug(f'0xDE - gPOLY: {x}, {y}, Operations: {operations}')

    ops = []
    for i in range(operations):
        dx = data_stack.read(0, dsf_offset + 6 + i * 4)
        dy = data_stack.read(0, dsf_offset + 8 + i * 4)
        ops.append((dx, dy))

    procedure.get_graphics_context().gPOLY(x, y, ops)


def qcode_glineby(procedure, data_stack, stack) -> None:
    #_logger.debug("0xDA - gLINEBY pop%2, pop%1")

    dx, dy = stack.pop_2()
    procedure.get_graphics_context().gLINEBY(dx, dy)


def qcode_gstyle(procedure, data_stack, stack) -> None:
    #_logger.debug("0xCE - gSTYLE pop%1")

    style = stack.pop()

    #_logger.debug(f" - gSTYLE {style} - STUB")


def qcode_gtwidth(procedure, data_stack, stack) -> None:
    #_logger.debug("0x57 0x32 - push% gTWIDTH pop$1")
    text_len = procedure.get_graphics_context().gTWIDTH(stack.pop())
    stack.push(0, text_len)


def qcode_gprint(procedure, data_stack, stack) -> None:
    op_code = procedure.get_executed_opcode()
    #_logger.debug(f"{hex(op_code)} - gPRINT pop+ ;")

    # Sanitise text
    text = str(stack.pop()).replace('\00', '') + ' '

    if len(text) > 0:
        #_logger.debug(f" - gPRINT '{text}' {len(text)} characters")
        procedure.get_graphics_context().gPRINT(text)


def qcode_gprint_comma(procedure, data_stack, stack) -> None:
    #_logger.debug("0xD8 - gPRINT ,")
    procedure.get_graphics_context().gPRINT(' ')


def qcode_gprintb(procedure, data_stack, stack) -> None:
    #_logger.debug("0xD9 - N' gPRINTB pop+ ;")

    arg_count = procedure.read_qcode_byte()

    # Defaults when not specified
    al = 2  # Default to Left Align
    tp = 0
    bt = 0
    m = 0

    if arg_count == 5:
        m = stack.pop()

    if arg_count >= 4:
        bt = stack.pop()

    if arg_count >= 3:
        tp = stack.pop()

    if arg_count >= 2:
        al = stack.pop()

    w = stack.pop()
    t = stack.pop()

    #_logger.debug(f" - gPRINTB args={arg_count} {t}, {w}, {al}, {tp}, {bt}, {m}")

    procedure.get_graphics_context().gPRINTB(str(t), w, al, tp, bt, m)


def qcode_gfont(procedure, data_stack, stack) -> None:
    #_logger.debug(f"0xCA - gFONT")

    font_id = stack.pop()
    procedure.get_graphics_context().gFONT(font_id)
    procedure.set_trap(False)


def qcode_guse(procedure, data_stack, stack) -> None:
    #_logger.debug(f"0xC7 - gUSE pop%1")
    procedure.get_window_manager().gUSE(stack.pop())
    procedure.set_trap(False)


def qcode_gbutton(procedure, data_stack, stack) -> None:
    #_logger.debug(f"0xFF 0x0F - gBUTTON pop%1")

    st = stack.pop()
    width, height = stack.pop_2()
    ty = stack.pop()
    text = stack.pop()

    #_logger.debug(f" - gBUTTON '{text}', {ty}, {width}, {height}, {st}")
    procedure.get_graphics_context().gBUTTON(text, ty, width, height, st)


def qcode_gupdate(procedure, data_stack, stack) -> None:
    #_logger.debug("0xE3 - gUPDATE")

    # Qn format 0,1,FF (Off, On, Omitted)
    arg = procedure.read_qcode_byte()
    procedure.get_window_manager().gUPDATE(arg)


def qcode_defaultwin(procedure, data_stack, stack):
    #_logger.debug("0xFF 0x01 - DEFAULTWIN")

    mode = stack.pop()
    procedure.get_window_manager().DEFAULTWIN(mode)


def qcode_ggrey(procedure, data_stack, stack):
    #_logger.debug("0xFF 0x00 - gGREY")

    mode = stack.pop()

    #_logger.debug(f" -gGREY {mode}")

    procedure.get_graphics_context().gGREY(mode)


def qcode_gfill(procedure, data_stack, stack):
    #_logger.debug("0xDF - gFILL")

    gmode = stack.pop()
    width, height = stack.pop_2()

    #_logger.debug(f"gFILL {width}, {height}, {gmode}")
    procedure.get_graphics_context().gFILL(width, height, gmode)


def qcode_gbox(
    procedure,
    data_stack,
    stack
) -> None:

    #_logger.debug("0xD8 - gBOX")

    width, height = stack.pop_2()
    procedure.get_graphics_context().gBOX(width, height)


def qcode_gclock(procedure, data_stack, stack):
    #_logger.debug(f"0xF5 - gCLOCK")

    arg = procedure.read_qcode_byte()

    if arg > 1:
        for i in range(arg-1):
            stack.pop()
        #_logger.debug(f" - gCLOCK arg count = {arg-1}")
    elif arg == 0:
        #_logger.debug(f" - gCLOCK OFF")
        pass
    elif arg == 1:
        #_logger.debug(f" - gCLOCK ON")
        pass

    #_logger.warning(f"gCLOCK - STUB")

    #graphics_cursor = procedure.get_graphics_context()


def qcode_gvisible(procedure, data_stack, stack) -> None:
    #_logger.debug("0xC9 - gVISIBLE")

    mode = procedure.read_qcode_byte()
    procedure.get_graphics_context().gVISIBLE(mode)


def qcode_gpeekline(
    procedure,
    data_stack,
    stack
) -> None:

    #_logger.debug("0xE6 - gPEEKLINE  pop%5 pop%4 pop%3 pop%2 pop%1")

    ln = stack.pop()
    d_addr = stack.pop()
    x, y = stack.pop_2()
    id = stack.pop()

    #_logger.debug(f" - gPEEKLINE {id}, {x}, {y}, {d_addr}, {ln}")
    line_data_bits = procedure.get_window_manager().gPEEKLINE(
        id, x, y, ln)
    #_logger.debug(line_data_bits)

    # Bits need to be packed to 16bit words
    bits_required = int(len(line_data_bits) / 16)
    bits_required += 16 if (len(line_data_bits) -
                            bits_required * 16) > 0 else 0

    bitstring = line_data_bits.rjust(bits_required, '0')
    for i in range(0, len(bitstring), 16):
        bitvalue = int(bitstring[i:i+16], 2)

        #_logger.debug(f"{bitstring[i:i+16]} > {bitvalue} to DSF {d_addr + int(i/16) * 2}")
        # Iterate through the DSF as a word as we write it out
        data_stack.write(4, bitvalue, d_addr + int(i/16) * 2)


def qcode_gloadbit(procedure, data_stack, stack):
    #_logger.debug("0x57 0x28 - gLOADBIT")

    args = procedure.read_qcode_byte()

    # Defaults
    index = 0
    write = 1

    if args == 3:
        index = stack.pop()

    if args >= 2:
        write = stack.pop()

    name = stack.pop()

    if not '.' in name:
        # If there is no extension on the given file, .pic is assummed
        name += '.PIC'

    trans_name = translate_path_from_sibo(name, procedure.executable)
    #_logger.debug(f" - gLOADBIT {name} > {trans_name} {write} {index}")

    # Depending on whether the the source file is the OPA itself or a PIC file, choose a different path

    if trans_name == procedure.executable.file:
        # Loading an image from the OPA itself

        # The user could have performed CALL(0x5F8D, cx, dx) to change the offset in the file to read an image
        open_addr_offset = None
        if procedure.get_window_manager().open_address:
            open_addr_offset = procedure.get_window_manager().open_address[1]

        # Extract the corresponding binary data from the OPA file itself
        id = None
        for e in procedure.executable.embedded_files:
            if not open_addr_offset or open_addr_offset == e['start_offset']:
                if e['type'] == 'PIC':
                    #_logger.debug(" - Loading internal PIC from OPA")
                    pic_binary = procedure.executable.binary[e['start_offset']                                                             :e['end_offset']]
                    id = procedure.executable.window_manager.gLOADBIT_binary(
                        pic_binary, write, index)
                    break

        if not id:
            # Could not find an embedded PIC file
            raise ('No embedded PIC file detected')
    else:
        # Load from an external .PIC file
        id = procedure.get_window_manager().gLOADBIT(
            trans_name, write, index)

    stack.push(0, id)


def qcode_gxborder(procedure, data_stack, stack):
    #_logger.debug("0xFF 0x10 - gXBORDER")

    arg_count = procedure.read_qcode_byte()

    if arg_count == 4:
        width, height = stack.pop_2()
    else:
        height = None
        width = None

    flags = stack.pop()
    type = stack.pop()

    #_logger.debug(f" - gXBORDER {type}, {flags}, {width}, {height}")

    procedure.get_graphics_context().gXBORDER(type, flags, width, height)


def qcode_gxprint(procedure, data_stack, stack):
    #_logger.debug("0xF3 - gXPRINT pop$ pop%")

    flags = stack.pop()
    text = stack.pop()

    #_logger.debug(f" - gXPRINT {text} {flags}")
    procedure.get_graphics_context().gPRINT(text)


def qcode_gcopy(procedure, data_stack, stack):
    #_logger.debug("0xE1 - gCOPY pop% pop% pop% pop% pop% pop%")

    # gCOPY id%,x%,y%,w%,h%,mode%

    mode = stack.pop()
    w, h = stack.pop_2()
    x, y = stack.pop_2()
    id = stack.pop()

    #_logger.debug(f" - gCOPY {id} {x} {y} {w} {h} {mode}")
    procedure.get_window_manager().gCOPY(id, x, y, w, h, mode)
    procedure.set_trap(False)


def qcode_gpatt(procedure, data_stack, stack):
    #_logger.debug("0xE0 - gPATT pop% pop% pop% pop%")

    mode = stack.pop()
    w, h = stack.pop_2()
    id = stack.pop()

    #_logger.debug(f" - gPATT {id} {w} {h} {mode}")
    procedure.get_window_manager().gPATT(id, w, h, mode)
    procedure.set_trap(False)


def qcode_gtmode(procedure, data_stack, stack):
    #_logger.debug("0xCD - gTMODE pop%")

    mode = stack.pop()

    #_logger.warning(f" - gTMODE {mode} - STUB")
    procedure.get_graphics_context().gTMODE(mode)


def qcode_ginfo(procedure, data_stack, stack):
    #_logger.debug("0xD0 - gINFO pop%")

    dsf_offset = stack.pop()

    ginfo = procedure.get_graphics_context().gINFO()

    #_logger.debug(f" - gINFO {dsf_offset}")

    # Write out gINFO struct to memory
    for i in range(32):
        data_stack.write(0, ginfo[i], dsf_offset + 2 * i)


def qcode_gcreatebit(procedure, data_stack, stack):
    w, h = stack.pop_2()

    id = procedure.get_window_manager().gCREATE(
        0, 0, w, h, False, 0, drawable=True)

    #_logger.debug(f"0x57 0x27 - gCREATEBIT({w}, {h}) -> {id}")

    stack.push(0, id)


def qcode_ginvert(procedure, data_stack, stack):
    w, h = stack.pop_2()

    procedure.get_graphics_context().gINVERT(w, h)

    #_logger.debug(f"0xF2 - gINVERT({w}, {h})")


def qcode_gscroll(procedure, data_stack, stack):

    args = procedure.read_qcode_byte()

    xpos = None
    ypos = None
    width = None
    height = None

    if args == 6:
        width, height = stack.pop_2()
        xpos, ypos = stack.pop_2()

    dx, dy = stack.pop_2()

    procedure.get_graphics_context().gSCROLL(dx, dy, xpos, ypos, width, height)

    #_logger.debug(f"0xE2 - gSCROLL({dx}, {dy}, {xpos}, {ypos}, {width}, {height})")


def qcode_createsprite(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x3B - CREATESPRITE")
    sprite_id = DrawableSprite.create_sprite()

    stack.push(0, sprite_id)


def qcode_appendsprite(procedure, data_stack, stack):
    #_logger.debug("0x57 0x07 - APPENDSPRITE")

    # Nx: 0 = 2 arguments, 1 = 4 arguments
    nx = procedure.read_qcode_byte()

    dx = 0
    dy = 0

    if nx == 1:
        dx, dy = stack.pop_2()

    bitmap_arr_addr = stack.pop()
    tenths = stack.pop()

    #_logger.debug(f"APPENDSPRITE {tenths}, {dx}, {dy}, {bitmap_arr_addr}")

    spritelist = []
    for i in range(6):
        dsf_text = data_stack.read(3, bitmap_arr_addr, i)

        if len(dsf_text) == 0:
            trans_name = ""
        else:
            trans_name = translate_path_from_sibo(
                dsf_text, procedure.executable)

        #_logger.debug(f"{dsf_text} -> {trans_name}")
        spritelist.append(trans_name)

    DrawableSprite.append_sprite(tenths, spritelist, dx, dy)


def qcode_drawsprite(procedure, data_stack, stack):
    #_logger.debug("0x57 0x08 - DRAWSPRITE")

    dx, dy = stack.pop_2()
    procedure.get_window_manager().DRAWSPRITE(dx, dy)


def qcode_posssprite(procedure, data_stack, stack):
    #_logger.debug("0x57 0x0A - POSSSPRITE")

    dx, dy = stack.pop_2()
    procedure.get_window_manager().POSSSPRITE(dx, dy)


def qcode_gsavebit(procedure, data_stack, stack):
    #_logger.debug("0xC5 - gSAVEBIT")

    # Nx: 0 = 1 argument, 1 = 3 arguments
    nx = procedure.read_qcode_byte()

    height = None if nx == 0 else stack.pop()
    width = None if nx == 0 else stack.pop()

    name = stack.pop()
    trans_name = translate_path_from_sibo(name, procedure.executable)

    procedure.get_graphics_context().gSAVEBIT(trans_name, width, height)
    procedure.set_trap(False)
