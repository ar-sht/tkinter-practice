import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import Dialog
from datetime import datetime
from . import widgets as w


class DataRecordForm(ttk.Frame):
    """The input form for our widgets"""

    def _add_frame(self, label, cols=3):
        """Add a LabelFrame to the form"""
        frame = ttk.LabelFrame(self, text=label)  # create the frame with whole form as parent and label passed in
        frame.grid(sticky=(tk.W + tk.E))  # add frame to form
        # each column should expand evenly
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def _on_save(self):
        self.event_generate('<<SaveRecord>>')

    def reset(self):
        """Resets the form entries"""
        lab = self._vars['Lab'].get()
        time = self._vars['Time'].get()
        technician = self._vars['Technician'].get()
        try:
            plot = self._vars['Plot'].get()
        except tk.TclError:
            plot = ''
        plot_values = (
            self._vars['Plot'].label_widget.input.cget('values')
        )

        for var in self._vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set('')

        if self.settings['autofill date'].get():
            current_date = datetime.today().strftime('%Y-%m-%d')
            self._vars['Date'].set(current_date)
            self._vars['Time'].label_widget.input.focus()

        if (
                self.settings['autofill sheet data'].get() and
                plot not in ('', 0, plot_values[-1])
        ):
            self._vars['Lab'].set(lab)
            self._vars['Time'].set(time)
            self._vars['Technician'].set(technician)
            next_plot_index = plot_values.index(str(plot)) + 1
            self._vars['Plot'].set(plot_values[next_plot_index])
            self._vars['Seed Sample'].label_widget.input.focus()

    def get(self):
        data = dict()
        fault = self._vars['Equipment Fault'].get()
        for key, variable in self._vars.items():
            if fault and key in ['Light', 'Humidity', 'Temperature']:
                data[key] = ''
            else:
                try:
                    data[key] = variable.get()
                except tk.TclError:
                    message = f'Error in field: {key}. Data was not saved!'
                    raise ValueError(message)
        return data

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for key, var in self._vars.items():
            inp = var.label_widget.input
            error = var.label_widget.error
            if hasattr(inp, 'trigger_focusout_validation'):
                inp.trigger_focusout_validation()
            if error.get():
                errors[key] = error.get()
        return errors

    def __init__(self, parent, model, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = model
        self.settings = settings
        fields = self.model.fields

        # holding all our data in tk vars
        self._vars = {
            'Date': tk.StringVar(),
            'Time': tk.StringVar(),
            'Technician': tk.StringVar(),
            'Lab': tk.StringVar(),
            'Plot': tk.IntVar(),
            'Seed Sample': tk.StringVar(),
            'Humidity': tk.DoubleVar(),
            'Light': tk.DoubleVar(),
            'Temperature': tk.DoubleVar(),
            'Equipment Fault': tk.BooleanVar(),
            'Plants': tk.IntVar(),
            'Blossoms': tk.IntVar(),
            'Fruit': tk.IntVar(),
            'Min Height': tk.DoubleVar(),
            'Max Height': tk.DoubleVar(),
            'Med Height': tk.DoubleVar(),
            'Notes': tk.StringVar()
        }

        # First section of form -  Record Info
        r_info = self._add_frame("Record Information")

        # First row of entry things for record info
        w.LabelInput(
            r_info, "Date",
            field_spec=fields['Date'],
            var=self._vars['Date'],
        ).grid(row=0, column=0)
        w.LabelInput(
            r_info, "Time",
            field_spec=fields['Time'],
            var=self._vars['Time'],
        ).grid(row=0, column=1)
        w.LabelInput(
            r_info, "Technician",
            field_spec=fields['Technician'],
            var=self._vars['Technician'],
        ).grid(row=0, column=2)

        # Second row of entry things for record info
        w.LabelInput(
            r_info, "Lab",
            field_spec=fields['Lab'],
            var=self._vars['Lab'],
        ).grid(row=1, column=0)
        w.LabelInput(
            r_info, "Plot",
            field_spec=fields['Plot'],
            var=self._vars['Plot'],
        ).grid(row=1, column=1)
        w.LabelInput(
            r_info, "Seed Sample",
            field_spec=fields['Seed Sample'],
            var=self._vars['Seed Sample'],
        ).grid(row=1, column=2)

        # Second section of form - Environmental Data
        e_info = self._add_frame("Environment Data")

        # First row of entry things for environmental data section
        w.LabelInput(
            e_info, "Humidity (g/m³)",
            field_spec=fields['Humidity'],
            var=self._vars['Humidity'],
            disable_var=self._vars['Equipment Fault'],
        ).grid(row=0, column=0)
        w.LabelInput(
            e_info, "Light (klx)",
            field_spec=fields['Light'],
            var=self._vars['Light'],
            disable_var=self._vars['Equipment Fault'],
        ).grid(row=0, column=1)
        w.LabelInput(
            e_info, "Temperature (°C)",
            input_class=w.ValidatedSpinbox,
            field_spec=fields['Temperature'],
            var=self._vars['Temperature'],
            disable_var=self._vars['Equipment Fault'],
        ).grid(row=0, column=2)

        # Second row of entry thing for environmental data section
        w.LabelInput(
            e_info, "Equipment Fault",
            field_spec=fields['Equipment Fault'],
            var=self._vars['Equipment Fault'],
        ).grid(row=1, column=0, columnspan=3)

        # Third section of form - Plant Data
        p_info = self._add_frame("Plant Data")

        # First row of entry things for plant data section
        w.LabelInput(
            p_info, "Plants",
            field_spec=fields['Plants'],
            var=self._vars['Plants'],
        ).grid(row=0, column=0)
        w.LabelInput(
            p_info, "Blossoms",
            field_spec=fields['Blossoms'],
            var=self._vars['Blossoms'],
        ).grid(row=0, column=1)
        w.LabelInput(
            p_info, "Fruit",
            field_spec=fields['Fruit'],
            var=self._vars['Fruit'],
        ).grid(row=0, column=2)

        # Second row of entry things for plant data section
        min_height_var = tk.DoubleVar(value=float('-Infinity'))
        max_height_var = tk.DoubleVar(value=float('Infinity'))

        w.LabelInput(
            p_info, "Min Height (cm)",
            field_spec=fields['Min Height'],
            var=self._vars['Min Height'],
            input_args={
                'max_var': max_height_var,
                'focus_update_var': min_height_var
            }
        ).grid(row=1, column=0)
        w.LabelInput(
            p_info, "Max Height (cm)",
            field_spec=fields['Max Height'],
            var=self._vars['Max Height'],
            input_args={
                'min_var': min_height_var,
                'focus_update_var': max_height_var
            }
        ).grid(row=1, column=1)
        w.LabelInput(
            p_info, "Median Height (cm)",
            field_spec=fields['Med Height'],
            var=self._vars['Med Height'],
            input_args={
                'min_var': min_height_var,
                'max_var': max_height_var
            }
        ).grid(row=1, column=2)

        # Notes section
        w.LabelInput(
            self, "Notes",
            input_class=w.BoundText, var=self._vars['Notes'],
            input_args={'width': 75, 'height': 10}
        ).grid(sticky=tk.W, row=3, column=0)

        # Buttons section
        buttons = tk.Frame(self)
        buttons.grid(sticky=(tk.W + tk.E), row=4)

        # Save button
        self.savebutton = ttk.Button(
            buttons, text="Save", command=self._on_save
        )
        self.savebutton.pack(side=tk.RIGHT)

        # Reset button
        self.resetbutton = ttk.Button(
            buttons, text="Reset", command=self.reset
        )
        self.resetbutton.pack(side=tk.RIGHT)


class LoginDialog(Dialog):
    """A dialog that asks for username and password"""

    def __init__(self, parent, title, error=''):
        self._pw = tk.StringVar()
        self._user = tk.StringVar()
        self._error = tk.StringVar(value=error)
        super().__init__(parent, title=title)

    def body(self, frame):
        ttk.Label(frame, text='Login to ABQ').grid(row=0)

        if self._error.get():
            ttk.Label(frame, textvariable=self._error).grid(row=1)

        user_inp = w.LabelInput(
            frame, 'User name:', input_class=w.RequiredEntry,
            var=self._user
        )
        user_inp.grid()

        w.LabelInput(
            frame, 'Password:', input_class=w.RequiredEntry,
            input_args={'show': '*'}, var=self._pw
        ).grid()

        return user_inp.input

    def buttonbox(self):
        box = ttk.Frame(self)
        ttk.Button(
            box, text='Login', command=self.ok, default=tk.ACTIVE
        ).grid(padx=5, pady=5)

        ttk.Button(
            box, text='Cancel', command=self.cancel
        ).grid(row=0, column=1, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def apply(self):
        self.result = (self._user.get(), self._pw.get())
