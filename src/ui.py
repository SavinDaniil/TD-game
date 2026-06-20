import pygame

from src.constants import (ABILITY_BUTTON_HEIGHT, ABILITY_BUTTON_SPACING, ABILITY_BUTTON_Y_START, BACKGROUND,
                           BUTTON_HEIGHT, BUTTON_Y_START, HEIGHT, MUTED_TEXT, PANEL, PANEL_LIGHT, PANEL_WIDTH, PANEL_X,
                           PAUSE_MENU_HEIGHT, PAUSE_MENU_WIDTH, TEXT, TOWER_BUTTON_HEIGHT, TOWER_BUTTON_SPACING,
                           TOWER_BUTTON_Y_START, TOWER_DATA, TOWER_TYPES, TOWER_MAX_UPGRADE_LEVEL,
                           TOWER_ULTIMATE_LEVEL, UPGRADE_BUTTON_Y, UPGRADE_INFO, WIDTH, YELLOW, SPEED_OPTIONS)
from src.utils import clamp, draw_text


class Button:
    def __init__(self, rect, text, action, color=PANEL_LIGHT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.color = color
        self.disabled = False
        self.selected = False

    def draw(self, surface, font, mouse_pos, active=False):
        color = self.color
        text_color = TEXT
        border_color = (78, 89, 118)
        if self.disabled:
            color = (28, 34, 52)
            text_color = MUTED_TEXT
        elif self.rect.collidepoint(mouse_pos):
            color = tuple(min(255, value + 24) for value in color)
        if active or self.selected:
            color = (62, 83, 122)
            text_color = TEXT
            border_color = (110, 126, 166)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=8)
        draw_text(surface, font, self.text, text_color, self.rect.center, center=True)


class Slider:
    def __init__(self, rect, values, value):
        self.rect = pygame.Rect(rect)
        self.values = [float(item) for item in values]
        self.value = self._snap(value)
        self.dragging = False
        self.handle_radius = 12

    def _snap(self, value):
        return min(self.values, key=lambda item: abs(item - value))

    def _ratio_from_value(self, value):
        if len(self.values) == 1:
            return 0
        index = self.values.index(self._snap(value))
        return index / (len(self.values) - 1)

    def _value_from_x(self, x):
        ratio = clamp((x - self.rect.left) / max(1, self.rect.width), 0, 1)
        if len(self.values) == 1:
            return self.values[0]
        index = round(ratio * (len(self.values) - 1))
        return self.values[index]

    def sync(self, value):
        if not self.dragging:
            self.value = self._snap(value)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(0, 20).collidepoint(event.pos):
                self.dragging = True
                self.value = self._value_from_x(event.pos[0])
                return self.value, False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self._value_from_x(event.pos[0])
            return self.value, False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self.dragging = False
            self.value = self._value_from_x(event.pos[0])
            return self.value, True
        return None

    def draw(self, surface, mouse_pos, active_color=YELLOW):
        line_y = self.rect.centery
        start = (self.rect.left, line_y)
        end = (self.rect.right, line_y)
        pygame.draw.line(surface, (68, 76, 103), start, end, 6)

        ratio = self._ratio_from_value(self.value)
        fill_x = self.rect.left + int(self.rect.width * ratio)
        pygame.draw.line(surface, active_color, start, (fill_x, line_y), 6)

        for item in self.values:
            tick_ratio = self._ratio_from_value(item)
            tick_x = self.rect.left + int(self.rect.width * tick_ratio)
            tick_color = active_color if item <= self.value else (115, 124, 150)
            pygame.draw.circle(surface, tick_color, (tick_x, line_y), 5)

        hovering = self.rect.inflate(0, 20).collidepoint(mouse_pos)
        handle_color = (245, 248, 255)
        if hovering or self.dragging:
            handle_color = (255, 255, 255)
        pygame.draw.circle(surface, handle_color, (fill_x, line_y), self.handle_radius)
        pygame.draw.circle(surface, PANEL, (fill_x, line_y), self.handle_radius - 5)


class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.title_font = pygame.font.SysFont("arial", 26, bold=True)
        self.buttons = []
        self.tower_buttons = []
        self.ability_buttons = []
        self.pause_buttons = []
        self.pause_speed_slider = None
        self.pause_volume_slider = None
        self.build_buttons()
        self.build_pause_controls()

    def build_buttons(self):
        self.buttons = [
            Button(
                (PANEL_X + 18, BUTTON_Y_START, PANEL_WIDTH - 36, BUTTON_HEIGHT),
                "Start Wave",
                "start_wave",
            )
        ]
        y = TOWER_BUTTON_Y_START
        for tower_type in TOWER_TYPES:
            data = TOWER_DATA[tower_type]
            text = f"{data['name']} ${data['cost']}"
            rect = (PANEL_X + 18, y, PANEL_WIDTH - 36, TOWER_BUTTON_HEIGHT)
            self.tower_buttons.append(Button(rect, text, f"build:{tower_type}"))
            y += TOWER_BUTTON_SPACING
        self.buttons += self.tower_buttons
        self.buttons.append(
            Button((PANEL_X + 18, UPGRADE_BUTTON_Y, PANEL_WIDTH - 36, 36), "Upgrade", "upgrade")
        )
        for index in range(3):
            rect = (
                PANEL_X + 18,
                ABILITY_BUTTON_Y_START + index * ABILITY_BUTTON_SPACING,
                PANEL_WIDTH - 36,
                ABILITY_BUTTON_HEIGHT,
            )
            self.ability_buttons.append(Button(rect, f"Ability {index + 1}", f"ability:{index}"))
        self.buttons += self.ability_buttons

    def build_pause_controls(self):
        menu_x = (WIDTH - PAUSE_MENU_WIDTH) // 2
        menu_y = (HEIGHT - PAUSE_MENU_HEIGHT) // 2
        inner_x = menu_x + 40
        inner_width = PAUSE_MENU_WIDTH - 80

        volume_values = [step / 10 for step in range(11)]
        self.pause_speed_slider = Slider((inner_x, menu_y + 150, inner_width, 24), SPEED_OPTIONS, 1.0)
        self.pause_volume_slider = Slider((inner_x, menu_y + 240, inner_width, 24), volume_values, 0.5)
        self.pause_buttons = [
            Button((inner_x, menu_y + 54, inner_width, 40), "Continue", "resume"),
            Button((inner_x, menu_y + PAUSE_MENU_HEIGHT - 54, inner_width, 36), "Main Menu", "return_to_menu",
                   color=BACKGROUND),
        ]

    def draw(self, surface, game, mouse_pos):
        panel_rect = pygame.Rect(PANEL_X, 0, WIDTH - PANEL_X, HEIGHT)
        pygame.draw.rect(surface, PANEL, panel_rect)
        pygame.draw.line(surface, (55, 64, 90), (PANEL_X, 0), (PANEL_X, HEIGHT), 2)
        self.update_ability_button_texts(game.selected_tower)

        draw_text(surface, self.font, f"HP: {game.player.hp}/{game.player.max_hp}", TEXT, (PANEL_X + 18, 20))
        draw_text(surface, self.font, f"Coins: {game.player.coins}", YELLOW, (PANEL_X + 18, 52))
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
        if game.paused and game.state == "playing":
            self.draw_pause_menu(surface, game, mouse_pos)

    def update_ability_button_texts(self, tower):
        if not tower:
            self.set_empty_ability_buttons()
            return
        choice_available = tower.needs_ability_choice() == "normal"
        for index, button in enumerate(self.ability_buttons):
            ability = tower.ability_options[index]
            button.text = ability
            button.selected = tower.has_ability(ability)
            button.disabled = button.selected or not choice_available

    def draw_selected_tower(self, surface, game):
        tower = game.selected_tower
        if not tower:
            draw_text(surface, self.small_font, "Selected: none", MUTED_TEXT, (PANEL_X + 18, 418))
            return

        y = 414
        draw_text(surface, self.font, f"Selected: {tower.name}", TEXT, (PANEL_X + 18, y))
        y += 28
        draw_text(surface, self.small_font, f"Lvl {tower.level}  Upg {tower.upgrade_level}/{TOWER_MAX_UPGRADE_LEVEL}",
                  MUTED_TEXT,
                  (PANEL_X + 18, y))
        self.draw_ultimate_status(surface, tower, y + 24)
        info = f"Dmg {tower.damage:.1f}  Rng {tower.range:.0f}  Spd {tower.attack_speed:.2f}"
        draw_text(surface, self.small_font, info, MUTED_TEXT, (PANEL_X + 18, 682))
        if tower.needs_ability_choice():
            draw_text(surface, self.small_font, "Choose an ability", YELLOW, (PANEL_X + 18, 658))

    def set_empty_ability_buttons(self):
        for button in self.ability_buttons:
            button.text = "-"
            button.disabled = True
            button.selected = False

    def draw_ultimate_status(self, surface, tower, y):
        if tower.has_ultimate():
            text = "Ultimate: unlocked"
            color = YELLOW
        else:
            text = f"Ultimate: unlocks at lvl {TOWER_ULTIMATE_LEVEL} ({tower.level}/{TOWER_ULTIMATE_LEVEL})"
            color = MUTED_TEXT
        draw_text(surface, self.small_font, text, color, (PANEL_X + 18, y))

    def draw_messages(self, surface, game):
        if game.state == "game_over":
            self.draw_center_message(surface, "GAME OVER", "Click to return to menu")
        elif game.state == "victory":
            self.draw_center_message(surface, "VICTORY", "Click to return to menu")

    def draw_pause_menu(self, surface, game, mouse_pos):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))

        menu_rect = pygame.Rect(
            (WIDTH - PAUSE_MENU_WIDTH) // 2,
            (HEIGHT - PAUSE_MENU_HEIGHT) // 2,
            PAUSE_MENU_WIDTH,
            PAUSE_MENU_HEIGHT,
        )
        pygame.draw.rect(surface, PANEL, menu_rect, border_radius=14)
        pygame.draw.rect(surface, (78, 89, 118), menu_rect, 2, border_radius=14)

        self.pause_speed_slider.sync(game.game_speed)
        self.pause_volume_slider.sync(game.music_manager.volume)

        draw_text(surface, self.title_font, "Pause", TEXT, (menu_rect.centerx, menu_rect.y + 22), center=True)
        draw_text(surface, self.small_font, "Game speed", TEXT, (menu_rect.x + 40, menu_rect.y + 118))
        draw_text(surface, self.small_font, f"x{game.game_speed:.1f}", YELLOW, (menu_rect.right - 80, menu_rect.y + 118))
        self.pause_speed_slider.draw(surface, mouse_pos)

        draw_text(surface, self.small_font, "Music volume", TEXT, (menu_rect.x + 40, menu_rect.y + 208))
        draw_text(surface, self.small_font, f"{int(game.music_manager.volume * 100)}%", YELLOW,
                  (menu_rect.right - 80, menu_rect.y + 208))
        self.pause_volume_slider.draw(surface, mouse_pos, active_color=(88, 225, 220))

        for button in self.pause_buttons:
            button.draw(surface, self.small_font, mouse_pos)

    def draw_center_message(self, surface, title, subtitle):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        draw_text(surface, self.title_font, title, TEXT, (WIDTH // 2, HEIGHT // 2 - 30), True)
        draw_text(surface, self.font, subtitle, MUTED_TEXT, (WIDTH // 2, HEIGHT // 2 + 6), True)

    def handle_click(self, pos):
        for button in self.buttons:
            if button.rect.collidepoint(pos) and not button.disabled:
                return button.action
        return None

    def handle_pause_event(self, event):
        speed = self.pause_speed_slider.handle_event(event)
        if speed is not None:
            value, committed = speed
            return ("set_speed", value, committed)

        volume = self.pause_volume_slider.handle_event(event)
        if volume is not None:
            value, committed = volume
            return ("set_music_volume", value, committed)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.pause_buttons:
                if button.rect.collidepoint(event.pos):
                    return ("action", button.action, True)
        return None

    def draw_upgrades(self, surface, player):
        surface.fill((13, 16, 29))
        draw_text(surface, self.title_font, "Permanent Upgrades", TEXT, (WIDTH // 2, 45), center=True)
        draw_text(surface, self.font, f"Meta coins: {player.meta_coins}", YELLOW, (WIDTH // 2, 84), center=True)
        mouse_pos = pygame.mouse.get_pos()
        upgrade_width = 520
        upgrade_x = (WIDTH - upgrade_width) // 2

        y = 140
        rects = {}
        for key, info in UPGRADE_INFO.items():
            level = player.get_upgrade_level(key)
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
