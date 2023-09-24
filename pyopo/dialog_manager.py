from pyopo.filehandler_filesystem import *
from typing import List

import pygame
from pygame.locals import *

import logging
import logging.config

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


DIALOG_MARGIN = 6
DIALOG_PADDING = 2

# Minimum width a dialog row can be
MIN_ROW_WIDTH = 180

ALLOWED_ALPHA_CHARS = [
    K_a,
    K_b,
    K_c,
    K_d,
    K_e,
    K_f,
    K_g,
    K_h,
    K_i,
    K_j,
    K_k,
    K_l,
    K_m,
    K_n,
    K_o,
    K_p,
    K_q,
    K_r,
    K_s,
    K_t,
    K_u,
    K_v,
    K_w,
    K_x,
    K_y,
    K_z,
    K_SPACE,
    K_COMMA,
    K_PERIOD,
]
ALLOWED_NUM_CHARS = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]


class Dialog:
    def __init__(self, title, flags) -> None:
        self.title = title
        self.flags = flags

        self.pos_x = 0
        self.pos_y = 0

        self.dialog_font = pygame.font.SysFont("arial", 10)
        self.dialog_font_bold = pygame.font.SysFont("arial", 10, bold=True)

        # Store the max index of selectable item
        self.select_count = 0

        self.dialog_surface = None

        self.selected_item = None

        # Internal flags
        self.show = False

        self.dialog_items = []

        if len(title) > 0 and flags != 2:
            self.dialog_items.append(
                {
                    "type": "dINIT",
                    "title": title,
                    "selectable": False,
                    "selection_index": None,
                }
            )

    def DIALOG(self) -> None:
        self.show = True

        if self.select_count == 0:
            self.selected_item = None
        else:
            self.selected_item = 0

    def dTEXT(self, p: str, body: str, text_align: int) -> None:
        use_bold = False
        draw_line = False
        selectable = False
        text_type = text_align

        if text_type - 1024 >= 0:
            selectable = True
            text_type -= 1024

        if text_type - 512 >= 0:
            draw_line = True
            text_type -= 512

        if text_type - 256 >= 0:
            use_bold = True
            text_type -= 256

        self.dialog_items.append(
            {
                "type": "dTEXT",
                "p": p,
                "body": body,
                "text_align": text_type,
                "use_bold": use_bold,
                "draw_line": draw_line,
                "selectable": selectable,
                "selection_index": None if not selectable else self.select_count,
            }
        )

        if selectable:
            self.select_count += 1

    def dEDIT(self, addr: int, value: str, prompt: str, max_len: int) -> None:
        self.dialog_items.append(
            {
                "type": "dEDIT",
                "addr": addr,
                "value": str(value),
                "prompt": prompt,
                "max_len": max_len,
                "selectable": True,
                "selection_index": self.select_count,
            }
        )

        self.select_count += 1

    def dBUTTONS(self, buttons) -> None:
        self.dialog_items.append(
            {
                "type": "dBUTTONS",
                "buttons": buttons,
                "selectable": False,
                "selection_index": None,
            }
        )

    def dLONG(self, addr: int, value: int, prompt: str, min: int, max: int) -> None:
        self.dialog_items.append(
            {
                "type": "dLONG",
                "addr": addr,
                "value": str(value),
                "prompt": prompt,
                "min": min,
                "max": max,
                "selectable": True,
                "selection_index": self.select_count,
            }
        )

        self.select_count += 1

    def dFLOAT(
        self, addr: int, value: float, prompt: str, min: float, max: float
    ) -> None:
        self.dialog_items.append(
            {
                "type": "dFLOAT",
                "addr": addr,
                "value": str(value),
                "prompt": prompt,
                "min": min,
                "max": max,
                "selectable": True,
                "selection_index": self.select_count,
            }
        )

        self.select_count += 1

    def dFILE(
        self, addr: int, value: str, file_list: str, prompt: str, flags: int
    ) -> None:
        self.dialog_items.append(
            {
                "type": "dFILE",
                "addr": addr,
                "value": 0,
                "prompt": prompt,
                "choice_list": file_list,
                "selectable": True,
                "selection_index": self.select_count,
                "dfile_flags": flags,
                "dfile_value": value,
            }
        )

    def dCHOICE(self, addr, value, prompt, choice_list):
        self.dialog_items.append(
            {
                "type": "dCHOICE",
                "addr": addr,
                "value": max(1, value),
                "prompt": prompt,
                "choice_list": choice_list,
                "selectable": True,
                "selection_index": self.select_count,
            }
        )

        self.select_count += 1

    def dPOSITION(self, x: int, y: int) -> None:
        self.pos_x = x
        self.pos_y = y

    def handle_DIALOG(self, data_stack) -> int:
        # Store results into the Data Stack Frame
        for item in self.dialog_items:
            if item["type"] == "dEDIT":
                print(f"Storing '{item['value']}' to {item['addr']}")
                data_stack.write(3, item["value"], item["addr"])
            elif item["type"] == "dLONG":
                print(f"Storing '{item['value']}' to {item['addr']}")
                data_stack.write(1, int(item["value"]), item["addr"])
            elif item["type"] == "dFLOAT":
                print(f"Storing '{item['value']}' to {item['addr']}")
                data_stack.write(2, float(item["value"]), item["addr"])
            elif item["type"] == "dFILE":
                print(f"Storing '{item['value']}' to {item['addr']}")
                data_stack.write(3, item["dfile_value"], item["addr"])

        # If the user cancels the dialog with Esc, 0 is returned, but this is handled elsewhere
        if self.select_count == 0:
            # There were no selectable items on the dialog
            return 1
        else:
            # Return the line which was highlighted (which widget, not which selectable item)
            for i in range(len(self.dialog_items)):
                if self.dialog_items[i]["selection_index"] == self.selected_item:
                    return i + 1

            raise ("Unable to determine selected item")

    def handle_keypress(self, evt_id: int):
        print(f"Handling Dialog Keypress: {evt_id}")

        if (
            self.selected_item is not None
        ):  # Would be 0 if there are no selectable items
            if evt_id == 257:
                print("Down Pressed")
                # Down Arrow Key
                self.selected_item += 1
                if self.selected_item >= self.select_count:
                    self.selected_item = 0

                print(f"Selected Dialog item = {self.selected_item}")

            elif evt_id == 256:
                # Up Arrow Key
                print("Up Pressed")
                self.selected_item -= 1
                if self.selected_item < 0:
                    self.selected_item = self.select_count - 1

                print(f"Selected Dialog item = {self.selected_item}")

            else:
                print(f"Passing value to selected item: {self.selected_item}")
                # Pass on the keypress to the entry
                for i in range(len(self.dialog_items)):
                    if self.dialog_items[i]["selection_index"] == self.selected_item:
                        # Pass over keypress to the selected item
                        print(f"Passing over value: {evt_id} to selected item")

                        if self.dialog_items[i]["type"] in ["dEDIT"]:
                            if evt_id == 8:
                                # User has pressed delete
                                if len(self.dialog_items[i]["value"]) > 0:
                                    self.dialog_items[i]["value"] = self.dialog_items[
                                        i
                                    ]["value"][:-1]
                            elif (
                                evt_id in ALLOWED_ALPHA_CHARS
                                or evt_id in ALLOWED_NUM_CHARS
                            ):
                                # Add the character
                                self.dialog_items[i]["value"] += chr(evt_id)
                        elif self.dialog_items[i]["type"] in ["dLONG", "dFLOAT"]:
                            if evt_id == 8:
                                # User has pressed delete
                                if len(self.dialog_items[i]["value"]) > 0:
                                    self.dialog_items[i]["value"] = self.dialog_items[
                                        i
                                    ]["value"][:-1]
                            elif evt_id in ALLOWED_NUM_CHARS:
                                # Add the character
                                self.dialog_items[i]["value"] += chr(evt_id)
                            elif (
                                self.dialog_items[i]["type"] == "dFLOAT"
                                and evt_id == K_PERIOD
                            ):
                                # dFLOAT allows for decimal
                                if "." not in self.dialog_items[i]["value"]:
                                    self.dialog_items[i]["value"] += "."
                            elif (
                                evt_id == K_MINUS
                                and len(self.dialog_items[i]["value"]) == 0
                            ):
                                # Only alow minus symbol as first character
                                self.dialog_items[i]["value"] += "-"

                        elif self.dialog_items[i]["type"] in ["dFILE", "dCHOICE"]:
                            # Only accept left and right
                            if evt_id == 259:
                                # Left
                                self.dialog_items[i]["value"] -= 1
                                if self.dialog_items[i]["value"] == 0:
                                    self.dialog_items[i]["value"] = len(
                                        self.dialog_items[i]["choice_list"].split(",")
                                    )

                            elif evt_id == 258:
                                # Right
                                self.dialog_items[i]["value"] += 1
                                if self.dialog_items[i]["value"] > len(
                                    self.dialog_items[i]["choice_list"].split(",")
                                ):
                                    self.dialog_items[i]["value"] = 1
                        break

            # Force re-render
            self.dialog_surface = None

    def get_button_keycodes(self) -> List[int]:
        button_keycodes = []
        for item in self.dialog_items:
            if item["type"] == "dBUTTONS":
                for i in range(len(item["buttons"])):
                    button_keycodes.append(item["buttons"][i][1])

        return button_keycodes

    def composite(self, screen_width, screen_height):
        if self.dialog_surface:
            # If no updates have been required, return the pre-rendered surface
            return self.dialog_surface

        # Based on the default Font, determine the size (height) of each row
        item_height = self.dialog_font.size("TEXT")[1] + DIALOG_PADDING * 2

        # Work out maximum width & height of the items
        max_width = 0
        for item in self.dialog_items:
            item_width = 0
            if item["type"] == "dINIT":
                item_width = (
                    self.dialog_font.size(item["title"])[0] + DIALOG_PADDING * 2
                )
            elif item["type"] == "dTEXT":
                item_width = (
                    self.dialog_font.size(item["p"])[0]
                    + self.dialog_font.size(item["body"])[0]
                    + DIALOG_PADDING * 3
                )
            elif item["type"] in ["dEDIT", "dLONG", "dCHOICE", "dFLOAT"]:
                item_width = (
                    self.dialog_font.size(item["prompt"])[0]
                    + self.dialog_font.size("ABCDEFGHIJKL")[0]
                    + DIALOG_PADDING * 3
                )

                # item_width = screen_width - DIALOG_MARGIN * 2 - DIALOG_PADDING * 2
            elif item["type"] == "dBUTTONS":
                item_width = 0
                max_button_width = 0
                for i in range(len(item["buttons"])):
                    # Work out the size of the maximum button
                    button_text = (
                        item["buttons"][i][0] + " %" + chr(item["buttons"][i][1])
                    )
                    max_button_width = max(
                        max_button_width, self.dialog_font.size(button_text)[0]
                    )

                button_width = max_button_width + DIALOG_PADDING * 2
                item["button_width"] = button_width

                item_width = button_width * len(item["buttons"])
                item_width += DIALOG_PADDING * (len(item["buttons"]) - 1)

                item["buttons_total_width"] = item_width

                item_width += DIALOG_MARGIN * 2 + DIALOG_PADDING * 2

            # Set minimum width
            item_width = max(item_width, MIN_ROW_WIDTH)

            max_width = max(max_width, item_width)

        max_height = item_height * len(self.dialog_items)

        self.dialog_width = max_width + DIALOG_MARGIN * 2
        self.dialog_height = max_height + DIALOG_MARGIN * 2

        # Generate the surface for the dialog
        self.dialog_surface = pygame.Surface((self.dialog_width, self.dialog_height))
        self.dialog_surface.fill((255, 255, 255))

        # Render the border
        pygame.draw.rect(
            self.dialog_surface,
            (0, 0, 0),
            (0, 0, self.dialog_width, self.dialog_height),
            2,
        )
        pygame.draw.rect(
            self.dialog_surface,
            (160, 160, 160),
            (4, 4, self.dialog_width - 8, self.dialog_height - 8),
            1,
        )

        # Render each part of the dialog
        height_offset = 5
        for i in range(len(self.dialog_items)):
            item = self.dialog_items[i]

            if item["type"] == "dINIT":
                self.dialog_surface.fill(
                    color=(192, 192, 192),
                    rect=(5, height_offset, self.dialog_width - 10, item_height),
                )

                font_surface = self.dialog_font.render(item["title"], True, (0, 0, 0))
                self.dialog_surface.blit(
                    font_surface,
                    (
                        self.dialog_width / 2 - font_surface.get_width() / 2,
                        height_offset + DIALOG_PADDING,
                    ),
                )
            elif item["type"] == "dTEXT":
                if item["selectable"] and self.selected_item == item["selection_index"]:
                    # Item is selected
                    print("Item is selected")
                    self.dialog_surface.fill(
                        color=(160, 160, 160),
                        rect=(
                            DIALOG_MARGIN,
                            height_offset,
                            self.dialog_width - (DIALOG_MARGIN) * 2,
                            item_height,
                        ),
                    )

                d_offset = DIALOG_MARGIN + DIALOG_PADDING
                if len(item["p"]) > 0:
                    font_surface = self.dialog_font.render(item["p"], True, (0, 0, 0))
                    self.dialog_surface.blit(
                        font_surface, (d_offset, height_offset + DIALOG_PADDING)
                    )
                    d_offset += font_surface.get_width() + DIALOG_PADDING

                if len(item["body"]) > 0:
                    if item["use_bold"]:
                        font_surface = self.dialog_font_bold.render(
                            item["body"], True, (0, 0, 0)
                        )
                    else:
                        font_surface = self.dialog_font.render(
                            item["body"], True, (0, 0, 0)
                        )

                    if item["text_align"] == 1:
                        # Right Align Body Text
                        d_offset = (
                            self.dialog_width
                            - DIALOG_MARGIN
                            - font_surface.get_width()
                            - DIALOG_PADDING
                        )
                    elif item["text_align"] == 2:
                        # Centre Align Body Text
                        d_offset = (
                            d_offset
                            + (
                                self.dialog_width
                                - DIALOG_MARGIN
                                - DIALOG_PADDING
                                - d_offset
                            )
                            / 2
                            - font_surface.get_width() / 2
                        )

                    self.dialog_surface.blit(
                        font_surface, (d_offset, height_offset + DIALOG_PADDING)
                    )

                    if item["draw_line"]:
                        pygame.draw.line(
                            self.dialog_surface,
                            (0, 0, 0),
                            (
                                DIALOG_MARGIN + DIALOG_PADDING,
                                height_offset + item_height - DIALOG_PADDING,
                            ),
                            (
                                self.dialog_width - DIALOG_MARGIN - DIALOG_PADDING,
                                height_offset + item_height - DIALOG_PADDING,
                            ),
                            1,
                        )
            elif item["type"] in ["dEDIT", "dLONG", "dFLOAT"]:
                d_offset = DIALOG_MARGIN + DIALOG_PADDING

                if len(item["prompt"]) > 0:
                    font_surface = self.dialog_font.render(
                        item["prompt"], True, (0, 0, 0)
                    )
                    self.dialog_surface.blit(
                        font_surface, (d_offset, height_offset + DIALOG_PADDING)
                    )
                    d_offset += DIALOG_PADDING + font_surface.get_width()

                if self.selected_item == item["selection_index"]:
                    # Current item is selected
                    render_col = (0, 0, 0)
                else:
                    render_col = (160, 160, 160)

                pygame.draw.rect(
                    self.dialog_surface,
                    render_col,
                    (
                        d_offset,
                        height_offset + 1,
                        self.dialog_width - DIALOG_MARGIN - DIALOG_PADDING - d_offset,
                        item_height - 2,
                    ),
                    1,
                )

                sanitised = str(item["value"]).replace("\0", "")
                # Draw Text
                if len(sanitised) > 0:
                    # Only render if there is actually text to render
                    font_surface = self.dialog_font.render(sanitised, True, render_col)
                    self.dialog_surface.blit(
                        font_surface, (d_offset + 2, height_offset + DIALOG_PADDING)
                    )

            elif item["type"] == "dBUTTONS":
                d_offset = DIALOG_MARGIN + DIALOG_PADDING

                print(item)

                for i in range(len(item["buttons"])):
                    button_text = (
                        item["buttons"][i][0] + " %" + chr(item["buttons"][i][1])
                    )
                    font_surface = self.dialog_font.render(button_text, True, (0, 0, 0))
                    button_text_offset = (
                        item["button_width"] - font_surface.get_width()
                    ) / 2

                    pygame.draw.rect(
                        self.dialog_surface,
                        (0, 0, 0),
                        (
                            d_offset,
                            height_offset + 1,
                            item["button_width"],
                            item_height - 2,
                        ),
                        1,
                    )

                    self.dialog_surface.blit(
                        font_surface,
                        (d_offset + button_text_offset, height_offset + DIALOG_PADDING),
                    )

                    d_offset += item["button_width"]

                    if i < len(item["buttons"]) - 1:
                        # Padding between buttons
                        d_offset += DIALOG_PADDING

            elif item["type"] in ["dFILE", "dCHOICE"]:
                d_offset = DIALOG_MARGIN + DIALOG_PADDING

                if len(item["prompt"]) > 0:
                    font_surface = self.dialog_font.render(
                        item["prompt"], True, (0, 0, 0)
                    )
                    self.dialog_surface.blit(
                        font_surface, (d_offset, height_offset + DIALOG_PADDING)
                    )
                    d_offset += DIALOG_PADDING + font_surface.get_width()

                if self.selected_item == item["selection_index"]:
                    # Current item is selected
                    render_col = (0, 0, 0)
                else:
                    render_col = (160, 160, 160)

                pygame.draw.rect(
                    self.dialog_surface,
                    render_col,
                    (
                        d_offset + 5,
                        height_offset + 1,
                        self.dialog_width
                        - DIALOG_MARGIN
                        - DIALOG_PADDING
                        - d_offset
                        - 10,
                        item_height - 2,
                    ),
                    1,
                )

                # Draw Triangles

                # Draw Text
                print(f"Current Index: {item['value']}")
                choice = item["choice_list"].split(",")[item["value"] - 1].strip()
                font_surface = self.dialog_font.render(choice, True, render_col)
                self.dialog_surface.blit(
                    font_surface, (d_offset + 5 + 2, height_offset + DIALOG_PADDING)
                )

            height_offset += item_height

        return self.dialog_surface

    def get_stanitised_font_surface(self, text: str, col):
        sanitised_text = text.replace("\0", "")

        font_surface = self.dialog_font.render(sanitised_text, True, col)
        return font_surface
