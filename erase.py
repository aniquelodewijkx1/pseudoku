import copy
import random
from abc import ABC, abstractmethod

import numpy as np

LEVEL_MAP = {
    'easy': 36,
    'medium': 52,
    'hard': 56,
    'extreme': 60
}


class Eraser(ABC):
    def __init__(self, board: np.ndarray, difficulty: str):
        self.puzzle = copy.deepcopy(board)
        self.difficulty = difficulty


    @abstractmethod
    def erase(self) -> np.ndarray:
        """ Abstract method to erase numbers from full sudoku to create a puzzle. """
        pass


class SymmetricEraser(Eraser, ABC):
    def __init__(self, board: np.ndarray, difficulty: str):
        super().__init__(board, difficulty)


    def erase(self) -> np.ndarray:
        num_to_remove = LEVEL_MAP[self.difficulty]
        remove_per_cell = num_to_remove // 9
        leftover = num_to_remove % 9

        # define starting cell for all 9 subgrids
        subgrid_starts = []
        for i in range(0, 8, 3):
            for j in range(0, 8, 3):
                subgrid_starts.append((i, j))

        # erase a balanced number of numbers in each cell
        for subgrid_start in subgrid_starts:
            erased = 0
            row_start, col_start = subgrid_start

            while erased < remove_per_cell:
                random_row = random.randint(row_start, row_start + 2)
                random_col = random.randint(col_start, col_start + 2)
                if self.puzzle[random_row][random_col] != 0:
                    self.puzzle[random_row][random_col] = 0
                    erased += 1

        erased = 0
        while erased < leftover:
            random_row = random.randint(0, 8)
            random_col = random.randint(0, 8)
            if self.puzzle[random_row][random_col] != 0:
                self.puzzle[random_row][random_col] = 0
                erased += 1

        return self.puzzle


class AutomorphicEraser(Eraser, ABC):
    def __init__(self, board: np.ndarray, difficulty: str):
        super().__init__(board, difficulty)


    def erase(self) -> np.ndarray:
        pass