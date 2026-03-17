class Room:

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connected_rooms = {}
        self.items = []
        self.enemy = None
        self.visited = False

    def connect(self, direction, room):
        self.connected_rooms[direction] = room

    def describe(self):

        print("\n==", self.name, "==")
        print(self.description)

        if self.items:
            print("Items here:", self.items)

        if self.enemy and self.enemy.is_alive():
            print("Enemy present:", self.enemy.name)

        print("Exits:", list(self.connected_rooms.keys()))