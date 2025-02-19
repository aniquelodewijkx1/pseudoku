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
        base_pattern = np.array([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ])
        # Kronecker product to expand the 3x3 pattern to 9x9
        self.grid = np.kron(base_pattern, np.ones((3, 3), dtype=int))

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
        """ Creates four subgrids evenly spaced. """

        for row in range(1, 4):
            for col in range(1, 4):
                self.grid[row][col] = 1
            for col in range(5, 8):
                self.grid[row][col] = 2

        for row in range(5, 8):
            for col in range(1, 4):
                self.grid[row][col] = 3
            for col in range(5, 8):
                self.grid[row][col] = 4

        return self.grid


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






