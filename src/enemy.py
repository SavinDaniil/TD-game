import math

import pygame

from src.constants import RED, WHITE
from src.utils import distance, regular_polygon


ENEMY_STATS = {
    "normal": {
        "hp": 38,
        "speed": 58,
        "reward": 12,
        "armor": 0,
        "flying": False,
        "color": (210, 218, 230),
    },
    "fast": {
        "hp": 24,
        "speed": 96,
        "reward": 14,
        "armor": 0,
        "flying": False,
        "color": (255, 214, 67),
    },
    "strong": {
        "hp": 95,
        "speed": 42,
        "reward": 24,
        "armor": 0.05,
        "flying": False,
        "color": (235, 76, 83),
    },
    "armored": {
        "hp": 78,
        "speed": 52,
        "reward": 22,
        "armor": 0.35,
        "flying": False,
        "color": (62, 88, 145),
    },
    "air": {
        "hp": 48,
        "speed": 74,
        "reward": 20,
        "armor": 0,
        "flying": True,
        "color": (92, 223, 255),
    },
    "boss": {
        "hp": 1600,
        "speed": 34,
        "reward": 260,
        "armor": 0.2,
        "flying": False,
        "color": (190, 54, 172),
    },
}


class Enemy:
    def __init__(self, path_points, enemy_type="normal", wave=1):
        stats = ENEMY_STATS[enemy_type]
        scale = 1 + (wave - 1) * 0.13
        self.path_points = path_points
        self.position = [float(path_points[0][0]), float(path_points[0][1])]
        self.path_index = 1
        self.enemy_type = enemy_type
        self.max_hp = int(stats["hp"] * scale)
        self.hp = self.max_hp
        self.speed = stats["speed"] * (1 + (wave - 1) * 0.015)
        self.reward = int(stats["reward"] * (1 + wave * 0.07))
        self.armor = stats["armor"]
        self.is_flying = stats["flying"]
        self.color = stats["color"]
        self.slow_multiplier = 1
        self.slow_timer = 0
        self.alive = True
        self.reached_base = False
        self.burn_timer = 0

    def update(self, dt):
        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.take_damage(5 * dt, "burn")

        if self.slow_timer > 0:
            self.slow_timer -= dt
        else:
            self.slow_multiplier = 1

        if self.path_index >= len(self.path_points):
            self.reached_base = True
            self.alive = False
            return

        target = self.path_points[self.path_index]
        dist = distance(self.position, target)
        move = self.speed * self.slow_multiplier * dt
        if dist <= move:
            self.position[0], self.position[1] = target
            self.path_index += 1
        else:
            dx = (target[0] - self.position[0]) / dist
            dy = (target[1] - self.position[1]) / dist
            self.position[0] += dx * move
            self.position[1] += dy * move

    def take_damage(self, amount, damage_type="normal"):
        if self.enemy_type == "armored" and damage_type != "sniper":
            amount *= 1 - self.armor
        if self.enemy_type == "boss" and damage_type in ("splash", "explosion"):
            amount *= 0.65
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
        return amount

    def apply_slow(self, multiplier, duration, hard_stop=False):
        if self.enemy_type == "boss":
            multiplier = 1 - (1 - multiplier) * 0.4
            hard_stop = False
        if hard_stop:
            multiplier = 0.03
        if multiplier < self.slow_multiplier:
            self.slow_multiplier = multiplier
            self.slow_timer = duration

    def draw(self, surface):
        x, y = int(self.position[0]), int(self.position[1])
        if self.enemy_type == "normal":
            pygame.draw.circle(surface, self.color, (x, y), 15)
        elif self.enemy_type == "fast":
            points = regular_polygon((x, y), 17, 3, -math.pi / 2)
            pygame.draw.polygon(surface, self.color, points)
        elif self.enemy_type == "strong":
            pygame.draw.rect(surface, self.color, (x - 15, y - 15, 30, 30))
        elif self.enemy_type == "armored":
            pygame.draw.polygon(surface, self.color, regular_polygon((x, y), 18, 6))
        elif self.enemy_type == "air":
            points = [(x, y - 18), (x + 18, y), (x, y + 18), (x - 18, y)]
            pygame.draw.polygon(surface, self.color, points)
        else:
            pygame.draw.polygon(surface, self.color, regular_polygon((x, y), 28, 8))
            pygame.draw.circle(surface, RED, (x, y), 13, 2)

        self.draw_hp_bar(surface, x, y)

    def draw_hp_bar(self, surface, x, y):
        width = 64 if self.enemy_type == "boss" else 34
        height = 7 if self.enemy_type == "boss" else 5
        top = y - 43 if self.enemy_type == "boss" else y - 27
        ratio = max(0, self.hp / self.max_hp)
        back = pygame.Rect(x - width // 2, top, width, height)
        front = pygame.Rect(x - width // 2, top, int(width * ratio), height)
        pygame.draw.rect(surface, (45, 47, 60), back)
        pygame.draw.rect(surface, WHITE if ratio > 0.4 else RED, front)
