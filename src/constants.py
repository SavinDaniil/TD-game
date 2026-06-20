import os


WIDTH = 1280
HEIGHT = 720
FPS = 60

GRID_COLS = 16
GRID_ROWS = 9
TILE_SIZE = 58
MAP_OFFSET_X = 24
MAP_OFFSET_Y = 58
MAP_WIDTH = GRID_COLS * TILE_SIZE
MAP_HEIGHT = GRID_ROWS * TILE_SIZE

PANEL_X = 970
PANEL_WIDTH = WIDTH - PANEL_X - 22

SAVE_PATH = os.path.join("data", "save.json")
MUSIC_DIR = os.path.join("data", "music")

START_HP = 100
START_COINS = 250
MAX_WAVE = 20
SPEED_OPTIONS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

LEVEL_DATA = {
    1: {
        "name": "Level 1",
        "waves": 10,
        "enemy_multiplier": 1.0,
        "path_nodes": [
            (0, 4),
            (4, 4),
            (4, 2),
            (8, 2),
            (8, 6),
            (11, 6),
            (11, 3),
            (15, 3),
        ],
        "tower_slots": {
            (1, 2),
            (1, 6),
            (2, 3),
            (2, 5),
            (3, 2),
            (3, 6),
            (5, 1),
            (5, 3),
            (5, 5),
            (6, 1),
            (6, 3),
            (7, 1),
            (7, 3),
            (7, 6),
            (9, 2),
            (9, 5),
            (9, 7),
            (10, 2),
            (10, 5),
            (10, 7),
            (12, 2),
            (12, 4),
            (13, 2),
            (13, 4),
            (14, 2),
            (14, 4),
        },
    },
    2: {
        "name": "Level 2",
        "waves": 15,
        "enemy_multiplier": 1.35,
        "path_nodes": [
            (0, 2),
            (3, 2),
            (3, 6),
            (6, 6),
            (6, 1),
            (10, 1),
            (10, 5),
            (13, 5),
            (13, 3),
            (15, 3),
        ],
        "tower_slots": {
            (1, 1),
            (1, 3),
            (2, 1),
            (2, 5),
            (4, 2),
            (4, 5),
            (4, 7),
            (5, 2),
            (5, 5),
            (7, 2),
            (7, 6),
            (8, 0),
            (8, 2),
            (8, 6),
            (9, 3),
            (9, 6),
            (11, 2),
            (11, 4),
            (11, 6),
            (12, 2),
            (12, 4),
            (14, 2),
            (14, 4),
        },
    },
    3: {
        "name": "Level 3",
        "waves": 20,
        "enemy_multiplier": 1.65,
        "path_nodes": [
            (0, 6),
            (2, 6),
            (2, 1),
            (5, 1),
            (5, 4),
            (8, 4),
            (8, 7),
            (12, 7),
            (12, 2),
            (15, 2),
        ],
        "tower_slots": {
            (1, 5),
            (1, 7),
            (3, 0),
            (3, 2),
            (3, 5),
            (4, 0),
            (4, 2),
            (4, 5),
            (6, 2),
            (6, 5),
            (7, 3),
            (7, 5),
            (9, 3),
            (9, 6),
            (9, 8),
            (10, 3),
            (10, 6),
            (10, 8),
            (11, 1),
            (11, 3),
            (11, 6),
            (13, 1),
            (13, 3),
            (14, 1),
            (14, 3),
        },
    },
}

BLACK = (7, 9, 18)
BACKGROUND = (13, 16, 29)
GRID_LINE = (28, 34, 54)
ROAD = (42, 55, 75)
ROAD_EDGE = (68, 93, 126)
PANEL = (18, 23, 38)
PANEL_LIGHT = (32, 39, 60)
TEXT = (224, 232, 246)
MUTED_TEXT = (142, 153, 178)
GREEN = (78, 220, 128)
RED = (242, 82, 96)
YELLOW = (255, 201, 64)
CYAN = (59, 222, 220)
ORANGE = (255, 155, 59)
PURPLE = (178, 102, 255)
BLUE = (86, 160, 255)
WHITE = (245, 248, 255)

TOWER_TYPES = ["basic", "sniper", "cannon", "freeze", "anti_air", "splash"]

TOWER_DATA = {
    "basic": {
        "name": "Basic",
        "cost": 50,
        "damage": 10,
        "range": 120,
        "attack_speed": 1.0,
        "target_type": "ground",
        "upgrade_cost": 45,
        "color": CYAN,
    },
    "sniper": {
        "name": "Sniper",
        "cost": 120,
        "damage": 55,
        "range": 260,
        "attack_speed": 0.35,
        "target_type": "ground",
        "upgrade_cost": 95,
        "color": GREEN,
    },
    "cannon": {
        "name": "Cannon",
        "cost": 100,
        "damage": 22,
        "range": 100,
        "attack_speed": 0.55,
        "target_type": "ground",
        "upgrade_cost": 80,
        "color": RED,
    },
    "freeze": {
        "name": "Freeze",
        "cost": 90,
        "damage": 0,
        "range": 110,
        "attack_speed": 1.0,
        "target_type": "ground",
        "upgrade_cost": 70,
        "color": (116, 224, 255),
    },
    "anti_air": {
        "name": "Anti-air",
        "cost": 85,
        "damage": 18,
        "range": 150,
        "attack_speed": 1.4,
        "target_type": "air",
        "upgrade_cost": 75,
        "color": ORANGE,
    },
    "splash": {
        "name": "Splash",
        "cost": 110,
        "damage": 8,
        "range": 150,
        "attack_speed": 0.8,
        "target_type": "ground",
        "upgrade_cost": 85,
        "color": PURPLE,
    },
}

UPGRADE_INFO = {
    "max_hp": {"name": "Max HP", "base_cost": 60, "step": 45, "max": 10},
    "damage_bonus": {
        "name": "Tower Damage Bonus",
        "base_cost": 75,
        "step": 60,
        "max": 10,
    },
    "attack_speed_bonus": {
        "name": "Tower Attack Speed Bonus",
        "base_cost": 75,
        "step": 60,
        "max": 10,
    },
    "start_coins": {
        "name": "Start Coins",
        "base_cost": 55,
        "step": 45,
        "max": 10,
    },
    "kill_reward_bonus": {
        "name": "Kill Reward Bonus",
        "base_cost": 70,
        "step": 55,
        "max": 10,
    },
}

# Усиление врагов
WAVE_HP_SCALE = 0.13
WAVE_SPEED_SCALE = 0.015
WAVE_REWARD_SCALE = 0.07

# Усиление башен
LEVEL_UP_DAMAGE_MULTIPLIER_EARLY = 1.05
LEVEL_UP_DAMAGE_MULTIPLIER_LATE = 1.01
LEVEL_UP_RANGE_MULTIPLIER = 1.01
LEVEL_UP_SPEED_MULTIPLIER_EARLY = 1.015
LEVEL_UP_SPEED_MULTIPLIER_LATE = 1.01

# Прокачка башен
UPGRADE_DAMAGE_MULTIPLIER = 1.18
UPGRADE_RANGE_MULTIPLIER = 1.05
UPGRADE_SPEED_MULTIPLIER = 1.07
UPGRADE_COST_MULTIPLIER = 1.42

# Настройки снарядов
DIRECTIONAL_LIFETIME = 1.5
HOMING_LIFETIME = 3.0
HIT_DISTANCE = 14
EXP_DAMAGE_RATIO = 0.12
EXP_KILL_BONUS = 12

# Настройки волн
BASE_SPAWN_DELAY = 0.65
BASE_ENEMY_COUNT = 7
FAST_WAVE_THRESHOLD = 3
STRONG_WAVE_THRESHOLD = 6
ARMORED_WAVE_THRESHOLD = 8
AIR_WAVE_THRESHOLD = 10

# Настройки отрисовки карты
ROAD_EDGE_WIDTH = 51
ROAD_WIDTH = 39
TOWER_SLOT_RADIUS = 15
START_POINT_RADIUS = 12
END_POINT_RADIUS = 15
START_COLOR = (80, 245, 150)
END_COLOR = (245, 80, 115)

# Настройки игрока
HP_PER_UPGRADE = 12
COINS_PER_UPGRADE = 30
DAMAGE_BONUS_PER_LEVEL = 0.04
SPEED_BONUS_PER_LEVEL = 0.035
REWARD_BONUS_PER_LEVEL = 0.08
META_COIN_RATIO = 3

# Настройки UI
BUTTON_Y_START = 112
BUTTON_HEIGHT = 42
TOWER_BUTTON_Y_START = 194
TOWER_BUTTON_HEIGHT = 31
TOWER_BUTTON_SPACING = 36
UPGRADE_BUTTON_Y = 512
ABILITY_BUTTON_Y_START = 556
ABILITY_BUTTON_HEIGHT = 30
ABILITY_BUTTON_SPACING = 34
UPGRADE_WIDTH = 520
BACK_BUTTON_WIDTH = 160
BACK_BUTTON_HEIGHT = 40
PAUSE_MENU_WIDTH = 440
PAUSE_MENU_HEIGHT = 360

# Настройки башен
BASE_SPLASH_RADIUS = 55
BASE_SLOW_FACTOR = 0.65
BASE_SLOW_DURATION = 1.0
BASE_PROJECTILE_COUNT = 8
BASE_PROJECTILE_SPEED = 330
SNIPER_PROJECTILE_SPEED = 560
CANNON_PROJECTILE_SPEED = 260
ANTI_AIR_PROJECTILE_SPEED = 430
TOWER_INITIAL_COOLDOWN_MAX = 0.25
TOWER_MAX_LEVEL = 20
TOWER_MAX_UPGRADE_LEVEL = 10
TOWER_FIRST_ABILITY_LEVEL = 4
TOWER_SECOND_ABILITY_LEVEL = 7
TOWER_AUTO_ABILITY_LEVEL = 10
TOWER_ULTIMATE_LEVEL = 20
TOWER_DRAW_RADIUS = 25
TOWER_DRAW_INNER_RADIUS = 22
TOWER_SELECTED_RADIUS = 27
TOWER_RANGE_FILL_ALPHA = 34
TOWER_RANGE_BORDER_ALPHA = 90
BUILD_PREVIEW_FILL_ALPHA = 28
BUILD_PREVIEW_BORDER_ALPHA = 105
BUILD_PREVIEW_CORE_ALPHA = 85
BUILD_PREVIEW_CORE_RADIUS = 24

# Шрифты
TITLE_FONT_SIZE = 42
WIDGET_FONT_SIZE = 28
WIDGET_MARGIN = (0, 14)
