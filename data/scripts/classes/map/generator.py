import os

import pygame

from data.variables import *


class Generator:
    def __init__(self, block, type_):
        self.block = block
        self.type_ = type_
        self.item = 5
        self.generating_speed = GENS[self.type_][0] / 3600  # items / min
        self.counter = 0
        self.max_items = GENS[self.type_][1]
        self.sfx = {}

        for sf in os.listdir('data/sounds/sfx/gens'):
            sfx = pygame.mixer.Sound(f'data/sounds/sfx/gens/{sf}')
            img_name = sf.split('.')[0]
            self.sfx[img_name] = sfx

    def pick_up_items(self, terrain, player, effect):
        try:
            if terrain.map[0][self.block.coords].type != 'air':
                if self.item == self.max_items:
                    terrain.map[0][self.block.coords].type = f'{self.type_}_gen_top3'
                elif self.item > self.max_items/2:
                    terrain.map[0][self.block.coords].type = f'{self.type_}_gen_top2'
                elif self.item > 0:
                    terrain.map[0][self.block.coords].type = f'{self.type_}_gen_top1'
                else:
                    terrain.map[0][self.block.coords].type = 'block'

                if player.rect.colliderect(self.block.rect):
                    if self.item > 0:
                        effect.stats['money'][self.type_][1] += self.item
                        self.sfx['iron'].play()
                        self.item = 0
        except KeyError:
            pass

    def update(self, terrain, player, effect):
        self.pick_up_items(terrain, player, effect)

        if self.item < self.max_items:
            self.counter += self.generating_speed
            if self.type_ == 'iron':
                self.counter += self.generating_speed * effect.stats['base']['gen'][4]
            if self.counter > 1:
                self.item += 1
                self.counter = 0
