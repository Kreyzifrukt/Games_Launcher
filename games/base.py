"""Shared window, layout, and timer helpers for mini-games."""

import tkinter as tk

BG = "#111827"
PANEL = "#1f2937"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
ACCENT = "#7c93f5"


class GameWindow:
    """Base class that gives each game a consistent standalone window."""

    def __init__(self, master, title, size="720x560"):
        self.window = tk.Toplevel(master)
        self.window.title(f"{title} | Classic Arcade")
        self.window.geometry(size)
        self.window.minsize(420, 360)
        self.window.configure(bg=BG)
        self._after_ids = []
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 10))
        tk.Label(
            header, text=title, bg=BG, fg=TEXT,
            font=("Segoe UI", 19, "bold"),
        ).pack(side="left")
        tk.Button(
            header, text="Close", command=self.close,
            bg=PANEL, fg=TEXT, activebackground="#374151",
            activeforeground=TEXT, relief="flat", padx=12, pady=5,
        ).pack(side="right")
        self.body = tk.Frame(self.window, bg=BG)
        self.body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def schedule(self, delay, callback):
        """Schedule a callback and track it so it can be cancelled safely."""
        after_id = self.window.after(delay, callback)
        self._after_ids.append(after_id)
        return after_id

    def close(self):
        """Cancel pending callbacks and close the game window."""
        for after_id in self._after_ids:
            try:
                self.window.after_cancel(after_id)
            except tk.TclError:
                pass
        self._after_ids.clear()
        self.window.destroy()

    def label(self, parent, text, size=12, color=TEXT, **kwargs):
        return tk.Label(
            parent, text=text, bg=kwargs.pop("bg", BG), fg=color,
            font=("Segoe UI", size), **kwargs,
        )

    def button(self, parent, text, command, **kwargs):
        return tk.Button(
            parent, text=text, command=command, bg=ACCENT, fg="#ffffff",
            activebackground="#91a4ff", activeforeground="#ffffff",
            relief="flat", padx=12, pady=7, **kwargs,
        )
