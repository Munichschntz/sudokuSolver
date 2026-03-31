# (existing code unchanged)

def grid_to_json(grid, user_entered):
    """
    Return a JSON‑serialisable representation of the grid with cell background colors.
    This is useful for API responses or storage in databases.
    """
    cell_colors = []
    for y in range(GRID_SIZE):
        row = []
        for x in range(GRID_SIZE):
            val = grid[y][x]
            if val == 0:
                row.append("")          # no background
            elif user_entered[y][x]:
                row.append(USER_COLOR)
            else:
                row.append(SOLVED_COLOR)
        cell_colors.append(row)

    return {"grid": grid, "cell_colors": cell_colors}

# ----------------------------------------------------------------------
# Back‑tracking Sudoku solver
# ----------------------------------------------------------------------
def is_valid(grid: List[List[int]], row: int, col: int, num: int) -> bool:
    """
    Check if a number can be placed at grid[row][col] without violating Sudoku rules.
    """
    for i in range(GRID_SIZE):
        if grid[i][col] == num:
            return False
    for j in range(GRID_SIZE):
        if grid[row][j] == num:
            return False
    # Check 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if grid[i][j] == num:
                return False
    return True

def find_empty(grid: List[List[int]]) -> tuple[int, int]:
    """
    Find an empty cell (value = 0). Returns (row, col) or (-1, -1) if none.
    """
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                return (r, c)
    return (-1, -1)

def solve(grid: List[List[int]]) -> List[List[int]]:
    """
    Solve the Sudoku puzzle using back‑tracking.
    Raises ValueError if no solution exists.
    Returns the solved grid.
    """
    row, col = find_empty(grid)
    if row == -1:
        # Puzzle solved
        return grid

    for num in range(1, GRID_SIZE + 1):
        if is_valid(grid, row, col, num):
            grid[row][col] = num
            try:
                return solve(grid)
            except ValueError:
                # Backtrack
                grid[row][col] = 0
                continue

    raise ValueError("No solution found")