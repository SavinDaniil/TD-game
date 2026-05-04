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

START_HP = 100
START_COINS = 250
MAX_WAVE = 20

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
            (6, 1),
            (6, 3),
            (9, 2),
            (9, 5),
            (10, 5),
            (12, 2),
            (12, 4),
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

TOWER_TYPES = ["basic", "sniper", "cannon"]

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
        "range": 130,
        "attack_speed": 0.55,
        "target_type": "ground",
        "upgrade_cost": 80,
        "color": RED,
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
