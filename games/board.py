"""Board and card games."""

import random
import tkinter as tk

from .base import BG, GameWindow, TEXT


class TicTacToe(GameWindow):
    """Noughts and crosses against a computer opponent."""

    def __init__(self, master):
        super().__init__(master, "Tic-Tac-Toe", "420x500")
        self.board = [""] * 9
        self.buttons = []
        self.info = self.label(self.body, "Your turn: X").pack(pady=8)
        grid = tk.Frame(self.body, bg=BG)
        grid.pack()
        for index in range(9):
            button = tk.Button(
                grid, text="", width=5, height=2, font=("Segoe UI", 22, "bold"),
                bg="#263248", fg=TEXT, relief="flat",
                command=lambda i=index: self._play(i),
            )
            button.grid(row=index // 3, column=index % 3, padx=4, pady=4)
            self.buttons.append(button)
        self.info = grid.master.winfo_children()[0]
        self.button(self.body, "New game", self._reset).pack(pady=12)

    def _winner(self):
        lines = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                 (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for a, b, c in lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return "Draw" if all(self.board) else None

    def _mark(self, index, mark):
        self.board[index] = mark
        self.buttons[index].configure(text=mark, state="disabled")

    def _play(self, index):
        if self.board[index] or self._winner():
            return
        self._mark(index, "X")
        if not self._winner():
            choices = [i for i, value in enumerate(self.board) if not value]
            if choices:
                self._mark(random.choice(choices), "O")
        result = self._winner()
        self.info.configure(text=f"{result} wins!" if result in ("X", "O")
                            else "It's a draw." if result else "Your turn: X")

    def _reset(self):
        self.board = [""] * 9
        for button in self.buttons:
            button.configure(text="", state="normal")
        self.info.configure(text="Your turn: X")


class ConnectFour(GameWindow):
    """Connect four discs on a six-row board."""

    def __init__(self, master):
        super().__init__(master, "Connect Four", "560x590")
        self.board = [[0] * 7 for _ in range(6)]
        self.turn = 1
        self.finished = False
        self.info = self.label(self.body, "Your discs are red.", 12)
        self.info.pack(pady=6)
        controls = tk.Frame(self.body, bg=BG)
        controls.pack()
        for col in range(7):
            self.button(controls, str(col + 1), lambda c=col: self._drop(c)).pack(
                side="left", padx=2
            )
        self.canvas = tk.Canvas(
            self.body, width=406, height=348, bg="#1d4ed8", highlightthickness=0
        )
        self.canvas.pack(pady=8)
        self._draw()

    def _drop(self, col):
        if self.finished:
            return
        row = next((r for r in range(5, -1, -1) if not self.board[r][col]), None)
        if row is None:
            return
        self.board[row][col] = self.turn
        self._draw()
        if self._won(row, col):
            self.finished = True
            self.info.configure(text="You win!" if self.turn == 1 else "Computer wins!")
        elif all(self.board[0]):
            self.finished = True
            self.info.configure(text="Draw.")
        else:
            self.turn = 3 - self.turn
            if self.turn == 2:
                self.schedule(300, self._computer_move)
            else:
                self.info.configure(text="Your turn.")

    def _computer_move(self):
        choices = [c for c in range(7) if not self.board[0][c]]
        if choices and not self.finished:
            self._drop(random.choice(choices))

    def _won(self, row, col):
        player = self.board[row][col]
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            count = 1
            for sign in (-1, 1):
                r, c = row + dr * sign, col + dc * sign
                while 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == player:
                    count += 1
                    r += dr * sign
                    c += dc * sign
            if count >= 4:
                return True
        return False

    def _draw(self):
        self.canvas.delete("all")
        for row in range(6):
            for col in range(7):
                value = self.board[row][col]
                color = "#ef4444" if value == 1 else "#facc15" if value == 2 else "#dbeafe"
                x, y = col * 58 + 5, row * 58 + 5
                self.canvas.create_oval(x, y, x + 48, y + 48, fill=color, outline="")


class Reversi(GameWindow):
    """Reversi with legal captures and a simple greedy opponent."""

    DIRECTIONS = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                  (0, 1), (1, -1), (1, 0), (1, 1))

    def __init__(self, master):
        super().__init__(master, "Reversi", "560x600")
        self.board = [[0] * 8 for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 2
        self.board[3][4] = self.board[4][3] = 1
        self.turn = 1
        self.info = self.label(self.body, "Your turn: black")
        self.info.pack(pady=6)
        self.canvas = tk.Canvas(
            self.body, width=440, height=440, bg="#16804a", highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._click)
        self._draw()

    def _flips(self, row, col, player):
        if self.board[row][col]:
            return []
        opponent = 3 - player
        flips = []
        for dr, dc in self.DIRECTIONS:
            line = []
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                line.append((r, c))
                r += dr
                c += dc
            if line and 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                flips.extend(line)
        return flips

    def _apply(self, row, col, player, flips):
        self.board[row][col] = player
        for r, c in flips:
            self.board[r][c] = player

    def _click(self, event):
        row, col = event.y // 55, event.x // 55
        if not (0 <= row < 8 and 0 <= col < 8) or self.turn != 1:
            return
        flips = self._flips(row, col, 1)
        if not flips:
            return
        self._apply(row, col, 1, flips)
        self.turn = 2
        self._computer_move()

    def _computer_move(self):
        moves = [(r, c, self._flips(r, c, 2))
                 for r in range(8) for c in range(8) if self._flips(r, c, 2)]
        if moves:
            row, col, flips = max(moves, key=lambda move: len(move[2]))
            self._apply(row, col, 2, flips)
        self.turn = 1
        self._draw()
        black = sum(cell == 1 for line in self.board for cell in line)
        white = sum(cell == 2 for line in self.board for cell in line)
        self.info.configure(text=f"Black {black} : {white} White | Your turn")

    def _draw(self):
        self.canvas.delete("all")
        for i in range(9):
            self.canvas.create_line(i * 55, 0, i * 55, 440, fill="#0b5d35")
            self.canvas.create_line(0, i * 55, 440, i * 55, fill="#0b5d35")
        for row in range(8):
            for col in range(8):
                value = self.board[row][col]
                if value:
                    color = "#111827" if value == 1 else "#f9fafb"
                    x, y = col * 55 + 7, row * 55 + 7
                    self.canvas.create_oval(x, y, x + 41, y + 41, fill=color, outline="")


class Blackjack(GameWindow):
    """Single-player blackjack with hit, stand, and new-hand controls."""

    def __init__(self, master):
        super().__init__(master, "Blackjack", "520x460")
        self.info = self.label(self.body, "Choose Hit or Stand.", 12)
        self.info.pack(pady=8)
        self.table = self.label(self.body, "", 14, justify="left")
        self.table.pack(pady=16)
        controls = tk.Frame(self.body, bg=BG)
        controls.pack()
        self.button(controls, "Hit", self._hit).pack(side="left", padx=4)
        self.button(controls, "Stand", self._stand).pack(side="left", padx=4)
        self.button(controls, "New hand", self._new_hand).pack(side="left", padx=4)
        self._new_hand()

    def _draw_card(self):
        return random.randint(2, 14)

    @staticmethod
    def _score(hand):
        total = sum(min(card, 10) for card in hand)
        aces = hand.count(14)
        while aces and total + 10 <= 21:
            total += 10
            aces -= 1
        return total

    @staticmethod
    def _name(card):
        return {11: "J", 12: "Q", 13: "K", 14: "A"}.get(card, str(card))

    def _new_hand(self):
        self.player = [self._draw_card(), self._draw_card()]
        self.dealer = [self._draw_card(), self._draw_card()]
        self.active = True
        self.info.configure(text="Choose Hit or Stand.")
        self._render()

    def _render(self, reveal=False):
        dealer = self.dealer if reveal else self.dealer[:1]
        dealer_text = " ".join(self._name(card) for card in dealer)
        player_text = " ".join(self._name(card) for card in self.player)
        self.table.configure(
            text=f"Dealer: {dealer_text}{'' if reveal else '  ?'}"
                 f"\nYou: {player_text} ({self._score(self.player)})"
        )

    def _hit(self):
        if not self.active:
            return
        self.player.append(self._draw_card())
        score = self._score(self.player)
        if score > 21:
            self.active = False
            self.info.configure(text="Bust. Dealer wins.")
            self._render(True)
        else:
            self._render()

    def _stand(self):
        if not self.active:
            return
        while self._score(self.dealer) < 17:
            self.dealer.append(self._draw_card())
        player, dealer = self._score(self.player), self._score(self.dealer)
        result = "You win!" if dealer > 21 or player > dealer else (
            "Draw." if player == dealer else "Dealer wins."
        )
        self.active = False
        self.info.configure(text=result)
        self._render(True)
