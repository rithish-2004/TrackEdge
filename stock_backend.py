import sqlite3
import os

def aggregate_items(db_path, table_name):
    """
    Returns a dict {item_name: total_qty} for all rows in the table,
    summing up all quantities for each item (case-insensitive).
    """
    data = {}
    if not os.path.exists(db_path):
        return data
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"SELECT item, qty FROM {table_name}")
        for item, qty in cur.fetchall():
            base = item.strip().lower()
            data[base] = data.get(base, 0) + int(qty)
        conn.close()
    except Exception as e:
        print(f"Error reading {db_path}: {e}")
    return data

def get_stock_data():
    """
    Returns a dict {item_name: remaining_stock}
    where remaining_stock = total_purchased - total_sold, always >= 0.
    Also returns a dict of items where sales > purchases.
    """
    purchases = aggregate_items(os.path.join("inward", "purchase.db"), "purchase_product")
    sales = aggregate_items(os.path.join("outward", "customer.db"), "customer_product")
    all_items = set(purchases.keys()) | set(sales.keys())
    stock = {}
    missing_purchase = {}
    for item in all_items:
        purchase_qty = purchases.get(item, 0)
        sale_qty = sales.get(item, 0)
        if sale_qty > purchase_qty:
            missing_purchase[item] = sale_qty - purchase_qty
        stock[item] = max(0, purchase_qty - sale_qty)
    return stock, missing_purchase
