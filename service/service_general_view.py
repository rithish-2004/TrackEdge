import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from service import service_backend
from tkcalendar import DateEntry

class ServiceGeneralViewFrame(tk.Frame):
    def __init__(self, parent, theme, get_colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.theme = theme
        self.get_colors = get_colors

        self.num_var = tk.IntVar(value=5)
        self.order_var = tk.StringVar(value='recent')
        self.view_mode_var = tk.StringVar(value='service')

        self.from_date_var = tk.StringVar(value='')
        self.to_date_var = tk.StringVar(value='')

        self.build_title()
        self.build_widgets()
        self.configure_theme()
        self.refresh_table(filter_clicked=False)

    def build_title(self):
        colors = self.get_colors()
        self.title_label = tk.Label(self, text="Service - General View", font=("Arial", 22, "bold"),
                                   bg=colors["bg"], fg=colors["fg"])
        self.title_label.pack(pady=(20, 10))

    def build_widgets(self):
        colors = self.get_colors()
        self.controls = tk.Frame(self, bg=colors["bg"])
        self.controls.pack(fill='x', pady=10)

        tk.Radiobutton(self.controls, text="View Service", variable=self.view_mode_var, value='service', font=("Arial", 12, "bold"),
                       bg=colors["bg"], fg=colors["fg"], selectcolor=colors["entry_bg"],
                       command=self.on_view_mode_change).pack(side='left', padx=(10,2))
        tk.Radiobutton(self.controls, text="View Transaction", variable=self.view_mode_var, value='transaction', font=("Arial", 12, "bold"),
                       bg=colors["bg"], fg=colors["fg"], selectcolor=colors["entry_bg"],
                       command=self.on_view_mode_change).pack(side='left', padx=(2,10))

        self.from_label = tk.Label(self.controls, text="From:", bg=colors["bg"], fg=colors["fg"])
        self.from_entry = DateEntry(self.controls, textvariable=self.from_date_var, date_pattern='yyyy-mm-dd', style='TEntry')
        self.to_label = tk.Label(self.controls, text="To:", bg=colors["bg"], fg=colors["fg"])
        self.to_entry = DateEntry(self.controls, textvariable=self.to_date_var, date_pattern='yyyy-mm-dd', style='TEntry')

        self.num_label = tk.Label(self.controls, text="Entries:", bg=colors["bg"], fg=colors["fg"])
        self.num_entry = tk.Spinbox(self.controls, from_=1, to=100, textvariable=self.num_var, width=4, bg=colors["entry_bg"], fg=colors["fg"])
        self.order_label = tk.Label(self.controls, text="Order:", bg=colors["bg"], fg=colors["fg"])
        self.order_combo = ttk.Combobox(self.controls, textvariable=self.order_var, values=['recent', 'oldest'],
                                        width=8, state='readonly', style="Custom.TCombobox")

        self.filter_btn = tk.Button(self.controls, text="Filter", bg=colors["button_bg"], fg=colors["fg"], command=lambda: self.refresh_table(filter_clicked=True))
        self.filter_btn.pack(side='left')
        self.reset_btn = tk.Button(self.controls, text="Reset", bg=colors["button_bg"], fg=colors["fg"], command=self.reset_filters)
        self.reset_btn.pack(side='left', padx=2)

        self.table_frame = tk.Frame(self, bg=colors["bg"])
        self.table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("Customer", "Item", "Fault", "Amount", "Date")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', stretch=True, width=1, minwidth=80)
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind('<Configure>', self._resize_columns)

        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')

        self.on_view_mode_change()

    def _resize_columns(self, event=None):
        total_width = self.tree.winfo_width()
        num_cols = len(self.tree["columns"])
        if num_cols > 0:
            col_width = int(total_width / num_cols)
            for col in self.tree["columns"]:
                self.tree.column(col, width=col_width)

    def on_view_mode_change(self):
        for widget in [self.from_label, self.from_entry, self.to_label, self.to_entry,
                       self.num_label, self.num_entry, self.order_label, self.order_combo]:
            widget.pack_forget()

        if self.view_mode_var.get() == 'service':
            self.from_label.pack(side='left', padx=(10,2))
            self.from_entry.pack(side='left')
            self.to_label.pack(side='left', padx=(10,2))
            self.to_entry.pack(side='left')
        else:
            self.num_label.pack(side='left', padx=(10,2))
            self.num_entry.pack(side='left')
            self.order_label.pack(side='left', padx=(10,2))
            self.order_combo.pack(side='left')

        self.refresh_table()

    def refresh_table(self, filter_clicked=False):
        try:
            value = self.num_var.get()
            limit = int(value) if value else 5
            if limit <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showwarning("Invalid Input", "Please enter a positive integer for number of entries.")
            self.num_var.set(5)
            limit = 5

        for row in self.tree.get_children():
            self.tree.delete(row)

        view_mode = self.view_mode_var.get()
        if view_mode == 'service':
            from_date = self.from_date_var.get().strip()
            to_date = self.to_date_var.get().strip()
            if not filter_clicked:
                data = service_backend.get_service_items_general_view()
            else:
                if from_date and to_date:
                    try:
                        datetime.strptime(from_date, "%Y-%m-%d")
                        datetime.strptime(to_date, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showwarning("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
                        return
                    data = service_backend.get_service_items_general_view(from_date, to_date)
                else:
                    data = service_backend.get_service_items_general_view()
            columns = ("Customer", "Item", "Fault", "Amount", "Date")
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
            for customer, item, desc, amount, date in data:
                self.tree.insert('', 'end', values=(customer, item, desc, amount, date))
            self._resize_columns()
        else:
            columns = ("Customer", "Payment ID", "Amount", "Date")
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
            try:
                data = service_backend.get_recent_service_payments_general(order=self.order_var.get(), limit=limit)
                for customer, payment_id, amount, date in data:
                    self.tree.insert('', 'end', values=(customer, payment_id, amount, date))
                self._resize_columns()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch service payments: {e}")

    def reset_filters(self):
        self.from_date_var.set('')
        self.to_date_var.set('')
        self.refresh_table(filter_clicked=False)

    def configure_theme(self):
        colors = self.get_colors()
        self.configure(bg=colors["bg"])
        self.title_label.configure(bg=colors["bg"], fg=colors["fg"])
        self.controls.configure(bg=colors["bg"])
        self.table_frame.configure(bg=colors["bg"])
        self.update_widget_colors(self.controls)
        self.update_widget_colors(self.table_frame)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background=colors["table_bg"],
                        foreground=colors["table_fg"],
                        fieldbackground=colors["table_bg"],
                        bordercolor=colors["table_border"],
                        borderwidth=1)
        style.configure("Treeview.Heading",
                        background=colors["table_head_bg"],
                        foreground=colors["table_head_fg"],
                        font=("Arial", 11, "bold"))
        style.map('Treeview', background=[('selected', colors["table_head_bg"])])
        style.configure("Custom.TCombobox",
                        fieldbackground=colors["entry_bg"],
                        background=colors["entry_bg"],
                        foreground=colors["fg"])
        style.configure("Custom.TEntry",
                        fieldbackground=colors["entry_bg"],
                        foreground=colors["fg"],
                        background=colors["entry_bg"])

    def update_widget_colors(self, frame):
        colors = self.get_colors()
        for widget in frame.winfo_children():
            if widget.winfo_class() == 'Label':
                widget.configure(bg=colors["bg"], fg=colors["fg"])
            elif widget.winfo_class() == 'Entry':
                widget.configure(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"])
            elif widget.winfo_class() == 'Button':
                widget.configure(bg=colors["button_bg"], fg=colors["fg"])
            elif widget.winfo_class() == 'Frame':
                widget.configure(bg=colors["bg"])
                self.update_widget_colors(widget)
            elif widget.winfo_class() == 'Radiobutton':
                widget.configure(bg=colors["bg"], fg=colors["fg"], selectcolor=colors["entry_bg"])

    def update_theme(self):
        self.configure_theme()
        self.refresh_table()
