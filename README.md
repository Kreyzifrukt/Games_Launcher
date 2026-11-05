# Classic Arcade Launcher

A desktop launcher for 20 classic mini-games, built with Python and Tkinter.

## Requirements

- Python 3.10 or newer
- Tkinter (included with most standard Python installations)

No third-party Python packages are required.

## Run

```bash
python main.py
```

## Games

| Category | Games |
| --- | --- |
| Arcade | Snake, Pong, Breakout, Tetris |
| Puzzle | Minesweeper, 2048, Memory, Lights Out, Sliding Puzzle, Maze |
| Board | Tic-Tac-Toe, Connect Four, Reversi, Blackjack |
| Quick | Guess the Number, Rock Paper Scissors, Hangman, Simon, Reaction Test, Typing Test |

## Controls

- **Snake:** arrow keys
- **Pong:** W/S or arrow keys
- **Breakout:** move the mouse over the paddle
- **Tetris:** arrow keys (up rotates, down drops)
- **2048:** arrow keys
- **Maze:** arrow keys
- **Other games:** use the on-screen controls

## Features

- Searchable catalog and category filters
- Favorites
- Dark desktop interface
- Separate windows for each game
- Local settings stored in `~/.classic_arcade_launcher/settings.json`

## Project layout

- `main.py` — application entry point
- `launcher.py` — catalog, search, filters, and preferences
- `games/base.py` — shared game-window and timer helpers
- `games/arcade.py` — real-time arcade games
- `games/board.py` — board and card games
- `games/puzzles.py` — puzzle games
- `games/quick.py` — quick-play games
