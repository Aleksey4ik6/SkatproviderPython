import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import threading
import subprocess
import platform
import database
import requests
import time
import re

# Настройки темы
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ISPAutomationSystem(ctk.CTk):
    def __init__(self, operator_data):
        super().__init__()

        self.operator = operator_data
        self.title(f"АРМ Оператора СКАТ - {self.operator['full_name']}")
        self.geometry("1200x800")

        self.conn = database.get_connection()
        if self.conn is None:
            messagebox.showerror("Ошибка БД", "Не удалось подключиться к базе данных. Проверьте database.py")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Боковое меню ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="СКАТ Провайдер",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.operator_label = ctk.CTkLabel(self.sidebar_frame, text=f"Сотрудник:\n{self.operator['full_name']}",
                                           font=ctk.CTkFont(size=12), text_color="gray")
        self.operator_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.btn_panel = ctk.CTkButton(self.sidebar_frame, text="Панель",
                                       command=lambda: self.select_frame("dashboard"))
        self.btn_panel.grid(row=2, column=0, padx=20, pady=10)

        self.btn_clients = ctk.CTkButton(self.sidebar_frame, text="Клиенты",
                                         command=lambda: self.select_frame("customers"))
        self.btn_clients.grid(row=3, column=0, padx=20, pady=10)

        self.btn_plans = ctk.CTkButton(self.sidebar_frame, text="Тарифы", command=lambda: self.select_frame("plans"))
        self.btn_plans.grid(row=4, column=0, padx=20, pady=10)

        self.btn_complaints = ctk.CTkButton(self.sidebar_frame, text="Обращения",
                                            command=lambda: self.select_frame("complaints"))
        self.btn_complaints.grid(row=5, column=0, padx=20, pady=10)

        self.btn_billing = ctk.CTkButton(self.sidebar_frame, text="Счета", command=lambda: self.select_frame("billing"))
        self.btn_billing.grid(row=6, column=0, padx=20, pady=10)

        self.btn_diag = ctk.CTkButton(self.sidebar_frame, text="Диагностика", fg_color="#8B0000", hover_color="#A52A2A",
                                      command=lambda: self.select_frame("troubleshooting"))
        self.btn_diag.grid(row=7, column=0, padx=20, pady=10)

        self.btn_ai = ctk.CTkButton(self.sidebar_frame, text="ИИ Ассистент", fg_color="#4B0082", hover_color="#800080",
                                    command=lambda: self.select_frame("ai_assistant"))
        self.btn_ai.grid(row=8, column=0, padx=20, pady=20)

        # --- Основная область ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.frames = {}
        self.create_dashboard_frame()
        self.create_customers_frame()
        self.create_plans_frame()
        self.create_complaints_frame()
        self.create_billing_frame()
        self.create_troubleshooting_frame()
        self.create_ai_frame()

        self.select_frame("dashboard")

    def select_frame(self, name):
        for frame in self.frames.values(): frame.pack_forget()
        if name in self.frames:
            self.frames[name].pack(fill="both", expand=True)
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
            elif name == "troubleshooting":
                self.load_diag_customers()

    # ==========================================
    # ДАШБОРД
    # ==========================================
    def create_dashboard_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["dashboard"] = frame
        ctk.CTkLabel(frame, text="Панель управления", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w",
                                                                                                     pady=(0, 20))
        stats_grid = ctk.CTkFrame(frame, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 20))
        self.stat_card(stats_grid, "Всего клиентов", "0", 0, 0)
        self.stat_card(stats_grid, "Активных клиентов", "0", 0, 1)
        self.stat_card(stats_grid, "Тарифов", "0", 0, 2)
        self.stat_card(stats_grid, "Открытых обращений", "0", 0, 3)
        ctk.CTkLabel(frame, text="Недавняя активность", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w",
                                                                                                       pady=(10, 10))
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white", rowheight=25)
        style.configure("Treeview.Heading", background="#1f6aa5", foreground="white")
        columns = ('type', 'details', 'date')
        self.activity_tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)
        self.activity_tree.heading('type', text='Тип');
        self.activity_tree.heading('details', text='Детали');
        self.activity_tree.heading('date', text='Дата')
        self.activity_tree.pack(fill="both", expand=True)

    def stat_card(self, parent, title, value, row, col):
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(padx=10, pady=(10, 0))
        value_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        value_lbl.pack(padx=10, pady=(5, 10))
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
            for item in self.activity_tree.get_children(): self.activity_tree.delete(item)
            cursor.execute(
                "SELECT 'Новый клиент' as type, name as details, registration_date as date FROM customers ORDER BY registration_date DESC LIMIT 5")
            for row in cursor.fetchall(): self.activity_tree.insert('', 'end', values=row)
            cursor.close()
        except Exception:
            pass

    # ==========================================
    # КЛИЕНТЫ
    # ==========================================
    def create_customers_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["customers"] = frame
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", pady=(0, 20))
        self.cust_name = ctk.CTkEntry(form_frame, placeholder_text="ФИО")
        self.cust_name.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.cust_address = ctk.CTkEntry(form_frame, placeholder_text="Адрес")
        self.cust_address.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.cust_phone = ctk.CTkEntry(form_frame, placeholder_text="Телефон")
        self.cust_phone.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.cust_email = ctk.CTkEntry(form_frame, placeholder_text="Email")
        self.cust_email.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.cust_ip = ctk.CTkEntry(form_frame, placeholder_text="IP Роутера (напр. 192.168.1.10)")
        self.cust_ip.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.cust_plan = ctk.CTkComboBox(form_frame, values=["Выберите тариф"])
        self.cust_plan.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        btn_add = ctk.CTkButton(form_frame, text="Добавить клиента", command=self.add_customer)
        btn_add.grid(row=2, column=1, padx=10, pady=10)
        form_frame.grid_columnconfigure((0, 1, 2), weight=1)
        columns = ('id', 'name', 'address', 'phone', 'ip', 'plan')
        self.cust_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns: self.cust_tree.heading(col, text=col.upper())
        self.cust_tree.bind("<Double-1>", self.edit_customer_on_click)
        self.cust_tree.pack(fill="both", expand=True)

    def load_customers(self):
        if not self.conn: return
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT c.customer_id, c.name, c.address, c.phone, c.ip_address, p.name FROM customers c LEFT JOIN plans p ON c.plan_id = p.plan_id")
        for item in self.cust_tree.get_children(): self.cust_tree.delete(item)
        for row in cursor.fetchall(): self.cust_tree.insert('', 'end', values=row)
        cursor.execute('SELECT plan_id, name FROM plans')
        self.cust_plan.configure(values=[f"{p[0]} - {p[1]}" for p in cursor.fetchall()])
        cursor.close()

    def add_customer(self):
        if not self.conn: return
        name = self.cust_name.get();
        address = self.cust_address.get();
        phone = self.cust_phone.get()
        email = self.cust_email.get();
        ip_addr = self.cust_ip.get();
        plan_str = self.cust_plan.get()
        if not all([name, address, phone]): return messagebox.showerror("Ошибка", "Заполните ФИО, адрес и телефон")
        plan_id = int(plan_str.split(' - ')[0]) if ' - ' in plan_str else None
        ip_addr = ip_addr if ip_addr else "192.168.1.1"
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO customers (name, address, phone, email, ip_address, plan_id, registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, address, phone, email, ip_addr, plan_id, datetime.now()))
            self.conn.commit()
            cursor.close()
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def edit_customer_on_click(self, event):
        item_id = self.cust_tree.focus()
        if not item_id: return
        item = self.cust_tree.item(item_id)
        customer_id, current_name = item['values'][0], item['values'][1]
        new_name = simpledialog.askstring("Редактирование", f"Новое ФИО для '{current_name}':",
                                          initialvalue=current_name)
        if new_name and new_name.strip() != "":
            try:
                cursor = self.conn.cursor()
                cursor.execute("UPDATE customers SET name = %s WHERE customer_id = %s", (new_name, customer_id))
                self.conn.commit()
                cursor.close()
                self.load_customers()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    # ==========================================
    # ТАРИФЫ
    # ==========================================
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
        ctk.CTkButton(form_frame, text="Добавить тариф", command=self.add_plan).grid(row=1, column=1, padx=10, pady=10)
        form_frame.grid_columnconfigure((0, 1, 2), weight=1)
        columns = ('id', 'name', 'speed', 'price')
        self.plans_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns: self.plans_tree.heading(col, text=col.upper())
        self.plans_tree.pack(fill="both", expand=True)

    def load_plans(self):
        if not self.conn: return
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM plans')
        for item in self.plans_tree.get_children(): self.plans_tree.delete(item)
        for row in cursor.fetchall(): self.plans_tree.insert('', 'end', values=row)
        cursor.close()

    def add_plan(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO plans (name, speed, price) VALUES (%s, %s, %s)",
                           (self.plan_name.get(), self.plan_speed.get(), float(self.plan_price.get())))
            self.conn.commit()
            cursor.close()
            self.load_plans()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ==========================================
    # ОБРАЩЕНИЯ
    # ==========================================
    def create_complaints_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["complaints"] = frame
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", pady=(0, 20))
        self.comp_cust = ctk.CTkComboBox(form_frame, width=300, values=["Выберите клиента"])
        self.comp_cust.pack(padx=10, pady=10)
        self.comp_desc = ctk.CTkEntry(form_frame, width=300, placeholder_text="Описание проблемы")
        self.comp_desc.pack(padx=10, pady=10)
        ctk.CTkButton(form_frame, text="Создать тикет", command=self.add_complaint).pack(pady=10)
        columns = ('id', 'customer', 'desc', 'status', 'date')
        self.comp_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns: self.comp_tree.heading(col, text=col.upper())
        self.comp_tree.pack(fill="both", expand=True)

    def load_complaints(self):
        if not self.conn: return
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id, name FROM customers")
        self.comp_cust.configure(values=[f"{c[0]} - {c[1]}" for c in cursor.fetchall()])
        cursor.execute(
            "SELECT co.complaint_id, c.name, co.description, co.status, co.date FROM complaints co JOIN customers c ON co.customer_id = c.customer_id")
        for item in self.comp_tree.get_children(): self.comp_tree.delete(item)
        for row in cursor.fetchall(): self.comp_tree.insert('', 'end', values=row)
        cursor.close()

    def add_complaint(self):
        if ' - ' not in self.comp_cust.get(): return
        cust_id = int(self.comp_cust.get().split(' - ')[0])
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO complaints (customer_id, description, status, date) VALUES (%s, %s, %s, %s)",
                       (cust_id, self.comp_desc.get(), 'Открыто', datetime.now()))
        self.conn.commit()
        cursor.close()
        self.load_complaints()

    # ==========================================
    # СЧЕТА
    # ==========================================
    def create_billing_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["billing"] = frame
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", pady=(0, 20))
        self.bill_cust = ctk.CTkComboBox(form_frame, values=["Выберите клиента"])
        self.bill_cust.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.bill_amount = ctk.CTkEntry(form_frame, placeholder_text="Сумма")
        self.bill_amount.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(form_frame, text="Выставить счёт", command=self.generate_bill).grid(row=1, column=0, padx=10,
                                                                                          pady=10)
        ctk.CTkButton(form_frame, text="Оплатить выбранный", fg_color="green", command=self.mark_bill_paid).grid(row=1,
                                                                                                                 column=1,
                                                                                                                 padx=10,
                                                                                                                 pady=10)
        form_frame.grid_columnconfigure((0, 1), weight=1)
        columns = ('id', 'customer', 'amount', 'due_date', 'status')
        self.bills_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns: self.bills_tree.heading(col, text=col.upper())
        self.bills_tree.pack(fill="both", expand=True)

    def load_bills(self):
        if not self.conn: return
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id, name FROM customers")
        self.bill_cust.configure(values=[f"{c[0]} - {c[1]}" for c in cursor.fetchall()])
        cursor.execute(
            "SELECT b.bill_id, c.name, b.amount, b.due_date, CASE WHEN b.paid = 1 THEN 'Оплачен' ELSE 'Долг' END FROM billing b JOIN customers c ON b.customer_id = c.customer_id ORDER BY b.due_date DESC")
        for item in self.bills_tree.get_children(): self.bills_tree.delete(item)
        for row in cursor.fetchall(): self.bills_tree.insert('', 'end', values=row)
        cursor.close()

    def generate_bill(self):
        if ' - ' not in self.bill_cust.get(): return
        cust_id = int(self.bill_cust.get().split(' - ')[0])
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO billing (customer_id, amount, due_date, paid) VALUES (%s, %s, %s, 0)",
                       (cust_id, float(self.bill_amount.get()), datetime.now() + timedelta(days=30)))
        self.conn.commit()
        cursor.close()
        self.load_bills()

    def mark_bill_paid(self):
        selected = self.bills_tree.selection()
        if not selected: return
        bill_id = self.bills_tree.item(selected[0])['values'][0]
        cursor = self.conn.cursor()
        cursor.execute("UPDATE billing SET paid = 1, payment_date = %s WHERE bill_id = %s", (datetime.now(), bill_id))
        self.conn.commit()
        cursor.close()
        self.load_bills()

    # ==========================================
    # ДИАГНОСТИКА
    # ==========================================
    def create_troubleshooting_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["troubleshooting"] = frame
        ctk.CTkLabel(frame, text="Удаленная сетевая диагностика (ICMP)", font=ctk.CTkFont(size=20, weight="bold")).pack(
            pady=20)
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(form_frame, text="Целевой узел:").grid(row=0, column=0, padx=10, pady=10)
        self.diag_cust_combo = ctk.CTkComboBox(form_frame, width=350, values=["Загрузка..."])
        self.diag_cust_combo.grid(row=0, column=1, padx=10, pady=10)
        self.btn_run_diag = ctk.CTkButton(form_frame, text="Начать PING", command=self.start_diag_thread,
                                          fg_color="#1f6aa5")
        self.btn_run_diag.grid(row=0, column=2, padx=10, pady=10)
        self.diag_result = ctk.CTkTextbox(frame, height=400, font=ctk.CTkFont(family="Consolas", size=14),
                                          fg_color="#0a0a0a", text_color="#00ff00")
        self.diag_result.pack(fill="both", expand=True, padx=20, pady=20)
        self.diag_result.insert("0.0", "Терминал готов...\n")

    def load_diag_customers(self):
        if not self.conn: return
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id, name, ip_address FROM customers")
        self.diag_cust_combo.configure(values=[f"{c[0]} - {c[1]} [IP: {c[2]}]" for c in cursor.fetchall()])
        cursor.close()

    def start_diag_thread(self):
        cust_str = self.diag_cust_combo.get()
        if ' [IP: ' not in cust_str: return
        ip_address = cust_str.split('[IP: ')[1].replace(']', '')
        self.diag_result.delete("0.0", "end")
        self.diag_result.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] PING {ip_address}\n")
        self.btn_run_diag.configure(state="disabled")
        threading.Thread(target=self.run_ping, args=(ip_address,), daemon=True).start()

    def safe_print(self, text):
        self.after(0, lambda: self.diag_result.insert("end", text))

    def run_ping(self, ip_address):
        if ip_address == "10.255.255.254":
            self.safe_print(f"Обмен пакетами с {ip_address} по с 32 байтами данных:\n")
            for _ in range(4): time.sleep(1); self.safe_print("Превышен интервал ожидания для запроса.\n")
            self.safe_print("\n[СТАТУС]: УЗЕЛ НЕДОСТУПЕН (Тайм-аут).\n")
            self.after(0, lambda: self.btn_run_diag.configure(state="normal", text="Начать PING"))
            return
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        try:
            result = subprocess.run(['ping', param, '4', ip_address], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding='cp866')
            self.safe_print(result.stdout + "\n")
        except Exception as e:
            self.safe_print(f"Ошибка ОС: {str(e)}\n")
        finally:
            self.after(0, lambda: self.btn_run_diag.configure(state="normal", text="Начать PING"))

    # ==========================================
    # ИИ АССИСТЕНТ (НАКОНЕЦ-ТО С ЖИРНЫМ ШРИФТОМ!)
    # ==========================================
    def create_ai_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["ai_assistant"] = frame

        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text="ИИ-Помощник инженера", font=ctk.CTkFont(size=20, weight="bold")).pack(
            side="left")

        # Окно чата
        self.ai_chat_window = ctk.CTkTextbox(frame, height=450, font=ctk.CTkFont(size=14), wrap="word")
        self.ai_chat_window.pack(fill="both", expand=True, padx=10, pady=10)

        # -------------------------------------------------------------------
        # СОЗДАЕМ ТЕГ ДЛЯ ЖИРНОГО ШРИФТА ЧЕРЕЗ БАЗОВЫЙ TKINTER
        # -------------------------------------------------------------------
        bold_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        # Обращаемся к "внутреннему" слою текстового поля, чтобы настроить тег
        self.ai_chat_window._textbox.tag_configure("bold_tag", font=bold_font)

        welcome_text = "Система: Суфлер готов. Опишите проблему.\n" + "-" * 50 + "\n\n"
        self.ai_chat_window.insert("0.0", welcome_text)
        self.ai_chat_window.configure(state="disabled")

        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.ai_input = ctk.CTkEntry(input_frame, placeholder_text="Опишите проблему клиента...", height=40)
        self.ai_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_ai_send = ctk.CTkButton(input_frame, text="Отправить", command=self.send_to_ai, width=120, height=40)
        self.btn_ai_send.pack(side="right")

    def insert_with_markdown(self, text):
        """Очищает текст от markdown-символов и вставляет как plain text."""
        # Убираем заголовки: ### Текст -> Текст
        text = re.sub(r'^#{1,3}\s*', '', text, flags=re.MULTILINE)
        # Убираем жирный: **текст** -> текст
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.DOTALL)
        # Убираем курсив: *текст* -> текст
        text = re.sub(r'\*(.+?)\*', r'\1', text, flags=re.DOTALL)
        # Убираем инлайн-код: `текст` -> текст
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Убираем одиночные оставшиеся * и `
        text = text.replace('*', '').replace('`', '')

        self.ai_chat_window.configure(state="normal")
        self.ai_chat_window.insert("end", text)
        self.ai_chat_window.configure(state="disabled")
        self.ai_chat_window.see("end")

    def send_to_ai(self):
        user_message = self.ai_input.get().strip()
        if not user_message: return

        self.ai_input.delete(0, "end")

        # Вставляем текст пользователя обычным шрифтом
        self.ai_chat_window.configure(state="normal")
        self.ai_chat_window.insert("end", f"Вы: {user_message}\n\n")
        self.ai_chat_window.configure(state="disabled")
        self.ai_chat_window.see("end")

        self.btn_ai_send.configure(state="disabled", text="Анализ...")

        threading.Thread(target=self.request_openrouter, args=(user_message,), daemon=True).start()

    def request_openrouter(self, user_text):
        OPENROUTER_API_KEY = "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"
        # ИИ будет отдавать нормальный маркдаун с **жирным** текстом
        system_prompt = "Ты сетевой инженер-помощник для ISP. Отвечай кратко, структурированно, по пунктам. Без markdown-форматирования: не используй **, *, #, бэктики. Используй только обычный текст."
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openrouter/hunter-alpha",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            ai_response = response.json()['choices'][0]['message']['content']
        except Exception as e:
            ai_response = f"[Ошибка API]: {str(e)}"

        self.after(0, lambda: self.update_ai_chat(ai_response))

    def update_ai_chat(self, ai_text):
        self.ai_chat_window.configure(state="normal")
        self.ai_chat_window.insert("end", "ИИ-Инженер:\n")
        self.ai_chat_window.configure(state="disabled")

        # Пропускаем текст через наш парсер жирного шрифта
        self.insert_with_markdown(ai_text)

        self.ai_chat_window.configure(state="normal")
        self.ai_chat_window.insert("end", "\n" + "-" * 50 + "\n\n")
        self.ai_chat_window.configure(state="disabled")
        self.ai_chat_window.see("end")

        self.btn_ai_send.configure(state="normal", text="Отправить")


# ==========================================
# ОКНО АВТОРИЗАЦИИ
# ==========================================
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Авторизация - СКАТ")
        self.geometry("400x350")
        self.resizable(False, False)

        self.user_data = None
        database.create_default_admin()

        self.lbl_title = ctk.CTkLabel(self, text="Вход в систему", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(pady=(40, 20))

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Логин (admin)", width=250)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Пароль (admin)", width=250, show="*")
        self.entry_pass.pack(pady=10)

        self.btn_login = ctk.CTkButton(self, text="Войти в АРМ", width=250, command=self.check_login)
        self.btn_login.pack(pady=20)

    def check_login(self):
        user = database.verify_login(self.entry_user.get(), self.entry_pass.get())
        if user:
            self.user_data = user
            self.withdraw()  # Скрываем окно вместо quit
            self.quit()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()

    if login_app.user_data:
        operator_info = login_app.user_data
        try:
            login_app.destroy()
        except Exception:
            pass
        app = ISPAutomationSystem(operator_data=operator_info)
        app.mainloop()