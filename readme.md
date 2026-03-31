# Sudoku Solver

Desktop Sudoku project with a Tkinter interface and a separate solver module.

## Features

- Backtracking Sudoku solve and random puzzle generation
- Difficulty presets from shared UI config
- Save/load game states as JSON under saves/
- Color metadata for the desktop UI

## Requirements

- Python 3.10+

## Run Tkinter desktop app

```bash
python tkinter_gui.py
```

## Project layout

- tkinter_gui.py: Tkinter desktop interface
- solver.py: solver, generator, and JSON save/load core
- ui_config.py: labels, colors, and options
- saves/: saved game states

## Notes

- Saved games are stored as JSON files in saves/.
- Solver logic remains separate from the Tkinter UI.