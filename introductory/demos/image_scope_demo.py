import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.smile = tk.PhotoImage(file='smile.gif')
        tk.Label(self, image=self.smile).pack()


App().mainloop()
