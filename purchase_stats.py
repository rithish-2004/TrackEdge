import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from datetime import datetime
import math
import os
import sys
from tkinter import messagebox
from pathlib import Path


class PurchaseStats:
    def __init__(self, parent, theme, sales_frame):
        self.parent = parent
        self.theme = theme
        self.sales_frame = sales_frame
        self.open_windows = []
        self.setup_sales_stats()

    def get_customer_stats(self):
        conn = sqlite3.connect("inward/purchase.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM purchaser")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM purchaser WHERE LOWER(status) = LOWER(?)", ('pending',))
        pending = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM purchaser WHERE LOWER(status) = LOWER(?)", ('completed',))
        completed = cur.fetchone()[0]
        conn.close()
        return total, pending, completed

    def show_pending_customers(self):
        self._show_customer_details('pending')

    def show_completed_customers(self):
        self._show_customer_details('completed')

    def _show_customer_details(self, status):
        conn = sqlite3.connect("inward/purchase.db")
        cur = conn.cursor()
        cur.execute("SELECT purchaser_id, purchaser_name, Place, phone_number, total_amount, date, amount_paid, remaining_amount FROM purchaser WHERE LOWER(status) = LOWER(?) ORDER BY purchaser_name", (status,))
        rows = cur.fetchall()
        conn.close()

        top = tk.Toplevel(self.parent)
        top.title(f"{status.capitalize()} Purchaser")
        top.state('zoomed')
        top.configure(bg=self.theme["bg"])
        self.open_windows.append(top)

        title_label = tk.Label(top, text=f"{status.capitalize()} Purchaser", font=("Arial", 18, "bold"),
                            bg=self.theme.get("notif_container_bg", self.theme["bg"]),
                            fg=self.theme["fg"])
        title_label.pack(side=tk.TOP, fill=tk.X, pady=(10, 5))

        # Live search bar
        search_frame = tk.Frame(top, bg=self.theme["bg"])
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        search_label = tk.Label(search_frame, text="Search:", font=("Arial", 14),
                            bg=self.theme["bg"], fg=self.theme["fg"])
        search_label.pack(side=tk.LEFT, padx=(0,5))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, bg=self.theme["bg"], fg=self.theme["fg"])
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Table frame
        table_frame = tk.Frame(top, bg=self.theme["bg"], bd=2, relief="groove")
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background=self.theme["bg"],
            foreground=self.theme["fg"],
            fieldbackground=self.theme["bg"],
            bordercolor=self.theme.get("notif_container_bg", self.theme["bg"]),
            borderwidth=2,
            relief="solid")
        style.configure("Treeview.Heading",
            background=self.theme.get("notif_container_bg", self.theme["bg"]),
            foreground=self.theme["fg"],
            font=("Arial", 12, "bold"),
            relief="flat")
        style.map("Treeview",
            background=[("selected", self.theme.get("info", "#FF8C00"))],
            foreground=[("selected", self.theme["fg"])])

        if status.lower() == 'pending':
            columns = ("ID", "Name", "Place", "Phone", "Total", "Date", "Paid", "Remaining to Pay", "Refund")
        else:
            columns = ("ID", "Name", "Place", "Phone", "Total", "Date", "Paid")

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
            tree.column(col, width=120, stretch=True)

        for row in rows:
            if status.lower() == 'pending':
                remaining = row[7] if row[7] is not None else 0
                if remaining > 0:
                    remaining_to_pay = f"{remaining:.2f}"
                    refund = ""
                elif remaining < 0:
                    remaining_to_pay = ""
                    refund = f"{-remaining:.2f}"
                else:
                    remaining_to_pay = ""
                    refund = ""
                tree.insert("", "end", values=(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    remaining_to_pay, refund
                ))
            else:
                tree.insert("", "end", values=(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6]
                ))

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scroll_y.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Live search functionality
        def search_customers(*args):
            query = search_var.get().lower()
            for child in tree.get_children():
                values = tree.item(child)["values"]
                if any(query in str(v).lower() for v in values):
                    tree.selection_set(child)
                    tree.focus(child)
                    tree.see(child)
                    break

        search_var.trace_add("write", search_customers)

        # Store widgets for theme updates
        top._tree = tree
        top._table_frame = table_frame
        top._title_label = title_label
        top._search_frame = search_frame
        top._search_label = search_label
        top._search_entry = search_entry


    def create_stat(self, frame, value, label, color, row, col, padx=0, click_command=None):
        container = tk.Frame(frame, bg=self.theme.get("notif_container_bg", self.theme["bg"]))
        value_label = tk.Label(container, text=str(value), font=("Arial", 18, "bold"),
                               bg=self.theme.get("notif_container_bg", self.theme["bg"]), fg=color)
        value_label.pack()
        label_label = tk.Label(container, text=label, font=("Arial", 11),
                               bg=self.theme.get("notif_container_bg", self.theme["bg"]), fg=self.theme["fg"])
        label_label.pack()
        if click_command:
            value_label.bind("<Button-1>", lambda e: click_command())
            label_label.bind("<Button-1>", lambda e: click_command())
            value_label.config(cursor="hand2")
            label_label.config(cursor="hand2")
        container.grid(row=row, column=col, sticky="n", pady=(5, 0), padx=padx)

    def create_pie_chart(self, frame, pending, completed):
        # Make the pie chart a bit bigger
        canvas = tk.Canvas(frame, bg=self.theme.get("notif_container_bg", self.theme["bg"]),
                           width=150, height=150, highlightthickness=0)
        canvas.pack(padx=5, pady=5)
        total = pending + completed
        if total == 0:
            canvas.create_oval(30, 30, 120, 120, outline="#ccc", fill="#eee")
            return

        pending_pct = int(round((pending / total) * 100)) if total else 0
        completed_pct = 100 - pending_pct

        start = 0
        # Pending slice (red)
        if pending > 0:
            extent = pending / total * 360
            canvas.create_arc(20, 20, 130, 130, start=start, extent=extent,
                              fill=self.theme.get("pending", "#FF3B30"),
                              outline=self.theme.get("pending", "#FF3B30"))
            angle = start + extent / 2
            x = 75 + 40 * math.cos(math.radians(angle))
            y = 75 - 40 * math.sin(math.radians(angle))
            canvas.create_text(x, y, text=f"{pending_pct}%", font=("Arial", 13, "bold"),
                              fill="white" if pending_pct else "#888")
            start += extent
        # Completed slice (green)
        if completed > 0:
            extent = completed / total * 360
            canvas.create_arc(20, 20, 130, 130, start=start, extent=extent,
                              fill=self.theme.get("completed", "#34C759"),
                              outline=self.theme.get("completed", "#34C759"))
            angle = start + extent / 2
            x = 75 + 40 * math.cos(math.radians(angle))
            y = 75 - 40 * math.sin(math.radians(angle))
            canvas.create_text(x, y, text=f"{completed_pct}%", font=("Arial", 13, "bold"),
                              fill="white" if completed_pct else "#888")

    def download_excel(self):
        try:
            
            # Fetch all customer data
            conn = sqlite3.connect("inward/purchase.db")
            cur = conn.cursor()
            cur.execute("SELECT purchaser_id, purchaser_name, Place, phone_number, total_amount, date, amount_paid, remaining_amount, status FROM purchaser ORDER BY purchaser_name")
            rows = cur.fetchall()
            conn.close()

            # Prepare Pending and Completed data
            pending_data = []
            completed_data = []
            pending_columns = ["ID", "Name", "Place", "Phone", "Total", "Date", "Paid", "Remaining to Pay", "Refund"]
            completed_columns = ["ID", "Name", "Place", "Phone", "Total", "Date", "Paid"]

            for row in rows:
                remaining = row[7] if row[7] is not None else 0
                status = row[8].lower()
                if status == 'pending':
                    if remaining > 0:
                        remaining_to_pay = f"{remaining:.2f}"
                        refund = ""
                    elif remaining < 0:
                        remaining_to_pay = ""
                        refund = f"{-remaining:.2f}"
                    else:
                        remaining_to_pay = ""
                        refund = ""
                    pending_data.append([
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        remaining_to_pay, refund
                    ])
                elif status == 'completed':
                    completed_data.append([
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6]
                    ])

            # Save to Excel with two sheets
            downloads = str(Path.home() / "Downloads")
            filename = os.path.join(downloads, f"Purchases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

            with pd.ExcelWriter(filename) as writer:
                pd.DataFrame(pending_data, columns=pending_columns).to_excel(writer, sheet_name="Pending", index=False)
                pd.DataFrame(completed_data, columns=completed_columns).to_excel(writer, sheet_name="Completed", index=False)

            # Show themed notification
            self.show_themed_messagebox(
                "Success",
                f"Data exported to {filename}\n\nClick OK to open the file."
            )

            # Open the file after OK
            abs_filename = os.path.abspath(filename)
            try:
                if sys.platform.startswith('darwin'):
                    os.system(f'open "{abs_filename}"')
                elif os.name == 'nt':
                    os.startfile(abs_filename)
                elif os.name == 'posix':
                    os.system(f'xdg-open "{abs_filename}"')
            except Exception as open_err:
                self.show_themed_messagebox("Open File", f"Could not open file automatically: {open_err}")

        except Exception as e:
            self.show_themed_messagebox("Error", f"Failed to export: {e}")

    def show_themed_messagebox(self, title, message):
        # Custom themed messagebox using your theme
        top = tk.Toplevel(self.parent)
        top.title(title)
        top.configure(bg=self.theme.get("notif_container_bg", self.theme["bg"]))
        top.grab_set()
        w, h = 480, 180  # Increased width for better layout
        x = top.winfo_screenwidth() // 2 - w // 2
        y = top.winfo_screenheight() // 2 - h // 2
        top.geometry(f"{w}x{h}+{x}+{y}")

        label = tk.Label(
            top, text=title, font=("Arial", 14, "bold"),
            bg=self.theme.get("notif_container_bg", self.theme["bg"]),
            fg=self.theme["fg"]
        )
        label.pack(pady=(18, 6))

        msg = tk.Label(
            top, text=message, font=("Arial", 11),
            bg=self.theme.get("notif_container_bg", self.theme["bg"]),
            fg=self.theme["fg"], wraplength=420, justify="center"
        )
        msg.pack(pady=(0, 18))

        btn = tk.Button(
            top, text="OK", font=("Arial", 12, "bold"),
            bg=self.theme.get("notif_container_bg", self.theme["bg"]),
            fg=self.theme["fg"], relief="ridge",
            command=top.destroy
        )
        btn.pack(ipadx=18, ipady=2, pady=(0, 8))
        top.wait_window()

    def setup_sales_stats(self):
        for widget in self.sales_frame.winfo_children():
            widget.destroy()

        total, pending, completed = self.get_customer_stats()

        # Ensure the sales_frame expands fully
        self.sales_frame.grid(sticky="nsew", padx=5, pady=5)
        self.sales_frame.columnconfigure(0, weight=1)
        self.sales_frame.rowconfigure(1, weight=1)  # row 1 for content_frame

        # Heading
        sales_heading = tk.Label(
            self.sales_frame,
            text="Purchase",
            font=("Arial", 14, "bold"),
            bg=self.theme.get("notif_container_bg", self.theme["bg"]),
            fg=self.theme["fg"]
        )
        sales_heading.grid(row=0, column=0, columnspan=3, pady=(4, 0), sticky="nsew")

        # Main content grid: 2 rows, 3 columns
        content_frame = tk.Frame(
            self.sales_frame,
            bg=self.theme.get("notif_container_bg", self.theme["bg"])
        )
        content_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)

        # Make content_frame expand to fill sales_frame
        for i in range(2):
            content_frame.rowconfigure(i, weight=1)
        for i in range(3):
            content_frame.columnconfigure(i, weight=1)

        # Left column: Total above Completed
        self.create_stat(content_frame, total, "Total", self.theme["fg"], row=0, col=0)
        self.create_stat(
            content_frame, completed, "Completed",
            self.theme.get("completed", "#34C759"), row=1, col=0,
            click_command=self.show_completed_customers
        )

        # Middle column: Pending above Download Excel
        self.create_stat(
            content_frame, pending, "Pending",
            self.theme.get("pending", "#FF3B30"), row=0, col=1, padx=20,
            click_command=self.show_pending_customers
        )
        download_btn = tk.Button(
            content_frame,
            text="Download\nExcel",
            font=("Arial", 12, "bold"),
            bg=self.theme.get("notif_container_bg", self.theme["bg"]),
            fg=self.theme["fg"],
            bd=1,
            relief="ridge",
            command=self.download_excel
        )
        download_btn.grid(row=1, column=1, sticky="nsew", pady=4, padx=8)
        # Right: Pie chart (centered over both rows)
        pie_frame = tk.Frame(
            content_frame,
            bg=self.theme.get("notif_container_bg", self.theme["bg"])
        )
        pie_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(10, 0))
        self.create_pie_chart(pie_frame, pending, completed)
    def update_theme(self, theme):
        self.theme = theme
        self.setup_sales_stats()
        for window in self.open_windows:
            if window.winfo_exists():
                window.configure(bg=self.theme["bg"])
                if hasattr(window, '_title_label'):
                    window._title_label.configure(
                        bg=self.theme.get("notif_container_bg", self.theme["bg"]),
                        fg=self.theme["fg"],
                        font=("Arial", 18, "bold"))
                if hasattr(window, '_table_frame'):
                    window._table_frame.configure(bg=self.theme["bg"])
                if hasattr(window, '_search_frame'):
                    window._search_frame.configure(bg=self.theme["bg"])
                if hasattr(window, '_search_label'):
                    window._search_label.configure(
                        bg=self.theme["bg"],
                        fg=self.theme["fg"],
                        font=("Arial", 14))
                if hasattr(window, '_search_entry'):
                    window._search_entry.configure(
                        bg=self.theme["bg"],
                        fg=self.theme["fg"])
                if hasattr(window, '_tree'):
                    style = ttk.Style()
                    style.theme_use("clam")
                    style.configure("Treeview",
                        background=self.theme["bg"],
                        foreground=self.theme["fg"],
                        fieldbackground=self.theme["bg"],
                        bordercolor=self.theme.get("notif_container_bg", self.theme["bg"]),
                        borderwidth=2,
                        relief="solid")
                    style.configure("Treeview.Heading",
                        background=self.theme.get("notif_container_bg", self.theme["bg"]),
                        foreground=self.theme["fg"],
                        font=("Arial", 12, "bold"),
                        relief="flat")
                    style.map("Treeview",
                        background=[("selected", self.theme.get("info", "#FF8C00"))],
                        foreground=[("selected", self.theme["fg"])])

