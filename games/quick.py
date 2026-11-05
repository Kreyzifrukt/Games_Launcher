"""Quick-play games and reflex challenges."""

import random
import time
import tkinter as tk

from .base import BG, GameWindow, TEXT


class GuessNumber(GameWindow):
    """Guess a random number between one and one hundred."""

    def __init__(self, master):
        super().__init__(master, "Guess the Number", "440x420")
        self.secret = random.randint(1, 100)
        self.attempts = 0
        self.info = self.label(self.body, "I'm thinking of a number from 1 to 100.")
        self.info.pack(pady=12)
        self.entry = tk.Entry(
            self.body, font=("Segoe UI", 16), justify="center",
            bg="#263248", fg=TEXT, insertbackground=TEXT, relief="flat",
        )
        self.entry.pack(pady=8, ipady=7)
        self.entry.bind("<Return>", lambda _event: self._guess())
        self.button(self.body, "Guess", self._guess).pack(pady=6)
        self.button(self.body, "New number", self._reset).pack(pady=6)

    def _guess(self):
        try:
            value = int(self.entry.get())
        except ValueError:
            self.info.configure(text="Enter a whole number.")
            return
        if not 1 <= value <= 100:
            self.info.configure(text="Choose a number from 1 to 100.")
            return
        self.attempts += 1
        if value == self.secret:
            self.info.configure(text=f"Correct! You needed {self.attempts} guesses.")
        elif value < self.secret:
            self.info.configure(text="Too low. Try a higher number.")
        else:
            self.info.configure(text="Too high. Try a lower number.")

    def _reset(self):
        self.secret = random.randint(1, 100)
        self.attempts = 0
        self.entry.delete(0, "end")
        self.info.configure(text="New number selected. Good luck.")


class RockPaperScissors(GameWindow):
    """Rock, paper, scissors against the computer."""

    def __init__(self, master):
        super().__init__(master, "Rock Paper Scissors", "460x420")
        self.score = [0, 0]
        self.result = self.label(self.body, "Choose your move.", 14)
        self.result.pack(pady=18)
        self.score_label = self.label(self.body, "You 0 : 0 Computer", 11)
        self.score_label.pack(pady=8)
        controls = tk.Frame(self.body, bg=BG)
        controls.pack(pady=12)
        for move in ("Rock", "Paper", "Scissors"):
            self.button(
                controls, move, lambda choice=move: self._play(choice)
            ).pack(side="left", padx=5)

    def _play(self, choice):
        computer = random.choice(("Rock", "Paper", "Scissors"))
        if choice == computer:
            message = f"Draw. Both chose {choice}."
        elif (choice, computer) in (
            ("Rock", "Scissors"), ("Paper", "Rock"), ("Scissors", "Paper")
        ):
            self.score[0] += 1
            message = f"You win. {choice} beats {computer}."
        else:
            self.score[1] += 1
            message = f"Computer wins. {computer} beats {choice}."
        self.result.configure(text=message)
        self.score_label.configure(
            text=f"You {self.score[0]} : {self.score[1]} Computer"
        )


class Hangman(GameWindow):
    """Guess a hidden word with a limited number of mistakes."""

    WORDS = ("PYTHON", "ARCADE", "KEYBOARD", "PUZZLE", "COMPUTER",
             "PIXEL", "GALAXY", "ROCKET", "CASTLE", "DRAGON")

    def __init__(self, master):
        super().__init__(master, "Hangman", "480x460")
        self.info = self.label(self.body, "", 14)
        self.info.pack(pady=10)
        self.word_label = self.label(self.body, "", 20)
        self.word_label.pack(pady=12)
        self.entry = tk.Entry(
            self.body, width=5, font=("Segoe UI", 16), justify="center",
            bg="#263248", fg=TEXT, insertbackground=TEXT, relief="flat",
        )
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", lambda _event: self._guess())
        self.button(self.body, "Guess letter", self._guess).pack(pady=6)
        self.button(self.body, "New word", self._reset).pack(pady=6)
        self._reset()

    def _reset(self):
        self.word = random.choice(self.WORDS)
        self.guessed = set()
        self.mistakes = 0
        self.active = True
        self.entry.delete(0, "end")
        self._render()

    def _guess(self):
        if not self.active:
            return
        letter = self.entry.get().strip().upper()[:1]
        self.entry.delete(0, "end")
        if not letter.isalpha() or letter in self.guessed:
            return
        self.guessed.add(letter)
        if letter not in self.word:
            self.mistakes += 1
        if all(char in self.guessed for char in self.word):
            self.active = False
            self.info.configure(text="You guessed the word!")
        elif self.mistakes >= 6:
            self.active = False
            self.info.configure(text=f"Out of guesses. The word was {self.word}.")
        self._render()

    def _render(self):
        self.word_label.configure(
            text=" ".join(char if char in self.guessed else "_" for char in self.word)
        )
        if self.active:
            self.info.configure(
                text=f"Mistakes: {self.mistakes}/6 | Used: {', '.join(sorted(self.guessed))}"
            )


class Simon(GameWindow):
    """Repeat a growing sequence of four colored lights."""

    COLORS = ("#ef4444", "#22c55e", "#3b82f6", "#eab308")

    def __init__(self, master):
        super().__init__(master, "Simon", "440x500")
        self.sequence = []
        self.position = 0
        self.active = False
        self.info = self.label(self.body, "Press Start and repeat the sequence.", 11)
        self.info.pack(pady=8)
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(pady=12)
        self.pads = []
        for index, color in enumerate(self.COLORS):
            pad = tk.Button(
                grid, text="", width=9, height=4, bg=color,
                activebackground=color, relief="flat",
                command=lambda i=index: self._input(i),
            )
            pad.grid(row=index // 2, column=index % 2, padx=8, pady=8)
            self.pads.append(pad)
        self.button(self.body, "Start / Restart", self._start).pack(pady=8)

    def _start(self):
        self.sequence = []
        self._next_round()

    def _next_round(self):
        self.sequence.append(random.randrange(4))
        self.position = 0
        self.active = False
        self.info.configure(text=f"Watch the sequence. Round {len(self.sequence)}")
        self._show_step(0)

    def _show_step(self, index):
        if index >= len(self.sequence):
            self.active = True
            self.info.configure(text="Your turn. Repeat the sequence.")
            return
        color_index = self.sequence[index]
        self.pads[color_index].configure(relief="sunken")
        self.schedule(350, lambda: self.pads[color_index].configure(relief="raised"))
        self.schedule(550, lambda: self._show_step(index + 1))

    def _input(self, index):
        if not self.active:
            return
        if self.sequence[self.position] != index:
            self.active = False
            self.info.configure(text=f"Wrong sequence. You reached round {len(self.sequence)}.")
            return
        self.position += 1
        if self.position == len(self.sequence):
            self.active = False
            self.schedule(650, self._next_round)


class ReactionTest(GameWindow):
    """Measure the delay between a green signal and a click."""

    def __init__(self, master):
        super().__init__(master, "Reaction Test", "500x420")
        self.state = "idle"
        self.started = 0.0
        self.best = None
        self.target = tk.Button(
            self.body, text="Click to start", width=25, height=6,
            bg="#263248", fg=TEXT, activebackground="#374151",
            relief="flat", font=("Segoe UI", 15, "bold"),
            command=self._click,
        )
        self.target.pack(expand=True, fill="both", padx=25, pady=20)
        self.info = self.label(self.body, "Wait for green, then click.", 11)
        self.info.pack(pady=8)

    def _click(self):
        if self.state == "idle":
            self.state = "waiting"
            self.target.configure(text="Wait...", bg="#b45309")
            self.delay = random.randint(1500, 4500)
            self.schedule(self.delay, self._ready)
        elif self.state == "waiting":
            self.state = "idle"
            self.target.configure(text="Too early! Click to try again.", bg="#263248")
        elif self.state == "ready":
            elapsed = (time.perf_counter() - self.started) * 1000
            self.best = elapsed if self.best is None else min(self.best, elapsed)
            self.state = "idle"
            self.target.configure(text=f"{elapsed:.0f} ms\nClick to retry", bg="#263248")
            self.info.configure(text=f"Best: {self.best:.0f} ms")

    def _ready(self):
        if self.state == "waiting":
            self.state = "ready"
            self.started = time.perf_counter()
            self.target.configure(text="CLICK NOW!", bg="#15803d")


class TypingTest(GameWindow):
    """One-minute typing test with live accuracy and words-per-minute."""

    TEXTS = (
        "Practice makes progress when you stay curious and keep building.",
        "Small steps every day can lead to surprisingly big results.",
        "Classic games are simple to learn and difficult to master.",
    )

    def __init__(self, master):
        super().__init__(master, "Typing Test", "650x480")
        self.sample = random.choice(self.TEXTS)
        self.started = None
        self.info = self.label(self.body, "Type the sentence below. Timer starts on first key.", 11)
        self.info.pack(pady=8)
        self.sample_label = self.label(
            self.body, self.sample, 14, justify="left", wraplength=560
        )
        self.sample_label.pack(pady=15)
        self.entry = tk.Text(
            self.body, height=5, wrap="word", bg="#263248", fg=TEXT,
            insertbackground=TEXT, relief="flat", font=("Segoe UI", 12),
        )
        self.entry.pack(fill="x", pady=8)
        self.entry.bind("<KeyRelease>", self._update)
        self.stats = self.label(self.body, "WPM: 0 | Accuracy: 100%", 12)
        self.stats.pack(pady=8)
        self.button(self.body, "New test", self._reset).pack(pady=8)

    def _update(self, _event=None):
        if self.started is None:
            self.started = time.perf_counter()
        typed = self.entry.get("1.0", "end-1c")
        elapsed = max((time.perf_counter() - self.started) / 60, 1 / 60)
        correct = sum(
            index < len(self.sample) and char == self.sample[index]
            for index, char in enumerate(typed)
        )
        accuracy = 100 * correct / max(len(typed), 1)
        wpm = len(typed.split()) / elapsed
        self.stats.configure(text=f"WPM: {wpm:.0f} | Accuracy: {accuracy:.0f}%")
        if typed == self.sample:
            self.stats.configure(text=f"Completed! WPM: {wpm:.0f} | Accuracy: 100%")

    def _reset(self):
        self.sample = random.choice(self.TEXTS)
        self.started = None
        self.sample_label.configure(text=self.sample)
        self.entry.delete("1.0", "end")
        self.stats.configure(text="WPM: 0 | Accuracy: 100%")
