import pygame

from src.constants import (
    BACKGROUND,
    BUILD_PREVIEW_BORDER_ALPHA,
    BUILD_PREVIEW_CORE_ALPHA,
    BUILD_PREVIEW_CORE_RADIUS,
    BUILD_PREVIEW_FILL_ALPHA,
    FPS,
    SPEED_OPTIONS,
    TOWER_DATA,
)
from src.game_session import GameSession
from src.ui import UI
from src.utils import load_save, save_json


class Game:
    def __init__(self, screen, return_to_menu, music_manager, level_id=1, random_map=False):
        self.screen = screen
        self.return_to_menu = return_to_menu
        self.music_manager = music_manager
        self.clock = pygame.time.Clock()
        self.save_data = load_save()
        self.session = GameSession(self.save_data, level_id=level_id, random_map=random_map)
        self.ui = UI()
        self.selected_tower_type = None
        self.selected_tower = None
        self.paused = False
        self.running = True
        self.state = "playing"
        self.game_speed = self.save_data.get("game_speed", 1.0)

    @property
    def player(self):
        return self.session.player

    @property
    def wave_manager(self):
        return self.session.wave_manager

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

        cell = self.session.map.get_cell_by_mouse(pos)
        if not cell:
            return

        tower = self.session.get_tower_at_cell(cell)
        if tower:
            self.selected_tower = tower
            self.selected_tower_type = None
            return

        if self.selected_tower_type:
            self.try_build_tower(cell)

    def handle_ui_action(self, action):
        if action == "start_wave":
            self.session.start_wave()
        elif action == "resume":
            self.paused = False
        elif action == "return_to_menu":
            self.running = False
            self.return_to_menu()
        elif action.startswith("set_speed:"):
            speed = float(action.split(":")[1])
            if speed in SPEED_OPTIONS:
                self.game_speed = speed
        elif action == "upgrade" and self.selected_tower:
            self.selected_tower.upgrade(self.player)
        elif action.startswith("build:"):
            self.selected_tower_type = action.split(":")[1]
            self.selected_tower = None
        elif action.startswith("ability:") and self.selected_tower:
            index = int(action.split(":")[1])
            if self.selected_tower.can_choose_ability():
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
        tower = self.session.build_tower(self.selected_tower_type, cell)
        if tower:
            self.selected_tower = tower
            self.selected_tower_type = None

    def update(self, dt):
        outcome = self.session.update(dt)
        if outcome:
            self.finish_run(outcome)

    def finish_run(self, state):
        self.state = state
        self.session.sync_progress_to_save()
        save_json(self.save_data)

    def draw(self):
        self.screen.fill(BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()
        mouse_cell = self.session.map.get_cell_by_mouse(mouse_pos)
        self.session.map.draw(self.screen, mouse_cell, self.session.towers)
        self.draw_build_preview(mouse_cell)
        if self.selected_tower:
            self.selected_tower.draw_range(self.screen)
        for tower in self.session.towers:
            tower.draw(self.screen, tower is self.selected_tower)
        for enemy in self.session.enemies:
            enemy.draw(self.screen)
        for projectile in self.session.projectiles:
            projectile.draw(self.screen)
        self.ui.draw(self.screen, self, mouse_pos)
        pygame.display.flip()

    def draw_build_preview(self, mouse_cell):
        if not self.selected_tower_type or not mouse_cell:
            return
        if not self.session.map.can_place_tower(mouse_cell, self.session.towers):
            return

        data = TOWER_DATA[self.selected_tower_type]
        center = self.session.map.cell_center(mouse_cell)
        preview = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(preview, (*data["color"][:3], BUILD_PREVIEW_FILL_ALPHA), center, int(data["range"]))
        pygame.draw.circle(
            preview,
            (*data["color"][:3], BUILD_PREVIEW_BORDER_ALPHA),
            center,
            int(data["range"]),
            2,
        )
        pygame.draw.circle(
            preview,
            (*data["color"][:3], BUILD_PREVIEW_CORE_ALPHA),
            center,
            BUILD_PREVIEW_CORE_RADIUS,
            2,
        )
        self.screen.blit(preview, (0, 0))
