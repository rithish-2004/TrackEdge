import tkinter as tk
from tkinter import ttk
from inward import db_backend
from tkcalendar import DateEntry
from datetime import datetime

class InwardViewPurchaseFrame(tk.Frame):
    def __init__(self, parent, theme, get_colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.theme = theme
        self.get_colors = get_colors

        # Create variables
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.place_var = tk.StringVar()
        self.filtered_start_date = None
        self.filtered_end_date = None
        self.build_title1()

        # Create section frames in correct order - only ONCE!
        colors = self.get_colors()
        self.header_frame = tk.Frame(self, bg=colors["bg"])
        self.header_frame.pack(side="top", fill="x")
        self.filter_frame = tk.Frame(self, bg=colors["bg"])
        self.filter_frame.pack(side="top", fill="x")
        self.details_frame = tk.Frame(self, bg=colors["bg"])
        self.details_frame.pack(side="top", fill="both", expand=True)

        self.build_search_fields()

        self.show_purchase_details("", "", "")

        self.configure_theme()

    def build_title1(self):
        colors = self.get_colors()
        self.title_label1 = tk.Label(self, text="View Purchaser Details", font=("Arial", 22, "bold"),
                                bg=colors["bg"], fg=colors["fg"])
        self.title_label1.pack(pady=(20, 10))

    def configure_theme(self):
        colors = self.get_colors()
        self.configure(bg=colors["bg"])
        self.title_label1.configure(bg=colors["bg"], fg=colors["fg"])
        self.header_frame.configure(bg=colors["bg"])
        self.filter_frame.configure(bg=colors["bg"])
        self.details_frame.configure(bg=colors["bg"])

        # Update classic Tk widgets' colors
        self.update_widget_colors(self.header_frame)
        self.update_widget_colors(self.filter_frame)
        self.update_widget_colors(self.details_frame)

        # ttk styles for all ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TCombobox", fieldbackground=colors["entry_bg"], background=colors["entry_bg"], foreground=colors["fg"])
        style.configure("Custom.DateEntry", fieldbackground=colors["entry_bg"], background=colors["entry_bg"], foreground=colors["fg"], arrowcolor=colors["fg"])
        style.configure("Custom.Treeview", background=colors["table_bg"], foreground=colors["table_fg"], fieldbackground=colors["table_bg"], bordercolor=colors["table_border"])
        style.configure("Custom.Treeview.Heading", background=colors["table_head_bg"], foreground=colors["table_head_fg"], relief="flat")
        style.configure("Vertical.TScrollbar", background=colors["scroll_bg"], troughcolor=colors["scroll_trough"], bordercolor=colors["scroll_border"], arrowcolor=colors["scroll_arrow"])
        style.configure("Horizontal.TScrollbar", background=colors["scroll_bg"], troughcolor=colors["scroll_trough"], bordercolor=colors["scroll_border"], arrowcolor=colors["scroll_arrow"])
        colors = self.get_colors()
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=colors["bg"])
        if hasattr(self, 'cards_frame'):
            self.cards_frame.configure(bg=colors["bg"])
        if hasattr(self, 'scroll_container'):
            self.scroll_container.configure(bg=colors["bg"])
        if hasattr(self, 'cards_frame'):
            for widget in self.cards_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=colors["card_bg"])


 
    def rebuild_search_and_details(self):
        # Destroy and rebuild search fields and details for new theme
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        self.header_frame.destroy()
        self.build_search_fields()
        # Optionally, also rebuild details if needed
        if hasattr(self, "current_name"):
            self.show_purchase_details(self.current_name, self.current_phone, self.current_place)
    
    def filter_by_date(self):
        # Parse dates from the DateEntry widgets
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        self.filtered_start_date = start_date if start_date else None
        self.filtered_end_date = end_date if end_date else None
        # Refresh the card display with the filter applied
        self.show_purchase_details(self.current_name, self.current_phone, self.current_place)

    def reset_date_filter(self):
        self.filtered_start_date = None
        self.filtered_end_date = None
        self.start_date_var.set('')
        self.end_date_var.set('')
        self.show_purchase_details(self.current_name, self.current_phone, self.current_place)


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
            
            # Do NOT try to configure ttk widgets here!


    def update_theme(self):
        self.configure_theme()
        if hasattr(self, 'cards_frame'):
            self.cards_frame.configure(bg=self.get_colors()["bg"])
            self.cards_frame.update_idletasks()


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


    def build_purchase_details(self):
        colors = self.get_colors()
        self.details_frame = tk.Frame(self, bg=colors["bg"])
        self.details_frame.pack(pady=10, fill="x")

        self.title_label = tk.Label(self.details_frame, text="Purchase Details", font=("Arial", 14, "bold"), bg=colors["bg"], fg=colors["fg"])
        self.title_label.pack(anchor="w", padx=10, pady=5)

        self.details_label = tk.Label(self.details_frame, text="", font=("Arial", 12), bg=colors["bg"], fg=colors["fg"])
        self.details_label.pack(anchor="w", padx=10, pady=5)

    def on_name_type(self, event):
        prefix = self.name_var.get()
        # Search for each word (split by space)
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
            self.show_purchase_details(result[0], result[1], result[2])

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
            self.show_purchase_details(result[0], result[1], result[2])
    
    
   
    def build_scrollable_details_frame(self):
        colors = self.get_colors()
        # Remove old canvas/scrollbar if they exist
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()

        # In your build_scrollable_details_frame function:
        self.scroll_container = tk.Frame(self.details_frame, bg=colors["bg"])
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(self.scroll_container, bg=colors["bg"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Vertical.TScrollbar",
                        background=colors["scroll_bg"],
                        troughcolor=colors["scroll_trough"],
                        bordercolor=colors["scroll_border"],
                        arrowcolor=colors["scroll_arrow"])
        self.scrollbar = ttk.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview, style="Custom.Vertical.TScrollbar")
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.cards_frame = tk.Frame(self.canvas, bg=colors["bg"])
        self.cards_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="n")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfig(self.cards_window, width=self.canvas.winfo_width())
        self.cards_frame.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_frame_configure)

        # When packing each card:
        card = tk.Frame(self.cards_frame, bd=2, relief="groove", bg=colors["card_bg"])
        card.pack(pady=10, anchor="center")

    # When creating your DateEntry widgets:
    def get_to_pay_text(self, amount):
        if amount < 0:
            return f"Refund Due: {abs(amount):.2f}"
        else:
            return f"To Pay: {amount:.2f}"

    
    def show_purchase_details(self, name, phone, place):
        self.current_name = name
        self.current_phone = phone
        self.current_place = place

        # Clear previous details
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        colors = self.get_colors()
        style = ttk.Style()

        # 2. Title label
        self.title_label = tk.Label(
            self.details_frame,
            text="Purchase Details",
            font=("Arial", 14, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.title_label.pack(anchor="w", padx=10, pady=5)

        # 3. Purchaser info
        info = f"Name: {name}   Phone: {phone}   Place: {place}"
        info_label = tk.Label(
            self.details_frame,
            text=info,
            font=("Arial", 12),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        info_label.pack(anchor="w", padx=10, pady=5)

        purchases = db_backend.get_purchases_by_name_phone(name, phone)

        # 5. Calculate overall totals for summary
        total_amount = sum(p[1] for p in purchases)
        total_paid = sum(p[2] for p in purchases)
        total_remaining = sum(p[3] for p in purchases)
        any_pending = any(p[4] == "pending" for p in purchases)

        if total_remaining == 0:
            status_text = "Completed"
            status_bg = "#ccffcc"
            status_fg = "#006600"
        else:
            status_text = "Pending"
            status_bg = "#ffcccc"
            status_fg = "#a80000"


        # 6. Summary label
        to_pay_text = self.get_to_pay_text(total_remaining)
        summary_label = tk.Label(
            self.details_frame,
            text=f"Status: {status_text}    Total: {total_amount:.2f}    Paid: {total_paid:.2f}    {to_pay_text}",
            font=("Arial", 12, "bold"),
            bg=status_bg,
            fg=status_fg
        )

        summary_label.pack(anchor="w", padx=10, pady=(5, 10), fill="x")

        # 7. Build the scrollable area for cards
        self.build_scrollable_details_frame()

        # --- Group all purchases and transactions by date ---
        # Gather all transaction-only dates too!
        all_dates = set()
        purchases_by_date = {}
        for purchase in purchases:
            date = purchase[5]
            purchases_by_date.setdefault(date, []).append(purchase)
            all_dates.add(date)

        # Also get all transaction dates for this customer (even if no purchase that day)
        payment_dates = db_backend.get_payment_dates_by_name_phone(name, phone)
        for d in payment_dates:
            all_dates.add(d)

        # Clear previous cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()


        activity_dates = db_backend.get_all_activity_dates(name, phone)

        # Filter dates if a filter is set
        if self.filtered_start_date and self.filtered_end_date:
            start_dt = datetime.strptime(self.filtered_start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(self.filtered_end_date, '%Y-%m-%d')
            filtered_dates = [
                date for date in activity_dates
                if start_dt <= datetime.strptime(date, '%Y-%m-%d') <= end_dt
            ]
        else:
            filtered_dates = activity_dates

        for date in sorted(filtered_dates, reverse=True):
            products = db_backend.get_products_by_name_phone_and_date(name, phone, date)
            payments = db_backend.get_payments_by_name_phone_and_date(name, phone, date)
            if not products and not payments:
                continue  # Skip this date, nothing to show
            card = tk.Frame(self.cards_frame, bd=2, relief="groove", bg=colors["card_bg"], padx=10, pady=10)
            card.pack(fill="x", expand=True, padx=10, pady=10)
            # ... display card content ...



            # --- Centered Date label ---
            date_label = tk.Label(
                card,
                text=date,
                font=("Arial", 12, "bold"),
                bg=colors["card_bg"],
                fg=colors["fg"]
            )
            date_label.pack(anchor="center", pady=(0, 10))

            if products:
    # Create a frame for the table and scrollbar
                table_frame = tk.Frame(card, bg=colors["card_bg"])
                table_frame.pack(fill="x", padx=5, pady=5)

                # Create the Treeview with your custom style
                table = ttk.Treeview(
                    table_frame,
                    columns=("item", "qty", "price", "desc", "amount"),
                    show="headings",
                    height=len(products),
                    style="Custom.Treeview"
                )
                for col, heading in zip(("item", "qty", "price", "desc", "amount"), ["Item", "Qty", "Price", "Description", "Amount"]):
                    table.heading(col, text=heading)
                    table.column(col, anchor="center", width=100)
                for prod in products:
                    table.insert("", "end", values=prod)

                # Create the vertical scrollbar with your custom style
                scrollbar = ttk.Scrollbar(
                    table_frame,
                    orient="vertical",
                    command=table.yview,
                    style="Vertical.TScrollbar"
                )
                table.configure(yscrollcommand=scrollbar.set)

                # Pack Treeview and scrollbar
                table.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")


                # --- Status/Amount info (for products on this date) ---
                # You may need to aggregate these if multiple purchases on same date
                # Example assumes all products on this date are part of the same purchase
                # If not, you can sum/aggregate as needed
                #total_amount = sum(float(p[4]) for p in products)  # Assuming amount is at index 4
                #amount_paid = sum(float(pay[3]) for pay in payments) if payments else 0  # Assuming amount_paid is at index 3
               # remaining_amount = total_amount - amount_paid
                #status = "Pending" if remaining_amount > 0 else "Completed"

                #status_label = tk.Label(
                   # card,
                   # text=f"Status: {status}   Total: {total_amount:.2f}   Paid: {amount_paid:.2f}   To Pay: {remaining_amount:.2f}",
                 #font=("Arial", 11, "bold"),
                   # bg=colors["card_bg"],
                    #fg=colors["fg"]
               # )
               # status_label.pack(anchor="w", padx=10, pady=5)
            else:
                no_prod_label = tk.Label(
                    card,
                    text="No products purchased on this date.",
                    bg=colors["card_bg"],
                    fg=colors["fg"],
                    font=("Arial", 10, "italic")
                )
                no_prod_label.pack(anchor="w", padx=10, pady=5)

            # --- Show Transaction History Button ---
            btn = tk.Button(
                card,
                text="Show Transaction History",
                bg=colors["button_bg"],
                fg=colors["fg"]
            )
            btn.pack(anchor="e", padx=10, pady=5)

            # --- Transaction history toggle ---
            def toggle_history(frame=card, dt=date, btn=btn):
                colors = self.get_colors()
                if hasattr(frame, "_history_shown") and frame._history_shown:
                    if hasattr(frame, "_history_frame"):
                        frame._history_frame.pack_forget()
                    frame._history_shown = False
                    btn.config(text="Show Transaction History")
                else:
                    if not hasattr(frame, "_history_frame"):
                        frame._history_frame = tk.Frame(frame, bg=colors["bg"])
                        # Get all payments for this date
                        local_payments = db_backend.get_payments_by_name_phone_and_date(name, phone, dt)
                        if not local_payments:
                            no_pay_label = tk.Label(
                                frame._history_frame,
                                text="No transaction history.",
                                bg=colors["bg"],
                                fg=colors["fg"]
                            )
                            no_pay_label.pack(anchor="w", padx=10, pady=5)
                        else:
                            history_canvas = tk.Canvas(frame._history_frame, bg=colors["bg"], height=120, highlightthickness=0)
                            history_scrollbar = tk.Scrollbar(frame._history_frame, orient="vertical", command=history_canvas.yview)
                            history_canvas.configure(yscrollcommand=history_scrollbar.set)
                            history_canvas.pack(side="left", fill="both", expand=True)
                            history_scrollbar.pack(side="right", fill="y")

                            history_inner = tk.Frame(history_canvas, bg=colors["bg"])
                            history_canvas.create_window((0, 0), window=history_inner, anchor="nw")

                            def on_history_configure(event):
                                history_canvas.configure(scrollregion=history_canvas.bbox("all"))
                            history_inner.bind("<Configure>", on_history_configure)

                            for pay in local_payments:
                                pay_date, payment_id, purchaser_id, amount_paid = pay
                                pay_label = tk.Label(
                                    history_inner,
                                    text=f"Payment ID: {payment_id}   Amount: {amount_paid:.2f}",
                                    font=("Arial", 10),
                                    bg=colors["bg"],
                                    fg=colors["fg"]
                                )
                                pay_label.pack(anchor="w", padx=10, pady=2)
                    frame._history_frame.pack(fill="x", padx=5, pady=5, before=btn)
                    frame._history_shown = True
                    btn.config(text="Hide Transaction History")

            btn.config(command=lambda f=card, dt=date, b=btn: toggle_history(f, dt, b))
