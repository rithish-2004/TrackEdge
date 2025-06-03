import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os

class CompanyInfoDisplay(tk.Frame):
    def __init__(self, parent, theme_colors, update_callback):
        super().__init__(parent)
        self.theme_colors = theme_colors
        self.update_callback = update_callback
        self.logo_img = None
        self.configure(bg=self.theme_colors()["bg"])
        self.load_company_info()
        self.create_widgets()
        self.apply_theme()

    def load_company_info(self):
        try:
            with open("company_info.json", encoding="utf-8") as f:
                self.company_info = json.load(f)
        except Exception:
            self.company_info = {}

    def create_widgets(self):
        # Center everything in a container frame
        self.container = tk.Frame(self, bg=self.theme_colors()["bg"])
        self.container.place(relx=0.5, rely=0.5, anchor="center")

       
        # Info fields
        self.info_frame = tk.Frame(self.container, bg=self.theme_colors()["bg"])
        self.info_frame.pack(pady=10, fill=tk.X)

        fields = [
            ("Admin", self.company_info.get("admin", "")),
            ("Contact", self.company_info.get("contact", "")),
            ("Address", self.company_info.get("address", "")),
            ("About", self.company_info.get("about", "")),
        ]
        for label, value in fields:
            row = tk.Frame(self.info_frame, bg=self.theme_colors()["bg"])
            row.pack(anchor="w", pady=2, fill=tk.X)
            tk.Label(row, text=f"{label}:", font=("Arial", 11, "bold"),
                     bg=self.theme_colors()["bg"], fg=self.theme_colors()["fg"]).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 11),
                     bg=self.theme_colors()["bg"], fg=self.theme_colors()["fg"]).pack(side=tk.LEFT, padx=5)

        # Buttons row
        self.buttons_frame = tk.Frame(self.container, bg=self.theme_colors()["bg"])
        self.buttons_frame.pack(pady=10)
        self.edit_btn = tk.Button(
            self.buttons_frame, text="Edit Details", command=self.edit_details,
            bg=self.theme_colors()["button_bg"], fg=self.theme_colors()["fg"], font=("Arial", 11)
        )
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        if self.company_info.get("logo"):
            self.remove_logo_btn = tk.Button(
                self.buttons_frame, text="Remove Logo", command=self.remove_logo,
                bg=self.theme_colors()["button_bg"], fg=self.theme_colors()["fg"], font=("Arial", 11)
            )
            self.remove_logo_btn.pack(side=tk.LEFT, padx=5)

    def edit_details(self):
        from user import CompanyInfoForm  # Lazy import
        for widget in self.winfo_children():
            widget.destroy()
        self.edit_form = CompanyInfoForm(
    self,
    self.theme_colors,
    self.save_changes,
    initial_data=self.company_info,
    edit_mode=True,
    cancel_callback=self.update_callback  # <-- use the callback passed from main app
)

        self.edit_form.pack(fill=tk.BOTH, expand=True)

    def save_changes(self, new_data):
        # Remove logo if requested
        if new_data.get("logo") == "__REMOVE__":
            new_data["logo"] = ""
        with open("company_info.json", "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)
        self.update_callback()

    def remove_logo(self):
        self.company_info["logo"] = ""
        with open("company_info.json", "w", encoding="utf-8") as f:
            json.dump(self.company_info, f, indent=2)
        self.update_callback()

    def update_theme(self):
        self.apply_theme()

    def apply_theme(self):
        colors = self.theme_colors()
        self.configure(bg=colors["bg"])
        for widget in self.winfo_children():
            self._apply_theme_recursive(widget, colors)

    def _apply_theme_recursive(self, widget, colors):
        try:
            widget.configure(bg=colors["bg"], fg=colors["fg"])
        except Exception:
            try:
                widget.configure(bg=colors["bg"])
            except Exception:
                pass
        for child in widget.winfo_children():
            self._apply_theme_recursive(child, colors)
