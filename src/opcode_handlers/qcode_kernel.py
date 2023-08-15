import struct
import time
import random
import pygame
import datetime

from filehandler_filesystem import *
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

TICKS_PER_SECOND = 32 # S3 is 32, Emulator is 18.2

# Battery emulated values
BATTERY_MAH = 2800

"""
 This is the S5 Mapping!!!
    System   9:1  Esc     15:0  Delete   4:0  1 14:1  A 12:2  N  0:6
    Data     7:1  Tab      0:2  Enter    0:0  2 14:2  B  8:6  O  4:5
    Word    11:1  Control  4:7  ShiftR   6:7  3 10:6  C 10:3  P  2:5
    Agenda   3:1  ShiftL   2:7  Up      14:5  4  8:2  D 10:4  Q 12:1
    Time     1:1  Psion    0:7  Left     0:4  5  8:3  E 10:5  R  8:1
    World    5:1  Menu    10:7  Down     0:5  6 14:3  F 10:1  S 12:4
    Calc     3:0  Diamond  8:7  Right    0:1  7  6:6  G  8:5  T  8:4
    Sheet    1:0  Space    8:0  Help     6:2  8  4:3  H 14:6  U  6:5
    + and =  2:3  - and _  2:2                9  4:4  I  4:2  V 10:2
    * and :  2:6  / and ;  2:1                0  2:4  J  6:4  W 12:5
    , and <  6:1  . and > 14:4                        K  4:1  X 12:6
                                                      L  4:6  Y  0:3
                                                      M  6:3  Z 12:3
"""
HwGetScanCodes = {
    pygame.K_RETURN:     (1, 0x01), # Enter
    pygame.K_RIGHT:    (1, 0x02), # Right
    pygame.K_TAB:      (1, 0x04), # Tab
    # Y
    pygame.K_LEFT:    (1, 0x10), # Left
    pygame.K_DOWN:    (1, 0x20), # Down

    pygame.K_ESCAPE:     (8, 0x0100), # Esc

    pygame.K_DELETE:      (3, 0x01), # Delete
    
    pygame.K_SPACE:     (5, 0x01), # Space
    
    pygame.K_UP:    (8, 0x20), # Up
}

def qcode_OS(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x35 - OS")

    # N Format
    arg_count = int(procedure.read_qcode_byte())
    if arg_count == 3:
        addr_2 = stack.pop()
    else:
        addr_2 = None
    
    addr_1 = stack.pop()
    i = stack.pop()

    #_logger.debug(f" - OS {hex(i)}, {addr_1}, {addr_2}")

    if i == 0x87:
        #_logger.debug(f' - OS Call 0x87 - carried out automatically for OPL programs - Not Implemented')
        pass
    elif i == 0x88:
        #_logger.debug(f' - OS Call 0x88 - ProcSetPriority ProcID={addr_1} - Not Implemented')
        pass
    elif i == 0x8B:
        # General Services

        # GenVersion
        # $123F: Final Release

        pass
    elif i == 0x8D:
        #_logger.debug("- OS Call - Window Server")

        if arg_count == 2:
            #_logger.debug(f" - wEndRedraw of window handle {addr_1} - Not Implemented")
            pass
    elif i == 0x8E:
        #_logger.debug(" - Hardware Control 0x8E  - Not Implemented")
        pass
    else:
        #_logger.warning(f'OS Call Not implemented - STUB')
        input()

    # Return the register flags
    stack.push(0, 0)


def qcode_call(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x02 - CALL")

    # N FOrmat
    arg_count = int(procedure.read_qcode_byte())

    # CALL(s%,bx%,cx%,dx%,si%,di%)


    args = []
    for i in range(arg_count):
        args.append(stack.pop())

    #_logger.debug(f" - CALL {arg_count} arguments - CALL({args})")

    # Go through known high level Calls
    if args[-1] == 0x0189:
        # Fn $89 Sub $01
        # TimSleepForTicks fails
        #_logger.debug("CALL 0x0189: - TimSleepForTicks fails")
        
        time.sleep(1.0 / TICKS_PER_SECOND * args[0])
        stack.push(0, 0)
    elif args[-1] == 0x0C88:
        # Fn $88 Sub $0C
        # ProcRename fails
        #_logger.debug("CALL 0x0C88: - ProcRename - Not Implemented")

        stack.push(0, 0)
    elif args[-1] == 0x058B:
        # Fn $8B Sub $05
        # GenGetCountryData
        #_logger.debug("CALL 0x058B: - GenGetCountryData")

        """
        GenGetCountryData
            BX: 40 byte buffer
        Fills the buffer with country-specific data:
        Offset  0 (word): country code (e.g. UK is 44) of locale
        Offset  2 (word): current offset from GMT in minutes (+ is ahead)
        Offset  4 (byte): date format (0 = MDY, 1 = DMY, 2 = YMD)
        Offset  5 (byte): time format (0 = am-pm, 1 = 24 hour)
        Offset  6 (byte): currency symbol position (0 = before, 1 = after)
        Offset  7 (byte): currency symbol separated with space (0 = yes, 1 = no)
        Offset  8 (byte): currency decimal places
        Offset  9 (byte): currency negative format (0 = minus, 1 = brackets)
        Offset 10 (byte): currency triad threshold
        Offset 11 (byte): triad separator
        Offset 12 (byte): decimal separator
        Offset 13 (byte): date separator
        Offset 14 (byte): time separator
        Offset 15 to  23: currency symbol (cstr)
        Offset 24 (byte): start of week (0 = Mon, 1 = Tue, ... 6 = Sun)
        Offset 25 (byte): currently active summer times:
            Bit 0:       home
            Bit 1:       European
            Bit 2:       Northern
            Bit 3:       Southern
            Bits 4 to 7: unused, always zero
        Offset 26 (byte): clock type (0 = analogue, 1 = digital)
        Offset 27 (byte): number of letters in day abbreviation (0 to 6)
        Offset 28 (byte): number of letters in month abbreviation (0 to 255)
        Offset 29 (byte): workdays (the set bits indicate the workdays)
            Bit 0: Monday
            Bit 1: Tuesday
            Bit 2: Wednesday
            Bit 3: Thursday
            Bit 4: Friday
            Bit 5: Saturday
            Bit 6: Sunday
            Bit 7: always zero
        Offset 30 (byte): units (0 = inches, 1 = centimetres)
        """
        
        dsf_addr = args[-2]

        countrydata = bytearray(40)

        struct.pack_into("<H", countrydata, 0, 44) # UK Dial code

        countrydata[4] = 1 # DMY
        countrydata[5] = 1 # 24hr Clock
        countrydata[6] = 0 # Currency symbol (£) before
        countrydata[7] = 0 # No Currency symbol space
        countrydata[8] = 2 # Currency decimal places
        countrydata[9] = 0 # Currency negative format -
        countrydata[10] = 3 # Triad threshold
        countrydata[11] = ord(",") # Tirad char
        countrydata[12] = ord(".") # Decimal char
        countrydata[13] = ord("-") # Date Seperator
        countrydata[14] = ord(":") # Time Seperator
        countrydata[15] = ord("£") # Currency symbol
        countrydata[24] = 0 # Mon start of weeek
        countrydata[26] = 1 # Digital clock
        countrydata[27] = 3 # 3 chr day abbr
        countrydata[28] = 3 # 3 chr month abbr
        countrydata[29] = 31 # Mon-Fri workdays
        countrydata[30] = 1 # CM units

        data_stack.memory[dsf_addr:dsf_addr+len(countrydata)] = countrydata
        stack.push(0, 0)

    elif args[-1] == 0x118E:
        # Fn $8E Sub $11
        # HwGetSupplyStatus
        #_logger.debug("CALL 0x118E: - HwGetSupplyStatus")

        """
        HwGetSupplyStatus
        BX: 6 byte buffer
        Gets information about the power supply. The buffer is filled with the
        following data:
        Offset  0 (word): main battery voltage in mV
        Offset  2 (word): backup battery voltage in mV
        Offset  4 (word): positive if external power is available, zero if not
                    available, and negative if the detector is disabled
                    because an SSD door is open.
        """

        dsf_addr = args[-2]

        supplystatus = [0] * 3

        supplystatus[0] = 1500
        supplystatus[1] = 1500
        supplystatus[2] = 0

        for i in range(len(supplystatus)):
            data_stack.write(0, supplystatus[i], dsf_addr + 2 * i)

        stack.push(0, 0)

    elif args[-1] == 0x1b8B:
        # Fn $8B Sub $1B
        # GenGetLanguageCode
        #_logger.debug("CALL 0x1b8B: - GenGetLanguageCode")
        
        stack.push(0, 1) # English - UK

    elif args[-1] == 0x1C8E:
        # Fn $8E Sub $1C
        # HwSupplyWarnings
        #_logger.debug("CALL 0x1C8E: - HwSupplyWarnings")

        """

        HwSupplyWarnings
            BX: 8 byte buffer
        Gets information about the power supply. The buffer is filled with the
        following data:
        Offset  0 (word): main battery good voltage threshold in mV
        Offset  2 (word): backup battery good voltage threshold in mV
        Offset  4 (word): main battery nominal maximum voltage in mV
        Offset  6 (word): backup battery nominal maximum voltage in mV
        The values will depend on the battery type set by GenSetBatteryType.
        
        """

        dsf_addr = args[-2]

        supplystatus = [0] * 4

        supplystatus[0] = 1400
        supplystatus[1] = 1400
        supplystatus[2] = 1400
        supplystatus[3] = 1400

        for i in range(len(supplystatus)):
            data_stack.write(0, supplystatus[i], dsf_addr + 2 * i)

        stack.push(0, 0)

    elif args[-1] == 0x228E:
        # Fn $8E Sub $22
        # HwSupplyInfo v3

        """
        
        HwSupplyInfo v3
            BX: 22 byte buffer
        Fills the buffer with additional information about the power supply:
        Offset  0 (byte): main battery status:
            0 = not present
            1 = very low voltage
            2 = low voltage
            3 = good voltage
        Offset  1 (byte): worst main battery status since batteries last inserted
        Offset  2 (byte): non-zero if backup battery voltage is good
        Offset  3 (byte): non-zero if external supply is present
        Offset  4 (word): warning flags
            Bit 0: set if power supply too low for sound
            Bit 1: set if power supply too low to use flash
            Bit 2: set   if offset 6 changed because system clock changed
                clear if offset 6 changed because the batteries were changed
        Offset  6 (long): abstime when batteries inserted
        Offset 10 (long): ticks running on battery
        Offset 14 (long): ticks running on external supply
        Offset 18 (long): mA-ticks (i.e. mAhours * 60 * 60 * 32)

        18 expects ticks in internal format
        
        """

        dsf_addr = args[-2]

        
        supplystatus = bytearray(22)

        supplystatus[0] = 3 # Good voltage
        supplystatus[1] = 3 # Always been good
        supplystatus[2] = 1 # Backup battery good
        supplystatus[3] = 0 # External power not present
        supplystatus[4] = 0 # Warning Flags
        supplystatus[5] = 0 # Warning Flags

        # Time when batteries were inserted (a day ago)
        struct.pack_into("<L", supplystatus, 6, int((datetime.datetime.now()-datetime.timedelta(days=1)).timestamp()))
        
        # Ticks running on battery  - 1hr
        struct.pack_into("<L", supplystatus, 10, int(3600 * TICKS_PER_SECOND))

        # Ticks running on external power  - 15mins
        struct.pack_into("<L", supplystatus, 14, int(3600 * TICKS_PER_SECOND))

        # mA ticks
        struct.pack_into("<L", supplystatus, 18, int(BATTERY_MAH * 60 * 60 * TICKS_PER_SECOND))

        # Write to DSF
        data_stack.memory[dsf_addr:dsf_addr+len(supplystatus)] = supplystatus

        stack.push(0, 0)

    elif args[-1] == 0x6C8D:
        #_logger.info("CALL 0x6c8d: - Send Machine Switch On Event - Not Implemented")
        stack.push(0, 0)
        
    elif args[-1] == 0x0F8B:
        # Fn $8B Sub $0F
        # GenGetSoundFlags
        #_logger.info("CALL 0x108B: - GenGetSoundFlags")
        
        # Bit 15: set=disable all sound
        stack.push(0, 0)
    elif args[-1] == 0x108B:
        #_logger.debug("CALL 0x108B: - GenSetSoundFlags")
        
        #_logger.debug(f"GenSetSoundFlags -> {args[-2]}")
        stack.push(0, 0)
    elif args[-1] == 0x138E:
        #_logger.debug("CALL 0x138E: - HwReadLcdContrast")
        stack.push(0, 8) # 50%
    elif args[-1] == 0x198D and args[-2] == 100:
        #_logger.debug("CALL 0x198d, 100: - Send App to foreground - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x198D and args[-2] == 0:
        #_logger.debug("CALL 0x198d, 100: - Send App to background - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x138B:
        #_logger.debug("CALL 0x138b: - Unmark App as Active - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x1E86:
        #_logger.debug("CALL 0x1E86: - Async playback of WVE - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x1F86:
        #_logger.debug("CALL 0x1F86: - Sync playback of WVE - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x2186:
        #_logger.debug("CALL 0x2186: - Async record of WVE - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x2386:
        #_logger.debug("CALL 0x2386: - Cancel record of WVE - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x2286:
        #_logger.debug("CALL 0x2286: - Sync record of WVE - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x2086:
        #_logger.debug("CALL 0x2086: - Cancel playback of WVE - Not Implemented")
        stack.push(0, 0)
    elif args[-1] == 0x5F8D:
        # gSetOpenAddress
        bx=args[-2] # 0=cancel, 1=direct, 2=indirect long, 3=indirect word
        cx=args[-3] # file offset low  word ??? it's declared as ULONG 
        dx=args[-4] # file offset high word ??? it's declared as ULONG
        
        #_logger.debug(f"CALL 0x5F8D: - gSetOpenAddress({bx}, {cx}, {dx})")
        procedure.executable.window_manager.gSetOpenAddress(bx, cx, dx)
         
        stack.push(0, 0)
    elif args[-1] == 0x288E:
        # Fn $8E Sub $28: HwGetScanCodes
        addr = args[-2]
        #_logger.debug(f"CALL 0x288E, {addr}: - HwGetScanCodes - Keyboard Scan")

        buffer = [0] * 10
        # Instead of looking at the last key press (key down event), see which keys are currently down state
        keys=pygame.key.get_pressed()
        for key_down in HwGetScanCodes:
            if keys[key_down]:
                # Key is currently pressed
                last_key_scan_loc = HwGetScanCodes.get(key_down, None)
                if last_key_scan_loc:
                    buffer[last_key_scan_loc[0]-1] = buffer[last_key_scan_loc[0]-1] or last_key_scan_loc[1]

        # Store in memory
        data_stack.memory[addr:addr+len(buffer)] = buffer
        stack.push(0, addr)
    else:
        # Fall back to attempting to calculate Call ID
        if args[-1] > 256:
            op = int(args[-1] / 256)
            fn = args[-1] - 256 * op
        else:
            fn = args[-1]
            op = 0

        # Emulate results
        if fn == 0x80:
            # Free Memory in bytes / 16
            # Return 256kb free

            print(" - Emulating ax=0x80 OS CALL: Free Memory")

            stack.push(0, 16384)
        elif fn == 0x88:
            if op == 0x00:
                # ID for the current process
                stack.push(0, 1024)
        elif fn == 0x8B and op == 0x12:
            # GenMarkActive
            print(" - GenMarkActive - Not Implemented")
            stack.push(0, 0)
        elif fn == 0x8B and op == 0x13:
            # GenMarkNonActive
            print(" - GenMarkNonActive - Not Implemented")
            stack.push(0, 0)
        elif fn == 0x8D:
            # Window Server
            if op == 0x5F:
                # gSetOpenAddress
                pass
            input()
            stack.push(0, 0)
        else:
            print(' - Unknown System CALL ')
            input()
            stack.push(0, 0)
