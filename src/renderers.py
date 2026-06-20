import math
import pygame

from src.constants import (RED, TOWER_DRAW_INNER_RADIUS, TOWER_DRAW_RADIUS, TOWER_RANGE_BORDER_ALPHA,
                           TOWER_RANGE_FILL_ALPHA, TOWER_SELECTED_RADIUS, WHITE)
from src.tower import AntiAirTower, BasicTower, CannonTower, FreezeTower, SniperTower, SplashTower
from src.utils import regular_polygon


def draw_tower_range(surface, tower):
    alpha = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    center = (int(tower.position[0]), int(tower.position[1]))
    pygame.draw.circle(alpha, (*tower.color[:3], TOWER_RANGE_FILL_ALPHA), center, int(tower.range))
    pygame.draw.circle(alpha, (*tower.color[:3], TOWER_RANGE_BORDER_ALPHA), center, int(tower.range), 2)
    surface.blit(alpha, (0, 0))


def draw_tower(surface, tower, selected=False):
    pygame.draw.circle(surface, (10, 13, 24), tower.position, TOWER_DRAW_RADIUS)
    _draw_tower_body(surface, tower)
    if selected:
        pygame.draw.circle(surface, WHITE, tower.position, TOWER_SELECTED_RADIUS, 2)


def _draw_tower_body(surface, tower):
    if isinstance(tower, BasicTower):
        points = regular_polygon(tower.position, 24, 4, math.pi / 4)
        pygame.draw.polygon(surface, tower.color, points)
        pygame.draw.circle(surface, (20, 35, 48), tower.position, 10)
        pygame.draw.circle(surface, WHITE, tower.position, 5)
        return

    if isinstance(tower, SniperTower):
        x, y = int(tower.position[0]), int(tower.position[1])
        pygame.draw.polygon(surface, tower.color, regular_polygon(tower.position, 26, 3, -math.pi / 2))
        barrel = [(x - 3, y + 11), (x - 3, y - 17), (x + 3, y - 17), (x + 3, y + 11)]
        pygame.draw.polygon(surface, WHITE, barrel)
        pygame.draw.line(surface, (36, 72, 44), (x, y - 14), (x, y + 8), 1)
        return

    if isinstance(tower, CannonTower):
        pygame.draw.polygon(surface, tower.color, regular_polygon(tower.position, 25, 5))
        pygame.draw.polygon(surface, (255, 154, 154), regular_polygon(tower.position, 12, 5))
        return

    if isinstance(tower, FreezeTower):
        pygame.draw.polygon(surface, tower.color, regular_polygon(tower.position, 25, 6, math.pi / 6))
        for angle in range(0, 180, 45):
            rad = math.radians(angle)
            dx = math.cos(rad) * 14
            dy = math.sin(rad) * 14
            pygame.draw.line(surface, WHITE, (tower.position[0] - dx, tower.position[1] - dy),
                             (tower.position[0] + dx, tower.position[1] + dy), 2)
        return

    if isinstance(tower, AntiAirTower):
        pygame.draw.polygon(surface, tower.color, regular_polygon(tower.position, 24, 6))
        arrow = [
            (tower.position[0], tower.position[1] - 15),
            (tower.position[0] + 10, tower.position[1] + 4),
            (tower.position[0] + 3, tower.position[1] + 4),
            (tower.position[0] + 3, tower.position[1] + 15),
            (tower.position[0] - 3, tower.position[1] + 15),
            (tower.position[0] - 3, tower.position[1] + 4),
            (tower.position[0] - 10, tower.position[1] + 4)
        ]
        pygame.draw.polygon(surface, (45, 28, 5), arrow)
        return

    if isinstance(tower, SplashTower):
        pygame.draw.circle(surface, tower.color, tower.position, 24)
        for index in range(8):
            angle = math.tau * index / 8
            end = (tower.position[0] + math.cos(angle) * 18, tower.position[1] + math.sin(angle) * 18)
            pygame.draw.line(surface, WHITE, tower.position, end, 2)
        return

    pygame.draw.circle(surface, tower.color, tower.position, TOWER_DRAW_INNER_RADIUS, 3)


def draw_enemy(surface, enemy):
    x, y = int(enemy.position[0]), int(enemy.position[1])
    if enemy.enemy_type == "normal":
        pygame.draw.circle(surface, enemy.color, (x, y), 15)
    elif enemy.enemy_type == "fast":
        points = regular_polygon((x, y), 17, 3, -math.pi / 2)
        pygame.draw.polygon(surface, enemy.color, points)
    elif enemy.enemy_type == "strong":
        pygame.draw.rect(surface, enemy.color, (x - 15, y - 15, 30, 30))
    elif enemy.enemy_type == "armored":
        pygame.draw.polygon(surface, enemy.color, regular_polygon((x, y), 18, 6))
    elif enemy.enemy_type == "air":
        points = [(x, y - 18), (x + 18, y), (x, y + 18), (x - 18, y)]
        pygame.draw.polygon(surface, enemy.color, points)
    else:
        pygame.draw.polygon(surface, enemy.color, regular_polygon((x, y), 28, 8))
        pygame.draw.circle(surface, RED, (x, y), 13, 2)

    _draw_enemy_hp_bar(surface, enemy, x, y)


def _draw_enemy_hp_bar(surface, enemy, x, y):
    width = 64 if enemy.enemy_type == "boss" else 34
    height = 7 if enemy.enemy_type == "boss" else 5
    top = y - 43 if enemy.enemy_type == "boss" else y - 27
    ratio = max(0, enemy.hp / enemy.max_hp)
    back = pygame.Rect(x - width // 2, top, width, height)
    front = pygame.Rect(x - width // 2, top, int(width * ratio), height)
    pygame.draw.rect(surface, (45, 47, 60), back)
    pygame.draw.rect(surface, WHITE if ratio > 0.4 else RED, front)


def draw_projectile(surface, projectile):
    center = (int(projectile.position[0]), int(projectile.position[1]))
    pygame.draw.circle(surface, projectile.color, center, 5)
    if projectile.is_splash:
        pygame.draw.circle(surface, projectile.color[:3], center, 9, 1)
