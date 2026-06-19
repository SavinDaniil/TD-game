import random
import pygame
from src.constants import BACKGROUND, FPS, LEVEL_DATA, TOWER_DATA
from src.map import GameMap
from src.player import Player
from src.tower import TOWER_CLASSES
from src.ui import UI
from src.utils import load_save, save_json
from src.wave_manager import WaveManager


class Game:
    SPEED_OPTIONS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

    def __init__(self, screen, return_to_menu, music_manager, level_id=1, random_map=False):
        self.screen = screen
        self.return_to_menu = return_to_menu
        self.music_manager = music_manager
        self.random_map = random_map
        self.clock = pygame.time.Clock()
        self.save_data = load_save()
        self.player = Player(self.save_data)

        if random_map:
            self.max_waves = random.randint(15, 30)
            self.enemy_multiplier = 1.0
            self.map = GameMap(random_map=True)
        else:
            self.level_data = LEVEL_DATA[level_id]
            self.max_waves = self.level_data["waves"]
            self.enemy_multiplier = self.level_data["enemy_multiplier"]
            self.map = GameMap(level_id=level_id)

        self.wave_manager = WaveManager(self.map, self.max_waves, self.enemy_multiplier)
        self.ui = UI()
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.selected_tower_type = None
        self.selected_tower = None
        self.paused = False
        self.running = True
        self.state = "playing"
        self.game_speed = self.save_data.get("game_speed", 1.0)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            if self.state == "playing" and not self.paused:
                self.update(dt * self.game_speed)
            self.draw()
        save_json(self.save_data)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_json(self.save_data)
                pygame.quit()
                raise SystemExit
            self.music_manager.handle_event(event)
            if event.type == pygame.KEYDOWN:
                self.handle_key(event.key)
            if self.paused and self.state == "playing":
                result = self.ui.handle_pause_event(event)
                if result:
                    self.handle_pause_result(result)
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)

    def handle_key(self, key):
        if key == pygame.K_ESCAPE and self.state == "playing":
            self.paused = not self.paused
            self.selected_tower = None
            self.selected_tower_type = None
        elif key == pygame.K_p:
            self.paused = not self.paused

    def handle_click(self, pos):
        if self.state in ("game_over", "victory"):
            self.running = False
            self.return_to_menu()
            return
        action = self.ui.handle_click(pos)
        if action:
            self.handle_ui_action(action)
            return
        cell = self.map.get_cell_by_mouse(pos)
        if not cell:
            return
        tower = self.get_tower_at_cell(cell)
        if tower:
            self.selected_tower = tower
            self.selected_tower_type = None
            return
        if self.selected_tower_type:
            self.try_build_tower(cell)

    def handle_ui_action(self, action):
        if action == "start_wave":
            self.wave_manager.start_wave()
        elif action == "resume":
            self.paused = False
        elif action == "return_to_menu":
            self.running = False
            self.return_to_menu()
        elif action.startswith("set_speed:"):
            speed = float(action.split(":")[1])
            if speed in self.SPEED_OPTIONS:
                self.game_speed = speed
        elif action == "upgrade" and self.selected_tower:
            self.selected_tower.upgrade(self.player)
        elif action.startswith("build:"):
            self.selected_tower_type = action.split(":")[1]
            self.selected_tower = None
        elif action.startswith("ability:") and self.selected_tower:
            index = int(action.split(":")[1])
            if self.selected_tower.needs_ability_choice() == "normal":
                self.selected_tower.select_ability(index)

    def handle_pause_result(self, result):
        kind, value, committed = result
        if kind == "set_speed":
            self.set_game_speed(value, committed)
        elif kind == "set_music_volume":
            self.set_music_volume(value, committed)
        elif kind == "action":
            self.handle_ui_action(value)

    def set_game_speed(self, speed, save=False):
        self.game_speed = speed
        self.save_data["game_speed"] = self.game_speed
        if save:
            save_json(self.save_data)

    def set_music_volume(self, volume, save=False):
        self.music_manager.set_volume(volume)
        self.save_data["music_volume"] = self.music_manager.volume
        if save:
            save_json(self.save_data)

    def try_build_tower(self, cell):
        if not self.map.can_place_tower(cell, self.towers):
            return
        data = TOWER_DATA[self.selected_tower_type]
        if not self.player.spend(data["cost"]):
            return
        tower_class = TOWER_CLASSES[self.selected_tower_type]
        tower = tower_class(cell, self.map.cell_center(cell), self.player)
        self.towers.append(tower)
        self.selected_tower = tower
        self.selected_tower_type = None

    def get_tower_at_cell(self, cell):
        for tower in self.towers:
            if tower.cell == cell:
                return tower
        return None

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
            tower.update(dt, self.enemies, self.projectiles, self.map, self.towers)
        for projectile in list(self.projectiles):
            projectile.update(dt, self.enemies)
            if not projectile.alive:
                self.projectiles.remove(projectile)
        if self.player.hp <= 0:
            self.finish_run("game_over")
        elif self.wave_manager.is_finished(self.enemies):
            self.finish_run("victory")

    def finish_run(self, state):
        self.state = state
        self.save_data["meta_coins"] = self.player.meta_coins
        save_json(self.save_data)

    def draw(self):
        self.screen.fill(BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()
        mouse_cell = self.map.get_cell_by_mouse(mouse_pos)
        self.map.draw(self.screen, mouse_cell, self.towers)
        self.draw_build_preview(mouse_cell)
        if self.selected_tower:
            self.selected_tower.draw_range(self.screen)
        for tower in self.towers:
            tower.draw(self.screen, tower is self.selected_tower)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        self.ui.draw(self.screen, self, mouse_pos)
        pygame.display.flip()

    def draw_build_preview(self, mouse_cell):
        if not self.selected_tower_type or not mouse_cell:
            return
        if not self.map.can_place_tower(mouse_cell, self.towers):
            return
        data = TOWER_DATA[self.selected_tower_type]
        center = self.map.cell_center(mouse_cell)
        preview = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(preview, (*data["color"][:3], 28), center, int(data["range"]))
        pygame.draw.circle(preview, (*data["color"][:3], 105), center, int(data["range"]), 2)
        pygame.draw.circle(preview, (*data["color"][:3], 85), center, 24, 2)
        self.screen.blit(preview, (0, 0))
