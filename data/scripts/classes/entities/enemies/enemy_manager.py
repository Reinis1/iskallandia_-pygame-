from data.scripts.classes.entities.enemies.enemy import *


class EnemyManager:
    def __init__(self, terrain):
        self.track = None
        self.counter = 0
        self.enemies = []
        self.enemies_per_bed = {}
        self.sfx = {}
        self.spawn_sound_played = False
        for key, drake in DRAKES.items():
            drake['spawned'] = False
        for sf in os.listdir('data/sounds/sfx/enemies/enemy_m'):
            sfx = pygame.mixer.Sound(f'data/sounds/sfx/enemies/enemy_m/{sf}')
            img_name = sf.split('.')[0]
            self.sfx[img_name] = sfx

        for key, beds in terrain.beds.items():
            if key in ('warwick', 'i_warwick'):
                for bed in beds:
                    enemy_list = []
                    for i in range(ENEMIES[key]['count_per_bed']):
                        enemy_list.append(Warwick((bed.x, bed.y - 2 * TILE_SIZE), key))
                    self.enemies_per_bed[bed] = enemy_list
            elif key in ('vex', 'i_vex'):
                for bed in beds:
                    enemy_list = []
                    for i in range(ENEMIES[key]['count_per_bed']):
                        enemy_list.append(Vex((bed.x, bed.y - 2 * TILE_SIZE), key))
                    self.enemies_per_bed[bed] = enemy_list

    def update(self, terrain, player, water, proj_m, particle_m, effects, menu):
        self.counter += 1
        for bed, enemies in self.enemies_per_bed.items():
            try:
                if terrain.map[0][bed.coords].type != bed.type:
                    terrain.beds.pop(bed)
                    self.enemies_per_bed.pop(bed)
            except KeyError:
                pass
            else:
                for enemy in enemies:
                    if not enemy.alive:
                        enemy.respawn_timer -= 1
                        if enemy.respawn_timer < 0:
                            self.sfx[f'spawn'].play()
                            enemy.respawn_timer = ENEMIES[enemy.type]['respawn_time']
                            enemy.respawn()
                            self.enemies.append(enemy)

        for enemy in self.enemies:
            in_base = False
            if distance(player.bed.coords, enemy.coords) < CHUNK_SIZE:
                in_base = True
            enemy.update(terrain, player, water, proj_m, self, particle_m, effects, in_base, menu)

        for key, drake in DRAKES.items():
            if self.counter > drake['spawn_time'] - FRAME_RATE*2 and not drake['spawned']:
                if not self.spawn_sound_played:
                    self.sfx['drake_spawn'].play()
                    self.spawn_sound_played = True
                    player.current_drake = key
                    player.music_ch.play(player.music[key])
                if self.counter > drake['spawn_time']:
                    self.spawn_sound_played = False
                    drake['spawned'] = True
                    self.enemies.append(Drake1((player.rect.centerx, player.rect.centery-200), key, self))

    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
