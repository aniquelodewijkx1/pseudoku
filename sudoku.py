import random

import inquirer
import numpy as np
from matplotlib import pyplot as plt
from poetry.console.commands import self

from erase import BalancedEraser, AutomorphicEraser

ERASER_MAP = {
    "None (Standard)": BalancedEraser,
    "Automorphic": AutomorphicEraser
}


class Sudoku:
    def __init__(self, difficulty: str, type: str):
        self.board = np.zeros((9, 9), dtype=int)

        self.difficulty = difficulty
        self.type = type

        puzzle = self.generate_sudoku()
        self.plot(puzzle)


    @staticmethod
    def is_valid(board: np.ndarray, subgrids: dict[int, set], num: dict) -> bool:
        """ Checks if number is present in same row, column, or subgrid.
        - board: 9x9 numpy array populated with numbers
        - subgrids: {1: ((x, y), (x2, y2), ...), 2: (...), ...}
        - proposed_num: {"value": int 1-9, "row": x, "col": y}
        """
        value, row, col, subgrid = num["value"], num["row"], num["col"], num["subgrid"]
        if value in board[row]:
            return False
        if value in board[:, col]:
            return False

        subgrid_coords = subgrids[subgrid]
        subgrid_vals = [board[r][c] for r, c in subgrid_coords]
        if value in subgrid_vals:
            return False

        return True


    @staticmethod
    def find_empty_cell(board) -> tuple | None:
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None


    def populate_board(self) -> bool:
        if self.type == "Irregular":
            subgrids = self.generate_irregular_subgrids()
        else:
            subgrids = self.generate_subgrids()

        empty_cell = self.find_empty_cell(self.board)

        if not empty_cell:
            return True

        row, col = empty_cell

        for number in range(1, 10):
            num = {"value": number, "row": row, "col": col}
            if self.is_valid(self.board, num, subgrids):
                self.board[row][col] = number

                if self.populate_board():
                    return True

            self.board[row][col] = 0

        return False

    @staticmethod
    def generate_subgrids() -> dict[int, set]:
        subgrids = {i: set() for i in range(1, 10)}
        subgrid_starts = []
        for i in range(0, 8, 3):
            for j in range(0, 8, 3):
                subgrid_starts.append((i, j))

        for i, (r, c) in enumerate(subgrid_starts):
            for z in range(0, 3):
                for y in range(0, 3):
                    subgrids[i].add((r + z, c + y))

        return subgrids

    def generate_irregular_subgrids(self) -> dict[int, set[tuple]]:
        """ Generates a dictionary that maps 9 subgrids to a set of coordinates. """
        subgrids = {i: set() for i in range(1, 10)}

        # seed cells for 9 subgrids
        seeds = random.sample([(row, col) for row in range(9) for col in range(9)], 9)
        for i, (row, col) in enumerate(seeds):
            self.board[row][col] = i
            subgrids[i].add((row, col))

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # expand each subgrid iteratively
        while any(len(subgrids[subgrid]) for subgrid in subgrids) < 9:
            for s in range(1, 10):
                if len(subgrids[s]) == 9:
                    continue

                potential = set()
                for (x, y) in subgrids[s]:
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (
                                0 <= nx < 9 and
                                0 <= ny < 9 and
                                self.board[nx][ny] == 0):
                            potential.add((nx, ny))
                if not potential:
                    continue

                cell = random.choice(list(potential))
                self.board[cell[0]][cell[1]] = s
                subgrids[s].add(cell)

        return subgrids


    def erase(self):
        eraser_class = ERASER_MAP[self.type]
        eraser = eraser_class(self.board, self.difficulty)

        puzzle = eraser.erase()

        return puzzle


    @staticmethod
    def plot(grid):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, 9)
        ax.set_ylim(0, 9)
        ax.set_xticks(np.arange(0, 10, 1))
        ax.set_yticks(np.arange(0, 10, 1))
        ax.grid(which='both', color='black', linewidth=1)

        # Add thicker lines for subgrids
        for i in range(0, 10):
            if i % 3 == 0:
                ax.axhline(i, color='black', linewidth=2.5)
                ax.axvline(i, color='black', linewidth=2.5)

        # Fill numbers
        for i in range(9):
            for j in range(9):
                num = grid[i, j]
                if num != 0:
                    ax.text(j + 0.5, 9 - i - 0.5, str(num),
                            fontsize=20, ha='center', va='center')

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        plt.show()


    def generate_sudoku(self) -> np.ndarray:
        if self.populate_board():
            puzzle = self.erase()
            return puzzle


if __name__ == '__main__':
    questions = [
        inquirer.List(
            'difficulty',
            message="Difficulty?",
            choices=['Easy', 'Medium', 'Hard', 'Extreme'],
        ),
        inquirer.List(
            'type',
            message="Type?",
            choices=['None (Standard)', 'Irregular Subgrids'],
        ),
    ]
    try:
        answers = inquirer.prompt(questions)
        sudoku = Sudoku(
            difficulty=answers['difficulty'].lower(),
            type=answers['type'])

    except Exception:
        print('🏜️ Run me from the terminal, thanks!')
