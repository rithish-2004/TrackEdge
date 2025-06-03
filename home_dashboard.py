import tkinter as tk
from tkinter import ttk
from stock_backend import get_stock_data
from sales_stats import SalesStats
from purchase_stats import PurchaseStats
from service_stats import ServiceStats


class HomeDashboardFrame(tk.Frame):
    def __init__(self, parent, get_theme_colors):
        super().__init__(parent)
        self.get_theme_colors = get_theme_colors
        self.theme = self.get_theme_colors()
        if "info" not in self.theme:
            self.theme["info"] = "#FF8C00"
        self._setup_ui()
        self.notification_labels = {}  # Keeps track of current notification widgets

        self._refresh_notifications()

    def update_theme(self):
        self.theme = self.get_theme_colors()
        if "info" not in self.theme:
            self.theme["info"] = "#FF8C00"

        # Update main container backgrounds
        self.configure(bg=self.theme["bg"])
        self.heading_label.configure(bg=self.theme["notif_container_bg"], fg=self.theme["fg"])
        self.left_panel.configure(bg=self.theme["notif_container_bg"])
        self.right_panel.configure(bg=self.theme["bg"])
        self.sales_frame.configure(bg=self.theme["bg"])
        self.purchase_frame.configure(bg=self.theme["bg"])
        self.service_frame.configure(bg=self.theme["bg"])

        # Update notification area
        self.notif_label.configure(bg=self.theme["notif_container_bg"], fg=self.theme["fg"])
        self.notif_canvas.configure(bg=self.theme["notif_container_bg"])
        self.notif_frame.configure(bg=self.theme["notif_container_bg"])

        # Update summary box and all its children
        self.summary_frame.configure(bg=self.theme["notif_container_bg"])
        self.summary_title.configure(bg=self.theme["notif_container_bg"], fg=self.theme["fg"])
        for row, color_key in zip(self.summary_rows, ["danger", "info", "warning", "safe"]):
            row.configure(bg=self.theme["notif_container_bg"])
            canvas = row.winfo_children()[0]
            canvas.configure(bg=self.theme["notif_container_bg"])
            canvas.delete("all")
            canvas.create_oval(2, 2, 18, 18, fill=self.theme.get(color_key, "#FFF"), outline=self.theme.get(color_key, "#FFF"))
            label = row.winfo_children()[1]
            label.configure(bg=self.theme["notif_container_bg"], fg=self.theme["fg"])

        # Update right panel frames and headings
        self.sales_stats.update_theme(self.theme)
        self.purchase_stats.update_theme(self.theme)
        self.service_stats.update_theme(self.theme)
        self._refresh_notifications()
       

    def _setup_ui(self):
        self.configure(bg=self.theme["bg"])

        # Common heading (top row, spans both panels)
        self.heading_label = tk.Label(
            self,
            text="Welcome to TrackEdge",
            font=("Arial", 18, "bold"),
            bg=self.theme["notif_container_bg"],
            fg=self.theme["fg"]
        )
        self.heading_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(8, 4))

        # Left panel (1/3)
        self.left_panel = tk.Frame(self, bg=self.theme["notif_container_bg"], width=340)
        self.left_panel.grid(row=1, column=0, sticky="nswe", padx=(10, 5), pady=10)
        self.left_panel.grid_propagate(False)

        # Notification label
        self.notif_label = tk.Label(
            self.left_panel,
            text="Stock Alerts",
            font=("Arial", 15, "bold"),
            bg=self.theme["notif_container_bg"],
            fg=self.theme["fg"]
        )
        self.notif_label.pack(pady=(0, 5), anchor="w", padx=8)

        # Notifications area (scrollable if needed)
        notif_area = tk.Frame(self.left_panel, bg=self.theme["notif_container_bg"])
        notif_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 0))
        notif_area.rowconfigure(0, weight=1)
        notif_area.columnconfigure(0, weight=1)

        self.notif_canvas = tk.Canvas(notif_area, bg=self.theme["notif_container_bg"],
                                      highlightthickness=0, bd=0)
        self.notif_frame = tk.Frame(self.notif_canvas, bg=self.theme["notif_container_bg"])
        self.notif_frame_id = self.notif_canvas.create_window((0, 0), window=self.notif_frame, anchor="nw")
        self.notif_canvas.grid(row=0, column=0, sticky="nsew")
        self.notif_scroll = ttk.Scrollbar(notif_area, orient="vertical", command=self.notif_canvas.yview)
        self.notif_canvas.configure(yscrollcommand=self.notif_scroll.set)
        self.notif_scroll.grid(row=0, column=1, sticky="ns")
        self.notif_scroll.grid_remove()  # Hide by default

        self.notif_frame.bind("<Configure>", self._on_notif_frame_configure)
        self.notif_canvas.bind("<Configure>", self._on_canvas_configure)

        # Inventory Summary at the bottom of left panel (with color circles)
        self.summary_frame = tk.Frame(self.left_panel, bg=self.theme["notif_container_bg"], bd=2, relief="groove")
        self.summary_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5), padx=10)

        self.summary_title = tk.Label(
            self.summary_frame,
            text="Inventory Summary",
            font=("Arial", 14, "bold"),
            bg=self.theme["notif_container_bg"],
            fg=self.theme["fg"]
        )
        self.summary_title.pack(anchor="w", pady=(0, 3))

        self.summary_rows = []
        color_keys = ["danger", "info", "warning", "safe"]
        for color_key in color_keys:
            row = tk.Frame(self.summary_frame, bg=self.theme["notif_container_bg"])
            canvas = tk.Canvas(row, width=20, height=20, bg=self.theme["notif_container_bg"], highlightthickness=0)
            canvas.create_oval(2, 2, 18, 18, fill=self.theme.get(color_key, "#FFF"), outline=self.theme.get(color_key, "#FFF"))
            canvas.pack(side=tk.LEFT, padx=(0, 6))
            label = tk.Label(row, text="", font=("Arial", 12), bg=self.theme["notif_container_bg"], fg=self.theme["fg"])
            label.pack(side=tk.LEFT)
            row.pack(anchor="w", pady=1)
            self.summary_rows.append(row)

        # Right panel (2/3, split into 3 vertical parts)s
        self.right_panel = tk.Frame(self, bg=self.theme["bg"])
        self.right_panel.grid(row=1, column=1, sticky="nswe", padx=(5, 5), pady=10)
        self.right_panel.grid_propagate(False)

        for i in range(3):
         self.right_panel.rowconfigure(i, weight=1)

        # Sales, Purchase, Service frames (stacked vertically)

        self.sales_frame = tk.Frame(self.right_panel, bg=self.theme["bg"], bd=4, relief="groove")
        self.sales_frame.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.sales_frame.columnconfigure(0, weight=1)


        self.purchase_frame = tk.Frame(self.right_panel, bg=self.theme["bg"], bd=4, relief="groove")
        self.purchase_frame.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)
        self.purchase_frame.columnconfigure(0, weight=1)  # <-- Add this

        self.service_frame = tk.Frame(self.right_panel, bg=self.theme["bg"], bd=4, relief="groove")
        self.service_frame.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)
        self.service_frame.columnconfigure(0, weight=1)


        self.sales_stats = SalesStats(self, self.theme, self.sales_frame)
        self.purchase_stats = PurchaseStats(self, self.theme, self.purchase_frame)
        self.service_stats = ServiceStats(self, self.theme, self.service_frame)  

        self.sales_heading = tk.Label(
            self.sales_frame,
            text="Sales",
            font=("Arial", 14, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        )
        self.sales_heading.grid(row=0, column=0, columnspan=3, pady=(8, 0), sticky="n")


        self.purchase_heading = tk.Label(
            self.purchase_frame,
            text="Purchase",
            font=("Arial", 16, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        )
        self.purchase_heading.grid(row=0, column=0, columnspan=3, pady=(8, 0), sticky="n")

        self.service_heading = tk.Label(
            self.service_frame,
            text="Service",
            font=("Arial", 16, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        )
        self.service_heading.grid(row=0, column=0, columnspan=3, pady=(8, 0), sticky="n")

        # Configure main grid weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

    def _on_canvas_configure(self, event):
        self.notif_canvas.itemconfig(self.notif_frame_id, width=event.width)

    def _on_notif_frame_configure(self, event):
        needs_scroll = self.notif_frame.winfo_height() > self.notif_canvas.winfo_height()
        if needs_scroll:
            self.notif_scroll.grid()
        else:
            self.notif_scroll.grid_remove()
        self.notif_canvas.configure(scrollregion=self.notif_canvas.bbox("all"))
    
    def _refresh_notifications(self):
        stock_data, missing_purchase = get_stock_data()
        low, missing, med, ok = 0, 0, 0, 0

        # Build a set of current notification keys
        current_keys = set()

        # 1. RED: Low stock (<10)
        for item, qty in stock_data.items():
            if qty <=2  and qty >= 0:
                key = f"danger:{item}"
                self._update_or_create_notification(key, f"{item}: {qty}", "danger")
                low += 1
                current_keys.add(key)

        # 2. ORANGE: Missing purchase (sales > purchases)
        for item, diff in missing_purchase.items():
            key = f"info:{item}"
            msg = f"Purchase missing for {item}: {diff} more sold than purchased"
            self._update_or_create_notification(key, msg, "info")
            missing += 1
            current_keys.add(key)

        # 3. YELLOW: Medium stock (10-19)
        for item, qty in stock_data.items():
            if 3 <= qty <= 5:
                key = f"warning:{item}"
                self._update_or_create_notification(key, f"{item}: {qty}", "warning")
                med += 1
                current_keys.add(key)

        # 4. GREEN: Healthy stock (≥20)
        for item, qty in stock_data.items():
            if qty >5:
                key = f"safe:{item}"
                self._update_or_create_notification(key, f"{item}: {qty}", "safe")
                ok += 1
                current_keys.add(key)

        # Remove notifications that are no longer relevant
        for key in list(self.notification_labels.keys()):
            if key not in current_keys:
                self.notification_labels[key].destroy()
                del self.notification_labels[key]

        # Update summary labels (unchanged)
        for row, text in zip(
            self.summary_rows,
            [
                f"Low Stock : {low}",
                f"Purchase Missing: {missing}",
                f"Medium Stock : {med}",
                f"Healthy Stock : {ok}"
            ]
        ):
            label = row.winfo_children()[1]
            label.config(text=text)

        self.after(30000, self._refresh_notifications)
     
    def _update_or_create_notification(self, key, text, level):
        color = self.theme.get(level, "#FFF")
        fg = self.theme["fg"]
        if key in self.notification_labels:
            frame = self.notification_labels[key]
            label = frame.winfo_children()[0]
            label.config(text=text, bg=color, fg=fg)
            frame.config(bg=color)
        else:
            frame = tk.Frame(self.notif_frame, bg=color, padx=8, pady=4)
            frame.pack(fill=tk.X, pady=4, padx=4)
            label = tk.Label(frame, text=text, font=("Arial", 13, "bold"), bg=color, fg=fg)
            label.pack(anchor="w")
            self.notification_labels[key] = frame

    def _add_notification(self, item, qty, level, message=None):
        color = self.theme.get(level, "#FFF")
        fg = self.theme["fg"]
        frame = tk.Frame(self.notif_frame, bg=color, padx=8, pady=4)
        frame.pack(fill=tk.X, pady=4, padx=4)
        if message:
            text = message.format(item=item, diff=qty)
        else:
            text = f"{item}: {qty}"
        label = tk.Label(frame, text=text, font=("Arial", 13, "bold"), bg=color, fg=fg)
        label.pack(anchor="w")

    
