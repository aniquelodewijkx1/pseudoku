import numpy as np
from matplotlib import pyplot as plt


class Sudoku:
    def __init__(self):
        self.board = np.zeros((9, 9), dtype=int)
        self.generate_sudoku()


    def is_valid(self, row, col, num):
        """ Checks if number is present in same row, column, or subgrid. """
        subgrid_row = row // 3
        subgrid_col = col // 3

        if num in self.board[row]:
            return False
        if num in [self.board[i][col] for i in range(9)]:
            return False

        subgrid = self.board[
                  subgrid_row * 3: (subgrid_row + 1) * 3,
                  subgrid_col * 3: (subgrid_col + 1) * 3
                  ]

        if np.any(subgrid == num):
            return False

        return True


    def find_empty_cell(self) -> tuple | None:
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None


    def populate_board(self) -> bool:
        empty_cell = self.find_empty_cell()

        if not empty_cell:
            return True

        row, col = empty_cell

        for number in range(1, 10):
            if self.is_valid(row, col, number):
                self.board[row][col] = number

                if self.populate_board():
                    return True

            self.board[row][col] = 0

        return False

    def plot(self):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, 9)
        ax.set_ylim(0, 9)
        ax.set_xticks(np.arange(0, 10, 1))
        ax.set_yticks(np.arange(0, 10, 1))
        ax.grid(which='both', color='black', linewidth=1)

        # Add thicker lines for subgrids
        for i in range(0, 10):
            if i % 3 == 0:
                ax.axhline(i, color='black', linewidth=2.5)
                ax.axvline(i, color='black', linewidth=2.5)

        # Fill numbers
        for i in range(9):
            for j in range(9):
                num = self.board[i, j]
                if num != 0:
                    ax.text(j + 0.5, 9 - i - 0.5, str(num),
                            fontsize=20, ha='center', va='center')

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        plt.show()


    def generate_sudoku(self):
        if self.populate_board():
            # start taking values out
            return self.board


if __name__ == '__main__':
    sudoku = Sudoku()
    sudoku.generate_sudoku()
    sudoku.plot()
