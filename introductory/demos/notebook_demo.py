import tkinter as tk
from tkinter import ttk

root = tk.Tk()

notebook = ttk.Notebook(root)
notebook.grid(sticky='nsew')

banana_facts = [
  'Banana trees are of the genus Musa.',
  'Bananas are technically berries.',
  'All bananas contain small amounts of radioactive potassium.'
  'Bananas are used in paper and textile manufacturing.'
]
plantain_facts = [
  'Plantains are also of genus Musa.',
  'Plantains are starchier and less sweet than bananas',
  'Plantains are called "Cooking Bananas" since they are'
  ' rarely eaten raw.'
]

b_label = ttk.Label(notebook, text='\n\n'.join(banana_facts))
p_label = ttk.Label(notebook, text='\n\n'.join(plantain_facts))

notebook.add(b_label, text='Bananas', padding=20)
notebook.add(p_label, text='Plantains', padding=20)

notebook.tab(0, underline=0)
notebook.tab(1, underline=0)
notebook.enable_traversal()

notebook.select(0)
notebook.select(p_label)

root.mainloop()
