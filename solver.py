"""Shared Sudoku core logic used by both desktop and web apps."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import random
from pathlib import Path
from typing import List

from ui_config import DIFFICULTY_PRESETS, THEME_COLORS

GRID_SIZE = 9
BOX_SIZE = 3

# Shared color palette used by Tkinter and web responses.
USER_COLOR = THEME_COLORS["user_cell"]
SOLVED_COLOR = THEME_COLORS["solved_cell"]

SAVE_DIR = Path("saves")

Grid = List[List[int]]
BoolGrid = List[List[bool]]


def empty_grid() -> Grid:
    """Create a 9x9 grid initialized with zeros."""
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def validate_grid_shape(grid: Grid) -> None:
    """Ensure the grid is a 9x9 matrix of integers in range 0..9."""
    if len(grid) != GRID_SIZE:
        raise ValueError("Grid must contain 9 rows")

    for row in grid:
        if len(row) != GRID_SIZE:
            raise ValueError("Each row must contain 9 columns")
        for value in row:
            if not isinstance(value, int) or not 0 <= value <= GRID_SIZE:
                raise ValueError("Grid values must be integers between 0 and 9")


def normalize_user_entered(grid: Grid, user_entered: BoolGrid | None = None) -> BoolGrid:
    """Return a normalized boolean map for user-entered cells."""
    if user_entered is None:
        return [[cell != 0 for cell in row] for row in grid]

    if len(user_entered) != GRID_SIZE or any(len(row) != GRID_SIZE for row in user_entered):
        raise ValueError("user_entered must be a 9x9 boolean matrix")

    return [[bool(cell) for cell in row] for row in user_entered]


def is_valid(grid: Grid, row: int, col: int, num: int) -> bool:
    """Check if `num` can be placed at (row, col)."""
    if any(grid[row][j] == num for j in range(GRID_SIZE)):
        return False
    if any(grid[i][col] == num for i in range(GRID_SIZE)):
        return False

    start_row = (row // BOX_SIZE) * BOX_SIZE
    start_col = (col // BOX_SIZE) * BOX_SIZE
    for i in range(start_row, start_row + BOX_SIZE):
        for j in range(start_col, start_col + BOX_SIZE):
            if grid[i][j] == num:
                return False

    return True


def find_empty(grid: Grid) -> tuple[int, int]:
    """Find the next empty cell; return (-1, -1) if solved."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                return r, c
    return -1, -1


def _solve_backtracking(grid: Grid) -> bool:
    row, col = find_empty(grid)
    if row == -1:
        return True

    for num in range(1, GRID_SIZE + 1):
        if is_valid(grid, row, col, num):
            grid[row][col] = num
            if _solve_backtracking(grid):
                return True
            grid[row][col] = 0

    return False


def solve(grid: Grid) -> Grid:
    """Solve in place and return the solved grid, raising on failure."""
    validate_grid_shape(grid)
    if not _solve_backtracking(grid):
        raise ValueError("No solution found for the provided Sudoku grid")
    return grid


def solve_sudoku(grid: Grid) -> bool:
    """Compatibility wrapper used by the Flask app."""
    validate_grid_shape(grid)
    return _solve_backtracking(grid)


def _fill_grid_random(grid: Grid) -> bool:
    """Fill a grid randomly with a full valid solution."""
    row, col = find_empty(grid)
    if row == -1:
        return True

    candidates = list(range(1, GRID_SIZE + 1))
    random.shuffle(candidates)

    for num in candidates:
        if is_valid(grid, row, col, num):
            grid[row][col] = num
            if _fill_grid_random(grid):
                return True
            grid[row][col] = 0

    return False


def generate_full_solution() -> Grid:
    """Generate a complete valid Sudoku board."""
    grid = empty_grid()
    _fill_grid_random(grid)
    return grid


def generate_puzzle(difficulty: str = "Easy") -> Grid:
    """Generate a Sudoku puzzle by removing numbers from a solved board."""
    lookup = {name.lower(): clues for name, clues in DIFFICULTY_PRESETS.items()}
    clues = lookup.get(difficulty.lower(), DIFFICULTY_PRESETS["Easy"])
    puzzle = [row[:] for row in generate_full_solution()]

    cells_to_clear = GRID_SIZE * GRID_SIZE - clues
    positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    random.shuffle(positions)

    for idx in range(cells_to_clear):
        r, c = positions[idx]
        puzzle[r][c] = 0

    return puzzle


def cell_colors_for_grid(grid: Grid, user_entered: BoolGrid | None = None) -> List[List[str]]:
    """Build per-cell colors for UI clients."""
    users = normalize_user_entered(grid, user_entered)
    colors: List[List[str]] = []

    for y in range(GRID_SIZE):
        row_colors: List[str] = []
        for x in range(GRID_SIZE):
            value = grid[y][x]
            if value == 0:
                row_colors.append("")
            elif users[y][x]:
                row_colors.append(USER_COLOR)
            else:
                row_colors.append(SOLVED_COLOR)
        colors.append(row_colors)

    return colors


def grid_to_json(grid: Grid, user_entered: BoolGrid | None = None) -> dict:
    """Serialize a grid and color metadata for API/UI use."""
    validate_grid_shape(grid)
    return {
        "grid": [row[:] for row in grid],
        "cell_colors": cell_colors_for_grid(grid, user_entered),
    }


def save_game(
    grid: Grid,
    user_entered: BoolGrid | None = None,
    solved: bool | None = None,
    save_dir: Path = SAVE_DIR,
) -> str:
    """Save game state as JSON and return the created filepath."""
    validate_grid_shape(grid)
    users = normalize_user_entered(grid, user_entered)

    save_dir.mkdir(parents=True, exist_ok=True)
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.isoformat(timespec="seconds").replace("+00:00", "Z")
    filename = save_dir / f"save_{int(now_utc.timestamp())}.json"

    payload = {
        "grid": [row[:] for row in grid],
        "user_entered": users,
        "cell_colors": cell_colors_for_grid(grid, users),
        "timestamp": timestamp,
        "solved": bool(solved) if solved is not None else all(cell != 0 for row in grid for cell in row),
    }

    with filename.open("w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)

    return str(filename)


def load_saved_states(save_dir: Path = SAVE_DIR) -> List[dict]:
    """Load all saved states sorted by newest first."""
    if not save_dir.exists():
        return []

    states: List[dict] = []
    for json_file in save_dir.glob("save_*.json"):
        try:
            with json_file.open("r", encoding="utf-8") as file_obj:
                state = json.load(file_obj)
            state.setdefault(
                "timestamp",
                datetime.fromtimestamp(json_file.stat().st_mtime, tz=timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
            )
            states.append(state)
        except (json.JSONDecodeError, OSError):
            continue

    states.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return states
