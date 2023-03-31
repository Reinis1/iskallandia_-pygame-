import pygame
import random
import os

from data.scripts.classes.other.projectile import Projectile
from data.scripts.core_functions import move, distance
from data.variables import *
from data.scripts.classes.map.generator import *

''''
spawn()
'''


class Enemy:
    def __init__(self, start_pos, width, height, type_, respawn_time, hp):
        self.start_pos = start_pos
        self.in_void = False
        self.in_attack_range = False
        self.width = width
        self.height = height
        self.rect = pygame.Rect(start_pos[0], start_pos[1], width, height)
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
        self.current_chunk = (0, 0)
        self.unloaded = False
        self.type = type_
        self.hp = hp

        self.respawn_timer = respawn_time
        self.alive = False

        self.current_animation = 'walk'
        self.animations = self.load_animations(f'data\imgs\enemies\{type_}')
        self.animation_counter = 0
        self.animation_flip = False
        self.halt = False
        self.cooldown = FRAME_RATE
        self.font = pygame.font.Font('data/fonts/minecraft_font.ttf', 8)

    def load_animations(self, dir):
        animation_dict = {}
        for animation in os.listdir(dir):
            frame_list = []
            for frame in os.listdir(dir + '/' + animation):
                img = pygame.image.load(dir + '/' + animation + '/' + frame).convert_alpha()
                img = pygame.transform.scale(img, (self.width, self.height))
                frame_list.append(img)
            animation_dict[animation] = frame_list

        return animation_dict

    def respawn(self):
        self.alive = True
        self.hp = 16
        self.current_chunk = (self.start_pos[0] // CHUNK_SIZE, self.start_pos[1] // CHUNK_SIZE)
        self.rect.x = self.start_pos[0]
        self.rect.y = self.start_pos[1]


class Warwick(Enemy):

    def __init__(self, start_pos, sub_type):
        super().__init__(start_pos, TILE_SIZE, TILE_SIZE, sub_type, 1, 16)
        self.jump_height = ENEMIES[self.type]['jump_h']
        self.vel = ENEMIES[self.type]['speed']
        self.start_pos = start_pos

        self.attack_speed = 1

        self.jumping = False
        self.moving_right = False
        self.moving_left = False
        self.movement = [0, 0]

        self.breaking_block = False
        self.breaking_speed = 0

        self.collision_types = None
        self.tile_rects = None

        self.knocback = [0, 0]

        self.sfx = {}
        for sf in os.listdir('data/sounds/sfx/enemies/warwick'):
            sfx = pygame.mixer.Sound(f'data/sounds/sfx/enemies/warwick/{sf}')
            img_name = sf.split('.')[0]
            self.sfx[img_name] = sfx

    def hit(self, hp):
        self.sfx['hurt'].play()
        self.hp -= hp

    def move(self, terrain, effects, in_base):
        self.tile_rects = terrain.tile_rects

        self.rect, self.collision_types, self.hit_list = move(self.rect, self.tile_rects, (
            self.movement[0] + self.knocback[0], self.movement[1] - self.knocback[1]))

        if self.collision_types['bottom'] and not self.jumping:
            self.movement[1] = 1

        if not self.collision_types['bottom']:
            self.jumping = False
            self.movement[1] += GRAVITY_STRENGTH

        if self.collision_types['top']:
            self.movement[1] = 1

        if self.moving_right:
            self.movement[0] = self.vel + self.vel*effects['slow'][3]
            if in_base:
                self.movement[0] /= effects['trap'][3]
            self.current_animation = 'walk'

        if self.moving_left:
            self.movement[0] = -(self.vel + self.vel*effects['slow'][3])
            if in_base:
                self.movement[0] /= effects['trap'][3]
            self.current_animation = 'walk'

        if self.jumping and self.collision_types['bottom']:
            self.movement[1] = -self.jump_height
            self.jumping = False

        if not self.moving_left and not self.moving_right:
            self.movement[0] = 0

        if self.movement[1] > 2:
            if self.in_void:
                self.movement[1] = 2

    def do_attack_move(self, player, map, enemy_m):
        dx = player.coords[0] - self.coords[0]
        dy = player.coords[1] - self.coords[1]
        if abs(dx) >= abs(dy):
            self.attack_move_x(player, map)
        else:
            self.attack_move_x(player, map)

    def attack_move_y(self, player, map):
        pass

    def attack_move_x(self, player, map):
        if not self.in_attack_range:
            try:
                if self.rect.x < player.rect.x:  # player is on the right

                    self.moving_right = True  # case 1 (flat)
                    self.moving_left = False
                    if not self.halt:
                        self.current_animation = 'walk'
                    self.animation_flip = False

                    if map[(self.coords[0] + 1, self.coords[1])].type != 'air':  # case 1 obstacle
                        self.jumping = True

                    elif map[(self.coords[0] + 1, self.coords[1] + 1)].type == 'air':
                        if map[(self.coords[0] + 2, self.coords[1] + 1)].type == 'air':
                            if map[(self.coords[0] + 2, self.coords[1] + 2)].type == 'air':
                                self.moving_right = False
                        else:
                            self.jumping = True
                            self.halt = True
                            self.animation_counter = 0
                            self.current_animation = 'jump'

                else:
                    self.moving_right = False  # case 1 (flat)
                    self.moving_left = True
                    self.animation_flip = True
                    if not self.halt:
                        self.current_animation = 'walk'

                    if map[(self.coords[0] - 1, self.coords[1])].type != 'air':  # case 1 obstacle
                        self.jumping = True
                        self.halt = True
                        self.animation_counter = 0
                        self.current_animation = 'jump'

                    elif map[(self.coords[0] - 1, self.coords[1] + 1)].type == 'air':
                        if map[(self.coords[0] - 2, self.coords[1] + 1)].type == 'air':
                            if map[(self.coords[0] + 2, self.coords[1] + 2)].type == 'air':
                                self.moving_left = False
                        else:
                            self.jumping = True
                            self.halt = True
                            self.animation_counter = 0
                            self.current_animation = 'jump'

                self.unloaded = False

            except KeyError:
                self.unloaded = True

        else:
            self.moving_right = False
            self.moving_left = False
            if not self.halt:
                self.current_animation = 'bite'

    def check_attack_range(self, player):
        if distance(self.coords, player.coords) <= ENEMIES['warwick']['attack_range']:
            self.in_attack_range = True
        else:
            self.in_attack_range = False

    def draw(self, display):
        if self.animation_counter // 7 < len(self.animations[self.current_animation]):
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        else:
            self.animation_counter = 0
            self.halt = False
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        self.animation_counter += PLAYER_ANIMATION_SPEED*3

        current_img = pygame.transform.flip(current_img, self.animation_flip, False)

        scrolled_pos = (self.rect.centerx - scroll[0]-self.width//2, self.rect.y - scroll[1] + 3)
        display.blit(current_img, scrolled_pos)

        try:
            hp_string = f'hp: {self.hp:.1f}'
        except ValueError:
            hp_string = f'hp: {self.hp}'
        font_render = self.font.render(hp_string, True, (1, 1, 1))
        display.blit(font_render, scrolled_pos)

    def update(self, terrain, player, water, proj_m, enemy_m, particle_m, effects, in_base, menu):
        self.check_attack_range(player)
        if self.alive:
            if in_base:
                self.hp -= effects['trap'][3]/FRAME_RATE
            if self.hp <= 0:
                self.alive = False
                self.sfx['death'].play()
                enemy_m.enemies.remove(self)
        if not self.unloaded:
            if random.randint(0, FRAME_RATE*4) == 1:
                self.sfx[f'idle{random.randint(1, 3)}'].play()
            if random.randint(1, FRAME_RATE // 4) == 1:
                for enemy in enemy_m.enemies:
                    if self.rect.colliderect(enemy.rect):
                        self.movement[0] += random.randrange(-5, 5)
                        break

            self.move(terrain, effects, in_base)
            self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
            if self.in_attack_range:
                if self.cooldown < 0:
                    player.hit(ENEMIES[self.type]['ad'])
                    self.sfx['attack'].play()
                    self.cooldown = FRAME_RATE
                else:
                    self.cooldown -= random.randrange(0, 2)
            else:
                self.cooldown -= random.randrange(0, 2)
        else:
            self.movement = [0, 0]

        self.do_attack_move(player, terrain.map[0], enemy_m)

        if self.rect.bottom > VOID_Y:
            self.in_void = True
            self.hp -= 5 * 1 / FRAME_RATE
            loc = (self.rect.centerx - scroll[0]) // WAVE_LENGTH
            water.splash(loc, -3)
        else:
            self.in_void = False

        if self.knocback[0] > 0:
            self.knocback[0] -= 0.5
        elif self.knocback[0] < 0:
            self.knocback[0] += 0.5

        if self.knocback[1] > 0:
            self.knocback[1] -= 0.5
        elif self.knocback[1] < 0:
            self.knocback[1] += 0.5


class DarkVex:  # attacks bed
    def __init__(self, start_pos, enemy_m):
        self.in_block = False
        self.reach_distance = REACH
        self.rect = pygame.Rect(start_pos[0], start_pos[1], TILE_SIZE // 2, TILE_SIZE // 2)
        self.velocity = [0, 0]
        enemy_m.enemies.append(self)
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
        self.width = TILE_SIZE // 2
        self.height = TILE_SIZE // 2
        self.hp = 20
        self.speed = 2
        self.unloaded = False

    def move(self, terrain, player):
        try:
            bed = terrain.map[0][(terrain.player_spawnpoint[0] // TILE_SIZE, terrain.player_spawnpoint[1] // TILE_SIZE)]
            self.unloaded = False
            for block_rect in terrain.tile_rects:
                if self.rect.colliderect(block_rect):
                    self.in_block = True
                    block_coords = (block_rect.x // TILE_SIZE, block_rect.y // TILE_SIZE)
                    if terrain.map[0][block_coords].type == 'bed':
                        player.bed_hp -= 1
                    terrain.map[0][block_coords].hp -= 10
                    if terrain.map[0][block_coords].hp < 1:
                        terrain.map[0][block_coords].type = 'air'
                    break
                else:
                    self.in_block = False

            if self.in_block:
                pass
            else:
                self.speed = 1
                if (bed.coords[0] * TILE_SIZE) + TILE_SIZE // 2 > self.rect.centerx:
                    self.rect.x += self.speed
                else:
                    self.rect.x -= self.speed
                if bed.coords[1] * TILE_SIZE + 2 * TILE_SIZE + TILE_SIZE // 2 > self.rect.centery:
                    self.rect.y += self.speed
                else:
                    self.rect.y -= self.speed
        except KeyError:
            self.unloaded = True

    def update(self, terrain, player, water, proj_m, enemy_m):
        self.move(terrain, player)
        if self.hp < 1:
            enemy_m.enemies.remove(self)
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)

    def draw(self, screen):
        scrolled_pos = (self.rect.x - scroll[0], self.rect.y - scroll[1] + 3)


class Drake1:
    def __init__(self, start_pos, type_, enemy_m):
        self.animation_flip_y = False
        self.current_animation = 'fly'
        self.animation_flip = False
        self.animation_counter = 0

        self.stats = DRAKES[type_]
        self.end_y = 0
        self.end_x = 0
        self.in_block = False
        self.reach_distance = REACH
        self.rect = pygame.Rect(start_pos[0], start_pos[1], TILE_SIZE * 3, TILE_SIZE * 2)
        self.velocity = [0, 0]
        enemy_m.enemies.append(self)
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
        self.width = TILE_SIZE * 3
        self.height = TILE_SIZE * 2
        self.hp = self.stats['hp']
        self.purge = 2 * FRAME_RATE
        self.animations = self.load_animations(f'data/imgs/enemies/drakes/{type_}')
        self.font = pygame.font.Font('data/fonts/minecraft_font.ttf', 10)
        self.type = type_

        self.sfx = {}
        for sf in os.listdir('data/sounds/sfx/enemies/drake'):
            sfx = pygame.mixer.Sound(f'data/sounds/sfx/enemies/drake/{sf}')
            img_name = sf.split('.')[0]
            self.sfx[img_name] = sfx

        self.gen_move()

    def load_animations(self, dir):
        animation_dict = {}
        for animation in os.listdir(dir):
            frame_list = []
            for frame in os.listdir(dir + '/' + animation):
                img = pygame.image.load(dir + '/' + animation + '/' + frame).convert_alpha()
                img = pygame.transform.scale(img, (self.width, self.height))
                frame_list.append(img)
            animation_dict[animation] = frame_list

        return animation_dict

    def hit(self, hp):
        self.sfx['hurt'].play()
        self.hp -= hp

    def gen_move(self):
        self.end_x = random.randint(scroll[0], scroll[0] + WINDOW_SIZE[0])
        self.end_y = random.randint(scroll[1], scroll[1] + WINDOW_SIZE[1])
        self.velocity = [self.end_x - self.rect.centerx, self.end_y - self.rect.centery]
        self.animation_flip = True if self.velocity[0] < 0 else False

        magnitude = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.65

        self.velocity = [self.velocity[0] / magnitude * 10, self.velocity[1] / magnitude * 10]
        self.velocity[0] *= self.stats['speed']
        self.velocity[1] *= self.stats['speed']

    def move(self, terrain, player_rect):
        self.current_animation = 'up' if abs(self.velocity[1]) > abs(self.velocity[0] * 1.5) else 'fly'
        if self.current_animation == 'up':
            self.animation_flip_y = True if self.velocity[1] > 0 else False
        else:
            self.animation_flip_y = False

        for block_rect in terrain.tile_rects:
            if self.rect.colliderect(block_rect):
                self.in_block = True
                block_coords = (block_rect.x // TILE_SIZE, block_rect.y // TILE_SIZE)
                terrain.map[0][block_coords].hp -= self.stats['block_dmg']
                if terrain.map[0][block_coords].hp < 1:
                    terrain.remove_block(block=terrain.map[0][block_coords])
                break
            else:
                self.in_block = False
        self.rect.centerx += self.velocity[0]
        self.rect.centery += self.velocity[1]

    def shoot(self, player, proj_m, particle_m):
        proj_m.projectiles.append(Projectile(
            self.rect.center, (player.rect.centerx - scroll[0], player.rect.centery - scroll[1]),
            self.stats['proj'], proj_m, particle_m, shooter='enemy'))

    def update(self, terrain, player_rect, water, proj_m, enemy_m, particle_m, effects, in_base, menu):
        self.purge -= 1
        self.animation_flip_y = False
        self.current_animation = 'idle'
        if self.purge == FRAME_RATE//2 and self.stats['shoot']:
            if distance(player_rect.rect.center, self.rect.center) < (RENDER_DISTANCE+1) * CHUNK_SIZE * TILE_SIZE:
                self.shoot(player_rect, proj_m, particle_m)
        if self.purge > FRAME_RATE:
            self.move(terrain, player_rect)

        if self.purge < 0:
            self.purge = 8 * FRAME_RATE
            if distance(player_rect.rect.center, self.rect.center) < RENDER_DISTANCE*CHUNK_SIZE*TILE_SIZE:
                self.sfx['charge'].play()
            self.gen_move()

        if self.hp < 1:
            enemy_m.enemies.remove(self)
            self.sfx['death'].play()
            player_rect.drakes_killed += 1
            if self.type == 'elder':
                player_rect.victory = True
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)

        if self.rect.colliderect(player_rect.rect):
            ad = self.stats['ad']/FRAME_RATE
            player_rect.hit(ad - ad*effects['drake_debuff'][3], stun=False)
            player_rect.knocback[1] = random.randint(-3, -1)
            player_rect.knocback[0] = random.randint(-2, 2)

    def draw(self, screen):
        if self.animation_counter // 7 < len(self.animations[self.current_animation]):
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        else:
            self.animation_counter = 0
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        self.animation_counter += abs((self.velocity[0] + -self.velocity[1]) / 10)

        current_img = pygame.transform.flip(current_img, self.animation_flip, self.animation_flip_y)

        scrolled_pos = (self.rect.x - scroll[0], self.rect.y - scroll[1] + 3)
        screen.blit(current_img, scrolled_pos)
        try:
            hp_string = f'hp: {self.hp:.1f}'
        except ValueError:
            hp_string = f'hp: {self.hp}'
        font_render = self.font.render(hp_string, True, 'white')
        screen.blit(font_render, scrolled_pos)


class Vex(Enemy):  # attacks player
    def __init__(self, start_pos, sub_type):
        super().__init__(start_pos, TILE_SIZE//2, TILE_SIZE//2, sub_type, .4, 10)
        self.in_block = False
        self.reach_distance = REACH
        self.velocity = [0, 0]
        self.base_speed = ENEMIES[sub_type]['speed']
        self.speed = self.base_speed

        self.sfx = {}
        for sf in os.listdir('data/sounds/sfx/enemies/vex'):
            sfx = pygame.mixer.Sound(f'data/sounds/sfx/enemies/vex/{sf}')
            img_name = sf.split('.')[0]
            self.sfx[img_name] = sfx

    def move(self, terrain, player_rect, effects, in_base):
        for block_rect in terrain.tile_rects:
            if self.rect.colliderect(block_rect):
                self.in_block = True
                block_coords = (block_rect.x // TILE_SIZE, block_rect.y // TILE_SIZE)
                terrain.map[0][block_coords].hp -= 1
                if terrain.map[0][block_coords].hp < 1:
                    terrain.remove_block(block=terrain.map[0][block_coords])
                break
            else:
                self.in_block = False

        if self.in_block:
            self.speed += 0.2 # - (0.2 * effects['slow'][3])
            if player_rect.rect.centerx > self.rect.centerx:
                if self.speed > 1:
                    self.rect.x += self.speed
                    self.speed = 0
                    if not self.halt:
                        self.current_animation = 'walk'
            else:
                if self.speed > 1:
                    if not self.halt:
                        self.current_animation = 'walk'
                    self.animation_flip = True
                    self.rect.x -= self.speed
                    self.speed = 0

            if player_rect.rect.centery > self.rect.centery:
                self.rect.y += self.speed
            else:
                self.rect.y -= self.speed
        else:
            self.speed = self.base_speed
            self.speed -= self.speed * effects['slow'][3]
            if in_base:
                self.speed -= self.speed * effects['trap'][3]
            if player_rect.rect.centerx > self.rect.centerx:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed
            if player_rect.rect.centery > self.rect.centery:
                self.rect.y += self.speed
            else:
                self.rect.y -= self.speed

    def check_attack_range(self, player):
        if distance(self.rect.center, player.rect.center) <= ENEMIES['vex']['attack_range']:
            self.in_attack_range = True
        else:
            self.in_attack_range = False

    def update(self, terrain, player, water, proj_m, enemy_m, particle_m, effects, in_base, menu):
        if distance(self.coords, player.coords) < CHUNK_SIZE * RENDER_DISTANCE:
            self.check_attack_range(player)
            self.move(terrain, player, effects, in_base)
            if self.alive:
                if self.hp <= 0:
                    self.sfx['death'].play()
                    self.alive = False
                    enemy_m.enemies.remove(self)
            self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)

            if self.in_attack_range:
                if self.cooldown < 0:
                    player.hit(ENEMIES['vex']['ad'])
                    self.sfx['attack'].play()
                    self.cooldown = FRAME_RATE
                    self.halt = True
                    self.current_animation = 'bite'

            self.cooldown -= 1

            if random.randint(1, FRAME_RATE//4) == 1:
                self.rect.x += random.randrange(-1, 1)
                self.rect.y += random.randrange(-1, 1)

    def hit(self, hp):
        self.sfx['hurt'].play()
        self.hp -= hp

    def draw(self, screen):
        if self.animation_counter // 7 < len(self.animations[self.current_animation]):
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        else:
            self.animation_counter = 0
            self.halt = False
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        self.animation_counter += PLAYER_ANIMATION_SPEED*3

        current_img = pygame.transform.flip(current_img, self.animation_flip, False)

        scrolled_pos = (self.rect.centerx - scroll[0]-self.width//2, self.rect.y - scroll[1] + 3)
        screen.blit(current_img, scrolled_pos)

        try:
            hp_string = f'hp: {self.hp:.1f}'
        except ValueError:
            hp_string = f'hp: {self.hp}'
        font_render = self.font.render(hp_string, True, (1, 1, 1))
        screen.blit(font_render, scrolled_pos)

