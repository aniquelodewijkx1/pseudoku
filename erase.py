import logging
import random
from abc import ABC, abstractmethod

import numpy as np


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

LEVEL_MAP = {
    'easy': 36,
    'medium': 52,
    'hard': 56,
    'extreme': 60
}


class Eraser(ABC):

    @staticmethod
    def erase(sudoku):
        """ Abstract method to erase numbers from full sudoku to create a puzzle. """
        pass


class BalancedEraser(Eraser):
    """ Erases a balanced number of cells from each subgrid."""
    @staticmethod
    def erase(sudoku):
        logger.info("Making puzzle...")

        board, difficulty, subgrid = sudoku.board, sudoku.difficulty, sudoku.subgrid

        num_to_remove = LEVEL_MAP[difficulty.lower()]
        remove_per_cell = num_to_remove // 9
        leftover = num_to_remove % 9

        for subgrid_id in range(1,10):
            rows, cols = np.where(subgrid == subgrid_id)
            cells = list(zip(rows, cols))

            erased = 0
            while erased < remove_per_cell:
                rand_row, rand_col = random.choice(list(cells))
                if (val := board[rand_row][rand_col]) != 0:
                    board[rand_row][rand_col] = 0
                    # verify single solution or restore the cell
                    if board.has_unique_solution():
                        erased += 1
                    else:
                        board[rand_row][rand_col] = val

        erased = 0
        while erased < leftover:
            random_row = random.randint(0, 8)
            random_col = random.randint(0, 8)
            if board[random_row][random_col] != 0:
                board[random_row][random_col] = 0
                erased += 1

        return
