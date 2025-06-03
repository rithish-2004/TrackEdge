import tkinter as tk
from tkinter import ttk
from service import service_backend

class CustomerModifyFrame(tk.Frame):
    def __init__(self, parent, get_colors):
        super().__init__(parent)
        self.get_colors = get_colors
        self.current_name = None
        self.current_phone = None
        self.build_widgets()
        self.update_theme()

    def build_widgets(self):
        colors = self.get_colors()
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

        self.heading = tk.Label(self, text="Modify Service Customers", font=("Arial", 16, "bold"))
        self.heading.grid(row=0, column=0, columnspan=4, pady=(10, 4))

        self.name_label = tk.Label(self, text="Name:")
        self.name_label.grid(row=1, column=0, sticky="e", pady=10)
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(self, textvariable=self.name_var, width=18)
        self.name_combo.grid(row=1, column=1, sticky="w", padx=2)
        self.name_combo.bind("<KeyRelease>", self.on_name_type)
        self.name_combo.bind("<<ComboboxSelected>>", self.on_name_select)

        self.phone_label = tk.Label(self, text="Phone Number:")
        self.phone_label.grid(row=1, column=2, sticky="e")
        self.phone_var = tk.StringVar()
        self.phone_combo = ttk.Combobox(self, textvariable=self.phone_var, width=18)
        self.phone_combo.grid(row=1, column=3, sticky="w", padx=2)
        self.phone_combo.bind("<KeyRelease>", self.on_phone_type)
        self.phone_combo.bind("<<ComboboxSelected>>", self.on_phone_select)

        self.details_label = tk.Label(self, text="Service Customer Details", font=("Arial", 13, "bold"))
        self.details_label.grid(row=2, column=0, columnspan=4, pady=(10, 2))

        self.details_info = tk.Label(self, text="", font=("Arial", 11))
        self.details_info.grid(row=3, column=0, columnspan=4, pady=(0, 5))

        self.status_bar = tk.Label(self, text="", font=("Arial", 11, "bold"), width=65)
        self.status_bar.grid(row=4, column=0, columnspan=4, pady=(0, 10), ipadx=10, ipady=5, sticky="n")

        self.note_label = tk.Label(self, text="Note: Only Place and Phone Number can be edited.", font=("Arial", 10, "italic"))
        self.note_label.grid(row=5, column=0, columnspan=4, pady=(0, 10))

        self.form_frame = tk.Frame(self)
        self.form_frame.grid(row=6, column=0, columnspan=4, pady=(0, 10))
        for i in range(2):
            self.form_frame.grid_columnconfigure(i, weight=1)

        self.edit_name_label = tk.Label(self.form_frame, text="Name:")
        self.edit_name_label.grid(row=0, column=0, sticky="e", pady=3)
        self.edit_name_var = tk.StringVar()
        self.name_entry = tk.Entry(self.form_frame, textvariable=self.edit_name_var, state="disabled", width=25)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=3)

        self.edit_place_label = tk.Label(self.form_frame, text="Place:")
        self.edit_place_label.grid(row=1, column=0, sticky="e", pady=3)
        self.edit_place_var = tk.StringVar()
        self.place_entry = tk.Entry(self.form_frame, textvariable=self.edit_place_var, width=25)
        self.place_entry.grid(row=1, column=1, sticky="w", pady=3)

        self.edit_phone_label = tk.Label(self.form_frame, text="Phone:")
        self.edit_phone_label.grid(row=2, column=0, sticky="e", pady=3)
        self.edit_phone_var = tk.StringVar()
        self.edit_phone_entry = tk.Entry(self.form_frame, textvariable=self.edit_phone_var, width=25)
        self.edit_phone_entry.grid(row=2, column=1, sticky="w", pady=3)

        self.update_btn = tk.Button(self, text="Update Details", command=self.save_changes, font=("Arial", 11, "bold"))
        self.update_btn.grid(row=7, column=0, columnspan=4, pady=(10, 10), ipadx=10)

        self.notif_label = tk.Label(self, text="", font=("Arial", 11, "bold"))
        self.notif_label.grid(row=8, column=0, columnspan=4, pady=(0, 10))

        # Style for comboboxes
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TCombobox",
                        fieldbackground=colors["entry_bg"],
                        background=colors["entry_bg"],
                        foreground=colors["fg"])
        style.configure("TButton", background=colors["button_bg"], foreground=colors["fg"])
        self.name_combo.configure(style="Custom.TCombobox")
        self.phone_combo.configure(style="Custom.TCombobox")

    def update_theme(self):
        colors = self.get_colors()
        self.config(bg=colors["bg"])

        # Set bg/fg for labels and buttons (not frames)
        for widget in [
            self.heading, self.name_label, self.phone_label, self.details_label,
            self.details_info, self.status_bar, self.note_label,
            self.edit_name_label, self.edit_place_label, self.edit_phone_label,
            self.notif_label
        ]:
            widget.config(bg=colors["bg"], fg=colors["fg"])
        self.note_label.config(fg="#FF8C00")  # Special color for note

        # Set bg only for form_frame (no fg!)
        self.form_frame.config(bg=colors["bg"])

        # Set bg/fg for entries
        for widget in [self.name_entry, self.place_entry, self.edit_phone_entry]:
            widget.config(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"])

        # Set button colors
        self.update_btn.config(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])

        # Style for ttk.Combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TCombobox",
                        fieldbackground=colors["entry_bg"],
                        background=colors["entry_bg"],
                        foreground=colors["fg"])
        self.name_combo.configure(style="Custom.TCombobox")
        self.phone_combo.configure(style="Custom.TCombobox")

    

    def on_name_type(self, event):
        prefix = self.name_var.get()
        results = service_backend.search_customer_by_name(prefix)
        names = [r[0] for r in results]
        self.name_combo['values'] = names

    def on_name_select(self, event):
        self.fill_details_by_name(self.name_var.get())

    def on_phone_type(self, event):
        prefix = self.phone_var.get()
        results = service_backend.search_customer_by_phone(prefix)
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones

    def on_phone_select(self, event):
        self.fill_details_by_phone(self.phone_var.get())

    def fill_details_by_name(self, name):
        res = service_backend.customer_exists_by_name(name)
        if res:
            place, phone = res
            result = service_backend.get_service_customer_by_name_phone(name, phone)
        else:
            result = None

        if result:
            service_id, name, phone, place, total, paid, remaining = result
            self.details_info.config(text=f"Name: {name}    Phone: {phone}    Place: {place}")
            self.edit_name_var.set(name)
            self.edit_place_var.set(place)
            self.edit_phone_var.set(phone)
            self.current_name = name
            self.current_phone = phone
            self.update_status_bar(name, phone)
        else:
            self.details_info.config(text="No customer found.")
            self.status_bar.config(text="", bg=self.get_colors()["bg"])

    def fill_details_by_phone(self, phone):
        res = service_backend.customer_exists_by_phone(phone)
        if res:
            name, place = res
            result = service_backend.get_service_customer_by_name_phone(name, phone)
        else:
            result = None

        if result:
            service_id, name, phone, place, total, paid, remaining = result
            self.details_info.config(text=f"Name: {name}    Phone: {phone}    Place: {place}")
            self.edit_name_var.set(name)
            self.edit_place_var.set(place)
            self.edit_phone_var.set(phone)
            self.current_name = name
            self.current_phone = phone
            self.update_status_bar(name, phone)
        else:
            self.details_info.config(text="No customer found.")
            self.status_bar.config(text="", bg=self.get_colors()["bg"])

    def update_status_bar(self, name, phone):
        result = service_backend.get_service_customer_by_name_phone(name, phone)
        if result:
            _, _, _, _, total, paid, remaining = result
            if abs(remaining) < 0.01:
                self.status_bar.config(
                    text=f"Status: Completed    Total: {total:.2f}    Paid: {paid:.2f}    To Pay: 0.00",
                    bg="#ccffcc", fg="#006600")
            else:
                self.status_bar.config(
                    text=f"Status: Pending    Total: {total:.2f}    Paid: {paid:.2f}    To Pay: {remaining:.2f}",
                    bg="#ffcccc", fg="#a80000")
        else:
            self.status_bar.config(
                text="No service record found.",
                bg=self.get_colors()["bg"], fg=self.get_colors()["fg"])

    def save_changes(self):
        name = self.edit_name_var.get()
        new_place = self.edit_place_var.get().strip()
        new_phone = self.edit_phone_var.get().strip()

        if not name or not new_place or not new_phone:
            self.show_notification("All fields are required.", "danger")
            return

        if not new_phone.isdigit() or len(new_phone) != 10:
            self.show_notification("Phone number must be exactly 10 digits.", "danger")
            return

        # Only check for phone conflict if the phone has changed
        if new_phone != self.current_phone:
            with service_backend.get_db_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT customer_name FROM service_customer WHERE phone_number=? ORDER BY date DESC LIMIT 1", (new_phone,))
                row = c.fetchone()
                if row and row[0] != name:
                    self.show_notification("Phone number already exists for another customer!", "danger")
                    return

        try:
            with service_backend.get_db_connection() as conn:
                c = conn.cursor()
                c.execute("""
                    UPDATE service_customer SET phone_number=?, place=?
                    WHERE customer_name=? AND phone_number=?
                """, (new_phone, new_place, name, self.current_phone))
                conn.commit()
            self.show_notification(f"Place '{new_place}', Phone '{new_phone}' updated.", "success")
            self.current_phone = new_phone
            self.update_status_bar(name, new_phone)
        except Exception as e:
            self.show_notification(f"Error: {e}", "danger")

    def show_notification(self, text, type_):
        colors = self.get_colors()
        color = colors.get(type_, colors["fg"])
        self.notif_label.config(text=text, fg=color)
        self.notif_label.after(3500, lambda: self.notif_label.config(text=""))
    
if __name__ == "__main__":
    import themes
    def get_colors():
        theme = themes.load_theme()
        return themes.THEMES[theme]

    root = tk.Tk()
    root.title("Modify Service Customer")
    root.geometry("700x500")
    frame = CustomerModifyFrame(root, get_colors)
    frame.pack(fill="both", expand=True)

    def switch_theme(event=None):
        curr = themes.load_theme()
        new = "dark" if curr == "light" else "light"
        themes.save_theme(new)
        frame.update_theme()
    root.bind("<F5>", switch_theme)

    root.mainloop()
