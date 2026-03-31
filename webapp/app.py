"""Flask web application for Sudoku solving and puzzle generation."""

from pathlib import Path
import sys

from flask import Flask, jsonify, request

# Allow importing the shared root-level solver module from this subfolder.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from solver import (  # noqa: E402
    GRID_SIZE,
    generate_puzzle,
    grid_to_json,
    load_saved_states,
    save_game,
    solve_sudoku,
)

app = Flask(__name__)

@app.route("/")
def index():
    """Simple health response for the API root."""
    return jsonify({"name": "sudoku-web-api", "status": "ok", "grid_size": GRID_SIZE})

@app.route("/generate")
def generate():
    """
    Generate a new puzzle with optional difficulty.
    Returns JSON containing the puzzle grid and cell colors.
    """
    difficulty = request.args.get("difficulty", "Easy")
    puzzle = generate_puzzle(difficulty=difficulty)
    return jsonify(grid_to_json(puzzle))

@app.route("/solve", methods=["POST"])
def solve():
    """
    Solve a Sudoku grid posted as JSON.
    Returns the solved grid and cell colors indicating solver-filled cells.
    """
    data = request.get_json()
    if not data or "grid" not in data:
        return jsonify({"error": "Invalid input"}), 400

    grid = data["grid"]
    # Copy to avoid modifying original
    solution_grid = [row[:] for row in grid]
    solved = solve_sudoku(solution_grid)
    if not solved:
        return jsonify({"error": "Puzzle is unsolvable"}), 400

    user_entered = [[grid[r][c] != 0 for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
    return jsonify(grid_to_json(solution_grid, user_entered))

@app.route("/save", methods=["POST"])
def save():
    """
    Save the current game state.
    Uses existing `save_game` from solver module.
    Returns success status and filename.
    """
    data = request.get_json()
    if not data or "grid" not in data:
        return jsonify({"error": "Invalid input"}), 400

    grid = data["grid"]
    user_entered = data.get("user_entered", [[False]*GRID_SIZE for _ in range(GRID_SIZE)])
    solved_flag = all(cell != 0 for row in grid for cell in row)

    save_path = save_game(grid, user_entered, solved_flag)
    return jsonify({"status": "saved", "path": save_path})

@app.route("/load", methods=["GET"])
def load():
    """
    Load the most recent saved state.
    Returns JSON with grid, cell colors and timestamp.
    """
    states = load_saved_states()
    if not states:
        return jsonify({"error": "No saved games"}), 404

    latest_state = states[0]
    # Build color array based on stored cell_colors
    cell_colors = latest_state["cell_colors"]
    return jsonify({
        "grid": latest_state["grid"],
        "cell_colors": cell_colors,
        "timestamp": latest_state["timestamp"],
        "solved": latest_state["solved"]
    })

if __name__ == "__main__":
    app.run(debug=True)