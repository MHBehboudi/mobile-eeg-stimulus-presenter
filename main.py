# main.py
import tkinter as tk
from experiment import Experiment

if __name__ == "__main__":
    root = tk.Tk()
    app = Experiment(root)
    root.mainloop()
