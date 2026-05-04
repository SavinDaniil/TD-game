import json
import math
import os

from src.constants import SAVE_PATH


DEFAULT_SAVE = {
    "meta_coins": 0,
    "best_wave": 0,
    "upgrades": {
        "max_hp": 0,
        "damage_bonus": 0,
        "attack_speed_bonus": 0,
        "start_coins": 0,
        "kill_reward_bonus": 0,
    },
}


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def clamp(value, low, high):
    return max(low, min(high, value))


def load_save():
    if not os.path.exists(SAVE_PATH):
        save_json(DEFAULT_SAVE)
        return DEFAULT_SAVE.copy()

    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        data = DEFAULT_SAVE.copy()

    fixed = DEFAULT_SAVE.copy()
    fixed["upgrades"] = DEFAULT_SAVE["upgrades"].copy()
    fixed.update({key: data.get(key, fixed[key]) for key in fixed})
    fixed["upgrades"].update(data.get("upgrades", {}))
    save_json(fixed)
    return fixed


def save_json(data):
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def draw_text(surface, font, text, color, pos, center=False):
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)


def regular_polygon(center, radius, sides, angle_offset=0):
    points = []
    for index in range(sides):
        angle = angle_offset + 2 * math.pi * index / sides
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        points.append((x, y))
    return points
