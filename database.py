import sqlite3

DB_NAME = "isp_database.db"


def get_connection(db_path: str = DB_NAME) -> sqlite3.Connection:
    """
    Создаёт подключение к БД и гарантирует наличие всех таблиц.
    """
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """
    Создаёт таблицы, если их ещё нет.
    """
    cursor = conn.cursor()

    # Клиенты
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        plan_id INTEGER,
        registration_date TEXT,
        FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
    )
    ''')

    # Тарифы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plans (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        speed TEXT NOT NULL,
        price REAL NOT NULL,
        data_limit TEXT,
        description TEXT
    )
    ''')

    # Обращения
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        resolution TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    ''')

    # Счета
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS billing (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        due_date TEXT NOT NULL,
        paid INTEGER DEFAULT 0,
        payment_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    ''')

    conn.commit()
