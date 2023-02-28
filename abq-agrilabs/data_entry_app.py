"""The ABQ Data Entry application"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pathlib import Path
import csv


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


variables = dict()
records_saved = 0


root = tk.Tk()
root.title('ABQ Data Entry Application')
root.columnconfigure(0, weight=1)

ttk.Label(
    root,
    text='ABQ Data Entry Application',
    font=('TkDefaultFont', 16)
).grid()


drf = ttk.Frame(root)
drf.grid(padx=10, sticky=(tk.W + tk.E))
drf.columnconfigure(0, weight=1)


r_info = ttk.LabelFrame(drf, text='Record Information')
r_info.grid(sticky=(tk.W + tk.E))
for i in range(3):
    r_info.columnconfigure(i, weight=1)

variables['Date'] = tk.StringVar()
ttk.Label(r_info, text='Date').grid(row=0, column=0)
ttk.Entry(
    r_info,
    textvariable=variables['Date']
).grid(row=1, column=0, sticky=(tk.W + tk.E))

time_values = ['8:00', '12:00', '16:00', '20:00']
variables['Time'] = tk.StringVar()
ttk.Label(r_info, text='Time').grid(row=0, column=1)
ttk.Combobox(
    r_info,
    textvariable=variables['Time'],
    values=time_values
).grid(row=1, column=1, sticky=(tk.W + tk.E))

variables['Technician'] = tk.StringVar()
ttk.Label(r_info, text='Technician').grid(row=0, column=2)
ttk.Entry(
    r_info,
    textvariable=variables['Technician']
).grid(row=1, column=2, sticky=(tk.W + tk.E))

variables['Lab'] = tk.StringVar()
ttk.Label(r_info, text='Lab').grid(row=2, column=0)
lab_frame = ttk.Frame(r_info)
for lab in ('A', 'B', 'C'):
    ttk.Radiobutton(
        lab_frame,
        value=lab,
        text=lab,
        variable=variables['Lab']
    ).pack(side=tk.LEFT, expand=True)
lab_frame.grid(row=3, column=0, sticky=(tk.W + tk.E))

variables['Plot'] = tk.IntVar()
ttk.Label(r_info, text='Plot').grid(row=2, column=1)
ttk.Combobox(
    r_info,
    textvariable=variables['Plot'],
    values=list(range(1, 21))
).grid(row=3, column=1, sticky=(tk.W + tk.E))

variables['Seed Sample']= tk.StringVar()
ttk.Label(r_info, text='Seed Sample').grid(row=2, column=2)
ttk.Entry(
    r_info,
    textvariable=variables['Seed Sample']
).grid(row=3, column=2, sticky=(tk.W + tk.E))


e_info = ttk.LabelFrame(drf, text='Environment Data')
e_info.grid(sticky=(tk.W + tk.E))
for i in range(3):
    e_info.columnconfigure(i, weight=1)

variables['Humidity'] = tk.DoubleVar()
ttk.Label(e_info, text="Humidity (g/m³)").grid(row=0, column=0)
ttk.Spinbox(
    e_info,
    textvariable=variables['Humidity'],
    from_=0.5,
    to=52.0,
    increment=0.01
).grid(row=1, column=0, sticky=(tk.W + tk.E))

variables['Light'] = tk.DoubleVar()
ttk.Label(e_info, text='Light (klx)').grid(row=0, column=1)
ttk.Spinbox(
    e_info,
    textvariable=variables['Light'],
    from_=0,
    to=100,
    increment=0.01
).grid(row=1, column=1, sticky=(tk.W + tk.E))

variables['Temperature'] = tk.DoubleVar()
ttk.Label(e_info, text='Temperature (˚C)').grid(row=0, column=2)
ttk.Spinbox(
    e_info,
    textvariable=variables['Temperature'],
    from_=4,
    to=40,
    increment=0.01
).grid(row=1, column=2, sticky=(tk.W + tk.E))

variables['Equipment Fault'] = tk.BooleanVar(value=False)
ttk.Checkbutton(
    e_info,
    variable=variables['Equipment Fault'],
    text='Equipment Fault'
).grid(row=2, column=0, sticky=tk.W, pady=5)


p_info = ttk.LabelFrame(drf, text='Plant Data')
p_info.grid(sticky=(tk.W + tk.E))
for i in range(3):
    p_info.columnconfigure(i, weight=1)

variables['Plants'] = tk.IntVar()
ttk.Label(p_info, text='Plants').grid(row=0, column=0)
ttk.Spinbox(
    p_info,
    textvariable=variables['Plants'],
    from_=0,
    to=20,
    increment=1
).grid(row=1, column=0, sticky=(tk.W + tk.E))

variables['Blossoms'] = tk.IntVar()
ttk.Label(p_info, text='Blossoms').grid(row=0, column=1)
ttk.Spinbox(
    p_info,
    textvariable=variables['Blossoms'],
    from_=0,
    to=1000,
    increment=1
).grid(row=1, column=1, sticky=(tk.W + tk.E))

variables['Fruits'] = tk.IntVar()
ttk.Label(p_info, text='Fruit').grid(row=0, column=2)
ttk.Spinbox(
    p_info,
    textvariable=variables['Fruits'],
    from_=0,
    to=1000,
    increment=1
).grid(row=1, column=2, sticky=(tk.W + tk.E))

variables['Min Height'] = tk.DoubleVar()
ttk.Label(p_info, text='Min Height (cm)').grid(row=2, column=0)
ttk.Spinbox(
    p_info,
    textvariable=variables['Min Height'],
    from_=0,
    to=1000,
    increment=0.01
).grid(row=3, column=0, sticky=(tk.W + tk.E))

variables['Max Height'] = tk.DoubleVar()
ttk.Label(p_info, text='Max Height (cm)').grid(row=2, column=1)
ttk.Spinbox(
    p_info,
    textvariable=variables['Max Height'],
    from_=0,
    to=1000,
    increment=0.01
).grid(row=3, column=1, sticky=(tk.W + tk.E))

variables['Med Height'] = tk.DoubleVar()
ttk.Label(p_info, text='Med Height (cm)').grid(row=2, column=2)
ttk.Spinbox(
    p_info,
    textvariable=variables['Med Height'],
    from_=0,
    to=1000,
    increment=0.01
).grid(row=3, column=2, sticky=(tk.W + tk.E))


ttk.Label(drf, text="Notes").grid()
notes_inp = tk.Text(drf, width=75, height=10)
notes_inp.grid(sticky=(tk.W + tk.E))


buttons = tk.Frame(drf)
buttons.grid(sticky=(tk.W + tk.E))

save_button = ttk.Button(buttons, text='Save')
save_button.pack(side=tk.RIGHT)

reset_button = ttk.Button(buttons, text='Reset')
reset_button.pack(side=tk.RIGHT)


status_variable = tk.StringVar()
ttk.Label(
    root,
    textvariable=status_variable
).grid(sticky=(tk.W + tk.E), row=99, padx=10)


def on_reset():
    """Called when reset button is clicked or after save"""
    for variable in variables.values():
        if isinstance(variable, tk.BooleanVar):
            variable.set(False)
        else:
            variable.set('')
        notes_inp.delete('1.0', tk.END)


reset_button.configure(command=on_reset)


def on_save():
    """Handle save button clicks"""
    global records_saved
    datestring = datetime.today().strftime("%Y-%m-%d")
    filename = f"abq_data_record_{datestring}.csv"
    newfile = not Path(filename).exists()

    data = dict()
    fault = variables['Equipment Fault'].get()
    for key, variable in variables.items():
        if fault and key in ('Light', 'Humidity', 'Temperature'):
            data[key] = ''
        else:
            try:
                data[key] = variable.get()
            except tk.TclError:
                status_variable.set(
                    f"Error in field: {key}. Data was not saved!"
                )
                return
    data['Notes'] = notes_inp.get('1.0', tk.END)

    with open(filename, 'a', newline='') as fh:
        csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
        if newfile:
            csvwriter.writeheader()
        csvwriter.writerow(data)

    records_saved += 1
    status_variable.set(
        f"{records_saved} records saved this session"
    )
    on_reset()


save_button.configure(command=on_save)


on_reset()
root.mainloop()
