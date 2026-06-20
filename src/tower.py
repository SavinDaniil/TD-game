import math
import random

from src.constants import (ANTI_AIR_PROJECTILE_SPEED, BASE_PROJECTILE_COUNT, BASE_PROJECTILE_SPEED, BASE_SLOW_DURATION,
                           BASE_SLOW_FACTOR, BASE_SPLASH_RADIUS, CANNON_PROJECTILE_SPEED,
                           LEVEL_UP_DAMAGE_MULTIPLIER_EARLY, LEVEL_UP_DAMAGE_MULTIPLIER_LATE, LEVEL_UP_RANGE_MULTIPLIER,
                           LEVEL_UP_SPEED_MULTIPLIER_EARLY, LEVEL_UP_SPEED_MULTIPLIER_LATE, SNIPER_PROJECTILE_SPEED,
                           TOWER_AUTO_ABILITY_LEVEL, TOWER_DATA, TOWER_FIRST_ABILITY_LEVEL, TOWER_INITIAL_COOLDOWN_MAX,
                           TOWER_MAX_LEVEL, TOWER_MAX_UPGRADE_LEVEL, TOWER_SECOND_ABILITY_LEVEL, TOWER_ULTIMATE_LEVEL,
                           UPGRADE_COST_MULTIPLIER, UPGRADE_DAMAGE_MULTIPLIER, UPGRADE_RANGE_MULTIPLIER,
                           UPGRADE_SPEED_MULTIPLIER)
from src.projectile import Projectile
from src.utils import distance

ABILITY_TEXT = [
    "Faster Attack",
    "More Damage",
    "Longer Range",
]

ABILITY_EFFECTS = {
    "Faster Attack": {"attack_speed": 1.2},
    "More Damage": {"damage": 1.25},
    "Longer Range": {"range": 1.2},
}


class Tower:
    tower_type = "basic"
    projectile_speed = BASE_PROJECTILE_SPEED

    def __init__(self, cell, position, player):
        data = TOWER_DATA[self.tower_type]
        self._cell = cell
        self.position = position
        self._player = player
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
        self._selected_abilities = []
        self.color = data["color"]
        self.cooldown = random.random() * TOWER_INITIAL_COOLDOWN_MAX
        self.power_multiplier = 1

    @property
    def cell(self):
        return self._cell

    @property
    def next_level_exp(self):
        return 35 + self.level * 18

    @property
    def ability_options(self):
        return ABILITY_TEXT

    @property
    def selected_abilities(self):
        return tuple(self._selected_abilities)

    def is_on_cell(self, cell):
        return self._cell == cell

    def has_ability(self, ability):
        return ability in self._selected_abilities

    def has_ultimate(self):
        return self.has_ability("ultimate")

    def can_upgrade(self):
        return self.upgrade_level < TOWER_MAX_UPGRADE_LEVEL

    def needs_ability_choice(self):
        if self.level >= TOWER_SECOND_ABILITY_LEVEL and len(self._selected_abilities) < 2:
            return "normal"
        if self.level >= TOWER_FIRST_ABILITY_LEVEL and len(self._selected_abilities) < 1:
            return "normal"
        return None

    def can_choose_ability(self):
        return self.needs_ability_choice() == "normal"

    def update(self, dt, session):
        self.cooldown -= dt
        if self.cooldown <= 0:
            target = self.find_target(session.enemies)
            if target:
                self.shoot(target, session)
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

    def shoot(self, target, session):
        damage = self.damage * self.power_multiplier
        session.projectiles.append(Projectile(self.position, target, self.projectile_speed, damage, self.color,
                                              owner=self, damage_type=self.tower_type))

    def gain_exp(self, amount):
        if self.level >= TOWER_MAX_LEVEL:
            return
        self.experience += amount
        while self.level < TOWER_MAX_LEVEL and self.experience >= self.next_level_exp:
            self.experience -= self.next_level_exp
            self.level_up()

    def level_up(self):
        self.level += 1
        if self.level <= 10:
            self.damage *= LEVEL_UP_DAMAGE_MULTIPLIER_EARLY
            self.range *= LEVEL_UP_RANGE_MULTIPLIER
            self.attack_speed *= LEVEL_UP_SPEED_MULTIPLIER_EARLY
        else:
            self.damage *= LEVEL_UP_DAMAGE_MULTIPLIER_LATE
            self.range *= LEVEL_UP_RANGE_MULTIPLIER
            self.attack_speed *= LEVEL_UP_SPEED_MULTIPLIER_LATE

        if self.level == TOWER_AUTO_ABILITY_LEVEL:
            self.select_remaining_ability()
        if self.level == TOWER_ULTIMATE_LEVEL and not self.has_ultimate():
            self._selected_abilities.append("ultimate")

    def select_ability(self, index):
        if index < 0 or index >= len(self.ability_options):
            return
        ability = self.ability_options[index]
        if ability in self._selected_abilities:
            return
        self._selected_abilities.append(ability)
        self.apply_ability(ability)

    def select_remaining_ability(self):
        for index, ability in enumerate(self.ability_options):
            if ability not in self._selected_abilities:
                self.select_ability(index)
                return

    def apply_ability(self, ability):
        effects = ABILITY_EFFECTS.get(ability, {})
        for attr, multiplier in effects.items():
            if hasattr(self, attr):
                current = getattr(self, attr)
                if isinstance(current, (int, float)):
                    setattr(self, attr, current * multiplier)

    def upgrade(self, player):
        if not self.can_upgrade():
            return False
        if not player.spend(self.upgrade_cost):
            return False
        self.upgrade_level += 1
        self.damage *= UPGRADE_DAMAGE_MULTIPLIER
        self.range *= UPGRADE_RANGE_MULTIPLIER
        self.attack_speed *= UPGRADE_SPEED_MULTIPLIER
        self.upgrade_cost = int(self.upgrade_cost * UPGRADE_COST_MULTIPLIER)
        return True


class BasicTower(Tower):
    tower_type = "basic"


class SniperTower(Tower):
    tower_type = "sniper"
    projectile_speed = SNIPER_PROJECTILE_SPEED

    def shoot(self, target, session):
        damage = self.damage
        if self.has_ultimate():
            strongest = max([enemy for enemy in session.enemies if enemy.alive and not enemy.is_flying],
                            key=lambda enemy: enemy.hp, default=target)
            if strongest.enemy_type == "boss" and random.random() < 0.2:
                damage *= 4
                target = strongest

        session.projectiles.append(
            Projectile(
                self.position,
                target,
                self.projectile_speed,
                damage,
                self.color,
                owner=self,
                damage_type="sniper",
            )
        )


class CannonTower(Tower):
    tower_type = "cannon"
    projectile_speed = CANNON_PROJECTILE_SPEED

    def __init__(self, cell, position, player):
        super().__init__(cell, position, player)
        self.splash_radius = BASE_SPLASH_RADIUS
        self.shots = 0

    def shoot(self, target, session):
        self.shots += 1
        radius = self.splash_radius
        damage = self.damage
        if self.has_ultimate() and self.shots % 5 == 0:
            radius *= 1.8
            damage *= 1.8

        session.projectiles.append(
            Projectile(
                self.position,
                target,
                self.projectile_speed,
                damage,
                self.color,
                owner=self,
                radius=radius,
                is_splash=True,
                damage_type="explosion",
            )
        )


class FreezeTower(Tower):
    tower_type = "freeze"

    def __init__(self, cell, position, player):
        super().__init__(cell, position, player)
        self.slow = BASE_SLOW_FACTOR
        self.duration = BASE_SLOW_DURATION
        self.pulse = 0

    def update(self, dt, session):
        self.pulse += dt
        for enemy in session.enemies:
            if enemy.alive and not enemy.is_flying and distance(self.position, enemy.position) <= self.range:
                hard_stop = self.has_ultimate() and random.random() < 0.002 and enemy.enemy_type != "boss"
                enemy.apply_slow(self.slow, self.duration, hard_stop)
                if self.damage > 0:
                    dealt = enemy.take_damage(self.damage * dt, "freeze")
                    self.gain_exp(dealt * 0.08)


class AntiAirTower(Tower):
    tower_type = "anti_air"
    projectile_speed = ANTI_AIR_PROJECTILE_SPEED

    def shoot(self, target, session):
        targets = [target]
        if self.has_ultimate() and random.random() < 0.15:
            targets = [
                enemy
                for enemy in session.enemies
                if enemy.alive and enemy.is_flying and distance(self.position, enemy.position) <= self.range
            ]

        for enemy in targets:
            session.projectiles.append(
                Projectile(
                    self.position,
                    enemy,
                    self.projectile_speed,
                    self.damage,
                    self.color,
                    owner=self,
                    damage_type="air",
                )
            )


class SplashTower(Tower):
    tower_type = "splash"

    def __init__(self, cell, position, player):
        super().__init__(cell, position, player)
        self.projectile_count = BASE_PROJECTILE_COUNT

    def find_target(self, enemies):
        for enemy in enemies:
            if enemy.alive and not enemy.is_flying and distance(self.position, enemy.position) <= self.range:
                return enemy
        return None

    def shoot(self, target, session):
        count = self.projectile_count
        if self.has_ultimate() and random.random() < 0.15:
            for enemy in session.enemies:
                if enemy.alive and distance(self.position, enemy.position) <= self.range:
                    dealt = enemy.take_damage(self.damage * 3, "splash")
                    self.gain_exp(dealt * 0.15)
            count += 4

        for index in range(count):
            angle = math.tau * index / count
            direction = (math.cos(angle), math.sin(angle))
            session.projectiles.append(
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


TOWER_CLASSES = {
    "basic": BasicTower,
    "sniper": SniperTower,
    "cannon": CannonTower,
    "freeze": FreezeTower,
    "anti_air": AntiAirTower,
    "splash": SplashTower,
}
