"""Shared UI configuration for Tkinter and web clients."""

from __future__ import annotations

from typing import Any

THEME_COLORS = {
    "app_bg": "#f6f4ef",
    "panel_bg": "#fbfaf8",
    "grid_line": "#2b2a28",
    "button_bg": "#1f2937",
    "button_fg": "#f9fafb",
    "entry_bg": "#ffffff",
    "text_primary": "#111827",
    "text_muted": "#374151",
    "border": "#d6d3cd",
    "user_cell": "#ffa500",
    "solved_cell": "#32cd32",
}

DIFFICULTY_PRESETS = {
    "Easy": 40,
    "Medium": 32,
    "Hard": 26,
}

LABELS = {
    "app_title": "Sudoku Studio",
    "subtitle": "One solver core for desktop and web.",
    "difficulty": "Difficulty:",
    "default_status": "Enter values or generate a puzzle.",
    "invalid_input": "Only digits 1-9 are allowed in a cell.",
    "generated_status": "Generated {difficulty} puzzle.",
    "solved_status": "Solved successfully.",
    "unsolved_status": "Puzzle appears unsolvable. Check your inputs.",
    "unsolved_title": "Unsolvable",
    "unsolved_message": "This puzzle cannot be solved.",
    "cleared_status": "Grid cleared.",
    "saved_status": "Saved game to {path}.",
    "loaded_status": "Loaded latest save from {timestamp}.",
    "no_saves_title": "No saves",
    "no_saves_message": "No saved puzzles found.",
    "invalid_save_title": "Invalid save",
    "invalid_save_message": "Latest save file has invalid grid data.",
    "wrap_navigation": "Wrap navigation",
}

BUTTON_LABELS = {
    "generate": "Generate",
    "solve": "Solve",
    "clear": "Clear",
    "save": "Save",
    "load_latest": "Load Latest",
}

UI_OPTIONS = {
    "wrap_navigation_default": False,
}


def difficulty_options() -> tuple[str, ...]:
    """Return the shared ordered list of supported difficulty levels."""
    return tuple(DIFFICULTY_PRESETS.keys())


def get_ui_config() -> dict[str, Any]:
    """Return JSON-serializable UI config payload for clients."""
    return {
        "theme": THEME_COLORS,
        "labels": LABELS,
        "buttons": BUTTON_LABELS,
        "difficulty_options": list(difficulty_options()),
        "difficulty_presets": DIFFICULTY_PRESETS,
        "options": UI_OPTIONS,
    }
