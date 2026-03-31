# Sudoku Solver – Interactive Terminal Edition

A lightweight, terminal‑based Sudoku solver built with **Rich** for beautiful rendering and **readchar** for responsive key handling.

---

## 📦 What this project does

- **Interactive puzzle editor**: move the cursor with `w/a/s/d` (or arrow keys), enter numbers 1–9, clear cells (`0` / `.` / backspace).
- **Automatic solving**: press `s` to solve the current grid. The solver fills all empty cells using a classic recursive back‑tracking algorithm.
- **Colourful UI**:
  - *User‑entered* cells are highlighted in bright orange.
  - *Solved* cells (previously empty) show a pastel green background.
  - Cursor is shown with a yellow background and white text.
- **Save & load**:  
  - `p` – Save the current state to a JSON file. The saved state includes each cell’s background colour so that restoring it preserves the exact look.
  - `l` – List all saved states (with solved/unsolved status and relative timestamp). Press a number to restore a specific puzzle.
- **Clear all**: `c` clears every cell, resetting the board.

---

## 📥 Installation

```bash
# Clone or download the repository
git clone https://github.com/<your_username>/sudoku_solver.git
cd sudoku_solver

# Install required Python packages
pip install readchar rich
```

The program is pure Python 3.x and requires no external dependencies beyond `readchar` and `rich`.

---

## 🚀 Running the solver

```bash
python sudoku_solver.py
```

You’ll see a nicely formatted Sudoku grid in your terminal. The top line displays the key bindings:

```
Arrow keys (w/a/s/d): move | 1-9: enter | 0/.: clear | s: solve | p: save | l: list | c: clear all | q: quit
```

### Key controls

| Key | Action |
|-----|--------|
| `w` / ↑ | Move cursor up |
| `a` / ← | Move cursor left |
| `s` / ↓ | Move cursor down |
| `d` / → | Move cursor right |
| `1–9` | Enter the number in the selected cell |
| `0`, `.`, Backspace (`←`) | Clear the selected cell |
| `s` | Solve the puzzle (fills all empty cells) |
| `p` | Save current state to disk |
| `l` | List saved states and restore one by pressing its index |
| `c` | Clear all cells |
| `q` | Quit the program |

---

## 📁 Saved States

All saved puzzles are stored in the `saves/` directory (created automatically). Each file contains:

- The grid (`grid` – 9×9 list of integers).
- The per‑cell background colour (`cell_colors`) to restore exact visual appearance.
- Timestamp (`timestamp`).
- Solved flag (`solved`).

When you press `l`, the program displays all saved states with a human‑readable relative time (“2 days ago”, “3 hours ago”, etc.).  
Press the corresponding number to load that puzzle back into the current grid.

---

## 🎨 Color Scheme

| State | Background colour |
|-------|-------------------|
| **User‑entered** | `#ffa500` (bright orange) |
| **Solved** | `#32cd32` (pastel green) |
| **Cursor** | Yellow background with white text |

The grid is padded so each cell occupies three columns, making the separators align perfectly.

---

## 🛠️ Extending

Feel free to tweak the colour codes or add more features such as:

- Import/export from a CSV/JSON file.
- Custom puzzle generation.
- Performance profiling for larger puzzles.

Happy solving!