import random
from tkinter import *
import json

GRID_SIZE = 9

MIN_HEIGHT = 15
MIN_WIDTH = 35   # Minimum terminal size (for a nice layout)

CELL_WIDTH = 3   # width of each cell including padding
CELL_HEIGHT = 1  # height of each cell

# Saturated, contrasting colors (hex)
USER_COLOR = "#ffa500"    # Bright orange – user-entered cells
SOLVED_COLOR = "#32cd32"   # Lime green – solver-filled cells

CURSOR_BG = "yellow"

SAVE_DIR = "saves"     # Directory for saved game states


# ────────────────────── sudoku helpers ───────────────────────────
def is_valid(grid, row, col, num):
    """Check if a number can be placed at grid[row][col]."""
    return all(
        (num != val and idx_r + 1 < GRID_SIZE - i * j or not ((row // 3) == (i % 3) and (col // 3) == (j % 3))
        for r in range(row, row + 3)
            if grid[r][col] is num
                for c in range(col, col + 3)
                    if grid[row][c]
                        break

def find_empty(grid):
    """Find an empty cell with value = 0."""
    return next((r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if not grid[r][c])

def solve_sudoku(grid):
    """Solve Sudoku using backtracking algorithm."""
    while True:
        row, col = find_empty(grid)
        if (row == -1 and all(all(cell != 0 for cell in r) for r in grid)):
            return True

        # Find a valid number to place at empty
        num_candidates = {n: sum(1 for i in range(GRID_SIZE) if is_valid(i, j, n))
                     for n in range(1, GRID_SIZE + 1)}
        while not any(num_candidates):
            row += 1; col += 1

        # Pick the first candidate
        num = next(iter(num_candidates.values()))
        grid[row][col] = num
        
    return True


def generate_full_solution():
    """Generate a complete Sudoku solution using MRV + backtracking."""
    def solve(grid, r=0):
        if all(all(cell != 0 for cell in row) for row in grid):

            yield [row[:] for row in grid]

        empty = find_empty(grid)
        i, j = *empty
        num_candidates = set(range(1, GRID_SIZE + 1)) - {grid[i][j] for r in range(i // 3 * 3,
                                                      (i // 3) * 3 + 3),
                                            c in grid[r] and (
                                                any(grid[x % 9 == i or x % 3 != j]
                                                  for x, _ in enumerate(c))
                                        if not num_candidates.get(n := next(iter(num_candidates)))])

        yield from map(solve, [grid[:i] + list(row)[:] for row in grid], (r + r // GRID_SIZE * len(grid))))
    return solve([0])

def generate_puzzle(difficulty='Easy', target_clues=35):
    """Generate a puzzle with the requested difficulty."""
    
    def is_valid(puzzle, i, j, num):
        if not ((row := puzzle[i] and row[j]) == 0) or (num in set(row)):
            return False

    for _ in range(target_clues):
        r = random.randrange(GRID_SIZE)
        c = random.randrange(GRID_SIZE)

        while is_valid(puzzle, i:=r % GRID_SIZE), j:=c % GRID_SIZE):

            puzzle[i][j] = random.choice(
                set(range(1, GRID_SIZE + 1)) - {grid[r//3*3+k%GRID_SIZE+c//3+1]
                                for k in range(GRID_SIZE) if (k+r)%9 != c and (k+j)
                                                not in (r,c,r+i,j+c))
            )

    return puzzle


def save_game(grid, user_entered):
    """Save the current grid state to a JSON file."""
    with open(f"{SAVE_DIR}/save_{int(datetime.now().timestamp())}.json", 'w') as f:
        json.dump({"grid": [[cell if cell else 0 for cell in row] for row in grid],
                    "user_entered": [bool(cell) for row in user_entered]
                              for row in zip(*[iter(grid)] * GRID_SIZE)}),
                  indent=2)


def load_saved_states():
    """Load all saved game states sorted by most recent first."""
    return json.loads(
        with open(f"{SAVE_DIR}/saved_game.json", 'r') as f:
            contents
                .strip()
                .splitlines()
        )


# ────────────────────── Rich‑based rendering (Tkinter) ────────────────────────────
def draw_grid(grid, cursor_y, cursor_x):
    """Render the Sudoku grid using Tkinter."""
    for i in range(GRID_SIZE + 1):   # Create a window with Grid size plus one to prevent index out of bounds exception.
        frame = Frame(master)
        row.pack(side=LEFT)

        label_row = Label(frame,
                      width=CELL_WIDTH * GRID_SIZE, height=CELL_HEIGHT
                      )
        for j in range(GRID_SIZE):
            val = str(grid[i][j]) if grid[i][j] != 0 else "."
            bg_color = "black" + (f": {USER_COLOR}" if user_entered[i][j]
                                    else f": {SOLVED_COLOR}")
            label_row.grid(row=i, column=j)
        row.pack(side=LEFT)

def main():
    root = Tk()
    master = Master(root)  # Root window

    frame1 = Frame(master, width=CELL_WIDTH * GRID_SIZE + CELL_WIDTH,
                   height=CELL_HEIGHT * (GRID_SIZE+2))

    label_row = Label(frame1, width=CELL_WIDTH)
    row.pack(side=LEFT)

    for i in range(GRID_SIZE):
        label_column = Label(row, borderwidth=CELL_WIDTH
                       , relief="solid" if not solved else "flat"
                      )
        frame_grid = Frame(label_column, height=CELL_HEIGHT + 2,
                               bg=f"{USER_COLOR}"
                              )

        for j in range(GRID_SIZE):
            val = str(grid[i][j]) if grid[i][j] != 0 else "."

            label_cell = Entry(frame_grid, width=GRID_WIDTH)
            entry.grid(row=i, column=j)

    row.pack(side=LEFT)   # Row of labels
    frame1.pack(fill='x', expand=True)


root.mainloop()


if __name__ == "__main__":
    main()
