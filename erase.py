import logging
import random
from abc import ABC, abstractmethod

import numpy as np

from sudoku import Sudoku

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

LEVEL_MAP = {
    'easy': 36,
    'medium': 52,
    'hard': 56,
    'extreme': 60
}


class Eraser(ABC):
    def __init__(self, sudoku: Sudoku):
        self.sudoku = sudoku
        self.board = sudoku.board
        self.difficulty = sudoku.difficulty
        self.subgrid = sudoku.subgrid.grid


    @abstractmethod
    def erase(self) -> Sudoku:
        """ Abstract method to erase numbers from full sudoku to create a puzzle. """
        pass


class BalancedEraser(Eraser, ABC):
    """ Erases a balanced number of cells from each subgrid."""


    def __init__(self, sudoku: Sudoku) -> None:
        super().__init__(sudoku)


    def erase(self) -> Sudoku:
        logger.info("Making puzzle...")

        num_to_remove = LEVEL_MAP[self.difficulty]
        remove_per_cell = num_to_remove // 9
        leftover = num_to_remove % 9

        subgrid_ids = range(1, 10)
        for subgrid_id in subgrid_ids:
            rows, cols = np.where(self.board == subgrid_id)
            cells = zip(rows, cols)

            erased = 0
            while erased < remove_per_cell:
                rand_row, rand_col = random.choice(list(cells))
                if (val := self.board[rand_row][rand_col]) != 0:
                    self.board[rand_row][rand_col] = 0
                    # verify single solution or restore the cell
                    if self.board.has_unique_solution():
                        erased += 1
                    else:
                        self.board[rand_row][rand_col] = val

        erased = 0
        while erased < leftover:
            random_row = random.randint(0, 8)
            random_col = random.randint(0, 8)
            if self.board[random_row][random_col] != 0:
                self.board[random_row][random_col] = 0
                erased += 1

        return self.board
