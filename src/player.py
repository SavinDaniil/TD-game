from src.constants import START_COINS, START_HP


class Player:
    def __init__(self):
        self.max_hp = START_HP
        self.hp = self.max_hp
        self.coins = START_COINS

    def take_damage(self, amount):
        self.hp -= int(max(1, amount))

    def add_coins(self, amount):
        self.coins += amount
