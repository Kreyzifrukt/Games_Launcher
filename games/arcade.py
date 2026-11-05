"""Real-time arcade games: Snake, Pong, Breakout, and Tetris."""

import random
import tkinter as tk

from .base import BG, GameWindow, TEXT


class Snake(GameWindow):
    """Classic snake controlled with the arrow keys."""

    def __init__(self, master):
        super().__init__(master, "Snake", "560x600")
        self.size = 20
        self.snake = [(8, 8), (7, 8), (6, 8)]
        self.direction = (1, 0)
        self.pending = self.direction
        self.food = self._food()
        self.score = 0
        self.running = True
        self.score_label = self.label(self.body, "Score: 0", 12)
        self.score_label.pack(pady=4)
        self.canvas = tk.Canvas(
            self.body, width=420, height=420, bg="#0b1220",
            highlightthickness=0,
        )
        self.canvas.pack(pady=8)
        self.window.bind("<Up>", lambda _e: self._turn((0, -1)))
        self.window.bind("<Down>", lambda _e: self._turn((0, 1)))
        self.window.bind("<Left>", lambda _e: self._turn((-1, 0)))
        self.window.bind("<Right>", lambda _e: self._turn((1, 0)))
        self._draw()
        self._tick()

    def _food(self):
        while True:
            point = (random.randrange(21), random.randrange(21))
            if point not in getattr(self, "snake", []):
                return point

    def _turn(self, direction):
        if direction != (-self.direction[0], -self.direction[1]):
            self.pending = direction

    def _draw(self):
        self.canvas.delete("all")
        for index, (x, y) in enumerate(self.snake):
            color = "#9be564" if index == 0 else "#55b76a"
            self.canvas.create_rectangle(
                x * 20 + 1, y * 20 + 1, x * 20 + 19, y * 20 + 19,
                fill=color, outline="",
            )
        x, y = self.food
        self.canvas.create_oval(
            x * 20 + 3, y * 20 + 3, x * 20 + 17, y * 20 + 17,
            fill="#f87171", outline="",
        )

    def _tick(self):
        if not self.running:
            return
        self.direction = self.pending
        head = (
            self.snake[0][0] + self.direction[0],
            self.snake[0][1] + self.direction[1],
        )
        growing = head == self.food
        body = self.snake if growing else self.snake[:-1]
        if not (0 <= head[0] < 21 and 0 <= head[1] < 21) or head in body:
            self.running = False
            self.label(self.body, f"Game over! Final score: {self.score}", 14).pack()
            return
        self.snake.insert(0, head)
        if growing:
            self.score += 10
            self.score_label.configure(text=f"Score: {self.score}")
            self.food = self._food()
        else:
            self.snake.pop()
        self._draw()
        self.schedule(105, self._tick)


class Pong(GameWindow):
    """Single-player Pong against a basic computer opponent."""

    def __init__(self, master):
        super().__init__(master, "Pong", "700x520")
        self.score = [0, 0]
        self.canvas = tk.Canvas(
            self.body, width=640, height=400, bg="#0b1220",
            highlightthickness=0,
        )
        self.canvas.pack(pady=8)
        self.info = self.label(self.body, "Move with W/S or ↑/↓", 11)
        self.info.pack()
        self.left_y = self.right_y = 200
        self.ball = [320, 200, 4, 3]
        self.window.bind("<w>", lambda _e: self._move(-24))
        self.window.bind("<s>", lambda _e: self._move(24))
        self.window.bind("<Up>", lambda _e: self._move(-24))
        self.window.bind("<Down>", lambda _e: self._move(24))
        self._tick()

    def _move(self, amount):
        self.left_y = max(45, min(355, self.left_y + amount))

    def _tick(self):
        self.canvas.delete("all")
        self.canvas.create_line(320, 0, 320, 400, fill="#344054", dash=(5, 6))
        self.canvas.create_rectangle(18, self.left_y - 45, 28, self.left_y + 45,
                                     fill="#7c93f5", outline="")
        self.canvas.create_rectangle(612, self.right_y - 45, 622, self.right_y + 45,
                                     fill="#f5c96a", outline="")
        x, y, dx, dy = self.ball
        self.right_y += max(-5, min(5, (y - self.right_y) * 0.08))
        if y <= 8 or y >= 392:
            dy *= -1
        if 18 <= x <= 30 and abs(y - self.left_y) < 52:
            dx = abs(dx) * 1.04
        if 610 <= x <= 622 and abs(y - self.right_y) < 52:
            dx = -abs(dx) * 1.04
        x += dx
        y += dy
        if x < 0 or x > 640:
            self.score[1 if x < 0 else 0] += 1
            self.info.configure(text=f"You {self.score[0]} : {self.score[1]} Computer")
            x, y, dx, dy = 320, 200, 4 * (1 if x < 0 else -1), 3
        self.ball = [x, y, dx, dy]
        self.canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill="#ffffff", outline="")
        self.canvas.create_text(320, 24, text=f"{self.score[0]}   :   {self.score[1]}",
                                fill="#ffffff", font=("Segoe UI", 18, "bold"))
        self.schedule(16, self._tick)


class Breakout(GameWindow):
    """Breakout with paddle movement controlled by the mouse."""

    def __init__(self, master):
        super().__init__(master, "Breakout", "620x600")
        self.canvas = tk.Canvas(
            self.body, width=560, height=480, bg="#0b1220",
            highlightthickness=0,
        )
        self.canvas.pack(pady=8)
        self.score = 0
        self.ball = [280, 400, 3, -4]
        self.paddle_x = 280
        self.bricks = {(row, col) for row in range(5) for col in range(10)}
        self.canvas.bind("<Motion>", self._mouse)
        self._tick()

    def _mouse(self, event):
        self.paddle_x = max(45, min(515, event.x))

    def _tick(self):
        self.canvas.delete("all")
        for row, col in self.bricks:
            x, y = 8 + col * 55, 25 + row * 23
            self.canvas.create_rectangle(x, y, x + 49, y + 17,
                                         fill=["#f87171", "#f5c96a", "#7c93f5"][row % 3],
                                         outline="")
        x, y, dx, dy = self.ball
        x += dx
        y += dy
        if x < 7 or x > 553:
            dx *= -1
        if y < 7:
            dy *= -1
        if 425 <= y <= 440 and abs(x - self.paddle_x) < 55 and dy > 0:
            dy = -abs(dy)
        hit = None
        for row, col in self.bricks:
            bx, by = 8 + col * 55, 25 + row * 23
            if bx <= x <= bx + 49 and by <= y <= by + 17:
                hit = (row, col)
                break
        if hit:
            self.bricks.remove(hit)
            self.score += 10
            dy *= -1
        if y > 480:
            self.label(self.body, f"Game over. Score: {self.score}", 13).pack()
            return
        if not self.bricks:
            self.label(self.body, f"You cleared the board! Score: {self.score}", 13).pack()
            return
        self.ball = [x, y, dx, dy]
        self.canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill="#ffffff", outline="")
        self.canvas.create_rectangle(
            self.paddle_x - 48, 445, self.paddle_x + 48, 456,
            fill="#7c93f5", outline="",
        )
        self.canvas.create_text(45, 465, text=f"Score: {self.score}",
                                fill="#ffffff", anchor="w")
        self.schedule(16, self._tick)


class Tetris(GameWindow):
    """Keyboard-controlled falling-block puzzle."""

    SHAPES = [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(0, 0), (0, 1), (1, 1), (2, 1)],
    ]
    COLORS = ["#f5c96a", "#7c93f5", "#55b76a", "#f87171", "#b78af5"]

    def __init__(self, master):
        super().__init__(master, "Tetris", "420x600")
        self.cell = 26
        self.board = [[None for _ in range(10)] for _ in range(20)]
        self.canvas = tk.Canvas(
            self.body, width=260, height=520, bg="#0b1220",
            highlightthickness=0,
        )
        self.canvas.pack(pady=5)
        self.score = 0
        self._new_piece()
        self.window.bind("<Left>", lambda _e: self._shift(-1))
        self.window.bind("<Right>", lambda _e: self._shift(1))
        self.window.bind("<Down>", lambda _e: self._drop())
        self.window.bind("<Up>", lambda _e: self._rotate())
        self._tick()

    def _new_piece(self):
        index = random.randrange(len(self.SHAPES))
        self.shape = list(self.SHAPES[index])
        self.color = self.COLORS[index]
        self.px, self.py = 3, 0
        if self._collides(self.px, self.py, self.shape):
            self.label(self.body, f"Game over. Score: {self.score}", 13).pack()

    def _collides(self, px, py, shape):
        for x, y in shape:
            nx, ny = px + x, py + y
            if nx < 0 or nx >= 10 or ny >= 20:
                return True
            if ny >= 0 and self.board[ny][nx]:
                return True
        return False

    def _shift(self, amount):
        if not self._collides(self.px + amount, self.py, self.shape):
            self.px += amount
            self._draw()

    def _rotate(self):
        rotated = [(3 - y, x) for x, y in self.shape]
        if not self._collides(self.px, self.py, rotated):
            self.shape = rotated
            self._draw()

    def _drop(self):
        if not self._collides(self.px, self.py + 1, self.shape):
            self.py += 1
        else:
            self._lock()
        self._draw()

    def _lock(self):
        for x, y in self.shape:
            if self.py + y >= 0:
                self.board[self.py + y][self.px + x] = self.color
        remaining = [row for row in self.board if any(cell is None for cell in row)]
        cleared = 20 - len(remaining)
        self.board = [[None] * 10 for _ in range(cleared)] + remaining
        self.score += cleared * 100
        self._new_piece()

    def _draw(self):
        self.canvas.delete("all")
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color:
                    self._cell(x, y, color)
        for x, y in self.shape:
            self._cell(self.px + x, self.py + y, self.color)

    def _cell(self, x, y, color):
        self.canvas.create_rectangle(
            x * self.cell + 1, y * self.cell + 1,
            (x + 1) * self.cell - 1, (y + 1) * self.cell - 1,
            fill=color, outline="",
        )

    def _tick(self):
        self._drop()
        self.schedule(500, self._tick)
