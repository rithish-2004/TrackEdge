import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import random
import json
import subprocess
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import themes
from service import service_backend

class ServiceAddFrame(tk.Frame):
    def __init__(self, parent, get_colors):
        super().__init__(parent)
        self.get_colors = get_colors
        self.build_form()
        self.update_theme()
    
    def center_fault_text(self, event=None):
     self.desc_text.tag_add("center", "1.0", "end")
    
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"


    def build_form(self):
        self.grid_columnconfigure(0, weight=1)
        row = 0
        padx = 200

        self.title_label = tk.Label(self, text="Add Service", font=("Arial", 18, "bold"))
        self.title_label.grid(row=row, column=0, pady=(20, 10), padx=padx, sticky="ew")
        row += 1

        # Name
        self.name_label = tk.Label(self, text="Name*:", anchor="center", justify="center")
        self.name_label.grid(row=row, column=0, padx=padx, sticky="ew")
        row += 1
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(self, textvariable=self.name_var, width=14, justify="center")
        self.name_combo.grid(row=row, column=0, pady=(0, 6), padx=padx, sticky="ew")
        row += 1

        # Place
        self.place_label = tk.Label(self, text="Place*:", anchor="center", justify="center")
        self.place_label.grid(row=row, column=0, padx=padx, sticky="ew")
        row += 1
        self.place_var = tk.StringVar()
        self.place_entry = tk.Entry(self, textvariable=self.place_var, width=14, justify="center")
        self.place_entry.grid(row=row, column=0, pady=(0, 6), padx=padx, sticky="ew")
        row += 1

        # Phone
        self.phone_label = tk.Label(self, text="Phone*:", anchor="center", justify="center")
        self.phone_label.grid(row=row, column=0, padx=padx, sticky="ew")
        row += 1
        self.phone_var = tk.StringVar()
        self.phone_combo = ttk.Combobox(self, textvariable=self.phone_var, width=14, justify="center")
        self.phone_combo.grid(row=row, column=0, pady=(0, 10), padx=padx, sticky="ew")
        row += 1

        # Service Name (required)
        self.service_label = tk.Label(self, text="Model*:", anchor="center", justify="center")
        self.service_label.grid(row=row, column=0, padx=padx, sticky="ew")
        row += 1
        self.service_var = tk.StringVar()
        self.service_entry = tk.Entry(self, textvariable=self.service_var, width=14, justify="center")
        self.service_entry.grid(row=row, column=0, pady=(0, 6), padx=padx, sticky="ew")
        row += 1

        # Description (optional, multi-line, small)
        self.desc_label = tk.Label(self, text="Fault:", anchor="center", justify="center")
        self.desc_label.grid(row=row, column=0, padx=padx, sticky="ew")
        row += 1
        self.desc_text = tk.Text(self, width=14, height=2, wrap="word")
        self.desc_text.tag_configure("center", justify='center')
        self.desc_text.grid(row=row, column=0, pady=(0, 6), padx=padx, sticky="ew")
        self.desc_text.bind("<KeyRelease>", self.center_fault_text)
        self.desc_text.bind("<Tab>", self.focus_next_widget)  # Add this line!

        row += 1

        # Amount (optional)
        self.amount_label = tk.Label(self, text="Estimated Amount:", anchor="center", justify="center")
        self.amount_label.grid(row=row, column=0, padx=padx, sticky="ew")
        row += 1
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(self, textvariable=self.amount_var, width=14, justify="center")
        self.amount_entry.grid(row=row, column=0, pady=(0, 6), padx=padx, sticky="ew")
        row += 1

        # Advance (optional)
        self.advance_label = tk.Label(self, text="Advance:", anchor="center", justify="center")
        self.advance_label.grid(row=row, column=0, padx=padx, sticky="ew")
        row += 1
        self.advance_var = tk.StringVar()
        self.advance_entry = tk.Entry(self, textvariable=self.advance_var, width=14, justify="center")
        self.advance_entry.grid(row=row, column=0, pady=(0, 6), padx=padx, sticky="ew")
        row += 1

        # Submit Button
        self.submit_btn = tk.Button(self, text="Submit", width=14, command=self.submit_form)
        self.submit_btn.grid(row=row, column=0, pady=(5, 20), padx=padx, sticky="ew")

        self.name_combo.bind('<KeyRelease>', self.on_name_type)
        self.name_combo.bind('<<ComboboxSelected>>', self.on_name_select)
        self.name_combo.bind('<FocusIn>', self.on_name_focus)
        self.phone_combo.bind('<KeyRelease>', self.on_phone_type)
        self.phone_combo.bind('<<ComboboxSelected>>', self.on_phone_select)
        self.phone_combo.bind('<FocusIn>', self.on_phone_focus)

    # --- Customer autocomplete logic ---
    def on_name_type(self, event):
        prefix = self.name_var.get()
        results = service_backend.search_customer_by_name(prefix)
        names = [r[0] for r in results]
        self.name_combo['values'] = names

    def on_name_select(self, event):
        selected_name = self.name_var.get()
        result = service_backend.customer_exists_by_name(selected_name)
        if result:
            place, phone = result
            self.place_var.set(place)
            self.phone_var.set(phone)

    def on_phone_type(self, event):
        prefix = self.phone_var.get()
        results = service_backend.search_customer_by_phone(prefix)
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones

    def on_phone_select(self, event):
        selected_phone = self.phone_var.get()
        result = service_backend.customer_exists_by_phone(selected_phone)
        if result:
            name, place = result
            self.name_var.set(name)
            self.place_var.set(place)

    def on_name_focus(self, event):
        results = service_backend.search_customer_by_name('')
        names = [r[0] for r in results]
        self.name_combo['values'] = names

    def on_phone_focus(self, event):
        results = service_backend.search_customer_by_phone('')
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones

    def update_theme(self):
        colors = self.get_colors()
        self.config(bg=colors["bg"])
        for widget in [
            self.title_label, self.name_label, self.place_label, self.phone_label,
            self.service_label, self.amount_label, self.desc_label, self.advance_label
        ]:
            widget.config(bg=colors["bg"], fg=colors["fg"])
        for widget in [
            self.place_entry, self.service_entry, self.amount_entry, self.advance_entry
        ]:
            widget.config(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"], justify="center")
        self.desc_text.config(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"])
        self.submit_btn.config(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])
        style = ttk.Style()
        style.configure("Custom.TCombobox",
                        fieldbackground=colors["entry_bg"],
                        background=colors["entry_bg"],
                        foreground=colors["fg"])
        self.name_combo.configure(style="Custom.TCombobox")
        self.phone_combo.configure(style="Custom.TCombobox")

    def show_notification(self, message, title="Notification", on_close=None):
        colors = self.get_colors()
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.configure(bg=colors["bg"])
        popup.transient(self)
        popup.grab_set()
        popup.resizable(False, False)

        label = tk.Label(
            popup, text=message, bg=colors["bg"], fg=colors["fg"],
            font=("Arial", 12), wraplength=220, justify="center"
        )
        label.pack(padx=20, pady=(15, 10), fill="both", expand=True)

        btn_frame = tk.Frame(popup, bg=colors["bg"])
        btn_frame.pack(pady=(0, 15))

        def close_popup():
            popup.destroy()
            if on_close:
                on_close()

        ok_btn = tk.Button(
            btn_frame, text="OK", command=close_popup,
            bg=colors["button_bg"], fg=colors["fg"],
            activebackground=colors["button_bg"], width=8
        )
        ok_btn.pack(side="left", padx=8)

        popup.update_idletasks()
        width = popup.winfo_reqwidth()
        height = popup.winfo_reqheight()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.wait_window()

    def submit_form(self):
        from datetime import datetime
        name = self.name_var.get().strip()
        place = self.place_var.get().strip()
        phone = self.phone_var.get().strip()
        service = self.service_var.get().strip()
        desc = self.desc_text.get("1.0", "end").strip()
        amount = self.amount_var.get().strip()
        advance = self.advance_var.get().strip()

        if not name or not place or not phone or not service:
            self.show_notification("Please fill all required fields.", title="Missing Data")
            return

        if not (phone.isdigit() and len(phone) == 10):
            self.show_notification("Phone number must be exactly 10 digits.", title="Invalid Phone Number")
            return

        try:
            total_amount = float(amount) if amount else 0.0
            amount_paid = float(advance) if advance else 0.0
        except ValueError:
            self.show_notification("Amount and Advance must be numbers.", title="Invalid Data")
            return

        if amount and advance and amount_paid > total_amount:
            self.show_notification(
                "Advance amount cannot be greater than the estimated amount.",
                title="Invalid Advance"
            )
            return

        # --- Conflict check ---
        conflict = service_backend.check_name_phone_conflict(name, phone)
        if conflict == "phone_conflict":
            self.show_notification(
                "This phone number is already registered with another name.",
                title="Duplicate Phone Number"
            )
            return
        if conflict == "name_conflict":
            self.show_notification(
                "This name is already registered with another phone number.",
                title="Duplicate Name"
            )
            return

        # --- Add customer ---
        status = "completed" if total_amount == amount_paid else "pending"
        service_id, result, new_total, new_paid, new_remaining, status = service_backend.add_or_update_service_customer(
            customer_name=name,
            place=place,
            phone_number=phone,
            total_amount=total_amount,
            amount_paid=amount_paid
        )


        # --- Add service item ---
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        service_backend.add_service_item(
            service_id,  # positional arguments as required!
            service,
            desc,
            total_amount
        )

        # --- Add payment if any advance ---
        if amount_paid > 0:
            service_backend.add_service_payment(
                service_id,
                amount_paid,
                "Payment"
            )

        to_pay = total_amount - amount_paid

        bill_data = {
            "name": name,
            "place": place,
            "phone": phone,
            "service": service,
            "desc": desc,
            "total_amount": total_amount,
            "amount_paid": amount_paid,
            "to_pay": to_pay,
            "date": datetime.now().strftime("%d-%m-%Y"),
        }

        self.generate_and_print_bill(bill_data)
        self.show_notification("Service added and bill sent to printer.", title="Service Added", on_close=self.reset_form)
        
        

    def generate_and_print_bill(self, bill_data):
        # Load company info
        with open("company_info.json", "r", encoding="utf-8") as f:
            company = json.load(f)
        # Ensure bills folder exists
        os.makedirs("bills", exist_ok=True)
        bill_number = get_next_bill_number()
        item_name = "".join([c for c in bill_data['service'] if c.isalnum()])[:10]
        filename = f"bills/{item_name}_{bill_number}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        def draw_bill(y_offset, copy_label):
            left = 30
            right = width - 30
            top = height - y_offset

            # Rectangle
            c.setLineWidth(1)
            c.rect(left, top - 370, right - left, 370)

            # Company info (logo, name, etc.)
            if os.path.exists(company.get("logo", "")):
                c.drawImage(company["logo"], left + 5, top - 60, width=50, height=50, mask='auto')
            c.setFont("Helvetica-Bold", 10)
            c.drawRightString(right - 5, top - 10, f"Cell : {company['contact']}")
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString((left + right) / 2, top - 20, company["name"])
            c.setFont("Helvetica", 12)
            c.drawCentredString((left + right) / 2, top - 40, company["about"])
            c.setFont("Helvetica", 10)
            c.drawCentredString((left + right) / 2, top - 55, company["address"])
            c.line(left + 5, top - 65, right - 5, top - 65)

            # Bill header
            c.setFont("Helvetica", 10)
            c.drawString(left + 10, top - 80, f"No: {bill_number}")
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString((left + right) / 2, top - 80, "SERVICE JOB CARD")
            c.setFont("Helvetica", 10)
            c.drawRightString(right - 10, top - 80, f"Date: {bill_data['date']}")

            # Customer info (all bold)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 10, top - 100, "To:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 45, top - 100, bill_data["name"])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 220, top - 100, "Ph:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 250, top - 100, bill_data["phone"])

            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 10, top - 120, "Place:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 55, top - 120, bill_data["place"])

            # Item info (all bold)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 10, top - 145, "Model:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 60, top - 145, bill_data["service"])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 10, top - 165, "Fault:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 55, top - 165, bill_data["desc"])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 10, top - 185, "Estimated Amount:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 120, top - 185, str(bill_data["total_amount"]))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 10, top - 205, "Advance:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 70, top - 205, str(bill_data["amount_paid"]))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left + 10, top - 225, "Balance:")
            c.setFont("Helvetica", 10)
            c.drawString(left + 60, top - 225, str(bill_data["to_pay"]))

            # Separator
            c.line(left + 5, top - 235, right - 5, top - 235)

            # IMPORTANT section (English)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(left + 10, top - 245, "IMPORTANT :")
            c.setFont("Helvetica", 8)
            important_lines = [
                "🔹 Please collect your item within two week. After that, we are not responsible.",
                "🔹 Please bring this Job Card receipt for delivery. Without it, the item will not be handed over.",
                "🔹 No warranty for repaired or replaced parts unless specified.",
                "🔹 If the product is not delivered by the due date, it is due to unavailability of spares or ongoing product issues.",
                "🔹 If service cannot be completed, the product will be returned and may not be in the same condition as received. No guarantee for the return.",
                "🔹 All legal matters are subject to jurisdiction within Madurai district only."
            ]
            for i, line in enumerate(important_lines):
                c.drawString(left + 20, top - 260 - i * 13, line)

            # For company and signature
            c.setFont("Helvetica", 9)
            c.drawRightString(right - 10, top - 350, "Signature")
            c.setFont("Helvetica", 9)
            c.drawString(left + 10, top - 350, f"For {company['name']}")
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(left + 10, top - 365, copy_label)

        # Draw two bills, if space, else new page
        draw_bill(30, "Customer Copy")
        if (30 + 400) < (A4[1] - 30):
            draw_bill(430, "Admin Copy")
        else:
            c.showPage()
            draw_bill(30, "Admin Copy")

        c.save()
        self.print_pdf(filename)

    def print_pdf(self, pdf_path):
        if sys.platform == "win32":
            os.startfile(os.path.abspath(pdf_path))
        elif sys.platform == "darwin":
            subprocess.run(["open", pdf_path])
        else:
            subprocess.run(["xdg-open", pdf_path])

    def reset_form(self):
        self.name_var.set("")
        self.place_var.set("")
        self.phone_var.set("")
        self.service_var.set("")
        self.desc_text.delete("1.0", "end")
        self.amount_var.set("")
        self.advance_var.set("")

   
   
def get_next_bill_number():
        counter_file = "bill_counter.json"
        # If the file does not exist, create it
        if not os.path.exists(counter_file):
            with open(counter_file, "w") as f:
                json.dump({"last_bill_number": 0}, f)
        # Read the current counter
        with open(counter_file, "r") as f:
            data = json.load(f)
        last_number = data.get("last_bill_number", 0)
        next_number = last_number + 1
        data["last_bill_number"] = next_number
        # Write back the updated counter
        with open(counter_file, "w") as f:
            json.dump(data, f)
        # Return the formatted bill number
        return f"BILL{next_number:05d}"

# Example usage:
if __name__ == "__main__":
    def get_colors():
        theme = themes.load_theme()
        return themes.THEMES[theme]

    root = tk.Tk()
    root.title("Add Service")
    root.geometry("400x600")
    frame = ServiceAddFrame(root, get_colors)
    frame.pack(fill="both", expand=True)

    def switch_theme(event=None):
        curr = themes.load_theme()
        new = "dark" if curr == "light" else "light"
        themes.save_theme(new)
        frame.update_theme()
    root.bind("<F5>", switch_theme)

    root.mainloop()
