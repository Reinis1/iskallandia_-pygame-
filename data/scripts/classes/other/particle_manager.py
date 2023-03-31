import pygame
import random
from data.variables import *
import os

imgs_dir = 'data/imgs/particles/bubble/'

window2 = pygame.Surface((600, 400))

group = []


def mutate_color(color, rate):
    new_color = []
    for i in color:
        i += random.randint(-rate, rate)
        if i > 255:
            i = 255
        elif i < 1:
            i = 1
        new_color.append(i)
    return tuple(new_color)


def mutate_pos(pos, rate, dir=None):
    if not dir:
        return pos
    elif dir == 'all':
        new_pos = (pos[0] + random.randint(-rate, rate), pos[1] + random.randint(-rate, rate))
    elif dir == 'x':
        new_pos = (pos[0] + random.randint(-rate, rate), pos[1])
    else:
        new_pos = (pos[0], pos[1] + random.randint(-rate, rate))
    return new_pos


class Particles(pygame.sprite.Sprite):
    "Creates particles starting from pos with a color"

    def __init__(self, pos, y_dir, color, particle_m=None, sparse=30, turn="off", radius=(4, 6),
                 vel=(2, 2), type_='basic', speed=0.01, shrink=0.05, mutate_rate=40, dir=None):
        super(Particles, self).__init__()
        self.mutate_rate = mutate_rate
        self.particles_list = []
        self.pos = pos
        self.color = color
        self.y_dir = y_dir
        self.radius = radius
        self.sparse = sparse  # generate particles not from the same starting point
        # self.generate_particles()
        particle_m.group[type_] = self
        self.m = particle_m
        self.turn = turn  # this makes the effect visible
        self.vel = vel
        self.speed = speed
        self.shrink = shrink
        self.dir = dir

    def choose_y_dir(self):
        "Makes particles go in every direction you want"

        # Make the flow go down
        if self.y_dir == "down":
            y_dir = 2  # self.vel[1]

        elif self.y_dir == "up":
            y_dir = -2  # self.vel[1]

        # Make the particles spread all y_dirs
        elif self.y_dir == "all":
            # y_dir = random.randrange(-self.vel[1], self.vel[1]+1)
            y_dir = random.randrange(-2, 2, 1)
        else:
            raise ValueError

        return y_dir

    def generate_particles(self):
        """List with position etc of particles"""
        if self.turn == 'on':

            # setting the data for each particles
            self.pos = mutate_pos(self.pos, self.sparse, dir=self.dir)
            origin = [self.pos[0], self.pos[1]]  # Starting here each particles
            y_dir = self.choose_y_dir()
            x_dir = random.randint(0, 20) / 10 - 1
            dirs = [x_dir, y_dir]  # movement
            radius = random.randint(self.radius[0], self.radius[1])  # radius
            # Appending data to the list
            self.particles_list.append([origin, dirs, radius, mutate_color(self.color, self.mutate_rate)])
        self.generate_movements()

    def generate_movements(self):
        # Moving the coordinates and size of self.particles_list
        for particle in self.particles_list[:]:
            # if self.turn == 'off':
            #     self.particles_list.remove(particle)
            # else:
                particle[0][0] += particle[1][0]  # x pos += x_dir
                particle[0][1] += particle[1][1]  # y pos += y_dir
                particle[2] -= self.shrink # how fast circles shrinks
                # if particle[1][1] < 0:
                #     particle[1][1] -= self.speed
                # else:  # circles speed
                #     particle[1][1] += self.speed

                if particle[2] < 0 or particle[0][0] <= scroll[0]+WINDOW_SIZE[0]//8 or \
                        particle[0][0] >= scroll[0]+WINDOW_SIZE[0]-WINDOW_SIZE[0]//16:
                    self.particles_list.remove(particle)

    def draw(self, screen):
        "Draws particles based on data in the self.particles_list"
        #if self.turn == "on":
        for particle in self.particles_list:
            pygame.draw.circle(
                screen, particle[3],
                (round(particle[0][0])-scroll[0]-29, round(particle[0][1])-scroll[1]+40), round(particle[2]))


p1 = 1
# Some random colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)


class ParticleManager:
    def __init__(self):
        self.player_pos = (0, 0)
        self.draw_fog = True
        self.added = False
        self.water_particles = []
        self.cooldown = 0
        self.bubble_img = []
        self.group = {}
        self.explosion_len = 45
        self.fog = pygame.image.load('data/imgs/fog.png').convert_alpha()
        self.fog_2 = pygame.image.load('data/imgs/fog_2.png').convert_alpha()
        self.player_p = Particles((0, 0), y_dir="all", color=(114, 70, 27),
                                  radius=(1, 3), particle_m=self, vel=(1, 1), type_='walk', speed=0.1, shrink=0.1,
                                  dir='x', sparse=10)
        self.ladder_p = Particles((0, 0), y_dir="all", color=(114, 70, 27),
                                  radius=(2, 3), particle_m=self, vel=(1, 1), type_='ladder', speed=1, shrink=0.05
                                  , dir='all', sparse=20)
        self.break_p = Particles((0, 0), y_dir="down", color=(214, 174, 114),
                                 radius=(1, 3), particle_m=self, vel=(1, 3), type_='break', speed=0.01, shrink=0.1
                                 , sparse=10, dir='all')
        self.void_p = Particles((0, 0), y_dir="up", color=(27, 170, 27),
                                radius=(4, 7), particle_m=self, vel=(3, 3),
                                type_='void', speed=0.05, shrink=0.08, dir='all')

        self.blood_p = Particles((0, 0), y_dir="down", color=(215, 27, 27),
                                 radius=(1, 4), particle_m=self, vel=(3, 3),
                                 type_='blood', speed=0.15, shrink=0.15, dir='y', sparse=TILE_SIZE)

        self.enemy_blood_p = Particles((0, 0), y_dir="all", color=(215, 50, 50),
                                       radius=(2, 5), particle_m=self, vel=(3, 3),
                                       type_='enemy_blood', speed=0.05, shrink=0.5, dir='all')
        self.player_kb_p = Particles((0, 0), y_dir="all", color=(566, 50, 220),
                                     radius=(2, 5), particle_m=self, vel=(3, 3),
                                     type_='player_kb_p', speed=0.05, shrink=0.5, dir='all')

        for img in os.listdir(imgs_dir):
            loaded_img = pygame.image.load(imgs_dir + '/' + img).convert_alpha()
            size = random.randint(20, 60)
            loaded_img = pygame.transform.scale(loaded_img, (size, size))
            self.bubble_img.append(loaded_img)
        self.generate_particles()

    def generate_particles(self):
        target_x = random.randint(scroll[0], RENDER_SIZE[0] + scroll[0])
        self.water_particles.append(Bubble(target_x, VOID_Y, self))

    def update(self, water, player):
        m_pos = (player.m_xy[0]+scroll[0]+TILE_SIZE-8, player.m_xy[1]+scroll[1]-TILE_SIZE)
        self.player_pos = (player.rect.left+TILE_SIZE, player.rect.bottom-TILE_SIZE)
        self.player_p.pos = (player.rect.left+TILE_SIZE, player.rect.bottom-TILE_SIZE)
        self.void_p.pos = (player.rect.left+TILE_SIZE, player.rect.bottom-TILE_SIZE)
        self.ladder_p.pos = (player.rect.left + TILE_SIZE, player.rect.bottom - TILE_SIZE-16)
        self.blood_p.pos = (player.rect.left + TILE_SIZE, player.rect.bottom - TILE_SIZE - 16)
        self.break_p.pos = m_pos
        self.player_kb_p.pos = (player.rect.left + TILE_SIZE, player.rect.bottom - TILE_SIZE - 16)
        if player.selected_enemy is not None:
            self.enemy_blood_p.pos = (player.selected_enemy.rect.centerx+player.selected_enemy.width,
                                      player.selected_enemy.rect.centery-player.selected_enemy.height)

        if player.collision_types['bottom']:
            if player.moving_right or player.moving_left:
                self.group['walk'].turn = "on"
                bl = player.standing_block
                if bl is not None and not bl.type == 'air':
                    self.group['walk'].color = BLOCK_COLORS[bl.type]
            else:
                self.group['walk'].turn = "off"
        else:
            self.group['walk'].turn = "off"

        self.group['ladder'].turn = "on" if player.on_ladder and player.movement[1] != 1 else 'off'
        if player.real_breaking:
            self.group['break'].turn = "on"
            try:
                self.group['break'].color = BLOCK_COLORS[player.selected_block.type]
            except KeyError:
                self.group['break'].color = (1, 1, 1)
        else:
            self.group['break'].turn = 'off'
        self.group['void'].turn = "on" if player.in_void else 'off'
        self.group['blood'].turn = "on" if player.current_animation == 'hurt' else 'off'
        self.group['enemy_blood'].turn = "on" if player.current_animation in ('hit', 'swing') else 'off'
        self.group['player_kb_p'].turn = 'on' if player.is_kb else 'off'
        try:
            if self.group['explosion'].turn == 'on':
                self.explosion_len -= 1
                if self.explosion_len < 0:
                    self.explosion_len = 45
                    self.group['explosion'].turn = 'off'
        except KeyError:
            pass

        if self.cooldown > 1:
            self.cooldown = 0
            self.generate_particles()

        for i in self.water_particles:  # Particles
            i.update(self)
            index = water.get_spring_index_for_x_pos(i.x)
            if i.y > water.get_target_height():
                if i.on_water_surface:
                    self.water_particles.remove(i)
                if not i.spring:
                    try:
                        i.spring = water.springs[index]
                    except IndexError:
                        self.water_particles.remove(i)
                    try:
                        i.next_spring = water.springs[index + 1]
                    except IndexError:
                        try:
                            self.water_particles.remove(i)
                        except ValueError:
                            pass
                    water.splash(index, 2)
        self.cooldown += 30/FRAME_RATE

        self.draw_fog = player.fog

    def draw(self, screen):
        for i in self.water_particles:  # Particles
            i.draw(screen)

        for key, par in self.group.items():
            if par.turn in ('on', 'off'):
                par.generate_particles()
                par.draw(screen)
        if self.draw_fog:
            screen.blit(self.fog, (self.player_pos[0]-scroll[0]-480, self.player_pos[1]-scroll[1]-320))
        else:
            screen.blit(self.fog_2, (self.player_pos[0] - scroll[0] - 480, self.player_pos[1] - scroll[1] - 320))


class Bubble:
    def __init__(self, x, y, m):
        self.x = x
        self.y = y
        self.height = random.randint(2, 10)
        self.width = random.randint(5, 50 + 20)
        self.dy = 0
        self.spring = None
        self.next_spring = None
        self.rot = random.randint(0, 360)
        self.rot = 0
        self.gravity = 0.1
        self.water_force = 0.005
        self.on_water_surface = False
        self.lifetime = random.randrange(FRAME_RATE, FRAME_RATE*8)
        self.m = random.choice(m.bubble_img)

    def update(self, m):
        self.lifetime -= 1
        if self.lifetime < 0:
            m.water_particles.remove(self)
        else:
            if self.spring:
                if self.on_water_surface:
                    self.y = self.spring.height - self.height
                else:
                    self.dy -= self.water_force
                    self.y += self.dy
                    if self.dy <= 0 and self.y <= self.spring.height:
                        self.on_water_surface = True
            else:
                self.dy += self.gravity
                self.y += self.dy

    def draw(self, surf: pygame.Surface):
        surf.blit(self.m, self.m.get_rect(center=(self.x - scroll[0], self.y + VOID_Y - RENDER_SIZE[1] // 2 - scroll[1])))

        # pygame.draw.circle(surf, 'green', (self.x-scroll[0], self.y+VOID_Y-WINDOW_SIZE[1] // 2-scroll[1]), size / 2)
