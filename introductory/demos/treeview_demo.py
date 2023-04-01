import tkinter as tk
from tkinter import ttk
from pathlib import Path


def sort(tv: ttk.Treeview, col, parent='', reverse=False):
    sort_index = list()
    for iid in tv.get_children(parent):
        sort_value = tv.set(iid, col) if col != '#0' else iid
        sort_index.append((sort_value, iid))

    sort_index.sort(reverse=reverse)

    for index, (_, iid) in enumerate(sort_index):
        tv.move(iid, parent, index)
        sort(tv, col, parent=iid, reverse=reverse)

    if parent == '':
        tv.heading(
            col,
            command=lambda col=col: sort(tv, col, reverse=not reverse)
        )


def show_directory_stats(*_):
    clicked_path = Path(tv.focus())
    num_children = len(list(clicked_path.iterdir()))
    status.set(
        f'Directory: {clicked_path.name}, {num_children} children'
    )


root = tk.Tk()

paths = Path('').glob('**/*')

tv = ttk.Treeview(
    root, columns=['size', 'modified'], selectmode='none'
)
tv.heading('#0', text='Name')
tv.heading('size', text='Size', anchor='center')
tv.heading('modified', text='Modified', anchor='e')
tv.column('#0', stretch=True)
tv.column('size', width=200)
tv.pack(expand=True, fill='both')

for path in paths:
    meta = path.stat()
    parent = str(path.parent)
    if parent == '.':
        parent = ''
    tv.insert(
        parent,
        'end',
        iid=str(path),
        text=str(path.name),
        values=[meta.st_size, meta.st_mtime]
    )

for cid in ['#0', 'size', 'modified']:
    tv.heading(cid, command=lambda col=cid: sort(tv, col))

status = tk.StringVar()
tk.Label(root, textvariable=status).pack(side=tk.BOTTOM)

tv.bind('<<TreeviewOpen>>', show_directory_stats)
tv.bind('<<TreeviewClose>>', lambda _: status.set(''))

root.mainloop()
