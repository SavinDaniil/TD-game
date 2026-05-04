import pygame

from src.utils import distance


class Projectile:
    def __init__(
        self,
        position,
        target,
        speed,
        damage,
        color,
        owner=None,
        radius=0,
        is_splash=False,
        direction=None,
        damage_type="normal",
    ):
        self.position = [float(position[0]), float(position[1])]
        self.target = target
        self.speed = speed
        self.damage = damage
        self.radius = radius
        self.color = color
        self.owner = owner
        self.is_splash = is_splash
        self.direction = direction
        self.damage_type = damage_type
        self.alive = True
        self.life_time = 1.5 if direction else 3.0

    def update(self, dt, enemies):
        if self.direction:
            self.position[0] += self.direction[0] * self.speed * dt
            self.position[1] += self.direction[1] * self.speed * dt
            self.life_time -= dt
            self.hit_enemy_on_path(enemies)
            if self.life_time <= 0:
                self.alive = False
            return

        if not self.target or not self.target.alive:
            self.alive = False
            return

        dist = distance(self.position, self.target.position)
        if dist <= self.speed * dt:
            self.position[0], self.position[1] = self.target.position
            self.apply_hit(enemies)
            self.alive = False
            return

        dx = (self.target.position[0] - self.position[0]) / dist
        dy = (self.target.position[1] - self.position[1]) / dist
        self.position[0] += dx * self.speed * dt
        self.position[1] += dy * self.speed * dt

    def hit_enemy_on_path(self, enemies):
        for enemy in enemies:
            if enemy.alive and distance(self.position, enemy.position) < 14:
                self.deal_damage(enemy)
                self.alive = False
                return

    def apply_hit(self, enemies):
        if self.is_splash:
            for enemy in enemies:
                if enemy.alive and distance(self.position, enemy.position) <= self.radius:
                    self.deal_damage(enemy)
        else:
            self.deal_damage(self.target)

    def deal_damage(self, enemy):
        if enemy and enemy.alive:
            dealt = enemy.take_damage(self.damage, self.damage_type)
            if self.owner:
                self.owner.gain_exp(dealt * 0.12)
                if not enemy.alive:
                    self.owner.gain_exp(12)

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            5,
        )
        if self.is_splash:
            pygame.draw.circle(
                surface,
                (*self.color[:3],),
                (int(self.position[0]), int(self.position[1])),
                9,
                1,
            )
