import random

from src.constants import LEVEL_DATA, TOWER_DATA
from src.map import GameMap
from src.player import Player
from src.tower import TOWER_CLASSES
from src.wave_manager import WaveManager


class GameSession:
    def __init__(self, save_data, level_id=1, random_map=False):
        self.save_data = save_data
        self.player = Player(save_data)
        self.random_map = random_map

        if random_map:
            self.max_waves = random.randint(15, 30)
            self.enemy_multiplier = 1.0
            self.map = GameMap(random_map=True)
        else:
            level_data = LEVEL_DATA[level_id]
            self.max_waves = level_data["waves"]
            self.enemy_multiplier = level_data["enemy_multiplier"]
            self.map = GameMap(level_id=level_id)

        self.wave_manager = WaveManager(self.map, self.max_waves, self.enemy_multiplier)
        self.enemies = []
        self.towers = []
        self.projectiles = []

    def start_wave(self):
        return self.wave_manager.start_wave()

    def get_tower_at_cell(self, cell):
        for tower in self.towers:
            if tower.is_on_cell(cell):
                return tower
        return None

    def build_tower(self, tower_type, cell):
        if not self.map.can_place_tower(cell, self.towers):
            return None

        data = TOWER_DATA.get(tower_type)
        if not data or not self.player.spend(data["cost"]):
            return None

        tower = TOWER_CLASSES[tower_type](cell, self.map.cell_center(cell), self.player)
        self.towers.append(tower)
        return tower

    def update(self, dt):
        self.wave_manager.update(dt, self.enemies)

        for enemy in list(self.enemies):
            enemy.update(dt)
            if enemy.reached_base:
                self.player.take_damage(enemy.hp)
            if not enemy.alive:
                if not enemy.reached_base:
                    self.player.add_kill_reward(enemy.reward)
                self.enemies.remove(enemy)

        for tower in self.towers:
            tower.update(dt, self)

        for projectile in list(self.projectiles):
            projectile.update(dt, self.enemies)
            if not projectile.alive:
                self.projectiles.remove(projectile)

        if self.player.hp <= 0:
            return "game_over"
        if self.wave_manager.is_finished(self.enemies):
            return "victory"
        return None

    def sync_progress_to_save(self):
        self.save_data["meta_coins"] = self.player.meta_coins
