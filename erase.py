import copy
import logging
import random
from abc import ABC, abstractmethod

import numpy as np

from utils import is_valid, find_empty_cell

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

LEVEL_MAP = {
    'easy': 36,
    'medium': 52,
    'hard': 56,
    'extreme': 60
}


class Eraser(ABC):
    def __init__(self, board: np.ndarray, difficulty: str, subgrids: dict):
        self.puzzle = copy.deepcopy(board)
        self.difficulty = difficulty
        self.subgrids = subgrids


    @abstractmethod
    def erase(self) -> np.ndarray:
        """ Abstract method to erase numbers from full sudoku to create a puzzle. """
        pass


    @staticmethod
    def has_unique_solution(puzzle: np.ndarray, subgrids: dict) -> bool:
        """ Check if a puzzle has one solution with recursive backtracking. """
        solutions = [0]

        def solve(puzzle: np.ndarray, solutions: list[int], subgrids: dict) -> None:
            if solutions[0] > 1:
                return

            empty = find_empty_cell(puzzle)
            if empty is None:
                solutions[0] += 1
                return

            row, col = empty
            for num in range(1, 10):
                number = {'value': num, 'row': row, 'col': col}
                if is_valid(board=puzzle, subgrids=subgrids, num=number):
                    puzzle[row, col] = num
                    solve(puzzle, solutions, subgrids)
                    puzzle[row, col] = 0
            return

        puzzle_copy = puzzle.copy()
        solve(puzzle=puzzle_copy, solutions=solutions, subgrids=subgrids)
        return solutions[0] == 1


class BalancedEraser(Eraser, ABC):
    """ Erases a balanced number of cells from each subgrid."""
    def __init__(self, board: np.ndarray, difficulty: str, subgrids: dict) -> None:
        super().__init__(board, difficulty, subgrids)


    def erase(self) -> np.ndarray:
        logger.info("Making puzzle...")

        num_to_remove = LEVEL_MAP[self.difficulty]
        remove_per_cell = num_to_remove // 9
        leftover = num_to_remove % 9

        for subgrid, cells in self.subgrids.items():
            erased = 0
            while erased < remove_per_cell:
                rand_row, rand_col = random.choice(list(cells))
                if (val := self.puzzle[rand_row][rand_col]) != 0:
                    self.puzzle[rand_row][rand_col] = 0
                    # verify single solution or restore the cell
                    if Eraser.has_unique_solution(puzzle=self.puzzle, subgrids=self.subgrids):
                        erased += 1
                    else:
                        self.puzzle[rand_row][rand_col] = val

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

