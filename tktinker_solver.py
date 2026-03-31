"""Tkinter Sudoku UI that shares core logic with the webapp module."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from solver import (
    GRID_SIZE,
    SOLVED_COLOR,
    USER_COLOR,
    generate_puzzle,
    load_saved_states,
    save_game,
    solve_sudoku,
)

APP_BG = "#f6f4ef"
PANEL_BG = "#fbfaf8"
GRID_LINE = "#2b2a28"
BUTTON_BG = "#1f2937"
BUTTON_FG = "#f9fafb"
ENTRY_BG = "#ffffff"


def _difficulty_options() -> tuple[str, ...]:
    return ("Easy", "Medium", "Hard")


class SudokuTkApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.configure(bg=APP_BG)
        self.root.minsize(680, 780)

        self.grid_data = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.user_entered = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.entries: list[list[tk.Entry]] = []

        self.status_text = tk.StringVar(value="Enter values or generate a puzzle.")
        self.difficulty = tk.StringVar(value="Easy")

        self._build_ui()

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=APP_BG, padx=18, pady=18)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=APP_BG)
        header.pack(fill="x", pady=(0, 12))

        tk.Label(
            header,
            text="Sudoku Studio",
            font=("Segoe UI", 24, "bold"),
            bg=APP_BG,
            fg="#111827",
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Same solver engine as the web app, with instant desktop controls.",
            font=("Segoe UI", 11),
            bg=APP_BG,
            fg="#374151",
        ).pack(anchor="w", pady=(4, 0))

        controls = tk.Frame(outer, bg=PANEL_BG, padx=10, pady=10, highlightbackground="#d6d3cd", highlightthickness=1)
        controls.pack(fill="x", pady=(0, 12))

        ttk.Label(controls, text="Difficulty:", background=PANEL_BG).pack(side="left", padx=(0, 8))

        difficulty_box = ttk.Combobox(
            controls,
            values=_difficulty_options(),
            textvariable=self.difficulty,
            width=10,
            state="readonly",
        )
        difficulty_box.pack(side="left", padx=(0, 10))

        self._add_button(controls, "Generate", self.generate_new)
        self._add_button(controls, "Solve", self.solve_current)
        self._add_button(controls, "Clear", self.clear_grid)
        self._add_button(controls, "Save", self.save_current)
        self._add_button(controls, "Load Latest", self.load_latest)

        board_wrap = tk.Frame(outer, bg=PANEL_BG, padx=14, pady=14, highlightbackground="#d6d3cd", highlightthickness=1)
        board_wrap.pack(fill="both", expand=True)

        board = tk.Frame(board_wrap, bg=GRID_LINE)
        board.pack()

        for row in range(GRID_SIZE):
            row_widgets: list[tk.Entry] = []
            for col in range(GRID_SIZE):
                cell = tk.Entry(
                    board,
                    width=2,
                    justify="center",
                    font=("Segoe UI", 18, "bold"),
                    bg=ENTRY_BG,
                    relief="flat",
                )
                padx = (2 if col % 3 == 0 else 1, 2 if col % 3 == 2 else 1)
                pady = (2 if row % 3 == 0 else 1, 2 if row % 3 == 2 else 1)
                cell.grid(row=row, column=col, padx=padx, pady=pady, ipadx=9, ipady=8)
                cell.bind("<KeyRelease>", lambda event, r=row, c=col: self.on_cell_change(r, c))
                row_widgets.append(cell)
            self.entries.append(row_widgets)

        footer = tk.Label(
            outer,
            textvariable=self.status_text,
            font=("Segoe UI", 10),
            bg=APP_BG,
            fg="#374151",
            anchor="w",
        )
        footer.pack(fill="x", pady=(12, 0))

    def _add_button(self, parent: tk.Widget, text: str, command) -> None:
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            relief="flat",
            padx=12,
            pady=6,
            font=("Segoe UI", 10, "bold"),
            activebackground="#111827",
            activeforeground="#ffffff",
        ).pack(side="left", padx=4)

    def on_cell_change(self, row: int, col: int) -> None:
        raw_value = self.entries[row][col].get().strip()

        if raw_value == "":
            self.grid_data[row][col] = 0
            self.user_entered[row][col] = False
            self.entries[row][col].configure(bg=ENTRY_BG)
            return

        if not raw_value.isdigit() or raw_value not in {str(n) for n in range(1, 10)}:
            self.entries[row][col].delete(0, tk.END)
            self.grid_data[row][col] = 0
            self.user_entered[row][col] = False
            self.entries[row][col].configure(bg=ENTRY_BG)
            self.status_text.set("Only digits 1-9 are allowed in a cell.")
            return

        value = int(raw_value)
        self.grid_data[row][col] = value
        self.user_entered[row][col] = True
        self.entries[row][col].configure(bg=USER_COLOR)

    def _sync_board_from_state(self, mark_existing_as_user: bool = False) -> None:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                entry = self.entries[row][col]
                value = self.grid_data[row][col]

                entry.delete(0, tk.END)
                if value != 0:
                    entry.insert(0, str(value))

                if value == 0:
                    entry.configure(bg=ENTRY_BG)
                    self.user_entered[row][col] = False
                elif mark_existing_as_user:
                    self.user_entered[row][col] = True
                    entry.configure(bg=USER_COLOR)
                elif self.user_entered[row][col]:
                    entry.configure(bg=USER_COLOR)
                else:
                    entry.configure(bg=SOLVED_COLOR)

    def generate_new(self) -> None:
        self.grid_data = generate_puzzle(self.difficulty.get())
        self.user_entered = [[cell != 0 for cell in row] for row in self.grid_data]
        self._sync_board_from_state(mark_existing_as_user=True)
        self.status_text.set(f"Generated {self.difficulty.get()} puzzle.")

    def solve_current(self) -> None:
        original = [row[:] for row in self.grid_data]

        if not solve_sudoku(self.grid_data):
            messagebox.showerror("Unsolvable", "This puzzle cannot be solved.")
            self.status_text.set("Puzzle appears unsolvable. Check your inputs.")
            return

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if original[row][col] == 0 and self.grid_data[row][col] != 0:
                    self.user_entered[row][col] = False
                elif original[row][col] != 0:
                    self.user_entered[row][col] = True

        self._sync_board_from_state()
        self.status_text.set("Solved successfully.")

    def clear_grid(self) -> None:
        self.grid_data = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.user_entered = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self._sync_board_from_state()
        self.status_text.set("Grid cleared.")

    def save_current(self) -> None:
        solved = all(cell != 0 for row in self.grid_data for cell in row)
        path = save_game(self.grid_data, self.user_entered, solved)
        self.status_text.set(f"Saved game to {path}.")

    def load_latest(self) -> None:
        states = load_saved_states()
        if not states:
            messagebox.showinfo("No saves", "No saved puzzles found.")
            return

        latest = states[0]
        self.grid_data = [[int(cell) for cell in row] for row in latest.get("grid", [])]
        if len(self.grid_data) != GRID_SIZE or any(len(row) != GRID_SIZE for row in self.grid_data):
            messagebox.showerror("Invalid save", "Latest save file has invalid grid data.")
            return

        saved_users = latest.get("user_entered")
        if saved_users and len(saved_users) == GRID_SIZE and all(len(row) == GRID_SIZE for row in saved_users):
            self.user_entered = [[bool(cell) for cell in row] for row in saved_users]
        else:
            self.user_entered = [[cell != 0 for cell in row] for row in self.grid_data]

        self._sync_board_from_state()
        timestamp = latest.get("timestamp", "unknown time")
        self.status_text.set(f"Loaded latest save from {timestamp}.")


def main() -> None:
    root = tk.Tk()
    app = SudokuTkApp(root)
    _ = app
    root.mainloop()


if __name__ == "__main__":
    main()
