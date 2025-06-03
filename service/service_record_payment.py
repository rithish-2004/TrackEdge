import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from service import service_backend

class ServiceRecordPaymentFrame(tk.Frame):
    def __init__(self, parent, theme, get_colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.theme = theme
        self.get_colors = get_colors

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.place_var = tk.StringVar()
        self.amount_var = tk.StringVar()

        self.current_name = ""
        self.current_phone = ""
        self.current_place = ""
        self.current_service_id = ""

        self.total_amount = 0.0
        self.total_paid = 0.0
        self.remaining = 0.0

        colors = self.get_colors()
        self.topic_label = tk.Label(
            self,
            text="Service - Record Payment",
            font=("Arial", 20, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.topic_label.pack(side="top", pady=(15, 5))
        self.header_frame = tk.Frame(self, bg=colors["bg"])
        self.header_frame.pack(side="top", fill="x")
        self.details_frame = tk.Frame(self, bg=colors["bg"])
        self.details_frame.pack(side="top", fill="x")
        self.amount_frame = tk.Frame(self, bg=colors["bg"])
        self.amount_frame.pack(side="top", fill="x", pady=10)

        self.build_search_fields()
        self.show_service_details("", "", "")
        self.build_amount_entry()

        # --- Divider after Record Payment button ---
        self.after_payment_divider = tk.Frame(self, bg=colors["fg"], height=2)
        self.after_payment_divider.pack(fill="x", padx=10, pady=(5, 15))

        # --- Centered Heading for Spare/Additional Payment ---
        self.spare_label = tk.Label(
            self,
            text="Add Spare/Additional Payment",
            font=("Arial", 20, "bold"),  # Same as main heading
            bg=colors["bg"],
            fg=colors["fg"],
            anchor="center",
            justify="center"
        )
        self.spare_label.pack(fill="x", padx=10, pady=(0, 5))

        # --- Entry and Button for Spare Payment ---
        self.spare_amount_var = tk.StringVar()
        self.spare_amount_entry = tk.Entry(
            self,
            textvariable=self.spare_amount_var,
            width=15,
            bg=colors["entry_bg"],
            fg=colors["fg"]
        )
        self.spare_amount_entry.pack(anchor="center", padx=10, pady=(0, 8))

        self.add_spare_btn = tk.Button(
            self,
            text="Add to Total Amount",
            font=("Arial", 12, "bold"),
            bg=colors["button_bg"],
            fg=colors["fg"],
            command=self.on_add_spare_amount
        )
        self.add_spare_btn.pack(anchor="center", padx=10, pady=(0, 10))

        self.configure_theme()

    def show_themed_confirmation(self, amount, name, place, status):
        colors = self.get_colors()
        msg = f"{amount:.2f} is paid to {name}, {place}. Status: {status.capitalize()}."
        win = tk.Toplevel(self)
        win.title("Payment Recorded")
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

    def configure_theme(self):
        colors = self.get_colors()
        self.configure(bg=colors["bg"])
        if hasattr(self, 'topic_label'):
            self.topic_label.configure(bg=colors["bg"], fg=colors["fg"])
        self.header_frame.configure(bg=colors["bg"])
        self.details_frame.configure(bg=colors["bg"])
        self.amount_frame.configure(bg=colors["bg"])
        self.update_widget_colors(self.header_frame)
        self.update_widget_colors(self.details_frame)
        self.update_widget_colors(self.amount_frame)
        # Update divider and spare payment widgets
        if hasattr(self, 'after_payment_divider'):
            self.after_payment_divider.configure(bg=colors["fg"])
        if hasattr(self, 'spare_label'):
            self.spare_label.configure(bg=colors["bg"], fg=colors["fg"])
        if hasattr(self, 'spare_amount_entry'):
            self.spare_amount_entry.configure(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"])
        if hasattr(self, 'add_spare_btn'):
            self.add_spare_btn.configure(bg=colors["button_bg"], fg=colors["fg"])
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TCombobox", fieldbackground=colors["entry_bg"], background=colors["entry_bg"], foreground=colors["fg"])
        style.configure("Custom.TEntry", fieldbackground=colors["entry_bg"], background=colors["entry_bg"], foreground=colors["fg"])
        style.configure("TButton", background=colors["button_bg"], foreground=colors["fg"])

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

    def validate_amount_color_only(self, event=None):
        val = self.amount_var.get().strip()
        try:
            amt = float(val)
            if amt < 0 or amt > self.remaining:
                self.amount_entry.config(bg="#ffcccc")
            else:
                self.amount_entry.config(bg=self.get_colors()["entry_bg"])
        except ValueError:
            if val:
                self.amount_entry.config(bg="#ffcccc")
            else:
                self.amount_entry.config(bg=self.get_colors()["entry_bg"])

    def update_theme(self):
        self.configure_theme()
        self.build_search_fields()
        self.show_service_details(self.current_name, self.current_phone, self.current_place)
        self.build_amount_entry()

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

    def build_amount_entry(self):
        colors = self.get_colors()
        for widget in self.amount_frame.winfo_children():
            widget.destroy()
        tk.Label(self.amount_frame, text="Enter amount:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=10)
        self.amount_entry = tk.Entry(self.amount_frame, textvariable=self.amount_var, width=15, bg=colors["entry_bg"], fg=colors["fg"])
        self.amount_entry.pack(side="left", padx=5)
        self.amount_entry.bind("<KeyRelease>", self.validate_amount_color_only)

        record_btn = tk.Button(
            self.amount_frame,
            text="Record Payment",
            font=("Arial", 12, "bold"),
            bg=colors["button_bg"],
            fg=colors["fg"],
            command=self.on_record_payment
        )
        record_btn.pack(side="left", padx=15)

    def show_themed_error(self, message, title="Error"):
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
            text=title,
            bg=colors["bg"],
            fg="#a80000",
            font=("Arial", 13, "bold"),
            wraplength=300,
            justify="center"
        ).pack(padx=20, pady=(20, 5))

        tk.Label(
            win,
            text=message,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("Arial", 12),
            wraplength=300,
            justify="center"
        ).pack(padx=20, pady=(0, 10))

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

    def on_record_payment(self):
        val = self.amount_var.get().strip()
        try:
            amt = float(val)
            if amt <= 0:
                self.show_themed_error("Invalid Amount", "Enter a positive amount.")
                self.amount_entry.config(bg="#ffcccc")
                self.amount_entry.focus_set()
                return
            if amt > self.remaining:
                self.show_themed_error("Amount Exceeds", "Entered amount exceeds the remaining amount.")
                self.amount_entry.config(bg="#ffcccc")
                self.amount_entry.focus_set()
                return
        except ValueError:
            self.show_themed_error("Invalid Input", "Please enter a valid number.")
            self.amount_entry.config(bg="#ffcccc")
            self.amount_entry.focus_set()
            return

        # Find service_id for this name, phone, place
        service_id = service_backend.get_service_id(self.current_name, self.current_phone, self.current_place)
        if not service_id:
            self.show_themed_error("Not Found", "No matching service record found.")
            return

        # Add payment in backend
        success, new_paid, new_remaining, new_status = service_backend.add_service_payment_to_record(service_id, amt)
        if not success:
            self.show_themed_error("Payment Error", "Could not record payment. Please check the amount and try again.")
            return

        if new_status == "pending":
            self.show_themed_confirmation(amt, self.current_name, self.current_place, "pending")
        else:
            self.show_themed_confirmation(amt, self.current_name, self.current_place, "completed")

        # Refresh details
        self.show_service_details(self.current_name, self.current_phone, self.current_place)
        self.amount_var.set("")

    def on_name_type(self, event):
        prefix = self.name_var.get()
        if not prefix.strip():
            self.name_combo['values'] = []
            return
        results = service_backend.search_customer_by_name(prefix)
        names = [r[0] for r in results]
        self.name_combo['values'] = names

    def on_name_select(self, event):
        selected_name = self.name_var.get()
        result = service_backend.customer_exists_by_name(selected_name)
        if result:
            self.place_var.set(result[0])
            self.phone_var.set(result[1])
            self.show_service_details(selected_name, result[1], result[0])

    def on_phone_type(self, event):
        prefix = self.phone_var.get()
        results = service_backend.search_customer_by_phone(prefix)
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones

    def on_phone_select(self, event):
        selected_phone = self.phone_var.get()
        result = service_backend.customer_exists_by_phone(selected_phone)
        if result:
            self.name_var.set(result[0])
            self.place_var.set(result[1])
            self.show_service_details(result[0], selected_phone, result[1])

    def show_service_details(self, name, phone, place):
        self.current_name = name
        self.current_phone = phone
        self.current_place = place

        for widget in self.details_frame.winfo_children():
            widget.destroy()

        colors = self.get_colors()
        self.title_label = tk.Label(
            self.details_frame,
            text="Service Customer Details",
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

        # Get service details
        try:
            service = service_backend.get_service_customer_by_name_phone(name, phone)
        except Exception:
            service = None

        if service:
            self.current_service_id = service[0]
            self.total_amount = service[4]
            self.total_paid = service[5]
            self.remaining = service[6]
        else:
            self.current_service_id = ""
            self.total_amount = 0.0
            self.total_paid = 0.0
            self.remaining = 0.0

        if self.remaining == 0:
            status_text = "Completed"
            status_bg = "#ccffcc"
            status_fg = "#006600"
        else:
            status_text = "Pending"
            status_bg = "#ffcccc"
            status_fg = "#a80000"

        to_pay_text = self.get_to_pay_text(self.remaining)
        self.summary_label = tk.Label(
            self.details_frame,
            text=f"Status: {status_text}    Total: {self.total_amount:.2f}    received: {self.total_paid:.2f}    {to_pay_text}",
            font=("Arial", 12, "bold"),
            bg=status_bg,
            fg=status_fg
        )
        self.summary_label.pack(anchor="w", padx=10, pady=(5, 10), fill="x")

    def get_to_pay_text(self, amount):
        if amount < 0:
            return f"To Pay: {abs(amount):.2f}"
        else:
            return f"To Get: {amount:.2f}"

    # --- Spare/Additional Payment Handler ---
    def on_add_spare_amount(self):
        val = self.spare_amount_var.get().strip()
        try:
            amt = float(val)
            if amt <= 0:
                self.show_themed_error("Invalid Amount", "Enter a positive amount.")
                self.spare_amount_entry.config(bg="#ffcccc")
                self.spare_amount_entry.focus_set()
                return
        except ValueError:
            self.show_themed_error("Invalid Input", "Please enter a valid number.")
            self.spare_amount_entry.config(bg="#ffcccc")
            self.spare_amount_entry.focus_set()
            return

        service_id = self.current_service_id
        if not service_id:
            self.show_themed_error("No Service", "No service record selected.")
            return

        # Call backend to update
        success = service_backend.add_spare_amount_to_service(service_id, amt)
        if not success:
            self.show_themed_error("Update Error", "Could not add spare amount. Please try again.")
            return

        # Refresh details and clear entry
        self.show_service_details(self.current_name, self.current_phone, self.current_place)
        self.spare_amount_var.set("")
