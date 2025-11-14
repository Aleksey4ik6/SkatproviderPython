import tkinter as tk
from isp_app import ISPAutomationSystem


def main():
    root = tk.Tk()
    app = ISPAutomationSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
