import os
import json
import sys
import struct
import datetime
import math
import pygame
from typing import Optional
from pygame.locals import *
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)


class DebuggerProfiler:

    def __init__(self) -> None:
        self.profiling_sections = {
            0x00: {}, 
            0x57: {},
            0xED: {},
            0xFF: {}
        }
    
    def store_timing(
        self,
        timing: float,
        opcode: int,
        opcode_subsection: Optional[int]
    ) -> None:
    
        self.profiling_sections[0x00 if not opcode_subsection else opcode_subsection].setdefault(opcode, []).append(timing)

    def dump_timings(
        self
    ) -> None: 
        
        for section in self.profiling_sections:
            for opcode in self.profiling_sections[section]:
                total_time = sum(self.profiling_sections[section][opcode])
                samples = len(self.profiling_sections[section][opcode])
                _logger.critical(f"{hex(section).upper()}, {hex(opcode).upper()}, {samples}, {total_time:.6f}, {total_time / samples:.6f}")

    


