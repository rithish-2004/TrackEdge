import tkinter as tk
from tkinter import ttk
from inward import db_backend
from tkcalendar import DateEntry


class InwardModifyFrame(tk.Frame):
    def __init__(self, parent, theme, get_colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.theme = theme
        self.get_colors = get_colors

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.place_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()


        self.current_name = ""
        self.current_phone = ""
        self.current_place = ""
        
        colors = self.get_colors()
        self.build_title1()
        self.modify_option = tk.StringVar(value="Product")
        
        self.header_frame = tk.Frame(self, bg=colors["bg"])
        self.header_frame.pack(side="top", fill="x")
        self.details_frame = tk.Frame(self, bg=colors["bg"])
        self.details_frame.pack(side="top", fill="x")
        self.modify_frame = tk.Frame(self, bg=colors["bg"])
        self.modify_frame.pack(side="top", fill="x", pady=20)
        
        self.build_search_fields()
        self.modify_option = tk.StringVar(value="Product")
        self.modify_option.trace_add("write", self.on_modify_option_change)
        self.reset_state()
        self.current_name = ""
        self.current_phone = ""
        self.current_place = ""
        self.configure_theme()
            
    def build_title1(self):
        colors = self.get_colors()
        self.title_label1 = tk.Label(self, text="Purchase - Modify options", font=("Arial", 22, "bold"),
                                bg=colors["bg"], fg=colors["fg"])
        self.title_label1.pack(pady=(20, 10))

    def clear_details(self):
        if hasattr(self, 'mod_name_entry') and self.mod_name_entry.winfo_exists():
            self.mod_name_entry.config(state="normal")
            self.mod_name_entry.delete(0, tk.END)
            self.mod_name_entry.config(state="readonly")
        if hasattr(self, 'mod_place_entry') and self.mod_place_entry.winfo_exists():
            self.mod_place_entry.delete(0, tk.END)
        if hasattr(self, 'mod_phone_entry') and self.mod_phone_entry.winfo_exists():
            self.mod_phone_entry.delete(0, tk.END)

    
    # Add similar checks for other widgets


    def configure_theme(self):
        colors = self.get_colors()
        self.configure(bg=colors["bg"])
        self.title_label1.configure(bg=colors["bg"], fg=colors["fg"])

        self.header_frame.configure(bg=colors["bg"])
        self.details_frame.configure(bg=colors["bg"])
        self.modify_frame.configure(bg=colors["bg"])
        self.update_widget_colors(self.header_frame)
        self.update_widget_colors(self.details_frame)
        self.update_widget_colors(self.modify_frame)
        style = ttk.Style()
       
        style.theme_use('clam')
        
        # Configure core styles
        style.configure("Custom.TCombobox", 
                    fieldbackground=colors["entry_bg"],
                    background=colors["entry_bg"],
                    foreground=colors["fg"])
                    
        style.configure("Custom.TEntry",
                    fieldbackground=colors["entry_bg"],
                    foreground=colors["fg"])
                    
        style.configure("TButton",
                    background=colors["button_bg"],
                    foreground=colors["fg"])
        
        # DateEntry specific styling
        style.map('DateEntry',
                fieldbackground=[('readonly', colors["entry_bg"]),
                            ('disabled', colors["entry_bg"])])
        style.configure('DateEntry',
                    foreground=colors["fg"],
                    bordercolor=colors["bg"],
                    arrowcolor=colors["fg"])
    

       


    def update_widget_colors(self, frame):
        colors = self.get_colors()
        for widget in frame.winfo_children():
            if widget.winfo_class() == 'Label':
                widget.configure(bg=colors["bg"], fg=colors["fg"])
            elif widget.winfo_class() == 'Entry':
                widget.configure(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"], readonlybackground=colors["entry_bg"])
            elif widget.winfo_class() == 'Button':
                widget.configure(bg=colors["button_bg"], fg=colors["fg"])
            elif widget.winfo_class() == 'Frame':
                widget.configure(bg=colors["bg"])
                self.update_widget_colors(widget)


    def update_theme(self):
        self.configure_theme()
        self.build_search_fields()
        if self.current_name:
            self.show_purchaser_details(self.current_name, self.current_phone, self.current_place)
        else:
            self.clear_details()
        self.on_modify_option_change()  # This will rebuild the product/filter area with new colors!


    def on_modify_option_change(self, *args):
        if self.modify_option.get() == "Purchaser":
            self.build_modify_fields()
            if self.current_name:
                self.set_modify_fields(self.current_name, self.current_place, self.current_phone)
        elif self.modify_option.get() == "Product":
            if self.current_name and self.current_phone:
                # Always show all products at first (unfiltered)
                products = db_backend.get_products_by_name_phone_and_date(self.current_name, self.current_phone, '', '')
                self.show_product_cards(products)
            else:
                self.show_product_cards([])
        
        elif self.modify_option.get() == "Transactions":
            if self.current_name and self.current_phone:
                self.build_transaction_filter_fields()
            else:
                for widget in self.modify_frame.winfo_children():
                    widget.destroy()
            
        else:
            for widget in self.modify_frame.winfo_children():
                widget.destroy()


    def set_modify_fields(self, name, place, phone):
        if hasattr(self, "mod_name_entry"):
            self.mod_name_entry.config(state="normal")
            self.mod_name_entry.delete(0, tk.END)
            self.mod_name_entry.insert(0, name)
            self.mod_name_entry.config(state="readonly")
        if hasattr(self, "mod_place_entry"):
            self.mod_place_entry.delete(0, tk.END)
            self.mod_place_entry.insert(0, place)
        if hasattr(self, "mod_phone_entry"):
            self.mod_phone_entry.delete(0, tk.END)
            self.mod_phone_entry.insert(0, phone)

    def build_search_fields(self):
        colors = self.get_colors()
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        tk.Label(self.header_frame, text="Name:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(row=0, column=0, padx=5, pady=5)
        self.name_combo = ttk.Combobox(self.header_frame, textvariable=self.name_var, width=20, style="Custom.TCombobox")
        self.name_combo.grid(row=0, column=1, padx=5, pady=5)
        self.name_combo.bind('<KeyRelease>', self.on_name_type)
        self.name_combo.bind('<<ComboboxSelected>>', self.on_name_select)
        tk.Label(self.header_frame, text="Phone Number:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(row=0, column=2, padx=5, pady=5)
        self.phone_combo = ttk.Combobox(self.header_frame, textvariable=self.phone_var, width=15, style="Custom.TCombobox")
        self.phone_combo.grid(row=0, column=3, padx=5, pady=5)
        self.phone_combo.bind('<KeyRelease>', self.on_phone_type)
        self.phone_combo.bind('<<ComboboxSelected>>', self.on_phone_select)
        tk.Label(self.header_frame, text="Place:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(row=0, column=4, padx=5, pady=5)
        self.place_entry = tk.Entry(self.header_frame, textvariable=self.place_var, width=20, bg=colors["entry_bg"], fg=colors["fg"])
        self.place_entry.grid(row=0, column=5, padx=5, pady=5)
        tk.Button(self.header_frame, text="Search", bg=colors["button_bg"], fg=colors["fg"], command=self.on_search).grid(row=0, column=6, padx=10, pady=5)

    def build_modify_fields(self):
        colors = self.get_colors()
        for widget in self.modify_frame.winfo_children():
            widget.destroy()

        center_frame = tk.Frame(self.modify_frame, bg=colors["bg"])
        center_frame.pack(expand=True, anchor="center", pady=10)

        instruction = tk.Label(
            center_frame,
            text="Note: Only Place and Phone Number can be edited.",
            font=("Arial", 11, "italic"),
            bg=colors["bg"],
            fg="#cc6600"
        )
        instruction.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        tk.Label(center_frame, text="Name:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        self.mod_name_entry = tk.Entry(center_frame, width=24, bg=colors["entry_bg"], fg=colors["fg"], 
                                      readonlybackground=colors["entry_bg"], state="readonly")
        self.mod_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(center_frame, text="Place:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(
            row=2, column=0, padx=5, pady=5, sticky="e")
        self.mod_place_entry = tk.Entry(center_frame, width=24, bg=colors["entry_bg"], fg=colors["fg"])
        self.mod_place_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(center_frame, text="Phone:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(
            row=3, column=0, padx=5, pady=5, sticky="e")
        self.mod_phone_entry = tk.Entry(center_frame, width=24, bg=colors["entry_bg"], fg=colors["fg"])
        self.mod_phone_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        update_btn = tk.Button(
            center_frame,
            text="Update Details",
            bg=colors["button_bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            command=self.on_update_details
        )
        update_btn.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")

        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)

    def reset_state(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.place_var.set("")
        self.current_name = ""
        self.current_phone = ""
        self.current_place = ""
        if hasattr(self, "mod_name_entry"):
            self.mod_name_entry.config(state="normal")
            self.mod_name_entry.delete(0, tk.END)
            self.mod_name_entry.config(state="readonly")
        if hasattr(self, "mod_place_entry"):
            self.mod_place_entry.delete(0, tk.END)
        if hasattr(self, "mod_phone_entry"):
            self.mod_phone_entry.delete(0, tk.END)
        for widget in self.details_frame.winfo_children():
            widget.destroy()



    def on_search(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        place = self.place_var.get().strip()
        self.show_purchaser_details(name, phone, place)

    def on_name_type(self, event):
        prefix = self.name_var.get()
        words = prefix.strip().split()
        if not words:
            self.name_combo['values'] = []
            return
        results = db_backend.search_purchasers_by_name_words(words)
        names = [r[0] for r in results]
        self.name_combo['values'] = names

    def on_name_select(self, event):
        selected_name = self.name_var.get()
        result = db_backend.get_purchaser_by_name(selected_name)
        if result:
            self.phone_var.set(result[1])
            self.place_var.set(result[2])
            self.show_purchaser_details(result[0], result[1], result[2])

    def on_phone_type(self, event):
        prefix = self.phone_var.get()
        results = db_backend.search_purchasers_by_phone(prefix)
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones

    def on_phone_select(self, event):
        selected_phone = self.phone_var.get()
        result = db_backend.get_purchaser_by_phone(selected_phone)
        if result:
            self.name_var.set(result[0])
            self.place_var.set(result[2])
            self.show_purchaser_details(result[0], result[1], result[2])

    def show_purchaser_details(self, name, phone, place):
        self.current_name = name
        self.current_phone = phone
        self.current_place = place
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        colors = self.get_colors()
        self.title_label = tk.Label(
            self.details_frame,
            text="Purchaser Details",
            font=("Arial", 14, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.title_label.pack(anchor="w", padx=10, pady=5)

        info_frame = tk.Frame(self.details_frame, bg=colors["bg"])
        info_frame.pack(anchor="w", padx=10, pady=5)
        tk.Label(info_frame, text="Name:", font=("Arial", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side="left")
        tk.Label(info_frame, text=name, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=(0, 10))
        tk.Label(info_frame, text="Phone:", font=("Arial", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side="left")
        tk.Label(info_frame, text=phone, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=(0, 10))
        tk.Label(info_frame, text="Place:", font=("Arial", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side="left")
        tk.Label(info_frame, text=place, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(side="left")

        try:
            purchases = db_backend.get_purchases_by_name_phone(name, phone)
        except Exception:
            purchases = []

        self.total_amount = sum(p[1] for p in purchases)
        self.total_paid = sum(p[2] for p in purchases)
        self.remaining = sum(p[3] for p in purchases)
        any_pending = any(p[4] == "pending" for p in purchases)

        if self.remaining == 0:
            status_text = "Completed"
            status_bg = "#ccffcc"
            status_fg = "#006600"
        else:
            status_text = "Pending"
            status_bg = "#ffcccc"
            status_fg = "#a80000"


        if self.remaining < 0:
            refund_due = abs(self.remaining)
            to_pay_text = f"Refund Due: {refund_due:.2f}"
        else:
            to_pay_text = f"To Pay: {self.remaining:.2f}"

        self.summary_label = tk.Label(
            self.details_frame,
            text=f"Status: {status_text}    Total: {self.total_amount:.2f}    Paid: {self.total_paid:.2f}    {to_pay_text}",
            font=("Arial", 12, "bold"),
            bg=status_bg,
            fg=status_fg
        )

        self.summary_label.pack(anchor="w", padx=10, pady=(5, 10), fill="x")
        # --- Radio Buttons for Modify Options ---
        radio_frame = tk.Frame(self.details_frame, bg=colors["bg"])
        radio_frame.pack(anchor="w", padx=10, pady=(0, 10))

        tk.Label(radio_frame, text="Modify:", font=("Arial", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=(0, 10))

        options = [("Product", "Product"), ("Transactions", "Transactions"), ("Purchaser", "Purchaser")]
        for text, value in options:
            tk.Radiobutton(
                radio_frame,
                text=text,
                variable=self.modify_option,
                value=value,
                font=("Arial", 11),
                bg=colors["bg"],
                fg=colors["fg"],
                selectcolor=colors["entry_bg"],
                activebackground=colors["bg"],
                activeforeground=colors["fg"]
            ).pack(side="left", padx=5)
        self.on_modify_option_change()
        # Only update modify fields if Purchaser is selected
        if self.modify_option.get() == "Purchaser":
            if hasattr(self, "mod_name_entry"):
                self.mod_name_entry.config(state="normal")
                self.mod_name_entry.delete(0, tk.END)
                self.mod_name_entry.insert(0, name)
                self.mod_name_entry.config(state="readonly")
            if hasattr(self, "mod_place_entry"):
                self.mod_place_entry.delete(0, tk.END)
                self.mod_place_entry.insert(0, place)
            if hasattr(self, "mod_phone_entry"):
                self.mod_phone_entry.delete(0, tk.END)
                self.mod_phone_entry.insert(0, phone)



    def show_themed_confirmation(self, name, place, phone):
        colors = self.get_colors()
        msg = f"Purchaser details updated to:\n\nName: {name}\nPlace: {place}\nPhone: {phone}"
        win = tk.Toplevel(self)
        win.title("Details Updated")
        win.configure(bg=colors["bg"])
        win.resizable(False, False)
        win.geometry("+%d+%d" % (
            self.winfo_rootx() + self.winfo_width() // 2 - 150,
            self.winfo_rooty() + self.winfo_height() // 2 - 60
        ))
        tk.Label(
            win,
            text=msg,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            wraplength=300,
            justify="center"
        ).pack(padx=20, pady=(20, 10))
        tk.Button(
            win,
            text="OK",
            command=win.destroy,
            bg=colors["button_bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            relief="raised"
        ).pack(pady=(0, 20))
        win.transient(self)
        win.grab_set()
        win.wait_window()

    def on_update_details(self):
        new_phone = self.mod_phone_entry.get().strip()
        new_place = self.mod_place_entry.get().strip()
        name = self.mod_name_entry.get().strip()
        if not new_phone.isdigit() or len(new_phone) != 10:
            self.show_themed_error("Invalid Phone", "Phone number must be exactly 10 digits.")
            return
        if not new_phone or not new_place:
            self.show_themed_error("Input Error", "Phone number and place cannot be empty.")
            return
        other = db_backend.get_purchaser_by_phone(new_phone)
        if other and (other[0] != name or other[2] != self.current_place):
            self.show_themed_error("Phone Exists", f"Phone number {new_phone} is already used by another purchaser.")
            return
        updated = db_backend.update_purchaser_phone_place(
            old_name=name,
            old_place=self.current_place,
            new_phone=new_phone,
            new_place=new_place
        )
        if updated:
            self.show_themed_confirmation(name, new_place, new_phone)
            self.reset_state()
        else:
            self.show_themed_error("Update Failed", "Could not update purchaser details.")

    def show_themed_error(self, title, msg):
        colors = self.get_colors()
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=colors["bg"])
        win.resizable(False, False)
        win.geometry("+%d+%d" % (
            self.winfo_rootx() + self.winfo_width() // 2 - 150,
            self.winfo_rooty() + self.winfo_height() // 2 - 60
        ))
        tk.Label(
            win,
            text=msg,
            bg=colors["bg"],
            fg="#a80000",
            font=("Arial", 12, "bold"),
            wraplength=300,
            justify="center"
        ).pack(padx=20, pady=(20, 10))
        tk.Button(
            win,
            text="OK",
            command=win.destroy,
            bg=colors["button_bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            relief="raised"
        ).pack(pady=(0, 20))
        win.transient(self)
        win.grab_set()
        win.wait_window()

    def show_product_cards(self, products):
        colors = self.get_colors()
        card_bg = colors.get("card_bg", "#f0f0f0")

        for widget in self.modify_frame.winfo_children():
            widget.destroy()

        # --- Outer grid container ---
        outer_frame = tk.Frame(self.modify_frame, bg=colors["bg"])
        outer_frame.grid(row=0, column=0, sticky="nsew")
        self.modify_frame.grid_rowconfigure(0, weight=1)
        self.modify_frame.grid_columnconfigure(0, weight=1)

        # --- Filter UI ---
        filter_frame = tk.Frame(outer_frame, bg=colors["bg"])
        filter_frame.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        outer_frame.grid_columnconfigure(0, weight=1)

        # In your show_product_cards or filter UI creation:
        start_date_value = self.start_date_var.get()
        start_date_entry = DateEntry(
            filter_frame, textvariable=self.start_date_var, date_pattern='yyyy-mm-dd', width=12,
            background=colors["entry_bg"], foreground=colors["fg"], borderwidth=1,
            readonlybackground=colors["entry_bg"], disabledbackground=colors["entry_bg"]
        )
        start_date_entry.pack(side="left", padx=5)
        if start_date_value:
            start_date_entry.set_date(start_date_value)
        else:
            start_date_entry._set_text('')  # This clears the field without setting to today

        end_date_value = self.end_date_var.get()
        end_date_entry = DateEntry(
            filter_frame, textvariable=self.end_date_var, date_pattern='yyyy-mm-dd', width=12,
            background=colors["entry_bg"], foreground=colors["fg"], borderwidth=1,
            readonlybackground=colors["entry_bg"], disabledbackground=colors["entry_bg"]
        )
        end_date_entry.pack(side="left", padx=5)
        if end_date_value:
            end_date_entry.set_date(end_date_value)
        else:
            end_date_entry._set_text('')


        tk.Button(filter_frame, text="Filter Dates", bg=colors["button_bg"], fg=colors["fg"], command=self.apply_date_filter).pack(side="left", padx=10)
        tk.Button(filter_frame, text="Reset", bg=colors["button_bg"], fg=colors["fg"], command=self.reset_date_filter).pack(side="left", padx=5)

        # --- Table area ---
        table_container = tk.Frame(outer_frame, bg=colors["bg"])
        table_container.grid(row=1, column=0, sticky="nsew")
        outer_frame.grid_rowconfigure(1, weight=1)

        # Scrollable canvas
        table_canvas = tk.Canvas(table_container, bg=colors["bg"], highlightthickness=0)
        table_canvas.grid(row=0, column=0, sticky="nsew")
        table_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=table_canvas.yview)
        table_scrollbar.grid(row=0, column=1, sticky="ns")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        table_frame = tk.Frame(table_canvas, bg=colors["bg"])
        table_canvas.create_window((0, 0), window=table_frame, anchor="nw")
        table_canvas.configure(yscrollcommand=table_scrollbar.set)

        def on_canvas_configure(event):
            table_canvas.itemconfig("table_frame", width=event.width)
        table_canvas.bind("<Configure>", lambda event: table_canvas.itemconfig(table_canvas.find_withtag("table_frame"), width=event.width))

        # --- Table Header with Actions ---
        headers = ["Item", "Qty", "Price", "Description", "Amount", "Date", "Actions"]
        for col, h in enumerate(headers):
            tk.Label(table_frame, text=h, bg=colors["bg"], fg=colors["fg"], font=("Arial", 10, "bold"),
                    borderwidth=1, relief="solid", anchor="center").grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        # --- Table Rows ---
        for row_idx, product in enumerate(products, start=1):
            for col_idx, value in enumerate(product):
                display_value = value
                if headers[col_idx] in ["Price", "Amount"]:
                    try:
                        display_value = f"₹{float(value):.2f}"
                    except Exception:
                        display_value = str(value)
                tk.Label(table_frame, text=display_value, bg=card_bg, fg=colors["fg"], borderwidth=1,
                        relief="solid", anchor="center").grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
            # Actions column with Edit and Delete
            actions_frame = tk.Frame(table_frame, bg=card_bg)
            actions_frame.grid(row=row_idx, column=len(headers)-1, sticky="nsew", padx=1, pady=1)
            tk.Button(actions_frame, text="Edit", bg=colors["button_bg"], fg=colors["fg"],
          command=lambda p=product: self.show_edit_form(p), width=6).pack(side="left", padx=2)

            tk.Button(actions_frame, text="Delete", bg=colors["button_bg"], fg=colors["fg"],
                    command=lambda p=product: self.on_delete_product(p), width=6).pack(side="left", padx=2)
       


        # --- Make columns expand equally ---
        for col in range(len(headers)):
            table_frame.grid_columnconfigure(col, weight=1)


    def reset_date_filter(self):
        self.start_date_var.set("")
        self.end_date_var.set("")
        # Now the DateEntry will be blank until user picks a date
        products = db_backend.get_products_by_name_phone_and_date(
            self.current_name, self.current_phone, None, None
        )
        self.show_product_cards(products)

    def apply_date_filter(self):
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()
        if not start_date and not end_date:
            return
        products = db_backend.get_products_by_name_phone_and_date(
            self.current_name, self.current_phone, start_date, end_date
        )
        self.show_product_cards(products)

    def show_edit_form(self, product):
        colors = self.get_colors()

        # Remove any existing edit frame
        if hasattr(self, "edit_frame") and self.edit_frame is not None:
            self.edit_frame.destroy()

        # Unpack the product tuple (item, qty, price, description, amount, date)
        try:
            item, qty, price, description, amount, date = product
        except Exception:
            tk.messagebox.showerror("Error", "Product details are incomplete.")
            return

        self.edit_frame = tk.Frame(self.modify_frame, bg=colors["bg"], bd=2, relief="groove", width=200)
        self.edit_frame.grid(row=0, column=1, sticky="ns", padx=5, pady=3)
        self.edit_frame.grid_propagate(False)  # Prevents shrinking to fit contents

        self.modify_frame.grid_columnconfigure(1, weight=0)

        tk.Label(self.edit_frame, text="Edit Product", font=("Arial", 13, "bold"),
                bg=colors["bg"], fg=colors["fg"]).pack(pady=(2, 5))
        tk.Label(
    self.edit_frame,
    text="Note: You can only edit Item Name and Description.",
    font=("Arial", 11, "italic"),
    bg=colors["bg"],
    fg="#cc6600"  # Orange/brown for 'note'
).pack(fill="x", padx=5, pady=(3, 5))


        # Item Name (editable)
        tk.Label(self.edit_frame, text="Item Name:", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=5)
        self.edit_item_var = tk.StringVar(value=item)
        tk.Entry(self.edit_frame, textvariable=self.edit_item_var, bg=colors["entry_bg"], fg=colors["fg"]).pack(fill="x", padx=10, pady=3)

       # Quantity (readonly)
        tk.Label(self.edit_frame, text="Quantity:", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=5)
        tk.Label(self.edit_frame, text=str(qty), bg=colors["entry_bg"], fg=colors["fg"], anchor="w").pack(fill="x", padx=10, pady=3)

        # Price (readonly)
        # Price (display only)
        tk.Label(self.edit_frame, text="Price:", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=5)
        tk.Label(self.edit_frame, text=str(price), bg=colors["entry_bg"], fg=colors["fg"], anchor="w").pack(fill="x", padx=10, pady=3)

        # Description (editable)
        tk.Label(self.edit_frame, text="Description:", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=5)
        self.edit_desc_var = tk.StringVar(value=description)
        tk.Entry(self.edit_frame, textvariable=self.edit_desc_var, bg=colors["entry_bg"], fg=colors["fg"]).pack(fill="x", padx=10, pady=3)

        # Amount (readonly)
        tk.Label(self.edit_frame, text="Amount:", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=5)
        tk.Label(self.edit_frame, text=str(amount), bg=colors["entry_bg"], fg=colors["fg"], anchor="w").pack(fill="x", padx=10, pady=3)

        # Buttons
        btn_frame = tk.Frame(self.edit_frame, bg=colors["bg"])
        btn_frame.pack(pady=15, fill="x")

        tk.Button(
            btn_frame,
            text="Update",
            bg=colors["button_bg"],
            fg=colors["fg"],
            command=lambda: self.update_product(product)
        ).pack(side="left", padx=10, ipadx=10)

        tk.Button(
    btn_frame,
    text="Return Product",
    bg=colors["button_bg"],
    fg=colors["fg"],
    font=("Arial", 12, "bold"),
    command=lambda: self.show_return_form(product)
).pack(side="left", padx=10, ipadx=10)


        tk.Button(
            btn_frame,
            text="Cancel",
            bg=colors["button_bg"],
            fg=colors["fg"],
            command=lambda: [self.show_themed_message("Cancelling update...", title="Cancelled"), self.edit_frame.destroy()]
        ).pack(side="left", padx=10, ipadx=10)

    def update_product(self, old_product):
        new_item = self.edit_item_var.get().strip()
        new_desc = self.edit_desc_var.get().strip()
        item, qty, price, description, amount, date = old_product

        prod_id = db_backend.get_product_id_by_details(
            self.current_name, self.current_phone, item, qty, price, description, amount, date
        )

        if prod_id is None:
            self.show_themed_message("Could not find the product to update.", title="Error")
            return

        changed_name = (new_item != item)
        changed_desc = (new_desc != description)

        if not changed_name and not changed_desc:
            self.show_themed_confirmation("No changes made.", title="Info")
            return

        success = db_backend.update_product_by_id(prod_id, new_item, new_desc)
        if success:
            products = db_backend.get_products_by_name_phone_and_date(
                self.current_name, self.current_phone, self.start_date_var.get(), self.end_date_var.get())
            self.show_product_cards(products)
            if hasattr(self, "edit_frame") and self.edit_frame is not None:
                self.edit_frame.destroy()
            if changed_name and changed_desc:
                self.show_themed_message("Product name and description updated successfully!", title="Product Updated")
            elif changed_name:
                self.show_themed_message("Product name updated successfully!", title="Product Updated")
            elif changed_desc:
                self.show_themed_message("Product description updated successfully!", title="Product Updated")
        else:
            self.show_themed_message("Failed to update the product.", title="Error")

    def show_themed_message(self, message, title="Success"):
        colors = self.get_colors()
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=colors["bg"])
        win.resizable(False, False)
        win.geometry("+%d+%d" % (
            self.winfo_rootx() + self.winfo_width() // 2 - 150,
            self.winfo_rooty() + self.winfo_height() // 2 - 60
        ))
        tk.Label(
            win,
            text=message,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            wraplength=300,
            justify="center"
        ).pack(padx=20, pady=(20, 10))
        tk.Button(
            win,
            text="OK",
            command=win.destroy,
            bg=colors["button_bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            relief="raised"
        ).pack(pady=(0, 20))
        win.transient(self)
        win.grab_set()
        win.wait_window()

    def show_return_form(self, product):
        colors = self.get_colors()
        item, qty, price, description, amount, date = product

        # --- Get previous form size ---
        width, height = 400, 350  # default values
        if hasattr(self, "edit_frame") and self.edit_frame is not None:
            self.edit_frame.update_idletasks()
            width = self.edit_frame.winfo_width()
            height = self.edit_frame.winfo_height()
            self.edit_frame.destroy()

        # --- Remove any existing return frame ---
        if hasattr(self, "return_frame") and self.return_frame is not None:
            self.return_frame.destroy()

        self.return_frame = tk.Frame(self.modify_frame, bg=colors["bg"], bd=2, relief="groove", width=width, height=height)
        self.return_frame.grid(row=0, column=1, sticky="ns", padx=15, pady=10)
        self.return_frame.grid_propagate(False)

        tk.Label(self.return_frame, text="Return Product", font=("Arial", 13, "bold"),
                bg=colors["bg"], fg=colors["fg"]).pack(pady=(10, 15))

        # Show product info (not editable)
        tk.Label(self.return_frame, text=f"Item: {item}", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=10)
        tk.Label(self.return_frame, text=f"Description: {description}", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=10)
        tk.Label(self.return_frame, text=f"Available Quantity: {qty}", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=10)
        tk.Label(self.return_frame, text=f"Price per unit: {price}", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=10)
        tk.Label(self.return_frame, text=f"Total Amount: {amount}", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=10)

        # Editable quantity to return
        tk.Label(self.return_frame, text="Return Quantity:", bg=colors["bg"], fg=colors["fg"]).pack(anchor="w", padx=10, pady=(10, 0))
        return_qty_var = tk.IntVar(value=1)
        qty_entry = tk.Entry(self.return_frame, textvariable=return_qty_var, bg=colors["entry_bg"], fg=colors["fg"])
        qty_entry.pack(fill="x", padx=10, pady=3)

        def process_return():
            try:
                return_qty = int(return_qty_var.get())
                if return_qty < 1:
                    raise ValueError
                if return_qty > qty:
                    self.show_themed_message("Return quantity cannot be more than available quantity.", title="Invalid Quantity")
                    return
                if return_qty == qty:
                    self.show_themed_message("You can delete the product instead of returning.", title="Full Return Not Allowed")
                    return
            except Exception:
                self.show_themed_message("Enter a valid quantity to return.", title="Invalid Quantity")
                return

            refund_amount = return_qty * price
            new_qty = qty - return_qty
            new_amount = new_qty * price

            # --- Find product row id ---
            product_id = db_backend.get_product_id_by_details(
                self.current_name, self.current_phone, item, qty, price, description, amount, date
            )
            if not product_id:
                self.show_themed_message("Product not found for return.", title="Error")
                return

            # --- Update product in DB ---
            db_backend.update_product_quantity_and_amount_by_id(product_id, new_qty, new_amount)

            # --- Update purchaser in DB ---
            purchases = db_backend.get_purchases_by_name_phone(self.current_name, self.current_phone)
            if purchases:
                purchaser_id, total_amount, amount_paid, remaining_amount, status, pdate = purchases[0]
                new_total = total_amount - refund_amount
                new_remaining = remaining_amount - refund_amount
                db_backend.update_purchaser_amounts(purchaser_id, new_total, new_remaining)
                new_paid = db_backend.get_amount_paid_by_purchaser_id(purchaser_id)

                # Decide status based on new totals
                if new_total == new_paid and new_remaining == 0:
                    db_backend.update_purchaser_status(purchaser_id, "Completed")
                else:
                    db_backend.update_purchaser_status(purchaser_id, "Pending")



            # Confirmation
            self.show_themed_message(
                f"Returned {return_qty} units of '{item}'.\nRefund the Amount: {refund_amount:.2f}\nif you paid it already.",
                title="Return Processed"
            )
            self.return_frame.destroy()
            self.on_modify_option_change()
            self.show_purchaser_details(self.current_name, self.current_phone, self.current_place)

        btn_frame = tk.Frame(self.return_frame, bg=colors["bg"])
        btn_frame.pack(pady=15, fill="x")
        tk.Button(btn_frame, text="Process Return", bg=colors["button_bg"], fg=colors["fg"],
                command=process_return).pack(side="left", padx=10, ipadx=10)
        tk.Button(btn_frame, text="Cancel", bg=colors["button_bg"], fg=colors["fg"],
                command=self.return_frame.destroy).pack(side="left", padx=10, ipadx=10)
    
    def on_delete_product(self, product):
        colors = self.get_colors()
        item, qty, price, description, amount, date = product

        # Themed confirmation dialog
        confirm_win = tk.Toplevel(self)
        confirm_win.title("Delete Product")
        confirm_win.configure(bg=colors["bg"])
        confirm_win.resizable(False, False)
        confirm_msg = f"Are you sure you want to delete '{item}' ({qty} units)?\nThis will remove {amount:.2f} from the purchaser's total."
        tk.Label(confirm_win, text="Confirm Delete", font=("Arial", 13, "bold"), bg=colors["bg"], fg="#a80000").pack(padx=20, pady=(15, 5))
        tk.Label(confirm_win, text=confirm_msg, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"], wraplength=350, justify="center").pack(padx=20, pady=(0, 15))
        btn_frame = tk.Frame(confirm_win, bg=colors["bg"])
        btn_frame.pack(pady=(0, 15))
        tk.Button(btn_frame, text="Delete", bg="#a80000", fg="white", font=("Arial", 12, "bold"),
                command=lambda: self._delete_product_confirmed(product, confirm_win)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", bg=colors["button_bg"], fg=colors["fg"], font=("Arial", 12, "bold"),
                command=confirm_win.destroy).pack(side="left", padx=10)
        confirm_win.transient(self)
        confirm_win.grab_set()
        self.center_window(confirm_win)

    
    def center_window(self, win):
        win.update_idletasks()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        win_width = win.winfo_width()
        win_height = win.winfo_height()
        x = parent_x + (parent_width // 2) - (win_width // 2)
        y = parent_y + (parent_height // 2) - (win_height // 2)
        win.geometry(f"+{x}+{y}")
    
    def _delete_product_confirmed(self, product, confirm_win):
        item, qty, price, description, amount, date = product

        # Get product id
        product_id = db_backend.get_product_id_by_details(
            self.current_name, self.current_phone, item, qty, price, description, amount, date
        )
        if not product_id:
            confirm_win.destroy()
            self.show_themed_error("Product not found for deletion.", "Error")
            return
        purchases = db_backend.get_purchases_by_name_phone(self.current_name, self.current_phone)
        db_backend.delete_product_by_id(product_id)

        # Update purchaser totals
        purchases = db_backend.get_purchases_by_name_phone(self.current_name, self.current_phone)
        if purchases:
            purchaser_id, total_amount, amount_paid, remaining_amount, status, pdate = purchases[0]
            new_total = total_amount - amount
            new_remaining = remaining_amount - amount
            db_backend.update_purchaser_amounts(purchaser_id, new_total, new_remaining)
            if new_remaining == 0:
                db_backend.update_purchaser_status(purchaser_id, "Completed")
            else:
                db_backend.update_purchaser_status(purchaser_id, "Pending")
        
        confirm_win.destroy()
        self.on_modify_option_change()  # Refresh product cards
        self.show_purchaser_details(self.current_name, self.current_phone, self.current_place)  # Refresh summary/details
        #self.show_product_deleted_confirmation(item, qty, amount)  # Show confirmation LAST

    def show_product_deleted_confirmation(self, item, qty, amount):
        colors = self.get_colors()
        msg = f"Product '{item}' ({qty} units) deleted.\nAmount {amount:.2f} removed from purchaser's total."
        win = tk.Toplevel(self)
        win.title("Product Deleted")
        win.configure(bg=colors["bg"])
        win.resizable(False, False)
        win.geometry("+%d+%d" % (
            self.winfo_rootx() + self.winfo_width() // 2 - 150,
            self.winfo_rooty() + self.winfo_height() // 2 - 60
        ))
        tk.Label(
            win,
            text=msg,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            wraplength=300,
            justify="center"
        ).pack(padx=20, pady=(20, 10))
        tk.Button(
            win,
            text="OK",
            command=win.destroy,
            bg=colors["button_bg"],
            fg=colors["fg"],
            font=("Arial", 12, "bold"),
            relief="raised"
        ).pack(pady=(0, 20))
        win.transient(self)
        win.grab_set()
        win.wait_window()
    
    def show_transaction_cards(self, transactions):
        colors = self.get_colors()
        # Clear only the transaction area (not the filter)
        for widget in self.left_frame.winfo_children():
            if isinstance(widget, tk.Canvas) or isinstance(widget, tk.Scrollbar):
                widget.destroy()

    # ... rest of your code for scrollable cards ...

        # --- Scrollable area ---
        canvas = tk.Canvas(self.left_frame, bg=colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=canvas.yview,
                                troughcolor=colors["bg"], bg=colors["button_bg"], 
                                activebackground=colors["button_bg"])
        scroll_frame = tk.Frame(canvas, bg=colors["bg"])

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not transactions:
            tk.Label(scroll_frame, text="No payments found.", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(pady=20, fill="x")
            return

        for txn in transactions:
            date, payment_id, purchaser_id, amount_paid = txn
            card = tk.Frame(scroll_frame, bg=colors["entry_bg"], bd=1, relief="solid")
            card.pack(fill="x", padx=10, pady=5, expand=True)
            # Make the card expand to the width of the scroll_frame
            card.grid_columnconfigure(0, weight=1)
            tk.Label(card, text=f"Date: {date}", bg=colors["entry_bg"], fg=colors["fg"], font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=2)
            tk.Label(card, text=f"Amount Paid: {amount_paid:.2f}", bg=colors["entry_bg"], fg=colors["fg"], font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=10)
            tk.Label(card, text=f"Payment ID: {payment_id}", bg=colors["entry_bg"], fg=colors["fg"], font=("Arial", 11)).grid(row=2, column=0, sticky="w", padx=10)

    def build_transaction_filter_fields(self):
        colors = self.get_colors()
        # Clear the modify_frame before creating new frames
        for widget in self.modify_frame.winfo_children():
            widget.destroy()

        # Create left and right frames
        self.left_frame = tk.Frame(self.modify_frame, bg=colors["bg"], width=500)
        self.left_frame.pack(side="left", fill="both", expand=True)
        self.right_frame = tk.Frame(self.modify_frame, bg=colors["bg"])
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Reset date vars to blank
        self.start_date_var.set("")
        self.end_date_var.set("")

        # Date filter widgets in left_frame
        filter_frame = tk.Frame(self.left_frame, bg=colors["bg"])
        filter_frame.pack(anchor="w", padx=10, pady=10, fill="x")

        tk.Label(filter_frame, text="From:", bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=(0, 5))
        start_entry = DateEntry(
            filter_frame, textvariable=self.start_date_var, width=12,
            background=colors["entry_bg"], foreground=colors["fg"],
            bordercolor=colors["bg"], headersbackground=colors["entry_bg"],
            headersforeground=colors["fg"], selectbackground=colors["button_bg"],
            selectforeground=colors["fg"], date_pattern="yyyy-mm-dd"
        )
        start_entry.pack(side="left", padx=(0, 10))
        tk.Label(filter_frame, text="To:", bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=(0, 5))
        end_entry = DateEntry(
            filter_frame, textvariable=self.end_date_var, width=12,
            background=colors["entry_bg"], foreground=colors["fg"],
            bordercolor=colors["bg"], headersbackground=colors["entry_bg"],
            headersforeground=colors["fg"], selectbackground=colors["button_bg"],
            selectforeground=colors["fg"], date_pattern="yyyy-mm-dd"
        )
        end_entry.pack(side="left", padx=(0, 10))
        tk.Button(filter_frame, text="Filter", bg=colors["button_bg"], fg=colors["fg"], command=self.on_transaction_filter).pack(side="left", padx=10)

        # Show all transactions initially
        transactions = db_backend.get_transactions_by_name_phone_and_date(self.current_name, self.current_phone, '', '')
        self.show_transaction_cards(transactions)
        self.build_refund_form(self.right_frame)



    def on_transaction_filter(self):
        name = self.current_name
        phone = self.current_phone
        start = self.start_date_var.get().strip()
        end = self.end_date_var.get().strip()
        transactions = db_backend.get_transactions_by_name_phone_and_date(name, phone, start, end)
        self.show_transaction_cards(transactions)
    
    def build_refund_form(self, parent):
        colors = self.get_colors()
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="Mark Refunded Amount", font=("Arial", 14, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(pady=(20, 10))

        # Show max refund if overpaid
        max_refund = abs(self.remaining) if self.remaining < 0 else 0
        tk.Label(parent, text=f"Max Refundable: {max_refund:.2f}", font=("Arial", 11, "italic"), bg=colors["bg"], fg=colors["fg"]).pack(pady=(0, 10))

        tk.Label(parent, text="Refund Amount:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(pady=(10, 0))
        refund_amount_var = tk.StringVar()
        entry = tk.Entry(parent, textvariable=refund_amount_var, font=("Arial", 12), bg=colors["entry_bg"], fg=colors["fg"])
        entry.pack(pady=10, padx=30, fill="x")

        def on_refund():
            try:
                refund_amt = float(refund_amount_var.get())
                if refund_amt <= 0:
                    raise ValueError
            except ValueError:
                self.show_themed_error("Invalid Amount", "Please enter a valid refund amount.")
                return

            if refund_amt > max_refund:
                self.show_themed_error(
                    "Amount Exceeds Refund Due",
                    f"Enter an amount within the refundable range (max: {max_refund:.2f})."
                )
                return

            purchaser = db_backend.get_refund_purchaser_by_name_phone(self.current_name, self.current_phone)
            if not purchaser:
                self.show_themed_error("Error", "Purchaser not found.")
                return
            purchaser_id = purchaser[0]
            import datetime
            payment_id = f"REFUND-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            remarks = f"CREDITED {refund_amt:.2f}"

            success = db_backend.add_purchase_payment(
                purchaser_id, payment_id, now, refund_amt, transaction_type='credit', remarks=remarks
            )
            if success:
                self.show_themed_message("Refunded", f"Credited {refund_amt:.2f} is noted.")
                refund_amount_var.set("")
                self.show_purchaser_details(self.current_name, self.current_phone, self.current_place)
                self.on_transaction_filter()
            else:
                self.show_themed_error("Error", "Failed to mark refund.")

        tk.Button(parent, text="Mark Refunded", bg=colors["button_bg"], fg=colors["fg"], command=on_refund).pack(pady=15, padx=30, fill="x")
