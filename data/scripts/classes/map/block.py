import pygame
import os

from data.variables import *
pygame.init()
pygame.display.set_mode()

imgs_dir = 'data/imgs/blocks'

block_imgs = {}
for img in os.listdir(imgs_dir):
	loaded_img = pygame.image.load(imgs_dir + '/' + img).convert_alpha()
	loaded_img = pygame.transform.scale(loaded_img, (TILE_SIZE, TILE_SIZE))
	img_name = img.split('.')[0]
	block_imgs[img_name] = loaded_img


class Block:
	def __init__(self, pos, block_type, default=None, gen=None, save=False, animated=None):
		self.save = save
		self.pos = pos
		self.type = block_type
		self.x = pos[0]
		self.y = pos[1]
		self.coords = (self.x//TILE_SIZE, self.y//TILE_SIZE)
		self.chunk = (self.coords[0] >> 3, self.coords[1] >> 3)

		self.rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)

		self.gen = gen
		try:
			self.hardness = BLOCK_HARDNESS[self.type]
		except KeyError:
			self.hardness = 100

		self.hp = BLOCK_HP * self.hardness
		self.animate = animated
		self.anima_counter = 1
		self.in_reach = False
		if default is not None:
			self.default = default
		else:
			self.default = 'air'

	@property
	def img(self):
		if self.type == 'air':
			self.animate = None
		if self.animate:
			if self.anima_counter < self.animate:
				self.anima_counter += 1/FRAME_RATE*8
			else:
				self.anima_counter = 1
			return block_imgs[f'{self.type}{int(self.anima_counter)}']

		hp = (self.hp//self.hardness) + 1
		try:
			img = block_imgs[f'{self.type}{hp}']
		except KeyError:
			# self.type = 'air'
			img = block_imgs[f'{self.type}']

		return img

	def get_scrolled_rect(self, scroll):
		rect = pygame.Rect(self.x - scroll[0], self.y - scroll[1], TILE_SIZE, TILE_SIZE)
		return rect

	def get_scrolled_pos(self, scroll):
		pos = (self.x - scroll[0], self.y - scroll[1])
		return pos

	def reset(self):
		self.type = self.default
		