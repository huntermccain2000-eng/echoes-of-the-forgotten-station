import json
import random

from player import Player
from room import Room
from enemy import Enemy, BossEnemy
from ai_controller import AIController
from database import save_game_history


class GameEngine:

    def __init__(self):

        self.rooms = {}
        self.player = None
        self.ai = AIController()
        self.running = True
        self.ai_core_disabled = False
        self.station_destruction = False
        self.destruction_turns = 0
        self.bridge_search_count = 0
        self.med_search_count = 0 
        self.engineering_search_count = 0
        self.security_search_count = 0
        self.cargo_search_count = 0
        self.cryo_search_count = 0
        self.locker_open = False    
        self.access_slot_found = False
        self.secret_exit_found = False 
        self.passive_items = ["prybar", "map"]

    def start_game(self):

        name = input("Enter your name: ")
        self.player = Player(name)

        self.create_world()

        self.player.move(self.rooms["Cryo Chamber"])

        print("\nYou awaken in a damaged cryo pod aboard a drifting space station...")
        print("TIP: Type 'help' at any time to see ALL commands")
        self.player.current_room.describe()
        self.show_available_commands()

        while self.running:

            try:
                command = input("\n> ").lower().split()
                action = command[0]
            except:
                print("Invalid command.")
                continue

            self.process_command(command)

            self.check_room_events()
            self.check_destruction_timer()
            self.check_endings()

    def create_world(self):

        cryo = Room("Cryo Chamber","Cryo pods line the walls.")
        bridge = Room("Command Bridge","The control center of the station.")
        engineering = Room("Engineering Bay","Power systems flicker dangerously.")
        medical = Room("Medical Wing","Old medical tools scattered.")
        cargo = Room("Cargo Hold","Storage crates float in zero gravity.")
        security = Room("Security Office","Weapon lockers remain sealed.")
        ai_core = Room("AI Core Room","The rogue AI system resides here.")
        escape = Room("Escape Pod Bay","Escape pods ready for launch.")

    
        cryo.connect("north", bridge)
        cryo.connect("east", engineering)
        cryo.connect("west", medical)
        cryo.connect("south", cargo)

     
        bridge.connect("south", cryo)

      
        engineering.connect("west", cryo)

      
        medical.connect("east", cryo)

       
        cargo.connect("north", cryo)
        cargo.connect("south", security)

      
        security.connect("north", cargo)
        security.connect("south", ai_core)

      
        ai_core.connect("north", security)
        ai_core.connect("south", escape)

       
        escape.connect("north", ai_core)


        engineering.enemy = Enemy("Security Drone",40,10)
        security.enemy = Enemy("Defense Turret",50,15)
        ai_core.enemy = BossEnemy("Station AI Guardian",80,20)

        self.rooms = {
            "Cryo Chamber":cryo,
            "Command Bridge":bridge,
            "Engineering Bay":engineering,
            "Medical Wing":medical,
            "Cargo Hold":cargo,
            "Security Office":security,
            "AI Core Room":ai_core,
            "Escape Pod Bay":escape
        }
    def show_available_commands(self):

        room = self.player.current_room

        print("\n--- Available Actions ---")

        # movement commands
        for direction in room.connected_rooms:
            print("move", direction)

        # item pickup
        for item in room.items:
            print("take", item)

        # item usage
        for item in self.player.inventory:
            if item not in self.passive_items:
                print("use", item)

        # general commands
        print("search")
        print("map")
        print("status")
        print("save")
        print("load")
        print("help")
        print("history")
        print("quit")
    def show_help(self):

        print("\n--- AVAILABLE COMMANDS ---")

        print("move north  - move north")
        print("move south  - move south")
        print("move east   - move east")
        print("move west   - move west")

        print("look        - view room description")
        print("take ITEM   - pick up an item")
        print("use ITEM    - use an item from inventory")

        print("Map         - shows a map")
        print("status      - show player health and inventory")
        print("save        - save the game")
        print("load        - load a saved game")

        print("help        - show this command list")
        print("history     - view past game runs")
        print("quit        - exit the game")
    def run_back(self):

        if self.player.previous_room is None:
            print("There is nowhere to run back to!")
            return

        print("You run back to the previous room!")

        temp = self.player.current_room
        self.player.current_room = self.player.previous_room
        self.player.previous_room = temp

        self.player.current_room.describe()
        self.show_available_commands()

    def show_map(self):

        current = self.player.current_room.name

        def marker(room):
            if room == current:
                return "[YOU]"
            return "[ ]"

        print("\n====== STATION MAP ======\n")

        print("                     Command Bridge", marker("Command Bridge"))
        print("                         |")
        print("Medical Wing", marker("Medical Wing"),
            "--- Cryo Chamber", marker("Cryo Chamber"),
            "--- Engineering Bay", marker("Engineering Bay"))
        print("                         |")
        print("                     Cargo Hold", marker("Cargo Hold"))
        print("                         |")
        print("                  Security Office", marker("Security Office"))
        print("                         |")
        print("                  AI Core Room", marker("AI Core Room"))
        print("                         |")
        print("                   Escape Pod Bay", marker("Escape Pod Bay"))

        print("\n[YOU] = Your current location\n")

    def process_command(self, command):

        action = command[0]

        if action == "move":

            if len(command) < 2:
                print("Move where?")
                return

            self.move_player(command[1])

        elif action == "search":

            room = self.player.current_room

            room.describe()

            # secret discovery mechanic and BRIDGE SEARCH
            if room.name == "Command Bridge" and not self.secret_exit_found:

                self.bridge_search_count += 1
                print("A normal command bridge, however empty and ominous it may be. ")
                
                if self.bridge_search_count == 2:
                    print("Large windows provide a vivid sight into the empty space beyond")

                elif self.bridge_search_count == 3:
                    print("A old captains hat lies in the command chair, for some reason it looks like the hat of a pirate from the old terran stories.")
                    print("You leave the hat.")
                elif self.bridge_search_count == 4:
                    print("You notice scratches near a console panel...It could be moved, if you had the right tool.")

                elif self.bridge_search_count >= 5:
                    
                    if "prybar" in self.player.inventory:
                        print("\nYou pry open a hidden maintenance hatch hidden behind the console pannel!")
                        print("Its a secret path leads directly to the Escape Pod Bay!")

                        bridge = self.rooms["Command Bridge"]
                        escape = self.rooms["Escape Pod Bay"]

                        bridge.connect("secret", escape)

                        self.secret_exit_found = True
                    if "prybar" not in self.player.inventory: 
                        print(("You notice scratches near a console panel...It could be moved, if you had the right tool."))
        # MEDICAL ROOM SEARCHING
            if room.name== "Medical Wing":
                    self.med_search_count +=1
                    if self.med_search_count == 1:
                        print("Emergency sick beds lie scattered as if used as makeshift barricades...")
                    if self.med_search_count == 2:
                        print("You look closer and find an emergency medkit!")
                        if "medkit" not in room.items:
                            room.items.append("medkit")
                    if self.med_search_count == 3:
                        print("There is nothing usefull left...")
            # -------- ENGINEERING ROOM SEARCH --------
            if room.name == "Engineering Bay":

                self.engineering_search_count += 1

                if self.engineering_search_count == 1:
                    print("Burned wiring and sparking control panels cover the walls.")
                elif self.engineering_search_count == 2:
                    print("You find a heavy prybar lodged under a collapsed panel.")

                    if "prybar" not in room.items:
                        room.items.append("prybar")
                
                elif self.engineering_search_count == 3:
                    print("Behind a damaged console you discover a secured AI override slot.")
                    print("It looks like it requires an ACCESS CARD.")
                    self.access_slot_found = True

                elif self.engineering_search_count >= 4:
                    print("The AI override slot remains open, nothing else remains in this room")    
            # -------- SECURITY OFFICE SEARCH --------
            if room.name == "Security Office":

                self.security_search_count += 1

                if self.security_search_count == 1:
                    print("Locked weapon lockers line the walls. One locker is damaged but it can not be opened by hand.")

                elif self.security_search_count == 2:
                    if "prybar" not in self.player.inventory:
                        print("You cannot open the damaged locker by hand.")
                        self.security_search_count -= 1  # stays on step 2
                    
                    elif "prybar" in self.player.inventory:
                        print("You pry open a damaged locker and discover an ACCESS CARD!")
                        self.locker_open = True
                        
                        if "access card" not in room.items:
                            room.items.append("access card") 

                elif self.security_search_count >= 3 and self.locker_open == True:
                    print("The rest of the lockers are sealed too tight. There is nothing left for you.")
            #--------Cargo go cargoooo searching-----
            if room.name == "Cargo Hold":
                self.cargo_search_count += 1

                if self.cargo_search_count == 1:
                    print("The crates are marked with various warning labels")

                elif self.cargo_search_count == 2:
                    print("Upon closer inspection... You find nothing usefull to your journey")

                elif self.cargo_search_count >= 3:
                    print(".....There really is nothing usefull in the crates.")
            #----------CRYO SEARCHING ------
            if room.name == "Cryo Chamber":
                self.cryo_search_count += 1

                if self.cryo_search_count == 1:
                    print("As you look around the room you notice your Cryo Pod was the only one still active.")

                elif self.cryo_search_count == 2:
                    print("You look closer and find a Map on the ground!")
                    if "map" not in room.items:
                        room.items.append("map")

                elif self.cryo_search_count >= 3:
                    print("There is nothing left in this room. Its time to move on.")
            
            self.show_available_commands()
        elif action == "take":

            if len(command) < 2:
                print("Take what?")
                return

            item = " ".join(command[1:])
            self.take_item(item)

        elif action == "use":

            if len(command) < 2:
                print("Use what?")
                return

            item = " ".join(command[1:])
            self.player.use_item(item, self)

        elif action == "status":
            self.player.show_status()
        elif action == "map":
            if "map" in self.player.inventory:
                self.show_map()
            else:
                print("You don't have a map yet.")

        elif action == "help":
            self.show_help()

        elif action == "save":
            self.save_game()

        elif action == "load":
            self.load_game()

        elif action == "quit":
            self.running = False
        
        elif action == "history":
            from database import show_game_history
            show_game_history()

        else:
            print("Unknown command.")
            self.ai.failed_actions += 1

    def move_player(self, direction):

        room = self.player.current_room

        if direction in room.connected_rooms:

            new_room = room.connected_rooms[direction]
            self.player.move(new_room)
            new_room.describe()
            self.show_available_commands()

        else:
            print("You cannot go that way.")
            self.ai.failed_actions += 1

    def take_item(self, item):

        room = self.player.current_room

        if item in room.items:

            self.player.take_item(item)
            room.items.remove(item)
            print("Picked up:",item)

        else:
            print("Item not found.")

    def handle_combat(self, enemy):

        print("\nCombat with", enemy.name)

        total_damage_dealt = 0
        total_damage_taken = 0

        while enemy.is_alive() and self.player.is_alive():

            print("\n--- Combat Status ---")
            print("Your Health:", self.player.health)
            print(enemy.name, "Health:", enemy.health)

            action = input("fight/run: ")

            if action == "fight":

                damage = self.player.attack_power
                enemy.take_damage(damage)

                total_damage_dealt += damage

                print("You dealt", damage, "damage!")

                if enemy.is_alive():

                    enemy.attack(self.player)

                    total_damage_taken += enemy.damage
                    self.ai.damage_taken += enemy.damage

                    print(enemy.name, "dealt", enemy.damage, "damage!")

            elif action == "run":
                print("You escaped!")
                self.run_back()
                return

        print("\n--- Combat Summary ---")
        print("Total Damage Dealt:", total_damage_dealt)
        print("Total Damage Taken:", total_damage_taken)
        self.show_available_commands()

        if self.player.health <= 0:
            print("You have died.")
    
            save_game_history(
                self.player.name,
                "Death",
            len(self.player.rooms_visited)
            )   

            self.running = False
        else:
            print("Enemy defeated!")
            self.ai.combat_wins += 1
            # If the AI Guardian was destroyed, start station destruction
            if enemy.name == "Station AI Guardian" and not self.ai_core_disabled:

                print("\nWARNING: AI CORE DESTROYED")
                print("STATION REACTOR UNSTABLE")
                print("SELF-DESTRUCT INITIATED")
                print("YOU MUST ESCAPE TO THE POD BAY!\n")

                self.station_destruction = True
                self.destruction_turns = 4
    # ---------------- DESTRUCTION TIMER ---------------- #

    def check_destruction_timer(self):

        if not self.station_destruction:
            return

        self.destruction_turns -= 1

        print(f"\nSELF-DESTRUCT IN {self.destruction_turns} TURNS")

        if self.destruction_turns <= 0:

            print("\nThe station explodes before you escape.")
            print("ENDING: Total Destruction")
            save_game_history(
            self.player.name,
            "Total Destruction",
            len(self.player.rooms_visited)
            )
            self.running = False

    def check_room_events(self):

        room = self.player.current_room

        if room.enemy and room.enemy.is_alive():

            if room.name == "AI Core Room" and self.ai_core_disabled:
                print("The AI core defenses are offline. The guardian is inactive.")
                print("You are now left alone on a barren station, maybe someone will find you...only time will tell.")
                print("ENDING: Savior")
                print("")
                room.enemy.health = 0
                save_game_history(
                self.player.name,
                "AI Shutdown Ending",
                len(self.player.rooms_visited)
            )

                self.running = False
            self.ai.update(self.player,room.enemy)

            self.handle_combat(room.enemy)

     # ---------------- ENDINGS ---------------- #

    def check_endings(self):

        room = self.player.current_room.name

        if room == "Escape Pod Bay":

            if self.station_destruction:

                print("\nYou launch an escape pod just as the station explodes.")
                print("As your pod is ejected into space you look to the singular cryopod within.")
                print("You enter the cryopod and hope the next time you wake up its somehwere safe... if you ever wake up at all.")
                print("ENDING: Narrow Escape")
                print("")

                save_game_history(self.player.name,"Narrow Escape Ending",len(self.player.rooms_visited))

            else:

                print("\nYou enter the escape pod and press the launch button")
                print("As your pod is ejected into space you look to the singular cryopod within.")
                print("You enter the cryopod and hope the next time you wake up its somehwere safe... if you ever wake up at all.")
                print("ENDING: Survivor")
                print("")

                save_game_history(self.player.name,"Escape Ending",len(self.player.rooms_visited))

            self.running = False

    def save_game(self):

        enemy_states = {}

        for room_name, room in self.rooms.items():
            if room.enemy:
                enemy_states[room_name] = {
                    "health": room.enemy.health
                }

        data = {
            "name": self.player.name,
            "health": self.player.health,
            "inventory": self.player.inventory,
            "room": self.player.current_room.name,
            "enemy_states": enemy_states,
            "locker_open": self.locker_open,
            "station_destruction": self.station_destruction,
            "destruction_turns": self.destruction_turns,
            "bridge_search_count": self.bridge_search_count,
            "engineering_search_count": self.engineering_search_count,
            "security_search_count": self.security_search_count,
            "cryo_search_count": self.cryo_search_count,
            "secret_exit_found": self.secret_exit_found,
            "access_slot_found": self.access_slot_found,
            "access_slot_found": self.access_slot_found,
            "secret_exit_found": self.secret_exit_found
               }

        with open("savegame.json", "w") as f:
            json.dump(data, f)

        print("Game saved.")

    def load_game(self):

        try:
            with open("savegame.json") as f:
                data = json.load(f)

        except:
            print("Save file not found.")
            return

        # restore player
        self.player.name = data["name"]
        self.player.health = data["health"]
        self.player.inventory = data["inventory"]
        self.player.current_room = self.rooms[data["room"]]

        # restore enemies
        enemy_states = data.get("enemy_states", {})

        for room_name, state in enemy_states.items():
            room = self.rooms[room_name]

            if room.enemy:
                room.enemy.health = state["health"]

        # restore world flags
        self.bridge_search_count = data.get("bridge_search_count", 0)
        self.med_search_count = data.get("med_search_count", 0)
        self.engineering_search_count = data.get("engineering_search_count", 0)
        self.security_search_count = data.get("security_search_count", 0)
        self.cargo_search_count = data.get("cargo_search_count", 0)
        self.cryo_search_count = data.get("cryo_search_count", 0)
        self.access_slot_found = data.get("access_slot_found", False)
        self.secret_exit_found = data.get("secret_exit_found", False)
        self.locker_open = data.get("locker_open", False)
        self.station_destruction = data.get("station_destruction", False)
        self.destruction_turns = data.get("destruction_turns", 0)

        print("Game loaded.")
