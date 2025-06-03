import sqlite3
from datetime import datetime

DB_PATH = "service/service.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS service_customer (
            service_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            place TEXT,
            date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            amount_paid REAL NOT NULL,
            remaining_amount REAL NOT NULL,
            status TEXT NOT NULL
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS service_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (service_id) REFERENCES service_customer(service_id) ON DELETE CASCADE
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS service_payment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT NOT NULL,
            payment_id TEXT NOT NULL,
            date TEXT NOT NULL,
            amount_paid REAL NOT NULL,
            transaction_type TEXT NOT NULL DEFAULT 'credit',
            remarks TEXT,
            FOREIGN KEY (service_id) REFERENCES service_customer(service_id) ON DELETE CASCADE
        )
        """)
        conn.commit()

# --- CUSTOMER ADD/UPDATE LOGIC WITH CONFLICT CHECKS ---

def check_name_phone_conflict(name, phone):
    """
    Returns:
        - "ok" if no conflict (safe to add)
        - "phone_conflict" if phone exists for another name
        - "name_conflict" if name exists for another phone
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        # Check if phone exists with different name
        c.execute("SELECT customer_name FROM service_customer WHERE phone_number=? ORDER BY date DESC LIMIT 1", (phone,))
        row = c.fetchone()
        if row and row[0] != name:
            return "phone_conflict"
        # Check if name exists with different phone
        c.execute("SELECT phone_number FROM service_customer WHERE customer_name=? ORDER BY date DESC LIMIT 1", (name,))
        row = c.fetchone()
        if row and row[0] != phone:
            return "name_conflict"
        return "ok"

def add_service_customer(customer_name, place, phone_number, total_amount, amount_paid, status):
    """
    Add new customer. Assumes check_name_phone_conflict() has passed.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        service_id = f"SVC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        remaining_amount = total_amount - amount_paid
        c.execute("""
            INSERT INTO service_customer (service_id, customer_name, phone_number, place, date, total_amount, amount_paid, remaining_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (service_id, customer_name, phone_number, place, date, total_amount, amount_paid, remaining_amount, status))
        conn.commit()
        return service_id


def add_service_item(service_id, item_name, description, amount, date=None):
    if not date:
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO service_item (service_id, item_name, description, amount, date)
            VALUES (?, ?, ?, ?, ?)
        """, (service_id, item_name, description, amount, date))
        conn.commit()

# --- SERVICE PAYMENT ---

def add_service_payment(service_id, amount_paid, remarks=None):
    with get_db_connection() as conn:
        c = conn.cursor()
        payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        c.execute("""
            INSERT INTO service_payment (service_id, payment_id, date, amount_paid, remarks)
            VALUES (?, ?, ?, ?, ?)
        """, (service_id, payment_id, date, amount_paid, remarks))
        conn.commit()

def add_service_payment_to_record(service_id, amount):
    """
    Add a payment to the service_payment table, update service_customer's paid/remaining/status.
    Returns: (success, new_paid, new_remaining, new_status)
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            c.execute("""
                INSERT INTO service_payment (service_id, payment_id, date, amount_paid)
                VALUES (?, ?, ?, ?)
            """, (service_id, payment_id, date, amount))
            c.execute("""
                UPDATE service_customer
                SET amount_paid = amount_paid + ?,
                    remaining_amount = remaining_amount - ?
                WHERE service_id=?
            """, (amount, amount, service_id))
            c.execute("""
                SELECT amount_paid, remaining_amount FROM service_customer WHERE service_id=?
            """, (service_id,))
            paid, remaining = c.fetchone()
            if abs(remaining) < 0.01:
                status = "completed"
                c.execute("""
                    UPDATE service_customer SET status=? WHERE service_id=?
                """, (status, service_id))
                remaining = 0.0
            else:
                status = "pending"
            conn.commit()
            return True, paid, remaining, status
    except Exception as e:
        print("add_service_payment_to_record error:", e)
        return False, 0, 0, "error"

# --- SEARCH AND AUTOCOMPLETE HELPERS ---

def search_customer_by_name(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT customer_name, place, phone_number FROM service_customer
            WHERE customer_name LIKE ?
            GROUP BY customer_name, place, phone_number
        """, (f"{prefix}%",))
        return c.fetchall()

def search_customer_by_phone(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT phone_number, customer_name, place FROM service_customer
            WHERE phone_number LIKE ?
            GROUP BY phone_number, customer_name, place
        """, (f"{prefix}%",))
        return c.fetchall()

def customer_exists_by_name(name):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT place, phone_number FROM service_customer
            WHERE customer_name=?
            ORDER BY date DESC LIMIT 1
        """, (name,))
        return c.fetchone()

def customer_exists_by_phone(phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT customer_name, place FROM service_customer
            WHERE phone_number=?
            ORDER BY date DESC LIMIT 1
        """, (phone,))
        return c.fetchone()

def get_service_customer_by_name_phone(name, phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT service_id, customer_name, phone_number, place, total_amount, amount_paid, remaining_amount
            FROM service_customer
            WHERE customer_name=? AND phone_number=?
            ORDER BY date DESC LIMIT 1
        """, (name, phone))
        return c.fetchone()

def add_or_update_service_customer(customer_name, place, phone_number, total_amount, amount_paid):
    """
    - If phone exists and name matches: update totals (add to total_amount, add to amount_paid, recalc remaining and status)
    - If phone exists with different name: return error
    - If name exists with different phone: return error
    - If new: insert
    Returns: (service_id, result, new_total, new_paid, new_remaining, status)
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        # Check if phone exists
        c.execute("SELECT service_id, customer_name, total_amount, amount_paid FROM service_customer WHERE phone_number=?", (phone_number,))
        row = c.fetchone()
        if row:
            service_id, existing_name, prev_total, prev_paid = row
            if existing_name != customer_name:
                return None, "error_phone_conflict", None, None, None, None
            # Update: add to totals
            new_total = prev_total + total_amount
            new_paid = prev_paid + amount_paid
            new_remaining = new_total - new_paid
            status = "completed" if abs(new_remaining) < 0.01 else "pending"
            c.execute("""
                UPDATE service_customer
                SET customer_name=?, place=?, total_amount=?, amount_paid=?, remaining_amount=?, status=?
                WHERE service_id=?
            """, (customer_name, place, new_total, new_paid, new_remaining, status, service_id))
            conn.commit()
            return service_id, "updated", new_total, new_paid, new_remaining, status
        # Check if name exists with different phone
        c.execute("SELECT phone_number FROM service_customer WHERE customer_name=? ORDER BY date DESC LIMIT 1", (customer_name,))
        row = c.fetchone()
        if row and row[0] != phone_number:
            return None, "error_name_conflict", None, None, None, None
        # Insert new
        service_id = f"SVC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        remaining = total_amount - amount_paid
        status = "completed" if abs(remaining) < 0.01 else "pending"
        c.execute("""
            INSERT INTO service_customer (service_id, customer_name, phone_number, place, date, total_amount, amount_paid, remaining_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (service_id, customer_name, phone_number, place, date, total_amount, amount_paid, remaining, status))
        conn.commit()
        return service_id, "inserted", total_amount, amount_paid, remaining, status
def add_spare_amount_to_service(service_id, amount):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE service_customer
                SET total_amount = total_amount + ?, remaining_amount = remaining_amount + ?
                WHERE service_id = ?
            """, (amount, amount, service_id))
            item_name = "Spare Product"
            description = "Additional service to other repaired Parts"
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute("""
                INSERT INTO service_item (service_id, item_name, description, amount, date)
                VALUES (?, ?, ?, ?, ?)
            """, (service_id, item_name, description, amount, date_str))
            conn.commit()
            return c.rowcount == 1
    except Exception as e:
        print("Error updating spare amount:", e)
        return False
def get_service_id(name, phone, place):
    """
    Returns the service_id for a given customer name, phone, and place.
    If there are multiple, returns the most recent one (by date).
    Returns None if not found.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT service_id
            FROM service_customer
            WHERE customer_name=? AND phone_number=? AND place=?
            ORDER BY date DESC
            LIMIT 1
        """, (name, phone, place))
        row = c.fetchone()
        return row[0] if row else None


def get_all_activities_by_name_phone(name, phone, start_date=None, end_date=None):
    """Return a list of all activities (service items and payments) for the customer, sorted by date/time descending."""
    with get_db_connection() as conn:
        c = conn.cursor()
        # Service items
        c.execute("""
            SELECT si.date, 'service_item', si.item_name, si.description, si.amount, sc.service_id
            FROM service_item si
            JOIN service_customer sc ON sc.service_id = si.service_id
            WHERE sc.customer_name=? AND sc.phone_number=?
        """, (name, phone))
        service_items = [{
            "date": row[0],
            "type": row[1],
            "item_name": row[2],
            "description": row[3],
            "amount": row[4],
            "service_id": row[5]
        } for row in c.fetchall()]

        # Payments
        c.execute("""
            SELECT sp.date, 'payment', NULL, sp.remarks, sp.amount_paid, sp.service_id
            FROM service_payment sp
            JOIN service_customer sc ON sc.service_id = sp.service_id
            WHERE sc.customer_name=? AND sc.phone_number=?
        """, (name, phone))
        payments = [{
            "date": row[0],
            "type": row[1],
            "item_name": None,
            "description": row[3],
            "amount": row[4],
            "service_id": row[5]
        } for row in c.fetchall()]

        # Combine and filter by date if needed
        all_activities = service_items + payments
        if start_date:
            all_activities = [a for a in all_activities if a["date"][:10].replace("-", "/") >= start_date.replace("-", "/")]
        if end_date:
            all_activities = [a for a in all_activities if a["date"][:10].replace("-", "/") <= end_date.replace("-", "/")]
        all_activities.sort(key=lambda x: x["date"], reverse=True)
        return all_activities
def get_customer_by_name(name):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT customer_name, phone_number, place FROM service_customer WHERE customer_name = ? LIMIT 1", (name,))
        return c.fetchone()

def get_customer_by_phone(phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT customer_name, phone_number, place FROM service_customer WHERE phone_number = ? LIMIT 1", (phone,))
        return c.fetchone()

def search_customer_by_name_words(words):
    with get_db_connection() as conn:
        c = conn.cursor()
        query = "SELECT DISTINCT customer_name, phone_number, place FROM service_customer WHERE "
        query += " AND ".join(["customer_name LIKE ?"] * len(words))
        params = [f"%{w}%" for w in words]
        c.execute(query, params)
        return c.fetchall()

def search_customer_by_phone(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT DISTINCT phone_number, customer_name, place FROM service_customer WHERE phone_number LIKE ?", (f"{prefix}%",))
        return c.fetchall()
def get_customer_summary(name, phone):
    """Return total, paid, remaining, status for this customer (across all services)."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT SUM(total_amount), SUM(amount_paid), SUM(remaining_amount)
            FROM service_customer
            WHERE customer_name=? AND phone_number=?
        """, (name, phone))
        row = c.fetchone()
        total = row[0] or 0
        paid = row[1] or 0
        remaining = row[2] or 0
        status = "Completed" if abs(remaining) < 0.01 else "Pending"
        return total, paid, remaining, status

def get_service_history_by_date(name, phone, start_date=None, end_date=None):
    from collections import defaultdict
    with get_db_connection() as conn:
        c = conn.cursor()
        # Get all service items
        c.execute("""
            SELECT si.item_name, si.amount, si.description, si.date
            FROM service_item si
            JOIN service_customer sc ON si.service_id = sc.service_id
            WHERE sc.customer_name=? AND sc.phone_number=?
        """, (name, phone))
        items = c.fetchall()

        # Get all payments
        c.execute("""
            SELECT sp.amount_paid, sp.date
            FROM service_payment sp
            JOIN service_customer sc ON sp.service_id = sc.service_id
            WHERE sc.customer_name=? AND sc.phone_number=?
        """, (name, phone))
        payments = c.fetchall()

    # Group by date (YYYY/MM/DD)
    history = defaultdict(lambda: {"items": [], "payments": []})

    for item_name, amount, desc, dt in items:
        date_part = dt[:10].replace("-", "/")
        time_part = dt[11:] if len(dt) > 10 else ""
        history[date_part]["items"].append({
            "item_name": item_name,
            "amount": amount,
            "description": desc,
            "time": time_part
        })

    for amt, dt in payments:
        date_part = dt[:10].replace("-", "/")
        time_part = dt[11:] if len(dt) > 10 else ""
        history[date_part]["payments"].append({
            "amount": amt,
            "time": time_part
        })

    # Filter by date range if needed
    if start_date:
        history = {d: v for d, v in history.items() if d >= start_date.replace("-", "/")}
    if end_date:
        history = {d: v for d, v in history.items() if d <= end_date.replace("-", "/")}

    return dict(sorted(history.items(), reverse=True))

def get_service_items_general_view(from_date=None, to_date=None):
    """
    Returns list of tuples: (customer_name, item_name, description, amount, date)
    Filters by date range on service_item.date (date part only, ignores time).
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        # Convert YYYY-MM-DD to YYYY/MM/DD for LIKE pattern matching
        if from_date and to_date:
            # Accept both '-' and '/' as separator for robustness
            from_date_str = from_date.replace("-", "/")
            to_date_str = to_date.replace("-", "/")
            c.execute("""
                SELECT sc.customer_name, si.item_name, si.description, si.amount, si.date
                FROM service_item si
                JOIN service_customer sc ON sc.service_id = si.service_id
                WHERE substr(replace(si.date, '-', '/'), 1, 10) BETWEEN ? AND ?
                ORDER BY si.date DESC
            """, (from_date_str, to_date_str))
        else:
            c.execute("""
                SELECT sc.customer_name, si.item_name, si.description, si.amount, si.date
                FROM service_item si
                JOIN service_customer sc ON sc.service_id = si.service_id
                ORDER BY si.date DESC
            """)
        return c.fetchall()

def get_recent_service_payments_general(order='recent', limit=10):
    """
    Returns list of tuples: (customer_name, payment_id, amount_paid, date)
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        order_by = "DESC" if order == "recent" else "ASC"
        c.execute(f"""
            SELECT sc.customer_name, sp.payment_id, sp.amount_paid, sp.date
            FROM service_payment sp
            JOIN service_customer sc ON sp.service_id = sc.service_id
            ORDER BY sp.date {order_by}
            LIMIT ?
        """, (limit,))
        return c.fetchall()

def get_service_item_by_id(item_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, service_id, item_name, description, amount, date 
            FROM service_item 
            WHERE id=?
        """, (item_id,))
        return c.fetchone()

def update_service_item(item_id, item_name, description, amount):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE service_item
            SET item_name=?, description=?, amount=?
            WHERE id=?
        """, (item_name, description, amount, item_id))
        conn.commit()
        return c.rowcount > 0

def delete_service_item(item_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM service_item WHERE id=?", (item_id,))
        conn.commit()
        return c.rowcount > 0

def search_service_customers_by_name(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        if prefix:
            c.execute("""
                SELECT customer_name, place, phone_number FROM service_customer
                WHERE customer_name LIKE ?
                ORDER BY customer_name ASC
                LIMIT 5
            """, ('%' + prefix + '%',))
        else:
            c.execute("""
                SELECT customer_name, place, phone_number FROM service_customer
                ORDER BY customer_name ASC
                LIMIT 5
            """)
        return c.fetchall()

# --- Call this at app start ---
initialize_db()
