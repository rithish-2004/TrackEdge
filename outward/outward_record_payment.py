import tkinter as tk
from tkinter import ttk, messagebox
from outward import customer_backend

class OutwardRecordPaymentFrame(tk.Frame):
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

        self.total_amount = 0.0
        self.total_paid = 0.0
        self.remaining = 0.0

        colors = self.get_colors()
        self.topic_label = tk.Label(
        self,
        text="Sales - Record Payment",
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
        self.show_purchase_details("", "", "")
        self.build_amount_entry()
        self.configure_theme()
    def show_themed_confirmation(self, amount, name, place, status):
        colors = self.get_colors()
        msg = f"{amount:.2f} is paid to {name}, {place}. Status: {status.capitalize()}."
        win = tk.Toplevel(self)
        win.title("Payment Recorded")
        win.configure(bg=colors["bg"])
        win.resizable(False, False)
        # Center the popup
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
            if amt < 0 or amt > self.total_amount:
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
        self.show_purchase_details(self.current_name, self.current_phone, self.current_place)
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

        # Add the Record Payment button
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

        # Center the popup (same logic as your confirmation)
        win.geometry("+%d+%d" % (
            self.winfo_rootx() + self.winfo_width() // 2 - 150,
            self.winfo_rooty() + self.winfo_height() // 2 - 60
        ))

        tk.Label(
            win,
            text=title,
            bg=colors["bg"],
            fg="#a80000",  # Red for error title
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

        # Find purchaser_id for this name, phone, place
        customer_id = customer_backend.get_customer_id(self.current_name, self.current_phone, self.current_place)
        if not customer_id:
            self.show_themed_error("Not Found", "No matching purchase record found.")
            return

        # Add payment in backend
        success, new_remaining, new_status = customer_backend.add_customer_payment_to_record(customer_id, amt)
        if not success:
            self.show_themed_error("Payment Error", "Could not record payment. Please check the amount and try again.")
            return

        if new_status == "pending":
            self.show_themed_confirmation(amt, self.current_name, self.current_place, "pending")
        else:
            self.show_themed_confirmation(amt, self.current_name, self.current_place, "completed")

        # Refresh details
        self.show_purchase_details(self.current_name, self.current_phone, self.current_place)
        self.amount_var.set("")


    def on_name_type(self, event):
        prefix = self.name_var.get()
        words = prefix.strip().split()
        if not words:
            self.name_combo['values'] = []
            return
        results = customer_backend.search_customer_by_name_words(words)
        names = [r[0] for r in results]
        self.name_combo['values'] = names

    def on_name_select(self, event):
        selected_name = self.name_var.get()
        result = customer_backend.get_customer_by_name(selected_name)
        if result:
            self.phone_var.set(result[1])
            self.place_var.set(result[2])
            self.show_purchase_details(result[0], result[1], result[2])

    def on_phone_type(self, event):
        prefix = self.phone_var.get()
        results = customer_backend.search_customer_by_phone(prefix)
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones

    def on_phone_select(self, event):
        selected_phone = self.phone_var.get()
        result = customer_backend.get_customer_by_phone(selected_phone)
        if result:
            self.name_var.set(result[0])
            self.place_var.set(result[2])
            self.show_purchase_details(result[0], result[1], result[2])

    def show_purchase_details(self, name, phone, place):
        self.current_name = name
        self.current_phone = phone
        self.current_place = place

        for widget in self.details_frame.winfo_children():
            widget.destroy()

        colors = self.get_colors()
        # 2. Title label
        self.title_label = tk.Label(
            self.details_frame,
            text="Customer Details",
            font=("Arial", 14, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.title_label.pack(anchor="w", padx=10, pady=5)

        # 3. Purchaser info
        info_frame = tk.Frame(self.details_frame, bg=colors["bg"])
        info_frame.pack(anchor="w", padx=10, pady=5)

        tk.Label(info_frame, text="Name:", font=("Arial", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side="left")
        tk.Label(info_frame, text=name, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=(0, 10))
        tk.Label(info_frame, text="Phone:", font=("Arial", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side="left")
        tk.Label(info_frame, text=phone, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=(0, 10))
        tk.Label(info_frame, text="Place:", font=("Arial", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side="left")
        tk.Label(info_frame, text=place, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).pack(side="left")
   

        try:
            purchases = customer_backend.get_customer_by_name_phone(name, phone)
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


        to_pay_text = self.get_to_pay_text(self.remaining)
        self.summary_label = tk.Label(
            self.details_frame,
            text=f"Status: {status_text}    Total: {self.total_amount:.2f}    recieved: {self.total_paid:.2f}    {to_pay_text}",
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
