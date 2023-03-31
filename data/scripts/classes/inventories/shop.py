import os

from data.scripts.core_functions import draw_rect_alpha, distance
from data.variables import *
import pygame

font = pygame.font.Font('data/fonts/minecraft_font.ttf', INV_FONT_SIZE)
imgs_dir = 'data/imgs/block_previews'
price_types_dir = 'data/imgs/price_types'


class Shop:
    def __init__(self, sortiment):

        self.rows = len(shop_sortiment)
        self.cols = len(shop_sortiment[0])
        scale = int(TILE_SIZE * 0.75)

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

        self.sortiment = sortiment
        self.contents = sortiment
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

    def on_shop_click(self, hotbar, inventory, effects, player):

        if inventory.selection is None:  # get selection if possible
            if self.selected_slot is not None:  # if a slot in *** shop *** is selected
                sel_col = self.selected_slot[0]
                sel_row = self.selected_slot[1]
                item = self.contents[sel_row - 1][sel_col].copy()

                if item != []:  # checks if the slot is not empty
                    if effects.stats['money'][item[2][1]][1] >= item[2][0]:
                        effects.stats['money'][item[2][1]][1] -= item[2][0]
                        if item[0] in ARMOR:
                            if item[3][0] == 'chest':
                                if item[0] == 'wings':
                                    player.wings = True
                                else:
                                    player.wings = False
                            if item[3][0] == 'helmet':
                                player.fog = False if item[0] in ('vision_helmet', 'astro_helmet') else True

                            if item[3][0] == 'boots':
                                if player.champ != 'sivir':
                                    player.no_fall_dmg = True if item[0] == 'jump_boots' else False
                                effects.stats['effects']['speed'][4][1] = item[3][2]
                                effects.stats['effects']['jump_height'][4][1] = item[3][3]
                            effects.stats['armor'][item[3][0]][0] = item[0]  # icon (visual)
                            effects.stats['armor'][item[3][0]][1] = item[0].capitalize()  # item name (visual)
                            effects.stats['armor'][item[3][0]][3] = item[3][1]  # prot from item
                        else:
                            inventory.selection = item  # buys item and ads it to inventory sel
                            if inventory.shift:
                                if not inventory.shift_to_hb(inventory.selection, hotbar) == 0:
                                    inventory.selection = None

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
            self.hovered_hotbar_slot = None

    def get_hovered(self):
        if self.selected_slot is not None:
            sel_col = self.selected_slot[0]
            sel_row = self.selected_slot[1]

            item = self.contents[sel_row - 1][sel_col].copy()
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

                        if n[1] > 1:
                            font_render = font.render(str(n[1]), True, (200, 200, 200))
                            font_centering_rect = font_render.get_rect()
                            font_centering_rect.bottomright = centering_rect.bottomright
                            display.blit(font_render, font_centering_rect.topleft)

                        price_render = font.render(str(n[2][0]), True, (200, 200, 200))
                        price_render_rect = price_render.get_rect()
                        price_render_rect.topleft = centering_rect.topleft
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
        pass





