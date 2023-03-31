import pygame
import numpy as np

from data.scripts.classes.map.block import Block
# from .tree import Tree
from data.variables import *
from data.scripts.classes.map.chunks import *


class BlockKeyError(Exception):
    pass


class Terrain:

    def __init__(self):
        self.buffer_frame = 0
        self.player_bed = None
        self.bed_added = False
        self.map = np.array([{}])
        self.bg_map = {}
        self.tile_rects = []
        self.placed_blocks = []
        self.loaded_chunks = []
        self.gens = []
        self.intractables = {'door': []}
        self.ladder_rect = []
        self.player_spawnpoint = (0, 0)
        self.beds = {'warwick': [], 'vex': [], 'i_warwick': [], 'i_vex': []}

        self.innit_starting_chunks(starting_chunks)

    def innit_starting_chunks(self, chunks):
        for chunk_pos_y, row_of_layouts in enumerate(chunks):
            for chunk_pos_x, chunk_layout in enumerate(row_of_layouts):
                if chunk_layout is not None:
                    for y, row in enumerate(chunk_layout):
                        for x, item in enumerate(row):

                            target_y = chunk_pos_y * CHUNK_SIZE + y
                            target_x = chunk_pos_x * CHUNK_SIZE + x
                            gen = None
                            animate = None
                            bg = 'air'
                            try:
                                block_type = BLOCK_KEYS[item][0]
                                bg = BLOCK_KEYS[item][1]
                            except KeyError as a:
                                raise BlockKeyError('Key not found') from a
                                # block_type = 'air'

                            if item == 'z':
                                gen = 'gold'
                            elif item == 'i':
                                gen = 'iron'
                            elif item == '|':
                                gen = 'emerald'
                            elif item == 'v':
                                gen = 'diamond'
                            elif item in ('Z', 'I', 'V', '1'):
                                animate = 4
                            elif item == 'd':
                                self.intractables['door'].append(
                                    Block((target_x * TILE_SIZE, target_y * TILE_SIZE), 'door'))
                            elif item == 'G':
                                self.intractables['door'].append(
                                    Block((target_x * TILE_SIZE, target_y * TILE_SIZE), 'door'))
                            elif item in ('l', 'm', 'n', 'o'):
                                self.ladder_rect.append(Block((target_x * TILE_SIZE, target_y * TILE_SIZE), 'ladder'))
                            elif item == 'B':
                                self.player_spawnpoint = (target_x * TILE_SIZE, (target_y - 2) * TILE_SIZE)
                                self.bed_added = False
                            elif item == 'W':
                                self.beds['warwick'].append(Block((target_x * TILE_SIZE, target_y * TILE_SIZE),
                                                                  block_type))
                            elif item == 'Q':
                                self.beds['i_warwick'].append(Block((target_x * TILE_SIZE, target_y * TILE_SIZE),
                                                                    block_type))
                            elif item == 'Y':
                                self.beds['i_vex'].append(Block((target_x * TILE_SIZE, target_y * TILE_SIZE),
                                                                block_type))
                            elif item == '%':
                                self.beds['vex'].append(Block((target_x * TILE_SIZE, target_y * TILE_SIZE),
                                                              block_type))
                            block = Block((target_x * TILE_SIZE, target_y * TILE_SIZE),
                                          block_type, gen=gen, animated=animate)
                            if gen is not None:
                                self.gens.append([block, gen])

                            self.placed_blocks.append(block)
                            self.bg_map[(target_x, target_y)] = Block((target_x * TILE_SIZE, target_y * TILE_SIZE), bg)

                            if not self.bed_added:
                                self.player_bed = block
                                self.bed_added = True

    def generate_chunk(self, x, y, chunk_data=air_c):
        # x and y values are for chunk x and y, not blocks
        if (x, y) not in [block.chunk for i, block in self.map[0].items()]:
            chunk_loaded = (x, y) in self.loaded_chunks
            for y_pos in range(CHUNK_SIZE):
                for x_pos in range(CHUNK_SIZE):

                    block_added = False

                    target_x = x * CHUNK_SIZE + x_pos
                    target_y = y * CHUNK_SIZE + y_pos

                    for block in list(self.placed_blocks):
                        if block.coords == (target_x, target_y):
                            self.map[0][block.coords] = block
                            block.save = True
                            self.placed_blocks.remove(block)
                            block_added = True

                    if not block_added:
                        tile_type = 'air'
                        block = Block((target_x * TILE_SIZE, target_y * TILE_SIZE), tile_type)
                        self.map[0][block.coords] = block

            if not chunk_loaded:
                self.loaded_chunks.append((x, y))
            self.buffer_frame = 3
            return True

    def unload_chunk(self, chunk_pos):
        for i, block in self.map[0].items():
            if block.chunk == chunk_pos:
                if block.save:
                    self.placed_blocks.append(block)
                del self.map[0][block.coords]

    def remove_block(self, block_pos=None, block=None):
        if not block:
            pos = (block_pos[0] // TILE_SIZE, block_pos[1] // TILE_SIZE)
            block = self.map[0][pos]
        else:
            pos = block.coords
        if 'gen_top' not in block.type:
            if block.type == 'gen':
                self.map[0][block.coords[0], block.coords[1]-1].type = 'air'
            if block.type == 'ladder':
                for ladder in self.ladder_rect:
                    if ladder.coords == pos:
                        self.ladder_rect.remove(ladder)

            self.map[0][block.coords].type = 'air'

    def add_block(self, block_pos, block_type):
        block_pos = tuple(val // TILE_SIZE for val in block_pos)
        if self.map[0][block_pos].type in BG_BLOCKS:
            self.map[0][block_pos].hardness = BLOCK_HARDNESS[block_type]
            self.map[0][block_pos].hp = BLOCK_HP * BLOCK_HARDNESS[block_type]
            self.map[0][block_pos].type = block_type
            if self.map[0][block_pos].type == 'ladder':
                self.ladder_rect.append(self.map[0][block_pos])
            self.placed_blocks.append(self.map[0][block_pos])
            return True

    def generate_hitbox(self):
        self.tile_rects = []
        for i, block in self.map[0].items():
            if block.type not in ('air', 'ladder', 'open_door', 'open_door_top', 'wall') \
                    and block.type not in BG_BLOCKS and block.gen is None:
                self.tile_rects.append(block.rect)

    def draw(self, display):
        for i, block in self.map[0].items():
            img = block.img
            try:
                bg_img = self.bg_map[block.coords].img
                display.blit(bg_img, block.get_scrolled_pos(scroll))
            except KeyError:
                pass
            display.blit(img, block.get_scrolled_pos(scroll))

            # if block.in_reach:
            #     block_rect = pygame.Rect(
            #         block.x - scroll[0],
            #         block.y - scroll[1],
            #         TILE_SIZE,
            #         TILE_SIZE
            #     )
            #     pygame.draw.rect(display, 'gray', block_rect, 1)

    def pre_generate_chunk(self, player):
        if self.buffer_frame > 0:
            self.buffer_frame -= 1
        else:
            for y in range(RENDER_DISTANCE):
                for x in range(RENDER_DISTANCE):
                    target_x = x + player.current_chunk[0] - RENDER_DISTANCE // 2
                    target_y = y + player.current_chunk[1] - RENDER_DISTANCE // 2
                    if self.generate_chunk(target_x, target_y):
                        return

    def update(self, player):
        self.generate_hitbox()
        self.pre_generate_chunk(player)
