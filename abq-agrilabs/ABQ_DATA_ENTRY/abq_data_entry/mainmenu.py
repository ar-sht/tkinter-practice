"""The Main Menu class for ABQ Data Entry"""
import tkinter as tk
from tkinter import messagebox


class MainMenu(tk.Menu):
    """The Application's main menu"""
    def _event(self, sequence):
        def callback(*_):
            root = self.master.winfo_toplevel()
            root.event_generate(sequence)
        return callback

    def __init__(self, parent, settings, **kwargs):
        super().__init__(parent, **kwargs)
        self.settings = settings

        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='About', command=self.show_about)

        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            label="Select file...",
            command=self._event('<<FileSelect>>')
        )
        file_menu.add_separator()
        file_menu.add_command(
            label='Quit',
            command=self._event('<<FileQuit>>')
        )

        options_menu = tk.Menu(self, tearoff=False)
        options_menu.add_checkbutton(
            label='Autofill Date',
            variable=self.settings['autofill date']
        )
        options_menu.add_checkbutton(
            label='Autofill Sheet data',
            variable=self.settings['autofill sheet data']
        )

        self.add_cascade(label='File', menu=file_menu)
        self.add_cascade(label='Options', menu=options_menu)
        self.add_cascade(label='Help', menu=help_menu)

    def show_about(self):
        """Show the about dialog"""
        about_message = 'ABQ Data Entry'
        about_detail = (
            'by Ari Shtein\n'
            'This is from the book "Python GUI Programming With Tkinter" by Alan D. Moore'
        )
        messagebox.showinfo(
            title='About', message=about_message, detail=about_detail
        )
