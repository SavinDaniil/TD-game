import pygame

from src.audio import MusicManager
from src.constants import BACKGROUND, LEVEL_DATA, MUTED_TEXT, PANEL, TEXT, UPGRADE_INFO, WIDTH, YELLOW
from src.game import Game
from src.player import Player
from src.ui import Button, Slider, UI
from src.utils import DEFAULT_SAVE, draw_text, load_save, save_json


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.save_data = load_save()
        self.player = Player(self.save_data)
        self.music_manager = MusicManager(self.save_data.get("music_volume", 0.5))
        self.ui = UI()
        self.state = "main"
        self.running = True
        self.main_buttons = []
        self.level_buttons = []
        self.volume_slider = None
        self.build_main_controls()
        self.build_level_controls()

    def build_main_controls(self):
        center_x = WIDTH // 2
        button_width = 300
        button_height = 48
        button_x = center_x - button_width // 2
        start_y = 270
        gap = 18

        self.volume_slider = Slider((center_x - 180, 205, 360, 24), [step / 10 for step in range(11)],
                                    self.music_manager.volume)
        self.main_buttons = [
            Button((button_x, start_y + 0 * (button_height + gap), button_width, button_height),
                   "Select Level", "select_level"),
            Button((button_x, start_y + 1 * (button_height + gap), button_width, button_height),
                   "Upgrades", "upgrades"),
            Button((button_x, start_y + 2 * (button_height + gap), button_width, button_height),
                   "Reset Progress", "reset_progress"),
            Button((button_x, start_y + 3 * (button_height + gap), button_width, button_height),
                   "Quit", "quit", color=BACKGROUND),
        ]

    def build_level_controls(self):
        button_width = 420
        button_height = 44
        button_x = WIDTH // 2 - button_width // 2
        start_y = 170
        gap = 14

        self.level_buttons = []
        for index, (level_id, data) in enumerate(LEVEL_DATA.items()):
            text = f"{data['name']} - {data['waves']} waves"
            rect = (button_x, start_y + index * (button_height + gap), button_width, button_height)
            self.level_buttons.append(Button(rect, text, f"level:{level_id}"))

        random_y = start_y + len(LEVEL_DATA) * (button_height + gap)
        self.level_buttons.append(
            Button((button_x, random_y, button_width, button_height), "Random Map - ?? waves", "level:random")
        )
        self.level_buttons.append(
            Button((WIDTH // 2 - 100, random_y + 78, 200, 50), "Back", "back", color=BACKGROUND)
        )

    def progress_text(self):
        coins = self.save_data.get("meta_coins", 0)
        return f"Meta coins: {coins}"

    def refresh(self):
        self.save_data = load_save()
        self.player = Player(self.save_data)
        self.music_manager.set_volume(self.save_data.get("music_volume", self.music_manager.volume))
        self.volume_slider.sync(self.music_manager.volume)

    def start_game(self, level_id, random_map=False):
        game = Game(self.screen, self.refresh, self.music_manager, level_id=level_id, random_map=random_map)
        game.run()
        self.music_manager.play()
        self.refresh()

    def reset_progress(self):
        refunded = self.calculate_spent_upgrade_coins()
        data = DEFAULT_SAVE.copy()
        data["upgrades"] = DEFAULT_SAVE["upgrades"].copy()
        data["meta_coins"] = self.save_data.get("meta_coins", 0) + refunded
        data["music_volume"] = self.save_data.get("music_volume", self.music_manager.volume)
        data["game_speed"] = self.save_data.get("game_speed", 1.0)
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
        in_upgrades = True
        while in_upgrades:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                self.music_manager.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    in_upgrades = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    rects = self.ui.draw_upgrades(self.screen, self.player)
                    for key, rect in rects.items():
                        if rect.collidepoint(event.pos):
                            if key == "back":
                                in_upgrades = False
                            else:
                                self.buy_upgrade(key)

            self.screen.fill(BACKGROUND)
            self.ui.draw_upgrades(self.screen, self.player)
            pygame.display.flip()
            self.clock.tick(60)
        self.refresh()

    def buy_upgrade(self, key):
        self.player.buy_permanent_upgrade(key)
        self.save_data["meta_coins"] = self.player.meta_coins
        self.save_data["upgrades"] = self.player.export_upgrades()
        save_json(self.save_data)

    def handle_main_event(self, event):
        slider_value = self.volume_slider.handle_event(event)
        if slider_value is not None:
            value, committed = slider_value
            self.music_manager.set_volume(value)
            self.save_data["music_volume"] = self.music_manager.volume
            if committed:
                save_json(self.save_data)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.main_buttons:
                if button.rect.collidepoint(event.pos):
                    if button.action == "select_level":
                        self.state = "levels"
                    elif button.action == "upgrades":
                        self.open_upgrades()
                    elif button.action == "reset_progress":
                        self.reset_progress()
                    elif button.action == "quit":
                        self.running = False
                    return

    def handle_level_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "main"
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.level_buttons:
                if button.rect.collidepoint(event.pos):
                    if button.action == "back":
                        self.state = "main"
                    elif button.action == "level:random":
                        self.start_game(level_id=1, random_map=True)
                    elif button.action.startswith("level:"):
                        level_id = int(button.action.split(":")[1])
                        self.start_game(level_id=level_id)
                    return

    def draw_main_menu(self):
        self.screen.fill(BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()
        card_rect = pygame.Rect(WIDTH // 2 - 240, 90, 480, 460)
        pygame.draw.rect(self.screen, PANEL, card_rect, border_radius=16)
        pygame.draw.rect(self.screen, (78, 89, 118), card_rect, 2, border_radius=16)

        title_font = pygame.font.SysFont("arial", 42, bold=True)
        draw_text(self.screen, title_font, "Tower Defense", TEXT, (WIDTH // 2, 132), center=True)
        draw_text(self.screen, self.ui.small_font, self.progress_text(), MUTED_TEXT, (WIDTH // 2, 165), center=True)
        draw_text(self.screen, self.ui.font, "Music volume", TEXT, (WIDTH // 2 - 180, 182))
        draw_text(self.screen, self.ui.font, f"{int(self.music_manager.volume * 100)}%", YELLOW, (WIDTH // 2 + 130, 182))
        self.volume_slider.draw(self.screen, mouse_pos, active_color=(88, 225, 220))

        for button in self.main_buttons:
            button.draw(self.screen, self.ui.font, mouse_pos)

    def draw_level_select(self):
        self.screen.fill(BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()
        card_rect = pygame.Rect(WIDTH // 2 - 280, 80, 560, 520)
        pygame.draw.rect(self.screen, PANEL, card_rect, border_radius=16)
        pygame.draw.rect(self.screen, (78, 89, 118), card_rect, 2, border_radius=16)

        title_font = pygame.font.SysFont("arial", 36, bold=True)
        draw_text(self.screen, title_font, "Select Level", TEXT, (WIDTH // 2, 122), center=True)

        for button in self.level_buttons:
            button.draw(self.screen, self.ui.font, mouse_pos)

    def run(self):
        while self.running:
            self.music_manager.play()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.music_manager.handle_event(event)
                if self.state == "main":
                    self.handle_main_event(event)
                elif self.state == "levels":
                    self.handle_level_event(event)

            if self.state == "main":
                self.draw_main_menu()
            else:
                self.draw_level_select()

            pygame.display.flip()
            self.clock.tick(60)
