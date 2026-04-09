import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime

# Configuration for MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # TODO: move to env
    'database': 'isp_database'
}


def get_connection():
    """Creates a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"MySQL connection error: {e}")
    return None


def hash_password(password: str) -> str:
    """Hashes password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_default_admin():
    """Creates default admin user admin/admin on first run."""
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operators WHERE username = 'admin'")
    if not cursor.fetchone():
        sql = "INSERT INTO operators (username, password_hash, full_name) VALUES (%s, %s, %s)"
        val = ('admin', hash_password('admin'), 'Главный Администратор')
        cursor.execute(sql, val)
        conn.commit()
        print("Создан стандартный администратор: admin / admin")
    cursor.close()
    conn.close()


def verify_login(username, password):
    """Verifies login credentials in DB."""
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    hashed_pw = hash_password(password)
    cursor.execute("SELECT * FROM operators WHERE username = %s AND password_hash = %s", (username, hashed_pw))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


# ---------------------------
# Messaging helpers
# ---------------------------

def save_message(customer_id, sender_type, text, sender_name=None):
    """Stores a chat message for a customer."""
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (customer_id, sender_type, sender_name, text, created_at) VALUES (%s, %s, %s, %s, %s)",
        (customer_id, sender_type, sender_name, text, datetime.now()))
    conn.commit()
    message_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return message_id


def fetch_messages(customer_id, limit=200):
    """Returns latest messages for a customer ordered by time."""
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT message_id, sender_type, sender_name, text, created_at, is_read "
        "FROM messages WHERE customer_id = %s ORDER BY created_at ASC LIMIT %s", (customer_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def mark_messages_read(customer_id, reader_type):
    """
    Marks messages from the opposite side as read.
    reader_type: 'client' or 'support'
    """
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    opposite = 'support' if reader_type == 'client' else 'client'
    cursor.execute("UPDATE messages SET is_read = 1 WHERE customer_id = %s AND sender_type = %s AND is_read = 0",
                   (customer_id, opposite))
    conn.commit()
    cursor.close()
    conn.close()


def get_customer_by_phone(phone):
    """Fetches customer data by phone for mobile login."""
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE phone = %s", (phone,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    return customer


def get_customer_finance_summary(customer_id):
    """Returns total unpaid amount and next due date for dashboard."""
    conn = get_connection()
    if not conn:
        return {"due": 0, "next_due": None}
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT COALESCE(SUM(amount),0) as due, MIN(due_date) as next_due FROM billing WHERE customer_id = %s AND paid = 0",
        (customer_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row or {"due": 0, "next_due": None}
