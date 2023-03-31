
def sec(seconds):
    return seconds * FRAME_RATE


WINDOW_SIZE = (480, 320)

# RENDER_SIZE = (1280, 720)
RENDER_SIZE = (1920, 1080)
# RENDER_SIZE = (2560, 1440)
FRAME_RATE = 90

GRAVITY_STRENGTH = 0.2
CHUNK_SIZE = 8  # in blocks
TILE_SIZE = 40  # in pixels
SCROLL_STIFF = 5
REACH = 4
AIR_TIME = sec(3)
# How closely the camera follows the player (higher number = less stiff)
RENDER_DISTANCE = 3  # in chunks
STACK_SIZE = 64  # Max number of blocks held in an inventory slot
INV_FONT_SIZE = 6

VOID_Y = TILE_SIZE*CHUNK_SIZE*16  # in pixels

BLOCK_HP = 8  # number of states the block goes through before it gets destroyed
# VOID_HEIGHT = CHUNK_SIZE*TILE_SIZE * 3  # in pixels/chunks
PLAYER_HP = 16
PLAYER_ANIMATION_SPEED = 0.5 * FRAME_RATE / 90
BASE_TIME = 45  # in sec
BED_DECAY = 12
BASE_BED_REGEN = 8
BED_DECAY_RANGE = 1  # in chunks

scroll = [0, 0]

DEFAULT_P_COLOR = (100, 100, 100)

DEFAULT_BLOCK_HARDNESS = 10
BG_BLOCKS = ['air', 'base_bg', 'woofram_bg', 'vexium_bg', 'iskallium_bg']
BLOCK_HARDNESS = {
    'dirt': 10,
    'stone': 40,
    'grass': 10,
    'grass_top': 10,
    'air': 1,
    'shop': 160,
    'ladder': 10,
    'bed': 160,
    'bedrock': 100,
    'deepslate': 40,
    'roof': 40,
    'rocks': 40,
    'slimium': 10,
    'iskallium_grass_top': 10,
    'vexium_grass_top': 10,
    'woofram_grass_top': 10,
}

BLOCK_DROPS = {
    'rocks': 'rocks',
    'stones': 'rocks',
    'grass': 'grass',
    'dirt': 'dirt',
    'stone': 'stone',
    'wall': 'rocks',
    'roof': 'roof',
    'slimium': 'slimium',
}

GENS = {
    'iron': [80, 32],
    'gold': [40, 16],
    'diamond': [20, 6],
    'emerald': [20, 2],
}

TOOL_SPEEDS = {
    'diamond_pickaxe': 8,
    'hatchet': 2,
    'stone_pickaxe': 4,
    'hand': 1,
}

WEAPON_DAMAGE = {
    'pickaxe': 4,
    'hand': 1,
    'stick': 1.5,
    'knife': 4,
    'sword': 20,
    'pistol': 1
}

COLORS = {
 "dark_gray": (200, 200, 200),
 'gray': (150, 150, 150),
 'brown': (114, 70, 27),
 'woofram': (216, 193, 41),
 'vexium': (32, 115, 179),
 'dark_green': (67, 114, 21),
 'iskallium':  (52, 192, 36),
 'white':  (255, 255, 255),
 'red':  (200, 50, 50),
 'black': (1, 1, 1),
}

WHITE = (255, 255, 255)
L_GRAY = (150, 150, 150)

PROJECTILE_TYPES = {        # 0.45 for vel is fine, smaller = faster
    'bullet':    {'ad': 1, 'block_dmg': 5, 'size': 5, 'range': 60, 'vel': 0.49,
                  'auto': True, 'penetration': 3, 'blast_radius': None},
    'fire_ball': {'ad': 4, 'block_dmg': 50, 'size': 12, 'range': 520, 'vel': 0.59,
                  'auto': False, 'penetration': 5, 'blast_radius': 4},
    'mutant': {'ad': 10, 'block_dmg': 200, 'size': 20, 'range': 1028, 'vel': 0.59,
                  'auto': False, 'penetration': 15, 'blast_radius': 8},
}

''' Water physics '''
WAVE_LENGTH = 10  # in pixels PLS have mercy for FPS (smaller wave = less FPS)
DAMPENING = 0.01  # spring clearance (how quickly the water pulls itself together)(
TENSION = 0.01  # spring pulling strength
GPU = False  # Leverage GPU to accelerate cubic extrapolate calculations in C++ to smoothen curves (say goodbye to FPS)

''' Item lists '''
TOOLS = ['pickaxe', 'pistol', 'knife', 'sword', 'stick', 'stone_pickaxe', 'diamond_pickaxe', 'hatchet']
GUNS = {'pistol': 'bullet', 'fire_ball': 'fire_ball'}
NO_HITBOX = ['air', 'wall']
ARMOR = ['boots', 'jump_boots', 'speed_boots', 'leather_chestplate', 'iron_chestplate', 'diamond_chestplate',
         'leather_helmet', 'vision_helmet', 'astro_helmet', 'wings']

''' Enemy attributes '''
ENEMIES = {'warwick': {'respawn_time': sec(10), 'count_per_bed': 3, 'attack_range': 0.9,
                       'speed': 2, 'jump_h': 4, 'ad': 1},
           'vex': {'respawn_time': sec(7), 'count_per_bed': 1, 'attack_range': .5, 'speed': 1, 'ad': .5},
           'i_vex': {'respawn_time': sec(3), 'count_per_bed': 2, 'attack_range': .5, 'speed': 2, 'ad': 2},
           'i_warwick': {'respawn_time': sec(5), 'count_per_bed': 3, 'attack_range': 1.1,
                         'speed': 4, 'jump_h': 6, 'ad': 4},
           }

DRAKES = {'first': {'block_dmg': 0.5, 'speed': 0.7, "ad": 3, 'hp': 70,
                    'spawned': False, 'spawn_time': sec(120), 'shoot': False},

          'second': {'block_dmg': 1, 'speed': 0.7, "ad": 4, 'hp': 120,
                     'spawned': False, 'spawn_time': sec(240),
                     'shoot': True, 'proj': 'bullet'},

          'third': {'block_dmg': 2, 'speed': 0.8, "ad": 10, 'hp': 300,
                    'spawned': False, 'spawn_time': sec(480),
                    'shoot': True, 'proj': 'fire_ball'},


          'elder': {'block_dmg': 5, 'speed': 0.9, "ad": 15, 'hp': 777,
                    'spawned': False, 'spawn_time': sec(777),
                    'shoot': True, 'proj': 'mutant'},
          }

''' 

    Shops <------
 
'''
shop_sortiment = [
  {1: ['slimium', 16, [4, 'iron']],      2: ['stone', 16, [8, 'iron']],  3: ['stick', 1, [12, 'iron']],
   4: ['hatchet', 1, [12, 'iron']],
   5: ['boots', 1, [12, 'iron'], ['boots', .02, 0, 0]],
   6: ['leather_chestplate', 1, [32, 'iron'], ['chest', .05]],
   7: ['leather_helmet', 1, [16, 'iron'], ['helmet', .03]],
   8: ['fire_ball', 1, [40, 'iron']]},

  {1: ['bedrock', 16, [1, 'emerald']],     2: ['pistol', 32, [4, 'gold']], 3: ['knife', 1, [3, 'gold']],
   4: ['stone_pickaxe', 1, [4, 'gold']],
   5: ['speed_boots', 1, [12, 'gold'], ['boots', .15, 1, 0]],
   6: ['iron_chestplate', 1, [16, 'gold'], ['chest', .35]],
   7: ['vision_helmet', 1, [6, 'gold'], ['helmet', .12]],
   8: ['wings', 1, [16, 'emerald'], ['chest', 0]]},

  {1: ['ladder', 8, [1, 'gold']],   2: ['pistol', 64, [1, 'emerald']], 3: ['sword', 1, [2, 'emerald']],
   4: ['diamond_pickaxe', 1, [1, 'emerald']],
   5: ['jump_boots', 1, [4, 'emerald'], ['boots', .2, 1, 4, ]],
   6: ['diamond_chestplate', 1, [8, 'emerald'], ['chest', .55]],
   7: ['astro_helmet', 1, [2, 'emerald'], ['helmet', .15]],
   8: ['fire_ball', 4, [6, 'gold']]},
]

upgrades_sortiment = [
  # def
  {1: ['speed', 1, [1, 'diamond', 2], ['base', 'speed', 0.5]],
   2: ['gen', 1, [2, 'diamond', 2], ['base', 'gen', 0.1]],
   3: ['sharp', 1, [2, 'diamond', 0.5], ['off', 'sharp', 0.3]],
   },

  {1: ['prot', 1, [3, 'diamond', 2], ['def', 'prot', 0.5]],
   2: ['tenacity', 1, [1, 'diamond', 2], ['def', 'tenacity', .15]],
   3: ['drake_debuff', 1, [1, 'diamond', 2], ['debuffs', 'drake_debuff', .12]],
   4: ['heal_pool', 1, [1, 'diamond', 2], ['base', 'heal_pool', .12]],
   },

  {1: ['slow', 1, [1, 'diamond', 0.1], ['debuffs', 'slow', 0.08]],
   2: ['base_time', 1, [1, 'diamond', 2], ['util', 'base_time', 0.18]],
   3: ['trap', 1, [2, 'diamond', 2], ['debuffs', 'trap', .15]],
   4: ['haste', 1, [1, 'diamond', 0.5], ['off', 'haste', 0.25]],
  },
]

BLOCK_COLORS = {
 'grass_top': COLORS['dark_green'],
 'deepslate': COLORS['black'],
 'wood': COLORS['brown'],
 'gen': COLORS['gray'],
 'shop': COLORS['brown'],
 'roof': COLORS['red'],
 'ladder': COLORS['brown'],
 'bed': COLORS['woofram'],
 'upgrade_shop': COLORS['brown'],
 'grass': COLORS['brown'],
 'stone': COLORS['gray'],
 'bedrock': COLORS['iskallium'],
 'slimium': COLORS['iskallium'],
 'ww_bed': COLORS['dark_gray'],

 'vex_bed': COLORS['dark_gray'],
 'vexium_stones': COLORS['vexium'],
 'vexium_rocks': COLORS['vexium'],

 'door_top': COLORS['brown'],
 'door''gen': COLORS['brown'],
 'woofram_rocks': COLORS['woofram'],
 'woofram_wall': COLORS['woofram'],
 'woofram_stones': COLORS['woofram'],
 'woofram_grass_top': COLORS['woofram'],

 'iskallium_stones': COLORS['iskallium'],
 'iskallium_rocks': COLORS['iskallium'],
 'iskallium_wall': COLORS['iskallium'],
 'iskallium_roof': COLORS['iskallium'],
 'iskallium_grass_top': COLORS['iskallium'],
 'iskallium_dirt': COLORS['brown'],
 'iskallium_stone': COLORS['gray'],
 'rocks': COLORS['gray'],
}

STATUS_EFFECTS = [
    ['def', 'prot'],
    ['def', 'tenacity'],
    None,
    ['base', 'speed'],
    ['base', 'gen'],
    ['base', 'heal_pool'],
    None,
    ['debuffs', 'trap'],
    ['debuffs', 'drake_debuff'],
    ['debuffs', 'slow'],
    None,
    ['util', 'base_time'],
    None,
    ['off', 'sharp'],
    ['off', 'haste'],
]

PLAYER_STATS = {
    'sealable': {
        'starting_item': ['hatchet', 1, [4, 'gold']],
        #  'starting_item': ['stone_pickaxe', 1, [4, 'gold']],
        'jumps': 2,
        'hp': 20,
        'speed': 2,
        'jump_h': 5,
        'sharp': .1,
        'haste': .5,
        'tenacity': .1,
        'protection': 0.1,
        'climbing_speed': 3,

    },
'hopper': {
        'starting_item': ['slimium', 16, [4, 'iron']],
        'jumps': 1,
        'hp': 30,
        'speed': 2,
        'jump_h': 4,
        'sharp': 0,
        'haste': 0,
        'tenacity': .5,
        'protection': 0.4,
        'climbing_speed': 1,
    },
    'sivir': {
        'starting_item': ['stick', 1, [4, 'iron']],
        'jumps': 2,
        'hp': 15,
        'speed': 3,
        'jump_h': 7,
        'sharp': .2,
        'haste': 0,
        'tenacity': 0,
        'protection': 0,
        'climbing_speed': 4,
    },
}

effects = {'money': {'iron': ['iron', 4, WHITE],
'gold': ['gold', 456, WHITE],
'diamond': ['diamond', 0, WHITE],
'emerald': ['emerald', 0, WHITE], },

'effects': {'speed': ['speed_boots', 'Speed', (100, 100, 100), 0, [2, 0, 0]],
            'jump_height': ['jump_boots', 'Jump height', (100, 100, 100), 0, [5, 0, 0]],
            'fly': ['wings', 'Fly enabled', (100, 100, 100), False, 0]},

'off': {'sharp': ['boots', '  Sharpness', (100, 100, 100), 0, 0],
        'haste': ['boots', '  Mining haste', (100, 100, 100), 0, 0],
        'shield': ['boots', 'normal', (100, 100, 100), 0, 0]},

'def': {'prot': ['prot', '  Protection', (20, 120, 20), 0, 0],  # (last is level)
        'health': ['boots', 'normal', (100, 100, 100), 1, 0],
        'tenacity': ['boots', '  Tenacity', (20, 20, 120), 0, 0]},

'armor': {'helmet': ['empty_helmet', ' Helmet', (100, 100, 100), 0, 0],
        'chest': ['empty_chestplate', ' Chestplate', (100, 100, 100), 0, 0],
        'boots': ['empty_boots', ' Boots', (100, 100, 100), 0, 0]},

'debuffs': {'slow': ['boots', '  Enemy slowness', (100, 100, 100), 0, 0],
        'drake_debuff': ['boots', '  Drake debuff', (100, 100, 100), 0, 0],
        'trap': ['boots', '  Trap', (100, 100, 100), 0, 0]},

'base': {'speed': ['speed_boots', '  Speed boost', (100, 100, 100), 0, 0],
        'gen': ['gen', '  Base gen speed', (100, 100, 100), 1, 0, 0],
        'heal_pool': ['heal_pool', '  Heal pool', (100, 100, 100), 0, 0]},

'util': {'base_time': ['boots', '  Base timer', (100, 100, 100), 0, 0],
        'drake_debuff': ['boots', 'normal', (100, 100, 100), 0, 0],
        'pool': ['boots', 'normal', (100, 100, 100), 0, 0]},
}

WINGS = False
FULL_SCREEN = True