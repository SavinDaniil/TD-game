import random

from src.constants import (BASE_SPAWN_DELAY, BASE_ENEMY_COUNT, FAST_WAVE_THRESHOLD, STRONG_WAVE_THRESHOLD,
                           ARMORED_WAVE_THRESHOLD, AIR_WAVE_THRESHOLD)
from src.enemy import Enemy


class WaveManager:
    def __init__(self, game_map, max_wave, enemy_multiplier=1.0):
        self.game_map = game_map
        self.max_wave = max_wave
        self.enemy_multiplier = enemy_multiplier
        self.current_wave = 0
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.wave_active = False
        self.spawn_delay = BASE_SPAWN_DELAY

    def start_wave(self):
        if self.wave_active or self.current_wave >= self.max_wave:
            return False
        self.current_wave += 1
        self.enemies_to_spawn = self.create_wave(self.current_wave)
        self.spawn_timer = 0
        self.wave_active = True
        return True

    def create_wave(self, wave):
        if wave == self.max_wave:
            enemies = ["boss"]
            amount = int(7 * self.enemy_multiplier)
            enemies += ["strong"] * amount
            enemies += ["armored"] * amount
            enemies += ["air"] * amount
            return enemies

        enemies = ["normal"] * int((BASE_ENEMY_COUNT + wave) * self.enemy_multiplier)
        if wave >= FAST_WAVE_THRESHOLD:
            enemies += ["fast"] * int((wave // 2 + 2) * self.enemy_multiplier)
        if wave >= STRONG_WAVE_THRESHOLD:
            enemies += ["strong"] * int(max(1, wave // 3) * self.enemy_multiplier)
        if wave >= ARMORED_WAVE_THRESHOLD:
            enemies += ["armored"] * int((wave // 4 + 1) * self.enemy_multiplier)
        if wave >= AIR_WAVE_THRESHOLD:
            enemies += ["air"] * int(max(1, wave // 3) * self.enemy_multiplier)
        random.shuffle(enemies)
        return enemies

    def update(self, dt, enemies):
        if not self.wave_active:
            return

        self.spawn_timer -= dt
        if self.enemies_to_spawn and self.spawn_timer <= 0:
            enemy_type = self.enemies_to_spawn.pop(0)
            enemies.append(Enemy(self.game_map.path_points, enemy_type, self.current_wave))
            self.spawn_timer = self.spawn_delay

        if not self.enemies_to_spawn and not any(enemy.alive for enemy in enemies):
            self.wave_active = False

    def is_finished(self, enemies):
        return (
            self.current_wave >= self.max_wave
            and not self.wave_active
            and not self.enemies_to_spawn
            and not any(enemy.alive for enemy in enemies)
        )
