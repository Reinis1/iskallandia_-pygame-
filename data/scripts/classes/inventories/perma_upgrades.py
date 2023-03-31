import os

from data.scripts.core_functions import draw_rect_alpha
from data.variables import *
import pygame

font = pygame.font.Font('data/fonts/minecraft_font.ttf', 12)
imgs_dir = 'data/imgs/block_previews'
price_types_dir = 'data/imgs/price_types'


class Upgrades:
    def __init__(self):

        self.rows = len(shop_sortiment)
        self.cols = len(shop_sortiment[0])
        scale = 32

        self.open = False

        self.width = self.cols * scale  # in real screen pixels
        self.height = self.rows * scale
        self.slot_width = scale
        self.slot_height = scale
        self.x = WINDOW_SIZE[0] // 2 - self.width // 2

        self.y = (WINDOW_SIZE[1] // 2 - self.height // 2) - (WINDOW_SIZE[1]//6)
        self.selected_slot = (1, 1)

        self.base_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.inventory_rects = []
        self.row_y = self.y

        self.sortiment = upgrades_sortiment
        self.contents = upgrades_sortiment
        self.selection = None

        self.m_xy = (0, 0)

        self.i = 1

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

    def on_shop_click(self, inventory, effects):
        if inventory.selection is None:  # get selection if possible
            if self.selected_slot is not None:  # if a slot in *** shop *** is selected
                sel_col = self.selected_slot[0]
                sel_row = self.selected_slot[1]
                try:
                    item = self.contents[sel_row - 1][sel_col]

                    if item != []:  # checks if the slot is not empty
                        if effects.stats['money'][item[2][1]][1] >= item[2][0]:  # checks money
                            if self.contents[sel_row-1][sel_col][1] < 4:  # checks if the upgrade level is below max (4)
                                effects.stats['money'][item[2][1]][1] -= item[2][0]  # removes money
                                # effects.stats[item[3][0]][item[3][1]][4] += 1  # adds 1 upgrade level to effect class
                                effects.stats[item[3][0]][item[3][1]][3] += item[3][2]  # adds the effect value to effects
                                effects.stats[item[3][0]][item[3][1]][4] += 1  # adds an actual level to effects for bliting correct color
                                self.contents[sel_row-1][sel_col][1] += 1  # adds the visual level to self.contents (bliting)
                                self.contents[sel_row-1][sel_col][2][0] *= 2
                except KeyError:
                    pass
                            # increeses price ^ (visual and factual)

    def get_selected_slot(self, mx, my):
        if self.open:
            for row_index, row in enumerate(self.inventory_rects):
                for i, l in row.items():
                    if l.collidepoint(mx, my):
                        self.selected_slot = (i, row_index + 1)
                        return
                    self.selected_slot = None

        else:
            self.selected_slot = None

    def get_hovered(self):
        if self.selected_slot is not None:
            sel_col = self.selected_slot[0]
            sel_row = self.selected_slot[1]
            try:
                item = self.contents[sel_row - 1][sel_col].copy()
            except (IndexError, KeyError):
                return None
            if item is not None and item != []:
                return item
            else: return None
        else:
            return None

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

            for row, slot_contents in enumerate(self.contents):
                for i, n in slot_contents.items():  # i = Number, n = rectangle
                    if n != None:
                        centering_rect = self.block_preview_imgs[n[0]].get_rect()
                        centering_rect.center = self.inventory_rects[row][i].center
                        display.blit(self.block_preview_imgs[n[0]], centering_rect.topleft)
                        if n[1] == 4:
                            font_render = font.render('MAX', True, (30, 30, 30))
                        elif n[1] > 1:
                            font_render = font.render(str(n[1]), True, (1, 1, 1))
                        else:
                            font_render = font.render('', True, (200, 200, 200))
                        font_centering_rect = font_render.get_rect()
                        font_centering_rect.bottomright = centering_rect.bottomright
                        display.blit(font_render, font_centering_rect.topleft)

                        price_render = font.render(str(n[2][0]), True, (200, 200, 200))
                        price_render_rect = price_render.get_rect()
                        price_render_rect.midtop = centering_rect.topleft
                        display.blit(price_render, price_render_rect.topleft)

                        display.blit(self.price_types[n[2][1]], centering_rect.midtop)

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

    def update(self, hotbar):
        self.contents = shop_sortiment
        self.contents[1][1] = ['grass', 1, [1, 'iron']]
        # watch(self.inventory_contents)