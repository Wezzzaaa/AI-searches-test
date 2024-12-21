import tkinter as tk
from tkinter import messagebox
import time
from collections import deque
import heapq

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    return True

def find_empty_cell_with_fewest_options(board):
    min_options, best_cell = 10, None
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                options = sum(1 for num in range(1, 10) if is_valid(board, row, col, num))
                if options < min_options:
                    min_options, best_cell = options, (row, col)
                    if min_options == 1:
                        return best_cell
    return best_cell

def deep_copy_board(board):
    return [row[:] for row in board]

def bfs_sudoku_solver(board, step_by_step=False):
    queue = deque([board])
    while queue:
        current_board = queue.popleft()
        empty_cell = find_empty_cell_with_fewest_options(current_board)
        if not empty_cell:
            return current_board
        row, col = empty_cell
        for num in range(1, 10):
            if is_valid(current_board, row, col, num):
                new_board = deep_copy_board(current_board)
                new_board[row][col] = num
                queue.append(new_board)
                if step_by_step:
                    yield new_board
    return None

def dfs_sudoku_solver(board, step_by_step=False):
    def dfs_recursive(board):
        empty_cell = find_empty_cell_with_fewest_options(board)
        if not empty_cell:
            return board
        row, col = empty_cell
        for num in range(1, 10):
            if is_valid(board, row, col, num):
                board[row][col] = num
                if dfs_recursive(board):
                    return board
                board[row][col] = 0
        return None
    if step_by_step:
        def dfs_step_by_step(board):
            empty_cell = find_empty_cell_with_fewest_options(board)
            if not empty_cell:
                yield board
            row, col = empty_cell
            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    board[row][col] = num
                    yield board
                    yield from dfs_step_by_step(board)
                    board[row][col] = 0
        return dfs_step_by_step(deep_copy_board(board))
    return dfs_recursive(deep_copy_board(board))

def ucs_sudoku_solver(board, step_by_step=False):
    pq = []
    heapq.heappush(pq, (0, board))
    while pq:
        cost, current_board = heapq.heappop(pq)
        empty_cell = find_empty_cell_with_fewest_options(current_board)
        if not empty_cell:
            return current_board
        row, col = empty_cell
        for num in range(1, 10):
            if is_valid(current_board, row, col, num):
                new_board = deep_copy_board(current_board)
                new_board[row][col] = num
                heapq.heappush(pq, (cost + 1, new_board))
                if step_by_step:
                    yield new_board
    return None

def solve_sudoku(board, method="dfs", step_by_step=False):
    if method == "bfs":
        return bfs_sudoku_solver(deep_copy_board(board), step_by_step)
    elif method == "ucs":
        return ucs_sudoku_solver(deep_copy_board(board), step_by_step)
    elif method == "dfs":
        return dfs_sudoku_solver(deep_copy_board(board), step_by_step)
    else:
        raise ValueError("Invalid method. Choose 'dfs', 'bfs', or 'ucs'.")

def create_gui():
    root = tk.Tk()
    root.title("Sudoku Solver")
    root.geometry("600x700")
    root.configure(bg="#f7f7f7")

    entries = [[None for _ in range(9)] for _ in range(9)]
    timer_label = tk.Label(root, text="Time: 0.00 seconds", font=("Arial", 14), bg="#f7f7f7")
    timer_label.grid(row=11, column=0, columnspan=9, pady=10)

    predefined_board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    def load_predefined_board():
        for row in range(9):
            for col in range(9):
                value = predefined_board[row][col]
                entries[row][col].delete(0, tk.END)
                if value != 0:
                    entries[row][col].insert(0, str(value))
                    entries[row][col].config(state="readonly", bg="#e0e0e0")
                else:
                    entries[row][col].config(state="normal", bg="white")

    def get_board_from_entries():
        board = []
        for row in range(9):
            row_values = []
            for col in range(9):
                value = entries[row][col].get()
                row_values.append(int(value) if value.isdigit() else 0)
            board.append(row_values)
        return board

    def update_entries_with_solution(board):
        for row in range(9):
            for col in range(9):
                entries[row][col].config(state="normal", bg="white")
                entries[row][col].delete(0, tk.END)
                entries[row][col].insert(0, str(board[row][col]) if board[row][col] != 0 else "")
                entries[row][col].config(state="readonly", bg="#e0e0e0")

    def solve():
        board = get_board_from_entries()
        method = method_var.get()
        if method not in {"dfs", "bfs", "ucs"}:
            messagebox.showerror("Error", "Invalid solving method selected!")
            return

        start_time = time.time()

        def update_timer():
            elapsed_time = time.time() - start_time
            timer_label.config(text=f"Time: {elapsed_time:.2f} seconds")
            root.after(100, update_timer)

        update_timer()

        step_by_step = step_var.get()
        solver = solve_sudoku(board, method, step_by_step=True)

        def animate_solution():
            try:
                step = next(solver)
                update_entries_with_solution(step)
                root.after(speed_slider.get(), animate_solution)
            except StopIteration:
                messagebox.showinfo("Success", "Sudoku solved successfully!")

        animate_solution()

    def restart():
        load_predefined_board()
        timer_label.config(text="Time: 0.00 seconds")

    def clear():
        for row in range(9):
            for col in range(9):
                entries[row][col].delete(0, tk.END)
                entries[row][col].config(state="normal", bg="white")
        timer_label.config(text="Time: 0.00 seconds")

    for row in range(9):
        for col in range(9):
            entry = tk.Entry(root, width=4, font=("Arial", 18), justify="center", bd=2, relief="solid")
            entry.grid(row=row, column=col, padx=5, pady=5)
            entries[row][col] = entry

    load_predefined_board()

    method_var = tk.StringVar(value="dfs")
    step_var = tk.BooleanVar(value=False)

    method_frame = tk.Frame(root, bg="#f7f7f7")
    method_frame.grid(row=9, column=0, columnspan=9, pady=10, sticky="ew")

    method_label = tk.Label(method_frame, text="Select Method:", font=("Arial", 12), bg="#f7f7f7")
    method_label.grid(row=0, column=0, padx=10)

    method_menu = tk.OptionMenu(method_frame, method_var, "dfs", "bfs", "ucs")
    method_menu.config(font=("Arial", 12))
    method_menu.grid(row=0, column=1)

    step_checkbox = tk.Checkbutton(method_frame, text="Step-by-Step", variable=step_var, font=("Arial", 12), bg="#f7f7f7")
    step_checkbox.grid(row=0, column=2, padx=10)

    speed_label = tk.Label(method_frame, text="Speed (ms):", font=("Arial", 12), bg="#f7f7f7")
    speed_label.grid(row=0, column=3, padx=10)

    speed_slider = tk.Scale(method_frame, from_=50, to=1000, orient="horizontal", font=("Arial", 12), length=200)
    speed_slider.set(200)
    speed_slider.grid(row=0, column=4)

    control_frame = tk.Frame(root, bg="#f7f7f7")
    control_frame.grid(row=10, column=0, columnspan=9, pady=10, sticky="ew")

    solve_button = tk.Button(control_frame, text="Solve", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=solve)
    solve_button.grid(row=0, column=0, padx=10, pady=10)

    restart_button = tk.Button(control_frame, text="Restart", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=restart)
    restart_button.grid(row=0, column=1, padx=10, pady=10)

    clear_button = tk.Button(control_frame, text="Clear", font=("Arial", 12, "bold"), bg="#FFC107", fg="white", command=clear)
    clear_button.grid(row=0, column=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
