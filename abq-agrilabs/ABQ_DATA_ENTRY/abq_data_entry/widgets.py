import tkinter as tk
from tkinter import ttk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .constants import FieldTypes as FT


class ValidatedMixin:
    """Adds a validation functionality to an input widget"""
    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)
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
            self._key_invalid(
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
            self, *args, min_var=None, max_var=None,
            focus_update_var=None, from_='-Infinity', to='Infinity', **kwargs
    ):
        super().__init__(*args, from_=from_, to=to, **kwargs)
        increment = Decimal(str(kwargs.get('increment', '1.0')))
        self.precision = increment.normalize().as_tuple().exponent
        self.variable = kwargs.get('textvariable')
        if not self.variable:
            self.variable = tk.DoubleVar()
            self.configure(textvariable=self.variable)
        if min_var:
            self.min_var = min_var
            self.min_var.trace_add('write', self._set_minimum)
        if max_var:
            self.max_var = max_var
            self.max_var.trace_add('write', self._set_maximum)
        self.focus_update_var = focus_update_var
        self.bind('<FocusOut>', self._set_focus_update_var)

    def _set_focus_update_var(self, event):
        value = self.get()
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(value)

    def _set_minimum(self, *_):
        current = self.get()
        try:
            new_min = self.min_var.get()
            self.config(from_=new_min)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()

    def _set_maximum(self, *_):
        current = self.get()
        try:
            new_max = self.max_var.get()
            self.config(to=new_max)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()

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


class ValidatedRadioGroup(ttk.Frame):
    """A validated radio button group"""
    def __init__(
            self, *args, variable=None, error_var=None,
            values=None, button_args=None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.variable = variable or tk.StringVar()
        self.error = error_var or tk.StringVar()
        self.values = values or list()
        self.button_args = button_args or dict()
        for v in self.values:
            button = ttk.Radiobutton(
                self, value=v, text=v,
                variable=self.variable, **self.button_args
            )
            button.pack(
                side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x'
            )
        self.bind('<FocusOut>', self.trigger_focusout_validation)

    def trigger_focusout_validation(self, *_):
        self.error.set('')
        if not self.variable.get():
            self.error.set('A value is required')


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
    field_types = {
        FT.string: RequiredEntry,
        FT.string_list: ValidatedCombobox,
        FT.short_string_list: ValidatedRadioGroup,
        FT.iso_date_string: DateEntry,
        FT.long_string: BoundText,
        FT.decimal: ValidatedSpinbox,
        FT.integer: ValidatedSpinbox,
        FT.boolean: ttk.Checkbutton
    }

    def __init__(
            self, parent, label, var, input_class=None,
            input_args=None, label_args=None, field_spec=None,
            disable_var=None, **kwargs
    ):
        super().__init__(parent, **kwargs)  # Creating frame

        # setting up additional args as empty dicts if none provided
        input_args = input_args or {}
        label_args = label_args or {}

        # set up variable to bind to widget and adding self as the label of this var
        self.variable = var
        self.variable.label_widget = self

        # process the field spec to determine input_class and validation
        if field_spec:
            field_type = field_spec.get('type', FT.string)
            input_class = input_class or self.field_types.get(field_type)
            if 'min' in field_spec and 'from_' not in input_args:
                input_args['from_'] = field_spec.get('min')
            if 'max' in field_spec and 'to' not in input_args:
                input_args['to'] = field_spec.get('max')
            if 'inc' in field_spec and 'increment' not in input_args:
                input_args['increment'] = field_spec.get('inc')
            if 'values' in field_spec and 'values' not in input_args:
                input_args['values'] = field_spec.get('values')

        # creating label
        if input_class in (ttk.Checkbutton, ttk.Button):  # no separate label needed if this type of input
            input_args["text"] = label
        else:
            # adding label with provided text & args and gridding it.
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # setting up args with proper variable binding
        if input_class in (
            ttk.Checkbutton, ttk.Button,
            ttk.Radiobutton, ValidatedRadioGroup
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

        if disable_var:
            self.disable_var = disable_var
            self.disable_var.trace_add('write', self._check_disable)

        self.error = getattr(self.input, 'error', tk.StringVar())
        ttk.Label(self, textvariable=self.error, **label_args).grid(
            row=2, column=0, sticky=(tk.W + tk.E)
        )

    def _check_disable(self, *_):
        if not hasattr(self, 'disable_var'):
            return
        if self.disable_var.get():
            self.input.configure(state=tk.DISABLED)
            self.variable.set('')
            self.error.set('')
        else:
            self.input.configure(state=tk.NORMAL)

    def grid(self, sticky=(tk.W + tk.E), **kwargs):
        """Override grid to add default sticky values"""
        super().grid(sticky=sticky, **kwargs)
