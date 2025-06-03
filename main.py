
import tkinter.ttk as ttk
import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
import time
from splash_screen import SplashScreen
from home_dashboard import HomeDashboardFrame
from inward.inward_add import InwardAddFrame
from inward.inward_view_purchase import InwardViewPurchaseFrame
from inward.inward_record_payment import InwardRecordPaymentFrame
from inward.inward_general_view import InwardGeneralViewFrame
from inward.inward_modify import InwardModifyFrame
from company_display import CompanyInfoDisplay
from outward.outward_add import OutwardAddFrame
from outward.outward_record_payment import OutwardRecordPaymentFrame
from outward.outward_view_purchase import OutwardViewPurchaseFrame
from outward.outward_general_view import OutwardGeneralViewFrame
from outward.outward_modify import OutwardModifyFrame
from service.service_add import ServiceAddFrame  # Adjust filename if different
from service.service_record_payment import ServiceRecordPaymentFrame
from service.service_view_customer import ServiceViewCustomerFrame
from service.service_general_view  import ServiceGeneralViewFrame
from service.service_modify import  CustomerModifyFrame
from themes import THEMES

import themes  # Import your new themes module
from user import CompanyInfoForm, load_company_info
import json


def load_company_info():
    try:
        with open('company_info.json', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

class TrackedgeApp:
    def __init__(self, root):
        self.root = root
        try:
            logo_img = Image.open("logo.png")
            logo_icon = ImageTk.PhotoImage(logo_img)
            self.root.iconphoto(True, logo_icon)
            self.logo_icon = logo_icon  # Save a reference to prevent garbage collection
        except Exception as e:
            print("Logo icon could not be loaded:", e)
        self.root.title("TrackEdge")
        try:
            self.root.state('zoomed')  # Windows
        except:
            try:
                self.root.attributes('-zoomed', True)  # Linux
            except:
                self.root.attributes('-fullscreen', True)  # macOS fallback

        self.theme = themes.load_theme()  # Use the theme loader

        self.icon_sets = {"dark": {}, "light": {}}
        self.sidebar_buttons = []
        company_info = load_company_info()
        if not company_info:
            self.show_company_info_form()
            return
        self.company_info = company_info



        self.setup_header()
        self.setup_sidebar()
        self.setup_main_area()
        self.apply_theme()

    def setup_header(self):
        colors = self.get_current_theme_colors()
        self.header_frame = tk.Frame(self.root, bg=colors["bg"])
        self.header_frame.pack(fill=tk.X)
       


        # --- Title (Trackedge) left of company name ---
        self.title_label = tk.Label(
            self.header_frame,
            text="TrackEdge",
            font=("Arial", 25, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.title_label.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Theme switch button (far right) ---
        self.switch_icons = {
            "dark": self.load_icon("switch.png", "dark"),
            "light": self.load_icon("switch.png", "light")
        }
        self.switch_button = tk.Button(
            self.header_frame,
            image=self.switch_icons[self.theme],
            command=self.switch_theme,
            relief="flat",
            bg=colors["bg"]
        )
        self.switch_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # --- Profile button (to the left of switch button) ---
        self.profile_icons = {
            "dark": self.load_icon("profile.png", "dark"),
            "light": self.load_icon("profile.png", "light")
        }
        self.profile_button = tk.Button(
            self.header_frame,
            image=self.profile_icons[self.theme],
            command=self.show_company_info,
            relief="flat",
            bg=colors["bg"]
        )
        self.profile_button.pack(side=tk.RIGHT, padx=10)

        # --- Company name (bold, to the left of profile button) ---
        self.company_name_label = tk.Label(
            self.header_frame,
            text=self.company_info.get("name", "Company Name"),
            font=("Arial", 12, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.company_name_label.pack(side=tk.RIGHT, padx=10)

        # --- Company logo (to the left of company name) ---
        logo_path = self.company_info.get("logo", "user_logo.jpg")
        try:
            logo_img = Image.open(logo_path).resize((32, 32))
            self.logo_photo = ImageTk.PhotoImage(logo_img)

            self.logo_label = tk.Label(self.header_frame, image=self.logo_photo, bg=colors["bg"])
            self.logo_label.pack(side=tk.RIGHT, padx=(10, 5), pady=5)
        except Exception as e:
            print("Logo could not be loaded:", e)
            self.logo_label = tk.Label(self.header_frame, text="", bg=colors["bg"], fg=colors["fg"])
            self.logo_label.pack(side=tk.RIGHT, padx=(10, 5), pady=5)

    def setup_sidebar(self):
       
        self.sidebar_outer = tk.Frame(self.root, width=200)
        self.sidebar_outer.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_outer.pack_propagate(False)  # Prevent shrinking

        # Canvas for scrolling
        self.sidebar_canvas = tk.Canvas(self.sidebar_outer, borderwidth=0, highlightthickness=0)
        self.sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Vertical scrollbar
        self.sidebar_scrollbar = tk.Scrollbar(self.sidebar_outer, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Sidebar content frame inside the canvas
        self.sidebar = tk.Frame(self.sidebar_canvas)
        self.sidebar_id = self.sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")

        # Configure scrolling
        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)
        self.sidebar.bind("<Configure>", lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))

        # Mousewheel support
        self.sidebar_canvas.bind_all("<MouseWheel>", self._on_sidebar_mousewheel)

        self.add_sidebar_button("home.png", "Home", self.show_home_dashboard)
        self.add_sidebar_label("SALES")
        self.add_sidebar_button("add.png", "Add",self.show_outward_add_form)
        self.add_sidebar_button("payment.png", "Record Payment",self.show_record_payment_outward)
        self.add_sidebar_button("view.png", "View Sales", self.outward_show_view_purchase)
        self.add_sidebar_button("general.png", "General View", self.show_outward_general_view)
        self.add_sidebar_button("modify.png", "Modify",  self.show_outward_modify )

        self.add_sidebar_label("PURCHASE")
        self.add_sidebar_button("add.png", "Add", self.show_inward_add_form)
        self.add_sidebar_button("payment.png", "Record Payment", self.show_record_payment)
        self.add_sidebar_button("view.png", "View Purchase", self.show_view_purchase)
        self.add_sidebar_button("general.png", "General View", self.show_inward_general_view)
        self.add_sidebar_button("modify.png", "Modify", self.show_inward_modify)

        self.add_sidebar_label("SERVICE")
        self.add_sidebar_button("add.png", "Add Service", self.show_add_service)
        self.add_sidebar_button("payment.png", "Record Payment", self.show_service_record_payment)
        self.add_sidebar_button("view.png", "View Purchase", self.service_show_view_customer)
        self.add_sidebar_button("general.png", "General View", self.show_service_general_view)
        self.add_sidebar_button("modify.png", "Modify", self.show_customer_modify)
       
    def show_customer_modify(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        # Set the background color of the main area to match the theme
       
        self.current_frame = CustomerModifyFrame(
            self.main_area,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)



    def show_add_service(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = ServiceAddFrame(self.main_area, self.get_current_theme_colors)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        

    def show_home_dashboard(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = HomeDashboardFrame(self.main_area, self.get_current_theme_colors)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_inward_modify(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = InwardModifyFrame(
            self.main_area,
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_outward_modify(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = OutwardModifyFrame(
            self.main_area,
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_view_purchase(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = InwardViewPurchaseFrame(
            self.main_area,    # parent
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def outward_show_view_purchase(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = OutwardViewPurchaseFrame(
            self.main_area,    # parent
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def service_show_view_customer(self):
    # Remove any existing widgets in the main area
        for widget in self.main_area.winfo_children():
            widget.destroy()
        # Create and pack the ServiceViewCustomerFrame
        self.current_frame = ServiceViewCustomerFrame(
            self.main_area,          # parent
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)



 
    def show_inward_general_view(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = InwardGeneralViewFrame(   # <-- Use the correct frame!
            self.main_area,                        # Parent should be main_area
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_outward_general_view(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = OutwardGeneralViewFrame(   # <-- Use the correct frame!
            self.main_area,                        # Parent should be main_area
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_service_general_view(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = ServiceGeneralViewFrame(   # <-- Use the correct frame!
            self.main_area,                        # Parent should be main_area
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    # In TrackedgeApp class, after existing view methods
    def show_company_info(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        self.current_frame = CompanyInfoDisplay(
            self.main_area,
            self.get_current_theme_colors,
            self.update_company_display
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def update_company_display(self):
        self.company_info = load_company_info()
        self.company_name_label.config(text=self.company_info.get("name", "Company Name"))
        # Optionally update the logo too:
        logo_path = self.company_info.get("logo", "user_logo.jpg")
        try:
            logo_img = Image.open(logo_path).resize((32, 32))
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            self.logo_label.config(image=self.logo_photo, text="")
        except Exception as e:
            print("Logo could not be loaded:", e)
            self.logo_label.config(image="", text="No Logo")
        self.show_company_info()


        
    def get_current_theme_colors(self):
        return themes.THEMES[self.theme]

    def switch_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        themes.save_theme(self.theme)
        self.apply_theme()
        
    def show_inward_add_form(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = InwardAddFrame(self.main_area, self.get_current_theme_colors)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_outward_add_form(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = OutwardAddFrame(self.main_area, self.get_current_theme_colors)
        self.current_frame.pack(fill=tk.BOTH, expand=True)


    def add_sidebar_button(self, icon_file, text, command=None):
        for theme in ["dark", "light"]:
            self.icon_sets[theme][text] = self.load_icon(icon_file, theme)

        btn = tk.Button(
            self.sidebar,
            text="  " + text,
            image=self.icon_sets[self.theme][text],
            compound='left',
            anchor='w',
            command=command,
            font=("Arial", 14)
        )
        btn.pack(fill=tk.X, pady=2, padx=10)
        btn._icon_key = text
        self.sidebar_buttons.append(btn)

    def show_record_payment(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = InwardRecordPaymentFrame(
            self.main_area,    # parent
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_record_payment_outward(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = OutwardRecordPaymentFrame(
            self.main_area,    # parent
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_service_record_payment(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        self.current_frame = ServiceRecordPaymentFrame(
            self.main_area,    # parent
            self.theme,
            self.get_current_theme_colors
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)


    def add_sidebar_label(self, text):
        lbl = tk.Label(self.sidebar, text=text, font=("Arial", 14, "bold"))
        lbl.pack(fill=tk.X, padx=15, pady=(15, 5))
        self.sidebar_buttons.append(lbl)

    def load_icon(self, file, theme, size=(24, 24)):
        try:
            path = os.path.join("icons", theme, file)
            image = Image.open(path).resize(size)
            return ImageTk.PhotoImage(image)
        except:
            return None
        
    def setup_main_area(self):
        self.main_area = tk.Frame(self.root)
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.show_home_dashboard()  # Show dashboard as default



    def display_content(self, content_text):
        for widget in self.main_area.winfo_children():
            widget.destroy()

        if content_text == "INWARD ➜ Add":
            self.current_frame = InwardAddFrame(self.main_area, self.get_current_theme_colors)
            self.current_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.content_label = tk.Label(self.main_area, text=content_text, font=("Arial", 30, "bold"))
            self.content_label.pack(pady=30)

    from tkinter import ttk

    def apply_theme(self):
        colors = self.get_current_theme_colors()

        # --- Set ttk theme and styles for all ttk widgets ---
        style = ttk.Style(self.root)
        if self.theme == "dark":
            style.theme_use("clam")  # 'clam' looks best for dark themes
        else:
            style.theme_use("default")  # 'default' is good for light themes

        # Configure ttk widget colors to match your theme
        style.configure('TCombobox',
            fieldbackground=colors["entry_bg"],
            background=colors["entry_bg"],
            foreground=colors["fg"]
        )
        style.configure('TEntry',
            fieldbackground=colors["entry_bg"],
            foreground=colors["fg"]
        )
        style.configure('TButton',
            background=colors["button_bg"],
            foreground=colors["fg"]
        )
        # Add more as needed for Treeview, etc.

        # --- Classic Tk widgets ---
        self.root.configure(bg=colors["bg"])
        self.header_frame.configure(bg=colors["bg"])
        if hasattr(self, "title_label"):
         self.title_label.configure(bg=colors["bg"], fg=colors["fg"])

        self.switch_button.configure(
            bg=colors["bg"],
            image=self.switch_icons[self.theme]
        )

        self.sidebar.configure(bg=colors["bg"])
        self.main_area.configure(bg=colors["bg"])

        for widget in self.sidebar_buttons:
            if isinstance(widget, tk.Button) and hasattr(widget, "_icon_key"):
                icon_key = widget._icon_key
                widget.configure(
                    bg=colors["button_bg"],
                    fg=colors["fg"],
                    activebackground=colors["button_bg"],
                    image=self.icon_sets[self.theme][icon_key]
                )
            else:
                widget.configure(bg=colors["bg"], fg=colors["fg"])

       
        if hasattr(self, 'current_frame') and self.current_frame and self.current_frame.winfo_exists():
            self.current_frame.update_theme()
        if hasattr(self, 'company_info_form') and self.company_info_form.winfo_exists():
            self.company_info_form.update_theme()
        if getattr(self, "logo_label", None) is not None:
            self.logo_label.config(bg=colors["bg"])
            


        # In existing apply_theme method, add these to the classic widgets section
        self.company_name_label.config(
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.profile_button.config(
            bg=colors["bg"],
            image=self.profile_icons[self.theme]
        )



    
    def _on_sidebar_mousewheel(self, event):
        self.sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def show_company_info_form(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.company_info_form = CompanyInfoForm(self.root, self.get_current_theme_colors, self.on_company_info_submitted)
        self.company_info_form.pack(fill=tk.BOTH, expand=True)

    def on_company_info_submitted(self, info):
        self.company_info = info
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_header()
        self.setup_sidebar()
        self.setup_main_area()
        self.apply_theme()

def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window initially

    splash = SplashScreen(root)
    splash.update()  # Ensure splash appears instantly

    def show_main_app():
        splash.destroy()
        app = TrackedgeApp(root)  # Build the full UI while still hidden

        # Maximize or set fullscreen here, after all widgets are created
        try:
            root.state('zoomed')  # Windows
        except:
            try:
                root.attributes('-zoomed', True)  # Linux
            except:
                root.attributes('-fullscreen', True)  # macOS fallback

        root.deiconify()  # Now show the fully built and maximized window

    root.after(2500, show_main_app)
    root.mainloop()


if __name__ == "__main__":
    main()
