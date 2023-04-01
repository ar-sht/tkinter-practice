import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from . import views as v
from . import models as m
from .mainmenu import MainMenu


class Application(tk.Tk):
    """Application root window"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.withdraw()
        if not self._show_login():
            self.destroy()
            return
        self.deiconify()

        self.model = m.CSVModel()

        self.settings_model = m.SettingsModel()
        self._load_settings()

        self.title("ABQ Data Entry Application")
        self.columnconfigure(0, weight=1)

        self.settings = {
            'autofill date': tk.BooleanVar(),
            'autofill sheet data': tk.BooleanVar()
        }

        menu = MainMenu(self, self.settings)
        self.config(menu=menu)
        event_callbacks = {
            '<<FileSelect>>': self._on_file_select,
            '<<FileQUit>>': lambda _: self.quit(),
            '<<ShowRecordlist>>': self._show_recordlist,
            '<<NewRecord>>': self._new_record,
        }
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        ttk.Label(
            self, text="ABQ Data Entry Application",
            font=("TkDefaultFont", 16)
        ).grid(row=0)

        self.notebook = ttk.Notebook(self)
        self.notebook.enable_traversal()
        self.notebook.grid(row=1, padx=10, sticky='nsew')

        self.recordform = v.DataRecordForm(self, self.model, self.settings)
        self.recordform.bind('<<SaveRecord>>', self._on_save)
        self.notebook.add(self.recordform, text='Entry Form')

        self.recordlist = v.RecordList(self)
        self.notebook.insert(0, self.recordlist, text='Records')
        self._populate_recordlist()
        self.recordlist.bind('<<OpenRecord>>', self._open_record)

        self.status = tk.StringVar()
        ttk.Label(
            self, textvariable=self.status
        ).grid(sticky=(tk.W + tk.E), row=2, padx=10)

        self._records_saved = 0

        self._show_recordlist()

    def _on_save(self, *_):
        """Handles save button clicks"""
        errors = self.recordform.get_errors()
        if errors:
            message = "Cannot save record"
            detail = (
                "The following fields have errors: "
                "\n  * {}".format(
                    '\n  * '.join(errors.keys())
                )
            )
            messagebox.showerror(
                title='Error',
                message=message,
                detail=detail
            )
            return False
        data = self.recordform.get()

        rownum = self.recordform.current_record

        self.model.save_record(data, rownum)
        self._records_saved += 1
        self.status.set(
            f"{self._records_saved} records saved this session"
        )
        self.recordform.reset()
        self._populate_recordlist()

    def _on_file_select(self, *_):
        """Handle the file->select action"""
        filename = filedialog.asksaveasfilename(
            title='Select the target file for saving records',
            defaultextension='.csv',
            filetypes=[('CSV', '*.csv *.CSV')]
        )

        if filename:
            self.model = m.CSVModel(filename=filename)
            self._populate_recordlist()

    def _show_login(self):
        error = ''
        title = 'Login to ABQ Data Entry'
        while True:
            login = v.LoginDialog(self, title, error)
            if not login.result:
                return False
            username, password = login.result
            if self._simple_login(username, password):
                return True
            error = 'Login Failed'

    def _load_settings(self):
        """Load settings into our self.settings dict"""
        vartypes = {
            'bool': tk.BooleanVar,
            'str': tk.StringVar,
            'int': tk.IntVar,
            'float': tk.DoubleVar,
        }
        self.settings = dict()
        for key, data in self.settings_model.fields.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])
        for var in self.settings.values():
            var.trace_add('write', self._save_settings)

    def _save_settings(self, *_):
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
        self.settings_model.save()

    def _show_recordlist(self, *_):
        self.notebook.select(self.recordlist)

    def _populate_recordlist(self):
        try:
            rows = self.model.get_all_records()
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem reading file',
                detail=str(e)
            )
        else:
            self.recordlist.populate(rows)

    def _new_record(self, *_):
        self.recordform.load_record(None)
        self.notebook.select(self.recordform)

    def _open_record(self, *_):
        """Open the selected id from recordlist in the recordform"""
        rowkey = self.recordlist.selected_id
        try:
            record = self.model.get_record(rowkey)
        except Exception as e:
            messagebox.showerror(
                title='Error', message='Problem reading file', detail=str(e)
            )
        else:
            self.recordform.load_record(rowkey, record)
            self.notebook.select(self.recordform)

    @staticmethod
    def _simple_login(username, password):
        return username == 'abq' and password == 'Flowers'
