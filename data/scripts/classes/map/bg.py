import pygame
import os
from ....variables import WINDOW_SIZE, scroll
from random import randint


class BackGround:
    def __init__(self):
        self.rects = []
        self.imgs = []
        for img in os.listdir('data/imgs/bg'):
            loaded_img = pygame.image.load(f'data/imgs/bg/{img}').convert_alpha()
            loaded_img = pygame.transform.scale(loaded_img, (WINDOW_SIZE[0], WINDOW_SIZE[1]))
            self.imgs.append([loaded_img, loaded_img.get_rect()])
        self.x = 0
        self.y = 0
        self.drift = 0

    def draw(self, display):
        self.drift += 0.05
        for i, img in enumerate(self.imgs):
            i += 1
            i /= 7
            drift = i * self.drift * 2
            if img[1].x + WINDOW_SIZE[0] + drift < scroll[0] * i:
                img[1].x += WINDOW_SIZE[0]
            if img[1].x + drift > scroll[0] * i:
                img[1].x += -WINDOW_SIZE[0]

            if img[1].y + WINDOW_SIZE[1] < scroll[1] * i:
                img[1].y += WINDOW_SIZE[1]
            if img[1].y > scroll[1] * i:
                img[1].y += -WINDOW_SIZE[1]

            display.blit(img[0], (int(-scroll[0] * i + img[1].x + drift),
                                  int(-scroll[1] * i + img[1].y)))
            display.blit(img[0], (int(-scroll[0] * i + img[1].x + WINDOW_SIZE[0] + drift ),
                                  int(-scroll[1] * i + img[1].y) + WINDOW_SIZE[1]))

            display.blit(img[0], (int(-scroll[0] * i + img[1].x + WINDOW_SIZE[0] + drift),
                                  int(-scroll[1] * i + img[1].y)))
            display.blit(img[0], (int(-scroll[0] * i + img[1].x + drift),
                                  int(-scroll[1] * i + img[1].y) + WINDOW_SIZE[1]))
