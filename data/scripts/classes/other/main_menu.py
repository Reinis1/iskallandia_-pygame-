import pygame
from data.variables import *
from data.scripts.classes.other.button import Button
from data.scripts.core_functions import draw_rect_alpha
import json
title_font = pygame.font.Font('data/fonts/minecraft_font.ttf', 20)
stat_font = pygame.font.Font('data/fonts/minecraft_font.ttf', 6)
b_font = 'data/fonts/minecraft_font.ttf'


def play(player, menu, self, htb):
    player.music_ch.play(player.music['starting'])
    player.champ = menu.champ
    player.no_fall_dmg = True if player.champ == 'sivir' else False
    player.load_player_moddel()
    player.bed_destroyed = False
    player.bed_hp = 160
    menu.state = 'menu'
    player.game_state = 'game'
    player.respawn(htb=htb)


def open_settings(player, menu, self, htb):
    menu.state = 'champ_select'


def open_score(player, menu, self, htb):
    menu.state = 'score'


def select_champ(player, menu, self, htb):
    menu.state = 'menu'
    menu.champ = self.txt


def back(player, menu, b, htb):
    menu.state = 'menu'


def exit_game(player, menu, b, htb):
    pygame.quit()


def how_to_play(player, menu, b, htb):
    menu.state = 'how_to_play'


class MainMenu:
    def __init__(self):
        self.last_frame = None
        force_s = pygame.image.load('data/imgs/player/hopper/idle/1.png')
        self.hopper_s = pygame.transform.scale(force_s, (TILE_SIZE*4, TILE_SIZE*4))

        force_s = pygame.image.load('data/imgs/player/sivir/idle/1.png')
        self.sivir_s = pygame.transform.scale(force_s, (TILE_SIZE * 4, TILE_SIZE * 4))
        cursor = pygame.image.load('data/imgs/block_previews/crosshair.png').convert_alpha()
        self.cursor = pygame.transform.scale(cursor, (TILE_SIZE//2, TILE_SIZE//2))
        self.title = title_font.render('ISKALLANDIA', True, (1, 100, 1))
        self.title_gg = title_font.render('Game over!', True, (1, 100, 1))
        self.title_v = title_font.render('Victory!', True, (1, 100, 1))
        self.m_pos = (0, 0)
        self.title_rect = self.title.get_rect()
        self.title_rect.inflate_ip(10, 10)
        self.title_rect.center = (WINDOW_SIZE[0] // 2, 100)
        self.score = 0
        self.drakes_killed = 0
        self.black_bg = pygame.Rect(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1])
        how_to_play_s = pygame.image.load('data/imgs/how_to_play.png')
        self.how_to_play_s = pygame.transform.scale(how_to_play_s, WINDOW_SIZE)

        self.state = 'menu'
        self.champ = 'sealable'
        splash_art = pygame.image.load('data/imgs/splash_art/art.png')
        self.splash_art = pygame.transform.scale(splash_art, WINDOW_SIZE)

        force_s = pygame.image.load('data/imgs/player/sealable/idle/1.png')
        self.force_s = pygame.transform.scale(force_s, (TILE_SIZE*4, TILE_SIZE*4))
        self.spacing_x = WINDOW_SIZE[0] // 4
        self.stat_fonts = []
        for champ, stats in PLAYER_STATS.items():
            sublist = []
            for stat, value in stats.items():
                stat_r = stat_font.render(f'{stat.capitalize()}', True, (170, 170, 170))
                if type(value) == list:
                    value = value[0]
                if type(value) == float:
                    value = f'{value:.0%}'
                value = stat_font.render(f'{value}', True, (255, 255, 255))
                pair = [stat_r, value]
                sublist.append(pair)
            self.stat_fonts.append(sublist)

        with open("data/data.json", "r") as f:
            data = json.load(f)
            self.h_score = data["h_score"]

        spacing_x = WINDOW_SIZE[0] // 4
        play_b = Button(position=(spacing_x, WINDOW_SIZE[1]-60),
                        size=(60, 20), clr=(120, 120, 120, 200), cngclr=(255, 0, 0), func=play, text='PLAY', font=b_font)

        settings_b = Button(position=(spacing_x*2, WINDOW_SIZE[1] - 60),
                            size=(60, 20), clr=(120, 120, 120, 200), cngclr=(255, 0, 0),
                            func=open_settings, text='Champ select', font=b_font)

        score_b = Button(position=(spacing_x * 3, WINDOW_SIZE[1] - 60),
                       size=(60, 20), clr=(120, 120, 120, 200), cngclr=(255, 0, 0),
                       func=open_score, text='High score', font=b_font)

        force_b = Button(position=(60, WINDOW_SIZE[1] - 30),
                       size=(60, 20), clr=(120, 120, 120), cngclr=(255, 0, 0),
                       func=select_champ, text='sealable', font=b_font)

        hopper_b = Button(position=(230, WINDOW_SIZE[1] - 30),
                       size=(60, 20), clr=(120, 120, 120), cngclr=(255, 0, 0),
                       func=select_champ, text='hopper', font=b_font)

        sivir_b = Button(position=(400, WINDOW_SIZE[1] - 30),
                          size=(60, 20), clr=(120, 120, 120), cngclr=(255, 0, 0),
                          func=select_champ, text='sivir', font=b_font)

        self.back_b = Button(position=(spacing_x * 3, WINDOW_SIZE[1] - 60),
                         size=(60, 20), clr=(120, 120, 120), cngclr=(255, 0, 0),
                         func=back, text='Main menu', font=b_font)

        self.exit_b = Button(position=(spacing_x * 3, WINDOW_SIZE[1] - 30),
                             size=(60, 20), clr=(70, 70, 70), cngclr=(155, 0, 0),
                             func=exit_game, text='Quit game', font=b_font)

        play_again_b = Button(position=(spacing_x * 2, WINDOW_SIZE[1] - 30),
                        size=(60, 20), clr=(70, 70, 70), cngclr=(155, 0, 0),
                        func=play, text='Play again', font=b_font)

        how_to_play_b = Button(position=(spacing_x * 1, WINDOW_SIZE[1] - 30),
                              size=(60, 20), clr=(70, 70, 70), cngclr=(155, 0, 0),
                              func=how_to_play, text='How to play', font=b_font)

        self.champ_button_list = [force_b, hopper_b, sivir_b]
        self.button_list = [play_b, settings_b, score_b,  self.exit_b, how_to_play_b]
        self.gg_button_list = [play_again_b, self.back_b, self.exit_b]
        self.score_button_list = [self.exit_b, self.back_b]
        self.how_to_play_button_list = [self.back_b]

    def draw(self, screen):
        if self.state == 'menu':
            screen.blit(self.splash_art, (0, 0))
            draw_rect_alpha(screen, (1, 1, 1, 135), self.black_bg)
            for b in self.button_list:
                b.draw(screen)

            screen.blit(self.title, (self.title_rect.x+5, self.title_rect.y+5))
            if self.champ =='sealable':
                screen.blit(self.force_s, ((WINDOW_SIZE[0]//2-TILE_SIZE*2)+30, WINDOW_SIZE[1] - 240))
            elif self.champ =='hopper':
                screen.blit(self.hopper_s, ((WINDOW_SIZE[0] // 2 - TILE_SIZE * 2) + 30, WINDOW_SIZE[1] - 240))
            elif self.champ == 'sivir':
                screen.blit(self.sivir_s, ((WINDOW_SIZE[0] // 2 - TILE_SIZE * 2) + 30, WINDOW_SIZE[1] - 240))
            screen.blit(self.cursor, self.m_pos)

        elif self.state == 'champ_select':
            screen.blit(self.splash_art, (0, 0))
            draw_rect_alpha(screen, (1, 1, 1, 200), self.black_bg)
            screen.blit(self.force_s, (20, WINDOW_SIZE[1] - 95 - TILE_SIZE*6))
            screen.blit(self.hopper_s, (185, WINDOW_SIZE[1] - 95 - TILE_SIZE * 6))
            screen.blit(self.sivir_s, (350, WINDOW_SIZE[1] - 95 - TILE_SIZE * 6))

            for i, champ in enumerate(self.stat_fonts):
                for o, pair in enumerate(champ):
                    screen.blit(pair[1], (90 + 170 * i, 150 + 12 * o))
                    screen.blit(pair[0], (20 + 170 * i, 150 + 12 * o))

            for b in self.champ_button_list:
                b.draw(screen)
            screen.blit(self.cursor, self.m_pos)

        elif self.state == 'gg':
            self.last_frame = pygame.transform.scale(self.last_frame, WINDOW_SIZE)
            screen.blit(self.last_frame, (0, 0))
            draw_rect_alpha(screen, (1, 1, 1, 50), self.black_bg)
            draw_rect_alpha(screen, (1, 1, 1, 190), self.title_rect)

            font_render = title_font.render(f'Score: {self.score:.0f}', True, (255, 255, 255))
            if self.drakes_killed == 0:
                font_render_2 = title_font.render(f'Not even a single drake killed, NOOB?', True, (255, 255, 255))
            else:
                font_render_2 = title_font.render(f'Only {self.drakes_killed} drakes killed...', True, (255, 255, 255))
            screen.blit(self.title_gg, (self.title_rect.x + 5, self.title_rect.y + 5))
            screen.blit(font_render, (self.title_rect.x + 5, self.title_rect.y + 45))
            screen.blit(font_render_2, (self.title_rect.x + 5, self.title_rect.y + 85))

            for b in self.gg_button_list:
                b.draw(screen)

            screen.blit(self.cursor, self.m_pos)

        elif self.state == 'victory':
            self.last_frame = pygame.transform.scale(self.last_frame, WINDOW_SIZE)
            screen.blit(self.last_frame, (0, 0))
            draw_rect_alpha(screen, (1, 1, 1, 50), self.black_bg)
            draw_rect_alpha(screen, (1, 1, 1, 190), self.title_rect)

            font_render = title_font.render(f'Score: 777!', True, (255, 255, 255))
            font_render_2 = title_font.render(f'All drakes killed!', True, (255, 255, 255))
            screen.blit(self.title_v, (self.title_rect.x + 5, self.title_rect.y + 5))
            screen.blit(font_render, (self.title_rect.x + 5, self.title_rect.y + 45))
            screen.blit(font_render_2, (self.title_rect.x + 5, self.title_rect.y + 85))

            for b in self.gg_button_list:
                b.draw(screen)

            screen.blit(self.cursor, self.m_pos)

        elif self.state == 'score':
            with open("data/data.json", "r") as f:
                data = json.load(f)
                self.h_score = data["h_score"]

            screen.blit(self.splash_art, (0, 0))
            draw_rect_alpha(screen, (1, 1, 1, 200), self.black_bg)

            screen.blit(self.force_s, (0, 110))
            screen.blit(self.hopper_s, (150, 75))
            screen.blit(self.sivir_s, (300, 40))

            spacing = 1
            spacing_y = 2

            offset_y = 40
            for champ, stats in data["h_score"].items():
                spacing += 1
                spacing_y -= 1
                champ_render = title_font.render(champ.capitalize(), True, (255, 255, 255))
                score_render = stat_font.render(f'High score: {int(stats[0])}', True, (255, 255, 255))
                win_render = stat_font.render(f'Wins: {int(stats[1])}', True, (155, 155, 155))
                drake_render = stat_font.render(f'Max drakes killed: {int(stats[2])}', True, (155, 155, 155))

                screen.blit(champ_render, (150 * spacing-270, 80 + offset_y*spacing_y))
                screen.blit(score_render, (150 * spacing-225, 130 + offset_y*spacing_y))
                screen.blit(win_render, (150 * spacing-225, 160 + offset_y*spacing_y))
                screen.blit(drake_render, (150 * spacing-225, 170 + offset_y*spacing_y))

            for b in self.score_button_list:
                b.draw(screen)
            screen.blit(self.cursor, self.m_pos)

        elif self.state == 'how_to_play':
            screen.blit(self.splash_art, (0, 0))
            draw_rect_alpha(screen, (1, 1, 1, 200), self.black_bg)
            screen.blit(self.how_to_play_s, (0, 0))
            for b in self.how_to_play_button_list:
                b.draw(screen)
            screen.blit(self.cursor, self.m_pos)

    def update(self, m_pos, player):
        if not player.music_ch.get_busy():
            player.music_ch.play(player.music['lobby'])
        self.m_pos = m_pos
        if self.state == 'menu':
            for b in self.button_list:
                b.mouseover()
        elif self.state == 'champ_select':
            for b in self.champ_button_list:
                b.mouseover()
        elif self.state == 'score':
            for b in self.score_button_list:
                b.mouseover()
        elif self.state == 'gg':
            for b in self.gg_button_list:
                b.mouseover()
        elif self.state == 'victory':
            for b in self.gg_button_list:
                b.mouseover()
        elif self.state == 'how_to_play':
            for b in self.how_to_play_button_list:
                b.mouseover()

    def on_click(self, pos, player, htb):
        if self.state == 'menu':
            for b in self.button_list:
                if b.rect.collidepoint(pos):
                    b.call_back(player, self, b, htb)

        elif self.state == 'champ_select':
            for b in self.champ_button_list:
                if b.rect.collidepoint(pos):
                    b.call_back(player, self, b, htb)

        elif self.state == 'score':
            for b in self.score_button_list:
                if b.rect.collidepoint(pos):
                    b.call_back(player, self, b, htb)

        elif self.state == 'gg':
            for b in self.gg_button_list:
                if b.rect.collidepoint(pos):
                    b.call_back(player, self, b, htb)

        elif self.state == 'how_to_play':
            for b in self.how_to_play_button_list:
                if b.rect.collidepoint(pos):
                    b.call_back(player, self, b, htb)

        elif self.state == 'victory':
            for b in self.gg_button_list:
                if b.rect.collidepoint(pos):
                    b.call_back(player, self, b, htb)

