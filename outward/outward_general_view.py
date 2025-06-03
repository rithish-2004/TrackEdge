import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from outward import customer_backend
from tkcalendar import DateEntry

class OutwardGeneralViewFrame(tk.Frame):
    def __init__(self, parent, theme, get_colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.theme = theme
        self.get_colors = get_colors

        self.num_var = tk.IntVar(value=5)
        self.order_var = tk.StringVar(value='recent')
        self.view_mode_var = tk.StringVar(value='product')
        


        # Date range variables for product view
        #today_str = datetime.now().strftime("%Y-%m-%d")
        self.from_date_var = tk.StringVar(value='')
        self.to_date_var = tk.StringVar(value='')
        self.build_title()

        self.build_widgets()
        self.configure_theme()
        self.refresh_table(filter_clicked=False)

    def build_title(self):
        colors = self.get_colors()
        self.title_label = tk.Label(self, text="Sales - General View", font=("Arial", 22, "bold"),
                                bg=colors["bg"], fg=colors["fg"])
        self.title_label.pack(pady=(20, 10))

    def build_widgets(self):
        colors = self.get_colors()

        # Controls Frame
        self.controls = tk.Frame(self, bg=colors["bg"])
        self.controls.pack(fill='x', pady=10)

        # View mode radio buttons
        tk.Radiobutton(self.controls, text="View Product", variable=self.view_mode_var, value='product',font=("Arial", 12, "bold"),
                       bg=colors["bg"], fg=colors["fg"], selectcolor=colors["entry_bg"],
                       command=self.on_view_mode_change).pack(side='left', padx=(10,2))
        tk.Radiobutton(self.controls, text="View Transaction", variable=self.view_mode_var, value='transaction',font=("Arial", 12, "bold"),
                       bg=colors["bg"], fg=colors["fg"], selectcolor=colors["entry_bg"],
                       command=self.on_view_mode_change).pack(side='left', padx=(2,10))

        # Date range fields (for product view)
        self.from_label = tk.Label(self.controls, text="From:", bg=colors["bg"], fg=colors["fg"])
        """self.from_entry = DateEntry(self.controls, textvariable=self.from_date_var, width=10, 
                                    date_pattern='yyyy-mm-dd', background=colors["entry_bg"], 
                                    foreground=colors["fg"], borderwidth=2)"""
        self.to_label = tk.Label(self.controls, text="To:", bg=colors["bg"], fg=colors["fg"])
        """#self.to_entry = DateEntry(self.controls, textvariable=self.to_date_var, width=10, 
                                date_pattern='yyyy-mm-dd', background=colors["entry_bg"], 
                                foreground=colors["fg"], borderwidth=2)"""
        self.from_entry = DateEntry(self.controls, textvariable=self.from_date_var, date_pattern='yyyy-mm-dd', style='TEntry')
        self.to_entry = DateEntry(self.controls, textvariable=self.to_date_var, date_pattern='yyyy-mm-dd', style='TEntry')




        # Number of entries and order (for transaction view)
        self.num_label = tk.Label(self.controls, text="Entries:", bg=colors["bg"], fg=colors["fg"])
        self.num_entry = tk.Spinbox(self.controls, from_=1, to=100, textvariable=self.num_var, width=4, bg=colors["entry_bg"], fg=colors["fg"])
        self.order_label = tk.Label(self.controls, text="Order:", bg=colors["bg"], fg=colors["fg"])
        self.order_combo = ttk.Combobox(self.controls, textvariable=self.order_var, values=['recent', 'oldest'],
                                        width=8, state='readonly', style="Custom.TCombobox")

        # Filter button
        #self.filter_btn = tk.Button(self.controls, text="Filter", bg=colors["button_bg"], fg=colors["fg"], command=self.refresh_table)
        #self.filter_btn = tk.Button(text="Filter", command=self.refresh_table)
        self.filter_btn = tk.Button(self.controls, text="Filter", bg=colors["button_bg"], fg=colors["fg"], command=lambda: self.refresh_table(filter_clicked=True))
        self.filter_btn.pack(side='left')

        # Table Frame
        self.table_frame = tk.Frame(self, bg=colors["bg"])
        self.table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("Customer", "Product", "Qty", "Price", "Amount", "Date")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', stretch=True, width=100)
        self.tree.pack(side='left', fill='both', expand=True)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')

        # Initial layout
        self.on_view_mode_change()

    def on_view_mode_change(self):
        # Hide all controls first
        for widget in [self.from_label, self.from_entry, self.to_label, self.to_entry,
                       self.num_label, self.num_entry, self.order_label, self.order_combo]:
            widget.pack_forget()

        if self.view_mode_var.get() == 'product':
            # Show date range fields
            self.from_label.pack(side='left', padx=(10,2))
            self.from_entry.pack(side='left')
            self.to_label.pack(side='left', padx=(10,2))
            self.to_entry.pack(side='left')
        else:
            # Show number/order controls
            self.num_label.pack(side='left', padx=(10,2))
            self.num_entry.pack(side='left')
            self.order_label.pack(side='left', padx=(10,2))
            self.order_combo.pack(side='left')

        self.refresh_table()
    def refresh_table(self,filter_clicked=False):
        # Validate number of entries
        try:
            value = self.num_var.get()
            limit = int(value) if value else 5
            if limit <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showwarning("Invalid Input", "Please enter a positive integer for number of entries.")
            self.num_var.set(5)
            limit = 5

        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        view_mode = self.view_mode_var.get()
        if view_mode == 'product':
            from_date = self.from_date_var.get().strip()
            to_date = self.to_date_var.get().strip()

            # On initial load, ignore date fields and show all products
            if not filter_clicked:
                data = customer_backend.get_customer_by_date_range()
            else:
                # Only filter if both dates are provided
                if from_date and to_date:
                    try:
                        datetime.strptime(from_date, "%Y-%m-%d")
                        datetime.strptime(to_date, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showwarning("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
                        return
                    data = customer_backend.get_customer_by_date_range(from_date, to_date)
                else:
                    data = customer_backend.get_customer_by_date_range()


            columns = ("Customer", "Product", "Qty", "Price", "Amount", "Date")
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)

            # Show only up to 'limit' entries
            for purchaser, item, qty, price, amount, date in data:

                self.tree.insert('', 'end', values=(purchaser, item, qty, price, amount, date))


        else:
            columns = ("Purchaser", "Payment ID", "Amount", "Date")
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, stretch=True)  # Allow column to expand

            self.tree.pack(expand=True, fill='both')  # Make treeview expand to fill space

            try:
                data = customer_backend.get_recent_customer_payments(order=self.order_var.get(), limit=limit)
                for purchaser, payment_id, amount, date in data:
                    self.tree.insert('', 'end', values=(purchaser, payment_id, amount, date))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch purchase payments: {e}")


    
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

        # Treeview
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

        # Combobox
        style.configure("Custom.TCombobox",
                        fieldbackground=colors["entry_bg"],
                        background=colors["entry_bg"],
                        foreground=colors["fg"])

        # Spinbox (if using ttk.Spinbox)
        style.configure("Custom.TSpinbox",
                        fieldbackground=colors["entry_bg"],
                        background=colors["entry_bg"],
                        foreground=colors["fg"])

        # Entry/DateEntry (if using ttk.Entry or tkcalendar.DateEntry)
        style.configure("Custom.TEntry",
                        fieldbackground=colors["entry_bg"],
                        foreground=colors["fg"],
                        background=colors["entry_bg"])

        # Calendar popup for DateEntry (optional)
        style.configure("Custom.Calendar.Treeview",
                        background=colors["entry_bg"],
                        foreground=colors["fg"],
                        fieldbackground=colors["entry_bg"])




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
            # Do NOT try to set bg/fg for ttk widgets

    def update_theme(self):
        self.configure_theme()
        self.refresh_table()

# Standalone test
if __name__ == "__main__":
    import themes
    def get_colors(): return themes.THEMES[themes.load_theme()]
    root = tk.Tk()
    root.title("Inward General View")
    theme = themes.load_theme()
    root.configure(bg=themes.THEMES[theme]['bg'])
    frame = OutwardGeneralViewFrame(root, theme, get_colors)
    frame.pack(fill="both", expand=True)
    root.mainloop()
