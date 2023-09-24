import os
import json
import struct

import pygame
from pygame.locals import *

import logging
import logging.config

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


MENU_MARGIN = 16
MENU_PADDING_WIDTH = 12
MENU_PADDING_HEIGHT = 6
MENU_ITEM_PADDING_HEIGHT = 2


class Menu:
    def __init__(self) -> None:
        self.menu_font = pygame.font.SysFont("arial", 10)
        self.menu_font_bold = pygame.font.SysFont("arial", 10, bold=True)

        # A cache of the rendered screen buffer, so not to render the screen each frame
        self.cached_surface_buffer = None

        # The character code of the menu item that is currently selected
        self.selected_item = [0, 0]

        # Internal flags
        self.show = False

        self.menu_items = []

    def MENU(self, mcard_index: int, item_index: int) -> None:
        self.selected_item = [mcard_index, item_index]

        self.show = True

    def mCARD(self, title: str, entries):
        self.menu_items.append((title, entries))

    def handle_MENU(self):
        # If there was a highlighted line, return the number
        m = self.selected_item[0]
        i = self.selected_item[1]

        return self.menu_items[m][1][i][1]

    def handle_keypress(self, evt_id: int) -> None:
        print(f"Handling Dialog Keypress: {evt_id}")

        if self.selected_item != 0:  # Would be 0 if there are no selectable items
            print(pygame.K_RIGHT)
            if evt_id == pygame.K_UP:
                # Up Arrow Key
                self.selected_item[1] -= 1
                if self.selected_item[1] == -1:
                    self.selected_item[1] = (
                        len(self.menu_items[self.selected_item[0]][1]) - 1
                    )

            elif evt_id == pygame.K_DOWN:
                # Down Arrow Key
                self.selected_item[1] += 1
                if self.selected_item[1] == len(
                    self.menu_items[self.selected_item[0]][1]
                ):
                    self.selected_item[1] = 0

            elif evt_id == pygame.K_LEFT:
                # Left Arrow Key
                self.selected_item[0] -= 1
                if self.selected_item[0] == -1:
                    self.selected_item[0] = len(self.menu_items) - 1

                self.selected_item[1] = 0

            elif evt_id == pygame.K_RIGHT:
                # Right Arrow Key
                self.selected_item[0] += 1
                if self.selected_item[0] == len(self.menu_items):
                    self.selected_item[0] = 0

                self.selected_item[1] = 0

            # Force re-render
            self.cached_surface_buffer = None

    def composite(self, render_surface: pygame.Surface) -> pygame.Surface:
        if self.cached_surface_buffer:
            # If no updates have been required, return the pre-rendered surface
            render_surface.blit(
                self.cached_surface_buffer,
                (
                    0,
                    0,
                    self.cached_surface_buffer.get_width(),
                    self.cached_surface_buffer.get_height(),
                ),
            )
            return render_surface

        item_height = self.menu_font_bold.size("TEXT")[1]

        menu_h = item_height + MENU_PADDING_HEIGHT * 2
        menu_w = MENU_MARGIN * 2 + sum(
            [
                self.menu_font_bold.size(mcard[0])[0] + MENU_PADDING_WIDTH * 3
                for mcard in self.menu_items
            ]
        )

        # Render drop shadow
        render_surface.fill(color=(128, 128, 128), rect=(2, 2, menu_w, menu_h))

        # Clear menu background
        render_surface.fill(color=(255, 255, 255), rect=(0, 0, menu_w, menu_h))

        # Draw Menu Borders
        pygame.draw.rect(render_surface, (0, 0, 0), (0, 0, menu_w, menu_h), 2)
        pygame.draw.rect(
            render_surface, (160, 160, 160), (3, 3, menu_w - 6, menu_h - 6), 1
        )

        pygame.draw.line(
            render_surface, (64, 64, 64), (2, menu_h - 2), (menu_w - 2, menu_h - 2), 1
        )
        pygame.draw.line(
            render_surface, (64, 64, 64), (3, menu_h - 3), (menu_w - 3, menu_h - 3), 1
        )

        pygame.draw.line(
            render_surface, (64, 64, 64), (menu_w - 3, 3), (menu_w - 3, menu_h - 3), 1
        )

        # Fill menu background
        render_surface.fill(color=(192, 192, 192), rect=(4, 4, menu_w - 8, menu_h - 8))

        # Render mCARDS
        menu_off = MENU_MARGIN
        for m in range(len(self.menu_items)):
            font_surface = self.menu_font_bold.render(
                self.menu_items[m][0], True, (0, 0, 0)
            )

            if m == self.selected_item[0]:
                # mCARD is selected.
                render_surface.fill(
                    color=(255, 255, 255),
                    rect=(
                        menu_off,
                        0,
                        font_surface.get_width() + MENU_PADDING_WIDTH * 2,
                        menu_h,
                    ),
                )
                pygame.draw.rect(
                    render_surface,
                    (0, 0, 0),
                    (
                        menu_off,
                        0,
                        font_surface.get_width() + MENU_PADDING_WIDTH * 2,
                        menu_h,
                    ),
                    2,
                )
                pygame.draw.rect(
                    render_surface,
                    (160, 160, 160),
                    (
                        menu_off + 3,
                        3,
                        font_surface.get_width() + MENU_PADDING_WIDTH * 2 - 6,
                        menu_h - 6,
                    ),
                    1,
                )

                mcard_h = len(self.menu_items[m][1]) * (
                    item_height + 2 * MENU_ITEM_PADDING_HEIGHT
                )

                max_width = 0
                for i in range(len(self.menu_items[m][1])):
                    mcard_item_w = self.menu_font_bold.size(
                        self.menu_items[m][1][i][0] + "Ctrl + A"
                    )[0]
                    max_width = max(max_width, mcard_item_w)

                max_width += MENU_PADDING_WIDTH * 2

                mcard_w = max_width  # Test

                # mCARD drop shadow
                render_surface.fill(
                    color=(128, 128, 128),
                    rect=(menu_off + 2, menu_h, mcard_w + 2, menu_h - 8 + mcard_h),
                )

                # mCARD dropdown border
                render_surface.fill(
                    color=(255, 255, 255),
                    rect=(menu_off, menu_h - 6, mcard_w, menu_h - 6 + mcard_h),
                )

                pygame.draw.rect(
                    render_surface,
                    (0, 0, 0),
                    (menu_off, menu_h - 6, mcard_w, menu_h - 6 + mcard_h),
                    2,
                )
                pygame.draw.rect(
                    render_surface,
                    (160, 160, 160),
                    (menu_off + 3, menu_h - 3, mcard_w - 6, menu_h - 12 + mcard_h),
                    1,
                )

                mcard_off_h = menu_h
                for i in range(len(self.menu_items[m][1])):
                    if self.selected_item[1] == i:
                        render_surface.fill(
                            color=(0, 0, 0),
                            rect=(
                                menu_off + 5,
                                mcard_off_h,
                                mcard_w - 10,
                                item_height + 2 * MENU_ITEM_PADDING_HEIGHT,
                            ),
                        )

                        mcard_item_col = (255, 255, 255)
                    else:
                        mcard_item_col = (0, 0, 0)

                    mcard_off_h += MENU_ITEM_PADDING_HEIGHT
                    mcard_font_surface = self.menu_font_bold.render(
                        self.menu_items[m][1][i][0], True, mcard_item_col
                    )
                    render_surface.blit(
                        mcard_font_surface, (menu_off + MENU_PADDING_WIDTH, mcard_off_h)
                    )

                    print(self.menu_items[m][1][i][1])
                    char_val = self.menu_items[m][1][i][1]
                    char_val = min(char_val, 120)
                    char_val = max(char_val, 65)

                    mcard_font_surface = self.menu_font.render(
                        "Ctrl+" + chr(char_val), True, mcard_item_col
                    )
                    render_surface.blit(
                        mcard_font_surface,
                        (
                            menu_off + mcard_w - 10 - mcard_font_surface.get_width(),
                            mcard_off_h,
                        ),
                    )

                    mcard_off_h += item_height + MENU_ITEM_PADDING_HEIGHT

            render_surface.blit(
                font_surface, (menu_off + MENU_PADDING_WIDTH, MENU_PADDING_HEIGHT)
            )

            menu_off += font_surface.get_width() + MENU_PADDING_WIDTH * 2

        self.cached_surface_buffer = pygame.Surface.copy(render_surface)

        return render_surface
