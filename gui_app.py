import tkinter as tk
from tkinter import ttk
import builtins
import threading
import queue

from game_engine import GameEngine


class GameGUI:
    def __init__(self, root):

        self.root = root
        self.root.title("Space Station Survival")
        self.root.geometry("1100x720")

        # Engine
        self.engine = GameEngine()

        # Communication
        self.output_queue = queue.Queue()
        self.command_queue = queue.Queue()

        # Command tracking
        self.available_commands = []
        self.collecting_commands = False

        # Build UI
        self.create_widgets()

        # Hook input/output
        self.redirect_io()

        # Start game
        self.start_game()

        # UI loop
        self.root.after(100, self.update_screen)

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def create_widgets(self):

        left = tk.Frame(self.root)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.output_box = tk.Text(
            left,
            bg="black",
            fg="lime",
            font=("Consolas", 11),
            wrap="word",
            state="disabled"
        )
        self.output_box.pack(fill="both", expand=True)

        bottom = tk.Frame(left)
        bottom.pack(fill="x", pady=5)

        self.entry = tk.Entry(bottom, font=("Consolas", 11))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.send_entry)

        ttk.Button(bottom, text="Send", command=self.send_entry).pack(side="left", padx=5)

        # Right panel
        right = tk.Frame(self.root)
        right.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(right, text="COMMANDS", font=("Arial", 12, "bold")).pack(pady=5)

        self.button_frame = tk.Frame(right)
        self.button_frame.pack()

    # -------------------------------------------------
    # INPUT / OUTPUT REDIRECT
    # -------------------------------------------------
    def redirect_io(self):

        self.real_print = builtins.print
        self.real_input = builtins.input

        def fake_print(*args, **kwargs):
            text = " ".join(str(a) for a in args)
            self.output_queue.put(text)

        def fake_input(prompt=""):
            if prompt:
                self.output_queue.put(prompt)
            return self.command_queue.get()

        builtins.print = fake_print
        builtins.input = fake_input

    def restore_io(self):
        builtins.print = self.real_print
        builtins.input = self.real_input

    # -------------------------------------------------
    # GAME THREAD
    # -------------------------------------------------
    def start_game(self):
        thread = threading.Thread(target=self.run_game, daemon=True)
        thread.start()

    def run_game(self):
        try:
            self.engine.start_game()
        except Exception as e:
            self.output_queue.put(f"ERROR: {e}")
        finally:
            self.restore_io()

    # -------------------------------------------------
    # SEND COMMANDS
    # -------------------------------------------------
    def send_command(self, cmd):

        self.write_text("> " + cmd)
        self.command_queue.put(cmd)

        if cmd.lower() == "quit":
            self.root.after(200, self.root.destroy)

    def send_entry(self, event=None):

        cmd = self.entry.get().strip()
        if not cmd:
            return

        self.send_command(cmd)
        self.entry.delete(0, tk.END)

    # -------------------------------------------------
    # VALID COMMAND FILTER
    # -------------------------------------------------
    def is_valid_command(self, text):

        text = text.strip().lower()

        base = {
            "search", "map", "status", "save",
            "load", "help", "history", "quit",
            "fight", "run"
        }

        if text.startswith("move "):
            return True
        if text.startswith("take "):
            return True
        if text.startswith("use "):
            return True

        return text in base

    # -------------------------------------------------
    # SCREEN UPDATE LOOP
    # -------------------------------------------------
    def update_screen(self):

        rebuild = False

        while not self.output_queue.empty():

            text = self.output_queue.get()
            self.write_text(text)

            clean = text.strip().lower()

            # Start command list capture
            if clean == "--- available actions ---":
                self.collecting_commands = True
                self.available_commands = []
                rebuild = True
                continue

            # Combat mode override
            if clean.startswith("combat with"):
                self.available_commands = ["fight", "run"]
                rebuild = True
                continue

            if clean == "fight/run:":
                self.available_commands = ["fight", "run"]
                rebuild = True
                continue

            # Collect commands
            if self.collecting_commands:

                if self.is_valid_command(clean):
                    self.available_commands.append(clean)
                else:
                    self.collecting_commands = False

        if rebuild:
            self.build_buttons()

        self.root.after(100, self.update_screen)

    # -------------------------------------------------
    # BUTTON SYSTEM
    # -------------------------------------------------
    def build_buttons(self):

        for w in self.button_frame.winfo_children():
            w.destroy()

        seen = set()

        for cmd in self.available_commands:

            if cmd in seen:
                continue

            seen.add(cmd)

            ttk.Button(
                self.button_frame,
                text=cmd.title(),
                width=22,
                command=lambda c=cmd: self.send_command(c)
            ).pack(pady=3)

    # -------------------------------------------------
    # OUTPUT
    # -------------------------------------------------
    def write_text(self, text):

        self.output_box.config(state="normal")
        self.output_box.insert("end", text + "\n")
        self.output_box.see("end")
        self.output_box.config(state="disabled")


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    GameGUI(root)
    root.mainloop()