import numpy as np
from matplotlib import pyplot as plt, patches

from pseudoku.subgrid import Subgrid, RegularSubgrid, HyperSubgrid


def plot(size: int, subgrids: list[Subgrid], sudoku: np.ndarray):
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_xticks(np.arange(0, size + 1, 1))
    ax.set_yticks(np.arange(0, size + 1, 1))
    ax.grid(which='both', color='black', linewidth=1)

    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # draw subgrid boundaries
    for subgrid in subgrids:
        if isinstance(subgrid, RegularSubgrid):
                subgrid_ids = np.unique(subgrid)
                for subgrid_id in subgrid_ids:
                    # find coordinates of the cells in current subgrid
                    rows, cols = np.where(subgrid == subgrid_id)
                    if len(rows) > 0 and len(cols) > 0:
                        # determine bounding box for subgrid
                        min_row, max_row = rows.min(), rows.max()
                        min_col, max_col = cols.min(), cols.max()

                        # convert grid coordinates to plot coordinates
                        lower_left = (min_col, size - 1 - max_row)
                        width = max_col - min_col + 1
                        height = max_row - min_row + 1

                        # rectangle patch for subgrid boundary
                        rect = patches.Rectangle(lower_left, width, height,
                                                 linewidth=2.5, edgecolor='black', facecolor='none')
                        ax.add_patch(rect)

        if isinstance(subgrid, HyperSubgrid):
            import tkinter as tk
            import numpy as np

            def create_sudoku_board(board, subgrid_ids):
                root = tk.Tk()
                root.title("Sudoku")

                rows, cols = board.shape
                entries = {}

                # Adjust cell size, fonts, etc., as needed
                for i in range(rows):
                    for j in range(cols):
                        e = tk.Entry(root, width=2, font=("Helvetica", 20), justify='center')
                        e.grid(row=i, column=j, padx=5, pady=5)
                        if board[i, j] != 0:  # Assuming 0 represents an empty cell
                            e.insert(0, str(board[i, j]))
                            e.config(state='disabled', disabledforeground='black')
                        entries[(i, j)] = e


                # Optionally, add a button to validate the solution
                def check_solution():
                    user_solution = np.zeros((rows, cols), dtype=int)
                    for (i, j), entry in entries.items():
                        try:
                            user_solution[i, j] = int(entry.get())
                        except ValueError:
                            user_solution[i, j] = 0  # or handle invalid input as needed
                    print("User solution:")
                    print(user_solution)
                    # Here, you could add code to check the validity of the solution


                check_btn = tk.Button(root, text="Check", command=check_solution)
                check_btn.grid(row=rows, column=0, columnspan=cols, pady=10)

                root.mainloop()


            # Example usage:
            # Generate a sample 4x4 board (use your generator for a larger board)
            board = np.array([
                [1, 0, 0, 2],
                [0, 2, 1, 0],
                [0, 1, 2, 0],
                [2, 0, 0, 1]
            ])
            subgrid_ids = np.array([
                [1, 1, 2, 2],
                [1, 1, 2, 2],
                [3, 3, 4, 4],
                [3, 3, 4, 4]
            ])
            create_sudoku_board(board, subgrid_ids)


    # fill in numbers from grid
    for i in range(size):
        for j in range(size):
            num = board[i, j]
            if num != 0:
                ax.text(j + 0.5, size - i - 0.5, str(num),
                        fontsize=20, ha='center', va='center')

    plt.show()