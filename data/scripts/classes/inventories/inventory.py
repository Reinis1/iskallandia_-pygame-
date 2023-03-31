import pygame
import os



from data.variables import *
from data.scripts.core_functions import draw_rect_alpha

imgs_dir = 'data/imgs/block_previews'
price_types_dir = 'data/imgs/price_types'

font = pygame.font.Font('data/fonts/minecraft_font.ttf', INV_FONT_SIZE)
subt_font = pygame.font.Font('data/fonts/minecraft_font.ttf', 10)


class PlayerInventory:

    def __init__(self, rows=3, cols=9, pos_hint_y=None):
        self.h = 10
        self.hovered_upgrade = False
        self.rows = rows
        self.cols = cols
        scale = int(TILE_SIZE*0.75)
        self.shift = False

        self.open = False

        self.width = self.cols * scale  # in real screen pixels
        self.height = self.rows * scale
        self.slot_width = scale
        self.slot_height = scale
        self.x = WINDOW_SIZE[0] // 2 - self.width // 2

        if pos_hint_y is None:
            self.y = (WINDOW_SIZE[1] // 2 - self.height // 2) + 50
        else:
            self.y = pos_hint_y
        self.selected_slot = (1, 1)

        self.base_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.inventory_rects = []
        self.row_y = self.y

        self.inventory_contents = []
        self.empty_inventory = None
        self.selection = None

        self.i = 0
        self.hovered_hotbar_slot = None

        self.m_xy = (0, 0)
        self.hovered = None
        self.info_rect = pygame.Rect(0, 0, TILE_SIZE*3, TILE_SIZE)
        self.clear_inv()

        for row in range(self.rows):  # creates all the physical rects for inventory
            x = self.x
            self.slot_rects = {}
            for i in range(self.cols):
                rect = pygame.Rect(x, self.row_y, self.slot_width, self.slot_height)
                self.slot_rects[i + 1] = rect
                x += self.slot_width
            self.inventory_rects.append(self.slot_rects)
            self.row_y += self.slot_height

        self.block_preview_imgs = {}
        for img in os.listdir(imgs_dir):
            loaded_img = pygame.image.load(imgs_dir + '/' + img).convert_alpha()
            loaded_img = pygame.transform.scale(loaded_img, (self.slot_width - TILE_SIZE//10, self.slot_height - TILE_SIZE//10))
            img_name = img.split('.')[0]
            self.block_preview_imgs[img_name] = loaded_img

        self.price_types = {}
        for img in os.listdir(price_types_dir):
            loaded_img = pygame.image.load(price_types_dir + '/' + img).convert_alpha()
            loaded_img = pygame.transform.scale(loaded_img, (self.slot_width - TILE_SIZE//2, self.slot_height - TILE_SIZE//2))
            img_name = img.split('.')[0]
            self.price_types[img_name] = loaded_img

    def clear_inv(self):
        self.inventory_contents = []
        for row in range(self.rows):  # creates a data set to store items in inventory - list[dict: list[type, amount]]
            slot_contents = {}
            for slot in range(self.cols):
                slot_contents[slot + 1] = []
            self.inventory_contents.append(slot_contents)

    def add(self, block_type: str, amount: int):
        for inventory_row in self.inventory_contents:
            for index, item in inventory_row.items():
                if item != []:
                    if item[0] == block_type and item[1] < STACK_SIZE:
                        starting_amount = item[1]
                        item[1] += amount
                        if item[1] > STACK_SIZE:
                            item[1] = STACK_SIZE
                            remaining_amount = amount - (STACK_SIZE - starting_amount)
                            self.add(block_type, remaining_amount)
                            return
                        else:
                            return

        for inventory_row in self.inventory_contents:
            for index, item in inventory_row.items():
                if item == []:
                    item.append(block_type)
                    item.append(amount)
                    return

    def add_to_selected_slot(self, inventory, bl=None):
        block = self.selection

        sel_col = self.selected_slot[0]
        sel_row = self.selected_slot[1]
        slot = self.inventory_contents[sel_row - 1][sel_col]

        if slot == []:
            self.selection = None
            self.inventory_contents[sel_row - 1][sel_col] = block
        elif slot[0] == block[0] and slot[1] < STACK_SIZE:
            self.inventory_contents[sel_row-1][sel_col][1] += block[1]
            if self.inventory_contents[sel_row - 1][sel_col][1] > STACK_SIZE:
                self.selection[1] = self.inventory_contents[sel_row - 1][sel_col][1]-STACK_SIZE
                self.inventory_contents[sel_row - 1][sel_col][1] = STACK_SIZE

            else:
                self.selection = None
        else:
            self.selection = self.inventory_contents[sel_row - 1][sel_col]
            self.inventory_contents[sel_row - 1][sel_col] = block

    def add_to_selected_hb_slot(self, block, hotbar):
        slot = hotbar.slot_contents[self.hovered_hotbar_slot]

        if slot == []:
            hotbar.slot_contents[self.hovered_hotbar_slot] = block
            self.selection = None
        elif slot[0] == block[0] and slot[1] < STACK_SIZE:
            hotbar.slot_contents[self.hovered_hotbar_slot][1] += block[1]
            if hotbar.slot_contents[self.hovered_hotbar_slot][1] > STACK_SIZE:
                self.selection[1] = hotbar.slot_contents[self.hovered_hotbar_slot][1]-STACK_SIZE
            else:
                self.selection = None
        else:
            self.selection = hotbar.slot_contents[self.hovered_hotbar_slot]
            hotbar.slot_contents[self.hovered_hotbar_slot] = block

    def get_selected_slot(self, mx, my, hotbar):
        if self.open:
            for index, rect in hotbar.slot_rects.items():
                if rect.collidepoint(mx, my):
                    self.hovered_hotbar_slot = index
                    break
                self.hovered_hotbar_slot = None

            for row_index, row in enumerate(self.inventory_rects):  # row = [] # Inventory
                for i, l in row.items():
                    if l.collidepoint(mx, my):
                        self.selected_slot = (i, row_index + 1)
                        return True
                    self.selected_slot = None

        else:
            self.selected_slot = None
            self.hovered_hotbar_slot = None

    def shift_to_hb(self, item, hotbar):
        slot = hotbar.get_available_slot(item[0])
        if slot == 0:
            return 0
        if hotbar.slot_contents[slot] == []:
            hotbar.slot_contents[slot] = item
        else:
            hotbar.slot_contents[slot][1] += item[1]
            if hotbar.slot_contents[slot][1] > STACK_SIZE:
                item[1] = hotbar.slot_contents[slot][1]-STACK_SIZE
                self.shift_to_hb(item, hotbar)
                hotbar.slot_contents[slot][1] = STACK_SIZE

    def on_click(self, hotbar, inventory):  # specific to player_inventory instance
        if self.selection is None:  # get selection is possible
            if self.selected_slot is not None:  # if a slot in inv is selected
                sel_col = self.selected_slot[0]
                sel_row = self.selected_slot[1]
                item = self.inventory_contents[sel_row - 1][sel_col]

                if item != []:
                    self.selection = item
                    self.inventory_contents[sel_row - 1][sel_col] = []
                    if self.shift:
                        if self.shift_to_hb(self.selection, hotbar) == 0:
                            self.inventory_contents[sel_row - 1][sel_col] = self.selection
                        self.selection = None
                else:
                    self.selection = None

            elif self.hovered_hotbar_slot is not None:  # if a slot in hotbar is hovered
                item = hotbar.slot_contents[self.hovered_hotbar_slot]  # stores slot info into a list variable
                if item != []:  # cheks if it has an item in the slot
                    self.selection = item
                    hotbar.slot_contents[self.hovered_hotbar_slot] = []
                    if self.shift:
                        self.add(item[0], item[1])
                        self.selection = None
                else:
                    self.selection = None
            else:
                self.selection = None


        else:  # something is already selected and it is clicked with
            if self.selected_slot is not None:
                self.add_to_selected_slot(inventory)

            elif self.hovered_hotbar_slot is not None:
                self.add_to_selected_hb_slot(self.selection, hotbar)

            else:
                self.add(self.selection[0], (self.selection[1]))
                self.selection = None

    def close(self, player_inventory):
        if self.selection is not None:
            player_inventory.add(self.selection[0], self.selection[1])
            self.selection = None

    def draw(self, display):
        if self.open:
            draw_rect_alpha(display, (0, 0, 0, 50), self.base_rect)
            for row, slot_rects in enumerate(self.inventory_rects):
                for i, rect in slot_rects.items():
                    if (i, row+1) != self.selected_slot:
                        pygame.draw.rect(display, (25, 25, 25), rect, 1)
                    # Drawing selected slot after the rest so that it is drawn on top of other slots
                    if self.selected_slot is not None:
                        sel_row = self.selected_slot[0]
                        sel_col = self.selected_slot[1] - 1
                        pygame.draw.rect(display, (200, 200, 200), self.inventory_rects[sel_col][sel_row], 2)

            for row, slot_contents in enumerate(self.inventory_contents):
                for i, n in slot_contents.items():  # i = Number, n = rectangle
                    if n != []:
                        centering_rect = self.block_preview_imgs[n[0]].get_rect()
                        centering_rect.center = self.inventory_rects[row][i].center
                        display.blit(self.block_preview_imgs[n[0]], centering_rect.topleft)

                        if n[1] > 1:
                            font_render = font.render(str(n[1]), True, (200, 200, 200))
                            font_centering_rect = font_render.get_rect()
                            font_centering_rect.bottomright = centering_rect.bottomright
                            display.blit(font_render, font_centering_rect.topleft)

            self.display_info(display)

            if self.selection is not None:
                n = self.selection
                centering_rect = self.block_preview_imgs[n[0]].get_rect()
                centering_rect.center = self.m_xy
                display.blit(self.block_preview_imgs[n[0]], centering_rect.topleft)
                if n[1] > 1:
                    font_render = font.render(str(n[1]), True, (200, 200, 200))
                    font_centering_rect = font_render.get_rect()
                    font_centering_rect.bottomright = centering_rect.bottomright
                    display.blit(font_render, font_centering_rect.topleft)

    def update(self, hotbar, shop, upgrades):
        # hotbar.display_cursor = False if self.open else True
        self.i += 480
        if self.i % 1 == 0:
            pass
        self.hovered = shop.get_hovered()
        if self.hovered is None:
            self.hovered = upgrades.get_hovered()
            self.hovered_upgrade = True if self.hovered is not None else False
        if self.hovered is None:
            if self.selected_slot is not None:
                sel_col = self.selected_slot[0]
                sel_row = self.selected_slot[1]
                item = self.inventory_contents[sel_row - 1][sel_col]
                if item is not None and item != []:
                    self.hovered = item.copy()
                else: self.hovered = None
            else:
                self.hovered = None
        # for i, n in self.slot_contents.items():
        #     if n != []:
        #         if n[1] <= 0:
        #             self.slot_contents[i] = []

    def display_info(self, display):
        if self.hovered is not None:
            self.info_rect.topleft = self.m_xy
            draw_rect_alpha(display, (0, 0, 0, 200), self.info_rect)
            if not self.hovered_upgrade:
                name = subt_font.render(str(self.hovered[0]).capitalize(), True, (200, 200, 200))
                display.blit(name, self.m_xy)
                try:
                    price = subt_font.render(str(self.hovered[2][0]), True, L_GRAY)
                    money_type = self.price_types[self.hovered[2][1]]
                    display.blit(price, (self.info_rect.right-self.h*3, self.info_rect.top))
                    display.blit(money_type, (self.info_rect.right-self.h, self.info_rect.top))
                except (KeyError, IndexError):
                    pass
                if self.hovered[0] in TOOLS and self.hovered[0] not in [gun for gun in GUNS.keys()]:
                    try:
                        ad = WEAPON_DAMAGE[self.hovered[0]]
                    except KeyError:
                        ad = WEAPON_DAMAGE['hand']
                    try:
                        haste = TOOL_SPEEDS[self.hovered[0]]
                    except KeyError:
                        haste = TOOL_SPEEDS['hand']
                    final_ad = font.render(f'Damage: {ad}', True, L_GRAY)
                    final_haste = font.render(f'Mining speed: {haste}', True, L_GRAY)
                    display.blit(final_ad, (self.m_xy[0], self.m_xy[1]+self.h))
                    display.blit(final_haste, (self.m_xy[0], self.m_xy[1] + self.h*2))

                elif self.hovered[0] in [gun for gun in GUNS.keys()]:
                    ad = PROJECTILE_TYPES[GUNS[self.hovered[0]]]['ad']
                    block_dmg = PROJECTILE_TYPES[GUNS[self.hovered[0]]]['block_dmg']
                    pen = PROJECTILE_TYPES[GUNS[self.hovered[0]]]['penetration']

                    final_ad = font.render(f'Damage: {ad}', True, L_GRAY)
                    final_block_dmg = font.render(f'Block dmg: {block_dmg}', True, L_GRAY)
                    final_pen = font.render(f'Penetration: {pen}', True, L_GRAY)

                    display.blit(final_ad, (self.m_xy[0], self.m_xy[1]+self.h*1))
                    display.blit(final_block_dmg, (self.m_xy[0], self.m_xy[1] + self.h*2))
                    display.blit(final_pen, (self.m_xy[0], self.m_xy[1] + self.h*3))

                elif self.hovered[0] in ARMOR:
                    if self.hovered[3][0] == 'boots':
                        speed = self.hovered[3][2]
                        j_height = self.hovered[3][3]
                        if speed != 0:
                            final_speed = font.render(f'+{speed} speed', True, 'blue')
                            display.blit(final_speed, (self.m_xy[0], self.m_xy[1] + self.h*3))
                        elif j_height != 0:
                            final_jump_height = font.render(f'+{j_height} jump height', True, 'blue')
                            display.blit(final_jump_height, (self.m_xy[0], self.m_xy[1] + self.h*3))

                    final_prot = font.render(f'Protection: {self.hovered[3][1]*10}', True, L_GRAY)
                    display.blit(final_prot, (self.m_xy[0], self.m_xy[1] + self.h*2))
                else:
                    try:
                        hardness = BLOCK_HARDNESS[self.hovered[0]]
                    except KeyError:
                        hardness = DEFAULT_BLOCK_HARDNESS
                    final_hardness = font.render(f'Toughness: {hardness}', True, L_GRAY)
                    display.blit(final_hardness, (self.m_xy[0], self.m_xy[1] + self.h*2))

            else:  # upgrade hovered
                name = subt_font.render(str(self.hovered[3][1]).capitalize(), True, (200, 200, 200))
                price = font.render(str(self.hovered[3][0]), True, L_GRAY)
                display.blit(price, (self.info_rect.centerx, self.info_rect.top))
                display.blit(name, self.m_xy)