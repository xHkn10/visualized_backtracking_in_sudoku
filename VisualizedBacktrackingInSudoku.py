import os
import random
import sys
import tkinter as tk
import tkinter.messagebox

import customtkinter as ctk

WIDTH = 630 + 3
HEIGHT = 630 + 30 + 3
curr_board = [[0 for _ in range(9)] for _ in range(9)]


class App(ctk.CTk):
    root: ctk.CTk

    def __init__(self, title="Visualized Backtracking In Sudoku", size=(WIDTH, HEIGHT), **kwargs):
        super().__init__(**kwargs)
        App.root = self
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(size[0], size[1])

        self.board_frame = BoardFrame(self)
        self.button_frame = ButtonFrame(self)

        self.entries: list[list[ctk.CTkEntry]] = [[None for _ in range(9)] for _ in range(9)]

        for y in range(9):
            for x in range(9):
                entry = NumEntry(self.board_frame, font=("Helvetica", 55), text_color="white", fg_color="#1a1824")
                entry.bind("<KeyPress>", command=lambda event, y=y, x=x: self.navigate(event, y, x))
                entry.bind("<Return>", command=lambda event: self.enter())
                self.entries[y][x] = entry
                entry.grid(row=y, column=x)

        self.mainloop()

    def navigate(self, event, y, x):
        if y != 0 and (event.keysym == "w" or event.keysym == "Up"):
            self.entries[y - 1][x].focus_set()
            return
        if x != 0 and (event.keysym == "a" or event.keysym == "Left"):
            self.entries[y][x - 1].focus_set()
            return
        if y != 8 and (event.keysym == "s" or event.keysym == "Down"):
            self.entries[y + 1][x].focus_set()
            return
        if x != 8 and (event.keysym == "d" or event.keysym == "Right"):
            self.entries[y][x + 1].focus_set()

    def enter(self):
        global curr_board

        for y in range(9):
            for x in range(9):
                s = self.entries[y][x].get().strip()
                if s.isalpha():
                    clear()
                    tk.messagebox.showerror(title="Error", message="Invalid input!")
                    return
                if s == "":
                    curr_board[y][x] = 0
                elif 0 <= int(s) <= 9:
                    curr_board[y][x] = int(s)
                else:
                    clear()
                    tk.messagebox.showerror(title="Error", message="Invalid sudoku!")
                    return

        if not valid(curr_board):
            tk.messagebox.showerror(title="Error", message="Invalid sudoku!")
            return

        solve()


class BoardFrame(ctk.CTkFrame):
    def __init__(self, master, width=WIDTH, height=HEIGHT - 100, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.pack()


class ButtonFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.clear_button = ctk.CTkButton(self, text="Clear", corner_radius=10, command=clear, fg_color="#2d2069",
                                          width=WIDTH // 3)
        self.randomize_button = ctk.CTkButton(self, text="Random", corner_radius=10, command=randomize,
                                              fg_color="#2d2069", width=WIDTH // 3)
        self.restart_button = ctk.CTkButton(self, text="Restart", corner_radius=10, command=restart, fg_color="#2d2069",
                                            width=WIDTH // 3)
        self.slider = ctk.CTkSlider(self, from_=1, to=200)
        self.clear_button.pack(side=ctk.LEFT, fill="y")
        self.randomize_button.pack(side=ctk.RIGHT, fill="y")
        self.restart_button.pack()
        self.slider.pack(side=ctk.BOTTOM)
        self.pack(side=ctk.BOTTOM, fill="both")


class NumEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=master.cget("width") // 9, height=master.cget("height") // 9, **kwargs)


def restart():
    App.root.destroy()
    os.system("python VisualizedBacktrackingInSudoku.py")
    sys.exit()


def clear():
    global curr_board
    for y in range(9):
        for x in range(9):
            curr_board[y][x] = 0
            curr_entry: ctk.CTkEntry = App.root.entries[y][x]
            curr_entry.configure(state="normal", fg_color="#1a1824")
            curr_entry.delete(0, tk.END)

    try:
        raise TerminateRecursion
    except TerminateRecursion:
        pass


def randomize():
    clear()
    global curr_board
    for y in range(9):
        for x in range(9):
            if random.randint(1, 9) != 9: continue
            n = random.randint(1, 9)
            if can_put(n, y, x):
                curr_entry: ctk.CTkEntry = App.root.entries[y][x]
                curr_board[y][x] = n
                curr_entry.delete(0, ctk.END)
                curr_entry.insert(0, n)
                curr_entry.configure(state="readonly")
                curr_entry.configure(fg_color="#3b316b")


class TerminateRecursion(Exception):
    pass


def solve():
    global curr_board
    try:
        recurse(0, 0, zero_counter(curr_board))
    except TerminateRecursion:
        pass


def recurse(y, x, zeros):
    speed = 1000 // int(App.root.button_frame.slider.get())
    global curr_board
    if zeros == 0:
        raise TerminateRecursion

    if x == 9:
        recurse(y + 1, 0, zeros)
        return

    if curr_board[y][x] != 0:
        recurse(y, x + 1, zeros)
        return
    # shuffling for indeterministic results (otherwise same inputs always give the same results)
    ns = list(range(1, 10))
    random.shuffle(ns)
    for n in ns:
        if can_put(n, y, x):
            curr_board[y][x] = n
            curr_entry: ctk.CTkEntry = App.root.entries[y][x]
            curr_entry.configure(fg_color="#1c0c6b")
            curr_entry.delete(0, ctk.END)
            curr_entry.insert(0, n)
            App.root.update()
            App.root.after(speed)
            curr_entry.configure(fg_color="#1a1824")
            App.root.update()
            recurse(y, x + 1, zeros - 1)
            curr_board[y][x] = 0
            curr_entry.delete(0, ctk.END)
            App.root.update()


def can_put(n, y, x) -> bool:
    global curr_board
    for i in range(9):
        if curr_board[y][i] == n:
            return False

    for j in range(9):
        if curr_board[j][x] == n:
            return False

    y0 = (y // 3) * 3
    x0 = (x // 3) * 3

    for addY in range(0, 3):
        for addX in range(0, 3):
            if curr_board[y0 + addY][x0 + addX] == n:
                return False

    return True


def zero_counter(board: list[list[int]]) -> int:
    ans = 0
    for y in range(9):
        for x in range(9):
            if board[y][x] == 0:
                ans += 1
    return ans


# check validness of the board using bit manipulation
def valid(board: list[list[int]]) -> bool:
    for row in board:
        bits = 2 ** 9
        for n in row:
            if n == 0: continue
            if bits & (1 << (n - 1)):
                return False
            bits |= (1 << (n - 1))

    for x in range(9):
        bits = 2 ** 9
        for y in range(9):
            n = board[y][x]
            if n == 0: continue
            if bits & (1 << (n - 1)):
                return False
            bits |= (1 << (n - 1))

    for y0, x0 in zip((0, 0, 0, 3, 3, 3, 6, 6, 6), (0, 3, 6, 0, 3, 6, 0, 3, 6)):
        bits = 2 ** 9
        for addY in range(3):
            for addX in range(3):
                n = board[y0 + addY][x0 + addX]
                if n == 0: continue
                if bits & (1 << (n - 1)):
                    return False
                bits |= (1 << (n - 1))

    return True


if __name__ == '__main__':
    App()
