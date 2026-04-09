import customtkinter as ctk
import database

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MobileAppPrototype(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Эмуляция экрана смартфона
        self.title("Личный кабинет СКАТ")
        self.geometry("360x640")
        self.resizable(False, False)

        self.lbl_title = ctk.CTkLabel(self, text="СКАТ Провайдер", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(pady=(60, 5))

        self.lbl_sub = ctk.CTkLabel(self, text="Мобильный кабинет абонента", font=ctk.CTkFont(size=14),
                                    text_color="gray")
        self.lbl_sub.pack(pady=(0, 40))

        self.phone_entry = ctk.CTkEntry(self, placeholder_text="Номер телефона (+79...)", width=280, height=45)
        self.phone_entry.pack(pady=20)

        self.btn_check = ctk.CTkButton(self, text="Войти по номеру", width=280, height=45, command=self.check_data)
        self.btn_check.pack(pady=10)

        # Фрейм для результатов (информация о тарифе и балансе)
        self.info_frame = ctk.CTkFrame(self, width=300, fg_color="transparent")
        self.info_frame.pack(pady=30, fill="x", padx=20)

        self.result_lbl = ctk.CTkLabel(self.info_frame, text="", font=ctk.CTkFont(size=16), wraplength=300)
        self.result_lbl.pack(pady=5)

        self.tariff_lbl = ctk.CTkLabel(self.info_frame, text="", font=ctk.CTkFont(size=14, weight="bold"),
                                       text_color="#1f6aa5")
        self.tariff_lbl.pack(pady=5)

    def check_data(self):
        phone = self.phone_entry.get()
        if not phone:
            self.result_lbl.configure(text="Введите номер телефона!", text_color="red")
            self.tariff_lbl.configure(text="")
            return

        conn = database.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Ищем клиента и его тариф (сложный запрос JOIN)
            cursor.execute("""
                SELECT c.customer_id, c.name, p.name as plan_name, p.speed 
                FROM customers c 
                LEFT JOIN plans p ON c.plan_id = p.plan_id 
                WHERE c.phone = %s
            """, (phone,))
            user = cursor.fetchone()

            if user:
                # Считаем долги
                cursor.execute("SELECT SUM(amount) as total_debt FROM billing WHERE customer_id = %s AND paid = 0",
                               (user['customer_id'],))
                debt = cursor.fetchone()['total_debt']

                # Вывод информации
                if debt is None or debt == 0:
                    self.result_lbl.configure(text=f"Здравствуйте, {user['name']}!\nБаланс: Положительный",
                                              text_color="#00FF00")
                else:
                    self.result_lbl.configure(text=f"Здравствуйте, {user['name']}!\nК оплате: {debt} руб.",
                                              text_color="red")

                # Вывод тарифа
                if user['plan_name']:
                    self.tariff_lbl.configure(text=f"Ваш тариф: {user['plan_name']}\nСкорость: {user['speed']}")
                else:
                    self.tariff_lbl.configure(text="Тариф не назначен")
            else:
                self.result_lbl.configure(text="Абонент не найден.", text_color="red")
                self.tariff_lbl.configure(text="")

            cursor.close()
            conn.close()


if __name__ == "__main__":
    app = MobileAppPrototype()
    app.mainloop()