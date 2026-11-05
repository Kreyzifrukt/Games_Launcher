"""Puzzle games: Minesweeper, 2048, Memory, Lights Out, Sliding Puzzle, Maze."""

import random
import tkinter as tk

from .base import BG, GameWindow, TEXT


class Minesweeper(GameWindow):
    """Small 9 by 9 minesweeper board with recursive empty-cell reveal."""

    def __init__(self, master):
        super().__init__(master, "Minesweeper", "500x570")
        self.info = self.label(self.body, "Find all safe cells.", 11)
        self.info.pack(pady=5)
        self.grid = tk.Frame(self.body, bg=BG)
        self.grid.pack()
        self.button(self.body, "New board", self._reset).pack(pady=10)
        self._reset()

    def _reset(self):
        for child in self.grid.winfo_children():
            child.destroy()
        self.mines = set(random.sample(range(81), 10))
        self.revealed = set()
        self.flags = set()
        self.buttons = []
        self.finished = False
        for index in range(81):
            button = tk.Button(
                self.grid, text="", width=3, height=1,
                bg="#263248", fg=TEXT, relief="flat",
                command=lambda i=index: self._reveal(i),
            )
            button.grid(row=index // 9, column=index % 9, padx=1, pady=1)
            button.bind("<Button-3>", lambda event, i=index: self._flag(i))
            self.buttons.append(button)

    def _neighbors(self, index):
        row, col = divmod(index, 9)
        return [
            r * 9 + c for r in range(max(0, row - 1), min(9, row + 2))
            for c in range(max(0, col - 1), min(9, col + 2))
            if (r, c) != (row, col)
        ]

    def _flag(self, index):
        if self.finished or index in self.revealed:
            return
        if index in self.flags:
            self.flags.remove(index)
            self.buttons[index].configure(text="")
        else:
            self.flags.add(index)
            self.buttons[index].configure(text="⚑", fg="#f5c96a")

    def _reveal(self, index):
        if self.finished or index in self.revealed or index in self.flags:
            return
        if index in self.mines:
            self.buttons[index].configure(text="✹", bg="#991b1b")
            self.finished = True
            self.info.configure(text="Mine hit. Start a new board.")
            return
        self.revealed.add(index)
        count = sum(item in self.mines for item in self._neighbors(index))
        self.buttons[index].configure(
            text=str(count) if count else "", state="disabled",
            bg="#374151", disabledforeground="#93c5fd",
        )
        if count == 0:
            for neighbor in self._neighbors(index):
                self._reveal(neighbor)
        if len(self.revealed) == 81 - len(self.mines):
            self.finished = True
            self.info.configure(text="Board cleared. You win!")


class Game2048(GameWindow):
    """Keyboard-driven 2048 with merging and score tracking."""

    def __init__(self, master):
        super().__init__(master, "2048", "440x540")
        self.score = 0
        self.info = self.label(self.body, "Score: 0 | Use arrow keys", 11)
        self.info.pack(pady=6)
        self.buttons = []
        grid = tk.Frame(self.body, bg="#9b8b7a", padx=5, pady=5)
        grid.pack()
        for row in range(4):
            line = []
            for col in range(4):
                button = tk.Label(
                    grid, text="", width=5, height=2,
                    font=("Segoe UI", 18, "bold"), bg="#cdc1b4", fg="#3c342e",
                )
                button.grid(row=row, column=col, padx=3, pady=3)
                line.append(button)
            self.buttons.append(line)
        self.board = [[0] * 4 for _ in range(4)]
        self._spawn()
        self._spawn()
        self.window.bind("<Left>", lambda _e: self._move(0))
        self.window.bind("<Up>", lambda _e: self._move(1))
        self.window.bind("<Right>", lambda _e: self._move(2))
        self.window.bind("<Down>", lambda _e: self._move(3))
        self._draw()

    def _spawn(self):
        empty = [(r, c) for r in range(4) for c in range(4) if not self.board[r][c]]
        if empty:
            row, col = random.choice(empty)
            self.board[row][col] = 4 if random.random() < 0.1 else 2

    @staticmethod
    def _merge(line):
        values = [value for value in line if value]
        result = []
        score = 0
        index = 0
        while index < len(values):
            if index + 1 < len(values) and values[index] == values[index + 1]:
                value = values[index] * 2
                result.append(value)
                score += value
                index += 2
            else:
                result.append(values[index])
                index += 1
        return result + [0] * (4 - len(result)), score

    def _move(self, direction):
        old = [row[:] for row in self.board]
        total = 0
        for index in range(4):
            if direction in (0, 2):
                line = self.board[index][:]
            else:
                line = [self.board[row][index] for row in range(4)]
            if direction in (2, 3):
                line.reverse()
            line, score = self._merge(line)
            total += score
            if direction in (2, 3):
                line.reverse()
            for offset, value in enumerate(line):
                if direction in (0, 2):
                    self.board[index][offset] = value
                else:
                    self.board[offset][index] = value
        if old != self.board:
            self.score += total
            self._spawn()
            self._draw()

    def _draw(self):
        colors = {0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
                  16: "#f59563", 32: "#f67c5f", 64: "#f65e3b",
                  128: "#edcf72", 256: "#edcc61", 512: "#edc850",
                  1024: "#edc53f", 2048: "#edc22e"}
        for row in range(4):
            for col in range(4):
                value = self.board[row][col]
                self.buttons[row][col].configure(
                    text=str(value) if value else "",
                    bg=colors.get(value, "#3c3a32"),
                    fg="#3c342e" if value < 8 else "#ffffff",
                )
        self.info.configure(text=f"Score: {self.score} | Use arrow keys")


class Memory(GameWindow):
    """Match eight pairs of hidden symbols."""

    SYMBOLS = list("ABCDEFGH") * 2

    def __init__(self, master):
        super().__init__(master, "Memory", "460x500")
        self.cards = random.sample(self.SYMBOLS, len(self.SYMBOLS))
        self.opened = []
        self.matched = set()
        self.moves = 0
        self.info = self.label(self.body, "Moves: 0", 11)
        self.info.pack(pady=8)
        grid = tk.Frame(self.body, bg=BG)
        grid.pack()
        self.buttons = []
        for index in range(16):
            button = tk.Button(
                grid, text="?", width=5, height=2,
                font=("Segoe UI", 16, "bold"), bg="#263248", fg=TEXT,
                relief="flat", command=lambda i=index: self._flip(i),
            )
            button.grid(row=index // 4, column=index % 4, padx=4, pady=4)
            self.buttons.append(button)
        self.button(self.body, "Restart", self._restart).pack(pady=12)

    def _flip(self, index):
        if index in self.matched or index in self.opened or len(self.opened) == 2:
            return
        self.opened.append(index)
        self.buttons[index].configure(text=self.cards[index])
        if len(self.opened) == 2:
            self.moves += 1
            first, second = self.opened
            if self.cards[first] == self.cards[second]:
                self.matched.update(self.opened)
                self.opened.clear()
            else:
                self.schedule(700, self._hide_pair)
            self.info.configure(text=f"Moves: {self.moves} | Pairs: {len(self.matched)}/16")

    def _hide_pair(self):
        for index in self.opened:
            self.buttons[index].configure(text="?")
        self.opened.clear()

    def _restart(self):
        self.cards = random.sample(self.SYMBOLS, len(self.SYMBOLS))
        self.opened.clear()
        self.matched.clear()
        self.moves = 0
        self.info.configure(text="Moves: 0")
        for button in self.buttons:
            button.configure(text="?", state="normal")


class LightsOut(GameWindow):
    """Toggle a cell and its orthogonal neighbors to turn all lights off."""

    def __init__(self, master):
        super().__init__(master, "Lights Out", "430x500")
        self.info = self.label(self.body, "Turn every light off.", 11)
        self.info.pack(pady=8)
        grid = tk.Frame(self.body, bg=BG)
        grid.pack()
        self.buttons = []
        self.state = [[random.choice([0, 1]) for _ in range(5)] for _ in range(5)]
        for row in range(5):
            line = []
            for col in range(5):
                button = tk.Button(
                    grid, text="", width=5, height=2, relief="flat",
                    command=lambda r=row, c=col: self._toggle(r, c),
                )
                button.grid(row=row, column=col, padx=3, pady=3)
                line.append(button)
            self.buttons.append(line)
        self._draw()

    def _toggle(self, row, col):
        for r, c in ((row, col), (row - 1, col), (row + 1, col),
                     (row, col - 1), (row, col + 1)):
            if 0 <= r < 5 and 0 <= c < 5:
                self.state[r][c] ^= 1
        self._draw()
        if not any(any(line) for line in self.state):
            self.info.configure(text="All lights are off. You win!")

    def _draw(self):
        for row in range(5):
            for col in range(5):
                on = self.state[row][col]
                self.buttons[row][col].configure(
                    bg="#f5c96a" if on else "#263248",
                    activebackground="#ffe19a" if on else "#374151",
                )


class SlidingPuzzle(GameWindow):
    """Classic 15-puzzle with legal adjacent tile moves."""

    def __init__(self, master):
        super().__init__(master, "Sliding Puzzle", "430x500")
        self.info = self.label(self.body, "Arrange 1 to 15 in order.", 11)
        self.info.pack(pady=8)
        grid = tk.Frame(self.body, bg=BG)
        grid.pack()
        self.buttons = []
        self.tiles = list(range(1, 16)) + [0]
        for index in range(16):
            button = tk.Button(
                grid, text="", width=5, height=2, font=("Segoe UI", 16, "bold"),
                bg="#263248", fg=TEXT, relief="flat",
                command=lambda i=index: self._move(i),
            )
            button.grid(row=index // 4, column=index % 4, padx=4, pady=4)
            self.buttons.append(button)
        self.button(self.body, "Shuffle", self._shuffle).pack(pady=10)
        self._shuffle()

    def _shuffle(self):
        self.tiles = list(range(1, 16)) + [0]
        for _ in range(120):
            empty = self.tiles.index(0)
            choices = self._neighbors(empty)
            target = random.choice(choices)
            self.tiles[empty], self.tiles[target] = self.tiles[target], self.tiles[empty]
        self.info.configure(text="Arrange 1 to 15 in order.")
        self._draw()

    @staticmethod
    def _neighbors(index):
        row, col = divmod(index, 4)
        return [
            r * 4 + c for r, c in ((row - 1, col), (row + 1, col),
                                   (row, col - 1), (row, col + 1))
            if 0 <= r < 4 and 0 <= c < 4
        ]

    def _move(self, index):
        empty = self.tiles.index(0)
        if index not in self._neighbors(empty):
            return
        self.tiles[empty], self.tiles[index] = self.tiles[index], self.tiles[empty]
        self._draw()
        if self.tiles == list(range(1, 16)) + [0]:
            self.info.configure(text="Solved. Nice work!")

    def _draw(self):
        for index, value in enumerate(self.tiles):
            self.buttons[index].configure(
                text=str(value) if value else "",
                bg="#647fe8" if value else "#111827",
            )


class Maze(GameWindow):
    """Navigate a generated maze with arrow keys."""

    MAZE = [
        "###########",
        "#S#.......#",
        "#.#.#####.#",
        "#...#...#.#",
        "###.#.#.#.#",
        "#...#.#...#",
        "#.###.###.#",
        "#.....#...#",
        "#####.#.###",
        "#.........#",
        "#########E#",
    ]

    def __init__(self, master):
        super().__init__(master, "Maze", "470x510")
        self.player = [1, 1]
        self.info = self.label(self.body, "Reach the exit (E).", 11)
        self.info.pack(pady=6)
        self.canvas = tk.Canvas(
            self.body, width=330, height=330, bg="#0b1220", highlightthickness=0
        )
        self.canvas.pack()
        for key, delta in (("<Up>", (0, -1)), ("<Down>", (0, 1)),
                           ("<Left>", (-1, 0)), ("<Right>", (1, 0))):
            self.window.bind(key, lambda _e, d=delta: self._move(*d))
        self._draw()

    def _move(self, dx, dy):
        x, y = self.player
        nx, ny = x + dx, y + dy
        if self.MAZE[ny][nx] != "#":
            self.player = [nx, ny]
            self._draw()
            if self.MAZE[ny][nx] == "E":
                self.info.configure(text="You escaped the maze!")

    def _draw(self):
        self.canvas.delete("all")
        for row, line in enumerate(self.MAZE):
            for col, cell in enumerate(line):
                color = "#334155" if cell == "#" else "#0b1220"
                if cell == "E":
                    color = "#55b76a"
                x, y = col * 30, row * 30
                self.canvas.create_rectangle(x, y, x + 30, y + 30,
                                             fill=color, outline="#1f2937")
        x, y = self.player
        self.canvas.create_oval(
            x * 30 + 6, y * 30 + 6, x * 30 + 24, y * 30 + 24,
            fill="#f5c96a", outline="",
        )
