"""
Flask web application for Sudoku solving and puzzle generation.
"""

from flask import Flask, render_template, request, jsonify
import json

# Import solver functions from the existing solver module
from ..solver import (
    generate_puzzle,
    solve_sudoku,
    GRID_SIZE,
)

app = Flask(__name__)

@app.route("/")
def index():
    """Render the main page with an empty Sudoku grid."""
    # Initialize an empty puzzle
    puzzle = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    return render_template("index.html", puzzle=puzzle, solved=False)

@app.route("/generate")
def generate():
    """
    Generate a new puzzle with optional difficulty.
    Returns JSON containing the puzzle grid and cell colors.
    """
    difficulty = request.args.get("difficulty", "Easy")
    puzzle = generate_puzzle(difficulty=difficulty)
    # Build color array (empty cells have no color)
    cell_colors = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    return jsonify({"grid": puzzle, "cell_colors": cell_colors})

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
    # Build color array: solver-filled cells use SOLVED_COLOR from solver module
    from ..solver import SOLVED_COLOR, USER_COLOR

    cell_colors = []
    for y in range(GRID_SIZE):
        row = []
        for x in range(GRID_SIZE):
            val = solution_grid[y][x]
            if val == 0:
                row.append("")          # no background
            elif grid[y][x] != 0:      # user-entered cell remains same color
                row.append(USER_COLOR)
            else:
                row.append(SOLVED_COLOR)
        cell_colors.append(row)

    return jsonify({"grid": solution_grid, "cell_colors": cell_colors})

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

    from ..solver import save_game
    save_game(grid, user_entered, solved_flag)
    return jsonify({"status": "saved"})

@app.route("/load", methods=["GET"])
def load():
    """
    Load the most recent saved state.
    Returns JSON with grid, cell colors and timestamp.
    """
    from ..solver import load_saved_states
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