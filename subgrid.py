from abc import ABC

import numpy as np


class Subgrid(ABC):

    def __init__(self):
        self.grid = self.get_subgrid()

    def get_subgrid(self) -> np.ndarray:
        pass


class RegularSubgrid(Subgrid):

    def __init__(self):
        super().__init__()

    def get_subgrid(self) -> np.ndarray:
        base_pattern = np.array([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ])
        # Kronecker product to expand the 3x3 pattern to 9x9
        subgrid_patten = np.kron(base_pattern, np.ones((3, 3), dtype=int))
        return subgrid_patten


class IrregularSubgrid(Subgrid):

    def __init__(self):
        super().__init__()

    def return_subgrid(self) -> np.ndarray:
        pass