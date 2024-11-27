import tkinter as tk
from tkinter import ttk
from ui_controller import UIController

def main():
    window = tk.Tk()
    window.title("Merchant Bounties Tool")
    window.wm_attributes("-topmost", 1)
    window.geometry("300x600")
    window.configure(bg="#d2d2d2")

    ui_controller = UIController(window)
    window.mainloop()

if __name__ == "__main__":
    main()
