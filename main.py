import pygame
pygame.init()
pygame.mixer.init()
from sys import exit

from data.scripts.classes.map.bg import BackGround
from data.scripts.classes.map.gen_manager import GenManager
from data.scripts.classes.other.particle_manager import ParticleManager
from data.scripts.classes.entities.player import Player
from data.scripts.classes.map.terrain import Terrain
from data.scripts.classes.inventories.hotbar import Hotbar
from data.scripts.classes.inventories.inventory import PlayerInventory
from data.scripts.classes.inventories.shop import Shop
from data.scripts.classes.other.effect import Effect
from data.scripts.classes.entities.enemies.enemy_manager import EnemyManager
from data.scripts.classes.other.projectile_manager import ProjectileManager
from data.scripts.classes.other.main_menu import MainMenu
from data.scripts.classes.map.water import Wave
from data.scripts.classes.inventories.perma_upgrades import Upgrades

from data.scripts.core_functions import draw, distance

from data.variables import *
from pygame.locals import *

clock = pygame.time.Clock()

screen = pygame.Surface(WINDOW_SIZE)
if FULL_SCREEN:
    flags = GL_DOUBLEBUFFER | FULLSCREEN
else:
    flags = GL_DOUBLEBUFFER
render = pygame.display.set_mode(RENDER_SIZE, flags)

pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

main_menu = MainMenu()
bg = BackGround()
water = Wave()


def reset(replay=None):
    global hotbar
    hotbar = Hotbar()
    global terrain
    terrain = Terrain()
    global player
    player = Player(terrain.player_spawnpoint, TILE_SIZE, TILE_SIZE*2, 0.01, 16, terrain)
    global effects
    effects = Effect()
    global upgrades
    upgrades = Upgrades()

    global proj_m
    proj_m = ProjectileManager()
    global enemy_m
    enemy_m = EnemyManager(terrain)
    global particle_m
    particle_m = ParticleManager()
    global gen_m
    gen_m = GenManager(terrain)

    global player_inventory
    player_inventory = PlayerInventory()

    global player_shop
    player_shop = Shop(shop_sortiment)


reset()

frame = None
a = None
b = None

avg_fps = 0
tick_counter = 0
proj = []

last_frame = None

pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))

while __name__ == '__main__':

    clock.tick(FRAME_RATE)
    tick_counter += 1
    if tick_counter == FRAME_RATE:
        tick_counter = 0
        avg_fps /= FRAME_RATE
        pygame.display.set_caption(f'Videji fps: {(int(avg_fps))}')
    else:
        avg_fps += int(clock.get_fps())

    mx, my = pygame.mouse.get_pos()

    if player.game_state == 'main_menu':
        main_menu.update((mx, my), player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    main_menu.on_click((mx, my), player, hotbar)
                    effects.load_player_stats(player.champ)

        draw(screen, main_menu, game_state=player.game_state)


    if player.game_state == 'game':
        last_frame = frame
        player.last_frame = last_frame

        scroll[0] += int(
            ((player.rect.centerx-30) - scroll[0] - (WINDOW_SIZE[0]/2 + player.width/2 - 50)) / SCROLL_STIFF
        )
        #  if scroll[1] - WINDOW_SIZE[1] < VOID_Y - WINDOW_SIZE[1]: # futher down = bigger positive scroll y value
        scroll[1] += int(
            ((player.rect.centery-50) - scroll[1] - (WINDOW_SIZE[1]/2 + player.height/2 - 100)) / SCROLL_STIFF
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    player.moving_left = True
                if event.key == pygame.K_d:
                    player.moving_right = True
                if event.key == pygame.K_SPACE:
                    player.jumping = True
                if event.key == pygame.K_F4:
                    reset(True)
                if event.key == pygame.K_s:
                    player.descent = True

                if event.key == pygame.K_w:
                    player.climbing = True

                if event.key == pygame.K_e:
                    player_inventory.open = True
                    player.sfx['open_inv'].play()

                if event.key == pygame.K_LSHIFT:
                    player_inventory.shift = True

                if event.key == pygame.K_F3:
                    if player.hitboxes:
                        player.hitboxes = False
                    else:
                        player.hitboxes = True

                if event.key == pygame.K_ESCAPE:
                    player_inventory.open = False
                    player_shop.open = False
                    upgrades.open = False
                    player_inventory.close(player_inventory)

                if event.key == pygame.K_f:
                    hotbar.selected_slot = 1
                if event.key == pygame.K_q:
                    hotbar.selected_slot = 2

                try:
                    if int(pygame.key.name(event.key)) != 0:
                        hotbar.selected_slot = int(pygame.key.name(event.key))
                except ValueError:
                    pass

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    player.moving_right = False
                if event.key == pygame.K_a:
                    player.moving_left = False

                if event.key == pygame.K_w:
                    player.climbing = False

                if event.key == pygame.K_s:
                    player.descent = False

                if event.key == pygame.K_LSHIFT:
                    player_inventory.shift = False

                if event.key == pygame.K_e:
                    player_inventory.open = False
                    player_shop.open = False
                    upgrades.open = False
                    player_inventory.close(player_inventory)
                    player.sfx['close_inv'].play()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.on_left_click(hotbar, effects.stats)
                    if player_inventory.open:
                        player_inventory.on_click(hotbar, player_inventory)
                    if player_shop.open:
                        player_shop.on_shop_click(hotbar, player_inventory, effects, player)
                    if upgrades.open:
                        upgrades.on_shop_click(player_inventory, effects)
                if event.button == 3:
                    player.on_right_click(terrain, hotbar, player_shop,
                                          player_inventory, effects, proj_m, upgrades, particle_m)

            if event.type == pygame.MOUSEBUTTONUP:
                player.breaking_block = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    if hotbar.selected_slot != 9:
                        hotbar.selected_slot += 1
                    else:
                        hotbar.selected_slot = 1

                if event.button == 5:
                    if hotbar.selected_slot != 1:
                        hotbar.selected_slot -= 1
                    else:
                        hotbar.selected_slot = 9

        for block in [val for key, val in terrain.map[0].items()]:
            if distance(player.current_chunk, block.chunk) >= RENDER_DISTANCE:
                if block.save:
                    terrain.placed_blocks.append(block)
                del terrain.map[0][block.coords]

        player.get_selected_block(terrain, mx, my, player_inventory, player_shop, enemy_m)
        player_inventory.get_selected_slot(mx, my, hotbar)
        player_shop.get_selected_slot(mx, my)
        upgrades.get_selected_slot(mx, my)

        player_inventory.m_xy = (mx, my)
        player_shop.m_xy = (mx, my)
        upgrades.m_xy = (mx, my)
        player.m_xy = (mx, my)
        hotbar.m_xy = (mx, my)

        terrain.update(player)
        player.update(terrain, hotbar, effects, water, player_inventory, player_shop, upgrades, main_menu, last_frame)
        effects.update(player)

        enemy_m .update(terrain, player, water, proj_m, particle_m, effects.stats['debuffs'], main_menu)
        particle_m.update(water, player)
        proj_m.update(terrain, scroll, enemy_m.enemies, water, player)
        hotbar.update(player)

        water.update(player.hitboxes, particle_m)

        player_inventory.update(hotbar, player_shop, upgrades)
        player_shop.update(hotbar)

        gen_m.update(terrain, player, effects)

        draw(screen, bg, terrain, player,
             enemy_m, water, proj_m, particle_m, effects, hotbar, player_shop, upgrades, player_inventory)

        if player.victory:
            player.music_ch.stop()
            player.respawn(menu=main_menu, last_frame=last_frame, victory=True)
            reset()

        if player.bed_destroyed:
            if player.hp < 1:
                player.music_ch.stop()
                player.respawn(menu=main_menu, last_frame=last_frame)
                reset('gg')

    frame = pygame.transform.scale(screen, RENDER_SIZE)
    render.blit(frame, (0, 0))

