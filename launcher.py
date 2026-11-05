"""Main launcher window and local user preferences."""

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from games.arcade import Breakout, Pong, Snake, Tetris
from games.board import Blackjack, ConnectFour, Reversi, TicTacToe
from games.puzzles import Game2048, LightsOut, Memory, Maze, Minesweeper, SlidingPuzzle
from games.quick import Hangman, GuessNumber, ReactionTest, RockPaperScissors, Simon, TypingTest

APP_DIR = Path.home() / ".classic_arcade_launcher"
SETTINGS_FILE = APP_DIR / "settings.json"

GAME_LIST = [
    ("Snake", "Arcade", "Guide the snake, eat food, and avoid your tail.", Snake),
    ("Pong", "Arcade", "A paddle duel against the computer.", Pong),
    ("Breakout", "Arcade", "Bounce the ball and clear every brick.", Breakout),
    ("Tetris", "Arcade", "Fit falling blocks together and clear lines.", Tetris),
    ("Minesweeper", "Puzzle", "Find every safe tile without hitting a mine.", Minesweeper),
    ("2048", "Puzzle", "Combine matching tiles to reach 2048.", Game2048),
    ("Memory", "Puzzle", "Match all pairs with as few moves as possible.", Memory),
    ("Lights Out", "Puzzle", "Turn off every light on the board.", LightsOut),
    ("Sliding Puzzle", "Puzzle", "Arrange the numbered tiles in order.", SlidingPuzzle),
    ("Maze", "Puzzle", "Find your way from the start to the exit.", Maze),
    ("Tic-Tac-Toe", "Board", "Get three marks in a row against the computer.", TicTacToe),
    ("Connect Four", "Board", "Connect four discs before the computer does.", ConnectFour),
    ("Reversi", "Board", "Capture more squares than your opponent.", Reversi),
    ("Blackjack", "Board", "Beat the dealer without going over 21.", Blackjack),
    ("Guess the Number", "Quick", "Use hints to find the secret number.", GuessNumber),
    ("Rock Paper Scissors", "Quick", "Play against the computer.", RockPaperScissors),
    ("Hangman", "Quick", "Guess the hidden word before the drawing is complete.", Hangman),
    ("Simon", "Quick", "Repeat the growing sequence of colors.", Simon),
    ("Reaction Test", "Quick", "Test how quickly you react to a signal.", ReactionTest),
    ("Typing Test", "Quick", "Measure your typing speed and accuracy.", TypingTest),
]


class ArcadeLauncher(tk.Tk):
    """Game catalog with search, category filters, and favorites."""

    def __init__(self):
        super().__init__()
        self.title("Classic Arcade")
        self.geometry("1100x760")
        self.minsize(820, 600)
        self.configure(bg="#10131c")
        self.settings = self._load_settings()
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All games")
        self.show_favorites = False
        self._build_style()
        self._build_layout()
        self._render_games()

    def _load_settings(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"favorites": [], "recent": []}

    def _save_settings(self):
        SETTINGS_FILE.write_text(
            json.dumps(self.settings, indent=2), encoding="utf-8"
        )

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Arcade.TCombobox",
            fieldbackground="#202638",
            background="#202638",
            foreground="#f4f6fb",
            arrowcolor="#f4f6fb",
        )
        style.map(
            "Arcade.TCombobox",
            fieldbackground=[("readonly", "#202638")],
            foreground=[("readonly", "#f4f6fb")],
        )

    def _build_layout(self):
        header = tk.Frame(self, bg="#10131c")
        header.pack(fill="x", padx=32, pady=(26, 16))
        tk.Label(
            header, text="CLASSIC ARCADE", bg="#10131c",
            fg="#f4f6fb", font=("Segoe UI", 25, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header, text="Twenty timeless games. One place to play.",
            bg="#10131c", fg="#929bb0", font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(4, 0))

        toolbar = tk.Frame(self, bg="#10131c")
        toolbar.pack(fill="x", padx=32, pady=(0, 18))
        search = tk.Entry(
            toolbar, textvariable=self.search_var, relief="flat",
            bg="#202638", fg="#f4f6fb", insertbackground="#f4f6fb",
            font=("Segoe UI", 11),
        )
        search.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 12))
        search.bind("<KeyRelease>", lambda _event: self._render_games())

        selector = ttk.Combobox(
            toolbar, textvariable=self.category_var,
            values=["All games", "Arcade", "Puzzle", "Board", "Quick"],
            state="readonly", width=15, style="Arcade.TCombobox",
        )
        selector.pack(side="left", ipady=7)
        selector.bind("<<ComboboxSelected>>", lambda _event: self._render_games())

        self.favorites_button = tk.Button(
            toolbar, text="☆ Favorites", command=self._toggle_favorites,
            bg="#202638", fg="#f4f6fb", activebackground="#303a52",
            activeforeground="#ffffff", relief="flat", padx=14, pady=9,
            font=("Segoe UI", 10, "bold"),
        )
        self.favorites_button.pack(side="left", padx=(12, 0))

        self.status = tk.Label(
            self, text="", bg="#10131c", fg="#929bb0",
            font=("Segoe UI", 10),
        )
        self.status.pack(anchor="w", padx=34, pady=(0, 8))

        container = tk.Frame(self, bg="#10131c")
        container.pack(fill="both", expand=True, padx=32, pady=(0, 28))
        self.canvas = tk.Canvas(container, bg="#10131c", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=self.canvas.yview
        )
        self.grid_frame = tk.Frame(self.canvas, bg="#10131c")
        self.grid_frame.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.grid_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.canvas_window, width=event.width
            ),
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda event: self.canvas.yview_scroll(
                int(-event.delta / 120), "units"
            ),
        )

    def _toggle_favorites(self):
        self.show_favorites = not self.show_favorites
        self.favorites_button.configure(
            text="★ Favorites" if self.show_favorites else "☆ Favorites"
        )
        self._render_games()

    def _render_games(self):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        query = self.search_var.get().strip().casefold()
        category = self.category_var.get()
        favorites = set(self.settings.get("favorites", []))
        filtered = [
            item for item in GAME_LIST
            if (category == "All games" or item[1] == category)
            and (not query or query in item[0].casefold()
                 or query in item[2].casefold())
            and (not self.show_favorites or item[0] in favorites)
        ]
        self.status.configure(text=f"{len(filtered)} games available")
        if not filtered:
            tk.Label(
                self.grid_frame, text="No games found.",
                bg="#10131c", fg="#929bb0", font=("Segoe UI", 14),
            ).pack(pady=40)
            return
        for index, item in enumerate(filtered):
            self._create_card(*item, *divmod(index, 2))

    def _create_card(self, name, category, description, game_class, row, column):
        card = tk.Frame(
            self.grid_frame, bg="#1a2030", padx=18, pady=16,
            highlightthickness=1, highlightbackground="#293249",
        )
        card.grid(
            row=row, column=column, sticky="nsew",
            padx=(0, 10) if column == 0 else (10, 0), pady=(0, 16),
        )
        self.grid_frame.grid_columnconfigure(column, weight=1)
        top = tk.Frame(card, bg="#1a2030")
        top.pack(fill="x")
        tk.Label(
            top, text=name, bg="#1a2030", fg="#f4f6fb",
            font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        favorite = name in self.settings.get("favorites", [])
        tk.Button(
            top, text="★" if favorite else "☆",
            command=lambda: self._toggle_game_favorite(name),
            bg="#1a2030", fg="#f5c96a", activebackground="#1a2030",
            activeforeground="#ffffff", relief="flat", font=("Segoe UI", 16),
        ).pack(side="right")
        tk.Label(
            card, text=category.upper(), bg="#1a2030", fg="#7e91bc",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(7, 4))
        tk.Label(
            card, text=description, bg="#1a2030", fg="#aeb7c9",
            font=("Segoe UI", 10), wraplength=390, justify="left",
        ).pack(anchor="w", pady=(0, 14))
        tk.Button(
            card, text="PLAY", command=lambda: self._launch(name, game_class),
            bg="#647fe8", fg="#ffffff", activebackground="#7892f5",
            activeforeground="#ffffff", relief="flat", padx=20, pady=8,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

    def _toggle_game_favorite(self, name):
        favorites = set(self.settings.get("favorites", []))
        favorites.symmetric_difference_update({name})
        self.settings["favorites"] = sorted(favorites)
        self._save_settings()
        self._render_games()

    def _launch(self, name, game_class):
        recent = self.settings.get("recent", [])
        self.settings["recent"] = [name] + [
            item for item in recent if item != name
        ][:9]
        self._save_settings()
        try:
            game_class(self)
        except (tk.TclError, ValueError) as error:
            messagebox.showerror("Could not launch game", str(error))
