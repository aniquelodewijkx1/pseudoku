import copy
import random
from abc import ABC, abstractmethod

import numpy as np
from poetry.console.commands import self

from sudoku import Sudoku

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


    @staticmethod
    def has_unique_solution(puzzle: np.ndarray) -> bool:
        """ Check if a puzzle has one solution with recursive backtracking. """
        solutions = 0

        def solve(puzzle: np.ndarray, solutions: int) -> None:
            if Sudoku.find_empty_cell(puzzle) is None:
                solutions += 1
                return
            if solutions > 1:
                return

            for row in range(9):
                for col in range(9):
                    if puzzle[row, col] == 0:
                        for num in range(1, 10):
                            if Sudoku.is_valid(row, col, num):
                                puzzle[row, col] = num
                                solve(puzzle, solutions)
                                puzzle[row, col] = 0
            return


        solve(puzzle, solutions)
        return solutions == 1


class BalancedEraser(Eraser, ABC):
    """ Erases a balanced number of cells from each subgrid."""
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
                if val := self.puzzle[random_row][random_col] != 0:
                    self.puzzle[random_row][random_col] = 0
                    # verify single solution or restore the cell
                    if Eraser.has_unique_solution(self.puzzle):
                        erased += 1
                    else:
                        self.puzzle[random_row][random_col] = val

        erased = 0
        while erased < leftover:
            random_row = random.randint(0, 8)
            random_col = random.randint(0, 8)
            if self.puzzle[random_row][random_col] != 0:
                self.puzzle[random_row][random_col] = 0
                erased += 1

        return self.puzzle


class AutomorphicEraser(Eraser, ABC):
    """https://en.wikipedia.org/wiki/Mathematics_of_Sudoku"""
    def __init__(self, board: np.ndarray, difficulty: str):
        super().__init__(board, difficulty)


    def erase(self) -> np.ndarray:
        pass


class MinimalEraser(Eraser, ABC):
    """ Erases such that no clue can be removed that retains one solution."""
    def __init__(self, board: np.ndarray, difficulty: str):
        super().__init__(board, difficulty)


    def erase(self) -> np.ndarray:
        pass

