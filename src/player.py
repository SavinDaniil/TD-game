from src.constants import START_COINS, START_HP, UPGRADE_INFO


class Player:
    def __init__(self, save_data):
        self.save_data = save_data
        self.permanent_upgrades = save_data["upgrades"]
        self.max_hp = START_HP + self.permanent_upgrades["max_hp"] * 12
        self.hp = self.max_hp
        self.coins = START_COINS + self.permanent_upgrades["start_coins"] * 30
        self.meta_coins = save_data["meta_coins"]

    @property
    def damage_multiplier(self):
        return 1 + self.permanent_upgrades["damage_bonus"] * 0.04

    @property
    def speed_multiplier(self):
        return 1 + self.permanent_upgrades["attack_speed_bonus"] * 0.035

    @property
    def reward_multiplier(self):
        return 1 + self.permanent_upgrades["kill_reward_bonus"] * 0.08

    def add_kill_reward(self, amount):
        value = int(amount * self.reward_multiplier)
        self.coins += value
        self.meta_coins += max(1, value // 3)
        self.save_data["meta_coins"] = self.meta_coins

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
        self.save_data["meta_coins"] = self.meta_coins
        return True
