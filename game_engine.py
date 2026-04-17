import json
import os

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

        self.station_destruction = False
        self.destruction_turns = 0

        self.bridge_search_count = 0
        self.med_search_count = 0
        self.engineering_search_count = 0
        self.security_search_count = 0
        self.cargo_search_count = 0
        self.cryo_search_count = 0

        self.secret_exit_found = False
        self.locker_open = False

        self.create_world()

    # -------------------------------------------------
    # WORLD (YOUR ORIGINAL CONTENT RESTORED)
    # -------------------------------------------------
    def create_world(self):

        cryo = Room("Cryo Chamber", "Cryo pods line the walls.")
        bridge = Room("Command Bridge", "The control center of the station.")
        engineering = Room("Engineering Bay", "Power systems flicker dangerously.")
        medical = Room("Medical Wing", "Old medical tools scattered.")
        cargo = Room("Cargo Hold", "Storage crates float in zero gravity.")
        security = Room("Security Office", "Weapon lockers remain sealed.")
        ai_core = Room("AI Core Room", "The rogue AI system resides here.")
        escape = Room("Escape Pod Bay", "Escape pods ready for launch.")

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

        engineering.enemy = Enemy("Security Drone", 40, 10)
        security.enemy = Enemy("Defense Turret", 50, 15)
        ai_core.enemy = BossEnemy("Station AI Guardian", 80, 20)

        self.rooms = {
            "Cryo Chamber": cryo,
            "Command Bridge": bridge,
            "Engineering Bay": engineering,
            "Medical Wing": medical,
            "Cargo Hold": cargo,
            "Security Office": security,
            "AI Core Room": ai_core,
            "Escape Pod Bay": escape
        }

        self.player = Player("Player")
        self.player.move(cryo)

    # -------------------------------------------------
    # MAIN COMMAND ENTRY
    # -------------------------------------------------
    def process_command(self, cmd: str):

        cmd = cmd.lower().strip()
        parts = cmd.split()

        if not parts:
            return self.response(["Invalid command"])

        action = parts[0]
        output = []

        # ---------------- MOVE ----------------
        if action == "move":
            if len(parts) < 2:
                return self.response(["Move where?"])

            direction = parts[1]

            if direction in self.player.current_room.connected_rooms:

                new_room = self.player.current_room.connected_rooms[direction]
                self.player.move(new_room)

                output.append(f"You move {direction}.")
                output.append(new_room.description)

                if new_room.enemy and new_room.enemy.is_alive():
                    output.append(f"A hostile presence emerges: {new_room.enemy.name}")
                    return self.combat(new_room.enemy, output)

            else:
                output.append("That path is blocked.")

        # ---------------- SEARCH (FULL STORY LOGIC RESTORED) ----------------
        elif action == "search":
            output.extend(self.search_room())

        # ---------------- TAKE ----------------
        elif action == "take":
            item = " ".join(parts[1:])
            output.append(self.take_item(item))

        # ---------------- USE ----------------
        elif action == "use":
            item = " ".join(parts[1:])
            output.append(self.use_item(item))

        # ---------------- STATUS ----------------
        elif action == "status":
            output.append(f"Health: {self.player.health}")
            output.append(f"Inventory: {self.player.inventory}")

        # ---------------- MAP ----------------
        elif action == "map":
            output.append(self.get_map())

        # ---------------- HELP ----------------
        elif action == "help":
            output.append(self.get_help_text())

        # ---------------- QUIT ----------------
        elif action == "quit":
            self.running = False
            output.append("You abandon the station...")

        else:
            output.append("Unknown command.")

        return self.response(output)

    # -------------------------------------------------
    # FULL SEARCH SYSTEM (YOUR ORIGINAL TEXT RESTORED)
    # -------------------------------------------------
    def search_room(self):

        room = self.player.current_room
        output = []

        # ---------------- COMMAND BRIDGE ----------------
        if room.name == "Command Bridge":

            self.bridge_search_count += 1

            output.append("A vast command bridge, silent and abandoned.")

            if self.bridge_search_count == 2:
                output.append("Large windows reveal the endless void outside.")

            elif self.bridge_search_count == 3:
                output.append("A worn captain’s hat rests on the command chair.")

            elif self.bridge_search_count == 4:
                output.append("Scratches mark a panel — something may be hidden here.")

            elif self.bridge_search_count >= 5:

                if "prybar" in self.player.inventory and not self.secret_exit_found:

                    output.append("You pry open a hidden maintenance hatch!")
                    output.append("A secret route to the Escape Pod Bay is revealed.")

                    bridge = self.rooms["Command Bridge"]
                    escape = self.rooms["Escape Pod Bay"]

                    bridge.connect("secret", escape)

                    self.secret_exit_found = True

                else:
                    output.append("The panel is damaged but sealed tight.")

        # ---------------- MEDICAL ----------------
        elif room.name == "Medical Wing":

            self.med_search_count += 1

            if self.med_search_count == 1:
                output.append("Medical beds lie scattered, as if abandoned mid-treatment.")

            elif self.med_search_count == 2:
                output.append("You find an emergency medkit.")
                if "medkit" not in room.items:
                    room.items.append("medkit")

            else:
                output.append("Nothing else remains here.")

        # ---------------- ENGINEERING ----------------
        elif room.name == "Engineering Bay":

            self.engineering_search_count += 1

            if self.engineering_search_count == 1:
                output.append("Burned wiring and sparking panels line the walls.")

            elif self.engineering_search_count == 2:
                output.append("A heavy prybar is lodged under debris.")
                if "prybar" not in room.items:
                    room.items.append("prybar")

            elif self.engineering_search_count == 3:
                output.append("An AI override slot is exposed behind a console.")
                output.append("It requires an ACCESS CARD.")

            else:
                output.append("The room is stripped of anything useful.")

        # ---------------- SECURITY ----------------
        elif room.name == "Security Office":

            self.security_search_count += 1

            if self.security_search_count == 1:
                output.append("Locked weapon lockers line the walls.")

            elif self.security_search_count == 2:

                if "prybar" not in self.player.inventory:
                    output.append("The lockers are too strong to force open.")
                else:
                    output.append("You pry open a locker and find an ACCESS CARD!")
                    self.locker_open = True
                    if "access card" not in room.items:
                        room.items.append("access card")

            else:
                output.append("Everything of value is already taken.")

        # ---------------- CARGO ----------------
        elif room.name == "Cargo Hold":

            self.cargo_search_count += 1

            if self.cargo_search_count == 1:
                output.append("Crates float silently, labeled with warnings.")

            else:
                output.append("Nothing useful remains in the cargo hold.")

        # ---------------- CRYO ----------------
        elif room.name == "Cryo Chamber":

            self.cryo_search_count += 1

            if self.cryo_search_count == 1:
                output.append("Your cryo pod is the only one still active.")

            elif self.cryo_search_count == 2:
                output.append("You find a map lying on the floor.")
                if "map" not in room.items:
                    room.items.append("map")

            else:
                output.append("The chamber feels increasingly empty.")

        else:
            output.append(room.description)

        return output

    # -------------------------------------------------
    # ITEMS
    # -------------------------------------------------
    def take_item(self, item):

        room = self.player.current_room

        if item in room.items:
            self.player.inventory.append(item)
            room.items.remove(item)
            return f"Picked up {item}"

        return "Item not found"

    def use_item(self, item):

        if item in self.player.inventory:
            return f"You use the {item}."
        return "You don't have that item."

    # -------------------------------------------------
    # MAP TEXT
    # -------------------------------------------------
    def get_map(self):

        return f"""
            Command Bridge
                   |
Medical Wing -- Cryo Chamber -- Engineering Bay
                   |
                Cargo Hold
                   |
            Security Office
                   |
              AI Core Room
                   |
             Escape Pod Bay

You are in: {self.player.current_room.name}
"""

    # -------------------------------------------------
    # HELP TEXT
    # -------------------------------------------------
    def get_help_text(self):

        return "\n".join([
            "move <direction>",
            "search",
            "take <item>",
            "use <item>",
            "status",
            "map",
            "quit"
        ])

    # -------------------------------------------------
    # COMMAND GENERATION FOR GUI
    # -------------------------------------------------
    def get_commands(self):

        room = self.player.current_room
        cmds = []

        for d in room.connected_rooms:
            cmds.append(f"move {d}")

        for item in room.items:
            cmds.append(f"take {item}")

        for item in self.player.inventory:
            cmds.append(f"use {item}")

        cmds += ["search", "status", "map", "help", "quit"]

        return cmds

    # -------------------------------------------------
    # RESPONSE WRAPPER
    # -------------------------------------------------
    def response(self, output):

        return {
            "output": output,
            "commands": self.get_commands(),
            "game_over": not self.running,
            "hp": self.player.health,
            "room": self.player.current_room.name,
            "inventory": self.player.inventory
        }