import unittest
import database


class TestISPSystem(unittest.TestCase):

    def test_password_hashing(self):
        """Тест функции хеширования пароля"""
        password = "admin"
        hashed = database.hash_password(password)
        expected_hash = "1c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
        self.assertEqual(hashed, expected_hash, "Хеширование работает неверно!")

    def test_database_connection(self):
        """Тест возможности подключения к БД"""
        conn = database.get_connection()
        self.assertIsNotNone(conn, "Не удалось подключиться к базе данных!")
        if conn:
            self.assertTrue(conn.is_connected(), "Соединение не активно!")
            conn.close()

    def test_verify_login_valid(self):
        """Тест функции проверки логина и пароля (интеграционный тест)"""
        # Проверяем, что при верных данных функция возвращает словарь с данными пользователя
        user = database.verify_login("admin", "admin")
        self.assertIsNotNone(user, "Пользователь admin не найден в БД!")
        if user:
            self.assertEqual(user['username'], "admin")


if __name__ == '__main__':
    unittest.main()