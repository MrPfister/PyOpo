import os
import json
import sys
import struct
import datetime
import math
import pygame
from pygame.locals import *
import logging
import logging.config
from functools import lru_cache, cache

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)

OPO_WINDOW_SCALE = 2


class DebuggerDSF:
    def __init__(self, executable, width=480, height=160, dsf_size=64 * 1024) -> None:
        self.variables = {}
        self.blocks = {}

        self.width = width
        self.height = height
        self.stack_size = dsf_size

        self.executable = executable

        self.debug_surface = pygame.Surface((self.width, self.height))
        self.debug_surface.fill((255, 255, 255, 255))

        self.type_names = ["Int16", "Int32", "Float", "QStr", "Addr"]

        self.default_font = None

        self.composite_required = True

    def store_var(
        self, type, dsf_offset, procedure, value, size, global_var=False, array=False
    ):
        if type < 0 or type > 4:
            # _logger.warning(f"Attempting to store invalid variable type {type} - {value}")
            input()

        self.variables[dsf_offset] = {
            "type": type,
            "procedure": self.executable.get_proc_name(),
            "value": value,
            "global_var": global_var,
            "array": array,
            "size": size,
        }

        self.composite_required = True

    def store_alloc_block(self, start_offset, end_offset):
        pass

        self.composite_required = True

    def free_alloc_block(self, start_offset, end_offset):
        pass

        self.composite_required = True

    def free_proc_vars(self, start_offset, end_offset):
        # Perform garbage collection
        new_variable_dict = {}
        for var in self.variables:
            if var < start_offset or var > end_offset:
                new_variable_dict[var] = self.variables[var]

        self.variables = new_variable_dict

        self.composite_required = True

    def composite(self):
        DSF_VISUALISATION_BOX_WIDTH = 300

        if self.composite_required:
            # Render the frame a new
            self.debug_surface.fill((255, 255, 255, 255))

            # Draw box for DSF layout visualisation
            pygame.draw.rect(
                self.debug_surface,
                (0, 0, 0, 0),
                (5, 10, DSF_VISUALISATION_BOX_WIDTH, self.height - 15),
                1,
            )

            if self.default_font is None:
                self.default_font = pygame.font.Font(pygame.font.get_default_font(), 7)

            for block in self.blocks:
                pass

            bytes_per_row = int(self.stack_size / self.height - 17)

            for var in self.variables:
                var_y = int(var / bytes_per_row)
                var_x = 6 + int(
                    (DSF_VISUALISATION_BOX_WIDTH - 2)
                    / bytes_per_row
                    * int(var - var_y * bytes_per_row)
                )
                end_x = 6 + int(
                    (DSF_VISUALISATION_BOX_WIDTH - 2)
                    / bytes_per_row
                    * int(var + self.variables[var]["size"] - var_y * bytes_per_row)
                )
                var_y += 11  # Add border inset

                if end_x > 3 + DSF_VISUALISATION_BOX_WIDTH:
                    diff_x = end_x - 3 + DSF_VISUALISATION_BOX_WIDTH
                    end_x = 3 + DSF_VISUALISATION_BOX_WIDTH

                line_col = min(max(64 * self.variables[var]["type"], 0), 255)

                pygame.draw.line(
                    self.debug_surface,
                    (line_col, line_col, line_col, 0),
                    (var_x, var_y),
                    (end_x, var_y),
                    1,
                )

            font_surface = self.default_font.render(
                "Data Stack Frame Debugger:", True, (0, 0, 0, 255)
            )

            self.debug_surface.blit(font_surface, (5, 9 - font_surface.get_height()))

            pygame.draw.line(
                self.debug_surface,
                (0, 0, 0, 0),
                (DSF_VISUALISATION_BOX_WIDTH + 10, 10),
                (self.width - 5, 10),
                1,
            )

            font_surface = self.get_text_surface("Procedure DSF variables:")
            self.debug_surface.blit(
                font_surface,
                (DSF_VISUALISATION_BOX_WIDTH + 10, 9 - font_surface.get_height()),
            )

            var_counter = 0

            for var in self.variables:
                var_obj = self.variables[var]
                if var_obj["procedure"] is not self.executable.get_proc_name():
                    continue

                font_surface = self.default_font.render(
                    var_obj["procedure"], True, (0, 0, 0, 255)
                )
                self.debug_surface.blit(
                    font_surface,
                    (
                        DSF_VISUALISATION_BOX_WIDTH + 10,
                        19 - font_surface.get_height() + 8 * var_counter,
                    ),
                )

                font_surface = self.get_text_surface(self.type_names[var_obj["type"]])
                self.debug_surface.blit(
                    font_surface,
                    (
                        DSF_VISUALISATION_BOX_WIDTH + 45,
                        19 - font_surface.get_height() + 8 * var_counter,
                    ),
                )

                is_global = self.is_global_var(var, var_obj["procedure"])
                font_surface = self.get_text_surface(
                    f"Gbl - {self.global_var_name(var, var_obj['procedure'])}"
                    if is_global
                    else "Local"
                )
                self.debug_surface.blit(
                    font_surface,
                    (
                        DSF_VISUALISATION_BOX_WIDTH + 70,
                        19 - font_surface.get_height() + 8 * var_counter,
                    ),
                )

                # The value needs to be sanitised in case a null char is present.
                font_surface = self.get_text_surface(str(var_obj["value"]))
                self.debug_surface.blit(
                    font_surface,
                    (
                        DSF_VISUALISATION_BOX_WIDTH + 115,
                        19 - font_surface.get_height() + 8 * var_counter,
                    ),
                )

                var_counter += 1

            self.composite_required = False

        return self.debug_surface

    @lru_cache(maxsize=1024)
    def get_text_surface(self, text: str) -> pygame.Surface:
        sanitised = text.replace("\0", "")
        return self.default_font.render(sanitised, True, (0, 0, 0, 255))

    def is_global_var(self, dsf_offset: int, proc_name: str) -> bool:
        """Returns True if the specified DSF offset is the start location for a global variable within the specified procedure"""

        proc = self.executable.get_top_proc_instance_for_name(proc_name)

        for gd in proc.procedure["global_declarations"]:
            if dsf_offset == gd["data_stack_frame_offset"]:
                return True

        return False

    def global_var_name(self, dsf_offset: int, proc_name: str) -> str | None:
        proc = self.executable.get_top_proc_instance_for_name(proc_name)

        for gd in proc.procedure["global_declarations"]:
            if dsf_offset == gd["data_stack_frame_offset"]:
                return gd["name"]

        return False
