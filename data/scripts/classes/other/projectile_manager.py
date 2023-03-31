import os

import pygame


class ProjectileManager:
    def __init__(self):
        self.projectiles = []
        self.sfx = {}
        for sf in os.listdir('data/sounds/sfx/projectiles'):
            s = pygame.mixer.Sound(f'data/sounds/sfx/projectiles/{sf}')
            img_name = sf.split('.')[0]
            self.sfx[img_name] = s

    def draw(self, display):
        for proj in self.projectiles:
            proj.draw(display)

    def update(self, terrain, scroll, enemies, water, player):
        for proj in self.projectiles:
            proj.update(terrain, enemies, water, player, self.sfx)
