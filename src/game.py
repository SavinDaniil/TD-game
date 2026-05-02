import pygame

from src.constants import BACKGROUND, FPS, TEXT
from src.map import GameMap
from src.player import Player
from src.utils import draw_text
from src.wave_manager import WaveManager


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.map = GameMap()
        self.player = Player()
        self.wave_manager = WaveManager(self.map)
        self.enemies = []
        self.running = True
        self.state = "playing"

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            if self.state == "playing":
                self.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.wave_manager.start_wave()

    def update(self, dt):
        self.wave_manager.update(dt, self.enemies)
        for enemy in list(self.enemies):
            enemy.update(dt)
            if enemy.reached_base:
                self.player.take_damage(enemy.hp)
            if not enemy.alive:
                if not enemy.reached_base:
                    self.player.add_coins(enemy.reward)
                self.enemies.remove(enemy)

        if self.player.hp <= 0:
            self.state = "game_over"
        elif self.wave_manager.is_finished(self.enemies):
            self.state = "victory"

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.map.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        draw_text(self.screen, self.font, f"HP: {self.player.hp}", TEXT, (980, 30))
        draw_text(self.screen, self.font, f"Coins: {self.player.coins}", TEXT, (980, 62))
        draw_text(
            self.screen,
            self.font,
            f"Wave: {self.wave_manager.current_wave}/{self.wave_manager.max_wave}",
            TEXT,
            (980, 94),
        )
        draw_text(self.screen, self.font, "SPACE - start wave", TEXT, (980, 140))
        if self.state != "playing":
            draw_text(self.screen, self.font, self.state.upper(), TEXT, (640, 360), True)
        pygame.display.flip()
