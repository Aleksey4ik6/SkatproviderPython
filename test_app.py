import unittest
import database


class TestISPSystem(unittest.TestCase):

    def test_password_hashing(self):
        """Тест функции хеширования пароля"""
        password = "admin"
        hashed = database.hash_password(password)
        # Хеш слова 'admin' в SHA-256 всегда одинаковый
        expected_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
        self.assertEqual(hashed, expected_hash, "Хеширование работает неверно!")

    def test_database_connection(self):
        """Тест возможности подключения к БД"""
        conn = database.get_connection()
        self.assertIsNotNone(conn, "Не удалось подключиться к базе данных!")
        if conn:
            self.assertTrue(conn.is_connected(), "Соединение не активно!")
            conn.close()


if __name__ == '__main__':
    unittest.main()
