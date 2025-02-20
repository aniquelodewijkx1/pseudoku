import argparse
import copy
import logging
import random
from abc import ABC
from yaspin import yaspin
import inquirer
import numpy as np
from pydantic import BaseModel, conint

from plot import plot
from subgrid import Subgrid, RegularSubgrid, HyperSubgrid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

LEVEL_MAP = {
    'easy': 36,
    'medium': 52,
    'hard': 56,
    'extreme': 60
}

class Number(BaseModel):
    value: conint(ge=1, le=16)
    row: conint(ge=0, le=15)
    col: conint(ge=0, le=15)


class Eraser(ABC):

    @staticmethod
    def erase(sudoku: "Sudoku"):
        """ Abstract method to erase numbers from full sudoku to create a puzzle. """
        pass


class BalancedEraser(Eraser):
    """ Erases a balanced number of cells from each subgrid."""
    @staticmethod
    def erase(sudoku: "Sudoku"):
        board, difficulty = sudoku.board, sudoku.difficulty
        subgrid = RegularSubgrid(sudoku.size).get_subgrid()

        num_to_remove = LEVEL_MAP[difficulty]
        remove_per_cell = num_to_remove // sudoku.size
        leftover = num_to_remove % sudoku.size

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
    def __init__(self, size: int, difficulty: str, subgrids: list[Subgrid]):
        self.answer = None
        self.board = np.zeros((size, size), dtype=int)
        self.size = size
        self.difficulty = difficulty
        self.subgrids = [subgrid.get_subgrid() for subgrid in subgrids]


    def find_empty_cell(self) -> tuple | None:
        """ Find cell without value. """
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return i, j
        return None


    def try_fill_cell(self, row: int, col: int) -> bool:
        """ Fill an empty cell with a value and check validity. """
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
        """ Checks if number is present in same row, column, or subgrid(s). """
        if num.value in self.board[num.row]:
            return False

        if num.value in self.board[:, num.col]:
            return False

        for subgrid in self.subgrids:
            subgrid_id = subgrid[num.row, num.col]
            if subgrid_id == 0:
                continue

            rows, cols =  np.where(subgrid == subgrid_id)
            cellmates = list(zip(rows, cols))
            subgrid_vals = [self.board[r][c] for r, c in cellmates]
            if num.value in subgrid_vals:
                return False

        return True


    def has_unique_solution(self) -> bool:
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

            for subgrid in self.subgrids:
                subgrid_id = subgrid[num.row, num.col]
                rows, cols = np.where(subgrid == subgrid_id)
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


    def generate_sudoku(self):
        with yaspin(text="Generating sudoku...", color="yellow") as spinner:
            if self.populate_board():
                spinner.ok("✔")
                self.answer = copy.deepcopy(self.board)
                with yaspin(text="Making sure there's a single solution...", color="light_red") as spinner2:
                    BalancedEraser.erase(self)
                spinner2.ok("✔")
        return self.board


def get_cli_args():
    parser = argparse.ArgumentParser(description="Pseudoku CLI")
    parser.add_argument('-d', '--difficulty', type=str, choices=['easy', 'medium', 'hard', 'extreme'],
                        help='Difficulty level')
    parser.add_argument('-t', '--type', type=str, choices=['standard', 'hypergrid'],
                        help='Sudoku type')
    parser.add_argument('-s', '--size', type=int, choices=[4, 9, 16],
                        help='Grid size')
    return parser.parse_args()


def get_interactive_args(cli_args):

    questions = [
        inquirer.List(
            'difficulty',
            message="Difficulty?",
            choices=['easy', 'medium', 'hard', 'extreme'],
            default=cli_args.difficulty if cli_args.difficulty else 'easy'
        ),
        inquirer.List(
            'type',
            message="Type?",
            choices=['standard', 'hypergrid'],
            default=cli_args.type if cli_args.type else 'standard'
        ),
        inquirer.List(
            'size',
            message="Grid size?",
            choices=[4, 9, 16],
            default=cli_args.size if cli_args.size else 9
        )
    ]
    return inquirer.prompt(questions)


def main():
    cli_args = get_cli_args()

    # only 'difficulty' is a required flag
    if cli_args.difficulty is not None:
        difficulty = cli_args.difficulty
        grid_type = 'standard' if not cli_args.size else cli_args.type
        size = 9 if not cli_args.size else cli_args.size

    else:
        answers = get_interactive_args(cli_args)
        difficulty = answers['difficulty']
        grid_type = answers['type']
        size = answers['size']

    match grid_type:
        case 'standard':
            subgrids = [RegularSubgrid(size=size)]
        case 'hypergrid':
            subgrids = [RegularSubgrid(size=size), HyperSubgrid(size=size)]
        case _:
            raise RuntimeError('Unknown grid type')

    sudoku = Sudoku(
        size=size,
        difficulty=difficulty,
        subgrids=subgrids)

    sudoku.generate_sudoku()

    plot(subgrids, sudoku.board, sudoku.answer)


if __name__ == '__main__':
    main()
