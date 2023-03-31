import pygame
from data.variables import *

import numpy
from scipy.interpolate import interp1d
from random import randrange

Vector = pygame.Vector2

SMOOTH = True  # uses numpy + scipy

font = pygame.font.SysFont('consolas', 25)
s = pygame.Surface((RENDER_SIZE[0], RENDER_SIZE[1] * 2), pygame.SRCALPHA).convert_alpha()


def map_to_range(value, from_x, from_y, to_x, to_y):
    return value * (to_y - to_x) / (from_y - from_x)


class WaterSpring:
    def __init__(self, x=0, target_height=None):
        if not target_height:
            self.target_height = RENDER_SIZE[1] // 2
        else:
            self.target_height = target_height
        self.dampening = DAMPENING  # adjust accordingly in variables file
        self.tension = TENSION
        self.height = self.target_height
        self.vel = 0
        self.x = x
        self.tex = 0
        self.circle = (randrange(1, 254), randrange(1, 254), randrange(1, 254))

    def update(self):
        dh = self.target_height - self.height
        if abs(dh) < 0.01:
            self.height = self.target_height
        self.vel += self.tension * dh - self.vel * self.dampening
        self.height += self.vel
        self.height += 1

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, self.circle, (self.x-scroll[0], self.height), 3)


class Wave:
    def __init__(self):
        self.tex = 0
        diff = WAVE_LENGTH
        self.springs = [WaterSpring(x=i * diff + 0) for i in range(RENDER_SIZE[0] // diff)]
        self.points = []
        self.diff = WAVE_LENGTH

    def get_spring_index_for_x_pos(self, x):
        return int(x // self.diff)

    def get_target_height(self):
        return self.springs[0].target_height

    def set_target_height(self, height):
        for i in self.springs:
            i.target_height = height

    def update(self, hitboxes, particle_m):
        if scroll[1] > VOID_Y-RENDER_SIZE[1]:
            if self.springs[-1].x-WAVE_LENGTH < RENDER_SIZE[0] + scroll[0]:
                self.springs.append(WaterSpring(x=self.springs[-1].x + WAVE_LENGTH))
            if self.springs[-1].x + WAVE_LENGTH > RENDER_SIZE[0]-500 + scroll[0]:
                self.springs.pop(-1)

            if self.springs[0].x+ WAVE_LENGTH > scroll[0]:
                self.springs.insert(0, WaterSpring(self.springs[0].x - WAVE_LENGTH))
            if self.springs[0].x-WAVE_LENGTH < scroll[0]:
                self.springs.pop(0)

            for i in self.springs:
                i.update()
            self.points = [Vector(i.x, i.height) for i in self.springs]
            if GPU:
                self.points = get_curve(self.points)
            self.spread_wave()
            self.points.extend([Vector(RENDER_SIZE[0], RENDER_SIZE[1] * 2), Vector(0, RENDER_SIZE[1] * 2)])
            self.draw_water(s, hitboxes)

    def draw_water(self, surf: pygame.Surface, hitbox):
        surf.fill((0,0,0,0))
        if hitbox:
            for i in self.springs:
                i.draw(surf)
        self.points[-1][0] = self.points[0][0]
        self.points[-2][0] = self.points[-3][0]
        # self.points[-2][0] = self.points[0][0]
        pygame.draw.polygon(surf, (51, 204, 51, 95), [(i.x-scroll[0], i.y) for i in self.points])

    def draw(self, screen):
        if scroll[1] > VOID_Y-RENDER_SIZE[1]:
            self.draw_line(screen)
            y = VOID_Y - scroll[1] - RENDER_SIZE[1] // 2
            self.tex += 1
            screen.blit(s, (0, y))


    def draw_line(self, surf: pygame.Surface):
        pygame.draw.lines(surf, 'green', False, [(pt.x - scroll[0], pt.y - scroll[1] + VOID_Y - RENDER_SIZE[1] // 2) for pt in self.points[:-2]], 5)

    def spread_wave(self):
        spread = 0.05
        for i in range(len(self.springs)):
            if i > 0:
                self.springs[i - 1].vel += spread * (self.springs[i].height - self.springs[i - 1].height)
            try:
                self.springs[i + 1].vel += spread * (self.springs[i].height - self.springs[i + 1].height)
            except IndexError:
                pass

    def splash(self, index, vel):
        try:
            self.springs[index].vel -= vel
        except IndexError:
            pass


def get_curve(points):
    x_new = numpy.arange(points[0].x, points[-1].x, 1)
    x = numpy.array([i.x for i in points[:-1]])
    y = numpy.array([i.y for i in points[:-1]])
    f = interp1d(x, y, kind='cubic', fill_value='extrapolate')
    y_new = f(x_new)
    x1 = list(x_new)
    y1 = list(y_new)
    points = [Vector(x1[i], y1[i]) for i in range(len(x1))]
    return points
