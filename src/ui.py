import pygame

from src.constants import (
    HEIGHT,
    MUTED_TEXT,
    PANEL,
    PANEL_LIGHT,
    PANEL_WIDTH,
    PANEL_X,
    TEXT,
    TOWER_DATA,
    TOWER_TYPES,
    UPGRADE_INFO,
    WIDTH,
    YELLOW,
)
from src.utils import draw_text


class Button:
    def __init__(self, rect, text, action, color=PANEL_LIGHT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.color = color

    def draw(self, surface, font, mouse_pos, active=False):
        color = self.color
        if self.rect.collidepoint(mouse_pos):
            color = tuple(min(255, value + 24) for value in color)
        if active:
            color = (62, 83, 122)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (78, 89, 118), self.rect, 1, border_radius=8)
        draw_text(surface, font, self.text, TEXT, self.rect.center, center=True)


class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.title_font = pygame.font.SysFont("arial", 26, bold=True)
        self.buttons = []
        self.tower_buttons = []
        self.ability_buttons = []
        self.build_buttons()

    def build_buttons(self):
        self.buttons = [
            Button(
                (PANEL_X + 18, 112, PANEL_WIDTH - 36, 42),
                "Start Wave",
                "start_wave",
            )
        ]
        y = 194
        for tower_type in TOWER_TYPES:
            data = TOWER_DATA[tower_type]
            text = f"{data['name']}  ${data['cost']}"
            rect = (PANEL_X + 18, y, PANEL_WIDTH - 36, 31)
            self.tower_buttons.append(Button(rect, text, f"build:{tower_type}"))
            y += 36
        self.buttons += self.tower_buttons
        self.buttons.append(
            Button((PANEL_X + 18, 512, PANEL_WIDTH - 36, 36), "Upgrade", "upgrade")
        )
        for index in range(3):
            rect = (PANEL_X + 18, 556 + index * 34, PANEL_WIDTH - 36, 30)
            self.ability_buttons.append(
                Button(rect, f"Ability {index + 1}", f"ability:{index}")
            )
        self.buttons += self.ability_buttons

    def draw(self, surface, game, mouse_pos):
        panel_rect = pygame.Rect(PANEL_X, 0, WIDTH - PANEL_X, HEIGHT)
        pygame.draw.rect(surface, PANEL, panel_rect)
        pygame.draw.line(surface, (55, 64, 90), (PANEL_X, 0), (PANEL_X, HEIGHT), 2)
        self.update_ability_button_texts(game.selected_tower)

        draw_text(
            surface,
            self.font,
            f"HP: {game.player.hp}/{game.player.max_hp}",
            TEXT,
            (PANEL_X + 18, 20),
        )
        draw_text(
            surface,
            self.font,
            f"Coins: {game.player.coins}",
            YELLOW,
            (PANEL_X + 18, 52),
        )
        draw_text(
            surface,
            self.font,
            f"Wave: {game.wave_manager.current_wave}/{game.wave_manager.max_wave}",
            TEXT,
            (PANEL_X + 18, 84),
        )

        for button in self.buttons:
            active = False
            if button.action.startswith("build:"):
                selected_type = button.action.split(":")[1]
                active = game.selected_tower_type == selected_type
            button.draw(surface, self.small_font, mouse_pos, active)

        draw_text(surface, self.font, "Build", TEXT, (PANEL_X + 18, 166))
        self.draw_selected_tower(surface, game)
        self.draw_messages(surface, game)

    def update_ability_button_texts(self, tower):
        if not tower or tower.needs_ability_choice() != "normal":
            self.set_empty_ability_buttons()
            return

        for index, button in enumerate(self.ability_buttons):
            button.text = tower.ability_options[index]

    def draw_selected_tower(self, surface, game):
        tower = game.selected_tower
        if not tower:
            draw_text(
                surface,
                self.small_font,
                "Selected: none",
                MUTED_TEXT,
                (PANEL_X + 18, 418),
            )
            return

        y = 414
        draw_text(surface, self.font, f"Selected: {tower.name}", TEXT, (PANEL_X + 18, y))
        y += 28
        draw_text(
            surface,
            self.small_font,
            f"Lvl {tower.level}  Upg {tower.upgrade_level}/10",
            MUTED_TEXT,
            (PANEL_X + 18, y),
        )
        self.draw_selected_abilities(surface, tower, y + 24)
        info = (
            f"Dmg {tower.damage:.1f}  Rng {tower.range:.0f}  "
            f"Spd {tower.attack_speed:.2f}"
        )
        draw_text(surface, self.small_font, info, MUTED_TEXT, (PANEL_X + 18, 682))
        if tower.needs_ability_choice():
            draw_text(
                surface,
                self.small_font,
                "Choose an ability",
                YELLOW,
                (PANEL_X + 18, 658),
            )

    def set_empty_ability_buttons(self):
        for button in self.ability_buttons:
            button.text = "-"

    def draw_selected_abilities(self, surface, tower, y):
        if not tower.selected_abilities:
            draw_text(
                surface,
                self.small_font,
                "Abilities: none",
                MUTED_TEXT,
                (PANEL_X + 18, y),
            )
            return

        draw_text(surface, self.small_font, "Abilities:", MUTED_TEXT, (PANEL_X + 18, y))
        for index, ability in enumerate(tower.selected_abilities[:3]):
            draw_text(
                surface,
                self.small_font,
                f"{index + 1}. {ability}",
                TEXT,
                (PANEL_X + 32, y + 19 + index * 18),
            )

    def draw_messages(self, surface, game):
        if game.state == "game_over":
            self.draw_center_message(surface, "GAME OVER", "Click to return to menu")
        elif game.state == "victory":
            self.draw_center_message(surface, "VICTORY", "Click to return to menu")
        elif game.paused:
            self.draw_center_message(surface, "PAUSED", "Press P to continue")

    def draw_center_message(self, surface, title, subtitle):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        draw_text(surface, self.title_font, title, TEXT, (WIDTH // 2, HEIGHT // 2 - 30), True)
        draw_text(surface, self.font, subtitle, MUTED_TEXT, (WIDTH // 2, HEIGHT // 2 + 6), True)

    def handle_click(self, pos):
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                return button.action
        return None

    def draw_upgrades(self, surface, player):
        surface.fill((13, 16, 29))
        draw_text(
            surface,
            self.title_font,
            "Permanent Upgrades",
            TEXT,
            (WIDTH // 2, 45),
            center=True,
        )
        draw_text(
            surface,
            self.font,
            f"Meta coins: {player.meta_coins}",
            YELLOW,
            (WIDTH // 2, 84),
            center=True,
        )
        mouse_pos = pygame.mouse.get_pos()
        upgrade_width = 520
        upgrade_x = (WIDTH - upgrade_width) // 2

        y = 140
        rects = {}
        for key, info in UPGRADE_INFO.items():
            level = player.permanent_upgrades[key]
            cost = info["base_cost"] + info["step"] * level
            text = f"{info['name']}  Lv {level}/{info['max']}  Cost {cost}"
            rect = pygame.Rect(upgrade_x, y, upgrade_width, 42)
            pygame.draw.rect(surface, PANEL_LIGHT, rect, border_radius=8)
            draw_text(surface, self.font, text, TEXT, (rect.x + 14, rect.y + 10))
            rects[key] = rect
            y += 56

        back_rect = pygame.Rect(WIDTH // 2 - 80, y + 8, 160, 40)
        back_color = PANEL_LIGHT
        if back_rect.collidepoint(mouse_pos):
            back_color = tuple(min(255, value + 24) for value in back_color)
        pygame.draw.rect(surface, back_color, back_rect, border_radius=8)
        pygame.draw.rect(surface, (78, 89, 118), back_rect, 1, border_radius=8)
        draw_text(surface, self.font, "Back", TEXT, back_rect.center, center=True)
        rects["back"] = back_rect
        return rects
