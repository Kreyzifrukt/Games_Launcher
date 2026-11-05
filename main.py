"""Entry point for the Classic Arcade Launcher."""

from launcher import ArcadeLauncher


def main():
    """Start the desktop application."""
    app = ArcadeLauncher()
    app.mainloop()


if __name__ == "__main__":
    main()
