import mysql.connector
from mysql.connector import Error
import hashlib

# Configuration for MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # ВАЖНО: Укажи свой пароль от БД
    'database': 'isp_database'
}

def get_connection():
    """Creates a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None

def hash_password(password):
    """Хеширует пароль алгоритмом SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_admin():
    """Создает учетку admin:admin при первом запуске программы"""
    conn = get_connection()
    if conn:
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
    """Проверяет логин и пароль в БД"""
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        hashed_pw = hash_password(password)
        cursor.execute("SELECT * FROM operators WHERE username = %s AND password_hash = %s", (username, hashed_pw))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    return None