import pygame
import os
import json

from data.scripts.core_functions import move, distance
from data.variables import *
from data.scripts.classes.map.generator import *
from data.scripts.classes.other.projectile import Projectile

imgs_dir = 'data/imgs/block_previews'


class Player:
    def __init__(self, start_pos, width, height, vel, jump_height, terrain):
        self.jumps = 1
        self.champ = 'sealable'
        self.max_jumps = self.jumps
        self.in_base = False
        self.shop = None
        self.is_fall_dmg = False
        self.is_kb = False
        self.knocback = [0, 0]
        self.collision_types = {}
        self.hp_outline = pygame.Rect(120, 260, PLAYER_HP*5, 7)
        self.bed_hp_outline = pygame.Rect(275, 260, PLAYER_HP * 5, 7)
        self.flying = False
        self.animation_speed_multiplier = 0
        self.real_breaking = False
        self.breaking_angle = 0
        self.breaking_offset = 0
        self.air_time = AIR_TIME
        self.in_void = False
        self.on_ladder = False
        self.game_state = 'main_menu'
        self.current_drake = None

        self.width = width - TILE_SIZE*0.2
        self.height = height - TILE_SIZE*0.75
        self.vel = vel
        self.jump_height = jump_height
        self.reach_distance = REACH
        start_x, start_y = start_pos
        start_y += 2*TILE_SIZE
        start_x += TILE_SIZE
        self.start_pos = start_pos  # start_x, start_y
        self.hitboxes = False

        self.rect = pygame.Rect(start_pos[0], start_pos[1]+50, self.width, self.height)
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
        self.pixel_coords = (self.coords[0] * TILE_SIZE, self.coords[1] * TILE_SIZE)

        self.jumping = False
        self.moving_right = False
        self.moving_left = False
        self.movement = [.0, .0]
        self.selected_block = None
        self.climbing = False
        self.current_chunk = (0, 0)
        self.descent = False

        self.current_animation = 'idle'
        self.animations = self.load_animations('data/imgs/player/sealable')
        self.animation_counter = 0
        self.animation_flip = False
        self.halt = False
        self.halt_reason = ''

        self.breaking_block = False
        self.breaking_speed = 0
        self.centering_rect = pygame.image.load('data/imgs/block_previews/fl.png').convert_alpha().get_rect()
        self.hp = PLAYER_STATS[self.champ]['hp']
        self.font = pygame.font.Font('data/fonts/minecraft_font.ttf', 6)

        self.selected_enemy = None
        self.block_in_reach = []
        self.haste = 0
        self.fog = True

        self.scrolled_pos = (0, 0)
        self.projectiles = []
        self.m_xy = (0, 0)
        self.score = 0
        self.stats = {}
        self.sfx = {}
        self.walk_sfx = pygame.mixer.Channel(3)
        self.break_sfx = pygame.mixer.Channel(1)
        self.climbing_sfx = pygame.mixer.Channel(2)
        self.music_ch = pygame.mixer.Channel(4)
        self.block_preview_imgs = {}

        self.holding_item = None
        self.image = None
        self.base_time = BASE_TIME
        self.base_timer_max = self.base_time
        self.bed_hp = PLAYER_HP * 10
        self.bed = terrain.player_bed
        self.bed_destroyed = False
        self.standing_block = None

        self.delay = 0
        self.wings = WINGS
        wing_img = pygame.image.load('data/imgs/block_previews/player_wings.png').convert_alpha()
        self.wing_img = pygame.transform.scale(wing_img, (TILE_SIZE*2, TILE_SIZE*2))
        self.music = {}
        self.player_hitbox = self.player_hitbox = pygame.Rect(self.rect.x - scroll[0], self.rect.y - scroll[1],
                                                              self.width, self.height)
        self.stun_dur = 0
        self.slow_dur = 0
        self.slowed = False
        self.stunned = False
        self.tenacity = 0
        self.drakes_killed = 0
        self.last_frame = None
        self.victory = False

        for img in os.listdir(imgs_dir):
            loaded_img = pygame.image.load(imgs_dir + '/' + img).convert_alpha()
            loaded_img = pygame.transform.scale(loaded_img, (TILE_SIZE//2, TILE_SIZE//2))
            img_name = img.split('.')[0]
            self.block_preview_imgs[img_name] = loaded_img

        for sf in os.listdir('data/sounds/sfx/player'):
            sfx = pygame.mixer.Sound(f'data/sounds/sfx/player/{sf}')
            img_name = sf.split('.')[0]
            self.sfx[img_name] = sfx

        for sf in os.listdir('data/sounds/music/'):   #sound tracks (long innit time)
            sfx = pygame.mixer.Sound(f'data/sounds/music/{sf}')
            img_name = sf.split('.')[0]
            self.music[img_name] = sfx

        self.respawn()

    def load_player_moddel(self):
        self.animations = self.load_animations(f'data/imgs/player/{self.champ}')
        self.max_jumps = PLAYER_STATS[self.champ]['jumps']
        self.hp_outline = pygame.Rect(120, 260, PLAYER_STATS[self.champ]['hp'] * 5, 7)

    def hit(self, hp, dmg='ad', stun=True, dur=FRAME_RATE):  # (take damage)
        self.sfx['hurt'].play()
        self.halt = True
        self.current_animation = 'hurt'
        self.animation_counter = 1  # if self.animation_counter != 1 else 2
        if stun:
            self.stunned = stun
            self.stun_dur = dur - dur*self.tenacity

        if dmg == 'ad':
            armor_amount = 0
            hp /= 1 + self.stats['def']['prot'][3]
            for key in self.stats['armor'].keys():
                armor_amount += self.stats['armor'][key][3]
            hp /= 1 + armor_amount
        elif dmg == 'true':
            hp = hp
        self.hp -= hp

    def kb(self):
        self.movement[0] += self.knocback[0] - self.knocback[0] * self.tenacity
        self.movement[1] += self.knocback[1] - self.knocback[0] * self.tenacity
        self.is_kb = False
        if self.knocback[0] > 0:
            self.knocback[0] -= 0.5
            self.is_kb = True
        elif self.knocback[0] < 0:
            self.is_kb = True
            self.knocback[0] += 0.5

        if self.knocback[1] > 0:
            self.is_kb = True
            self.knocback[1] -= 0.5
        elif self.knocback[1] < 0:
            self.is_kb = True
            self.knocback[1] += 0.5

    def move(self, terrain):
        tile_rects = terrain.tile_rects
        if self.stunned:
            self.movement[0] = 0

        self.rect, self.collision_types, self.hit_list = move(self.rect, tile_rects, self.movement)

        if self.collision_types['bottom'] and not self.jumping and not self.climbing:
            self.jumps = self.max_jumps
            if not self.no_fall_dmg:
                if self.movement[1] > 8:
                    self.hit((h := self.movement[1]/2-4), 'true', dur=h/10)
            try:
                self.standing_block = terrain.map[0][self.coords[0], self.coords[1]+2]
            except KeyError:
                pass
            self.movement[1] = 1
            self.air_time = AIR_TIME
        else:
            self.standing_block = None

        if self.climbing and not self.stunned:
            if self.in_void:
                self.movement[1] = -0.81
            for ladder in terrain.ladder_rect:
                if self.rect.colliderect(ladder.rect):
                    self.movement[1] = -PLAYER_STATS[self.champ]['climbing_speed']
                    if not self.collision_types['top'] and not self.climbing_sfx.get_busy():
                        self.climbing_sfx.play(self.sfx['climbing'])
                        if not self.halt:
                            self.current_animation = 'climb'
                    break
            if self.wings and not self.in_void:
                if self.air_time > 0:
                    self.air_time -= 1
                    self.movement[1] = -2.81
                    self.flying = True
                else:
                    self.flying = False
            else:
                self.flying = False
        else:
            self.flying = False

        if not self.collision_types['bottom']:
            if self.jumps < 1:
                self.jumping = False
            self.movement[1] += GRAVITY_STRENGTH
            if self.descent:
                self.movement[1] += self.jump_height/16
        else:
            if self.current_animation == 'jump':
                self.halt = False

        if self.collision_types['top']:
            self.movement[1] = 1

        if self.moving_right:
            if self.in_void or self.flying:
                self.movement[0] = +self.vel // 2
            else:
                if not self.stunned:
                    self.movement[0] = +self.vel
            if not self.on_ladder and not self.halt:
                self.current_animation = 'walk'
            self.animation_flip = False
            if self.collision_types['bottom']:
                if not self.walk_sfx.get_busy():
                    self.walk_sfx.play(self.sfx['walk'])

        if self.moving_left:
            if self.in_void or self.flying:
                self.movement[0] = -self.vel//2
            else:
                if not self.stunned:
                    self.movement[0] = -self.vel
            if not self.on_ladder and not self.halt:
                self.current_animation = 'walk'
            self.animation_flip = True
            if self.collision_types['bottom']:
                if not self.walk_sfx.get_busy():
                    self.walk_sfx.play(self.sfx['walk'])

        if self.jumping:
            if self.collision_types['bottom'] or (not self.collision_types['bottom'] and self.jumps > 0):
                self.jumps -= 1
                self.jumping = False
                if not self.stunned:
                    self.movement[1] = -self.jump_height
                    self.halt = True
                    self.animation_speed_multiplier = 0.5
                    self.animation_counter = 0
                    self.current_animation = 'jump'
                    self.sfx['jump'].play()

        if not self.moving_left and not self.moving_right:
            self.movement[0] = 0
            if not self.climbing and not self.halt:
                self.current_animation = 'idle'

        if self.movement[1] > 1:
            if self.in_void:
                self.movement[1] = 1

        if self.movement[1] > 0.3:
            if self.on_ladder and not self.halt and self.movement[1] != 1:
                self.current_animation = 'climb_down'

        if self.movement[1] > 1.5:
            if self.on_ladder:
                if not self.climbing_sfx.get_busy():
                    self.climbing_sfx.play(self.sfx['climbing_down'])
                self.movement[1] = 1.5

        if self.movement[1] > 20:
            self.movement[1] = 20

    def get_selected_block(self, terrain, mx, my, inventory, shop, enemy_m):
        mx += scroll[0]
        my += scroll[1]
        selected_coords = (mx // TILE_SIZE, my // TILE_SIZE)
        if not inventory.open and not shop.open:
            for enemy in enemy_m.enemies:
                if enemy.rect.collidepoint(mx, my):
                    if distance(enemy.coords, self.coords) <= self.reach_distance:
                        self.selected_enemy = enemy
                        self.selected_block = None
                        return
            else:
                self.selected_enemy = None
                for i, block in terrain.map[0].items():
                    if distance(block.coords, self.coords) <= self.reach_distance:
                        block.in_reach = True
                    else:
                        block.in_reach = False

                    if selected_coords == block.coords:
                        if distance(selected_coords, self.coords) <= self.reach_distance:
                            if not block.rect.colliderect(self.rect):
                                target_x = (block.coords[0]-self.coords[0])
                                target_y = (block.coords[1]-self.coords[1])
                                if self.ray_trace(selected_coords, self.coords[0], self.coords[1], terrain.map[0]):
                                    self.selected_block = block
                                else:
                                    self.selected_block = None
                            else:
                                self.selected_block = None
                        else:
                            self.selected_block = None
        else:
            self.selected_block = None

    def ray_trace(self, selection, start_x, start_y, map):
        # for path in self.paths((start_x, start_y), (selection)):
        #     for i in path:
        #         if map[(start_x+i[0], start_x+i[1])].type != 'air':
        #             return False

        return True

    def break_block(self, terrain, hotbar):
        # self.current_animation = 'break'
        if self.selected_block and self.selected_block.type not in BG_BLOCKS:
            self.real_breaking = True
            if not self.break_sfx.get_busy():
                self.break_sfx.play(self.sfx['break'])
            try:
                self.breaking_speed = TOOL_SPEEDS[hotbar.selected_slot_content[0]]
            except (KeyError, IndexError):
                self.breaking_speed = TOOL_SPEEDS['hand']
            self.breaking_speed += self.breaking_speed * self.haste
            self.selected_block.hp -= int(self.breaking_speed + self.breaking_speed*self.haste)
            if self.selected_block.hp < 1:
                self.sfx['break_block'].play()
                for key, item in BLOCK_DROPS.items():
                    if key in self.selected_block.type:
                        hotbar.add_block_to_slot(item, 1)
                        break
                terrain.remove_block(self.selected_block.pos)
        else:
            self.real_breaking = False

    def on_left_click(self, hotbar, effects):
        if self.selected_block is not None:
            self.breaking_block = True
        elif self.selected_enemy is not None:
            self.halt = True
            self.animation_counter = 0
            self.halt_reason = 'hit'
            self.current_animation = 'hit' if self.moving_left or self.moving_right else 'swing'
            try:
                ad = WEAPON_DAMAGE[hotbar.selected_slot_content[0]]
            except (KeyError, IndexError):
                ad = WEAPON_DAMAGE['hand']
            ad += ad * effects['off']['sharp'][3]
            self.selected_enemy.hit(ad)
            if self.selected_enemy.rect.x < self.rect.x:
                self.selected_enemy.knocback = [-5, 4]
            else:
                self.selected_enemy.knocback = [5, 4]
        else:
            self.sfx['air_punch'].play(1)

    def on_right_click(self, terrain, hotbar, shop, inventory, effects, proj_m, upgrades, particle_m):
        if self.selected_block:
            if self.selected_block.type == 'door':
                terrain.map[0][self.selected_block.coords[0], self.selected_block.coords[1] - 1].type = 'open_door_top'
                self.selected_block.type = 'open_door'
                return

            if self.selected_block.type == 'door_top':
                self.selected_block.type = 'open_door_top'
                terrain.map[0][self.selected_block.coords[0], self.selected_block.coords[1] + 1].type = 'open_door'
                return

            elif self.selected_block.type == 'open_door':
                self.selected_block.type = 'door'
                terrain.map[0][self.selected_block.coords[0], self.selected_block.coords[1] - 1].type = 'door_top'
                return

            elif self.selected_block.type == 'open_door_top':
                self.selected_block.type = 'door_top'
                terrain.map[0][self.selected_block.coords[0], self.selected_block.coords[1]+1].type = 'door'
                return

            elif self.selected_block.type == 'shop':
                self.shop = self.selected_block
                shop.open = True
                inventory.open = True
                return

            elif self.selected_block.type == 'upgrade_shop':
                self.shop = self.selected_block
                upgrades.open = True
                inventory.open = True
                upgrades.on_shop_click(inventory, effects)
                return

        if hotbar.selected_slot_content is not None and not hotbar.selected_slot_content == []:
            if hotbar.selected_slot_content[0] in [gun for gun in GUNS.keys()]:  # will later be the list of thorwables
                hotbar.selected_slot_content[1] -= 1   # will later remove the used projectile
                self.animation_flip = True if not self.animation_flip else True
                proj_m.projectiles.append(Projectile(self.rect.center, self.m_xy,
                                                     GUNS[hotbar.selected_slot_content[0]], proj_m, particle_m))
            else:
                #self.current_animation = 'place'
                if self.selected_block:
                    if self.selected_block.type in BG_BLOCKS:
                        if not self.moving_left or self.moving_right:
                            if self.current_animation not in ('walk', 'climb'):
                                self.halt = True
                                self.animation_counter = 0
                                self.current_animation = 'craft'
                        if hotbar.selected_slot_content != []:
                            if hotbar.selected_slot_content[1] > 0 and hotbar.selected_slot_content[0] not in TOOLS:
                                if terrain.add_block(self.selected_block.pos, hotbar.selected_slot_content[0]):
                                    self.sfx['place'].play()
                                    hotbar.slot_contents[hotbar.selected_slot][1] -= 1

    def load_animations(self, dir):
        animation_dict = {}
        for animation in os.listdir(dir):
            frame_list = []
            for frame in os.listdir(dir + '/' + animation):
                img = pygame.image.load(dir + '/' + animation + '/' + frame).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE * 2 - TILE_SIZE//2, TILE_SIZE * 2 - TILE_SIZE//2))
                frame_list.append(img)
            animation_dict[animation] = frame_list

        return animation_dict

    def draw_animated_item(self, display):
        if self.holding_item in TOOLS:
            direction = pygame.math.Vector2(self.m_xy) - (self.rect.centerx - scroll[0], self.rect.centery - scroll[1])
            angle = direction.angle_to((0, 0))
            self.image = pygame.transform.rotate(self.block_preview_imgs[self.holding_item], angle)
            if self.breaking_block and self.selected_block is not None:
                if self.selected_block.type not in NO_HITBOX:
                    if self.breaking_angle < 60:
                        self.breaking_angle += 2
                        self.breaking_offset += 0.5
                    else:
                        self.breaking_angle = 0
                        self.breaking_offset = 0
            else:
                self.breaking_angle = 0
                self.breaking_offset = 0

            if -90 < angle < 90:
                self.image = pygame.transform.rotate(self.block_preview_imgs[self.holding_item],
                                                     -angle + self.breaking_angle)
                self.image = pygame.transform.flip(self.image, True, False)
                breaking_offset = -self.breaking_offset
            else:
                self.image = pygame.transform.rotate(self.block_preview_imgs[self.holding_item],
                                                     angle + self.breaking_angle)
                self.image = pygame.transform.flip(self.image, True, True)
                breaking_offset = self.breaking_offset
            rot_rect = self.image.get_rect()
            rot_rect.center = self.m_xy
            display.blit(self.image, (rot_rect.x + breaking_offset, rot_rect.y + self.breaking_offset))

    def draw(self, display):
        if self.wings:
            display.blit(self.wing_img, (self.rect.x - scroll[0]-self.width//2, self.rect.y - scroll[1]-23))
        if self.hitboxes:
            self.player_hitbox = pygame.Rect(self.rect.x - scroll[0], self.rect.y - scroll[1], self.width, self.height)
            pygame.draw.rect(display, 'white', self.player_hitbox, 1)
            pygame.draw.line(display, 'white', (0, VOID_Y-scroll[1]), (WINDOW_SIZE[0], VOID_Y-scroll[1]), 2)

            f = self.font.render('F3 screen on: ', True, (1, 1, 1))
            f_rect = f.get_rect()
            f_rect.midleft = (10, 100)
            display.blit(f, f_rect.topleft)

            c = self.font.render(f'x: {self.coords[0]}, y: {self.coords[1]}', True, (1, 1, 1))
            c_rect = c.get_rect()
            c_rect.midleft = (10, 150)
            display.blit(c, c_rect.topleft)

        if self.animation_counter // 7 < len(self.animations[self.current_animation]):
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        else:
            self.animation_counter = 1
            self.halt = False
            self.animation_speed_multiplier = 0
            current_img = self.animations[self.current_animation][int(self.animation_counter // 7)]
        self.animation_counter += PLAYER_ANIMATION_SPEED + self.animation_speed_multiplier
        if self.current_animation == 'walk':
            self.animation_counter += (self.vel-1)*0.8

        if self.animation_flip:
            current_img = pygame.transform.flip(current_img, True, False)
            offset_x = 9
        else:
            offset_x = -9

        self.scrolled_pos = ((self.rect.x - scroll[0] - offset_x) - 14, self.rect.y - scroll[1] - 8)
        display.blit(current_img, self.scrolled_pos)

        # try:
        #     display.blit(self.block_preview_imgs[self.holding_item], (self.rect.centerx-scroll[0],
        #                  self.rect.centery - scroll[1]))
        # except:
        #     pass

        # pygame.draw.line(display, 'white', (60, 80), (130, 100), 10)

    def respawn(self, effects=None, inv=None, htb=None, menu=None, last_frame=None, victory=False):
        if victory:
            with open("data/data.json", "r") as f:
                data = json.load(f)
            data['h_score'][self.champ][0] = 777
            data['h_score'][self.champ][1] = 4
            data['h_score'][self.champ][2] += 1
            with open("data/data.json", "w") as f:
                json.dump(data, f)

            menu.last_frame = self.last_frame
            menu.score = 777
            menu.state = 'victory'
            self.game_state = 'main_menu'

        if self.bed_destroyed:
            with open("data/data.json", "r") as f:
                data = json.load(f)
            data['h_score'][self.champ][0] = self.score if\
                self.score > data['h_score'][self.champ][0] else \
                data['h_score'][self.champ][0]

            data['h_score'][self.champ][1] = self.drakes_killed if\
                self.drakes_killed > data['h_score'][self.champ][1] else \
                data['h_score'][self.champ][1]
            with open("data/data.json", "w") as f:
                json.dump(data, f)
            menu.last_frame = last_frame
            menu.score = self.score
            menu.state = 'gg'
            self.game_state = 'main_menu'
        else:
            if inv:
                inv.clear_inv()
            if htb:
                htb.clear_htb(self.champ)
            self.hp = PLAYER_STATS[self.champ]['hp'] - 2
            self.current_chunk = ((self.start_pos[0]//TILE_SIZE)//CHUNK_SIZE,
                                  (self.start_pos[1]//TILE_SIZE)//CHUNK_SIZE)
            self.rect.x = self.start_pos[0]
            self.rect.y = self.start_pos[1]
        self.stun_dur = -1
        self.slow_dur = -1
        self.current_animation = 'idle'
        if effects:
            effects['iron'][1] = 4
            effects['gold'][1] = 0
            effects['diamond'][1] = 0
            effects['emerald'][1] = 0

    def update(self, terrain, hotbar, effects, water, inventory, shop, upgrades, menu, last_frame):
        self.delay += 20/FRAME_RATE
        self.kb()
        if not self.music_ch.get_busy():
            self.music_ch.play(self.music[self.current_drake])
        if not self.bed_destroyed:
            if distance(self.rect.center, terrain.player_spawnpoint) < BED_DECAY_RANGE*CHUNK_SIZE*TILE_SIZE:
                if self.base_time < self.base_timer_max:
                    self.base_time += BASE_BED_REGEN * (1/FRAME_RATE)
                self.in_base = True
                if self.hp < PLAYER_STATS[self.champ]['hp']:
                    self.hp += effects.stats['base']['heal_pool'][3]/FRAME_RATE
            else:
                self.in_base = False
                if self.base_time <= 0:
                    self.bed.hp -= BED_DECAY * 1/FRAME_RATE
                    if self.bed_hp <= 0:
                        self.bed_destroyed = True
                    self.base_time = 0
                else:
                    self.base_time -= 1/FRAME_RATE

        self.stats = effects.stats

        if self.score < 777:
            self.score += 1/FRAME_RATE
        if self.hp < 1:
            self.respawn(effects=effects.stats['money'], inv=inventory, htb=hotbar, menu=menu, last_frame=last_frame)

        if self.rect.bottom > VOID_Y:
            self.in_void = True
            self.hp -= 5 * 1/FRAME_RATE
            loc = (self.rect.centerx - scroll[0]) // WAVE_LENGTH
            water.splash(loc, -5)
        else:
            self.in_void = False

        self.move(terrain)
        self.coords = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
        self.pixel_coords = (self.coords[0] * TILE_SIZE, self.coords[1] * TILE_SIZE)

        if self.breaking_block:
            self.break_block(terrain, hotbar)

        for i, block in terrain.map[0].items():
            if self.coords == block.coords:
                self.current_chunk = block.chunk

        for ladder in terrain.ladder_rect:
            if self.rect.colliderect(ladder.rect):
                self.on_ladder = True
                break
            self.on_ladder = False

        if not self.breaking_block:
            self.real_breaking = False

        if not self.moving_left and not self.moving_right and not self.climbing and not self.jumping:
            if self.real_breaking and not self.halt:
                self.current_animation = 'break'

        self.bed_hp = self.bed.hp/BLOCK_HP
        if self.bed_hp < 1:
            self.bed_destroyed = True

        self.stun_dur -= 1
        self.slow_dur -= 1
        if self.stun_dur < 1:
            self.stunned = False
        if self.slow_dur < 1:
            self.slowed = False

        self.manage_effects(effects)

        if self.shop:
            if shop.open or upgrades.open:
                if distance(self.coords, self.shop.coords) > CHUNK_SIZE:
                    inventory.open = False
                    shop.open = False
                    upgrades.open = False
                    inventory.close(inventory)
                    self.sfx['close_inv'].play(1)
                    self.shop = None

    def manage_effects(self, effects):
        self.haste = effects.stats['off']['haste'][3]
        self.vel = sum(effects.stats['effects']['speed'][4])
        self.vel = self.vel + self.vel * effects.stats['effects']['speed'][3]
        self.vel = int(self.vel)
        if self.in_base:
            self.vel += effects.stats['base']['speed'][3]  # speed values
        self.jump_height = sum(effects.stats['effects']['jump_height'][4])
        self.jump_height = self.jump_height + self.jump_height * effects.stats['effects']['jump_height'][3]
        self.base_timer_max = BASE_TIME + BASE_TIME * effects.stats['util']['base_time'][3]
        self.tenacity = effects.stats['def']['tenacity'][3]

    def draw_bars(self, display):
        time = 10000
        for key, drake in DRAKES.items():
            if not drake['spawned']:
                new_time = int(DRAKES[key]['spawn_time']//FRAME_RATE - self.score)
                time = new_time if new_time < time else time
                air_time_font = self.font.render(f'Next drake arrives in {time}', True, (255, 255, 255))
                display.blit(air_time_font, (WINDOW_SIZE[0]//3-10, 15))

        if self.selected_block:
            block_rect = pygame.Rect(
                self.selected_block.x - scroll[0],
                self.selected_block.y - scroll[1],
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(display, 'white', block_rect, 1)

        if self.selected_enemy:
            block_rect = pygame.Rect(
                self.selected_enemy.rect.x - scroll[0],
                self.selected_enemy.rect.y - scroll[1], self.selected_enemy.width, self.selected_enemy.height
            )
            pygame.draw.rect(display, 'red', block_rect, 1)

        if self.wings and self.flying:
            air_time_font = self.font.render(f'wing time: {self.air_time/FRAME_RATE:.1f}', True, (1, 1, 1))
            display.blit(air_time_font, self.scrolled_pos)
        if self.stunned:
            air_time_font = self.font.render(f'stunned {self.stun_dur/FRAME_RATE:.1f}', True, (255, 255, 255))
            display.blit(air_time_font, self.scrolled_pos)

        self.draw_animated_item(display)

        score_font_render = self.font.render(f'Score: {int(self.score)}', True, 'white')
        display.blit(score_font_render, (WINDOW_SIZE[0] - 65, 10))

        pygame.draw.rect(display, 'black', self.hp_outline)
        if self.hp > 1:
            block_rect = pygame.Rect(120, 260, int(self.hp) * 5, 7)
            pygame.draw.rect(display, 'red', block_rect)
        pygame.draw.rect(display, 'gray', self.hp_outline, 1)

        if not self.bed_destroyed:
            timer_font_render = self.font.render(f'base timer: {int(self.base_time)}', True, 'white')
            display.blit(timer_font_render, (275, 250))

        if not self.bed_destroyed:
            pygame.draw.rect(display, 'black', self.bed_hp_outline)
            if self.bed_hp > 1:
                bed_hp_rect = pygame.Rect(275, 260, int(self.bed_hp/10) * 5, 7)
                pygame.draw.rect(display, 'yellow', bed_hp_rect)
            pygame.draw.rect(display, 'gray', self.bed_hp_outline, 1)
