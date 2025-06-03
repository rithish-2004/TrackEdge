import sqlite3
import os
from datetime import datetime

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "purchase.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    with get_db_connection() as conn:
        c = conn.cursor()

        c.execute("""
CREATE TABLE IF NOT EXISTS purchaser (
    purchaser_id TEXT PRIMARY KEY,
    purchaser_name TEXT NOT NULL,
    place TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,  -- <--- ADD UNIQUE HERE
    total_amount REAL NOT NULL,
    date TEXT NOT NULL,
    amount_paid REAL NOT NULL,
    remaining_amount REAL NOT NULL,
    status TEXT NOT NULL
)""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS purchase_product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchaser_id TEXT NOT NULL,
            item TEXT NOT NULL,
            qty REAL NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,  -- <-- Add this line
            FOREIGN KEY (purchaser_id) REFERENCES purchaser(purchaser_id) ON DELETE CASCADE
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS purchase_payment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchaser_id TEXT NOT NULL,
    payment_id TEXT NOT NULL,
    date TEXT NOT NULL,
    amount_paid REAL NOT NULL,
    transaction_type TEXT NOT NULL DEFAULT 'debit',
    remarks TEXT,
    FOREIGN KEY (purchaser_id) REFERENCES purchaser(purchaser_id) ON DELETE CASCADE
)""")

create_tables()
def get_next_purchaser_id():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT purchaser_id FROM purchaser ORDER BY purchaser_id DESC LIMIT 1")
            row = c.fetchone()
            return f"PU{int(row[0][2:])+1:05d}" if row else "PU00001"
    except sqlite3.Error as e:
        print(f"ID generation error: {e}")
        return "PU00001"  # Fallback

def add_purchaser(name, place, phone, total_amount, amount_paid):
    if check_purchaser_name_phone_match(name, phone):
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT purchaser_id FROM purchaser WHERE purchaser_name=? AND phone_number=?", (name, phone))
            row = c.fetchone()
            return row[0] if row else None

    if phone_exists(phone):
        print("This phone number is already registered with another name.")
        return None


    try:
        purchaser_id = get_next_purchaser_id()
        date_now = datetime.now().strftime("%Y-%m-%d")
        remaining = total_amount - amount_paid
        status = "completed" if remaining == 0 else "pending"
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO purchaser VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (purchaser_id, name, place, phone, total_amount, 
                 date_now, amount_paid, remaining, status))
        return purchaser_id
    except sqlite3.Error as e:
        print(f"Add purchaser error: {e}")
        return None


def add_purchase_product(purchaser_id, item, qty, price, description, amount, date_now):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO purchase_product 
                (purchaser_id, item, qty, price, description, amount, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)      -- <-- Add one more ? here
            """, (purchaser_id, item, qty, price, description, amount, date_now))  # <-- Add date_now here

            c.execute("""
                SELECT SUM(amount) FROM purchase_product WHERE purchaser_id=?
            """, (purchaser_id,))
            total_amount = c.fetchone()[0] or 0
            c.execute("""
                SELECT amount_paid FROM purchaser WHERE purchaser_id=?
            """, (purchaser_id,))
            amount_paid = c.fetchone()[0] or 0

            remaining = total_amount - amount_paid
            status = "completed" if remaining <= 0.001 else "pending"
            c.execute("""
                UPDATE purchaser SET total_amount=?, remaining_amount=?, status=?
                WHERE purchaser_id=?
            """, (total_amount, remaining, status, purchaser_id))

        return True
    except sqlite3.Error as e:
        print(f"Add purchase product error: {e}")
        return False

def add_purchase_payment(purchaser_id, payment_id, date, amount_paid, transaction_type='debit', remarks=None):
    """
    Adds a payment to the purchase_payment table and updates the amount_paid and remaining_amount in purchaser table.
    transaction_type: 'debit' (default) or 'credit'
    Returns True on success, False on failure.
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            c.execute("""
                INSERT INTO purchase_payment 
                (purchaser_id, payment_id, date, amount_paid, transaction_type, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (purchaser_id, payment_id, date, amount_paid, transaction_type, remarks))

            c.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN transaction_type='debit' THEN amount_paid ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN transaction_type='credit' THEN amount_paid ELSE 0 END), 0)
                FROM purchase_payment WHERE purchaser_id=?
            """, (purchaser_id,))
            total_paid = c.fetchone()[0] or 0


            c.execute("""
                SELECT total_amount FROM purchaser WHERE purchaser_id=?
            """, (purchaser_id,))
            total_amount = c.fetchone()[0] or 0

            remaining = total_amount - total_paid
            status = "completed" if remaining <= 0.001 else "pending"

            c.execute("""
                UPDATE purchaser SET amount_paid=?, remaining_amount=?, status=?
                WHERE purchaser_id=?
            """, (total_paid, remaining, status, purchaser_id))

        return True
    except sqlite3.Error as e:
        print(f"Add purchase payment error: {e}")
        return False



def search_purchasers_by_name(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        if prefix:
            c.execute("""
                SELECT purchaser_name, place, phone_number FROM purchaser
                WHERE purchaser_name LIKE ?
                ORDER BY purchaser_name ASC
                LIMIT 5
            """, ('%' + prefix + '%',))
        else:
            c.execute("""
                SELECT purchaser_name, place, phone_number FROM purchaser
                ORDER BY purchaser_name ASC
                LIMIT 5
            """)
        return c.fetchall()


def search_purchasers_by_phone(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        if prefix:
            c.execute("""
                SELECT phone_number, purchaser_name, place FROM purchaser
                WHERE phone_number LIKE ?
                ORDER BY phone_number ASC
                LIMIT 5
            """, (prefix + '%',))
        else:
            c.execute("""
                SELECT phone_number, purchaser_name, place FROM purchaser
                ORDER BY phone_number ASC
                LIMIT 5
            """)
        return c.fetchall()

def check_purchaser_name_phone_match(name, phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT purchaser_name FROM purchaser
            WHERE purchaser_name=? AND phone_number=?
        """, (name, phone))
        return c.fetchone() is not None
def phone_exists(phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM purchaser WHERE phone_number = ?", (phone,))
        return c.fetchone() is not None

def get_all_phone_numbers():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT phone_number FROM purchaser")
        return [row[0] for row in c.fetchall()]
    
def search_products_by_prefix(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT item, price, description
            FROM purchase_product
            WHERE item LIKE ?
            GROUP BY item
            ORDER BY item ASC
            LIMIT 10
        """, (prefix + '%',))
        return c.fetchall()

def search_purchasers_by_name_words(words):
    """
    Returns a list of (purchaser_name,) matching any word in the name (case-insensitive).
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        if not words:
            return []
        query = "SELECT DISTINCT purchaser_name FROM purchaser WHERE " + " OR ".join(["purchaser_name LIKE ?"] * len(words))
        params = [f"%{word}%" for word in words]
        c.execute(query, params)
        return c.fetchall()

def get_purchaser_by_name(name):
    """
    Returns (purchaser_name, phone_number, place) for the given name.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT purchaser_name, phone_number, place FROM purchaser WHERE purchaser_name = ?", (name,))
        return c.fetchone()

def get_purchaser_by_phone(phone):
    """
    Returns (purchaser_name, phone_number, place) for the given phone number.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT purchaser_name, phone_number, place FROM purchaser WHERE phone_number = ?", (phone,))
        return c.fetchone()
def get_purchases_by_name_phone(name, phone):
    """
    Returns a list of (purchaser_id, total_amount, amount_paid, remaining_amount, status, date)
    for the given purchaser, with pending first, then completed, ordered by date descending.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT purchaser_id, total_amount, amount_paid, remaining_amount, status, date
            FROM purchaser
            WHERE purchaser_name=? AND phone_number=?
            ORDER BY 
                CASE WHEN status='pending' THEN 0 ELSE 1 END,
                date DESC
        """, (name, phone))

        return c.fetchall()
def get_products_by_purchaser_id(purchaser_id):
    """
    Returns a list of (item, qty, price, description, amount) for the given purchaser_id.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT item, qty, price, description, amount
            FROM purchase_product
            WHERE purchaser_id=?
        """, (purchaser_id,))
        return c.fetchall()
def get_payments_by_purchaser_id(purchaser_id):
    """
    Returns a list of (date, payment_id, purchaser_id, amount_paid) for the given purchaser_id, ordered by date.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT date, payment_id, purchaser_id, amount_paid
            FROM purchase_payment
            WHERE purchaser_id=?
            ORDER BY date ASC
        """, (purchaser_id,))
        return c.fetchall()

def get_all_activity_dates(name, phone):
    """
    Returns a set of all unique dates where either a product was purchased
    or a payment was made for the given customer.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT DATE(pp.date)
FROM purchase_product pp
JOIN purchaser u ON pp.purchaser_id = u.purchaser_id
WHERE u.purchaser_name=? AND u.phone_number=?

        """, (name, phone))
        product_dates = set(row[0] for row in c.fetchall())
        c.execute("""
           SELECT DISTINCT DATE(p.date)
FROM purchase_payment p
JOIN purchaser u ON p.purchaser_id = u.purchaser_id
WHERE u.purchaser_name=? AND u.phone_number=?

        """, (name, phone))
        payment_dates = set(row[0] for row in c.fetchall())
        return product_dates.union(payment_dates)

def get_payment_dates_by_name_phone(name, phone):
    """
    Returns a set of unique dates where payments exist for this customer.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT DATE(p.date)
FROM purchase_payment p
JOIN purchaser u ON p.purchaser_id = u.purchaser_id
WHERE u.purchaser_name=? AND u.phone_number=?

        """, (name, phone))
        return set(row[0] for row in c.fetchall())
    
def get_payments_by_name_phone_and_date(name, phone, date):
    """
    Returns all payments for this customer on a specific date.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT p.date, p.payment_id, p.purchaser_id, p.amount_paid
            FROM purchase_payment p
            JOIN purchaser u ON p.purchaser_id = u.purchaser_id
            WHERE u.purchaser_name=? AND u.phone_number=? AND DATE(p.date)=?

            ORDER BY p.date ASC
        """, (name, phone, date))

        return c.fetchall()

def get_products_by_name_phone_and_date(name, phone, start_date=None, end_date=None):
    """
    Returns all products purchased by this customer between start_date and end_date (inclusive).
    If no dates are provided, returns all products for this customer.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        base_query = """
            SELECT pp.item, pp.qty, pp.price, pp.description, pp.amount, pp.date
            FROM purchase_product pp
            JOIN purchaser u ON pp.purchaser_id = u.purchaser_id
            WHERE u.purchaser_name=? AND u.phone_number=?
        """
        params = [name, phone]
        if start_date and end_date:
            base_query += " AND DATE(pp.date) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif start_date:
            base_query += " AND DATE(pp.date) >= ?"
            params.append(start_date)
        elif end_date:
            base_query += " AND DATE(pp.date) <= ?"
            params.append(end_date)
        base_query += " ORDER BY pp.date ASC"
        c.execute(base_query, params)
        return c.fetchall()

def generate_payment_id():
    """Generate a payment ID like PAY20250514185648 (using current timestamp)."""
    return "PAY" + datetime.now().strftime("%Y%m%d%H%M%S")

def add_purchase_payment_to_record(purchaser_id, amount_paid):
    """
    Adds a payment to the purchase_payment table and updates the purchaser's amount_paid, remaining_amount, and status.
    Returns (True, new_remaining, new_status) on success, (False, None, None) on failure.
    """
    from datetime import datetime
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Get current paid and remaining amounts
            c.execute("SELECT total_amount, amount_paid, remaining_amount FROM purchaser WHERE purchaser_id=?", (purchaser_id,))
            row = c.fetchone()
            if not row:
                return False, None, None
            total_amount, current_paid, current_remaining = row
            if amount_paid <= 0 or amount_paid > current_remaining:
                return False, None, None

            # Insert payment
            payment_id = f"PAY{int(datetime.now().timestamp())}"
            c.execute("""
                INSERT INTO purchase_payment (purchaser_id, payment_id, date, amount_paid)
                VALUES (?, ?, ?, ?)
            """, (purchaser_id, payment_id, date_now, amount_paid))

            # Update purchaser table
            new_paid = current_paid + amount_paid
            new_remaining = total_amount - new_paid
            new_status = "completed" if abs(new_remaining) < 0.001 else "pending"
            c.execute("""
                UPDATE purchaser SET amount_paid=?, remaining_amount=?, status=?
                WHERE purchaser_id=?
            """, (new_paid, new_remaining, new_status, purchaser_id))

        return True, new_remaining, new_status
    except Exception as e:
        print("Payment error:", e)
        return False, None, None
    
def get_purchaser_id(name, phone, place):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT purchaser_id FROM purchaser WHERE purchaser_name=? AND phone_number=? AND place=?", (name, phone, place))
        row = c.fetchone()
        return row[0] if row else None


def get_purchases_by_date_range(from_date=None, to_date=None):
    """
    Returns a list of (purchaser_name, item, qty, price, amount, date)
    for purchases in the given date range (inclusive), or all if no dates.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        if from_date and to_date:
            c.execute("""
                SELECT u.purchaser_name, p.item, p.qty, p.price, p.amount, p.date
                FROM purchase_product p
                JOIN purchaser u ON p.purchaser_id = u.purchaser_id
                WHERE DATE(p.date) BETWEEN ? AND ?
                ORDER BY p.date DESC
            """, (from_date, to_date))
        else:
            c.execute("""
                SELECT u.purchaser_name, p.item, p.qty, p.price, p.amount, p.date
                FROM purchase_product p
                JOIN purchaser u ON p.purchaser_id = u.purchaser_id
                ORDER BY p.date DESC
            """)
        return c.fetchall()



    
def get_recent_purchase_payments(order='recent', limit=5):
    """
    Returns a list of (purchaser_name, payment_id, amount_paid, date)
    ordered by date (recent or oldest first), limited by 'limit'.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT u.purchaser_name, p.payment_id, p.amount_paid, p.date
            FROM purchase_payment p
            JOIN purchaser u ON p.purchaser_id = u.purchaser_id
            ORDER BY datetime(p.date) {"DESC" if order == "recent" else "ASC"}
            LIMIT ?
        """, (limit,))
        return c.fetchall()

def update_purchaser_phone_place(old_name, old_place, new_phone, new_place):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM purchaser WHERE purchaser_name=? AND place=?", (old_name, old_place))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    c.execute("SELECT * FROM purchaser WHERE phone_number=? AND NOT (purchaser_name=? AND place=?)", (new_phone, old_name, old_place))
    if c.fetchone():
        conn.close()
        return False
    c.execute("UPDATE purchaser SET phone_number=?, place=? WHERE purchaser_name=? AND place=?", (new_phone, new_place, old_name, old_place))
    conn.commit()
    conn.close()
    return True

def get_all_products_by_name_phone(name, phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT pp.item, pp.qty, pp.price, pp.description, pp.amount, pp.date
            FROM purchase_product pp
            JOIN purchaser u ON pp.purchaser_id = u.purchaser_id
            WHERE u.purchaser_name=? AND u.phone_number=?
            ORDER BY pp.date ASC
        """, (name, phone))
        return c.fetchall()

def update_product_by_id(prod_id, new_item, new_desc):
    """
    Updates the item name and description for a specific product row by id.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE purchase_product
            SET item = ?, description = ?
            WHERE id = ?
        """, (new_item, new_desc, prod_id))
        conn.commit()
        return c.rowcount > 0  

def get_product_id_by_details(purchaser_name, phone, item, qty, price, description, amount, date):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT pp.id
            FROM purchase_product pp
            JOIN purchaser u ON pp.purchaser_id = u.purchaser_id
            WHERE u.purchaser_name=? AND u.phone_number=?
              AND pp.item=? AND pp.qty=? AND pp.price=? AND pp.description=? AND pp.amount=? AND pp.date=?
            LIMIT 1
        """, (purchaser_name, phone, item, qty, price, description, amount, date))
        row = c.fetchone()
        return row[0] if row else None

    
def update_product_quantity_and_amount_by_id(product_id, new_qty, new_amount):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE purchase_product
            SET qty=?, amount=?
            WHERE id=?
        """, (new_qty, new_amount, product_id))
        conn.commit()

def update_purchaser_amounts(purchaser_id, new_total, new_remaining):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE purchaser
            SET total_amount=?, remaining_amount=?
            WHERE purchaser_id=?
        """, (new_total, new_remaining, purchaser_id))
        conn.commit()

def update_purchaser_status(purchaser_id, status):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE purchaser SET status=? WHERE purchaser_id=?", (status, purchaser_id))
        conn.commit()

def get_amount_paid_by_purchaser_id(purchaser_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT amount_paid FROM purchaser WHERE purchaser_id=?", (purchaser_id,))
        row = c.fetchone()
        return row[0] if row else 0

def delete_product_by_id(product_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM purchase_product WHERE id=?", (product_id,))
        conn.commit()


def get_transactions_by_name_phone_and_date(name, phone, start, end):
    """
    Returns all payments for this customer, optionally filtered by date range.
    If start and end are empty, returns all payments.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT purchaser_id FROM purchaser WHERE purchaser_name=? AND phone_number=?", (name, phone))
        row = c.fetchone()
        if not row:
            return []
        purchaser_id = row[0]
        if start and end:
            c.execute("""
                SELECT p.date, p.payment_id, p.purchaser_id, p.amount_paid
                FROM purchase_payment p
                WHERE p.purchaser_id=? AND DATE(p.date) BETWEEN ? AND ?
                ORDER BY p.date DESC
            """, (purchaser_id, start, end))
        else:
            c.execute("""
                SELECT p.date, p.payment_id, p.purchaser_id, p.amount_paid
                FROM purchase_payment p
                WHERE p.purchaser_id=?
                ORDER BY p.date DESC
            """, (purchaser_id,))
        return c.fetchall()
def get_refund_purchaser_by_name_phone(name, phone):
    """
    Returns (purchaser_id,) for the given purchaser_name and phone_number, or None if not found.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT purchaser_id FROM purchaser WHERE purchaser_name=? AND phone_number=?", (name, phone))
        return c.fetchone()
    
def get_purchases_by_name_phone_and_date(name, phone, from_date=None, to_date=None):
    with get_db_connection() as conn:
        c = conn.cursor()
        query = """
            SELECT p.item, p.qty, p.price, p.amount, p.date
            FROM purchase_product p
            JOIN purchaser u ON p.purchaser_id = u.purchaser_id
            WHERE u.purchaser_name = ? AND u.phone_number = ?
        """
        params = [name, phone]
        if from_date and to_date:
            query += " AND DATE(p.date) BETWEEN ? AND ?"
            params.extend([from_date, to_date])
        query += " ORDER BY p.date DESC"
        c.execute(query, params)
        return c.fetchall()


if __name__ == "__main__":
    print("Tables created successfully!")
