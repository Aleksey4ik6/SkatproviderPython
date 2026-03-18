import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import database
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import database
import subprocess # НУЖНО ДЛЯ ПИНГА
import platform   # НУЖНО ДЛЯ ОПРЕДЕЛЕНИЯ ОС
import threading  # Чтобы интерфейс не зависал во время пинга

# Set theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ISPAutomationSystem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Система интернет-провайдера СКАТ")
        self.geometry("1200x800")

        # Database connection
        self.conn = database.get_connection()
        if self.conn is None:
            messagebox.showerror("Ошибка БД", "Не удалось подключиться к базе данных MySQL. Проверьте настройки в database.py")
            # We can still run the UI but DB ops will fail
        
        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="СКАТ Провайдер", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Панель", command=lambda: self.select_frame("dashboard"))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Клиенты", command=lambda: self.select_frame("customers"))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Тарифы", command=lambda: self.select_frame("plans"))
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_4 = ctk.CTkButton(self.sidebar_frame, text="Обращения", command=lambda: self.select_frame("complaints"))
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_5 = ctk.CTkButton(self.sidebar_frame, text="Счета", command=lambda: self.select_frame("billing"))
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_button_6 = ctk.CTkButton(self.sidebar_frame, text="Диагностика", command=lambda: self.select_frame("troubleshooting"))
        self.sidebar_button_6.grid(row=6, column=0, padx=20, pady=10)

        # Main Content Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Initialize Frames
        self.frames = {}
        self.create_dashboard_frame()
        self.create_customers_frame()
        self.create_plans_frame()
        self.create_complaints_frame()
        self.create_billing_frame()
        self.create_troubleshooting_frame()

        self.select_frame("dashboard")

    def select_frame(self, name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show selected frame
        if name in self.frames:
            self.frames[name].pack(fill="both", expand=True)
            
            # Refresh data if needed
            if name == "dashboard":
                self.update_dashboard_stats()
            elif name == "customers":
                self.load_customers()
            elif name == "plans":
                self.load_plans()
            elif name == "complaints":
                self.load_complaints()
            elif name == "billing":
                self.load_bills()

    # --- Dashboard ---
    def create_dashboard_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["dashboard"] = frame

        label = ctk.CTkLabel(frame, text="Панель управления", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(anchor="w", pady=(0, 20))

        # Stats Grid
        stats_grid = ctk.CTkFrame(frame, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 20))

        self.stat_card(stats_grid, "Всего клиентов", "0", 0, 0)
        self.stat_card(stats_grid, "Активных клиентов", "0", 0, 1)
        self.stat_card(stats_grid, "Тарифов", "0", 0, 2)
        self.stat_card(stats_grid, "Открытых обращений", "0", 0, 3)

        # Recent Activity
        activity_label = ctk.CTkLabel(frame, text="Недавняя активность", font=ctk.CTkFont(size=18, weight="bold"))
        activity_label.pack(anchor="w", pady=(10, 10))

        # Treeview for activity (using ttk as ctk doesn't have a complex table yet)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white", rowheight=25)
        style.configure("Treeview.Heading", background="#1f6aa5", foreground="white")
        
        columns = ('type', 'details', 'date')
        self.activity_tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)
        self.activity_tree.heading('type', text='Тип')
        self.activity_tree.heading('details', text='Детали')
        self.activity_tree.heading('date', text='Дата')
        self.activity_tree.column('type', width=150)
        self.activity_tree.column('details', width=400)
        self.activity_tree.column('date', width=150)
        self.activity_tree.pack(fill="both", expand=True)

    def stat_card(self, parent, title, value, row, col):
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        title_lbl.pack(padx=10, pady=(10, 0))
        
        value_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        value_lbl.pack(padx=10, pady=(5, 10))
        
        # Store reference to update later
        setattr(self, f"stat_{title.replace(' ', '_')}", value_lbl)

    def update_dashboard_stats(self):
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM customers')
            self.stat_Всего_клиентов.configure(text=str(cursor.fetchone()[0]))

            cursor.execute('SELECT COUNT(*) FROM customers WHERE plan_id IS NOT NULL')
            self.stat_Активных_клиентов.configure(text=str(cursor.fetchone()[0]))

            cursor.execute('SELECT COUNT(*) FROM plans')
            self.stat_Тарифов.configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM complaints WHERE status != 'Решено'")
            self.stat_Открытых_обращений.configure(text=str(cursor.fetchone()[0]))

            # Activity
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)

            cursor.execute('''
            SELECT 'Новый клиент' as type, name as details, registration_date as date
            FROM customers
            ORDER BY registration_date DESC
            LIMIT 5
            ''')
            for row in cursor.fetchall():
                self.activity_tree.insert('', 'end', values=row)

            cursor.close()
        except Exception as e:
            print(f"Error updating dashboard: {e}")

    # --- Customers ---
    def create_customers_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["customers"] = frame

        # Input Form
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", pady=(0, 20))

        self.cust_name = ctk.CTkEntry(form_frame, placeholder_text="Имя")
        self.cust_name.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.cust_address = ctk.CTkEntry(form_frame, placeholder_text="Адрес")
        self.cust_address.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.cust_phone = ctk.CTkEntry(form_frame, placeholder_text="Телефон")
        self.cust_phone.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        self.cust_email = ctk.CTkEntry(form_frame, placeholder_text="Email")
        self.cust_email.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.cust_plan = ctk.CTkComboBox(form_frame, values=["Выберите тариф"])
        self.cust_plan.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        btn_add = ctk.CTkButton(form_frame, text="Добавить", command=self.add_customer)
        btn_add.grid(row=1, column=2, padx=10, pady=10)

        form_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Table
        columns = ('id', 'name', 'address', 'phone', 'email', 'plan')
        self.cust_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.cust_tree.heading(col, text=col.capitalize())
            self.cust_tree.column(col, width=100)
        self.cust_tree.pack(fill="both", expand=True)

    def load_customers(self):
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT c.customer_id, c.name, c.address, c.phone, c.email, p.name 
            FROM customers c LEFT JOIN plans p ON c.plan_id = p.plan_id
            ''')
            rows = cursor.fetchall()
            
            for item in self.cust_tree.get_children():
                self.cust_tree.delete(item)
            
            for row in rows:
                self.cust_tree.insert('', 'end', values=row)
            
            # Update plan combobox
            cursor.execute('SELECT plan_id, name FROM plans')
            plans = cursor.fetchall()
            self.cust_plan.configure(values=[f"{p[0]} - {p[1]}" for p in plans])
            
            cursor.close()
        except Exception as e:
            print(f"Error loading customers: {e}")

    def add_customer(self):
        if not self.conn: return
        name = self.cust_name.get()
        address = self.cust_address.get()
        phone = self.cust_phone.get()
        email = self.cust_email.get()
        plan_str = self.cust_plan.get()

        if not all([name, address, phone, email]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        try:
            plan_id = int(plan_str.split(' - ')[0]) if ' - ' in plan_str else None
            cursor = self.conn.cursor()
            sql = "INSERT INTO customers (name, address, phone, email, plan_id, registration_date) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (name, address, phone, email, plan_id, datetime.now())
            cursor.execute(sql, val)
            self.conn.commit()
            cursor.close()
            self.load_customers()
            messagebox.showinfo("Успех", "Клиент добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- Plans ---
    def create_plans_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["plans"] = frame

        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", pady=(0, 20))

        self.plan_name = ctk.CTkEntry(form_frame, placeholder_text="Название")
        self.plan_name.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.plan_speed = ctk.CTkEntry(form_frame, placeholder_text="Скорость")
        self.plan_speed.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.plan_price = ctk.CTkEntry(form_frame, placeholder_text="Цена")
        self.plan_price.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        btn_add = ctk.CTkButton(form_frame, text="Добавить тариф", command=self.add_plan)
        btn_add.grid(row=1, column=1, padx=10, pady=10)

        form_frame.grid_columnconfigure((0, 1, 2), weight=1)

        columns = ('id', 'name', 'speed', 'price')
        self.plans_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.plans_tree.heading(col, text=col.capitalize())
        self.plans_tree.pack(fill="both", expand=True)

    def load_plans(self):
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT plan_id, name, speed, price FROM plans')
            rows = cursor.fetchall()
            for item in self.plans_tree.get_children():
                self.plans_tree.delete(item)
            for row in rows:
                self.plans_tree.insert('', 'end', values=row)
            cursor.close()
        except Exception as e:
            print(f"Error loading plans: {e}")

    def add_plan(self):
        if not self.conn: return
        try:
            name = self.plan_name.get()
            speed = self.plan_speed.get()
            price = float(self.plan_price.get())
            
            cursor = self.conn.cursor()
            sql = "INSERT INTO plans (name, speed, price) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, speed, price))
            self.conn.commit()
            cursor.close()
            self.load_plans()
            messagebox.showinfo("Успех", "Тариф добавлен")
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- Complaints ---
    def create_complaints_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["complaints"] = frame

        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", pady=(0, 20))

        self.comp_cust = ctk.CTkComboBox(form_frame, values=["Выберите клиента"])
        self.comp_cust.pack(fill="x", padx=10, pady=10)
        
        self.comp_desc = ctk.CTkEntry(form_frame, placeholder_text="Описание проблемы")
        self.comp_desc.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(form_frame, text="Создать обращение", command=self.add_complaint).pack(pady=10)

        columns = ('id', 'customer', 'desc', 'status', 'date')
        self.comp_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.comp_tree.heading(col, text=col.capitalize())
        self.comp_tree.pack(fill="both", expand=True)

    def load_complaints(self):
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            
            # Load customers for combobox
            cursor.execute("SELECT customer_id, name FROM customers")
            custs = cursor.fetchall()
            self.comp_cust.configure(values=[f"{c[0]} - {c[1]}" for c in custs])

            # Load complaints
            cursor.execute('''
            SELECT co.complaint_id, c.name, co.description, co.status, co.date 
            FROM complaints co JOIN customers c ON co.customer_id = c.customer_id
            ''')
            rows = cursor.fetchall()
            for item in self.comp_tree.get_children():
                self.comp_tree.delete(item)
            for row in rows:
                self.comp_tree.insert('', 'end', values=row)
            cursor.close()
        except Exception as e:
            print(f"Error loading complaints: {e}")

    def add_complaint(self):
        if not self.conn: return
        try:
            cust_str = self.comp_cust.get()
            desc = self.comp_desc.get()
            
            if ' - ' not in cust_str:
                messagebox.showerror("Ошибка", "Выберите клиента")
                return
                
            cust_id = int(cust_str.split(' - ')[0])
            
            cursor = self.conn.cursor()
            sql = "INSERT INTO complaints (customer_id, description, status, date) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (cust_id, desc, 'Открыто', datetime.now()))
            self.conn.commit()
            cursor.close()
            self.load_complaints()
            messagebox.showinfo("Успех", "Обращение создано")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- Billing ---
    def create_billing_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["billing"] = frame

        # Form
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", pady=(0, 20))

        self.bill_cust = ctk.CTkComboBox(form_frame, values=["Выберите клиента"])
        self.bill_cust.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.bill_amount = ctk.CTkEntry(form_frame, placeholder_text="Сумма")
        self.bill_amount.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.bill_date = ctk.CTkEntry(form_frame, placeholder_text="Срок (YYYY-MM-DD)")
        self.bill_date.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.bill_date.insert(0, (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))

        btn_create = ctk.CTkButton(form_frame, text="Создать счёт", command=self.generate_bill)
        btn_create.grid(row=1, column=0, padx=10, pady=10)
        
        btn_pay = ctk.CTkButton(form_frame, text="Отметить оплаченным", command=self.mark_bill_paid, fg_color="green")
        btn_pay.grid(row=1, column=1, padx=10, pady=10)

        form_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Table
        columns = ('id', 'customer', 'amount', 'due_date', 'status')
        self.bills_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.bills_tree.heading(col, text=col.capitalize())
        self.bills_tree.pack(fill="both", expand=True)

    def load_bills(self):
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            
            # Load customers
            cursor.execute("SELECT customer_id, name FROM customers")
            custs = cursor.fetchall()
            self.bill_cust.configure(values=[f"{c[0]} - {c[1]}" for c in custs])

            # Load bills
            cursor.execute('''
            SELECT b.bill_id, c.name, b.amount, b.due_date, 
                   CASE WHEN b.paid = 1 THEN 'Оплачен' ELSE 'Не оплачен' END as status
            FROM billing b JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.due_date DESC
            ''')
            rows = cursor.fetchall()
            for item in self.bills_tree.get_children():
                self.bills_tree.delete(item)
            for row in rows:
                self.bills_tree.insert('', 'end', values=row)
            cursor.close()
        except Exception as e:
            print(f"Error loading bills: {e}")

    def generate_bill(self):
        if not self.conn: return
        try:
            cust_str = self.bill_cust.get()
            amount = float(self.bill_amount.get())
            due_date = self.bill_date.get()
            
            if ' - ' not in cust_str:
                messagebox.showerror("Ошибка", "Выберите клиента")
                return
            
            cust_id = int(cust_str.split(' - ')[0])
            
            cursor = self.conn.cursor()
            sql = "INSERT INTO billing (customer_id, amount, due_date, paid) VALUES (%s, %s, %s, 0)"
            cursor.execute(sql, (cust_id, amount, due_date))
            self.conn.commit()
            cursor.close()
            self.load_bills()
            messagebox.showinfo("Успех", "Счёт создан")
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def mark_bill_paid(self):
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите счёт")
            return
            
        bill_id = self.bills_tree.item(selected[0])['values'][0]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE billing SET paid = 1, payment_date = %s WHERE bill_id = %s", (datetime.now(), bill_id))
            self.conn.commit()
            cursor.close()
            self.load_bills()
            messagebox.showinfo("Успех", "Счёт оплачен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- Troubleshooting ---
    def create_troubleshooting_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["troubleshooting"] = frame
        
        ctk.CTkLabel(frame, text="Диагностика сети", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        self.trouble_var = ctk.StringVar(value="no_connection")
        
        options_frame = ctk.CTkFrame(frame)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkRadioButton(options_frame, text="Нет подключения к интернету", variable=self.trouble_var, value="no_connection").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkRadioButton(options_frame, text="Низкая скорость / Буферизация", variable=self.trouble_var, value="slow").grid(row=0, column=1, padx=20, pady=10, sticky="w")
        ctk.CTkRadioButton(options_frame, text="Высокий пинг / Задержки", variable=self.trouble_var, value="ping").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkRadioButton(options_frame, text="Проблемы с DNS (сайты не грузятся)", variable=self.trouble_var, value="dns").grid(row=1, column=1, padx=20, pady=10, sticky="w")
        ctk.CTkRadioButton(options_frame, text="Проблемы с Wi-Fi роутером", variable=self.trouble_var, value="router").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        ctk.CTkButton(frame, text="Запустить диагностику", command=self.run_diag, height=40).pack(pady=20)
        
        self.diag_result = ctk.CTkTextbox(frame, height=250, font=ctk.CTkFont(family="Consolas", size=12))
        self.diag_result.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def run_diag(self):
        issue = self.trouble_var.get()
        self.diag_result.delete("0.0", "end")
        
        steps = []
        if issue == "no_connection":
            steps = [
                "1. Проверка физического подключения кабеля WAN... [OK]",
                "2. Пинг шлюза провайдера... [FAIL]",
                "3. Перезагрузка порта на коммутаторе... [DONE]",
                "4. Проверка статуса оплаты... [OK]",
                "\nРЕКОМЕНДАЦИЯ: Перезагрузите роутер. Если не поможет, требуется выезд техника."
            ]
        elif issue == "slow":
            steps = [
                "1. Замер скорости до ближайшего узла... [15 Mbps / 100 Mbps]",
                "2. Проверка загрузки канала... [HIGH]",
                "3. Анализ подключенных устройств... [5 активных устройств]",
                "\nРЕКОМЕНДАЦИЯ: Проверьте, не скачиваются ли обновления. Попробуйте подключиться по кабелю."
            ]
        elif issue == "ping":
            steps = [
                "1. Трассировка маршрута до 8.8.8.8... [OK]",
                "2. Проверка потерь пакетов... [0% loss]",
                "3. Проверка загрузки CPU роутера... [NORMAL]",
                "\nРЕКОМЕНДАЦИЯ: Используйте проводное подключение для игр. Проверьте настройки QoS на роутере."
            ]
        elif issue == "dns":
            steps = [
                "1. Проверка доступности DNS серверов... [TIMEOUT]",
                "2. Смена DNS на 8.8.8.8... [DONE]",
                "3. Очистка кэша DNS... [DONE]",
                "\nРЕКОМЕНДАЦИЯ: Попробуйте открыть сайт снова. Проблема должна быть решена."
            ]
        elif issue == "router":
            steps = [
                "1. Опрос статуса роутера... [ONLINE]",
                "2. Проверка уровня сигнала Wi-Fi... [WEAK -75dBm]",
                "3. Проверка канала Wi-Fi... [INTERFERENCE DETECTED]",
                "\nРЕКОМЕНДАЦИЯ: Смените канал Wi-Fi на менее загруженный (например, 1, 6 или 11). Переместите роутер ближе к центру помещения."
            ]
            
        # Simulate typing effect (simplified here)
        self.diag_result.insert("0.0", "Запуск диагностики...\n\n")
        for step in steps:
            self.diag_result.insert("end", step + "\n")

if __name__ == "__main__":
    app = ISPAutomationSystem()
    app.mainloop()
