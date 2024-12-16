import logging

import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def is_valid(board: np.ndarray, subgrids: dict[int, set], num: dict) -> bool:
    """ Checks if number is present in same row, column, or subgrid.
    - board: 9x9 numpy array populated with numbers
    - subgrids: {1: ((x, y), (x2, y2), ...), 2: (...), ...}
    - proposed_num: {"value": int 1-9, "row": x, "col": y}
    """
    value, row, col = num["value"], num["row"], num["col"]
    if value in board[row]:
        return False
    if value in board[:, col]:
        return False

    subgrid_coords = None
    for subgrid_id, cells in subgrids.items():
        if (row, col) in cells:
            subgrid_coords = cells
            break

    if subgrid_coords is None:
        raise "Cell not assigned to a subgrid."

    subgrid_vals = [board[r][c] for r, c in subgrid_coords]
    if value in subgrid_vals:
        return False

    return True


def find_empty_cell(board) -> tuple | None:
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return i, j
    return None
