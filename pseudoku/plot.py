import numpy as np
import tkinter as tk

from subgrid import Subgrid, RegularSubgrid, HyperSubgrid

def plot(subgrids: list[Subgrid], board_values: np.ndarray, correct_values: np.ndarray):
    print('board values')
    print(board_values)
    print('correct values')
    print(correct_values)
    # Get the regular subgrid mapping.
    grid_ids = None
    for sub in subgrids:
        if isinstance(sub, RegularSubgrid):
            grid_ids = sub.get_subgrid()
            break
    if grid_ids is None:
        raise ValueError("No RegularSubgrid found in subgrids.")

    # Create the main window and a canvas for drawing.
    root = tk.Tk()
    root.title("Pseudoku")
    cell_size = 50
    rows, cols = board_values.shape
    canvas_width = cols * cell_size
    canvas_height = rows * cell_size

    # Create a canvas with a white background.
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    # Dictionary to hold the Entry widgets.
    entries = {}

    # Create the grid of Entry widgets on the canvas.
    for i in range(rows):
        for j in range(cols):
            e = tk.Entry(root, width=2, font=("Helvetica", 20), justify='center',
                         bg="white", fg="black", relief="flat", bd=0, highlightthickness=0)
            # Place the entry widget in the center of its cell.
            x = j * cell_size + cell_size / 2
            y = i * cell_size + cell_size / 2
            canvas.create_window(x, y, window=e, width=cell_size - 10, height=cell_size - 10)
            if board_values[i, j] != 0:  # assuming 0 represents an empty cell
                e.insert(0, str(board_values[i, j]))
                # For prefilled cells, ensure disabled colors are white by default.
                e.config(state='disabled', disabledforeground='black', disabledbackground='white')
            entries[(i, j)] = e

    # Draw thin grid lines for every cell.
    for i in range(rows + 1):
        canvas.create_line(0, i * cell_size, canvas_width, i * cell_size, fill="gray", width=1)
    for j in range(cols + 1):
        canvas.create_line(j * cell_size, 0, j * cell_size, canvas_height, fill="gray", width=1)

    # Draw thicker lines between subgrids based on the regular grid_ids array.
    # Vertical thick lines:
    for i in range(rows):
        for j in range(cols - 1):
            if grid_ids[i, j] != grid_ids[i, j + 1]:
                x = (j + 1) * cell_size
                canvas.create_line(x, i * cell_size, x, (i + 1) * cell_size, fill="black", width=3)
    # Horizontal thick lines:
    for i in range(rows - 1):
        for j in range(cols):
            if grid_ids[i, j] != grid_ids[i + 1, j]:
                y = (i + 1) * cell_size
                canvas.create_line(j * cell_size, y, (j + 1) * cell_size, y, fill="black", width=3)

    # --- Additional plotting for HyperSubgrid(s) ---
    # For each HyperSubgrid, shade cells that are in its region and already nonempty.
    for sub in subgrids:
        if isinstance(sub, HyperSubgrid):
            hyper_mapping = sub.get_subgrid()
            for i in range(rows):
                for j in range(cols):
                    # Here, a nonzero in hyper_mapping indicates the cell is part of the hyper region.
                    # Shade the cell only if board_values is nonzero.
                    if hyper_mapping[i, j] != 0:
                        entry = entries[(i, j)]
                        entry.config(bg="palegreen")
                        if entry.cget("state") == "disabled":
                            entry.config(disabledbackground="palegreen")
    # -----------------------------------------------------

    # Label to display messages in the same window.
    message_label = tk.Label(root, text="", font=("Helvetica", 14))
    message_label.pack(pady=10)

    # Helper function to fade the text color from red to black.
    def fade_font(entry, colors=["#FF0000", "#CC0000", "#990000", "#660000", "#330000", "#000000"], index=0):
        if index < len(colors):
            entry.config(fg=colors[index])
            entry.after(300, lambda: fade_font(entry, colors, index+1))

    # Button callback to check the solution.
    def check_solution():
        error_found = False
        filled_all = True
        for (i, j), entry in entries.items():
            # Skip disabled (prefilled) cells.
            if str(entry.cget("state")) == "disabled":
                continue
            val = entry.get().strip()
            if val == "":
                filled_all = False
                continue
            try:
                user_val = int(val)
            except ValueError:
                error_found = True
                fade_font(entry)
                continue
            if user_val != correct_values[i, j]:
                error_found = True
                fade_font(entry)
        if error_found:
            message_label.config(text="At least one cell is incorrect.", fg="red")
        elif not filled_all:
            message_label.config(text="Perfect so far!", fg="blue")
        else:
            message_label.config(text="Congratulations!", fg="green")

    check_btn = tk.Button(root, text="Check", command=check_solution, font=("Helvetica", 14))
    check_btn.pack(pady=10)

    root.mainloop()