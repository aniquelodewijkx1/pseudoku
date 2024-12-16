import copy
import logging
import random
from abc import ABC, abstractmethod

import inquirer
import matplotlib.patches as patches
import numpy as np
from matplotlib import pyplot as plt
from pydantic import BaseModel, conint

from erase import Eraser
from subgrid import Subgrid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Number(BaseModel):
    value: conint(ge=1, le=9)
    row: conint(ge=1, le=9)
    col: conint(ge=1, le=9)


class Sudoku(ABC):
    def __init__(self, difficulty: str, eraser: Eraser, subgrid: Subgrid):
        self.board = np.zeros((9, 9), dtype=int)
        self.difficulty = difficulty
        self.eraser = eraser
        self.subgrid = Subgrid.grid


    @abstractmethod
    def populate_board(self) -> bool:
        empty_cell = self.find_empty_cell()

        if not empty_cell:
            return True

        row, col = empty_cell
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for number in numbers:
            num = Number(value=number, row=row, col=col)
            if self.is_valid(num=num):
                self.board[row][col] = number

                if self.populate_board():
                    return True

            self.board[row][col] = 0

        return False


    @abstractmethod
    def has_unique_solution(self) -> bool:
        """ Check if a board has one solution with recursive backtracking. """
        solutions = [0]


        def solve(board: Sudoku, solutions: list[int]) -> None:
            if solutions[0] > 1:
                return

            empty = self.find_empty_cell()
            if empty is None:
                solutions[0] += 1
                return

            row, col = empty
            for num in range(1, 10):
                number = {'value': num, 'row': row, 'col': col}
                if board.is_valid():
                    board[row, col] = num
                    solve(board, solutions)
                    board[row, col] = 0
            return


        puzzle_copy = copy.deepcopy(self.board)
        solve(board=puzzle_copy, solutions=solutions)

        return solutions[0] == 1


    @abstractmethod
    def find_empty_cell(self) -> tuple | None:
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None


    def is_valid(self, num: Number) -> bool:
        """ Checks if number is present in same row, column, or subgrid.
        - board: 9x9 numpy array populated with numbers
        - subgrids: {1: ((x, y), (x2, y2), ...), 2: (...), ...}
        - proposed_num: {"value": int 1-9, "row": x, "col": y}
        """
        if num.value in self.board[num.row]:
            return False
        if num.value in self.board[:, num.col]:
            return False

        subgrid_coords = None
        for subgrid_id, cells in subgrids.items():
            if (num.row, num.col) in cells:
                subgrid_coords = cells
                break

        if subgrid_coords is None:
            raise "Cell not assigned to a subgrid."

        subgrid_vals = [self.board[r][c] for r, c in subgrid_coords]
        if num.value in subgrid_vals:
            return False

        return True


    @abstractmethod
    def plot(self):
        logger.info("Plotting Sudoku...")

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, 9)
        ax.set_ylim(0, 9)
        ax.set_xticks(np.arange(0, 10, 1))
        ax.set_yticks(np.arange(0, 10, 1))
        ax.grid(which='both', color='black', linewidth=1)

        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # draw subgrid boundaries
        subgrid_ids = np.unique(self.subgrid)
        for subgrid_id in subgrid_ids:
            # find coordinates of the cells in current subgrid
            rows, cols = np.where(self.subgrid == subgrid_id)
            if len(rows) > 0 and len(cols) > 0:
                # determine bounding box for subgrid
                min_row, max_row = rows.min(), rows.max()
                min_col, max_col = cols.min(), cols.max()

                # convert grid coordinates to plot coordinates
                lower_left = (min_col, 8 - max_row)
                width = max_col - min_col + 1
                height = max_row - min_row + 1

                # rectangle patch for subgrid boundary
                rect = patches.Rectangle(lower_left, width, height,
                                         linewidth=2.5, edgecolor='black', facecolor='none')
                ax.add_patch(rect)

        # fill in numbers from grid
        for i in range(9):
            for j in range(9):
                num = self.grid[i, j]
                if num != 0:
                    ax.text(j + 0.5, 9 - i - 0.5, str(num),
                            fontsize=20, ha='center', va='center')

        plt.show()


    def generate_sudoku(self):
        pass


class RegularSudoku(Sudoku):
    def __init__(self, difficulty: str, eraser: Eraser, subgrids: Subgrid):
        super().__init__()


    def create_puzzle(self):
        return self.eraser.erase()


    def generate_sudoku(self):
        logger.info("Populating board...")
        if self.populate_board():
            puzzle = self.create_puzzle()
            puzzle.plot()


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

    answers = inquirer.prompt(questions)
    sudoku = Sudoku(
        difficulty=answers['difficulty'].lower(),
        type=answers['type'])
