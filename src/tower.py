import math
import random

import pygame

from src.constants import TOWER_DATA, WHITE
from src.projectile import Projectile
from src.utils import distance, regular_polygon


ABILITY_TEXT = {
    "basic": ["Faster attack", "More damage", "Fast projectiles"],
    "sniper": ["Crit chance", "Crit damage", "Faster aim"],
    "cannon": ["Blast radius", "Blast damage", "Burn"],
    "freeze": ["Harder slow", "More range", "Longer slow"],
    "anti_air": ["Air damage", "Fast rockets", "Two targets"],
    "splash": ["More shots", "Shot speed", "More damage"],
}


class Tower:
    tower_type = "basic"

    def __init__(self, cell, position, player):
        data = TOWER_DATA[self.tower_type]
        self.cell = cell
        self.position = position
        self.player = player
        self.name = data["name"]
        self.cost = data["cost"]
        self.level = 1
        self.experience = 0
        self.damage = data["damage"] * player.damage_multiplier
        self.range = data["range"]
        self.attack_speed = data["attack_speed"] * player.speed_multiplier
        self.target_type = data["target_type"]
        self.upgrade_level = 1
        self.upgrade_cost = data["upgrade_cost"]
        self.selected_abilities = []
        self.color = data["color"]
        self.cooldown = random.random() * 0.25
        self.projectile_speed = 330
        self.power_multiplier = 1
        self.ultimate_used = False

    @property
    def next_level_exp(self):
        return 35 + self.level * 18

    @property
    def ability_options(self):
        return ABILITY_TEXT[self.tower_type]

    def update(self, dt, enemies, projectiles, game_map=None, towers=None):
        self.cooldown -= dt
        if self.cooldown <= 0:
            target = self.find_target(enemies)
            if target:
                self.shoot(target, enemies, projectiles)
                self.cooldown = 1 / max(0.1, self.attack_speed)

    def can_target(self, enemy):
        if self.target_type == "both":
            return True
        if self.target_type == "air":
            return enemy.is_flying
        return not enemy.is_flying

    def find_target(self, enemies):
        possible = [
            enemy
            for enemy in enemies
            if enemy.alive
            and self.can_target(enemy)
            and distance(self.position, enemy.position) <= self.range
        ]
        if not possible:
            return None
        return max(possible, key=lambda enemy: enemy.path_index)

    def shoot(self, target, enemies, projectiles):
        projectiles.append(
            Projectile(
                self.position,
                target,
                self.projectile_speed,
                self.damage * self.power_multiplier,
                self.color,
                owner=self,
                damage_type=self.tower_type,
            )
        )

    def gain_exp(self, amount):
        if self.level >= 20:
            return
        self.experience += amount
        while self.level < 20 and self.experience >= self.next_level_exp:
            self.experience -= self.next_level_exp
            self.level_up()

    def level_up(self):
        self.level += 1
        if self.level <= 10:
            self.damage *= 1.05
            self.range *= 1.01
            self.attack_speed *= 1.015
        else:
            self.damage *= 1.01
            self.range *= 1.01
            self.attack_speed *= 1.01

        if self.level == 10:
            self.select_ability(2)
        if self.level == 20:
            self.select_final_ability(powerful=False)

    def needs_ability_choice(self):
        if self.level >= 7 and len(self.selected_abilities) < 2:
            return "normal"
        if self.level >= 4 and len(self.selected_abilities) < 1:
            return "normal"
        return None

    def select_ability(self, index):
        if index < 0 or index >= len(self.ability_options):
            return
        ability = self.ability_options[index]
        if ability in self.selected_abilities:
            return
        self.selected_abilities.append(ability)
        self.apply_ability(ability)

    def select_final_ability(self, powerful=False):
        if "ultimate" in self.selected_abilities or "powerful" in self.selected_abilities:
            return
        if powerful:
            self.selected_abilities.append("powerful")
            self.damage *= 1.1
            self.range *= 1.06
            self.attack_speed *= 1.08
        else:
            self.selected_abilities.append("ultimate")

    def apply_ability(self, ability):
        if "Faster" in ability or "Fast" in ability:
            self.attack_speed *= 1.15
            self.projectile_speed *= 1.12
        if "damage" in ability.lower() or "Crit damage" in ability:
            self.damage *= 1.18
        if "range" in ability.lower():
            self.range *= 1.15

    def upgrade(self, player):
        if self.upgrade_level >= 10:
            return False
        if not player.spend(self.upgrade_cost):
            return False
        self.upgrade_level += 1
        self.damage *= 1.18
        self.range *= 1.05
        self.attack_speed *= 1.07
        self.upgrade_cost = int(self.upgrade_cost * 1.42)
        return True

    def draw_range(self, surface):
        alpha = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(
            alpha,
            (*self.color[:3], 34),
            (int(self.position[0]), int(self.position[1])),
            int(self.range),
        )
        pygame.draw.circle(
            alpha,
            (*self.color[:3], 90),
            (int(self.position[0]), int(self.position[1])),
            int(self.range),
            2,
        )
        surface.blit(alpha, (0, 0))

    def draw(self, surface, selected=False):
        pygame.draw.circle(surface, (10, 13, 24), self.position, 25)
        pygame.draw.circle(surface, self.color, self.position, 22, 3)
        if selected:
            pygame.draw.circle(surface, WHITE, self.position, 27, 2)


class BasicTower(Tower):
    tower_type = "basic"

    def draw(self, surface, selected=False):
        points = regular_polygon(self.position, 24, 4, math.pi / 4)
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.circle(surface, (20, 35, 48), self.position, 10)
        pygame.draw.circle(surface, WHITE, self.position, 5)
        if selected:
            pygame.draw.circle(surface, WHITE, self.position, 30, 2)


class SniperTower(Tower):
    tower_type = "sniper"

    def shoot(self, target, enemies, projectiles):
        damage = self.damage
        if "Crit chance" in self.selected_abilities and random.random() < 0.25:
            damage *= 2.2 if "Crit damage" in self.selected_abilities else 1.7
        if "ultimate" in self.selected_abilities:
            strongest = max(
                [enemy for enemy in enemies if enemy.alive and not enemy.is_flying],
                key=lambda enemy: enemy.hp,
                default=target,
            )
            if strongest.enemy_type == "boss" and random.random() < 0.12:
                damage *= 4
                target = strongest
        projectiles.append(
            Projectile(
                self.position,
                target,
                560,
                damage,
                self.color,
                owner=self,
                damage_type="sniper",
            )
        )

    def draw(self, surface, selected=False):
        x, y = int(self.position[0]), int(self.position[1])
        pygame.draw.polygon(
            surface,
            self.color,
            regular_polygon(self.position, 26, 3, -math.pi / 2),
        )
        barrel = [(x - 3, y + 11), (x - 3, y - 17), (x + 3, y - 17), (x + 3, y + 11)]
        pygame.draw.polygon(surface, WHITE, barrel)
        pygame.draw.line(surface, (36, 72, 44), (x, y - 14), (x, y + 8), 1)
        if selected:
            pygame.draw.circle(surface, WHITE, self.position, 31, 2)


class CannonTower(Tower):
    tower_type = "cannon"

    def __init__(self, cell, position, player):
        super().__init__(cell, position, player)
        self.splash_radius = 55
        self.shots = 0

    def apply_ability(self, ability):
        super().apply_ability(ability)
        if "Blast radius" in ability:
            self.splash_radius *= 1.25
        if "Blast damage" in ability:
            self.damage *= 1.2

    def shoot(self, target, enemies, projectiles):
        self.shots += 1
        radius = self.splash_radius
        damage = self.damage
        if "ultimate" in self.selected_abilities and self.shots % 5 == 0:
            radius *= 1.8
            damage *= 1.8
        projectile = Projectile(
            self.position,
            target,
            260,
            damage,
            self.color,
            owner=self,
            radius=radius,
            is_splash=True,
            damage_type="explosion",
        )
        projectiles.append(projectile)
        if "Burn" in self.selected_abilities:
            target.burn_timer = 2.0

    def draw(self, surface, selected=False):
        pygame.draw.polygon(surface, self.color, regular_polygon(self.position, 25, 5))
        pygame.draw.polygon(
            surface,
            (255, 154, 154),
            regular_polygon(self.position, 12, 5),
        )
        if selected:
            pygame.draw.circle(surface, WHITE, self.position, 31, 2)


class FreezeTower(Tower):
    tower_type = "freeze"

    def __init__(self, cell, position, player):
        super().__init__(cell, position, player)
        self.slow = 0.65
        self.duration = 1.0
        self.pulse = 0

    def apply_ability(self, ability):
        super().apply_ability(ability)
        if "Harder slow" in ability:
            self.slow = 0.52
        if "Longer slow" in ability:
            self.duration = 1.7

    def update(self, dt, enemies, projectiles, game_map=None, towers=None):
        self.pulse += dt
        for enemy in enemies:
            if (
                enemy.alive
                and not enemy.is_flying
                and distance(self.position, enemy.position) <= self.range
            ):
                hard_stop = (
                    "ultimate" in self.selected_abilities
                    and random.random() < 0.002
                    and enemy.enemy_type != "boss"
                )
                enemy.apply_slow(self.slow, self.duration, hard_stop)
                if self.damage > 0:
                    dealt = enemy.take_damage(self.damage * dt, "freeze")
                    self.gain_exp(dealt * 0.08)

    def draw(self, surface, selected=False):
        pygame.draw.polygon(
            surface,
            self.color,
            regular_polygon(self.position, 25, 6, math.pi / 6),
        )
        for angle in range(0, 180, 45):
            rad = math.radians(angle)
            dx = math.cos(rad) * 14
            dy = math.sin(rad) * 14
            pygame.draw.line(
                surface,
                WHITE,
                (self.position[0] - dx, self.position[1] - dy),
                (self.position[0] + dx, self.position[1] + dy),
                2,
            )
        if selected:
            pygame.draw.circle(surface, WHITE, self.position, 31, 2)


class AntiAirTower(Tower):
    tower_type = "anti_air"

    def shoot(self, target, enemies, projectiles):
        targets = [target]
        if "Two targets" in self.selected_abilities:
            others = [
                enemy
                for enemy in enemies
                if enemy.alive
                and enemy.is_flying
                and enemy is not target
                and distance(self.position, enemy.position) <= self.range
            ]
            targets += others[:1]
        if "ultimate" in self.selected_abilities and random.random() < 0.08:
            targets = [
                enemy
                for enemy in enemies
                if enemy.alive
                and enemy.is_flying
                and distance(self.position, enemy.position) <= self.range
            ]
        for enemy in targets:
            projectiles.append(
                Projectile(
                    self.position,
                    enemy,
                    430,
                    self.damage,
                    self.color,
                    owner=self,
                    damage_type="air",
                )
            )

    def draw(self, surface, selected=False):
        pygame.draw.polygon(surface, self.color, regular_polygon(self.position, 24, 6))
        arrow = [
            (self.position[0], self.position[1] - 15),
            (self.position[0] + 10, self.position[1] + 4),
            (self.position[0] + 3, self.position[1] + 4),
            (self.position[0] + 3, self.position[1] + 15),
            (self.position[0] - 3, self.position[1] + 15),
            (self.position[0] - 3, self.position[1] + 4),
            (self.position[0] - 10, self.position[1] + 4),
        ]
        pygame.draw.polygon(surface, (45, 28, 5), arrow)
        if selected:
            pygame.draw.circle(surface, WHITE, self.position, 31, 2)


class SplashTower(Tower):
    tower_type = "splash"

    def __init__(self, cell, position, player):
        super().__init__(cell, position, player)
        self.projectile_count = 8

    def apply_ability(self, ability):
        super().apply_ability(ability)
        if "More shots" in ability:
            self.projectile_count += 3

    def find_target(self, enemies):
        for enemy in enemies:
            if (
                enemy.alive
                and not enemy.is_flying
                and distance(self.position, enemy.position) <= self.range
            ):
                return enemy
        return None

    def shoot(self, target, enemies, projectiles):
        count = self.projectile_count
        if "ultimate" in self.selected_abilities and random.random() < 0.15:
            for enemy in enemies:
                if enemy.alive and distance(self.position, enemy.position) <= self.range:
                    dealt = enemy.take_damage(self.damage * 3, "splash")
                    self.gain_exp(dealt * 0.15)
            count += 4
        for index in range(count):
            angle = math.tau * index / count
            direction = (math.cos(angle), math.sin(angle))
            projectiles.append(
                Projectile(
                    self.position,
                    None,
                    self.projectile_speed,
                    self.damage,
                    self.color,
                    owner=self,
                    direction=direction,
                    damage_type="splash",
                )
            )

    def draw(self, surface, selected=False):
        pygame.draw.circle(surface, self.color, self.position, 24)
        for index in range(8):
            angle = math.tau * index / 8
            end = (
                self.position[0] + math.cos(angle) * 18,
                self.position[1] + math.sin(angle) * 18,
            )
            pygame.draw.line(surface, WHITE, self.position, end, 2)
        if selected:
            pygame.draw.circle(surface, WHITE, self.position, 31, 2)


TOWER_CLASSES = {
    "basic": BasicTower,
    "sniper": SniperTower,
    "cannon": CannonTower,
    "freeze": FreezeTower,
    "anti_air": AntiAirTower,
    "splash": SplashTower,
}
