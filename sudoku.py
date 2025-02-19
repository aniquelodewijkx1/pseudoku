import copy
import logging
import random

import inquirer
import matplotlib.patches as patches
import numpy as np
from matplotlib import pyplot as plt
from pydantic import BaseModel, conint

from erase import Eraser, BalancedEraser
from subgrid import Subgrid, RegularSubgrid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Number(BaseModel):
    value: conint(ge=1, le=9)
    row: conint(ge=0, le=8)
    col: conint(ge=0, le=8)


class Sudoku:
    def __init__(self, size: int, difficulty: str, eraser: Eraser, subgrid: Subgrid):
        self.board = np.zeros((size, size), dtype=int)
        self.size = size
        self.difficulty = difficulty
        self.eraser = eraser
        self.subgrid = subgrid.grid


    def find_empty_cell(self) -> tuple | None:
        logger.info("Finding empty cell")
        """ Find cell without value. """
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return i, j
        return None


    def try_fill_cell(self, row: int, col: int) -> bool:
        """ Fill an empty cell with a value and check validity. """
        logger.info("Trying fill cell")
        numbers = list(range(1, self.size + 1))
        random.shuffle(numbers)

        for number in numbers:
            num = Number(value=number, row=row, col=col)
            if self.is_valid(num=num):
                self.board[row][col] = number
                return True

        return False


    def populate_board(self) -> bool:
        """ Fill all empty cells with valid values. """
        empty_cell = self.find_empty_cell()
        if not empty_cell:
            return True

        row, col = empty_cell
        if self.try_fill_cell(row, col):
            if self.populate_board():
                return True

        self.board[row, col] = 0  # backtrack
        return False


    def is_valid(self, num: Number) -> bool:
        """ Checks if number is present in same row, column, or subgrid. """
        logger.info("Checking validity.")
        if num.value in self.board[num.row]:
            return False
        if num.value in self.board[:, num.col]:
            return False

        subgrid_id = self.subgrid[num.row, num.col]
        rows, cols =  np.where(self.subgrid == subgrid_id)
        cellmates = list(zip(rows, cols))

        subgrid_vals = [self.board[r][c] for r, c in cellmates]
        if num.value in subgrid_vals:
            return False

        return True


    def has_unique_solution(self) -> bool:
        """ Check if a board has one solution with recursive backtracking. """
        logger.info("Checking for single solution.")
        solutions = [0]

        def solve(board: np.ndarray, solutions: list[int]) -> None:
            if solutions[0] > 1:
                return

            empty = self.find_empty_cell()
            if not empty:
                solutions[0] += 1
                return

            row, col = empty
            for number in range(1, self.size + 1):
                num = Number(value=number, row=row, col=col)
                if self.is_valid(num=num):
                    board[row, col] = num
                    solve(board, solutions)
                    board[row, col] = 0  # backtrack

        puzzle_copy = copy.deepcopy(self.board)
        solve(board=puzzle_copy, solutions=solutions)

        return solutions[0] == 1


    def plot(self):
        logger.info("Plotting Sudoku...")

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        ax.set_xticks(np.arange(0, self.size + 1, 1))
        ax.set_yticks(np.arange(0, self.size + 1, 1))
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
                lower_left = (min_col, self.size - 1 - max_row)
                width = max_col - min_col + 1
                height = max_row - min_row + 1

                # rectangle patch for subgrid boundary
                rect = patches.Rectangle(lower_left, width, height,
                                         linewidth=2.5, edgecolor='black', facecolor='none')
                ax.add_patch(rect)

        # fill in numbers from grid
        for i in range(self.size):
            for j in range(self.size):
                num = self.board[i, j]
                if num != 0:
                    ax.text(j + 0.5, self.size - i - 0.5, str(num),
                            fontsize=20, ha='center', va='center')

        plt.show()


    def generate_sudoku(self):
        logger.info("Making sudoku...")
        if self.populate_board():
            logger.info("Sudoku populated.")
            logger.info("Erasing...")
            self.eraser.erase(self)
            logger.info("Sudoku erased.")
            logger.info("Plotting...")
            self.plot()


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
        inquirer.List(
            'size',
            message="Grid size?",
            choices=[6, 8, 9],
        ),
    ]
    answers = inquirer.prompt(questions)

    balanced_eraser = BalancedEraser()
    regular_subgrid = RegularSubgrid(answers['size'])
    size, difficulty = answers['size'], answers['difficulty']
    sudoku = Sudoku(
        size=size,
        difficulty=difficulty,
        eraser=balanced_eraser,
        subgrid=regular_subgrid)

    sudoku.generate_sudoku()
