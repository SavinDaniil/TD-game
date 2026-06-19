from src.constants import (START_COINS, START_HP, UPGRADE_INFO, HP_PER_UPGRADE, COINS_PER_UPGRADE, META_COIN_RATIO,
                           DAMAGE_BONUS_PER_LEVEL, SPEED_BONUS_PER_LEVEL, REWARD_BONUS_PER_LEVEL)


class Player:
    def __init__(self, save_data):
        self._save_data = save_data
        self._permanent_upgrades = save_data["upgrades"].copy()
        self.max_hp = START_HP + self.permanent_upgrades["max_hp"] * HP_PER_UPGRADE
        self.hp = self.max_hp
        self.coins = START_COINS + self.permanent_upgrades["start_coins"] * COINS_PER_UPGRADE
        self.meta_coins = save_data["meta_coins"]

    @property
    def permanent_upgrades(self):
        return self._permanent_upgrades

    @property
    def meta_coins(self):
        return self._save_data["meta_coins"]

    @meta_coins.setter
    def meta_coins(self, value):
        self._save_data["meta_coins"] = value

    @property
    def damage_multiplier(self):
        return 1 + self.permanent_upgrades["damage_bonus"] * DAMAGE_BONUS_PER_LEVEL

    @property
    def speed_multiplier(self):
        return 1 + self.permanent_upgrades["attack_speed_bonus"] * SPEED_BONUS_PER_LEVEL

    @property
    def reward_multiplier(self):
        return 1 + self.permanent_upgrades["kill_reward_bonus"] * REWARD_BONUS_PER_LEVEL

    def add_kill_reward(self, amount):
        value = int(amount * self.reward_multiplier)
        self.coins += value
        self.meta_coins += max(1, value // META_COIN_RATIO)
        self._save_data["meta_coins"] = self.meta_coins

    def spend(self, amount):
        if self.coins < amount:
            return False
        self.coins -= amount
        return True

    def take_damage(self, amount):
        self.hp -= int(max(1, amount))

    def buy_permanent_upgrade(self, key):
        info = UPGRADE_INFO[key]
        level = self.permanent_upgrades[key]
        if level >= info["max"]:
            return False

        cost = info["base_cost"] + info["step"] * level
        if self.meta_coins < cost:
            return False

        self.meta_coins -= cost
        self.permanent_upgrades[key] += 1
        self._save_data["meta_coins"] = self.meta_coins
        return True
