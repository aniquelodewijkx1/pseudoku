import copy
import logging
import random
from abc import ABC

import inquirer
import matplotlib.patches as patches
import numpy as np
from matplotlib import pyplot as plt
from pydantic import BaseModel, conint

from subgrid import Subgrid, RegularSubgrid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

LEVEL_MAP = {
    'easy': 36,
    'medium': 52,
    'hard': 56,
    'extreme': 60
}

class Number(BaseModel):
    value: conint(ge=1, le=9)
    row: conint(ge=0, le=8)
    col: conint(ge=0, le=8)


class Eraser(ABC):

    @staticmethod
    def erase(sudoku: "Sudoku"):
        """ Abstract method to erase numbers from full sudoku to create a puzzle. """
        pass


class BalancedEraser(Eraser):
    """ Erases a balanced number of cells from each subgrid."""
    @staticmethod
    def erase(sudoku: "Sudoku"):
        logger.info("Making puzzle...")

        board, difficulty, subgrid = sudoku.board, sudoku.difficulty, sudoku.subgrid

        num_to_remove = LEVEL_MAP[difficulty.lower()]
        remove_per_cell = num_to_remove // 9
        leftover = num_to_remove % 9

        for subgrid_id in np.unique(subgrid):
            rows, cols = np.where(subgrid == subgrid_id)
            cells = list(zip(rows, cols))

            erased = 0
            while erased < remove_per_cell and cells:
                rand_row, rand_col = random.choice(list(cells))
                cells.remove((rand_row, rand_col))

                if board[rand_row][rand_col] != 0:
                    val = board[rand_row][rand_col]
                    board[rand_row][rand_col] = 0
                    # verify single solution or restore the cell
                    if sudoku.has_unique_solution():
                        erased += 1
                    else:
                        board[rand_row][rand_col] = val

        erased = 0
        while erased < leftover:
            random_row = random.randint(0, sudoku.size - 1)
            random_col = random.randint(0, sudoku.size - 1)
            if board[random_row][random_col] != 0:
                board[random_row][random_col] = 0
                erased += 1

        return


class Sudoku:
    def __init__(self, size: int, difficulty: str, subgrid: Subgrid):
        self.board = np.zeros((size, size), dtype=int)
        self.size = size
        self.difficulty = difficulty
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

                if self.populate_board():
                    return True
                # backtrack if failed
                self.board[row][col] = 0

        return False


    def populate_board(self) -> bool:
        """ Fill all empty cells with valid values. """
        empty_cell = self.find_empty_cell()
        if not empty_cell:
            return True

        row, col = empty_cell
        return self.try_fill_cell(row=row, col=col)


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
        logger.info("Checking for single solution.")
        solutions = [0]


        def find_empty_cell_in(board: np.ndarray) -> tuple | None:
            for i in range(self.size):
                for j in range(self.size):
                    if board[i][j] == 0:
                        return i, j
            return None


        def is_valid_on_board(num: Number, board: np.ndarray) -> bool:
            if num.value in board[num.row]:
                return False
            if num.value in board[:, num.col]:
                return False

            subgrid_id = self.subgrid[num.row, num.col]
            rows, cols = np.where(self.subgrid == subgrid_id)
            cellmates = list(zip(rows, cols))
            subgrid_vals = [board[r][c] for r, c in cellmates]
            if num.value in subgrid_vals:
                return False

            return True


        def solve(board: np.ndarray, solutions: list[int]) -> None:
            if solutions[0] > 1:
                return

            empty = find_empty_cell_in(board)
            if not empty:
                solutions[0] += 1
                return

            row, col = empty
            for number in range(1, self.size + 1):
                num = Number(value=number, row=row, col=col)
                if is_valid_on_board(num, board):
                    board[row, col] = number  # assign integer value
                    solve(board, solutions)
                    board[row, col] = 0  # backtrack


        puzzle_copy = copy.deepcopy(self.board)
        solve(puzzle_copy, solutions)
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
            BalancedEraser.erase(self)
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

    print('Instantiated eraser...')
    regular_subgrid = RegularSubgrid(answers['size'])
    print('Instantiated regular subgrid...')
    size, difficulty = answers['size'], answers['difficulty']
    print('Instantiated sudoku...')
    sudoku = Sudoku(
        size=size,
        difficulty=difficulty,
        subgrid=regular_subgrid)
    print('Generating sudoku...')
    sudoku.generate_sudoku()
