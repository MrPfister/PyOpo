
import struct
import json
import os
import time
import datetime
import pygame
from pygame.locals import *
from .opcodes import *

import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG) 

# OPL32 Error Constants - Formatting consistent with OPL32 manual not Python

KErrInvalidArgs = -2
KErrOutOfRange = -7

opl_error_code_descriptions = {
    -1: "General failure",
    -2: "Invalid arguments",
    -3: "O/S error",
    -4: "Service not supported",
    -5: "Underflow (number too small)",
    -6: "Overflow (number too large)",
    -7: "Out of range",
    -8: "Divide by zero",
    -9: "In use (e.g. serial port being used by another program)",
    -10: "No system memory",
    -11: "Segment table full",
    -12: "Semaphore table full",
    -13: "Process table full/Too many processes",
    -14: "Resource already open",
    -15: "Resource not open",
    -16: "Invalid image/device file",
    -17: "No receiver",
    -18: "Device table full",
    -19: "File system not found (e.g. if you unplug cable to PC)",
    -20: "Failed to start",
    -21: "Font not loaded",

    -22: "Too wide (dialogs)",
    -23: "Too many items (dialogs)",
    -24: "Batteries too low for digital audio",
    -25: "Batteries too low to write to Flash",

    -32: "File already exists",
    -33: "File does not exist",
    -34: "Write failed",
    -35: "Read failed",
    -36: "End of file (when you try to read past end of file)",
    -37: "Disk full",
    -38: "Invalid name",
    -39: "Access denied (e.g. to a protected file on PC)",
    -40: "File or device in use",
    -41: "Device does not exist",
    -42: "Directory does not exist",
    -43: "Record too large",
    -44: "Read only file",
    -45: "Invalid I/O request",
    -46: "I/O operation pending",
    -47: "Invalid volume (corrupt disk)",
    -48: "I/O cancelled",
    -50: "Disconnected",
    -51: "Connected",
    -52: "Too many retries",
    -53: "Line failure",
    -54: "Inactivity timeout",
    -55: "Incorrect parity",
    -56: "Serial frame (usually because Baud setting is wrong)",
    -57: "Serial overrun (usually because Handshaking is wrong)",
    -58: "Cannot connect to remote modem",
    -59: "Remote modem busy",
    -60: "No answer from remote modem",

    -61: "Number is black listed (you may try a number only a certain number of times; wait a while and try again)",
    -62: "Not ready",
    -63: "Unknown media (corrupt SSD)",
    -64: "Root directory full (on any device, the root directory has a maximum amount of memory allocated to it)",
    -65: "Write protected",
    -66: "File is corrupt (Media is corrupt on Series 3c)",
    -67: "User abandoned",
    -68: "Erase pack failure",
    -69: "Wrong file type",

    -70: "Missing quotation",
    -71: "String too long",
    -72: "Unexpected name",
    -73: "Name too long",
    -74: "Logical device must be A-Z (A-D on Series 5)",
    -75: "Bad field name",
    -76: "Bad number",
    -77: "Syntax error",
    -78: "Illegal character",
    -79: "Function argument error",
    -80: "Type mismatch",
    -81: "Missing label",
    -82: "Duplicate name",
    -83: "Declaration error",
    -84: "Bad array size",
    -85: "Structure fault",
    -86: "Missing endp",
    -87: "Syntax Error",
    -88: "Mismatched ( or )",
    -89: "Bad field list",
    -90: "Too complex",
    -91: "Missing ,",

    -92: "Variables too large",
    -93: "Bad assignment",
    -94: "Bad array index",
    -95: "Inconsistent procedure arguments",

    -96: "Illegal Opcode (corrupt module translate again)",
    -97: "Wrong number of arguments (to a function or parameters to a procedure)",
    -98: "Undefined externals (a variable has been encountered which hasn’t been declared)",
    -99: "Procedure not found",
    -100: "Field not found",
    -101: "File already open",
    -102: "File not open",
    -103: "Record too big (data file contains record too big for OPL)",
    -104: "Module already loaded (when trying to LOADM)",
    -105: "Maximum modules loaded (when trying to LOADM)",
    -106: "Module does not exist (when trying to LOADM)",
    -107: "Incompatible translator version (OPL file needs retranslation)",
    -108: "Module not loaded (when trying to UNLOADM)",
    -109: "Bad file type (data file header wrong or corrupt)",
    -110: "Type violation (passing wrong type to parameter)",
    -111: "Subscript or dimension error (out of range in array)",
    -112: "String too long",
    -113: "Device already open (when trying to LOPEN)",
    -114: "Escape key pressed",
    -115: "Incompatible runtime version",
    -116: "ODB file(s) not closed",
    -117: "Maximum drawables open (maximum 8 windows and/or bitmaps allowed)",
    -118: "Drawable not open",
    -119: "Invalid Window (window operation attempted on a bitmap)",
    -120: "Screen access denied (when run from Calculator)",

    -121: "OPX not found",
    -122: "Incompatible OPX version",
    -123: "OPX procedure not found",
    -124: "STOP used in callback from OPX",
    -125: "Incompatible update mode",
    -126: "In database transaction or started changing fields"
}