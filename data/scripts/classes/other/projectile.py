import os

import pygame

from data.scripts.classes.other.particle_manager import Particles
from data.scripts.core_functions import distance
from data.variables import *


class Projectile:
    def __init__(self, start_pos, end_pos, type_, projectile_manager, particle_m, shooter=None):
        self.stats = PROJECTILE_TYPES[type_]
        self.type = type_
        self.rect = pygame.Rect(start_pos[0], start_pos[1], self.stats['size'], self.stats['size'])

        self.end_pos = end_pos
        self.start_pos = (start_pos[0] - scroll[0], start_pos[1] - scroll[1])
        self.velocity = 1
        self.projectiles = []
        self.penetrtion = self.stats['penetration']
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)

        self.x = start_pos[0]
        self.y = start_pos[1]
        self.remaining_range = self.stats['range']
        self.velocity = [self.end_pos[0] - self.start_pos[0], self.end_pos[1] - self.start_pos[1]]

        magnitude = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** self.stats['vel']

        self.velocity = [self.velocity[0] / magnitude * 10, self.velocity[1] / magnitude * 10]
        self.proj_m = projectile_manager

        self.proj_m.projectiles.append(self)

        self.block_rect = pygame.Rect(
            self.rect.x - scroll[0],
            self.rect.y - scroll[1],
            self.stats['size'],
            self.stats['size']
        )
        self.splash = True
        self.shooter = shooter
        self.particles = Particles(self.rect.center, y_dir="all", color=(40, 40, 40),
                                   radius=(1, self.stats['size']), particle_m=particle_m, vel=(2, 2), type_='proj',
                                   speed=1, shrink=1, turn='on', dir=None)
        self.explosion_p = Particles(self.rect.center, y_dir="all", color=(210, 150, 10),
                                     radius=(2, 2*self.stats['size']), particle_m=particle_m, vel=(20, 20),
                                     type_='explosion',
                                     speed=1, shrink=4, turn='off', dir='all', sparse=20)
        self.particle_m = particle_m
        self.proj_m.sfx[f'{self.type}_shoot'].play()

    def update(self, terrain, enemies, water, player, sfx):
        self.particles.pos = (self.rect.left+TILE_SIZE, self.rect.top-TILE_SIZE)

        self.coords = (self.rect.x//TILE_SIZE, self.rect.y//TILE_SIZE)
        if self.rect.y > VOID_Y and self.splash:
            water.splash((self.rect.centerx - scroll[0]) // WAVE_LENGTH, -10)
            self.splash = False
        if self.remaining_range > 0 and self.penetrtion > 0:
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]

            if self.shooter is None:
                for enemy in enemies:
                    if self.rect.colliderect(enemy.rect):
                        enemy.hp -= self.stats['ad']
                        self.penetrtion -= 1
            if self.shooter == 'enemy':
                if self.rect.colliderect(player.rect):
                    player.hit(self.stats['ad'], dmg='ad')
                    self.penetrtion -= 1

            for i, block in terrain.map[0].items():
                if block.type != 'air':
                    if self.rect.colliderect(block.rect):
                        if self.stats['blast_radius'] is None:
                            block.hp -= self.stats['block_dmg']
                            self.penetrtion -= 1
                            if block.hp <= 1:
                                if block.type == 'ladder':
                                    for ladder in terrain.ladder_rect:
                                        if ladder.coords == block.coords:
                                            terrain.ladder_rect.remove(ladder)
                                terrain.remove_block(block.pos)
                        else:
                            for key, block_ in terrain.map[0].items():
                                if (a := distance(block_.coords, self.coords)) < self.stats['blast_radius']:
                                    block_.hp -= int(self.stats['block_dmg']*8 / (2*a+1))
                                    if block_.hp <= 1:
                                        terrain.remove_block(block.pos, block_)
                            try:
                                self.proj_m.projectiles.remove(self)
                                self.particles.turn = 'off'
                                self.explosion_p.pos = (self.rect.left + TILE_SIZE, self.rect.top - TILE_SIZE)
                                self.explosion_p.turn = 'on'
                                self.particle_m.explosion_len = 15
                                sfx[f'{self.type}_explode'].play()
                            except ValueError:
                                pass

            self.block_rect = pygame.Rect(
                self.rect.x - scroll[0],
                self.rect.y - scroll[1],
                self.stats['size'],
                self.stats['size']
            )
            self.remaining_range -= 1
        else:
            self.proj_m.projectiles.remove(self)
            self.particles.turn = 'off'

    def draw(self, screen):
        if not self.rect.centerx <= scroll[0] + WINDOW_SIZE[0] // 8 or \
                self.rect.centerx >= scroll[0] + WINDOW_SIZE[0] - WINDOW_SIZE[0] // 16:
            pygame.draw.circle(screen, 'red', self.block_rect.center, self.stats['size'])



