import struct
import datetime
import math
import logging
import logging.config
from pyopo.opl_exceptions import *
from typing import Optional

from functools import lru_cache

import pygame
from pygame.locals import *

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)

OPO_WINDOW_SCALE = 2  # Scaling for HiDPI screens


class text_screen:
    def __init__(self, max_width: int, max_height: int, window_surface):
        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 8)

        self.char_width = self.default_font.size("X")[0]
        self.char_height = self.default_font.size("X")[1]

        self.width_chars = int(max_width / self.char_width)
        self.height_chars = int(max_height / self.char_height)

        self.max_height = max_height
        self.max_width = max_width

        self.width = self.width_chars * self.char_width
        self.height = self.height_chars * self.char_height

        self.char_grid = [self.width_chars, self.height_chars]
        self.at_x = 1
        self.at_y = 1

        self.style = 0

        # The surface of graphics window 1 (default window)
        self.window_surface = window_surface

        # Where in the parent graphics window will the text window be rendered
        self.win_x = 0
        self.win_y = 0

    def AT(self, x: int, y: int) -> None:
        self.at_x = x
        self.at_y = y

    def STYLE(self, style: int) -> None:
        self.style = style

    def CLS(self) -> None:
        self.char_grid = [self.width_chars, self.height_chars]
        self.window_surface.fill(
            (255, 255, 255), (self.win_x, self.win_y, self.width, self.height)
        )


class DrawableSprite:
    _sprites = []
    _current_sprite = None

    draw_sprite = False

    def __init__(self, ID: int):
        self.ID = ID
        self.idx = 0
        self.start_time_tenths = None
        self.timespan_tenths = 0
        self.xpos = 0
        self.ypos = 0
        self.bitmap_sets = []

    @staticmethod
    def create_sprite() -> int:
        sprite_id = len(DrawableSprite._sprites)

        # SIBO16 OPL only supports a single sprite
        DrawableSprite._sprites = []

        DrawableSprite._sprites.append(DrawableSprite(sprite_id))

        DrawableSprite._current_sprite = len(DrawableSprite._sprites) - 1

        return sprite_id

    @staticmethod
    def append_sprite(tenths: int, spritelist: list[str], dx: int, dy: int) -> None:
        if not DrawableSprite._sprites:
            raise ("No Sprite defined")

        sprite = DrawableSprite._sprites[DrawableSprite._current_sprite]

        bitmap_set = {
            "dx": dx,
            "dy": dy,
            "tenths": tenths,
            "tenths_delta": 0
            if len(sprite.bitmap_sets) == 0
            else sprite.bitmap_sets[-1]["tenths_delta"] + tenths,
            "bitmaps": [],
        }

        for sprite_file in spritelist:
            if len(sprite_file) == 0:
                bitmap_set["bitmaps"].append(None)
            else:
                pic_binary = None
                with open(sprite_file, "rb") as f:
                    pic_binary = f.read()

                bitmap_surface = WindowManager.create_surface_from_bitmap_binary(
                    pic_binary, 0
                )
                bitmap_set["bitmaps"].append(bitmap_surface)

                _logger.info(
                    f"Loaded Sprite: {bitmap_surface.get_width()}, {bitmap_surface.get_height()}"
                )

        sprite.bitmap_sets.append(bitmap_set)
        sprite.timespan_tenths += tenths

    def _load_sprite(self, file):
        pass


class Window:
    GFONTS = None

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        visible,
        flags: int,
        ID: int,
        read_only=False,
        drawable=False,
    ) -> None:
        self.ID = ID

        self.gATx = 0
        self.gATy = 0

        # Location of the screen
        self.gPOSx = x
        self.gPOSy = y

        self.width = width
        self.height = height

        self.grey_plane_surface = pygame.Surface((self.width, self.height))
        self.grey_plane_surface.fill((255, 255, 255, 255))

        self.black_plane_surface = pygame.Surface((self.width, self.height))
        self.black_plane_surface.fill((255, 255, 255, 255))

        self.visible = visible

        self.init_GFONTS()
        self.current_gFONT: pygame.font.Font = Window.GFONTS[11]["Font"]

        self.gGREY_mode = 0
        self.gGMODE_mode = 0
        self.gTMODE_mode = 0

        self.is_drawable = drawable
        self.is_read_only = read_only

        # Even with gUPDATE OFF, some commands require forced updates (those that update state or return a value)
        self.update_required = False

        """
        i%(1) lowest character code
        i%(2) highest character code
        i%(3) height of font
        i%(4) descent of font
        i%(5) ascent of font
        i%(6) width of ‘0’ character
        i%(7) maximum character width
        i%(8) flags for font (see below)
        i%(9-17) name of font
        i%(18) current graphics mode (gGMODE)
        i%(19) current text mode (gTMODE)
        i%(20) current style (gSTYLE)
        i%(21) cursor state (ON=1,OFF=0)
        i%(22) ID of window containing cursor (-1 for text cursor)
        i%(23) cursor width
        i%(24) cursor height
        i%(25) cursor ascent
        i%(26) cursor x position in window
        i%(27) cursor y position in window
        i%(28) 1 if drawable is a bitmap
        i%(29) cursor effects
        i%(30) gGREY setting
        OPL
        ALPHABETIC LISTING 71
        i%(31) reserved (window server ID of drawable)
        i%(32) reserved
        """

    def init_GFONTS(self) -> None:
        """The PSION system fonts can only be stored once the pygame environment is initialised"""
        if Window.GFONTS:
            return

        Window.GFONTS = {
            1: {
                "Name": "Series 3 normal",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 8),
            },
            2: {
                "Name": "Series 3 bold",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 8),
            },
            3: {
                "Name": "Series 3 digits",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 6),
            },
            4: {
                "Name": "Mono",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 8),
            },
            5: {
                "Name": "Roman",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 8),
            },
            6: {
                "Name": "Roman",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 11),
            },
            7: {
                "Name": "Roman",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 13),
            },
            8: {
                "Name": "Roman",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 16),
            },
            9: {
                "Name": "Swiss",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 8),
            },
            10: {
                "Name": "Swiss",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 11),
            },
            11: {
                "Name": "Swiss",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 13),
            },
            12: {
                "Name": "Swiss",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 16),
            },
            13: {
                "Name": "Mono",
                "Font": pygame.font.Font(pygame.font.get_default_font(), 17),
            },
        }

    def gAT(self, x: int, y: int) -> None:
        self.gATx = x
        self.gATy = y

    def gMOVE(self, x: int, y: int) -> None:
        self.gATx += x
        self.gATy += y

    def gCLS(self) -> None:
        if self.gGREY_mode != 1:
            self.black_plane_surface.fill((255, 255, 255, 255))

        if self.gGREY_mode >= 1:
            self.grey_plane_surface.fill((255, 255, 255, 255))

    def gIDENTITY(self) -> int:
        return self.ID

    def gSAVEBIT(
        self, name: str, width: Optional[int] = None, height: Optional[int] = None
    ) -> None:
        if "." not in name:
            # If an extension is not given, .PIC is added automatically
            name += ".PIC"

        # If width & height are passed, save from the current cursor position

        _logger.info(f"gSAVEBIT - Filename: '{name}'")

        f = open(name, "wb")
        f.write("PIC".encode("ASCII"))
        f.write(struct.pack("<B", 0xDC))  # Magic Number
        f.write(struct.pack("<B", 0x30))  # Format version number. Always 0x30
        f.write(struct.pack("<B", 0x30))  # OPL runtime version number. Always 0x30

        f.write(struct.pack("<H", 2))  # Black + Grey Plane

        img_width = width if width else self.width
        img_height = height if height else self.height

        # Each row is rounded up to an even number of bytes
        data_size = math.ceil(img_width / 8)
        if data_size % 2 == 1:
            # Make even
            data_size += 1

        bytepacked_width = data_size
        data_size *= img_height

        _logger.debug(f"Width: {img_width}, Height = {img_height}")
        _logger.debug(f"Data Size: {data_size}, Byte Width = {bytepacked_width}")

        # Write out image header (Image 1 - Black Plane)
        f.write(struct.pack("<H", 0))  # CRC of iamge data - Currently ignored
        f.write(struct.pack("<H", img_width))
        f.write(struct.pack("<H", img_height))
        f.write(struct.pack("<H", data_size))
        f.write(
            struct.pack("<L", 12)
        )  # Relative offset to image data (after next record)

        # Write out image header (Image 2 - Grey Plane)
        f.write(struct.pack("<H", 0))  # CRC of iamge data - Currently ignored
        f.write(struct.pack("<H", img_width))
        f.write(struct.pack("<H", img_height))
        f.write(struct.pack("<H", data_size))
        f.write(struct.pack("<L", data_size))  # Offset to image data (after img 1 data)

        # Write out image data
        x_off = self.gATx if width else 0
        y_off = self.gATy if height else 0

        bytestr = ""
        imgs_to_write = [self.black_plane_surface, self.grey_plane_surface]

        byte_pack_struct = struct.Struct("<B")
        for surf in imgs_to_write:
            for y in range(img_height):
                for x in range(bytepacked_width * 8):
                    # Sanitise ranges
                    if y_off + y >= 0 and y_off + y < self.height:
                        if x_off + x >= 0 and x_off + x < self.width:
                            col = surf.get_at((x_off + x, y_off + y))
                        else:
                            col = (255, 255, 255, 0)
                    else:
                        col = (255, 255, 255, 0)

                    # 0 if filled, 1 otherwise
                    pixel_val = 0 if col[0] == 0 else 1

                    bytestr += str(pixel_val)
                    if len(bytestr) == 8:
                        # Complete byte, write out
                        f.write(byte_pack_struct.pack(int(bytestr, 2)))
                        bytestr = ""

        f.close()

    def gLINETO(self, x: int, y: int) -> None:
        self.draw_line((self.gATx, self.gATy), (x, y))

        # gLINETO moves the cursor to the end point
        self.gATx = x
        self.gATy = y

    def gPOLY(self, x: int, y: int, ops: list[tuple[int, int]]) -> None:
        cur_x = x
        cur_y = y

        for operation in ops:
            dx, dy = operation

            if dx % 2 == 1:
                # Odd: Move comman
                cur_x += int((dx - 1) / 2)
                cur_y += dy
            else:
                # Evwn: Draw command
                self.draw_line((cur_x, cur_y), (cur_x + int(dx / 2), cur_y + dy))

                cur_x += int(dx / 2)
                cur_y += dy

    def gLINEBY(self, dx: int, dy: int) -> None:
        self.draw_line((self.gATx, self.gATy), (self.gATx + dx, self.gATy + dy))

        # gLINEBY moves the cursor by the delta
        self.gATx += dx
        self.gATy += dy

    def draw_line(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        # Helper method to handle line drawing

        s_x, s_y = start
        e_x, e_y = end

        # On the S3, gLINETO does not draw the final pixel.
        # Its easier to store/replace the final pixel rather than doing lots of trig

        end_in_bounds = (e_x < self.black_plane_surface.get_width()) and (
            e_y < self.black_plane_surface.get_height()
        )
        end_in_bounds = end_in_bounds and (e_x >= 0) and (e_y >= 0)

        if self.gGREY_mode != 1:
            if end_in_bounds:
                end_col = self.black_plane_surface.get_at((e_x, e_y))

            if self.gGMODE_mode == 0:
                # Set Pixels
                pygame.draw.line(
                    self.black_plane_surface, (0, 0, 0, 0), (s_x, s_y), (e_x, e_y), 1
                )
            elif self.gGMODE_mode == 1:
                # Clear
                pygame.draw.line(
                    self.black_plane_surface,
                    (255, 255, 255, 255),
                    (s_x, s_y),
                    (e_x, e_y),
                    1,
                )
            elif self.gGMODE_mode == 2:
                # Invert
                # _logger.warning('Helper Drawline gGMODE = 2 not implemented')
                pass

            if end_in_bounds:
                self.black_plane_surface.set_at((e_x, e_y), end_col)

        if self.gGREY_mode > 0:
            if end_in_bounds:
                end_col = self.grey_plane_surface.get_at((e_x, e_y))

            if self.gGMODE_mode == 0:
                # Set Pixels
                pygame.draw.line(
                    self.grey_plane_surface,
                    (128, 128, 128, 0),
                    (s_x, s_y),
                    (e_x, e_y),
                    1,
                )
            elif self.gGMODE_mode == 1:
                # Clear
                pygame.draw.line(
                    self.grey_plane_surface,
                    (255, 255, 255, 255),
                    (s_x, s_y),
                    (e_x, e_y),
                    1,
                )
            elif self.gGMODE_mode == 2:
                # Invert
                # _logger.warning('Helper Drawline gGMODE = 2 not implemented')
                pass

            if end_in_bounds:
                self.grey_plane_surface.set_at((e_x, e_y), end_col)

    def gTWIDTH(self, text: str) -> int:
        self.update_required = True
        return self.current_gFONT.size(text)[0]

    def gWIDTH(self) -> int:
        return self.width

    def gHEIGHT(self) -> int:
        return self.height

    def gGMODE(self, mode: int) -> None:
        self.gGMODE_mode = mode
        _logger.debug(f"gGMODE = {mode}")

    def gTMODE(self, mode: int) -> None:
        self.gTMODE_mode = mode
        _logger.debug(f"gTMODE = {mode}")

    def gVISIBLE(self, mode: int) -> None:
        self.visible = mode
        self.update_required = True

    def gSETWIN(self, x: int, y: int, width: int, height: int) -> None:
        self.gPOSx = x
        self.gPOSy = y

        if width:
            self.width = width
            self.height = height

        self.update_required = True

    def gSCROLL(
        self, dx: int, dy: int, xpos: int, ypos: int, width: int, height: int
    ) -> None:
        if not width:
            width = self.width
            height = self.height
            xpos = 0
            ypos = 0

        # Rect was passed through
        tmp_grey = pygame.Surface((width, height))
        tmp_black = pygame.Surface((width, height))

        # Copy
        tmp_grey.blit(
            self.grey_plane_surface, (0, 0, width, height), (xpos, ypos, width, height)
        )
        tmp_black.blit(
            self.black_plane_surface, (0, 0, width, height), (xpos, ypos, width, height)
        )

        # Clear area being scrolled
        self.grey_plane_surface.fill((255, 255, 255, 255), (xpos, ypos, width, height))
        self.black_plane_surface.fill((255, 255, 255, 255), (xpos, ypos, width, height))

        # Copy to new location
        self.grey_plane_surface.blit(tmp_grey, (xpos + dx, ypos + dy, width, height))
        self.black_plane_surface.blit(tmp_black, (xpos + dx, ypos + dy, width, height))

        self.update_required = True

    def gBORDER(
        self, flags: int, width: int | None = None, height: int | None = None
    ) -> None:
        border_x = self.gATx
        border_y = self.gATy

        if width is None:
            width = self.width
            height = self.height
            border_x = 0
            border_y = 0
        else:
            # If width / height are given, the border is drawn from the current x/y
            border_x = self.gATx
            border_y = self.gATy

        col = (0, 0, 0, 0)
        thickness = 1

        if flags == 2:
            # removes a single pixel shadow (leaves a gap for single pixel shadow on Series 3c)
            col = (255, 255, 255, 255)
        elif flags == 3:
            # double pixel shadow
            thickness = 2
        elif flags == 4:
            # removes a double pixel shadow (leaves a gap for double pixel shadow on Series 3c)
            col = (255, 255, 255, 255)
            thickness = 2

        if self.gGREY_mode != 1:
            pygame.draw.rect(
                self.black_plane_surface,
                col,
                (border_x, border_y, width - thickness, height - thickness),
                thickness,
            )

        if self.gGREY_mode >= 1:
            if col[0] == 0:
                col = (128, 128, 128, 0)

            pygame.draw.rect(
                self.grey_plane_surface,
                col,
                (border_x, border_y, width - thickness, height - thickness),
                thickness,
            )

    def gXBORDER(
        self, type: int, flags: int, width: int | None = None, height: int | None = None
    ) -> None:
        # Just draw a simple border (gBORDER)
        self.gBORDER(flags, width, height)

    def gPRINT(self, text: str) -> None:
        sanitised = str(text).replace("\0", "")
        if len(sanitised) == 0:
            # No text to render, skip
            return

        if self.gTMODE_mode == 2:
            # Invert
            # _logger.warning('gPRINT gTMODE Invert! - STUB')
            pass

        # Subtract the height of the text; the y pos is the baseline
        if self.gGREY_mode > 0:
            # Grey plane
            font_surface = self.create_text_surface(
                sanitised,
                (255, 255, 255, 255) if self.gTMODE_mode == 1 else (128, 128, 128, 0),
            )

            if self.gTMODE_mode == 3:
                self.gFILL(font_surface.get_width(), font_surface.get_height(), 1)

            self.grey_plane_surface.blit(
                font_surface, (self.gATx, self.gATy - font_surface.get_height())
            )

        if self.gGREY_mode == 0 or self.gGREY_mode == 2:
            font_surface = self.create_text_surface(
                sanitised,
                (255, 255, 255, 255) if self.gTMODE_mode == 1 else (0, 0, 0, 0),
            )

            if self.gTMODE_mode == 3:
                self.gFILL(font_surface.get_width(), font_surface.get_height(), 1)

            self.black_plane_surface.blit(
                font_surface, (self.gATx, self.gATy - font_surface.get_height())
            )

        self.gATx += font_surface.get_width()

    @lru_cache(maxsize=1024)
    def create_text_surface(
        self, text: str, foreground: pygame.Color
    ) -> pygame.Surface:
        return self.current_gFONT.render(
            text,
            True,
            foreground,
        )

    def gPRINTB(
        self, text: str, width: int, align: int, top: int, bottom: int, margin: int
    ) -> None:
        sanitised = str(text).replace("\0", "")
        if len(sanitised) == 0:
            # No text to render, skip
            return

        # Subtract the height of the text; the y pos is the baseline
        if self.gGREY_mode > 0:
            # Grey plane
            font_surface = self.create_text_surface(
                sanitised,
                (128, 128, 128, 0),
            )

            surface_height = font_surface.get_height() + top + bottom
            surface_width = font_surface.get_width() + margin * 2

            self.grey_plane_surface.fill(
                (255, 255, 255, 255),
                (self.gATx, self.gATy - surface_height, width, surface_height),
            )
            self.grey_plane_surface.blit(
                font_surface,
                (self.gATx, self.gATy - bottom - font_surface.get_height()),
            )

        if self.gGREY_mode == 0 or self.gGREY_mode == 2:
            font_surface = self.create_text_surface(
                sanitised,
                (0, 0, 0, 0),
            )

            surface_height = font_surface.get_height() + top + bottom
            # surface_width = font_surface.get_width() + margin * 2

            self.black_plane_surface.fill(
                (255, 255, 255, 255),
                (self.gATx, self.gATy - surface_height, width, surface_height),
            )
            self.black_plane_surface.blit(
                font_surface,
                (self.gATx, self.gATy - bottom - font_surface.get_height()),
            )

        self.gATx += width

    def gBUTTON(self, text: str, ty, width: int, height: int, st) -> None:
        self.black_plane_surface.fill(
            (255, 255, 255, 255), (self.gATx, self.gATy, width, height)
        )
        self.grey_plane_surface.fill(
            (255, 255, 255, 255), (self.gATx, self.gATy, width, height)
        )

        pygame.draw.rect(
            self.black_plane_surface,
            (0, 0, 0, 0),
            (self.gATx, self.gATy, width, height),
            1,
        )
        self.grey_plane_surface.fill(
            (192, 192, 192, 0), (self.gATx + 3, self.gATy + 3, width - 6, height - 6)
        )

        pygame.draw.line(
            self.grey_plane_surface,
            (128, 128, 128, 0),
            (self.gATx + 1, self.gATy + height - 2),
            (self.gATx + width - 2, self.gATy + height - 2),
            1,
        )
        pygame.draw.line(
            self.grey_plane_surface,
            (128, 128, 128, 0),
            (self.gATx + 2, self.gATy + height - 3),
            (self.gATx + width - 3, self.gATy + height - 3),
            1,
        )

        pygame.draw.line(
            self.grey_plane_surface,
            (128, 128, 128, 0),
            (self.gATx + width - 2, self.gATy + 1),
            (self.gATx + width - 2, self.gATy + height - 2),
            1,
        )
        pygame.draw.line(
            self.grey_plane_surface,
            (128, 128, 128, 0),
            (self.gATx + width - 3, self.gATy + 2),
            (self.gATx + width - 3, self.gATy + height - 3),
            1,
        )

        text = text.replace("\00", "")
        if len(text) > 0:
            # Text for the button
            font_surface = self.create_text_surface(
                text,
                (0, 0, 0, 0),
            )

            # The text may need to be clipped to the button
            max_text_width = min(font_surface.get_width(), width)
            max_text_width = max(0, max_text_width)

            y_offset = max(0, (height - font_surface.get_height()) / 2)

            # Render the Text if its in bounds
            if max_text_width > 0:
                self.black_plane_surface.blit(
                    font_surface,
                    (self.gATx + width / 2 - max_text_width / 2, self.gATy + y_offset),
                )

    def gFONT(self, font_id: int) -> None:
        if font_id not in Window.GFONTS:
            raise (KErrOutOfRange)

        self.current_gFONT = Window.GFONTS[font_id]["Font"]

    def gGREY(self, mode: int) -> None:
        self.gGREY_mode = mode
        self.update_required = True

    def gINVERT(self, width: int, height: int) -> None:
        self.gFILL(width, height, 2)

        # gINVERT inverts the rectangle area apart from the 4 corner pixels

        self.invert_pixel(self.gATx, self.gATy)
        self.invert_pixel(self.gATx + width, self.gATy)
        self.invert_pixel(self.gATx, self.gATy + height)
        self.invert_pixel(self.gATx + width, self.gATy + height)

    def gX(self) -> int:
        return self.gATx

    def gY(self) -> int:
        return self.gATy

    def gORIGINX(self) -> int:
        return self.gPOSx

    def gORIGINY(self) -> int:
        return self.gPOSy

    def invert_pixel(self, x: int, y: int) -> None:
        if self.gATy + y >= self.black_plane_surface.get_height() or self.gATy + y < 0:
            return

        if self.gATx + x >= self.black_plane_surface.get_width() or self.gATx + x < 0:
            return

        if self.gGREY_mode > 0:
            # Grey plane
            col = self.grey_plane_surface.get_at((self.gATx + x, self.gATy + y))

            if col[0] == 255:
                col = (128, 128, 128, 0)
            else:
                col = (255, 255, 255, 255)

            self.grey_plane_surface.set_at((self.gATx + x, self.gATy + y), col)

        if self.gGREY_mode == 0 or self.gGREY_mode == 2:
            # Black Plane
            col = self.black_plane_surface.get_at((self.gATx + x, self.gATy + y))

            if col[0] == 0:
                col = (255, 255, 255, 255)
            else:
                col = (0, 0, 0, 0)

            self.black_plane_surface.set_at((self.gATx + x, self.gATy + y), col)

    def gFILL(self, width: int, height: int, mode: int) -> None:
        # 0 set
        # 1 cleared
        # 2 inverted

        if mode == 2:
            # Inverted requires more processing (per pixel)

            for y in range(height):
                if (
                    self.gATy + y >= self.black_plane_surface.get_height()
                    or self.gATy + y < 0
                ):
                    continue

                max_width = min(width, self.black_plane_surface.get_width() - self.gATx)
                for x in range(max_width):
                    if self.gATx + x < 0:
                        continue

                    if self.gGREY_mode > 0:
                        # Grey plane

                        col = self.grey_plane_surface.get_at(
                            (self.gATx + x, self.gATy + y)
                        )

                        if col[0] == 255:
                            col = (128, 128, 128, 0)
                        else:
                            col = (255, 255, 255, 255)

                        self.grey_plane_surface.set_at(
                            (self.gATx + x, self.gATy + y), col
                        )

                    if self.gGREY_mode == 0 or self.gGREY_mode == 2:
                        # Black Plane
                        col = self.black_plane_surface.get_at(
                            (self.gATx + x, self.gATy + y)
                        )

                        if col[0] == 0:
                            col = (255, 255, 255, 255)
                        else:
                            col = (0, 0, 0, 0)

                        self.black_plane_surface.set_at(
                            (self.gATx + x, self.gATy + y), col
                        )
        else:
            if self.gGREY_mode > 0:
                # Grey plane
                col = (128, 128, 128, 0) if mode == 0 else (255, 255, 255, 255)
                self.grey_plane_surface.fill(col, (self.gATx, self.gATy, width, height))

            if self.gGREY_mode == 0 or self.gGREY_mode == 2:
                col = (0, 0, 0, 0) if mode == 0 else (255, 255, 255, 255)
                self.black_plane_surface.fill(
                    col, (self.gATx, self.gATy, width, height)
                )

    def gBOX(self, width: int, height: int) -> None:
        if self.gGREY_mode > 0:
            # Grey plane
            pygame.draw.rect(
                self.black_plane_surface,
                (128, 128, 128, 0),
                (self.gATx, self.gATy, width, height),
                1,
            )

        if self.gGREY_mode == 0 or self.gGREY_mode == 2:
            # Black Plane
            pygame.draw.rect(
                self.black_plane_surface,
                (0, 0, 0, 0),
                (self.gATx, self.gATy, width, height),
                1,
            )

    def gINFO(self) -> list[int]:
        ginfo = [0] * 32

        """
        
        i%(1) lowest character code
        i%(2) highest character code
        i%(3) height of font
        i%(4) descent of font
        i%(5) ascent of font
        i%(6) width of ‘0’ character
        i%(7) maximum character width
        i%(8) flags for font (see below)
        i%(9-17) name of font
        i%(18) current graphics mode (gGMODE)
        i%(19) current text mode (gTMODE)
        i%(20) current style (gSTYLE)
        i%(21) cursor state (ON=1,OFF=0)
        i%(22) ID of window containing cursor (-1 for text cursor)
        i%(23) cursor width
        i%(24) cursor height
        i%(25) cursor ascent
        i%(26) cursor x position in window
        i%(27) cursor y position in window
        i%(28) 1 if drawable is a bitmap
        i%(29) cursor effects
        i%(30) gGREY setting
        ALPHABETIC LISTING 71
        i%(31) reserved (window server ID of drawable)
        i%(32) reserved
        
        """

        # All these indexes are offset -1 to the descriptor above
        ginfo[0] = 32  # Lowest Character Code
        ginfo[1] = 126  # Highest Character Code
        ginfo[2] = self.current_gFONT.size("0")[1]
        ginfo[3] = self.current_gFONT.get_descent()
        ginfo[4] = self.current_gFONT.get_ascent()
        ginfo[5] = self.current_gFONT.size("0")[0]  # width of ‘0’ character
        ginfo[6] = self.current_gFONT.size("W")[0]  # maximum character width

        ginfo[17] = self.gGMODE_mode

        ginfo[27] = 1 if self.is_drawable else 0
        ginfo[29] = self.gGREY_mode

        return ginfo


class WindowManager:
    def __init__(self, executable, width=480, height=160) -> None:
        self.width = width
        self.height = height

        self.executable = executable

        _logger.info("Initialising Display")
        self.init_sdl(width, height)

        self.default_font = pygame.font.SysFont("arial", 10)
        self.default_font_bold = pygame.font.SysFont("arial", 10, bold=True)

        pygame.display.set_caption(
            executable.header.source_filename.split("\\")[-1].replace("\0", "")
        )

        self.windows: list[Window] = []
        self.gupdate_enabled = True

        self.graphics_cursor = 0
        self._window_cursor: Window = None

        self.defaultwin_mode = 1

        self.giprint = None

        # Flags set by system calls
        self.open_address = None

        # Even with gUPDATE OFF, some commands require forced updates (those that update state or return a value)
        self.update_required = True

        self.gCREATE(0, 0, self.width, self.height, 1, 0)

        # The text window is a subset of the default graphics window
        self.text_window = text_screen(
            self.width, self.height, self.windows[0].black_plane_surface
        )

        self.last_render_time = datetime.datetime.now()

    def gCREATE(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        visible,
        flags: int,
        read_only=False,
        drawable=False,
    ) -> int:
        lowest_free = 1

        window_ids = list(map(lambda w: w.ID, self.windows))
        window_ids.sort()
        window_ids = set(window_ids)

        b = list(range(1, 9))
        lowest_free = list(window_ids ^ set(b))[0]

        _logger.info(f"Created new Graphics Window at ID {lowest_free}")

        # Add to the top (highest gRANK) of the window stack
        self.windows.append(
            Window(
                x=x,
                y=y,
                width=width,
                height=height,
                visible=visible,
                flags=flags,
                ID=lowest_free,
                read_only=read_only,
                drawable=drawable,
            )
        )

        self.graphics_cursor = len(self.windows) - 1
        self._window_cursor = self.windows[self.graphics_cursor]

        self.update_required = True

        return lowest_free

    def gLOADBIT(self, name: str, write: int, index: int) -> int:
        # write = 0: Read Only access, write = 1: Write access

        pic_binary = None
        with open(name, "rb") as f:
            pic_binary = f.read()

        return self.gLOADBIT_binary(pic_binary, write, index)

    def gLOADBIT_binary(self, pic_binary: bytes, write: int, index: int) -> int:
        bitmap_surface = WindowManager.create_surface_from_bitmap_binary(
            pic_binary, index
        )

        # Create the base graphics surface
        id = self.gCREATE(
            0,
            0,
            bitmap_surface.get_width(),
            bitmap_surface.get_height(),
            False,
            0,
            True if write == 1 else False,
            True,
        )

        # Set the newly created Windows bitmap to the graphic just loaded
        self.windows[-1].black_plane_surface.blit(bitmap_surface, (0, 0))

        self.update_required = True

        return id

    @staticmethod
    def create_surface_from_bitmap_binary(bytes, index: int):
        if bytes[0:3].decode("utf-8", "replace") != "PIC":
            raise ("Invalid Image")

        # Offset 3: 0xDC

        bmp_count = struct.unpack_from("<H", bytes, 6)[0]

        if index < 0 or index >= bmp_count:
            raise ("Invalid Bitmap Index Selected")

        bmp_offset = 8 + index * 12  # Offset of the 1st bitmap data

        # int16 offset 0 is CRC
        width, height = struct.unpack_from("<HH", bytes, bmp_offset + 2)

        # height = struct.unpack_from("<H", bytes, bmp_offset + 4)[0]
        # byte_len = struct.unpack_from("<H", bytes, bmp_offset + 6)[0]
        data_offset = (
            bmp_offset + 12 + struct.unpack_from("<L", bytes, bmp_offset + 8)[0]
        )

        _logger.debug("Creating surface from binary stream")
        _logger.debug(f" - Width: {width}")
        _logger.debug(f" - Height: {height}")
        _logger.debug(f" - Data Offset: {data_offset}")

        bitmap_surface = pygame.Surface((width, height))
        bitmap_surface.fill((255, 255, 255, 255))

        # The number of bytes devisible by 8 pixels
        byte_width = math.ceil(width / 8)

        if byte_width % 2 == 1:
            # The byte width is rounded up to an even number
            byte_width += 1

        _logger.debug(f"Byte Width: {byte_width}")

        bmp_d_off = data_offset
        for h in range(height):
            for w in range(byte_width):
                byte_pixels = bytes[bmp_d_off + w]

                # The byte represents 8 pixels on screen
                bits = [int(i) for i in "{0:08b}".format(byte_pixels)]

                for p in range(8):
                    if w * 8 + 8 - p < width and bits[p] == 1:
                        # Set the pixel
                        bitmap_surface.set_at((w * 8 + 8 - p, h), (0, 0, 0, 0))

            bmp_d_off += byte_width

        return bitmap_surface

    def GIPRINT(self, prompt: str, c: int) -> None:
        self.giprint = {
            "start_ts": datetime.datetime.now(),
            "prompt": prompt,
            "location": c,
        }

    def gCLOSE(self, id: int) -> None:
        if id == 1:
            raise ("Can not close default window")

        if id == self.windows[self.graphics_cursor].ID:
            # Close Current window, ID 1 becomes primary
            self.windows.pop(self.graphics_cursor)
            self.gUSE(1)
            return

        index_to_pop = next(
            (i for i in range(len(self.windows)) if self.windows[i].ID == id), None
        )

        if not index_to_pop:
            raise ("Index not found")

        self.windows.pop(index_to_pop)

    def init_sdl(self, width: int, height: int) -> None:
        pygame.init()

        debugger_height = 0
        if self.executable.memory_debugger:
            # There is a memory debugger to visualise too
            debugger_height = height * OPO_WINDOW_SCALE

        size = (width * OPO_WINDOW_SCALE, height * OPO_WINDOW_SCALE + debugger_height)
        self.screen_render_surface = pygame.display.set_mode(size)

        # This is the buffer surface all others will blit onto
        self.screen_buffer = pygame.Surface((width, height))

    def composite(self, executable, force=False):
        windows_update_required = self.gupdate_enabled and next(
            (True for w in self.windows if w.update_required), False
        )

        if (
            windows_update_required
            or self.update_required
            or force
            or executable.dialog_manager
            or executable.menu_manager
            or DrawableSprite.draw_sprite
        ):
            # Clear flag from specific graphic operations
            self.update_required = False

            self.screen_buffer.fill((255, 255, 255, 255))

            # List order represents inverse gRANK
            for window in self.windows:
                # Clear flag from specific graphic operations
                window.update_required = False

                if window.visible != 1:
                    continue

                self.screen_buffer.blit(
                    window.black_plane_surface,
                    Rect(window.gPOSx, window.gPOSy, window.width, window.height),
                )

                if self.defaultwin_mode == 1:
                    # Use BLEND_MIN to ensure Black is rendered ontop of the grey plane
                    self.screen_buffer.blit(
                        window.grey_plane_surface,
                        Rect(window.gPOSx, window.gPOSy, window.width, window.height),
                        special_flags=pygame.BLEND_MIN,
                    )

            # Render any active sprite animation
            if DrawableSprite.draw_sprite:
                # There is a sprite to draw to the screen buffer
                self.composite_sprite(self.screen_buffer)

            if executable.dialog_manager and executable.dialog_manager.show:
                # Render an active dialog
                dialog_surface = executable.dialog_manager.composite(
                    self.width, self.height
                )

                # Take into account dPOSITION values
                if executable.dialog_manager.pos_x == -1:
                    # Left
                    pos_x = 0
                elif executable.dialog_manager.pos_x == 1:
                    # Right
                    # -2 to account for shadow depth
                    pos_x = self.width - dialog_surface.get_width() - 2
                else:
                    # Center (Default)
                    pos_x = self.width / 2 - dialog_surface.get_width() / 2

                if executable.dialog_manager.pos_y == -1:
                    # Top
                    pos_y = 0
                elif executable.dialog_manager.pos_x == 1:
                    # Right
                    # -2 to account for shadow depth
                    pos_y = self.height - dialog_surface.get_height() - 2
                else:
                    # Center (Default)
                    pos_y = self.height / 2 - dialog_surface.get_height() / 2

                self.screen_buffer.fill(
                    (128, 128, 128, 0),
                    Rect(
                        pos_x + 2,
                        pos_y + 2,
                        dialog_surface.get_width(),
                        dialog_surface.get_height(),
                    ),
                )
                self.screen_buffer.blit(
                    dialog_surface,
                    Rect(
                        pos_x,
                        pos_y,
                        dialog_surface.get_width(),
                        dialog_surface.get_height(),
                    ),
                )

            if executable.menu_manager and executable.menu_manager.show:
                # Render an active menu
                self.screen_buffer = executable.menu_manager.composite(
                    self.screen_buffer
                )

            # GIPRINT overlay
            if self.giprint:
                font_surface = self.create_text_surface(
                    self.giprint["prompt"],
                    (255, 255, 255, 255),
                )

                match self.giprint["location"]:
                    case 0:
                        # Top Left
                        self.screen_buffer.fill(
                            (0, 0, 0, 0),
                            Rect(
                                0,
                                self.height - font_surface.get_height() - 4,
                                font_surface.get_width() + 4,
                                font_surface.get_height() + 4,
                            ),
                        )
                        self.screen_buffer.blit(
                            font_surface,
                            (2, self.height - font_surface.get_height() - 2),
                        )
                    case 1:
                        # Bottom Left
                        self.screen_buffer.fill(
                            (0, 0, 0, 0),
                            Rect(
                                0,
                                0,
                                font_surface.get_width() + 4,
                                font_surface.get_height() + 4,
                            ),
                        )
                        self.screen_buffer.blit(font_surface, (2, 2))
                    case 2:
                        # Top Right
                        self.screen_buffer.fill(
                            (0, 0, 0, 0),
                            Rect(
                                self.width - font_surface.get_width() - 4,
                                self.height - font_surface.get_height() - 4,
                                font_surface.get_width() + 4,
                                font_surface.get_height() + 4,
                            ),
                        )
                        self.screen_buffer.blit(
                            font_surface,
                            (
                                self.width - font_surface.get_width() - 2,
                                self.height - font_surface.get_height() - 2,
                            ),
                        )
                    case 3:
                        # Bottom Right
                        self.screen_buffer.fill(
                            (0, 0, 0, 0),
                            Rect(
                                self.width - font_surface.get_width() - 4,
                                0,
                                font_surface.get_width() + 4,
                                font_surface.get_height() + 4,
                            ),
                        )
                        self.screen_buffer.blit(
                            font_surface, (self.width - font_surface.get_width() - 2, 2)
                        )

                if datetime.datetime.now() - self.giprint[
                    "start_ts"
                ] > datetime.timedelta(seconds=2):
                    # Close GIPRINT
                    self.giprint = None

        # Scale the screen
        scaled_surface = pygame.transform.scale(
            self.screen_buffer,
            (self.screen_render_surface.get_width(), self.height * OPO_WINDOW_SCALE),
        )

        # Blit onto the render surface
        self.screen_render_surface.blit(
            scaled_surface,
            (0, 0, self.screen_render_surface.get_width(), scaled_surface.get_height()),
        )

        if executable.memory_debugger:
            # Composite the debugger if required
            executable.memory_debugger.composite()

            # Render the memory debugger onto the graphics surface too
            scaled_surface = pygame.transform.scale(
                executable.memory_debugger.debug_surface,
                (
                    self.screen_render_surface.get_width(),
                    self.height * OPO_WINDOW_SCALE,
                ),
            )

            self.screen_render_surface.blit(
                scaled_surface,
                (
                    0,
                    self.height * OPO_WINDOW_SCALE,
                    self.screen_render_surface.get_width(),
                    scaled_surface.get_height(),
                ),
            )

        pygame.display.flip()

    def gUSE(self, id: int) -> None:
        for i in range(len(self.windows)):
            if self.windows[i].ID == id:
                self.graphics_cursor = i
                self._window_cursor = self.windows[self.graphics_cursor]
                break

        self.update_required = True

    def gRANK(self) -> int:
        self.update_required = True

        return len(self.windows) - self.graphics_cursor

    def gORDER(self, id: int, index: int) -> None:
        # Store the ID which is the gUSE value
        gUSE_ID = self.windows[self.graphics_cursor].ID

        for i in range(len(self.windows)):
            if self.windows[i].ID == id:
                win = self.windows.pop(i)

                # print(f' - Found gORDER ID% {id} at index {i}')
                # print(f' - Windows Open {len(self.windows)}')

                # Move window - Positions are reversed within the window list
                if index > len(self.windows):
                    # print('Adding Window to end of the stack')
                    self.windows.insert(0, win)
                    # print(len(self.windows))
                elif index == 1:
                    # print('Adding Window to start of the stack')
                    self.windows.append(win)
                else:
                    # print('Moving window within stack')
                    # IDs are 1+ so don't need to -1 from len
                    self.windows.insert(len(self.windows) - index, win)

                break

        self.update_required = True

        # Make sure the Current Drawable is still pointing to the correct ID if its been moved.
        self.gUSE(gUSE_ID)

    def gCOPY(self, id: int, x: int, y: int, w: int, h: int, mode: int) -> None:
        for i in range(len(self.windows)):
            if self.windows[i].ID == id:
                from_window = self.windows[i]
                to_window = self.windows[self.graphics_cursor]

                # print(f" - Performing gCOPY from ID {id} > Win {i} to Win {self.graphics_cursor}")

                if mode == 3:
                    # Optimise for replace operation
                    to_window.black_plane_surface.blit(
                        from_window.black_plane_surface,
                        (to_window.gATx, to_window.gATy, w, h),
                        (x, y, w, h),
                    )
                    to_window.grey_plane_surface.blit(
                        from_window.grey_plane_surface,
                        (to_window.gATx, to_window.gATy, w, h),
                        (x, y, w, h),
                    )
                else:
                    for y_copy in range(h):
                        for x_copy in range(w):
                            self.set_at_mode(
                                from_window.black_plane_surface,
                                to_window.black_plane_surface,
                                x + x_copy,
                                y + y_copy,
                                to_window.gATx + x_copy,
                                to_window.gATy + y_copy,
                                mode,
                                False,
                            )
                            self.set_at_mode(
                                from_window.grey_plane_surface,
                                to_window.grey_plane_surface,
                                x + x_copy,
                                y + y_copy,
                                to_window.gATx + x_copy,
                                to_window.gATy + y_copy,
                                mode,
                                True,
                            )
                break

        self.update_required = True

    def set_at_mode(
        self,
        src,
        dest,
        src_x: int,
        src_y: int,
        dest_x: int,
        dest_y: int,
        mode: int,
        grey: bool,
    ) -> None:
        # Validate coords are in bounds
        if src_x < 0 or src_x >= src.get_width():
            return
        elif src_y < 0 or src_y >= src.get_height():
            return
        elif dest_x < 0 or dest_x >= dest.get_width():
            return
        elif dest_y < 0 or dest_y >= dest.get_height():
            return

        src_pixel = src.get_at((src_x, src_y))

        if src_pixel[0] == 0:
            # Modes 0, 1, 2 only operate when the source pixel is set
            if mode == 0:
                # Set
                if grey:
                    dest.set_at((dest_x, dest_y), (128, 128, 128, 0))
                else:
                    dest.set_at((dest_x, dest_y), (0, 0, 0, 0))
            elif mode == 1:
                # Clear
                dest.set_at((dest_x, dest_y), (255, 255, 255, 255))
            elif mode == 2:
                # Invert
                dst_pixel = dest.get_at((dest_x, dest_y))

                if dst_pixel[0] != 255:
                    dst_pixel = (255, 255, 255, 255)
                else:
                    if grey:
                        dst_pixel = (128, 128, 128, 0)
                    else:
                        dst_pixel = (0, 0, 0, 0)

                dest.set_at((dest_x, dest_y), dst_pixel)

    def gPATT(self, id: int, w: int, h: int, mode: int) -> None:
        for i in range(len(self.windows)):
            if self.windows[i].ID == id:
                from_window = self.windows[i]
                to_window = self.windows[self.graphics_cursor]

                s_w = from_window.width
                s_h = from_window.height

                for y in range(h):
                    for x in range(w):
                        self.set_at_mode(
                            from_window.black_plane_surface,
                            to_window.black_plane_surface,
                            x % s_w,
                            y % s_h,
                            to_window.gATx + x,
                            to_window.gATy + y,
                            mode,
                            False,
                        )
                        self.set_at_mode(
                            from_window.grey_plane_surface,
                            to_window.grey_plane_surface,
                            x % s_w,
                            y % s_h,
                            to_window.gATx + x,
                            to_window.gATy + y,
                            mode,
                            True,
                        )

                break

        self.update_required = True

    def gUPDATE(self, arg: int) -> None:
        if arg == 255:
            # print(f' - Forcing screen composite')

            self.composite(self.executable, True)
        else:
            self.gupdate_enabled = True if arg == 1 else False
            _logger.info(f" - gUPDATE INPUT: {arg}")
            _logger.info(f" - gUPDATE STATUS: {self.gupdate_enabled}")
            input()

    def DEFAULTWIN(self, mode: int) -> None:
        self.defaultwin_mode = mode
        self.update_required = True

    def cursor(self):
        return self._window_cursor

    def get_window_name(self) -> str:
        self.update_required = True
        return pygame.display.get_caption()[0]

    def set_window_name(self, name: str) -> None:
        self.update_required = True
        pygame.display.set_caption(name)

    @lru_cache(maxsize=1024)
    def create_text_surface(
        self, text: str, foreground: pygame.Color
    ) -> pygame.Surface:
        return self.default_font.render(
            text,
            True,
            foreground,
        )

    def gPEEKLINE(self, id: int, x: int, y: int, ln: int) -> str:
        surface_to_peek = self.screen_buffer
        if id != 0:
            use_grey = False
            if id > 0x8000:
                use_grey = True
                id -= 0x8000

            # Peek a window, not the whole screen
            for i in range(len(self.windows)):
                if self.windows[i].ID == id:
                    if use_grey:
                        surface_to_peek = self.windows[i].grey_plane_surface
                    else:
                        surface_to_peek = self.windows[i].black_plane_surface
                    break

        if x > surface_to_peek.get_width() or y > surface_to_peek.get_height():
            return "0" * ln

        result = ""
        for i in range(ln):
            if x + i > surface_to_peek.get_width():
                continue

            # Psion arrays start at 1...
            col = surface_to_peek.get_at((x + i - 1, y + 1))

            result += "1" if (col[0] != 255) else "0"

        return result

    def gSetOpenAddress(self, bx: int, cx: int, dx: int) -> None:
        self.open_address = [bx, cx, dx]

    def DRAWSPRITE(self, dx: int, dy: int) -> None:
        if len(DrawableSprite._sprites) == 0:
            # No sprites have been loaded
            raise ("No sprites have been loaded into memory")

        sprite = DrawableSprite._sprites[DrawableSprite._current_sprite]

        sprite.start_time_tenths = int(datetime.datetime.now().timestamp()) * 10
        sprite.xpos = dx
        sprite.ypos = dy

        DrawableSprite.draw_sprite = True
        self.update_required = True

    def POSSSPRITE(self, dx: int, dy: int) -> None:
        sprite = DrawableSprite._sprites[DrawableSprite._current_sprite]
        sprite.xpos = dx
        sprite.ypos = dy
        self.update_required = True

    def composite_sprite(self, render_surface):
        sprite = DrawableSprite._sprites[DrawableSprite._current_sprite]

        # HACK
        sprite_ggmode = 0

        # Check to see if the animation idx needs incrementing
        tenths_delta = (
            int(datetime.datetime.now().timestamp()) * 10 - sprite.start_time_tenths
        )

        # mod it to the max timespan
        if sprite.timespan_tenths == 0:
            tenths_delta = 0
        else:
            tenths_delta = tenths_delta % sprite.timespan_tenths

        # Work out which sprite to draw
        bitmap_set = [
            s
            for s in sprite.bitmap_sets
            if s["tenths_delta"] >= tenths_delta
            and s["tenths_delta"] + s["tenths"] <= tenths_delta
        ]

        if len(bitmap_set) == 0:
            raise ("Failed to find sprite")

        bitmap_set = bitmap_set[-1]["bitmaps"]

        if self.defaultwin_mode > 0:
            # Draw Grey Plane
            if sprite_ggmode == 0 and bitmap_set[3]:
                # Set Pixels
                self.grey_plane_surface.blit(bitmap_set[3], (sprite.xpos, sprite.ypos))
            elif sprite_ggmode == 1 and bitmap_set[4]:
                # Clear Pixels
                pass
                print("Composite Sprite - gGMODE 1 - Not yet implemented")
                # input()
            elif sprite_ggmode == 2 and bitmap_set[5]:
                pass
                print("Composite Sprite - gGMODE 2 - Not yet implemented")
                input()

        # Draw Black Plane
        if sprite_ggmode == 0 and bitmap_set[0]:
            # Set Pixels
            self.black_plane_surface.blit(bitmap_set[0], (sprite.xpos, sprite.ypos))
        elif sprite_ggmode == 1 and bitmap_set[1]:
            # Clear Pixels
            print("Composite Sprite - gGMODE 1 - Not yet implemented")
            input()
            pass
        elif sprite_ggmode == 2 and bitmap_set[2]:
            # Invert Pixels
            pass
            print("Composite Sprite - gGMODE 2 - Not yet implemented")
            input()
