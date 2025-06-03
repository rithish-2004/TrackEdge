import tkinter as tk
from tkinter import ttk
import themes
from outward import customer_backend
from inward import db_backend
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

from datetime import datetime
class OutwardAddFrame(tk.Frame):
    def __init__(self, parent, get_colors):
        super().__init__(parent)
        self.get_colors = get_colors
        self.rows = []
        self.build_title()
        self.build_header_fields()
        self.build_table_area()
        self.build_footer_fields()
        self.configure_theme()
        self.add_table_row()  # <-- Only here, after all frames are created!
        
    def build_title(self):
        colors = self.get_colors()
        self.title_label = tk.Label(self, text="Add Sales", font=("Arial", 22, "bold"),
                                bg=colors["bg"], fg=colors["fg"])
        self.title_label.pack(pady=(20, 10))
    
    def get_next_bill_number(self):
        path = os.path.join("outward", "bill_counter.json")
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump({"counter": 1}, f)
        with open(path) as f:
            data = json.load(f)
        bill_no = f"CUSTBILL{data['counter']:05d}"
        data['counter'] += 1
        with open(path, "w") as f:
            json.dump(data, f)
        return bill_no

    def load_company_info(self):
        with open("company_info.json") as f:
            return json.load(f)
    def generate_bill(self):
        data = self._bill_data
        bills_dir = "sales_bills"
        os.makedirs(bills_dir, exist_ok=True)
        bill_filename = os.path.join(bills_dir, f"{data['bill_no']}.pdf")
        self.generate_bill_pdf(
            data["company"],
            data["bill_no"],
            data["customer"],
            data["items"],
            data["total_qty"],
            data["total_amount"],
            filename=bill_filename
        )
        try:
            os.startfile(bill_filename)
        except Exception:
            pass


    def generate_bill_pdf(self, company, bill_no, customer, items, total_qty, total_amount, filename):
        styles = getSampleStyleSheet()
        bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12)
        normal = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Helvetica', fontSize=11)
        company_style = ParagraphStyle('Company', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, alignment=1, spaceAfter=2)
        about_style = ParagraphStyle('About', parent=styles['Normal'], fontName='Helvetica', fontSize=12, alignment=1, spaceAfter=2)
        contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontName='Helvetica', fontSize=11, alignment=1, spaceAfter=10)

        doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        story = []

        def draw_border(canvas, doc):
            width, height = A4
            margin = 20
            canvas.saveState()
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(2)
            canvas.rect(margin, margin, width - 2*margin, height - 2*margin)
            canvas.restoreState()

        def bill_elements():
            elements = []
            # Company Name as heading
            elements.append(Paragraph(f"<b>{company['name']}</b>", company_style))
            # About and Contact, centered
            if company.get("about", ""):
                elements.append(Paragraph(company.get("about", ""), about_style))
            elements.append(Paragraph(f"Contact: {company.get('contact', '')}", contact_style))
            # Space, then horizontal line
            elements.append(Spacer(1, 8))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=1, spaceAfter=12))
            # Bill info table
            info_data = [
                [
                    Paragraph(f"<b>Bill No:</b> {bill_no}", normal),
                    "",
                    Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y')}", normal)
                ],
                [
                    Paragraph(f"<b>Name:</b> {customer.get('name','')}", normal),
                    Paragraph(f"<b>Phone:</b> {customer.get('phone','')}", normal),
                    Paragraph(f"<b>Place:</b> {customer.get('place','')}", normal)
                ]
            ]
            info_table = Table(info_data, colWidths=[120, 220, 120])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
                ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black),
                ('LINEABOVE', (0,0), (-1,0), 0.5, colors.black),
                ('LINEBELOW', (0,1), (-1,1), 0.5, colors.black),
                ('LINEABOVE', (0,1), (-1,1), 0.5, colors.black),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 14))
            # Items Table
            table_data = [
                [Paragraph("<b>S.No</b>", bold), Paragraph("<b>Particulars</b>", bold), Paragraph("<b>Qty</b>", bold), Paragraph("<b>Amount</b>", bold)]
            ]
            for idx, item in enumerate(items, 1):
                table_data.append([
                    str(idx),
                    item["name"],
                    str(item["qty"]),
                    f"{item['amount']:.2f}"
                ])
            table_data.append(["", "", "", ""])
            table_data.append([
                "",
                Paragraph("<b>Total</b>", bold),
                Paragraph(f"<b>{total_qty}</b>", bold),
                Paragraph(f"<b>{total_amount:.2f}</b>", bold)
            ])
            table_data.append(["", "", "", ""])
            bill_table = Table(table_data, colWidths=[50, 220, 70, 90], repeatRows=1)
            bill_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-2), 0.8, colors.black),
                ('BOX', (0,0), (-1,-2), 1.5, colors.black),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('ALIGN', (2,0), (3,-1), 'CENTER'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LINEABOVE', (0,-2), (-1,-2), 1, colors.black),
                ('FONTNAME', (1,-2), (-1,-2), 'Helvetica-Bold'),
            ]))
            elements.append(bill_table)
            elements.append(Spacer(1, 24))
            # Signature
            signature_table = Table(
                [
                    ["", Paragraph("<b>Signature:</b> ", normal)]
                ],
                colWidths=[320, 180]
            )
            signature_table.setStyle(TableStyle([
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('VALIGN', (1,0), (1,0), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 20),
                ('FONTNAME', (1,0), (1,0), 'Helvetica-Bold'),
            ]))
            elements.append(signature_table)
            elements.append(Spacer(1, 10))
            return elements

        story.extend(bill_elements())
        doc.build(story, onFirstPage=draw_border, onLaterPages=draw_border)
    
    def build_header_fields(self):
        header_frame = tk.Frame(self)
        header_frame.pack(pady=20)
        self.header_frame = header_frame

        self.name_var = tk.StringVar()
        self.place_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        tk.Label(header_frame, text="Name:").grid(row=0, column=0, padx=10)
        self.name_combo = ttk.Combobox(header_frame, textvariable=self.name_var, width=20)
        self.name_combo.grid(row=0, column=1, padx=10)

        tk.Label(header_frame, text="Place:").grid(row=0, column=2, padx=10)
        tk.Entry(header_frame, textvariable=self.place_var, width=20).grid(row=0, column=3, padx=10)

        tk.Label(header_frame, text="Phone:").grid(row=0, column=4, padx=10)
        self.phone_combo = ttk.Combobox(header_frame, textvariable=self.phone_var, width=20)
        self.phone_combo.grid(row=0, column=5, padx=10)

        # --- Now bind events, after creating the Comboboxes! ---
        self.name_combo.bind('<KeyRelease>', self.on_name_type)
        self.name_combo.bind('<<ComboboxSelected>>', self.on_name_select)
        self.name_combo.bind('<FocusIn>', self.on_name_focus)

        self.phone_combo.bind('<KeyRelease>', self.on_phone_type)
        self.phone_combo.bind('<<ComboboxSelected>>', self.on_phone_select)

        self.phone_combo.bind('<FocusIn>', self.on_phone_focus)

    def on_name_type(self, event):
        prefix = self.name_var.get()
        results = customer_backend.search_customer_by_name(prefix)
        names = [r[0] for r in results]
        self.name_combo['values'] = names


    def on_name_select(self, event):
        selected_name = self.name_var.get()
        results = customer_backend.search_customer_by_name(selected_name)
        if results:
            place, phone = results[0][1], results[0][2]
            self.place_var.set(place)
            self.phone_var.set(phone)

    def on_phone_type(self, event):
        prefix = self.phone_var.get()
        results = customer_backend.search_customer_by_phone(prefix)
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones
        # Don't force dropdown open here!


    def on_phone_select(self, event):
        selected_phone = self.phone_var.get()
        results = customer_backend.search_customer_by_phone(selected_phone)
        if results:
            name, place = results[0][1], results[0][2]
            self.name_var.set(name)
            self.place_var.set(place)

    def on_name_focus(self, event):
        # Show first 5 names on focus
        results = customer_backend.search_customer_by_name('')
        names = [r[0] for r in results]
        self.name_combo['values'] = names
        # Optionally open dropdown
        # self.name_combo.event_generate('<Down>')

    def on_phone_focus(self, event):
       # Just update the list, don't force dropdown
        results = customer_backend.search_customer_by_phone('')
        phones = [r[0] for r in results]
        self.phone_combo['values'] = phones


    def build_table_area(self):
        table_frame = tk.Frame(self)
        table_frame.pack(fill='both', expand=True, padx=20)
        self.table_frame = table_frame

        # Canvas + Scrollbar for table
        self.canvas = tk.Canvas(table_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Table header
        header_labels = ["S.No", "Product Name", "Qty", "Price", "Amount", "Description", "Delete"]

        for idx, text in enumerate(header_labels):
            lbl = tk.Label(
                self.scrollable_frame,
                text=text,
                font=("Arial", 11, "bold"),
                anchor="center",  # Center vertically
                justify="center"  # Center horizontally
            )
  
            lbl.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")

        # After the for loop that creates header labels
        for i in range(7):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)



        # Add Row button
        add_row_btn = tk.Button(self, text="Add Row", command=self.add_table_row)
        add_row_btn.pack(pady=10)
        self.add_row_btn = add_row_btn

        # DO NOT call self.add_table_row() here!

    def build_footer_fields(self):
        footer_frame = tk.Frame(self)
        footer_frame.pack(pady=10, fill='x')
        self.footer_frame = footer_frame

        self.total_amount_var = tk.StringVar(value="0.00")
        self.amount_to_pay_var = tk.StringVar()

        tk.Label(footer_frame, text="Total Amount:").grid(row=0, column=0, padx=10, sticky='e')
        tk.Label(footer_frame, textvariable=self.total_amount_var, font=("Arial", 11, "bold")).grid(row=0, column=1, padx=10, sticky='w')
        tk.Label(footer_frame, text="Amount to Pay:").grid(row=0, column=2, padx=10, sticky='e')
        tk.Entry(footer_frame, textvariable=self.amount_to_pay_var, width=15).grid(row=0, column=3, padx=10, sticky='w')
        tk.Button(footer_frame, text="Submit", command=self.submit_form).grid(row=0, column=4, padx=20)

    def show_notification(self, message, title="Notification", on_close=None, show_print_checkbox=False):
        colors = self.get_colors()
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.configure(bg=colors["bg"])
        popup.transient(self)
        popup.grab_set()
        popup.resizable(False, False)

        # Message label
        label = tk.Label(
            popup,
            text=message,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("Arial", 12),
            wraplength=380,
            justify="left"
        )
        label.pack(padx=20, pady=(20, 10), fill="both", expand=True)

        # Add checkbox if requested
        print_var = tk.BooleanVar(value=False)
        if show_print_checkbox:
            checkbox = tk.Checkbutton(
                popup,
                text="To print the bill, click the checkbox",
                variable=print_var,
                bg=colors["bg"],
                fg=colors["fg"],
                selectcolor=colors["entry_bg"],
                font=("Arial", 11)
            )
            checkbox.pack(pady=(0, 10))

        # OK button
        def close_popup():
            popup.destroy()
            if on_close:
                on_close()
            # After closing, check if print_var is True and call bill generation
            if show_print_checkbox and print_var.get():
                self.generate_bill()  # You must define this method!

        btn = tk.Button(
            popup,
            text="OK",
            command=close_popup,
            bg=colors["button_bg"],
            fg=colors["fg"],
            activebackground=colors["button_bg"]
        )
        btn.pack(pady=(0, 20))

        # Center popup
        popup.update_idletasks()
        width = popup.winfo_reqwidth()
        height = popup.winfo_reqheight()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        popup.wait_window()

    def reset_form(self):
        self.name_var.set("")
        self.place_var.set("")
        self.phone_var.set("")
        self.amount_to_pay_var.set("")
        # Remove all rows except the first
        while len(self.rows) > 1:
            self.delete_row(self.rows[-1])
        # Clear the first row
        row = self.rows[0]
        row['product_var'].set("")
        row['qty_var'].set("")
        row['price_var'].set("")
        row['amount_var'].set("0.00")
        row['description_var'].set("")   # <-- Correct key!
        self.update_total_amount()



    def add_table_row(self):
        row = {}
        row['product_var'] = tk.StringVar()
        row['qty_var'] = tk.StringVar()
        row['price_var'] = tk.StringVar()
        row['amount_var'] = tk.StringVar(value="0.00")
        row['description_var'] = tk.StringVar()
        row['sno_label'] = tk.Label(self.scrollable_frame, text="", anchor="center", justify="center")
        row['product_entry'] = ProductAutocompleteEntry(self.scrollable_frame, row, textvariable=row['product_var'], width=30, justify="center")
        row['qty_entry'] = tk.Entry(self.scrollable_frame, textvariable=row['qty_var'], width=16, justify="center")
        row['price_entry'] = tk.Entry(self.scrollable_frame, textvariable=row['price_var'], width=16, justify="center")
        row['amount_label'] = tk.Label(self.scrollable_frame, textvariable=row['amount_var'], anchor="center", justify="center")
        row['description_entry'] = tk.Entry(self.scrollable_frame, textvariable=row['description_var'], width=50, justify="center")
        row['delete_btn'] = tk.Button(self.scrollable_frame, text="Delete", command=lambda: self.delete_row(row))


        # Bind events for auto-calculation
        row['qty_var'].trace_add("write", lambda *args, r=row: self.update_row_amount(r))
        row['price_var'].trace_add("write", lambda *args, r=row: self.update_row_amount(r))

        self.rows.append(row)
        self.regrid_rows()
        self.update_theme()
        self.update_total_amount()

    def delete_row(self, row):
        for widget in ['sno_label', 'product_entry', 'qty_entry', 'price_entry', 'amount_label', 'description_entry', 'delete_btn']:
            row[widget].destroy()
        self.rows.remove(row)
        self.regrid_rows()
        self.update_total_amount()

    def regrid_rows(self):
        for idx, row in enumerate(self.rows, start=1):
            widgets = [
            row['sno_label'],
            row['product_entry'],
            row['qty_entry'],
            row['price_entry'],
            row['amount_label'],
            row['description_entry'],
            row['delete_btn']
        ]
        for col, widget in enumerate(widgets):
            widget.grid_forget()
            widget.grid(row=idx, column=col, padx=5, pady=2, sticky="nsew")
        row['sno_label'].config(text=str(idx))

    def update_row_amount(self, row):
        try:
            qty = float(row['qty_var'].get())
            price = float(row['price_var'].get())
            amount = qty * price
            row['amount_var'].set(f"{amount:.2f}")
        except ValueError:
            row['amount_var'].set("0.00")
        self.update_total_amount()

    def update_total_amount(self):
        total = 0.0
        for row in self.rows:
            try:
                total += float(row['amount_var'].get())
            except ValueError:
                pass
        self.total_amount_var.set(f"{total:.2f}")

    def submit_form(self):
        name = self.name_var.get().strip()
        place = self.place_var.get().strip()
        phone = self.phone_var.get().strip()
        total_amount_str = self.total_amount_var.get().strip()
        amount_to_pay_str = self.amount_to_pay_var.get().strip()

        # Validate required fields
        if not name or not place or not phone or not total_amount_str:
            self.show_notification("Please fill all required fields.", title="Missing Data")
            return

        # Validate phone number format
        if not (phone.isdigit() and len(phone) == 10):
            self.show_notification("Phone number must be exactly 10 digits.", title="Invalid Phone Number")
            return

        # Validate amounts
        try:
            total_amount = float(total_amount_str)
            amount_to_pay = float(amount_to_pay_str) if amount_to_pay_str else 0.0
            if amount_to_pay < 0 or amount_to_pay > total_amount:
                self.show_notification("Amount to pay must be between 0 and total amount.", title="Invalid Amount")
                return
        except ValueError:
            self.show_notification("Amounts must be valid numbers.", title="Invalid Amount")
            return

        # Check purchaser logic
        # 1. If name and phone combo exists, allow (reuse purchaser_id)
        # 2. If phone exists with different name, error
        # 3. Else, add new purchaser

        customer_id = None
        if customer_backend.check_customer_name_phone_match(name, phone):
            # Get existing purchaser_id for this name-phone combo
            with customer_backend.get_db_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT customer_id FROM customer WHERE customer_name=? AND phone_number=?", (name, phone))
                row = c.fetchone()
                if row:
                    customer_id = row[0]
        elif customer_backend.phone_exists(phone):
            self.show_notification("This phone number is already registered with a different name.", title="Error")
            return
        else:
            # New name and phone, add new purchaser
            customer_id = customer_backend.add_customer(name, place, phone, total_amount, amount_to_pay)
            if not customer_id:
                self.show_notification("Failed to add Customer. Please try again.", title="Error")
                return

        # Add products
        for row in self.rows:
            item = row['product_var'].get().strip()
            qty_str = row['qty_var'].get().strip()
            price_str = row['price_var'].get().strip()
            amount_str = row['amount_var'].get().strip()
            description = row['description_var'].get().strip() or ""

            if not item or not qty_str or not price_str:
                self.show_notification("Product name, Quantity, and Price are required for every row.", title="Missing Product Data")
                return
            
            try:
                qty = float(qty_str)
                price = float(price_str)
                amount = float(amount_str) if amount_str else 0.0
            except ValueError:
                self.show_notification("Please enter valid numbers for quantity, price, and amount.", title="Invalid Product Data")
                return
                
            customer_backend.add_customer_product(
            customer_id,
            item,
            qty,
            price,
            description,
            amount,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")   # <-- Add this!
        )


        # Add payment record if any amount is paid
        if amount_to_pay > 0:
            payment_id = f"CREDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            customer_backend.add_customer_payment(
                customer_id,
                payment_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                amount_to_pay
            )
        
        bill_company = self.load_company_info()
        bill_no = self.get_next_bill_number()
        bill_customer = {
            "name": self.name_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "place": self.place_var.get().strip()
        }
        bill_items = []
        bill_total_qty = 0
        bill_total_amount = 0
        for row in self.rows:
            pname = row['product_var'].get().strip()
            qty_str = row['qty_var'].get().strip()
            amount_str = row['amount_var'].get().strip()
            if pname and qty_str and amount_str:
                try:
                    qty_val = float(qty_str)
                    amount_val = float(amount_str)
                except ValueError:
                    continue
                bill_items.append({"name": pname, "qty": qty_val, "amount": amount_val})
                bill_total_qty += qty_val
                bill_total_amount += amount_val

        # Store all bill data in a dict (optional, for convenience)
        self._bill_data = {
            "company": bill_company,
            "bill_no": bill_no,
            "customer": bill_customer,
            "items": bill_items,
            "total_qty": bill_total_qty,
            "total_amount": bill_total_amount
        }


        # Show confirmation
        balance = total_amount - amount_to_pay
        confirm_msg = (
            f"{amount_to_pay} is paid on {total_amount} for {name}, {place}.\n"
            f"Balance amount to pay: {balance:.2f}"
        )
        
        self.show_notification(
        confirm_msg,
        title="Payment Confirmation",
        on_close=self.reset_form,
        show_print_checkbox=True
    )



    def configure_theme(self):
        colors = self.get_colors()
        self.configure(bg=colors["bg"])
        self.header_frame.configure(bg=colors["bg"])
        self.table_frame.configure(bg=colors["bg"])
        self.footer_frame.configure(bg=colors["bg"])
        self.canvas.configure(bg=colors["bg"])
        self.scrollable_frame.configure(bg=colors["bg"])
        self.title_label.configure(bg=colors["bg"], fg=colors["fg"])

        # Header fields
        for widget in self.header_frame.winfo_children():
        # Skip ttk.Combobox for bg/fg
            if isinstance(widget, ttk.Combobox):
                continue
            if isinstance(widget, tk.Label):
                widget.configure(bg=colors["bg"], fg=colors["fg"])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"])
        # Table header and rows
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=colors["bg"], fg=colors["fg"])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])

        # Add Row button
        self.add_row_btn.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])

        # Footer
        for widget in self.footer_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=colors["bg"], fg=colors["fg"])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=colors["entry_bg"], fg=colors["fg"], insertbackground=colors["fg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["button_bg"])

    def update_theme(self):
        self.configure_theme()

class AutocompleteEntry(tk.Entry):
    def __init__(self, autocomplete_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autocomplete_list = autocomplete_list
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace("w", self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Down>", self.move_down)
        self.lb_up = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.lb_up:
                self.lb.destroy()
                self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = tk.Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y()+self.winfo_height())
                    self.lb_up = True
                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END,w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)

    def move_down(self, event):
        if self.lb_up:
            self.lb.focus()
            self.lb.selection_set(0)

    def comparison(self):
        pattern = self.var.get()
        return [w for w in self.autocomplete_list if w.startswith(pattern)]
import tkinter as tk

class ProductAutocompleteEntry(tk.Entry):
    def __init__(self, parent, row, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.row = row  # Reference to the row dict
        self.listbox = None
        self.bind('<KeyRelease>', self.check_autocomplete)

    def check_autocomplete(self, event):
        typed = self.get()
        if not typed:
            self.hide_listbox()
            return

        # First, search in customer db
        matches = customer_backend.search_products_by_prefix(typed)  # [(name, price, desc), ...]
        if matches:
            self.match_source = 'customer'
            self.current_matches = matches
            self.show_listbox([m[0] for m in matches])
            return

        # If not found, search in purchaser db
        matches = db_backend.search_products_by_prefix(typed)  # [(name, desc), ...]
        if matches:
            self.match_source = 'purchaser'
            self.current_matches = matches
            self.show_listbox([m[0] for m in matches])
            return

        self.hide_listbox()

    def show_listbox(self, names):
        if not self.listbox:
            root = self.winfo_toplevel()
            self.listbox = tk.Listbox(root, width=20)
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            self.listbox.place(x=x, y=y)
            self.listbox.bind("<ButtonRelease-1>", lambda e: self.select_from_listbox())
            self.listbox.bind("<Return>", lambda e: self.select_from_listbox())
        self.listbox.delete(0, tk.END)
        for name in names:
            self.listbox.insert(tk.END, name)


    def select_from_listbox(self, matches):
        if not self.listbox:
            return
        idx = self.listbox.curselection()
        if not idx:
            return
        selected = matches[idx[0]]

        if getattr(self, 'match_source', None) == 'customer':
            # selected: (name, price, desc)
            self.delete(0, tk.END)
            self.insert(0, selected[0])
            self.row['price_var'].set(str(selected[1]))
            self.row['description_var'].set(selected[2])
        elif getattr(self, 'match_source', None) == 'purchaser':
            # selected: (name, desc)
            self.delete(0, tk.END)
            self.insert(0, selected[0])
            self.row['price_var'].set("")  # No price from purchaser db
            self.row['description_var'].set(selected[1])
        self.hide_listbox()


    def hide_listbox(self):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None

    def select_from_listbox(self):
        if not self.listbox:
            return
        idx = self.listbox.curselection()
        if not idx:
            return
        selected = self.current_matches[idx[0]]

        if getattr(self, 'match_source', None) == 'customer':
            # selected: (name, price, desc)
            self.delete(0, tk.END)
            self.insert(0, selected[0])
            self.row['price_var'].set(str(selected[1]))
            self.row['description_var'].set(selected[2])
        elif getattr(self, 'match_source', None) == 'purchaser':
            # selected: (name, desc)
            self.delete(0, tk.END)
            self.insert(0, selected[0])
            self.row['price_var'].set(selected[1])# No price from purchaser db
            self.row['description_var'].set(selected[2])
        self.hide_listbox()



# Standalone test
if __name__ == "__main__":
    def get_colors():
        return themes.THEMES[themes.load_theme()]
    root = tk.Tk()
    root.geometry("900x600")
    frame = OutwardAddFrame(root, get_colors)
    frame.pack(fill="both", expand=True)
    root.mainloop()
