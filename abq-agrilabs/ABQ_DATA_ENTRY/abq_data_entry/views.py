import tkinter as tk
from tkinter import ttk
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

    def __init__(self, parent, model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = model
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
        )

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
            input_class=w.ValidatedSpinbox, var=self._vars['Max Height'],
            input_args={
                'min_var': min_height_var, 'focus_update_var': max_height_var
            }
        ).grid(row=1, column=1)
        w.LabelInput(
            p_info, "Median Height (cm)",
            input_class=w.ValidatedSpinbox, var=self._vars['Med Height'],
            input_args={
                'from_': 0, 'to': 1000, 'increment': .01,
                'min_var': min_height_var, 'max_var': max_height_var
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
            buttons, text="Save", command=self.master._on_save
        )
        self.savebutton.pack(side=tk.RIGHT)

        # Reset button
        self.resetbutton = ttk.Button(
            buttons, text="Reset", command=self.reset
        )
        self.resetbutton.pack(side=tk.RIGHT)
