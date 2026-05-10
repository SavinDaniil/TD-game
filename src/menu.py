import pygame
import pygame_menu

from src.constants import BACKGROUND, HEIGHT, LEVEL_DATA, TEXT, UPGRADE_INFO, WIDTH
from src.game import Game
from src.player import Player
from src.ui import UI
from src.utils import DEFAULT_SAVE, load_save, save_json


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.save_data = load_save()
        self.player = Player(self.save_data)
        self.menu = None
        self.ui = UI()
        self.build_main_menu()

    def build_theme(self):
        theme = pygame_menu.themes.Theme(
            background_color=BACKGROUND,
            title_background_color=(18, 23, 38),
            title_font_color=TEXT,
            widget_font_color=TEXT,
            widget_selection_effect=pygame_menu.widgets.LeftArrowSelection(),
            selection_color=(88, 225, 220),
        )
        theme.title_font_size = 42
        theme.widget_font_size = 28
        theme.widget_margin = (0, 14)
        return theme

    def build_main_menu(self):
        theme = self.build_theme()
        self.menu = pygame_menu.Menu("Tower Defense", WIDTH, HEIGHT, theme=theme)
        self.menu.add.label(self.progress_text(), font_size=20)
        self.menu.add.button("Select Level", self.open_level_select)
        self.menu.add.button("Upgrades", self.open_upgrades)
        self.menu.add.button("Reset Progress", self.reset_progress)
        self.menu.add.button("Quit", pygame_menu.events.EXIT)

    def progress_text(self):
        coins = self.save_data.get("meta_coins", 0)
        best = self.save_data.get("best_wave", 0)
        return f"Meta coins: {coins}    Best wave: {best}"

    def refresh(self):
        self.save_data = load_save()
        self.player = Player(self.save_data)
        self.build_main_menu()

    def start_game(self, level_id):
        game = Game(self.screen, self.refresh, level_id)
        game.run()

    def open_level_select(self):
        theme = self.build_theme()
        level_menu = pygame_menu.Menu("Select Level", WIDTH, HEIGHT, theme=theme)
        for level_id, data in LEVEL_DATA.items():
            text = f"{data['name']} - {data['waves']} waves"
            level_menu.add.button(text, self.start_game, level_id)
        level_menu.add.button("Back", self.refresh)
        level_menu.mainloop(self.screen)

    def reset_progress(self):
        refunded = self.calculate_spent_upgrade_coins()
        data = DEFAULT_SAVE.copy()
        data["upgrades"] = DEFAULT_SAVE["upgrades"].copy()
        data["meta_coins"] = self.save_data.get("meta_coins", 0) + refunded
        save_json(data)
        self.refresh()

    def calculate_spent_upgrade_coins(self):
        spent = 0
        upgrades = self.save_data.get("upgrades", {})
        for key, level in upgrades.items():
            info = UPGRADE_INFO[key]
            for bought_level in range(level):
                spent += info["base_cost"] + info["step"] * bought_level
        return spent

    def open_upgrades(self):
        clock = pygame.time.Clock()
        in_upgrades = True
        while in_upgrades:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    in_upgrades = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    rects = self.ui.draw_upgrades(self.screen, self.player)
                    for key, rect in rects.items():
                        if rect.collidepoint(event.pos):
                            self.buy_upgrade(key)

            self.screen.fill(BACKGROUND)
            self.ui.draw_upgrades(self.screen, self.player)
            pygame.display.flip()
            clock.tick(60)
        self.refresh()

    def buy_upgrade(self, key):
        self.player.buy_permanent_upgrade(key)
        self.save_data["meta_coins"] = self.player.meta_coins
        self.save_data["upgrades"] = self.player.permanent_upgrades
        save_json(self.save_data)

    def run(self):
        self.menu.mainloop(self.screen)
