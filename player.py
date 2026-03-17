from character import Character

class Player(Character):

    def __init__(self, name):
        super().__init__(name, 100)
        self.previous_room = None
        self.inventory = []
        self.current_room = None
        self.attack_power = 15
        self.rooms_visited = set()

    def move(self, room):
        self.previous_room = self.current_room
        self.current_room = room
        self.rooms_visited.add(room.name)

    def take_item(self, item):
        self.inventory.append(item)

    def use_item(self, item, game):

        if item not in self.inventory:
            print("You do not have that item.")
            return

        if item == "medkit":
            self.health = min(100, self.health + 100)
            print("You used a medkit and restored health.")
            self.inventory.remove(item)

        elif item == "access card":

            if self.current_room.name == "Engineering Bay" and game.access_slot_found:

                if not game.ai_core_disabled:
                    game.ai_core_disabled = True
                    print("\nYou swipe the access card at the engineering terminal.")
                    print("System override accepted.")
                    print("AI CORE DEFENSES DISABLED.\n")
                else:
                    print("The AI core is already disabled.")

            else:
                print("There is nothing here that uses an access card.")

    def show_status(self):

        print("\n--- STATUS ---")
        print("Health:", self.health)
        print("Inventory:", self.inventory)