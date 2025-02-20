import random
from abc import ABC, abstractmethod

import numpy as np


class Subgrid(ABC):
    def __init__(self, size: int):
        self.size = size
        self.grid = np.zeros(size, dtype=int)
        self.get_subgrid()

    @abstractmethod
    def get_subgrid(self) -> np.ndarray:
        pass


class RegularSubgrid(Subgrid):

    def __init__(self, size: int):
        super().__init__(size)

    def get_subgrid(self) -> np.ndarray:
        match self.size:
            case 4:
                base_pattern = np.array([
                    [1, 2,],
                    [3, 4]
                ])
                # Kronecker product to expand the 2x2 pattern to 4x4
                self.grid = np.kron(base_pattern, np.ones((2, 2), dtype=int))

            case 9:
                base_pattern = np.array([
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ])
                # Kronecker product to expand the 3x3 pattern to 9x9
                self.grid = np.kron(base_pattern, np.ones((3, 3), dtype=int))

            case 16:
                base_pattern = np.array([
                    [1, 2, 3, 4],
                    [5, 6, 7, 8],
                    [9, 10, 11, 12],
                    [13, 14, 15, 16]
                ])
                # Kronecker product to expand the 4x4 pattern to 16x16
                self.grid = np.kron(base_pattern, np.ones((4, 4), dtype=int))

        return self.grid


class IrregularSubgrid(Subgrid):

    def __init__(self, size: int):
        super().__init__(size)

    def get_subgrid(self) -> np.ndarray:
        pass

class HyperSubgrid(Subgrid):

    def __init__(self, size: int):
        super().__init__(size)


    def get_subgrid(self) -> np.ndarray:
        """
        Creates an array with internal hypergrids.

        For a grid of size n x n (n being 4, 9, 16, ...):
          - Let m = int(sqrt(n)). For a 4x4, m=2; 9x9, m=3; 16x16, m=4.
          - The number of hyper subgrids per row is k = (n - 1) // (m + 1).
          - Each hyper subgrid is of size m x m.
          - Hyper subgrids do not touch the edge, and are separated by exactly one empty row and column.

        The method fills the grid with unique positive integers (starting at 1) in each hyper subgrid,
        leaving 0s elsewhere.
        """
        n = self.size
        m = int(n ** 0.5)
        k = (n - 1) // (m + 1)

        grid = np.zeros((n, n), dtype=int)
        id_counter = 1
        for i in range(k):
            for j in range(k):
                # Calculate the top-left coordinates.
                start_row = i * (m + 1) + 1
                start_col = j * (m + 1) + 1
                # Fill an m x m block.
                for r in range(start_row, start_row + m):
                    for c in range(start_col, start_col + m):
                        grid[r, c] = id_counter
                id_counter += 1

        return grid


class KillerSubgrid(Subgrid):
    def __init__(self, size: int, difficulty: str):
        super().__init__(size)
        self.difficulty = difficulty

    def get_subgrid(self) -> np.ndarray:
        """ Creates cages with 2-5 cells with distinct sums. """
        difficulty_map = {
            'easy': 2,
            'medium': 4,
            'hard': 5,
            'extreme': 6,
        }
        num_cages = difficulty_map[self.difficulty]

        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))

        for i, _ in enumerate(num_cages):
            random_x = np.random.randint(0, self.size)
            random_y = np.random.randint(0, self.size)
            self.grid[random_x, random_y] = i + 1

            cage_size = random.randint(2, 6)

            for cell in range(cage_size):
                direction = random.choice(directions)
                new_cell = (random_x, random_y) + direction

                if new_cell == 0:
                    self.grid[new_cell] = i
                    random_x = new_cell[0]
                    random_y = new_cell[1]

        return self.grid
