import pygame
from data.variables import *
import os

imgs_dir = 'data/imgs/block_previews'

font = pygame.font.Font('data/fonts/minecraft_font.ttf', 6)


class Effect:
    def __init__(self):
        self.player = None
        self.stats = effects
        self.x = WINDOW_SIZE[0] - (TILE_SIZE + 20)
        self.y = TILE_SIZE + 5
        self.slot_rects = {}
        self.y_spacing = 0
        self.y_spacing_money = 0
        hsize = TILE_SIZE // 2
        self.status_effects_rects = {}

        for key, type_ in self.stats['money'].items():
            self.y_spacing_money += 1
            rect = pygame.Rect(WINDOW_SIZE[0] - hsize * self.y_spacing_money,
                               WINDOW_SIZE[1] - (hsize + 12),
                               hsize, hsize)
            self.slot_rects[key] = rect

        for i, item in enumerate(STATUS_EFFECTS):
            if item is not None:
                self.y_spacing += 0.4
                rect = pygame.Rect(5, self.y * self.y_spacing, hsize, hsize)
                self.status_effects_rects[i] = rect
            else:
                self.y_spacing += 0.2

        for key, type_ in self.stats['armor'].items():
            self.y_spacing += 0.6
            rect = pygame.Rect(WINDOW_SIZE[0]-TILE_SIZE+16, (self.y * self.y_spacing)-200, hsize, hsize)
            self.slot_rects[key] = rect

        self.block_preview_imgs = {}
        for img in os.listdir(imgs_dir):
            loaded_img = pygame.image.load(imgs_dir + '/' + img).convert_alpha()
            loaded_img = pygame.transform.scale(loaded_img, (hsize - TILE_SIZE//10, hsize - TILE_SIZE//10))
            img_name = img.split('.')[0]
            self.block_preview_imgs[img_name] = loaded_img

    def load_player_stats(self, champ):
        self.stats = {'money': {'iron': ['iron', 4, WHITE],
'gold': ['gold', 0, WHITE],
'diamond': ['diamond', 0, WHITE],
'emerald': ['emerald', 0, WHITE], },

'effects': {'speed': ['speed_boots', 'Speed', (100, 100, 100), 0, [PLAYER_STATS[champ]['speed'], 0, 0]],
            'jump_height': ['jump_boots', 'Jump height', (100, 100, 100), 0, [PLAYER_STATS[champ]['jump_h'], 0, 0]]},

'off': {'sharp': ['boots', '  Sharpness', (100, 100, 100), PLAYER_STATS[champ]['sharp'], 0],
        'haste': ['boots', '  Mining haste', (100, 100, 100), PLAYER_STATS[champ]['haste'], 0],},

'def': {'prot': ['prot', '  Protection', (20, 120, 20), PLAYER_STATS[champ]['protection'], 0],  # (last is level)
        'tenacity': ['boots', '  Tenacity', (20, 20, 120), PLAYER_STATS[champ]['tenacity'], 0]},

'armor': {'helmet': ['empty_helmet', ' Helmet', (100, 100, 100), 0, 0],
        'chest': ['empty_chestplate', ' Chestplate', (100, 100, 100), 0, 0],
        'boots': ['empty_boots', ' Boots', (100, 100, 100), 0, 0]},

'debuffs': {'slow': ['boots', '  Enemy slowness', (100, 100, 100), 0, 0],
        'drake_debuff': ['boots', '  Drake debuff', (100, 100, 100), 0, 0],
        'trap': ['boots', '  Trap', (100, 100, 100), 0, 0]},

'base': {'speed': ['speed_boots', '  Speed boost', (100, 100, 100), 0, 0],
        'gen': ['gen', '  Base gen speed', (100, 100, 100), 1, 0, 0],
        'heal_pool': ['  Heal pool', '  Heal pool', (100, 100, 100), 0, 0]},

'util': {'base_time': ['boots', '  Base timer', (100, 100, 100), 0, 0],
        'drake_debuff': ['boots', 'normal', (100, 100, 100), 0, 0],
}}

    def update(self, player):
        self.player = player

    def draw(self, display):
        self.player.draw_bars(display)
        for i, item in enumerate(STATUS_EFFECTS):
            if item is not None:
                centering_rect = self.block_preview_imgs[item[1]].get_rect()
                centering_rect.center = self.status_effects_rects[i].center
                display.blit(self.block_preview_imgs[item[1]], centering_rect.topleft)

                value = self.stats[item[0]][item[1]]
                color = tuple([x + 40 * value[4] for x in DEFAULT_P_COLOR]) if value[3] > 0 else DEFAULT_P_COLOR

                font_render = font.render(f'  {value[3]:.0%}', False, color)
                font_centering_rect = font_render.get_rect()
                font_centering_rect.bottomleft = centering_rect.bottomright
                display.blit(font_render, font_centering_rect.topleft)

                value = self.stats[item[0]][item[1]]
                font_render = font.render(f'{value[1]}', False, value[2])
                font_centering_rect = font_render.get_rect()
                font_centering_rect.topleft = centering_rect.topright
                display.blit(font_render, font_centering_rect.topleft)

        for key, effect in self.stats['armor'].items():
            if effect != []:
                centering_rect = self.block_preview_imgs[effect[0]].get_rect()
                centering_rect.center = self.slot_rects[key].center
                display.blit(self.block_preview_imgs[effect[0]], centering_rect.topleft)

        for key, effect in self.stats['money'].items():
            if effect != []:
                centering_rect = self.block_preview_imgs[effect[0]].get_rect()
                centering_rect.center = self.slot_rects[key].center
                display.blit(self.block_preview_imgs[effect[0]], centering_rect.topleft)

                font_render = font.render(str(effect[1]), True, effect[2])
                font_centering_rect = font_render.get_rect()
                font_centering_rect.bottomright = centering_rect.bottomright
                display.blit(font_render, font_centering_rect.topleft)
