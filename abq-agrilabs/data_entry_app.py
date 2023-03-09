"""The ABQ Data Entry application"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pathlib import Path
import csv
from decimal import Decimal, InvalidOperation


class ValidatedMixin:
    """Adds a validation functionality to an input widget"""
    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super.__init__(*args, **kwargs)
        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)
        self.configure(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        self.configure(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        self.error.set('')
        self._toggle_error()
        valid = True
        # if the widget is disabled don't validate
        state = str(self.configure('state')[-1])
        if state == tk.DISABLED:
            return valid
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._vey_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )

    def _focusout_invalid(self, **kwargs):
        """Handle invalid data on a focus event"""
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        """Handle invalid data on a key event. By default, we do nothing"""
        pass

    def trigger_focusout_validation(self):
        """To validate the input as a whole whenever we want"""
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid


class RequiredEntry(ValidatedMixin, ttk.Entry):
    """An Entry that requires a value"""
    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class DateEntry(ValidatedMixin, ttk.Entry):
    """An Entry that only accepts ISO Date strings"""
    def _key_validate(self, action, index, char, **kwargs):
        valid = True
        if action == '0':  # this is for deletion
            valid = True
        elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
            valid = char.isdigit()
        elif index in ('4', '7'):
            valid = char == '-'
        else:
            valid = False
        return valid

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set('A value is required')
            valid = False
        try:
            datetime.strptime(self.get(), '%Y-%m-%d')
        except ValueError:
            self.error.set('Invalid date')
            valid = False
        return valid


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):
    """A combobox that only takes values from its string list"""
    def _key_validate(self, proposed, action, **kwargs):
        valid = True
        if action == '0':
            self.set('')
            return True
        values = self.cget('values')
        # Do a case-insensitive match against the entered text
        matching = [
            x for x in values
            if x.lower().startswith(proposed.lower())
        ]
        if len(matching) == 0:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid = False
        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class ValidatedSpinbox(ValidatedMixin, ttk.Spinbox):
    def __init__(
            self, *args, from_='-Infinity', to='Infinity', **kwargs
    ):
        super().__init__(*args, from_=from_, to=to, **kwargs)
        increment = Decimal(str(kwargs.get('increment', '1.0')))
        self.precision = increment.normalize().as_tuple().exponent

    def _key_validate(
            self, char, index, current, proposed, action, **kwargs
    ):
        if action == '0':
            return True
        valid = True
        min_val = self.cget('from')
        max_val = self.cget('to')
        no_negative = min_val >= 0
        no_decimal = self.precision >= 0
        if any([
            (char not in '-123456789'),
            (char == '-' and (no_negative or index != '0')),
            (char == '.' and (no_decimal or '.' in current))
        ]):
            return False
        if proposed in '-.':
            return True
        proposed = Decimal(proposed)
        proposed_precision = proposed.as_tuple().exponent
        if any([
            (proposed > max_val),
            (proposed_precision < self.precision)
        ]):
            return False
        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        value = self.get()
        min_val = self.cget('from')
        max_val = self.cget('to')
        try:
            d_value = Decimal(value)
        except InvalidOperation:
            self.error.set(f'Invalid number string: {value}')
            return False
        if d_value < min_val:
            self.error.set(f'Value is too low (min {min_val})')
            valid = False
        if d_value > max_val:
            self.error.set(f'Value is too high (max {max_val})')
            valid = False
        return valid


class BoundText(tk.Text):
    """A Text widget with a bound variable"""
    def __init__(self, *args, textvariable=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._variable = textvariable
        if self._variable:
            self.insert('1.0', self._variable.get())
            self._variable.trace_add('write', self._set_content)
            self.bind('<<Modified>>', self._set_var)

    def _set_content(self, *_):
        """Set the text contents to the variable"""
        self.delete('1.0', tk.END)
        self.insert('1.0', self._variable.get())

    def _set_var(self, *_):
        """Set the variable to the text contents"""
        if self.edit_modified():
            content = self.get('1.0', 'end-1chars')
            self._variable.set(content)
            self.edit_modified(False)


class LabelInput(tk.Frame):
    """A widget containing a label and input together"""
    def __init__(
            self, parent, label, var, input_class=ttk.Entry,
            input_args=None, label_args=None, **kwargs
    ):
        super().__init__(parent, **kwargs)  # Creating frame

        # setting up additional args as empty dicts if none provided
        input_args = input_args or {}
        label_args = label_args or {}

        # set up variable to bind to widget and adding self as the label of this var
        self.variable = var
        self.variable.label_widget = self

        # creating label
        if input_class in (ttk.Checkbutton, ttk.Button):  # no separate label needed if this type of input
            input_args["text"] = label
        else:
            # adding label with provided text & args and gridding it.
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # setting up args with proper variable binding
        if input_class in (
            ttk.Checkbutton, ttk.Button, ttk.Radiobutton
        ):  # for these types we bind with "variable" keyword
            input_args["variable"] = self.variable
        else:  # otherwise we bind with "textvariable" keyword
            input_args["textvariable"] = self.variable

        # adding input
        if input_class == ttk.Radiobutton:  # radiobutton needs to add one for each of the values in input_args
            self.input = tk.Frame(self)  # create frame to hold them with this object as parent
            for v in input_args.pop('values', []):  # going through all values or nothing if nothing
                button = ttk.Radiobutton(
                    self.input, value=v, text=v, **input_args
                )  # create the button with created frame as parent, given value as text & value, and all input_args
                button.pack(
                    side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x'
                )  # pack in to the left side of created frame
        else:
            self.input = input_class(self, **input_args)  # otherwise it's easy, we're the parent, and we add the args

        # organizing the input into the whole widget
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))  # it goes below the label, stretches to each side
        self.columnconfigure(0, weight=1)  # first (and only) column should expand to the whole widget

    def grid(self, sticky=(tk.W + tk.E), **kwargs):
        """Override grid to add default sticky values"""
        super().grid(sticky=sticky, **kwargs)


class DataRecordForm(ttk.Frame):
    """The input form for our widgets"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        LabelInput(
            r_info, "Date", var=self._vars['Date']
        ).grid(row=0, column=0)
        LabelInput(
            r_info, "Time", input_class=ttk.Combobox,
            var=self._vars['Time'],
            input_args={'values': ['8:00', '12:00', '16:00', '20:00']}
        ).grid(row=0, column=1)
        LabelInput(
            r_info, "Technician", var=self._vars['Technician']
        ).grid(row=0, column=2)

        # Second row of entry things for record info
        LabelInput(
            r_info, "Lab", input_class=ttk.Radiobutton,
            var=self._vars['Lab'],
            input_args={'values': ['A', 'B', 'C']}
        ).grid(row=1, column=0)
        LabelInput(
            r_info, "Plot", input_class=ttk.Combobox,
            var=self._vars['Plot'],
            input_args={'values': [list(range(1, 21))]}
        ).grid(row=1, column=1)
        LabelInput(
            r_info, "Seed Sample", var=self._vars['Seed Sample']
        ).grid(row=1, column=2)

        # Second section of form - Environmental Data
        e_info = self._add_frame("Environment Data")

        # First row of entry things for environmental data section
        LabelInput(
            e_info, "Humidity (g/m³)",
            input_class=ttk.Spinbox, var=self._vars['Humidity'],
            input_args={'from_': 0.5, 'to': 52.0, 'increment': .01}
        ).grid(row=0, column=0)
        LabelInput(
            e_info, "Light (klx)", input_class=ttk.Spinbox,
            var=self._vars['Light'],
            input_args={'from_': 0, 'to': 100, 'increment': .01}
        ).grid(row=0, column=1)
        LabelInput(
            e_info, "Temperature (°C)",
            input_class=ttk.Spinbox, var=self._vars['Temperature'],
            input_args={'from_': 4, 'to': 40, 'increment': .01}
        )

        # Second row of entry thing for environmental data section
        LabelInput(
            e_info, "Equipment Fault",
            input_class=ttk.Checkbutton,
            var=self._vars['Equipment Fault']
        ).grid(row=1, column=0, columnspan=3)

        # Third section of form - Plant Data
        p_info = self._add_frame("Plant Data")

        # First row of entry things for plant data section
        LabelInput(
            p_info, "Plants", input_class=ttk.Spinbox,
            var=self._vars['Plants'],
            input_args={'from_': 0, 'to': 20}
        ).grid(row=0, column=0)
        LabelInput(
            p_info, "Blossoms", input_class=ttk.Spinbox,
            var=self._vars['Blossoms'],
            input_args={'from_': 0, 'to': 1000}
        ).grid(row=0, column=1)
        LabelInput(
            p_info, "Fruit", input_class=ttk.Spinbox,
            var=self._vars['Fruit'],
            input_args={'from_': 0, 'to': 1000}
        ).grid(row=0, column=2)

        # Second row of entry things for plant data section
        LabelInput(
            p_info, "Min Height (cm)",
            input_class=ttk.Spinbox, var=self._vars['Min Height'],
            input_args={'from_': 0, 'to': 1000, 'increment': .01}
        ).grid(row=1, column=0)
        LabelInput(
            p_info, "Max Height (cm)",
            input_class=ttk.Spinbox, var=self._vars['Max Height'],
            input_args={'from_': 0, 'to': 1000, 'increment': .01}
        ).grid(row=1, column=1)
        LabelInput(
            p_info, "Median Height (cm)",
            input_class=ttk.Spinbox, var=self._vars['Med Height'],
            input_args={'from_': 0, 'to': 1000, 'increment': .01}
        ).grid(row=1, column=2)

        # Notes section
        LabelInput(
            self, "Notes",
            input_class=BoundText, var=self._vars['Notes'],
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

    def _add_frame(self, label, cols=3):
        """Add a LabelFrame to the form"""
        frame = ttk.LabelFrame(self, text=label)  # create the frame with whole form as parent and label passed in
        frame.grid(sticky=(tk.W + tk.E))  # add frame to form
        # each column should expand evenly
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def reset(self):
        """Resets the form entries"""
        for var in self._vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set('')

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


class Application(tk.Tk):
    """Application root window"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Basic Setup
        self.title("ABQ Data Entry Application")
        self.columnconfigure(0, weight=1)

        # Window label
        ttk.Label(
            self, text="ABQ Data Entry Application",
            font=("TkDefaultFont", 16)
        ).grid(row=0)

        # Creating the form
        self.recordform = DataRecordForm(self)
        self.recordform.grid(row=1, column=0, padx=10, sticky=(tk.W + tk.E))

        # Status bar at the bottom
        self.status = tk.StringVar()
        ttk.Label(
            self, textvariable=self.status
        ).grid(sticky=(tk.W + tk.E), row=2, padx=10)

        self._records_saved = 0

    def _on_save(self):
        """Handles save button clicks"""
        datestring = datetime.today().strftime("%Y-%m-%d")
        filename = f'abq_data_record_{datestring}.csv'
        newfile = not Path(filename).exists()
        try:
            data = self.recordform.get()
        except ValueError as e:
            self.status.set(str(e))
            return
        with open(filename, 'a', newline='') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(data)
            self._records_saved += 1
            self.status.set(
                f"{self._records_saved} records saved this session"
            )
            self.recordform.reset()


if __name__ == '__main__':
    app = Application()
    app.mainloop()
