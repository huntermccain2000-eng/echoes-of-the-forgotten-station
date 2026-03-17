class AIController:

    def __init__(self):
        self.damage_taken = 0
        self.combat_wins = 0
        self.failed_actions = 0

    def rule_assistance(self):

        if self.damage_taken > 50:
            print("TIP: You may want to visit the Medical Wing.")

    def rule_difficulty(self, enemy):

        if self.combat_wins >= 2 and enemy:
            enemy.damage += 2
            print("The enemies seem to be adapting...")

    def rule_exploration(self, player):

        if len(player.rooms_visited) < 3:
            print("TIP: Exploring more areas may help uncover clues.")

    def update(self, player, enemy):

        self.rule_assistance()
        self.rule_exploration(player)

        if enemy:
            self.rule_difficulty(enemy)