import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json

COMPANY_INFO_PATH = "company_info.json"
LOGO_PATH = "user_logo.jpg"
PRIVACY_POLICY = (
  
    "                              TrackEdge Privacy Policy\n\n"
    "                              Effective Date: June 1, 2025\n\n"
    "                                   1. Introduction\n"
    "Thank you for choosing TrackEdge. Your privacy is important to us. This Privacy Policy describes how TrackEdge "
    "('the Application', 'we', 'us', or 'our') collects, uses, stores, and protects your information when you use our desktop software. "
    "By using TrackEdge, you agree to the practices described in this policy.\n\n"
    
    "                              2. Information We Collect\n"
    "TrackEdge is designed to operate primarily on your local device. The types of information the application may handle include:\n"
    "- Inventory data you enter (such as product names, quantities, sales, purchases, and service records).\n"
    "- User preferences and settings (such as themes and interface customizations).\n"
    "TrackEdge does NOT collect, transmit, or share any personal information with external servers or third parties by default.\n\n"
    
    "                              3. How We Use Your Information\n"
    "All data you input into TrackEdge is used solely to provide you with inventory management, sales and purchase tracking, "
    "and service statistics functionalities. Your data remains on your device and is not accessed by us or any third party.\n\n"
    
    "                              4. Data Storage and Security\n"
    "All information entered into TrackEdge is stored locally on your computer, typically in the application's data folder. "
    "We do not access, transmit, or back up your data externally. We recommend that you:\n"
    "- Protect your device with a strong password.\n"
    "- Regularly back up your data to prevent loss in case of device failure.\n"
    "- Keep your operating system and antivirus software up to date.\n"
    "TrackEdge does not access files or folders outside its own data directory unless you explicitly import or export data.\n\n"
    
    "                              5. Data Sharing and Disclosure\n"
    "TrackEdge does not share your information with any third parties. Your data is never sold, rented, or disclosed to others. "
    "If you choose to export data or share reports, you are solely responsible for the distribution of that information.\n\n"
      
    "                                   6. Children’s Privacy\n"
    "TrackEdge is not intended for use by children under the age of 16. We do not knowingly collect or store personal information from children. "
    "If you believe a child has provided us with personal information, please contact us so we can take appropriate action.\n\n"
    
    "                                 7. Your Rights and Choices\n"
    "Because TrackEdge stores all your data locally, you have full control over your information. You may edit, export, or delete your data at any time "
    "using the application's features. Uninstalling the application will not automatically delete your data files; you may remove them manually if desired.\n\n"
    
    "                                  8. Changes to This Policy\n"
    "We may update this Privacy Policy from time to time to reflect changes in our practices or applicable laws. "
    "When we make changes, we will update the effective date at the top of the policy. We encourage you to review this policy periodically.\n\n"
    
    "                                         9. Contact Us\n"
    "If you have any questions, concerns, or feedback regarding this Privacy Policy or the privacy practices of TrackEdge, please contact us at:\n"
    "Email: support@trackedge.com\n\n"
    
    "                                           10. Consent\n"
    "By using TrackEdge, you consent to the terms outlined in this Privacy Policy.\n\n"
    
    "                                           End of Policy."

)


def load_company_info():
    if os.path.exists(COMPANY_INFO_PATH):
        with open(COMPANY_INFO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_company_info(info):
    with open(COMPANY_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

class CompanyInfoForm(tk.Frame):
    def __init__(self, parent, get_colors, on_submit, initial_data=None, edit_mode=False, cancel_callback=None):
        super().__init__(parent)
        self.get_colors = get_colors
        self.on_submit = on_submit
        self.initial_data = initial_data or {}
        self.edit_mode = edit_mode
        self.cancel_callback = cancel_callback  # <--- ADD THIS LINE
        self.logo_path = self.initial_data.get("logo", None)
        self.logo_img = None
        self._build_layout()
        self.update_theme()

    def _build_layout(self):
        colors = self.get_colors()
        # Center everything using a container frame
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Heading
        self.heading = tk.Label(self.container, text="Welcome to Trackedge", font=("Arial", 22, "bold"))
        self.heading.pack(pady=(10, 20))

        # Form fields
        self.form_frame = tk.Frame(self.container)
        self.form_frame.pack(pady=10)

        self.entries = {}
        fields = [
            ("Company/Shop Name", "name"),
            ("Admin Name", "admin"),
            ("About", "about"),
            ("Contact Number", "contact"),
            ("Address", "address")
        ]
        for i, (label, key) in enumerate(fields):
            row = tk.Frame(self.form_frame)
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=label, font=("Arial", 14), width=18, anchor="e").pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(row, font=("Arial", 14), width=32)
            entry.pack(side=tk.LEFT, padx=5)
            # Insert the value from initial_data if present
            entry.insert(0, self.initial_data.get(key, ""))
            self.entries[key] = entry


        # Logo upload (optional)
        logo_row = tk.Frame(self.form_frame)
        logo_row.pack(fill=tk.X, pady=5)
        tk.Label(logo_row, text="Logo (optional)", font=("Arial", 14), width=18, anchor="e").pack(side=tk.LEFT, padx=5)
        self.logo_preview = tk.Label(logo_row, text="No Logo", width=10, height=2, bg=colors["bg"])
        self.logo_preview.pack(side=tk.LEFT, padx=(0, 12))
        self.logo_btn = tk.Button(logo_row, text="Upload Logo", font=("Arial", 12), command=self.upload_logo)
        self.logo_btn.pack(side=tk.LEFT)

        if self.logo_path and os.path.exists(self.logo_path):
            img = Image.open(self.logo_path).resize((80, 80))
            self.logo_img = ImageTk.PhotoImage(img)
            self.logo_preview.configure(image=self.logo_img, text="")
            self.logo_preview.image = self.logo_img
        else:
            self.logo_preview.configure(text="No Logo", image="")


        if not self.edit_mode:
            policy_frame = tk.Frame(self.container)
            policy_frame.pack(pady=(18, 0))
            self.policy_text = tk.Text(policy_frame, width=62, height=7, font=("Arial", 10), wrap="word", bd=1, relief="solid")
            self.policy_text.insert("1.0", PRIVACY_POLICY)
            self.policy_text.configure(state="disabled")
            self.policy_text.pack(side=tk.LEFT, fill=tk.BOTH)
            self.policy_scroll = tk.Scrollbar(policy_frame, orient="vertical", command=self.policy_text.yview)
            self.policy_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            self.policy_text.configure(yscrollcommand=self.policy_scroll.set)
            self.policy_text.bind("<ButtonRelease-1>", self._on_policy_scroll)
            self.policy_text.bind("<KeyRelease>", self._on_policy_scroll)
            self.policy_text.bind("<MouseWheel>", self._on_policy_scroll)

            # Policy checkbox (hidden initially)
            self.policy_var = tk.IntVar()
            self.policy_check = tk.Checkbutton(
                self.container,
                text="I have read and accept the Privacy Policy",
                variable=self.policy_var,
                font=("Arial", 12),
                command=self._on_policy_check
            )
            self.policy_check.pack(pady=(8, 12))
            self.policy_check.pack_forget()  # Hide initially

            # Submit button (disabled initially)
            self.submit_btn = tk.Button(self.container, text="Save & Continue", font=("Arial", 14, "bold"), command=self.submit, state=tk.DISABLED)
            self.submit_btn.pack(pady=20)
        else:
            # New code: no extra frame, both buttons themed and side by side
            self.btn_frame = tk.Frame(self.container, bg=colors["bg"])
            self.btn_frame.pack(pady=20)
            self.btn_frame.pack(anchor="center")

            self.submit_btn = tk.Button(
                self.btn_frame,
                text="Save",
                font=("Arial", 14, "bold"),
                command=self.submit,
                state=tk.NORMAL
            )
            self.submit_btn.pack(side=tk.LEFT, padx=(0, 10))

            self.cancel_btn = tk.Button(
                self.btn_frame,
                text="Cancel",
                font=("Arial", 14, "bold"),
                command=self.cancel_edit,
                state=tk.NORMAL
            )
            self.cancel_btn.pack(side=tk.LEFT)





       
    def cancel_edit(self):
        self.destroy()
        if hasattr(self, "cancel_callback") and self.cancel_callback:
            self.cancel_callback()


    def upload_logo(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if path:
            img = Image.open(path).convert("RGB")
            img = img.resize((80, 80))
            img.save(LOGO_PATH, format="JPEG")
            self.logo_img = ImageTk.PhotoImage(img)
            self.logo_preview.configure(image=self.logo_img, text="")
            self.logo_preview.image = self.logo_img  # Keep reference!
            self.logo_path = LOGO_PATH

    def submit(self):
        colors = self.get_colors()
        info = {k: e.get().strip() for k, e in self.entries.items()}

        # Validation
        if not all(info.values()):
            custom_messagebox(parent=self, title="Missing Info", message="Please fill in all fields.", colors=colors, icon="warning")
            return

        mobile = info.get("contact", "")
        if not (mobile.isdigit() and len(mobile) == 10):
            custom_messagebox(parent=self, title="Invalid Mobile Number", message="Contact Number must be exactly 10 digits.", colors=colors, icon="error")
            return

        if self.logo_path and os.path.exists(self.logo_path):
            info["logo"] = LOGO_PATH
        else:
            info["logo"] = "no logo"

        if self.edit_mode:
            answer = custom_yesno_messagebox(
                parent=self,
                title="Confirm Edit",
                message="Are you sure you want to edit details?",
                colors=colors,
                icon="question"
            )
            if not answer:
                # User clicked "No": close the form and show the info display again
                if self.cancel_callback:
                    self.destroy()  # Remove the edit form
                    self.cancel_callback()
                return
        else:
            if not self.policy_var.get():
                custom_messagebox(parent=self, title="Privacy Policy", message="You must accept the Privacy Policy to continue.", colors=colors, icon="error")
                return

        save_company_info(info)
        self.on_submit(info)

    def update_theme(self):
        colors = self.get_colors()
        self.configure(bg=colors["bg"])
        self.container.configure(bg=colors["bg"])
        self.heading.configure(bg=colors["bg"], fg=colors["fg"])
        self.form_frame.configure(bg=colors["bg"])
        for widget in self.form_frame.winfo_children():
            widget.configure(bg=colors["bg"])
            for subwidget in widget.winfo_children():
                if isinstance(subwidget, tk.Label):
                    subwidget.configure(bg=colors["bg"], fg=colors["fg"])
                elif isinstance(subwidget, tk.Entry):
                    subwidget.configure(bg=colors["entry_bg"], fg=colors["fg"])
                elif isinstance(subwidget, tk.Button):
                    subwidget.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])
        self.logo_preview.configure(bg=colors["bg"])
        self.logo_btn.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])
        if hasattr(self, "policy_text"):
         self.policy_text.configure(bg=colors["entry_bg"], fg=colors["fg"])
        if hasattr(self, "policy_check"):
         self.policy_check.configure(bg=colors["bg"], fg=colors["fg"], activebackground=colors["bg"])

        self.submit_btn.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])
        
        if hasattr(self, "cancel_btn"):
         self.cancel_btn.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])



    def _on_policy_scroll(self, event=None):
        if self._policy_scrolled_to_end():
            self.policy_check.pack(pady=(8, 12))
        else:
            self.policy_check.pack_forget()
            self.submit_btn.config(state=tk.DISABLED)
            self.policy_var.set(0)

    def _policy_scrolled_to_end(self):
        return float(self.policy_text.yview()[1]) >= 0.99

    def _on_policy_check(self):
        if self.policy_var.get():
            self.submit_btn.config(state=tk.NORMAL)
        else:
            self.submit_btn.config(state=tk.DISABLED)

    def _labeled_entry(self, label, value):
        colors = self.get_colors()
        frame = tk.Frame(self.container, bg=colors["bg"])
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=label, font=("Arial", 11, "bold"), bg=colors["bg"], fg=colors["fg"]).pack(side=tk.LEFT)
        entry = tk.Entry(frame, font=("Arial", 11), bg=colors["entry_bg"], fg=colors["fg"])
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        entry.insert(0, value)
        return entry
    
    def choose_logo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.logo_path = file_path
            img = Image.open(file_path).resize((48, 48))
            self.logo_img = ImageTk.PhotoImage(img)
            self.logo_label.config(image=self.logo_img, text="")

    def remove_logo(self):
        self.logo_path = None
        self.logo_label.config(image="", text="No Logo")

    def submit_company_info(self):
        info = {
            "name": self.name_entry.get(),
            "admin": self.admin_entry.get(),
            "contact": self.contact_entry.get(),
            "address": self.address_entry.get(),
            "about": self.about_entry.get(),
            "logo": self.logo_path if self.logo_path else ""
        }
        self.on_submit(info)
    
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
        
def custom_messagebox(parent, title, message, colors, icon="info"):
    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.grab_set()
    win.configure(bg=colors["bg"])
    win.resizable(False, False)

    # Center the window
    win.update_idletasks()
    x = parent.winfo_rootx() + parent.winfo_width() // 2 - 150
    y = parent.winfo_rooty() + parent.winfo_height() // 2 - 60
    win.geometry(f"300x120+{x}+{y}")

    # Icon (optional)
    if icon == "error":
        icon_text = "❌"
    elif icon == "warning":
        icon_text = "⚠️"
    else:
        icon_text = "ℹ️"

    icon_label = tk.Label(win, text=icon_text, font=("Arial", 24), bg=colors["bg"], fg=colors["fg"])
    icon_label.pack(pady=(12, 0))

    label = tk.Label(win, text=message, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"], wraplength=260)
    label.pack(pady=(8, 0), padx=10)

    btn = tk.Button(win, text="OK", command=win.destroy, font=("Arial", 11, "bold"),
                    bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])
    btn.pack(pady=(12, 10))

    win.wait_window()

def custom_yesno_messagebox(parent, title, message, colors, icon="question"):
    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.grab_set()
    win.configure(bg=colors["bg"])
    win.resizable(False, False)

    # Center the window
    win.update_idletasks()
    x = parent.winfo_rootx() + parent.winfo_width() // 2 - 150
    y = parent.winfo_rooty() + parent.winfo_height() // 2 - 60
    win.geometry(f"300x120+{x}+{y}")

    # Icon
    if icon == "error":
        icon_text = "❌"
    elif icon == "warning":
        icon_text = "⚠️"
    elif icon == "question":
        icon_text = "❓"
    else:
        icon_text = "ℹ️"

    icon_label = tk.Label(win, text=icon_text, font=("Arial", 24), bg=colors["bg"], fg=colors["fg"])
    icon_label.pack(pady=(12, 0))

    label = tk.Label(win, text=message, font=("Arial", 12), bg=colors["bg"], fg=colors["fg"], wraplength=260)
    label.pack(pady=(8, 0), padx=10)

    result = {"answer": None}
    def yes():
        result["answer"] = True
        win.destroy()
    def no():
        result["answer"] = False
        win.destroy()

    btn_frame = tk.Frame(win, bg=colors["bg"])
    btn_frame.pack(pady=(12, 10))
    btn_yes = tk.Button(btn_frame, text="Yes", command=yes, font=("Arial", 11, "bold"),
                        bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"], width=8)
    btn_yes.pack(side=tk.LEFT, padx=8)
    btn_no = tk.Button(btn_frame, text="No", command=no, font=("Arial", 11, "bold"),
                       bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"], width=8)
    btn_no.pack(side=tk.LEFT, padx=8)

    win.wait_window()
    return result["answer"]
