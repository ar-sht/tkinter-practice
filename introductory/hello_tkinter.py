#!/venv/bin/python3
"""Hello world application for Tkinter"""
import tkinter as tk

root = tk.Tk()

label = tk.Label(root, text="Hello World")
label.pack()

button = tk.Button(root, text="I'm a button!")
button.pack()

label2 = tk.Label(root, text="That button does nothing")
label2.pack()

root.mainloop()
