import sqlite3
import os
from datetime import datetime

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customer.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    with get_db_connection() as conn:
        c = conn.cursor()

        c.execute("""
CREATE TABLE IF NOT EXISTS customer (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    place TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,  -- <--- ADD UNIQUE HERE
    total_amount REAL NOT NULL,
    date TEXT NOT NULL,
    amount_paid REAL NOT NULL,
    remaining_amount REAL NOT NULL,
    status TEXT NOT NULL
)""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS customer_product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            item TEXT NOT NULL,
            qty REAL NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,  -- <-- Add this line
            FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS customer_payment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    payment_id TEXT NOT NULL,
    date TEXT NOT NULL,
    amount_paid REAL NOT NULL,
    transaction_type TEXT NOT NULL DEFAULT 'debit',
    remarks TEXT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
)""")

create_tables()
def get_next_customer_id():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1")
            row = c.fetchone()
            return f"CU{int(row[0][2:])+1:05d}" if row else "CU00001"
    except sqlite3.Error as e:
        print(f"ID generation error: {e}")
        return "CU00001"  # Fallback

def add_customer(name, place, phone, total_amount, amount_paid):
    # 1. If name and phone combination exists: OK
    if check_customer_name_phone_match(name, phone):
        # Optionally: you may want to just return the purchaser_id here
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT customer_id FROM customer WHERE customer_name=? AND phone_number=?", (name, phone))
            row = c.fetchone()
            return row[0] if row else None

    # 2. If phone exists but with different name: Error
    if phone_exists(phone):
        print("This phone number is already registered with another name.")
        return None

    # 3. If both name and phone are new: Add
    try:
        customer_id = get_next_customer_id()
        date_now = datetime.now().strftime("%Y-%m-%d")
        remaining = total_amount - amount_paid
        status = "completed" if remaining == 0 else "pending"
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO customer VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, name, place, phone, total_amount, 
                 date_now, amount_paid, remaining, status))
        return customer_id
    except sqlite3.Error as e:
        print(f"Add customer error: {e}")
        return None

# Similar error handling for add_purchase_product() and add_purchase_payment()

def add_customer_product(customer_id, item, qty, price, description, amount, date_now):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Insert the new product (add 'date' field)
            c.execute("""
                INSERT INTO customer_product 
                (customer_id, item, qty, price, description, amount, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)      -- <-- Add one more ? here
            """, (customer_id, item, qty, price, description, amount, date_now))  # <-- Add date_now here

            # Recalculate total amount for this purchase
            c.execute("""
                SELECT SUM(amount) FROM customer_product WHERE customer_id=?
            """, (customer_id,))
            total_amount = c.fetchone()[0] or 0

            # Get the amount paid so far
            c.execute("""
                SELECT amount_paid FROM customer WHERE customer_id=?
            """, (customer_id,))
            amount_paid = c.fetchone()[0] or 0

            remaining = total_amount - amount_paid
            status = "completed" if remaining <= 0.001 else "pending"

            # Update purchaser table
            c.execute("""
                UPDATE customer SET total_amount=?, remaining_amount=?, status=?
                WHERE customer_id=?
            """, (total_amount, remaining, status, customer_id))

        return True
    except sqlite3.Error as e:
        print(f"Add Customer product error: {e}")
        return False

def add_customer_payment(customer_id, payment_id, date, amount_paid, transaction_type='credit', remarks=None):
   
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Insert the new payment
            c.execute("""
                INSERT INTO customer_payment 
                (customer_id, payment_id, date, amount_paid, transaction_type, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (customer_id, payment_id, date, amount_paid, transaction_type, remarks))

            # Recalculate total paid for this purchase (debits minus credits)
            c.execute("""
    SELECT 
        COALESCE(SUM(CASE WHEN transaction_type='credit' THEN amount_paid ELSE 0 END), 0) -
        COALESCE(SUM(CASE WHEN transaction_type='debit' THEN amount_paid ELSE 0 END), 0)
    FROM customer_payment WHERE customer_id=?
""", (customer_id,))
            total_paid = c.fetchone()[0] or 0


            # Get the total amount for this purchase
            c.execute("""
                SELECT total_amount FROM customer WHERE customer_id=?
            """, (customer_id,))
            total_amount = c.fetchone()[0] or 0

            remaining = total_amount - total_paid
            status = "completed" if remaining <= 0.001 else "pending"

            # Update purchaser table
            c.execute("""
                UPDATE customer SET amount_paid=?, remaining_amount=?, status=?
                WHERE customer_id=?
            """, (total_paid, remaining, status, customer_id))

        return True
    except sqlite3.Error as e:
        print(f"Add customer payment error: {e}")
        return False



def search_customer_by_name(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        if prefix:
            c.execute("""
                SELECT customer_name, place, phone_number FROM customer
                WHERE customer_name LIKE ?
                ORDER BY customer_name ASC
                LIMIT 5
            """, ('%' + prefix + '%',))
        else:
            c.execute("""
                SELECT customer_name, place, phone_number FROM customer
                ORDER BY customer_name ASC
                LIMIT 5
            """)
        return c.fetchall()


def search_customer_by_phone(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        if prefix:
            c.execute("""
                SELECT phone_number, customer_name, place FROM customer
                WHERE phone_number LIKE ?
                ORDER BY phone_number ASC
                LIMIT 5
            """, (prefix + '%',))
        else:
            c.execute("""
                SELECT phone_number, customer_name, place FROM customer
                ORDER BY phone_number ASC
                LIMIT 5
            """)
        return c.fetchall()

def check_customer_name_phone_match(name, phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT customer_name FROM customer
            WHERE customer_name=? AND phone_number=?
        """, (name, phone))
        return c.fetchone() is not None
    
def phone_exists(phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM customer WHERE phone_number = ?", (phone,))
        return c.fetchone() is not None

def get_all_phone_numbers():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT phone_number FROM customer")
        return [row[0] for row in c.fetchall()]
    
def search_products_by_prefix(prefix):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT item, price, description
            FROM customer_product
            WHERE item LIKE ?
            GROUP BY item
            ORDER BY item ASC
            LIMIT 10
        """, (prefix + '%',))
        return c.fetchall()

def search_customer_by_name_words(words):
 
    with get_db_connection() as conn:
        c = conn.cursor()
        if not words:
            return []
        query = "SELECT DISTINCT customer_name FROM customer WHERE " + " OR ".join(["customer_name LIKE ?"] * len(words))
        params = [f"%{word}%" for word in words]
        c.execute(query, params)
        return c.fetchall()

def get_customer_by_name(name):

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT customer_name, phone_number, place FROM customer WHERE customer_name = ?", (name,))
        return c.fetchone()

def get_customer_by_phone(phone):
  
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT customer_name, phone_number, place FROM customer WHERE phone_number = ?", (phone,))
        return c.fetchone()
def get_customer_by_name_phone(name, phone):

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT customer_id, total_amount, amount_paid, remaining_amount, status, date
            FROM customer
            WHERE customer_name=? AND phone_number=?
            ORDER BY 
                CASE WHEN status='pending' THEN 0 ELSE 1 END,
                date DESC
        """, (name, phone))

        return c.fetchall()
    
def get_products_by_customer_id(customer_id):

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT item, qty, price, description, amount
            FROM customer_product
            WHERE customer_id=?
        """, (customer_id,))
        return c.fetchall()
    
def get_payments_by_customer_id(customer_id):

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT date, payment_id, customer_id, amount_paid
            FROM customer_payment
            WHERE customer_id=?
            ORDER BY date ASC
        """, (customer_id,))
        return c.fetchall()

def get_all_activity_dates(name, phone):
 
    with get_db_connection() as conn:
        c = conn.cursor()
        # Product dates
        c.execute("""
            SELECT DISTINCT DATE(pp.date)
FROM customer_product pp
JOIN customer u ON pp.customer_id = u.customer_id
WHERE u.customer_name=? AND u.phone_number=?

        """, (name, phone))
        product_dates = set(row[0] for row in c.fetchall())
        # Payment dates
        c.execute("""
           SELECT DISTINCT DATE(p.date)
FROM customer_payment p
JOIN customer u ON p.customer_id = u.customer_id
WHERE u.customer_name=? AND u.phone_number=?

        """, (name, phone))
        payment_dates = set(row[0] for row in c.fetchall())
        return product_dates.union(payment_dates)

def get_payment_dates_by_name_phone(name, phone):
  
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT DATE(p.date)
FROM customer_payment p
JOIN customer u ON p.customer_id = u.customer_id
WHERE u.customer_name=? AND u.phone_number=?

        """, (name, phone))
        return set(row[0] for row in c.fetchall())
    
def get_payments_by_name_phone_and_date(name, phone, date):
    """
    Returns all payments for this customer on a specific date.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT p.date, p.payment_id, p.customer_id, p.amount_paid
            FROM customer_payment p
            JOIN customer u ON p.customer_id = u.customer_id
            WHERE u.customer_name=? AND u.phone_number=? AND DATE(p.date)=?

            ORDER BY p.date ASC
        """, (name, phone, date))

        return c.fetchall()

def get_products_by_name_phone_and_date(name, phone, start_date=None, end_date=None):
   
    with get_db_connection() as conn:
        c = conn.cursor()
        base_query = """
            SELECT pp.item, pp.qty, pp.price, pp.description, pp.amount, pp.date
            FROM customer_product pp
            JOIN customer u ON pp.customer_id = u.customer_id
            WHERE u.customer_name=? AND u.phone_number=?
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
    
    return "CREDIT-" + datetime.now().strftime("%Y%m%d%H%M%S")

def add_customer_payment_to_record(customer_id, amount_paid):
 
    from datetime import datetime
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Get current paid and remaining amounts
            c.execute("SELECT total_amount, amount_paid, remaining_amount FROM customer WHERE customer_id=?", (customer_id,))
            row = c.fetchone()
            if not row:
                return False, None, None
            total_amount, current_paid, current_remaining = row
            if amount_paid <= 0 or amount_paid > current_remaining:
                return False, None, None

            # Insert payment
            payment_id = f"CREDIT-{int(datetime.now().timestamp())}"
            c.execute("""
                INSERT INTO customer_payment (customer_id, payment_id, date, amount_paid)
                VALUES (?, ?, ?, ?)
            """, (customer_id, payment_id, date_now, amount_paid))

            # Update purchaser table
            new_paid = current_paid + amount_paid
            new_remaining = total_amount - new_paid
            new_status = "completed" if abs(new_remaining) < 0.001 else "pending"
            c.execute("""
                UPDATE customer SET amount_paid=?, remaining_amount=?, status=?
                WHERE customer_id=?
            """, (new_paid, new_remaining, new_status, customer_id))

        return True, new_remaining, new_status
    except Exception as e:
        print("Payment error:", e)
        return False, None, None
    
def get_customer_id(name, phone, place):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT customer_id FROM customer WHERE customer_name=? AND phone_number=? AND place=?", (name, phone, place))
        row = c.fetchone()
        return row[0] if row else None


def get_customer_by_date_range(from_date=None, to_date=None):

    with get_db_connection() as conn:
        c = conn.cursor()
        if from_date and to_date:
            c.execute("""
                SELECT u.customer_name, p.item, p.qty, p.price, p.amount, p.date
                FROM customer_product p
                JOIN customer u ON p.customer_id = u.customer_id
                WHERE DATE(p.date) BETWEEN ? AND ?
                ORDER BY p.date DESC
            """, (from_date, to_date))
        else:
            c.execute("""
                SELECT u.customer_name, p.item, p.qty, p.price, p.amount, p.date
                FROM customer_product p
                JOIN customer u ON p.customer_id = u.customer_id
                ORDER BY p.date DESC
            """)
        return c.fetchall()


def get_recent_customer_payments(order='recent', limit=5):
   
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT u.customer_name, p.payment_id, p.amount_paid, p.date
            FROM customer_payment p
            JOIN customer u ON p.customer_id = u.customer_id
            ORDER BY datetime(p.date) {"DESC" if order == "recent" else "ASC"}
            LIMIT ?
        """, (limit,))
        return c.fetchall()

def update_customer_phone_place(old_name, old_place, new_phone, new_place):
    conn = get_db_connection()
    c = conn.cursor()
    # Check if purchaser exists
    c.execute("SELECT * FROM customer WHERE customer_name=? AND place=?", (old_name, old_place))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    # Check if new_phone is already used by another purchaser
    c.execute("SELECT * FROM customer WHERE phone_number=? AND NOT (customer_name=? AND place=?)", (new_phone, old_name, old_place))
    if c.fetchone():
        conn.close()
        return False
    # Update phone and place
    c.execute("UPDATE customer SET phone_number=?, place=? WHERE customer_name=? AND place=?", (new_phone, new_place, old_name, old_place))
    conn.commit()
    conn.close()
    return True

def get_all_products_by_name_phone(name, phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT pp.item, pp.qty, pp.price, pp.description, pp.amount, pp.date
            FROM customer_product pp
            JOIN customer u ON pp.customer_id = u.customer_id
            WHERE u.customer_name=? AND u.phone_number=?
            ORDER BY pp.date ASC
        """, (name, phone))
        return c.fetchall()

def update_product_by_id(prod_id, new_item, new_desc):
  
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE customer_product
            SET item = ?, description = ?
            WHERE id = ?
        """, (new_item, new_desc, prod_id))
        conn.commit()
        return c.rowcount > 0  # True if a row was updated

def get_product_id_by_details(customer_name, phone, item, qty, price, description, amount, date):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT pp.id
            FROM customer_product pp
            JOIN customer u ON pp.customer_id = u.customer_id
            WHERE u.customer_name=? AND u.phone_number=?
              AND pp.item=? AND pp.qty=? AND pp.price=? AND pp.description=? AND pp.amount=? AND pp.date=?
            LIMIT 1
        """, (customer_name, phone, item, qty, price, description, amount, date))
        row = c.fetchone()
        return row[0] if row else None

    
def update_product_quantity_and_amount_by_id(customer_id, new_qty, new_amount):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE customer_product
            SET qty=?, amount=?
            WHERE id=?
        """, (new_qty, new_amount, customer_id))
        conn.commit()

def update_customer_amounts(customer_id, new_total, new_remaining):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE customer
            SET total_amount=?, remaining_amount=?
            WHERE customer_id=?
        """, (new_total, new_remaining, customer_id))
        conn.commit()

def update_customer_status(customer_id, status):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE customer SET status=? WHERE customer_id=?", (status, customer_id))
        conn.commit()

def get_amount_paid_by_customer_id(customer_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT amount_paid FROM customer WHERE customer_id=?", (customer_id,))
        row = c.fetchone()
        return row[0] if row else 0

def delete_product_by_id(customer_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM customer_product WHERE id=?", (customer_id,))
        conn.commit()


def get_transactions_by_name_phone_and_date(name, phone, start, end):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT customer_id FROM customer WHERE customer_name=? AND phone_number=?", (name, phone))
        row = c.fetchone()
        if not row:
            return []
        customer_id = row[0]
        if start and end:
            c.execute("""
                SELECT p.date, p.payment_id, p.customer_id, p.amount_paid
                FROM customer_payment p
                WHERE p.customer_id=? AND DATE(p.date) BETWEEN ? AND ?
                ORDER BY p.date DESC
            """, (customer_id, start, end))
        else:
            c.execute("""
                SELECT p.date, p.payment_id, p.customer_id, p.amount_paid
                FROM customer_payment p
                WHERE p.customer_id=?
                ORDER BY p.date DESC
            """, (customer_id,))
        return c.fetchall()
    
def get_refund_customer_by_name_phone(name, phone):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT customer_id FROM customer WHERE customer_name=? AND phone_number=?", (name, phone))
        return c.fetchone()
    
def get_customer_by_name_phone_and_date(name, phone, from_date=None, to_date=None):
    with get_db_connection() as conn:
        c = conn.cursor()
        query = """
            SELECT p.item, p.qty, p.price, p.amount, p.date
            FROM customer_product p
            JOIN customer u ON p.customer_id = u.customer_id
            WHERE u.customer_name = ? AND u.phone_number = ?
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
