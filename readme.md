# Sudoku Solver

Sudoku project with shared core logic and multiple interfaces:

- FastAPI backend in app.py
- Flask web app in webapp/app.py
- Tkinter desktop UI in tkinter_gui.py
- Shared solver and persistence in solver.py

## Features

- Backtracking Sudoku solve and random puzzle generation
- Difficulty presets from shared UI config
- Save/load game states as JSON under saves/
- Shared color metadata for UI clients

## Requirements

- Python 3.10+

Install dependencies for the FastAPI app:

```bash
pip install fastapi uvicorn sqlalchemy bcrypt python-multipart jinja2
```

Install dependencies for the Flask web app:

```bash
pip install -r webapp/requirements.txt
```

## Run FastAPI app

```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

The FastAPI root route renders the shared web template from webapp/templates.

## Run Flask web app

```bash
python webapp/app.py
```

Default Flask URL: http://127.0.0.1:5000

## Run Tkinter desktop app

```bash
python tkinter_gui.py
```

## Project layout

- app.py: FastAPI routes, auth, game state API
- webapp/app.py: Flask routes for web gameplay
- webapp/templates/index.html: web UI
- solver.py: solver/generator/save-load shared core
- ui_config.py: shared labels, colors, options
- models.py, schemas.py, crud.py: persistence and API models

## Notes

- POST /solve in FastAPI is intentionally public.
- Solve responses use a grid plus cell_colors payload for web clients.