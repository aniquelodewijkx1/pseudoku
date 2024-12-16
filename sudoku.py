import logging
import random
from collections import deque

import inquirer
import matplotlib.patches as patches
import numpy as np
from matplotlib import pyplot as plt

from erase import BalancedEraser
from utils import is_valid, find_empty_cell

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ERASER_MAP = {
    "None (Standard)": BalancedEraser,
}


class Sudoku:
    def __init__(self, difficulty: str, type: str):
        self.board = np.zeros((9, 9), dtype=int)

        self.difficulty = difficulty
        self.type = type

        self.subgrids = self.generate_irregular_subgrids() if self.type == 'Irregular Subgrids' else self.generate_subgrids()

        puzzle = self.generate_sudoku()
        self.plot(puzzle, self.subgrids)


    def populate_board(self) -> bool:
        empty_cell = find_empty_cell(self.board)

        if not empty_cell:
            return True

        row, col = empty_cell
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for number in numbers:
            num = {"value": number, "row": row, "col": col}
            if is_valid(board=self.board, subgrids=self.subgrids, num=num):
                self.board[row][col] = number

                if self.populate_board():
                    return True

            self.board[row][col] = 0

        return False


    @staticmethod
    def generate_subgrids() -> dict[int, set]:
        logger.info("Generating subgrids...")

        subgrids = {i: set() for i in range(1, 10)}
        subgrid_starts = []
        for i in range(0, 8, 3):
            for j in range(0, 8, 3):
                subgrid_starts.append((i, j))

        for i, (r, c) in enumerate(subgrid_starts):
            for z in range(0, 3):
                for y in range(0, 3):
                    subgrids[i + 1].add((r + z, c + y))

        return subgrids


    def generate_irregular_subgrids(self) -> dict[int, set[tuple]]:
        """ Generates a dictionary that maps 9 subgrids to a set of coordinates. """
        logger.info("Generating irregular subgrids...")

        subgrids = {i: set() for i in range(1, 10)}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # seed cells for 9 subgrids
        seeds = random.sample([(row, col) for row in range(9) for col in range(9)], 9)
        for i, (row, col) in enumerate(seeds):
            subgrids[i+1].add((row, col))

        print(f'subgrids: {subgrids}')
        # expand each subgrid iteratively
        while any(len(subgrids[subgrid]) < 9 for subgrid in subgrids):
            for s in range(1, 10):
                if len(subgrids[s]) >= 9:
                    continue

                potential = set()
                for (x, y) in subgrids[s]:
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 9 and 0 <= ny < 9 and self.board[nx][ny] == 0:
                            potential.add((nx, ny))
                if not potential:
                    continue

                cell = random.choice(list(potential))
                self.board[cell[0]][cell[1]] = s
                subgrids[s].add(cell)
                print(subgrids)

        return subgrids



    def erase(self):
        eraser_class = ERASER_MAP[self.type]
        eraser = eraser_class(self.board, self.difficulty, self.subgrids)

        puzzle = eraser.erase()

        return puzzle


    @staticmethod
    def plot(grid, subgrids):
        logger.info("Plotting Sudoku...")

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, 9)
        ax.set_ylim(0, 9)
        ax.set_xticks(np.arange(0, 10, 1))
        ax.set_yticks(np.arange(0, 10, 1))
        ax.grid(which='both', color='black', linewidth=1)

        # bold lines around custom subgrids
        for subgrid_id, cells in subgrids.items():
            rows = [cell[0] for cell in cells]
            cols = [cell[1] for cell in cells]

            # determine bounding box
            min_row, max_row = min(rows), max(rows)
            min_col, max_col = min(cols), max(cols)

            # Convert grid coordinates to plot coordinates
            # invert grid coords to plot coords
            lower_left = (min_col, 8 - max_row)
            width = max_col - min_col + 1
            height = max_row - min_row + 1

            # create rectangle patch
            rect = patches.Rectangle(lower_left, width, height,
                                     linewidth=2.5, edgecolor='black', facecolor='none')
            ax.add_patch(rect)

        # Fill in the numbers
        for i in range(9):
            for j in range(9):
                num = grid[i, j]
                if num != 0:
                    ax.text(j + 0.5, 9 - i - 0.5, str(num),
                            fontsize=20, ha='center', va='center')

        # Remove tick labels
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        plt.show()


    def generate_sudoku(self) -> np.ndarray:
        logger.info("Populating board...")
        if self.populate_board():
            puzzle = self.erase()
            return puzzle


if __name__ == '__main__':
    questions = [
        inquirer.List(
            'difficulty',
            message="Difficulty?",
            choices=['Easy', 'Medium', 'Hard', 'Extreme'],
        ),
        inquirer.List(
            'type',
            message="Type?",
            choices=['None (Standard)', 'Irregular Subgrids'],
        ),
    ]

    answers = inquirer.prompt(questions)
    sudoku = Sudoku(
        difficulty=answers['difficulty'].lower(),
        type=answers['type'])
