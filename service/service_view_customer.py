import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
from service import service_backend

class ServiceViewCustomerFrame(tk.Frame):
    def __init__(self, parent, theme, get_colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.theme = theme
        self.get_colors = get_colors

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.place_var = tk.StringVar()
        self.filtered_start_date = None
        self.filtered_end_date = None

        self.build_title()
        colors = self.get_colors()
        self.header_frame = tk.Frame(self, bg=colors["bg"])
        self.header_frame.pack(side="top", fill="x")
        self.details_frame = tk.Frame(self, bg=colors["bg"])
        self.details_frame.pack(side="top", fill="both", expand=True)

        self.build_search_fields()
    

        self.configure_theme()

    def build_title(self):
        colors = self.get_colors()
        self.title_label = tk.Label(self, text="View Service Details", font=("Arial", 22, "bold"),
                                   bg=colors["bg"], fg=colors["fg"])
        self.title_label.pack(pady=(20, 10))

    def configure_theme(self):
        colors = self.get_colors()
        self.configure(bg=colors["bg"])
        self.title_label.configure(bg=colors["bg"], fg=colors["fg"])
        self.header_frame.configure(bg=colors["bg"])
        self.details_frame.configure(bg=colors["bg"])
        self.update_widget_colors(self.header_frame)
        self.update_widget_colors(self.details_frame)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TCombobox", fieldbackground=colors["entry_bg"], background=colors["entry_bg"], foreground=colors["fg"])
        style.configure("Custom.DateEntry", fieldbackground=colors["entry_bg"], background=colors["entry_bg"], foreground=colors["fg"], arrowcolor=colors["fg"])
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=colors["bg"])
        if hasattr(self, 'cards_frame'):
            self.cards_frame.configure(bg=colors["bg"])

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
        tk.Label(self.header_frame, text="Start Date:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(row=1, column=0, padx=5, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = DateEntry(self.header_frame, textvariable=self.start_date_var, width=12, style="Custom.DateEntry", date_pattern='yyyy-mm-dd')
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.header_frame, text="End Date:", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"]).grid(row=1, column=2, padx=5, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = DateEntry(self.header_frame, textvariable=self.end_date_var, width=12, style="Custom.DateEntry", date_pattern='yyyy-mm-dd')
        self.end_date_entry.grid(row=1, column=3, padx=5, pady=5)
        self.filter_button = tk.Button(self.header_frame, text="Filter", command=self.filter_by_date, bg=colors["button_bg"], fg=colors["fg"])
        self.filter_button.grid(row=1, column=4, padx=5, pady=5)
        self.reset_button = tk.Button(self.header_frame, text="Reset", command=self.reset_date_filter, bg=colors["button_bg"], fg=colors["fg"])
        self.reset_button.grid(row=1, column=5, padx=5, pady=5)

    def on_name_type(self, event):
        prefix = self.name_var.get()
        words = prefix.strip().split()
        if not words:
            self.name_combo['values'] = []
            return
        results = service_backend.search_customer_by_name_words(words)
        names = [r[0] for r in results]
        self.name_combo['values'] = names

    def on_name_select(self, event):
        selected_name = self.name_var.get()
        result = service_backend.get_customer_by_name(selected_name)
        if result:
            self.phone_var.set(result[1])
            self.place_var.set(result[2])
            self.show_service_details(result[0], result[1], result[2])

    def on_phone_type(self, event):
        prefix = self.phone_var.get()
        results = service_backend.search_customer_by_phone(prefix)
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones

    def on_phone_select(self, event):
        selected_phone = self.phone_var.get()
        result = service_backend.get_customer_by_phone(selected_phone)
        if result:
            self.name_var.set(result[0])
            self.place_var.set(result[2])
            self.show_service_details(result[0], result[1], result[2])

    def filter_by_date(self):
        self.filtered_start_date = self.start_date_var.get() or None
        self.filtered_end_date = self.end_date_var.get() or None
        self.show_service_details(self.name_var.get(), self.phone_var.get(), self.place_var.get())

    def reset_date_filter(self):
        self.filtered_start_date = None
        self.filtered_end_date = None
        self.start_date_var.set('')
        self.end_date_var.set('')
        self.show_service_details(self.name_var.get(), self.phone_var.get(), self.place_var.get())

    def build_scrollable_details_frame(self):
        colors = self.get_colors()
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()
        self.scroll_container = tk.Frame(self.details_frame, bg=colors["bg"])
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.canvas = tk.Canvas(self.scroll_container, bg=colors["bg"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        style = ttk.Style()
        style.theme_use('clam')
        self.scrollbar = ttk.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.cards_frame = tk.Frame(self.canvas, bg=colors["bg"])
        self.cards_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="n")
        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfig(self.cards_window, width=self.canvas.winfo_width())
        self.cards_frame.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_frame_configure)
    
    def show_service_details(self, name, phone, place):
        # Show message if no customer is selected
        if not name or not phone:
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            tk.Label(
                self.details_frame,
                text="Please select a customer.",
                font=("Arial", 14),
                bg=self.get_colors()["bg"],
                fg=self.get_colors()["fg"]
            ).pack(pady=40)
            # Also clear cards area if exists
            if hasattr(self, "cards_frame"):
                for widget in self.cards_frame.winfo_children():
                    widget.destroy()
            return

        self.current_name = name
        self.current_phone = phone
        self.current_place = place

        # Clear previous details
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        colors = self.get_colors()

        # Title label
        self.title_label2 = tk.Label(
            self.details_frame,
            text="Service Details",
            font=("Arial", 14, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.title_label2.pack(anchor="w", padx=10, pady=5)

        # Customer info
        info = f"Name: {name}   Phone: {phone}   Place: {place}"
        info_label = tk.Label(
            self.details_frame,
            text=info,
            font=("Arial", 12),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        info_label.pack(anchor="w", padx=10, pady=5)

        # Get summary
        total_amount, total_paid, total_remaining, status_text = service_backend.get_customer_summary(name, phone)
        status_bg = "#ccffcc" if status_text == "Completed" else "#ffcccc"
        status_fg = "#006600" if status_text == "Completed" else "#a80000"
        summary_label = tk.Label(
            self.details_frame,
            text=f"Status: {status_text}    Total: {total_amount:.2f}    Received: {total_paid:.2f}    To Pay: {total_remaining:.2f}",
            font=("Arial", 12, "bold"),
            bg=status_bg,
            fg=status_fg
        )
        summary_label.pack(anchor="w", padx=10, pady=(5, 10), fill="x")

        self.build_scrollable_details_frame()

        # --- Get all service items and payments grouped by date ---
        history = service_backend.get_service_history_by_date(
            name, phone, self.filtered_start_date, self.filtered_end_date
        )

        # Clear previous cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        for date, data in history.items():
            card = tk.Frame(self.cards_frame, bd=2, relief="groove", bg=colors["card_bg"])
            card.pack(pady=10, padx=20, fill="x", anchor="center")

            # Card header: Date
            tk.Label(card, text=f"Date: {date}", font=("Arial", 13, "bold"),
                    bg=colors["card_bg"], fg=colors["fg"]).pack(anchor="w", padx=10, pady=(5, 2))

            # --- Services Section ---
            if data["items"]:
                tk.Label(card, text="Services", font=("Arial", 12, "underline"),
                        bg=colors["card_bg"], fg=colors["fg"]).pack(anchor="w", padx=20, pady=(2, 0))
                for idx, item in enumerate(data["items"], 1):
                    text = f"{idx}. {item['item_name']}"
                    tk.Label(card, text=text, font=("Arial", 12, "bold"),
                            bg=colors["card_bg"], fg=colors["fg"]).pack(anchor="w", padx=40, pady=(2, 0))
                    if item["description"]:
                        tk.Label(card, text=f"   Fault: {item['description']}", font=("Arial", 11),
                                bg=colors["card_bg"], fg=colors["fg"]).pack(anchor="w", padx=60, pady=0)
                    tk.Label(card, text=f"   Amount: {item['amount']:.2f}", font=("Arial", 11),
                            bg=colors["card_bg"], fg=colors["fg"]).pack(anchor="w", padx=60, pady=(0, 2))

            # --- Transactions Section ---
            if data["payments"]:
                tk.Label(card, text="Transactions", font=("Arial", 12, "underline"),
                        bg=colors["card_bg"], fg=colors["fg"]).pack(anchor="w", padx=20, pady=(5, 0))
                for idx, pay in enumerate(data["payments"], 1):
                    text = f"{idx}. Payment: {pay['amount']:.2f}"
                    if pay["time"]:
                        text += f" | Time: {pay['time']}"
                    tk.Label(card, text=text, font=("Arial", 11, "italic"),
                            bg=colors["card_bg"], fg=colors["fg"]).pack(anchor="w", padx=40, pady=(2, 0))


    def update_theme(self):
        self.configure_theme()
        if getattr(self, "current_name", None):
            self.show_service_details(self.current_name, self.current_phone, self.current_place)
        else:
            self.show_service_details("", "", "")


