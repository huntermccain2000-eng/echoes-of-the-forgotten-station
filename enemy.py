from character import Character

class Enemy(Character):

    def __init__(self, name, health, damage):
        super().__init__(name, health)
        self.damage = damage - 5

    def attack(self, player):
        print(self.name, "attacks!")
        player.take_damage(self.damage)


class BossEnemy(Enemy):

    def attack(self, player):
        print(self.name, "launches a massive attack!")
        player.take_damage(18)