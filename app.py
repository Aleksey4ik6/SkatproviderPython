import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import subprocess
import platform
import database
import requests
import time
import re
import json
import os
import sys
import tempfile
import io
import math
from PIL import Image, ImageTk
try:
    import webview
except Exception:
    webview = None

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
        self.selected_house_id = None
        self.selected_lat = None
        self.selected_lon = None
        self.map_webview_process = None
        self.map_webview_payload_path = os.path.join(tempfile.gettempdir(), "skat_network_map_payload.json")
        self.map_webview_payload_hash = ""
        self.map_webview_refresh_job = None
        if self.conn:
            self.ensure_geo_schema()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Боковое меню ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(13, weight=1)

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

        self.btn_chat = ctk.CTkButton(self.sidebar_frame, text="Чаты", fg_color="#5a2ea6", hover_color="#6f3ad1",
                                      command=lambda: self.select_frame("chat"))
        self.btn_chat.grid(row=8, column=0, padx=20, pady=10)

        self.btn_profile_360 = ctk.CTkButton(self.sidebar_frame, text="Клиент 360", fg_color="#3b5f8a",
                                             hover_color="#4d77aa", command=lambda: self.select_frame("customer360"))
        self.btn_profile_360.grid(row=9, column=0, padx=20, pady=10)

        self.btn_self_service = ctk.CTkButton(self.sidebar_frame, text="Заявки SS", fg_color="#2f7a5f",
                                              hover_color="#3a9a78", command=lambda: self.select_frame("self_service"))
        self.btn_self_service.grid(row=10, column=0, padx=20, pady=10)

        self.btn_network = ctk.CTkButton(self.sidebar_frame, text="Карта сети", fg_color="#4f6d4a",
                                         hover_color="#648b5d", command=lambda: self.select_frame("network_map"))
        self.btn_network.grid(row=11, column=0, padx=20, pady=10)

        self.btn_ai = ctk.CTkButton(self.sidebar_frame, text="ИИ Ассистент", fg_color="#4B0082", hover_color="#800080",
                                    command=lambda: self.select_frame("ai_assistant"))
        self.btn_ai.grid(row=12, column=0, padx=20, pady=20)

        # --- Основная область ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.frames = {}
        self.chat_poll_job = None
        self.customer_360_poll_job = None
        self.active_chat_customer_id = None
        self.chat_cache = []
        self.chat_selection_sync = False
        self.customers_rows = []
        self.complaints_rows = []
        self.bills_rows = []
        self.chat_customers_rows = []
        self.customer_360_rows = []
        self.self_service_rows = []
        self.network_nodes_rows = []
        self.network_incidents_rows = []
        self.create_dashboard_frame()
        self.create_customers_frame()
        self.create_plans_frame()
        self.create_complaints_frame()
        self.create_billing_frame()
        self.create_troubleshooting_frame()
        self.create_chat_frame()
        self.create_customer_360_frame()
        self.create_self_service_frame()
        self.create_network_map_frame()
        self.create_ai_frame()

        self.select_frame("dashboard")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.stop_chat_polling()
        self.stop_customer_360_polling()
        self._stop_webview_map_process()
        self.destroy()

    def open_modal(self, title, geometry="460x240"):
        modal = ctk.CTkToplevel(self)
        modal.title(title)
        modal.geometry(geometry)
        modal.resizable(False, False)
        modal.transient(self)
        modal.lift()
        modal.focus_force()
        modal.grab_set()
        try:
            modal.attributes("-topmost", True)
            modal.after(150, lambda: modal.attributes("-topmost", False))
        except Exception:
            pass
        return modal

    def prompt_single_line(self, title, label, initial=""):
        modal = self.open_modal(title, "520x180")
        result = {"value": None}
        box = ctk.CTkFrame(modal)
        box.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(box, text=label).pack(anchor="w", pady=(0, 6))
        entry = ctk.CTkEntry(box, height=36)
        entry.insert(0, initial or "")
        entry.pack(fill="x")
        entry.focus_set()

        actions = ctk.CTkFrame(box, fg_color="transparent")
        actions.pack(fill="x", pady=(12, 0))

        def submit():
            result["value"] = entry.get().strip()
            modal.destroy()

        ctk.CTkButton(actions, text="Сохранить", fg_color="#1f6aa5", command=submit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="Отмена", command=modal.destroy).pack(side="left")

        modal.wait_window()
        return result["value"]

    def select_frame(self, name):
        if name != "chat":
            self.stop_chat_polling()
        if name != "customer360":
            self.stop_customer_360_polling()
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
            elif name == "chat":
                self.load_chat_customers()
                self.start_chat_polling()
            elif name == "customer360":
                self.load_customer_360_customers()
                self.start_customer_360_polling()
            elif name == "self_service":
                self.load_self_service_requests()
            elif name == "network_map":
                self.load_network_map_data()

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
        self.btn_address_api = ctk.CTkButton(form_frame, text="API адрес", width=90, command=self.open_address_picker)
        self.btn_address_api.grid(row=0, column=3, padx=(0, 10), pady=10, sticky="ew")
        self.btn_bulk_geo = ctk.CTkButton(form_frame, text="Обновить старые адреса", width=150,
                                          command=self.backfill_customer_addresses)
        self.btn_bulk_geo.grid(row=1, column=3, padx=(0, 10), pady=10, sticky="ew")
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
        self.cust_addr_info = ctk.CTkLabel(form_frame, text="Адрес не выбран через API", text_color="gray")
        self.cust_addr_info.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        form_frame.grid_columnconfigure((0, 1, 2), weight=1)
        form_frame.grid_columnconfigure(3, weight=0)

        filter_frame = ctk.CTkFrame(frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        self.cust_filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Поиск: ФИО, адрес, телефон, IP, тариф")
        self.cust_filter_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.cust_filter_entry.bind("<KeyRelease>", lambda e: self.apply_customer_filter())
        ctk.CTkButton(filter_frame, text="Сброс", width=90,
                      command=lambda: [self.cust_filter_entry.delete(0, "end"), self.apply_customer_filter()]).pack(
            side="left", padx=(0, 10))

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
        self.customers_rows = cursor.fetchall()
        self.apply_customer_filter()
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
                "INSERT INTO customers (name, address, phone, email, ip_address, plan_id, registration_date, house_id, latitude, longitude) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (name, address, phone, email, ip_addr, plan_id, datetime.now(),
                 self.selected_house_id, self.selected_lat, self.selected_lon))
            customer_id = cursor.lastrowid
            self.conn.commit()
            cursor.close()
            self.log_customer_event(customer_id, "Профиль", f"Создан клиент {name}")
            self.selected_house_id = None
            self.selected_lat = None
            self.selected_lon = None
            self.cust_addr_info.configure(text="Адрес не выбран через API", text_color="gray")
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def ensure_geo_schema(self):
        cursor = self.conn.cursor()
        # City houses directory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS city_houses (
                house_id INT AUTO_INCREMENT PRIMARY KEY,
                city VARCHAR(80) NOT NULL DEFAULT 'Абакан',
                street VARCHAR(255),
                house_number VARCHAR(60),
                full_address VARCHAR(255) NOT NULL,
                latitude DECIMAL(10, 7),
                longitude DECIMAL(10, 7),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_city_houses_full_address (full_address),
                INDEX idx_city_houses_latlon (latitude, longitude)
            )
        """)
        # House incidents used by city map
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS house_incidents (
                incident_id INT AUTO_INCREMENT PRIMARY KEY,
                house_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                severity VARCHAR(20) NOT NULL DEFAULT 'Средняя',
                status VARCHAR(20) NOT NULL DEFAULT 'Активна',
                description TEXT,
                started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME,
                FOREIGN KEY (house_id) REFERENCES city_houses(house_id),
                INDEX idx_house_incidents_status (house_id, status),
                INDEX idx_house_incidents_started (started_at)
            )
        """)
        # Extend customers table if needed
        for sql in [
            "ALTER TABLE customers ADD COLUMN house_id INT NULL",
            "ALTER TABLE customers ADD COLUMN latitude DECIMAL(10, 7) NULL",
            "ALTER TABLE customers ADD COLUMN longitude DECIMAL(10, 7) NULL",
            "ALTER TABLE customers ADD INDEX idx_customers_house_id (house_id)",
        ]:
            try:
                cursor.execute(sql)
            except Exception:
                pass
        self.conn.commit()
        cursor.close()

    def open_address_picker(self):
        modal = self.open_modal("Подбор адреса (API)", "760x520")
        layout = ctk.CTkFrame(modal)
        layout.pack(fill="both", expand=True, padx=16, pady=16)
        layout.grid_columnconfigure(0, weight=1)
        layout.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(layout, text="Запрос адреса (например: Абакан, Ленина 12)").grid(row=0, column=0, sticky="w")
        query_entry = ctk.CTkEntry(layout, height=36)
        query_entry.insert(0, self.cust_address.get().strip() or "Абакан, ")
        query_entry.grid(row=1, column=0, sticky="ew", pady=(4, 8))

        results_tree = ttk.Treeview(layout, columns=("address", "lat", "lon"), show="headings")
        results_tree.heading("address", text="Адрес")
        results_tree.heading("lat", text="Lat")
        results_tree.heading("lon", text="Lon")
        results_tree.column("address", width=520)
        results_tree.column("lat", width=90)
        results_tree.column("lon", width=90)
        results_tree.grid(row=2, column=0, sticky="nsew")

        state = {"rows": []}

        def search():
            q = query_entry.get().strip()
            if not q:
                return
            try:
                rows = self.geocode_search(q, limit=15)
            except Exception as e:
                messagebox.showerror("API адресов", f"Ошибка запроса: {e}")
                return
            state["rows"] = rows
            for item in results_tree.get_children():
                results_tree.delete(item)
            for idx, r in enumerate(rows):
                address = r.get("display_name", "")
                lat = r.get("lat", "")
                lon = r.get("lon", "")
                results_tree.insert("", "end", iid=str(idx), values=(address[:180], lat, lon))

        def choose():
            sel = results_tree.selection()
            if not sel:
                messagebox.showinfo("Адрес", "Выберите адрес из списка.")
                return
            row = state["rows"][int(sel[0])]
            full_address = row.get("display_name", "").strip()
            lat = float(row.get("lat", 0) or 0)
            lon = float(row.get("lon", 0) or 0)
            house_id = self.upsert_city_house(full_address, lat, lon, row.get("address", {}))
            self.selected_house_id = house_id
            self.selected_lat = lat
            self.selected_lon = lon
            self.cust_address.delete(0, "end")
            self.cust_address.insert(0, full_address)
            self.cust_addr_info.configure(text=f"Дом #{house_id}, координаты: {lat:.5f}, {lon:.5f}", text_color="#7ecf9a")
            modal.destroy()

        actions = ctk.CTkFrame(layout, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ctk.CTkButton(actions, text="Найти", command=search).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="Выбрать адрес", fg_color="#1f6aa5", command=choose).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="Отмена", command=modal.destroy).pack(side="left")

    def geocode_search(self, query, limit=10):
        headers = {"User-Agent": "AlekseySkat-ISP/1.0 (desktop app)"}
        q = query.strip()
        if "абакан" not in q.lower():
            q = f"{q}, Абакан"
        params = {
            "q": q,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": limit,
            "countrycodes": "ru",
        }
        resp = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=12)
        resp.raise_for_status()
        return resp.json()

    def upsert_city_house(self, full_address, lat, lon, addr_meta):
        street = addr_meta.get("road") or addr_meta.get("street") or addr_meta.get("pedestrian") or ""
        house_number = addr_meta.get("house_number") or ""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO city_houses (city, street, house_number, full_address, latitude, longitude, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE street=VALUES(street), house_number=VALUES(house_number), latitude=VALUES(latitude), longitude=VALUES(longitude)",
            ("Абакан", street, house_number, full_address, lat, lon, datetime.now()))
        self.conn.commit()
        cursor.execute("SELECT house_id FROM city_houses WHERE full_address=%s", (full_address,))
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else None

    def backfill_customer_addresses(self):
        if not self.conn:
            return
        confirm = messagebox.askyesno("Нормализация адресов",
                                      "Обновить координаты/house_id для старых клиентов без геопривязки?\nЭто может занять время.")
        if not confirm:
            return
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT customer_id, address FROM customers WHERE (house_id IS NULL OR latitude IS NULL OR longitude IS NULL) AND address IS NOT NULL AND address != ''")
        rows = cursor.fetchall()
        cursor.close()
        if not rows:
            messagebox.showinfo("Нормализация", "Нет клиентов для обновления.")
            return

        progress = self.open_modal("Нормализация адресов", "640x420")
        box = ctk.CTkFrame(progress)
        box.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(box, text=f"Клиентов к обработке: {len(rows)}").pack(anchor="w", pady=(0, 8))
        log = ctk.CTkTextbox(box, height=280)
        log.pack(fill="both", expand=True)
        bar = ctk.CTkProgressBar(box)
        bar.pack(fill="x", pady=(8, 0))
        bar.set(0)
        progress.update()

        success = 0
        failed = 0
        for idx, r in enumerate(rows, start=1):
            cid = r["customer_id"]
            addr = (r["address"] or "").strip()
            try:
                found = self.geocode_search(addr, limit=1)
                if not found:
                    failed += 1
                    log.insert("end", f"[{idx}] CID {cid}: не найдено -> {addr}\n")
                else:
                    geo = found[0]
                    full_address = geo.get("display_name", addr)
                    lat = float(geo.get("lat"))
                    lon = float(geo.get("lon"))
                    house_id = self.upsert_city_house(full_address, lat, lon, geo.get("address", {}))
                    cur = self.conn.cursor()
                    cur.execute("UPDATE customers SET address=%s, house_id=%s, latitude=%s, longitude=%s WHERE customer_id=%s",
                                (full_address, house_id, lat, lon, cid))
                    self.conn.commit()
                    cur.close()
                    success += 1
                    log.insert("end", f"[{idx}] CID {cid}: OK -> house_id {house_id}\n")
                progress.update()
            except Exception as e:
                failed += 1
                log.insert("end", f"[{idx}] CID {cid}: ошибка -> {e}\n")
                progress.update()
            bar.set(idx / len(rows))
            progress.update()
            time.sleep(1.0)  # polite rate for Nominatim

        log.insert("end", f"\nГотово. Успешно: {success}, ошибок: {failed}\n")
        messagebox.showinfo("Нормализация завершена", f"Успешно: {success}\nОшибок: {failed}")
        progress.destroy()
        self.load_customers()
        self.load_network_map_data()

    def edit_customer_on_click(self, event):
        item_id = self.cust_tree.focus()
        if not item_id: return
        values = self.cust_tree.item(item_id)['values']
        customer_id, name, addr, phone, ip, plan = values

        # получаем email и plan_id из БД
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT email, plan_id FROM customers WHERE customer_id=%s", (customer_id,))
        row = cursor.fetchone() or {"email": "", "plan_id": None}
        cursor.close()

        cursor = self.conn.cursor()
        cursor.execute("SELECT plan_id, name FROM plans")
        plans = cursor.fetchall() or []
        cursor.close()

        modal = ctk.CTkToplevel(self)
        modal.title("Редактирование клиента")
        modal.geometry("520x360")
        modal.resizable(False, False)

        grid = ctk.CTkFrame(modal)
        grid.pack(fill="both", expand=True, padx=20, pady=20)
        labels = [("ФИО", name), ("Адрес", addr), ("Телефон", phone), ("Email", row["email"]), ("IP роутера", ip)]
        entries = []
        for idx, (label, value) in enumerate(labels):
            ctk.CTkLabel(grid, text=label).grid(row=idx, column=0, sticky="w", pady=5)
            ent = ctk.CTkEntry(grid, width=320)
            ent.insert(0, value or "")
            ent.grid(row=idx, column=1, sticky="ew", pady=5, padx=(10, 0))
            entries.append(ent)
        grid.grid_columnconfigure(1, weight=1)

        plan_values = [f"{p[0]} - {p[1]}" for p in plans] or ["Планы не заданы"]
        ctk.CTkLabel(grid, text="Тариф").grid(row=len(labels), column=0, sticky="w", pady=5)
        plan_combo = ctk.CTkComboBox(grid, values=plan_values, width=320)
        chosen = plan_values[0]
        if row.get("plan_id"):
            for pv in plan_values:
                if pv.startswith(f"{row['plan_id']} -"):
                    chosen = pv
                    break
        plan_combo.set(chosen)
        plan_combo.grid(row=len(labels), column=1, sticky="ew", pady=5, padx=(10, 0))

        def save():
            new_name, new_addr, new_phone, new_email, new_ip = [e.get().strip() for e in entries]
            plan_val = plan_combo.get()
            plan_id = int(plan_val.split(' - ')[0]) if ' - ' in plan_val else None
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "UPDATE customers SET name=%s, address=%s, phone=%s, email=%s, ip_address=%s, plan_id=%s WHERE customer_id=%s",
                    (new_name, new_addr, new_phone, new_email, new_ip, plan_id, customer_id))
                self.conn.commit()
                cursor.close()
                self.log_customer_event(customer_id, "Профиль", "Обновлены данные клиента")
                self.load_customers()
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        btn_row = ctk.CTkFrame(modal, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(10, 10))
        btn_row.grid_columnconfigure((0, 1), weight=1, uniform="btns")
        ctk.CTkButton(btn_row, text="Сохранить", fg_color="#1f6aa5", command=save).grid(row=0, column=0, padx=6)
        ctk.CTkButton(btn_row, text="Отмена", command=modal.destroy).grid(row=0, column=1, padx=6)

    def apply_customer_filter(self):
        query = (self.cust_filter_entry.get().strip().lower() if hasattr(self, "cust_filter_entry") else "")
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        for row in self.customers_rows:
            row_text = " ".join([str(x or "").lower() for x in row])
            if query and query not in row_text:
                continue
            self.cust_tree.insert('', 'end', values=row)

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
        self.plans_tree.bind("<Double-1>", self.edit_plan_on_click)
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

    def edit_plan_on_click(self, event):
        sel = self.plans_tree.selection()
        if not sel: return
        plan_id = self.plans_tree.item(sel[0])['values'][0]
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM plans WHERE plan_id=%s", (plan_id,))
        plan = cursor.fetchone()
        cursor.close()
        if not plan: return

        modal = ctk.CTkToplevel(self)
        modal.title("Редактирование тарифа")
        modal.geometry("480x360")
        modal.resizable(False, False)

        form = ctk.CTkFrame(modal)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        fields = [
            ("Название", "name"),
            ("Скорость", "speed"),
            ("Цена", "price"),
            ("Лимит данных", "data_limit"),
            ("Описание", "description"),
        ]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(form, text=label).grid(row=i, column=0, sticky="w", pady=5)
            ent = ctk.CTkEntry(form, width=320)
            ent.insert(0, plan.get(key) or "")
            ent.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
            entries[key] = ent
        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "UPDATE plans SET name=%s, speed=%s, price=%s, data_limit=%s, description=%s WHERE plan_id=%s",
                    (entries["name"].get(), entries["speed"].get(), float(entries["price"].get() or 0),
                     entries["data_limit"].get(), entries["description"].get(), plan_id)
                )
                self.conn.commit()
                cursor.close()
                self.load_plans()
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(pady=(0, 10))
        ctk.CTkButton(btns, text="Сохранить", fg_color="#1f6aa5", command=save, width=140).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Отмена", command=modal.destroy, width=120).pack(side="left")

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

        filter_frame = ctk.CTkFrame(frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        self.comp_filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Поиск: клиент, описание")
        self.comp_filter_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.comp_filter_entry.bind("<KeyRelease>", lambda e: self.apply_complaint_filter())
        self.comp_status_filter = ctk.CTkComboBox(filter_frame, values=["Все статусы", "Открыто", "В работе", "Решено"],
                                                  width=160, command=lambda _: self.apply_complaint_filter())
        self.comp_status_filter.set("Все статусы")
        self.comp_status_filter.pack(side="left", padx=(0, 10), pady=10)
        self.comp_date_filter = ctk.CTkComboBox(filter_frame, values=["Все даты", "Сегодня", "7 дней", "30 дней"],
                                                width=130, command=lambda _: self.apply_complaint_filter())
        self.comp_date_filter.set("Все даты")
        self.comp_date_filter.pack(side="left", padx=(0, 10), pady=10)

        columns = ('id', 'customer', 'desc', 'status', 'date')
        self.comp_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns: self.comp_tree.heading(col, text=col.upper())
        self.comp_tree.bind("<Double-1>", self.edit_complaint_on_click)
        self.comp_tree.pack(fill="both", expand=True)

    def load_complaints(self):
        if not self.conn: return
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id, name FROM customers")
        self.comp_cust.configure(values=[f"{c[0]} - {c[1]}" for c in cursor.fetchall()])
        cursor.execute(
            "SELECT co.complaint_id, c.name, co.description, co.status, co.date FROM complaints co JOIN customers c ON co.customer_id = c.customer_id")
        self.complaints_rows = cursor.fetchall()
        self.apply_complaint_filter()
        cursor.close()

    def add_complaint(self):
        if ' - ' not in self.comp_cust.get(): return
        cust_id = int(self.comp_cust.get().split(' - ')[0])
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO complaints (customer_id, description, status, date) VALUES (%s, %s, %s, %s)",
                       (cust_id, self.comp_desc.get(), 'Открыто', datetime.now()))
        complaint_id = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        self.log_customer_event(cust_id, "Обращение", f"Создан тикет #{complaint_id}: {self.comp_desc.get()[:120]}")
        self.load_complaints()

    def edit_complaint_on_click(self, event):
        sel = self.comp_tree.selection()
        if not sel: return
        values = self.comp_tree.item(sel[0])['values']
        comp_id, customer_name, desc, status, date = values

        modal = ctk.CTkToplevel(self)
        modal.title("Редактирование обращения")
        modal.geometry("520x320")
        modal.resizable(False, False)

        form = ctk.CTkFrame(modal)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(form, text=f"Клиент: {customer_name}").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ctk.CTkLabel(form, text="Описание").grid(row=1, column=0, sticky="nw", pady=5)
        desc_box = ctk.CTkTextbox(form, height=100, wrap="word")
        desc_box.insert("0.0", desc)
        desc_box.grid(row=1, column=1, sticky="nsew", pady=5, padx=(10, 0))

        ctk.CTkLabel(form, text="Статус").grid(row=2, column=0, sticky="w", pady=10)
        status_combo = ctk.CTkComboBox(form, values=["Открыто", "В работе", "Решено"], width=200)
        status_combo.set(status)
        status_combo.grid(row=2, column=1, sticky="w", pady=10, padx=(10, 0))

        form.grid_columnconfigure(1, weight=1)

        def save():
            new_desc = desc_box.get("0.0", "end").strip()
            new_status = status_combo.get()
            cursor = self.conn.cursor()
            cursor.execute("SELECT customer_id FROM complaints WHERE complaint_id=%s", (comp_id,))
            row = cursor.fetchone()
            customer_id = row[0] if row else None
            cursor.execute("UPDATE complaints SET description=%s, status=%s WHERE complaint_id=%s",
                           (new_desc, new_status, comp_id))
            self.conn.commit()
            cursor.close()
            self.log_customer_event(customer_id, "Обращение", f"Тикет #{comp_id} изменен, статус: {new_status}")
            self.load_complaints()
            modal.destroy()

        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(pady=(0, 10))
        ctk.CTkButton(btns, text="Сохранить", fg_color="#1f6aa5", command=save, width=140).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Отмена", command=modal.destroy, width=120).pack(side="left")

    def apply_complaint_filter(self):
        query = (self.comp_filter_entry.get().strip().lower() if hasattr(self, "comp_filter_entry") else "")
        status_filter = self.comp_status_filter.get() if hasattr(self, "comp_status_filter") else "Все статусы"
        date_filter = self.comp_date_filter.get() if hasattr(self, "comp_date_filter") else "Все даты"
        for item in self.comp_tree.get_children():
            self.comp_tree.delete(item)
        for row in self.complaints_rows:
            row_text = f"{row[1]} {row[2]}".lower()
            if query and query not in row_text:
                continue
            if status_filter != "Все статусы" and row[3] != status_filter:
                continue
            if not self._date_matches_period(row[4], date_filter):
                continue
            self.comp_tree.insert('', 'end', values=row)

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

        filter_frame = ctk.CTkFrame(frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        self.bill_filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Поиск: клиент, сумма, дата")
        self.bill_filter_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.bill_filter_entry.bind("<KeyRelease>", lambda e: self.apply_bill_filter())
        self.bill_status_filter = ctk.CTkComboBox(filter_frame, values=["Все", "Оплачен", "Долг"], width=140,
                                                  command=lambda _: self.apply_bill_filter())
        self.bill_status_filter.set("Все")
        self.bill_status_filter.pack(side="left", padx=(0, 10), pady=10)
        self.bill_date_filter = ctk.CTkComboBox(filter_frame,
                                                values=["Все даты", "Сегодня", "7 дней", "30 дней", "Просроченные"],
                                                width=150, command=lambda _: self.apply_bill_filter())
        self.bill_date_filter.set("Все даты")
        self.bill_date_filter.pack(side="left", padx=(0, 10), pady=10)

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
        self.bills_rows = cursor.fetchall()
        self.apply_bill_filter()
        cursor.close()

    def generate_bill(self):
        if ' - ' not in self.bill_cust.get(): return
        cust_id = int(self.bill_cust.get().split(' - ')[0])
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO billing (customer_id, amount, due_date, paid) VALUES (%s, %s, %s, 0)",
                       (cust_id, float(self.bill_amount.get()), datetime.now() + timedelta(days=30)))
        bill_id = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        self.log_customer_event(cust_id, "Счет", f"Выставлен счет #{bill_id} на {self.bill_amount.get()} ₽")
        self.load_bills()

    def mark_bill_paid(self):
        selected = self.bills_tree.selection()
        if not selected: return
        bill_id = self.bills_tree.item(selected[0])['values'][0]
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id FROM billing WHERE bill_id=%s", (bill_id,))
        row = cursor.fetchone()
        customer_id = row[0] if row else None
        cursor.execute("UPDATE billing SET paid = 1, payment_date = %s WHERE bill_id = %s", (datetime.now(), bill_id))
        self.conn.commit()
        cursor.close()
        self.log_customer_event(customer_id, "Счет", f"Счет #{bill_id} отмечен как оплаченный")
        self.load_bills()

    def apply_bill_filter(self):
        query = (self.bill_filter_entry.get().strip().lower() if hasattr(self, "bill_filter_entry") else "")
        status_filter = self.bill_status_filter.get() if hasattr(self, "bill_status_filter") else "Все"
        date_filter = self.bill_date_filter.get() if hasattr(self, "bill_date_filter") else "Все даты"
        today = datetime.now().date()
        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)
        for row in self.bills_rows:
            row_text = " ".join([str(x or "").lower() for x in row[1:]])
            if query and query not in row_text:
                continue
            if status_filter != "Все" and row[4] != status_filter:
                continue
            due_date = self._to_date(row[3])
            if date_filter == "Просроченные":
                if row[4] != "Долг" or not due_date or due_date >= today:
                    continue
            elif not self._date_matches_period(due_date, date_filter):
                continue
            self.bills_tree.insert('', 'end', values=row)

    def _to_date(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
            return value
        raw = str(value).strip()
        if not raw:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y", "%d.%m.%Y %H:%M:%S"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        return None

    def _to_datetime(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        as_date = self._to_date(value)
        if as_date:
            return datetime.combine(as_date, datetime.min.time())
        raw = str(value).strip()
        if not raw:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                parsed = datetime.strptime(raw, fmt)
                return parsed
            except ValueError:
                continue
        return None

    def _date_matches_period(self, value, period):
        if period == "Все даты":
            return True
        dt = self._to_date(value)
        if not dt:
            return False
        today = datetime.now().date()
        if period == "Сегодня":
            return dt == today
        if period == "7 дней":
            return dt >= (today - timedelta(days=7))
        if period == "30 дней":
            return dt >= (today - timedelta(days=30))
        return True

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

    # ==========================================
    # ЧАТ С КЛИЕНТАМИ
    # ==========================================
    def create_chat_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["chat"] = frame

        ctk.CTkLabel(frame, text="Чаты с клиентами", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w",
                                                                                                    pady=(0, 10))
        top_filter = ctk.CTkFrame(frame)
        top_filter.pack(fill="x", pady=(0, 8))
        self.chat_filter_entry = ctk.CTkEntry(top_filter, placeholder_text="Поиск клиента по имени или телефону")
        self.chat_filter_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.chat_filter_entry.bind("<KeyRelease>", lambda e: self.apply_chat_customer_filter())

        container = ctk.CTkFrame(frame)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Список клиентов слева
        self.chat_tree = ttk.Treeview(container, columns=('name', 'phone', 'unread'), show='headings', height=25)
        self.chat_tree.heading('name', text='Клиент')
        self.chat_tree.heading('phone', text='Телефон')
        self.chat_tree.heading('unread', text='Непр.')
        self.chat_tree.column('name', width=160)
        self.chat_tree.column('phone', width=110)
        self.chat_tree.column('unread', width=60, anchor='center')
        self.chat_tree.bind("<<TreeviewSelect>>", self.on_select_chat_customer)
        self.chat_tree.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=5)

        # Область переписки
        chat_panel = ctk.CTkFrame(container)
        chat_panel.grid(row=0, column=1, sticky="nsew")
        chat_panel.grid_rowconfigure(0, weight=1)
        chat_panel.grid_columnconfigure(0, weight=1)

        self.chat_messages_frame = ctk.CTkScrollableFrame(chat_panel, fg_color="#1f1f28")
        self.chat_messages_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        input_row = ctk.CTkFrame(chat_panel, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", padx=5, pady=(5, 10))
        input_row.grid_columnconfigure(0, weight=1)
        self.chat_entry = ctk.CTkEntry(input_row, placeholder_text="Сообщение клиенту...", height=38)
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        send_btn = ctk.CTkButton(input_row, text="Отправить", fg_color="#5a2ea6", command=self.send_chat_message)
        send_btn.grid(row=0, column=1)

        self.chat_hint = ctk.CTkLabel(self.chat_messages_frame, text="Выберите клиента слева", text_color="gray")
        self.chat_hint.pack(pady=10)

    def load_chat_customers(self):
        conn = database.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.customer_id, c.name, c.phone,
                   SUM(CASE WHEN m.is_read = 0 AND m.sender_type = 'client' THEN 1 ELSE 0 END) AS unread
            FROM customers c
            LEFT JOIN messages m ON c.customer_id = m.customer_id
            GROUP BY c.customer_id, c.name, c.phone
            ORDER BY unread DESC, c.name
        """)
        self.chat_customers_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        self.apply_chat_customer_filter()

    def on_select_chat_customer(self, event):
        if self.chat_selection_sync:
            return
        selection = self.chat_tree.selection()
        if not selection:
            return
        customer_id = int(selection[0])
        values = self.chat_tree.item(selection[0], "values")
        self.active_chat_customer_id = customer_id
        self.active_chat_name = values[0] if values else "Клиент"
        self.load_chat_messages()

    def load_chat_messages(self):
        if not self.active_chat_customer_id:
            return
        messages = database.fetch_messages(self.active_chat_customer_id)
        self.chat_cache = messages
        self.render_chat_messages(messages)
        database.mark_messages_read(self.active_chat_customer_id, "support")
        self.load_chat_customers()

    def render_chat_messages(self, messages):
        for widget in self.chat_messages_frame.winfo_children():
            widget.destroy()
        if not messages:
            self.chat_hint = ctk.CTkLabel(self.chat_messages_frame, text="Пока нет сообщений", text_color="gray")
            self.chat_hint.pack(pady=10)
            return
        for msg in messages:
            align = "e" if msg["sender_type"] == "support" else "w"
            bubble = ctk.CTkFrame(self.chat_messages_frame, fg_color="#4b4b5a" if msg["sender_type"] == "client" else "#5a2ea6", corner_radius=10)
            bubble.pack(fill="x", pady=4, padx=6, anchor=align)
            author = msg["sender_name"] or ("Клиент" if msg["sender_type"] == "client" else "Оператор")
            ctk.CTkLabel(bubble, text=author, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=8, pady=(6, 0))
            ctk.CTkLabel(bubble, text=msg["text"], wraplength=700, justify="left").pack(anchor="w", padx=8, pady=4)
            ts = msg["created_at"].strftime("%d.%m %H:%M") if isinstance(msg["created_at"], datetime) else str(msg["created_at"])
            ctk.CTkLabel(bubble, text=ts, text_color="lightgray", font=ctk.CTkFont(size=10)).pack(anchor="e", padx=8, pady=(0, 6))

    def send_chat_message(self):
        if not self.active_chat_customer_id:
            messagebox.showinfo("Нет клиента", "Выберите клиента слева.")
            return
        text = self.chat_entry.get().strip()
        if not text:
            return
        database.save_message(self.active_chat_customer_id, "support", text, self.operator.get("full_name"))
        self.log_customer_event(self.active_chat_customer_id, "Чат", f"Оператор отправил сообщение: {text[:120]}")
        self.chat_entry.delete(0, "end")
        self.load_chat_messages()

    def start_chat_polling(self):
        self.stop_chat_polling()
        def poll():
            if self.active_chat_customer_id:
                latest = database.fetch_messages(self.active_chat_customer_id)
                if len(latest) != len(self.chat_cache):
                    self.chat_cache = latest
                    self.render_chat_messages(latest)
                    database.mark_messages_read(self.active_chat_customer_id, "support")
                    self.load_chat_customers()
            self.chat_poll_job = self.after(3000, poll)
        self.chat_poll_job = self.after(3000, poll)

    def stop_chat_polling(self):
        if self.chat_poll_job:
            self.after_cancel(self.chat_poll_job)
            self.chat_poll_job = None

    def apply_chat_customer_filter(self):
        query = (self.chat_filter_entry.get().strip().lower() if hasattr(self, "chat_filter_entry") else "")
        for item in self.chat_tree.get_children():
            self.chat_tree.delete(item)
        selected_iid = None
        for row in self.chat_customers_rows:
            name = str(row.get("name") or "")
            phone = str(row.get("phone") or "")
            unread = row.get("unread") or 0
            if query and query not in f"{name} {phone}".lower():
                continue
            iid = str(row["customer_id"])
            self.chat_tree.insert('', 'end', iid=iid, values=(name, phone, unread))
            if self.active_chat_customer_id and str(self.active_chat_customer_id) == iid:
                selected_iid = iid
        if selected_iid:
            self.chat_selection_sync = True
            try:
                self.chat_tree.selection_set(selected_iid)
            finally:
                self.after(1, lambda: setattr(self, "chat_selection_sync", False))

    # ==========================================
    # КЛИЕНТ 360 (таймлайн)
    # ==========================================
    def create_customer_360_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["customer360"] = frame

        ctk.CTkLabel(frame, text="Клиент 360", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 10))

        filters = ctk.CTkFrame(frame)
        filters.pack(fill="x", pady=(0, 10))
        self.c360_customer_combo = ctk.CTkComboBox(filters, values=["Выберите клиента"], width=300,
                                                   command=lambda _: self.load_customer_360_timeline())
        self.c360_customer_combo.pack(side="left", padx=10, pady=10)
        self.c360_type_filter = ctk.CTkComboBox(filters,
                                                values=["Все события", "Счет", "Обращение", "Чат", "Диагностика", "Профиль"],
                                                width=160, command=lambda _: self.apply_customer_360_filter())
        self.c360_type_filter.set("Все события")
        self.c360_type_filter.pack(side="left", padx=(0, 10), pady=10)
        self.c360_period_filter = ctk.CTkComboBox(filters, values=["Все даты", "Сегодня", "7 дней", "30 дней"],
                                                  width=130, command=lambda _: self.apply_customer_360_filter())
        self.c360_period_filter.set("Все даты")
        self.c360_period_filter.pack(side="left", padx=(0, 10), pady=10)

        columns = ("date", "type", "details", "author")
        self.c360_tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.c360_tree.heading("date", text="Дата")
        self.c360_tree.heading("type", text="Тип")
        self.c360_tree.heading("details", text="Событие")
        self.c360_tree.heading("author", text="Кто")
        self.c360_tree.column("date", width=140, anchor="w")
        self.c360_tree.column("type", width=110, anchor="w")
        self.c360_tree.column("details", width=620, anchor="w")
        self.c360_tree.column("author", width=160, anchor="w")
        self.c360_tree.pack(fill="both", expand=True)

    def load_customer_360_customers(self):
        if not self.conn:
            return
        prev = self.c360_customer_combo.get() if hasattr(self, "c360_customer_combo") else ""
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id, name, phone FROM customers ORDER BY name")
        values = [f"{r[0]} - {r[1]} ({r[2]})" for r in cursor.fetchall()]
        cursor.close()
        self.c360_customer_combo.configure(values=values or ["Нет клиентов"])
        if values:
            if prev in values:
                self.c360_customer_combo.set(prev)
            else:
                self.c360_customer_combo.set(values[0])
            self.load_customer_360_timeline()

    def load_customer_360_timeline(self):
        cust_value = self.c360_customer_combo.get()
        if " - " not in cust_value:
            return
        customer_id = int(cust_value.split(" - ")[0])
        conn = database.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        events = []

        cursor.execute("SELECT registration_date, name FROM customers WHERE customer_id=%s", (customer_id,))
        c = cursor.fetchone()
        if c and c.get("registration_date"):
            events.append({
                "date": c["registration_date"],
                "type": "Профиль",
                "details": f"Создан клиент: {c.get('name', '')}",
                "author": "Система"
            })

        cursor.execute("SELECT bill_id, amount, due_date, paid, payment_date FROM billing WHERE customer_id=%s ORDER BY due_date DESC",
                       (customer_id,))
        for b in cursor.fetchall():
            events.append({
                "date": b.get("payment_date") or b.get("due_date"),
                "type": "Счет",
                "details": f"Счет #{b['bill_id']}: {b['amount']} ₽, срок {b['due_date']}, статус {'Оплачен' if b['paid'] else 'Долг'}",
                "author": "Биллинг"
            })

        cursor.execute("SELECT complaint_id, description, status, date FROM complaints WHERE customer_id=%s ORDER BY date DESC",
                       (customer_id,))
        for comp in cursor.fetchall():
            events.append({
                "date": comp.get("date"),
                "type": "Обращение",
                "details": f"Тикет #{comp['complaint_id']}: {comp['status']} | {comp['description']}",
                "author": "Поддержка"
            })

        cursor.execute("SELECT sender_type, sender_name, text, created_at FROM messages WHERE customer_id=%s ORDER BY created_at DESC",
                       (customer_id,))
        for m in cursor.fetchall():
            events.append({
                "date": m.get("created_at"),
                "type": "Чат",
                "details": (m.get("text") or "")[:180],
                "author": m.get("sender_name") or ("Клиент" if m.get("sender_type") == "client" else "Оператор")
            })

        try:
            cursor.execute(
                "SELECT event_time, event_type, details, actor FROM customer_events WHERE customer_id=%s ORDER BY event_time DESC",
                (customer_id,))
            for ev in cursor.fetchall():
                events.append({
                    "date": ev.get("event_time"),
                    "type": ev.get("event_type") or "Профиль",
                    "details": ev.get("details") or "",
                    "author": ev.get("actor") or "Оператор"
                })
        except Exception:
            pass

        cursor.close()
        conn.close()
        self.customer_360_rows = sorted(
            events,
            key=lambda x: self._to_datetime(x.get("date")) or datetime.min,
            reverse=True
        )
        self.apply_customer_360_filter()

    def apply_customer_360_filter(self):
        event_type = self.c360_type_filter.get() if hasattr(self, "c360_type_filter") else "Все события"
        period = self.c360_period_filter.get() if hasattr(self, "c360_period_filter") else "Все даты"
        for item in self.c360_tree.get_children():
            self.c360_tree.delete(item)
        for ev in self.customer_360_rows:
            if event_type != "Все события" and ev.get("type") != event_type:
                continue
            if not self._date_matches_period(ev.get("date"), period):
                continue
            dt = self._to_datetime(ev.get("date"))
            dt_text = dt.strftime("%d.%m.%Y %H:%M") if dt else str(ev.get("date") or "")
            self.c360_tree.insert("", "end", values=(dt_text, ev.get("type"), ev.get("details"), ev.get("author")))

    def start_customer_360_polling(self):
        self.stop_customer_360_polling()

        def poll():
            if "customer360" in self.frames and self.frames["customer360"].winfo_ismapped():
                self.load_customer_360_timeline()
            self.customer_360_poll_job = self.after(2500, poll)

        self.customer_360_poll_job = self.after(2500, poll)

    def stop_customer_360_polling(self):
        if self.customer_360_poll_job:
            self.after_cancel(self.customer_360_poll_job)
            self.customer_360_poll_job = None

    # ==========================================
    # ЗАЯВКИ SELF-SERVICE
    # ==========================================
    def create_self_service_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["self_service"] = frame

        ctk.CTkLabel(frame, text="Заявки Self-service", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w",
                                                                                                       pady=(0, 10))
        filters = ctk.CTkFrame(frame)
        filters.pack(fill="x", pady=(0, 10))
        self.ss_search = ctk.CTkEntry(filters, placeholder_text="Поиск: клиент, тип, payload")
        self.ss_search.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.ss_search.bind("<KeyRelease>", lambda e: self.apply_self_service_filter())
        self.ss_status = ctk.CTkComboBox(filters, values=["Все", "Новая", "В работе", "Выполнена", "Отклонена"],
                                         width=140, command=lambda _: self.apply_self_service_filter())
        self.ss_status.set("Все")
        self.ss_status.pack(side="left", padx=(0, 10), pady=10)

        columns = ("id", "date", "customer_id", "customer", "type", "payload", "status", "comment")
        self.ss_tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.ss_tree.heading("id", text="ID")
        self.ss_tree.heading("date", text="Дата")
        self.ss_tree.heading("customer_id", text="CID")
        self.ss_tree.heading("customer", text="Клиент")
        self.ss_tree.heading("type", text="Тип")
        self.ss_tree.heading("payload", text="Данные")
        self.ss_tree.heading("status", text="Статус")
        self.ss_tree.heading("comment", text="Комментарий")
        self.ss_tree.column("id", width=50)
        self.ss_tree.column("date", width=130)
        self.ss_tree.column("customer_id", width=60)
        self.ss_tree.column("customer", width=200)
        self.ss_tree.column("type", width=130)
        self.ss_tree.column("payload", width=320)
        self.ss_tree.column("status", width=100)
        self.ss_tree.column("comment", width=220)
        self.ss_tree.pack(fill="both", expand=True)

        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(actions, text="В работу", fg_color="#a66a00", command=self.ss_take_in_progress).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Выполнить", fg_color="#1f6a3a", command=self.ss_complete_request).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Отклонить", fg_color="#8b1a1a", command=self.ss_reject_request).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Обновить", command=self.load_self_service_requests).pack(side="left", padx=5)

    def load_self_service_requests(self):
        if not self.conn:
            return
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.request_id, r.customer_id, c.name AS customer_name, r.request_type, r.payload, r.status, r.comment, r.created_at
            FROM customer_self_service_requests r
            JOIN customers c ON c.customer_id = r.customer_id
            ORDER BY r.created_at DESC
        """)
        self.self_service_rows = cursor.fetchall()
        cursor.close()
        self.apply_self_service_filter()

    def apply_self_service_filter(self):
        query = self.ss_search.get().strip().lower() if hasattr(self, "ss_search") else ""
        status = self.ss_status.get() if hasattr(self, "ss_status") else "Все"
        for item in self.ss_tree.get_children():
            self.ss_tree.delete(item)
        for row in self.self_service_rows:
            if status != "Все" and row.get("status") != status:
                continue
            row_text = f"{row.get('customer_name', '')} {row.get('request_type', '')} {row.get('payload', '')}".lower()
            if query and query not in row_text:
                continue
            created = row.get("created_at")
            created_text = created.strftime("%d.%m %H:%M") if isinstance(created, datetime) else str(created)
            self.ss_tree.insert("", "end", values=(
                row.get("request_id"),
                created_text,
                row.get("customer_id"),
                row.get("customer_name"),
                row.get("request_type"),
                (row.get("payload") or "")[:120],
                row.get("status"),
                row.get("comment") or ""
            ))

    def ss_get_selected_request_id(self):
        selected = self.ss_tree.selection()
        if not selected:
            messagebox.showinfo("Заявка", "Выберите заявку в таблице.")
            return None
        return int(self.ss_tree.item(selected[0])["values"][0])

    def ss_take_in_progress(self):
        req_id = self.ss_get_selected_request_id()
        if not req_id:
            return
        self.update_self_service_status(req_id, "В работе")

    def ss_complete_request(self):
        req_id = self.ss_get_selected_request_id()
        if not req_id:
            return
        comment = self.prompt_single_line("Выполнение заявки", "Комментарий для клиента:", "Заявка выполнена")
        if comment is None:
            return
        self.process_self_service_request(req_id, comment or "Заявка выполнена")

    def ss_reject_request(self):
        req_id = self.ss_get_selected_request_id()
        if not req_id:
            return
        comment = self.prompt_single_line("Отклонение заявки", "Укажите причину отказа:", "Недостаточно данных")
        if comment is None or not comment.strip():
            return
        self.update_self_service_status(req_id, "Отклонена", comment=comment)

    def update_self_service_status(self, request_id, new_status, comment=None):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT request_id, customer_id, request_type FROM customer_self_service_requests WHERE request_id=%s",
                       (request_id,))
        req = cursor.fetchone()
        if not req:
            cursor.close()
            return
        cursor.execute(
            "UPDATE customer_self_service_requests SET status=%s, comment=%s, processed_at=%s WHERE request_id=%s",
            (new_status, comment, datetime.now(), request_id))
        self.conn.commit()
        cursor.close()
        self.log_customer_event(req["customer_id"], "Профиль",
                                f"Self-service #{request_id}: статус '{new_status}' ({req['request_type']})")
        self.load_self_service_requests()
        if hasattr(self, "c360_customer_combo"):
            self.load_customer_360_timeline()

    def process_self_service_request(self, request_id, comment):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer_self_service_requests WHERE request_id=%s", (request_id,))
        req = cursor.fetchone()
        if not req:
            cursor.close()
            return
        payload = {}
        try:
            payload = json.loads(req.get("payload") or "{}")
        except Exception:
            payload = {}

        customer_id = req["customer_id"]
        rtype = req["request_type"]

        try:
            if rtype == "promised_payment":
                days = int(payload.get("days", 5))
                cursor.execute(
                    "UPDATE billing SET due_date = DATE_ADD(due_date, INTERVAL %s DAY) WHERE customer_id=%s AND paid=0",
                    (days, customer_id))
                cursor.execute(
                    "INSERT INTO customer_promised_payments (customer_id, amount, delay_days, approved_at, approved_by) VALUES (%s, %s, %s, %s, %s)",
                    (customer_id, float(payload.get("amount", 0) or 0), days, datetime.now(), self.operator.get("full_name")))
            elif rtype == "plan_change":
                plan_id = int(payload.get("target_plan_id")) if payload.get("target_plan_id") else None
                if not plan_id:
                    raise ValueError("Не указан target_plan_id")
                cursor.execute("UPDATE customers SET plan_id=%s WHERE customer_id=%s", (plan_id, customer_id))
            elif rtype == "addon":
                service = str(payload.get("service") or "").strip()
                if not service:
                    raise ValueError("Не указано название услуги")
                cursor.execute(
                    "INSERT INTO customer_addons (customer_id, service_name, status, created_at, activated_at) VALUES (%s, %s, %s, %s, %s)",
                    (customer_id, service, "Активна", datetime.now(), datetime.now()))
            elif rtype == "autopay":
                enabled = int(payload.get("enabled", 0))
                cursor.execute(
                    "INSERT INTO customer_autopay_settings (customer_id, enabled, updated_at) VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE enabled=VALUES(enabled), updated_at=VALUES(updated_at)",
                    (customer_id, enabled, datetime.now()))

            cursor.execute(
                "UPDATE customer_self_service_requests SET status=%s, comment=%s, processed_at=%s WHERE request_id=%s",
                ("Выполнена", comment, datetime.now(), request_id))
            self.conn.commit()
            self.log_customer_event(customer_id, "Профиль", f"Self-service #{request_id} выполнена ({rtype})")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка обработки", str(e))
        finally:
            cursor.close()
        self.load_self_service_requests()
        if hasattr(self, "c360_customer_combo"):
            self.load_customer_360_timeline()

    # ==========================================
    # КАРТА СЕТИ / АВАРИИ
    # ==========================================
    def create_network_map_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["network_map"] = frame

        ctk.CTkLabel(frame, text="Карта аварий и узлов", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w",
                                                                                                        pady=(0, 10))

        top = ctk.CTkFrame(frame)
        top.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(top, text="Добавить узел", command=self.add_network_node).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="Новая авария", fg_color="#8b1a1a", command=self.create_network_incident).pack(
            side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="Закрыть аварию", fg_color="#1f6a3a", command=self.resolve_network_incident).pack(
            side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="Назначить клиента к узлу", command=self.assign_customer_to_node).pack(
            side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="Обновить", command=self.load_network_map_data).pack(side="left", padx=6, pady=8)

        content = ctk.CTkFrame(frame)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(1, weight=1)

        self.network_nodes_tree = ttk.Treeview(content, columns=("id", "name", "type", "location", "status"), show="headings", height=8)
        for col, title, width in [("id", "ID", 50), ("name", "Узел", 180), ("type", "Тип", 110), ("location", "Локация", 180), ("status", "Статус", 90)]:
            self.network_nodes_tree.heading(col, text=title)
            self.network_nodes_tree.column(col, width=width)
        self.network_nodes_tree.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        self.network_nodes_tree.bind("<<TreeviewSelect>>", self.on_select_network_node)

        self.network_incidents_tree = ttk.Treeview(content, columns=("id", "node", "title", "desc", "severity", "status", "started"), show="headings", height=8)
        for col, title, width in [("id", "ID", 50), ("node", "Узел", 120), ("title", "Авария", 180), ("desc", "Описание", 220), ("severity", "Критич.", 90), ("status", "Статус", 90), ("started", "Начало", 130)]:
            self.network_incidents_tree.heading(col, text=title)
            self.network_incidents_tree.column(col, width=width)
        self.network_incidents_tree.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 6))

        self.network_canvas = ctk.CTkCanvas(content, bg="#10151d", highlightthickness=0, height=340)
        self.network_canvas.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(6, 0))

        right_bottom = ctk.CTkFrame(content)
        right_bottom.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(6, 0))
        right_bottom.grid_rowconfigure(1, weight=1)
        right_bottom.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right_bottom, text="Зона влияния (затронутые клиенты)",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        self.network_affected_tree = ttk.Treeview(right_bottom, columns=("id", "name", "phone"), show="headings")
        self.network_affected_tree.heading("id", text="CID")
        self.network_affected_tree.heading("name", text="Клиент")
        self.network_affected_tree.heading("phone", text="Телефон")
        self.network_affected_tree.column("id", width=60)
        self.network_affected_tree.column("name", width=220)
        self.network_affected_tree.column("phone", width=140)
        self.network_affected_tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def load_network_map_data(self):
        if not self.conn:
            return
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT node_id, name, node_type, location, x_pos, y_pos, status FROM network_nodes ORDER BY node_id")
        self.network_nodes_rows = cursor.fetchall()
        cursor.execute(
            "SELECT i.incident_id, i.node_id, n.name as node_name, i.title, i.description, i.severity, i.status, i.started_at "
            "FROM network_incidents i JOIN network_nodes n ON n.node_id = i.node_id ORDER BY i.started_at DESC")
        self.network_incidents_rows = cursor.fetchall()
        cursor.close()
        self.render_network_nodes()
        self.render_network_incidents()
        if self.network_canvas is not None:
            self.schedule_network_map_draw(30)
        elif hasattr(self, "network_map_hint"):
            houses = len(self.network_nodes_rows)
            incidents = sum(int(r.get("active_incidents") or 0) for r in self.network_nodes_rows)
            self.network_map_hint.configure(text=f"Домов на карте: {houses}. Активных аварий: {incidents}.")
        self.sync_webview_map_window()
        self.load_affected_customers()

    def render_network_nodes(self):
        for item in self.network_nodes_tree.get_children():
            self.network_nodes_tree.delete(item)
        for row in self.network_nodes_rows:
            self.network_nodes_tree.insert("", "end", iid=str(row["node_id"]),
                                           values=(row["node_id"], row["name"], row["node_type"], row["location"], row["status"]))

    def render_network_incidents(self):
        for item in self.network_incidents_tree.get_children():
            self.network_incidents_tree.delete(item)
        for row in self.network_incidents_rows:
            started = row["started_at"].strftime("%d.%m %H:%M") if isinstance(row["started_at"], datetime) else str(row["started_at"])
            self.network_incidents_tree.insert("", "end", iid=str(row["incident_id"]),
                                               values=(row["incident_id"], row["node_name"], row["title"],
                                                       (row.get("description") or "")[:100], row["severity"], row["status"], started))

    def draw_network_canvas(self):
        self.network_canvas.delete("all")
        if not self.network_nodes_rows:
            self.network_canvas.create_text(220, 160, text="Узлы не добавлены", fill="#8899aa", font=("Segoe UI", 13))
            return
        node_map = {r["node_id"]: r for r in self.network_nodes_rows}
        active_inc_nodes = {r["node_id"] for r in self.network_incidents_rows if r["status"] == "Активна"}
        for i, row in enumerate(self.network_nodes_rows):
            x = row["x_pos"] if row["x_pos"] else 80 + (i % 4) * 120
            y = row["y_pos"] if row["y_pos"] else 70 + (i // 4) * 100
            node_map[row["node_id"]]["_x"] = x
            node_map[row["node_id"]]["_y"] = y

        # Light topology lines by id order to keep view readable.
        ids = [r["node_id"] for r in self.network_nodes_rows]
        for idx in range(1, len(ids)):
            a = node_map[ids[idx - 1]]
            b = node_map[ids[idx]]
            self.network_canvas.create_line(a["_x"], a["_y"], b["_x"], b["_y"], fill="#2e3d52", width=2)

        for row in self.network_nodes_rows:
            x, y = row["_x"], row["_y"]
            color = "#d34a4a" if (row["node_id"] in active_inc_nodes or row["status"] == "DOWN") else "#3da96a"
            self.network_canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline="#d9e1ea")
            self.network_canvas.create_text(x, y + 30, text=f"{row['name']} ({row['node_id']})", fill="#d4dde7",
                                            font=("Segoe UI", 9))

    def on_select_network_node(self, _event=None):
        self.load_affected_customers()

    def load_affected_customers(self):
        for item in self.network_affected_tree.get_children():
            self.network_affected_tree.delete(item)
        sel = self.network_nodes_tree.selection()
        if not sel:
            return
        node_id = int(sel[0])
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT c.customer_id, c.name, c.phone "
            "FROM customer_node_links l JOIN customers c ON c.customer_id=l.customer_id "
            "WHERE l.node_id=%s ORDER BY c.name", (node_id,))
        for row in cursor.fetchall():
            self.network_affected_tree.insert("", "end", values=row)
        cursor.close()

    def add_network_node(self):
        modal = self.open_modal("Новый узел", "520x280")
        result = {"ok": False, "name": "", "type": "Роутер", "location": ""}
        box = ctk.CTkFrame(modal)
        box.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(box, text="Название узла").pack(anchor="w")
        name_entry = ctk.CTkEntry(box, height=34)
        name_entry.pack(fill="x", pady=(4, 8))
        ctk.CTkLabel(box, text="Тип узла").pack(anchor="w")
        type_combo = ctk.CTkComboBox(box, values=["Роутер", "Коммутатор", "БС", "OLT", "Маршрутизатор"], height=34)
        type_combo.set("Роутер")
        type_combo.pack(fill="x", pady=(4, 8))
        ctk.CTkLabel(box, text="Локация").pack(anchor="w")
        loc_entry = ctk.CTkEntry(box, height=34)
        loc_entry.insert(0, "Центральный узел")
        loc_entry.pack(fill="x", pady=(4, 12))

        actions = ctk.CTkFrame(box, fg_color="transparent")
        actions.pack(fill="x")
        def submit():
            result["name"] = name_entry.get().strip()
            result["type"] = type_combo.get().strip() or "Роутер"
            result["location"] = loc_entry.get().strip()
            result["ok"] = bool(result["name"])
            modal.destroy()
        ctk.CTkButton(actions, text="Создать", fg_color="#1f6aa5", command=submit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="Отмена", command=modal.destroy).pack(side="left")
        modal.wait_window()
        if not result["ok"]:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO network_nodes (name, node_type, location, status, created_at) VALUES (%s, %s, %s, %s, %s)",
            (result["name"], result["type"], result["location"], "OK", datetime.now()))
        self.conn.commit()
        cursor.close()
        self.load_network_map_data()

    def create_network_incident(self):
        sel = self.network_nodes_tree.selection()
        if not sel:
            messagebox.showinfo("Авария", "Сначала выберите узел.")
            return
        node_id = int(sel[0])
        modal = self.open_modal("Новая авария", "560x430")
        result = {"ok": False, "title": "", "severity": "Средняя", "desc": ""}
        body = ctk.CTkFrame(modal)
        body.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        body.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(body, text=f"Узел ID: {node_id}").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ctk.CTkLabel(body, text="Название аварии").grid(row=1, column=0, sticky="w")
        title_entry = ctk.CTkEntry(body, height=34)
        title_entry.insert(0, "Потеря связи")
        title_entry.grid(row=2, column=0, sticky="ew", pady=(4, 8))
        ctk.CTkLabel(body, text="Критичность").grid(row=3, column=0, sticky="w")
        severity_combo = ctk.CTkComboBox(body, values=["Низкая", "Средняя", "Высокая", "Критическая"], height=34)
        severity_combo.set("Средняя")
        severity_combo.grid(row=4, column=0, sticky="ew", pady=(4, 8))
        ctk.CTkLabel(body, text="Описание").grid(row=5, column=0, sticky="w")
        desc_entry = ctk.CTkTextbox(body, height=120)
        desc_entry.grid(row=6, column=0, sticky="nsew", pady=(4, 8))
        body.grid_rowconfigure(6, weight=1)

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=16, pady=(0, 14))
        def submit():
            result["title"] = title_entry.get().strip()
            result["severity"] = severity_combo.get().strip() or "Средняя"
            result["desc"] = desc_entry.get("0.0", "end").strip()
            result["ok"] = bool(result["title"])
            modal.destroy()
        ctk.CTkButton(actions, text="Создать аварию", fg_color="#8b1a1a", command=submit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="Отмена", command=modal.destroy).pack(side="left")
        modal.wait_window()
        if not result["ok"]:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO network_incidents (node_id, title, severity, status, description, started_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (node_id, result["title"], result["severity"], "Активна", result["desc"] or "", datetime.now()))
        cursor.execute("UPDATE network_nodes SET status='DOWN' WHERE node_id=%s", (node_id,))
        self.conn.commit()
        cursor.close()
        self.log_node_affected_customers(node_id, f"Авария: {result['title']}. {result['desc'][:80]}")
        self.load_network_map_data()

    def resolve_network_incident(self):
        sel = self.network_incidents_tree.selection()
        if not sel:
            messagebox.showinfo("Авария", "Выберите инцидент в таблице.")
            return
        incident_id = int(sel[0])
        comment = self.prompt_single_line("Закрытие аварии", "Комментарий при закрытии:", "Восстановлено")
        if comment is None:
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT node_id, title FROM network_incidents WHERE incident_id=%s", (incident_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return
        node_id, title = row[0], row[1]
        cursor.execute(
            "UPDATE network_incidents SET status='Закрыта', resolved_at=%s, description=CONCAT(IFNULL(description,''), %s) WHERE incident_id=%s",
            (datetime.now(), f"\n[Закрытие] {comment or ''}", incident_id))
        cursor.execute(
            "UPDATE network_nodes n SET status=CASE WHEN EXISTS (SELECT 1 FROM network_incidents i WHERE i.node_id=n.node_id AND i.status='Активна') THEN 'DOWN' ELSE 'OK' END WHERE n.node_id=%s",
            (node_id,))
        self.conn.commit()
        cursor.close()
        self.log_node_affected_customers(node_id, f"Авария закрыта: {title}")
        self.load_network_map_data()

    def assign_customer_to_node(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id, name FROM customers ORDER BY name")
        customers = cursor.fetchall()
        cursor.execute("SELECT node_id, name FROM network_nodes ORDER BY name")
        nodes = cursor.fetchall()
        cursor.close()
        if not customers or not nodes:
            messagebox.showwarning("Привязка", "Нужны клиенты и узлы.")
            return

        modal = self.open_modal("Привязка клиента к узлу", "420x220")
        box = ctk.CTkFrame(modal)
        box.pack(fill="both", expand=True, padx=20, pady=20)

        c_vals = [f"{c[0]} - {c[1]}" for c in customers]
        n_vals = [f"{n[0]} - {n[1]}" for n in nodes]
        ctk.CTkLabel(box, text="Клиент").pack(anchor="w")
        c_combo = ctk.CTkComboBox(box, values=c_vals, width=360)
        c_combo.set(c_vals[0])
        c_combo.pack(pady=(0, 10))
        ctk.CTkLabel(box, text="Узел").pack(anchor="w")
        n_combo = ctk.CTkComboBox(box, values=n_vals, width=360)
        n_combo.set(n_vals[0])
        n_combo.pack(pady=(0, 12))

        def submit():
            cust_id = int(c_combo.get().split(" - ")[0])
            node_id = int(n_combo.get().split(" - ")[0])
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO customer_node_links (customer_id, node_id, linked_at) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE node_id=VALUES(node_id), linked_at=VALUES(linked_at)",
                (cust_id, node_id, datetime.now()))
            self.conn.commit()
            cur.close()
            self.log_customer_event(cust_id, "Профиль", f"Клиент привязан к узлу #{node_id}")
            modal.destroy()
            self.load_network_map_data()

        ctk.CTkButton(box, text="Сохранить", fg_color="#1f6aa5", command=submit).pack(side="left", padx=4)
        ctk.CTkButton(box, text="Отмена", command=modal.destroy).pack(side="left", padx=4)

    def log_node_affected_customers(self, node_id, details):
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id FROM customer_node_links WHERE node_id=%s", (node_id,))
        customer_ids = [r[0] for r in cursor.fetchall()]
        cursor.close()
        for cid in customer_ids:
            self.log_customer_event(cid, "Диагностика", details)

    # ---- New city-house based map (overrides node-based methods above) ----
    def create_network_map_frame(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["network_map"] = frame
        self.network_map_zoom = 13
        self.network_map_center = None
        self.network_map_photo = None
        self.network_map_last_params = None
        self.network_map_resize_job = None
        self.network_map_draw_job = None
        self.network_map_drag_last = None
        self.network_map_drag_accum_dx = 0
        self.network_map_drag_accum_dy = 0
        self.network_map_image_cache = {}
        self.network_map_loading = False
        self.network_map_pending_request = None
        self.network_map_current_key = None
        self.network_map_last_render_key = None

        ctk.CTkLabel(frame, text="\u041a\u0430\u0440\u0442\u0430 \u0430\u0432\u0430\u0440\u0438\u0439 \u043f\u043e \u0410\u0431\u0430\u043a\u0430\u043d\u0443", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w",
                                                                                                           pady=(0, 10))
        top = ctk.CTkFrame(frame)
        top.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(top, text="\u0426\u0435\u043d\u0442\u0440: \u0410\u0431\u0430\u043a\u0430\u043d", fg_color="#1f6aa5", command=self.center_map_to_abakan).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="\u0426\u0435\u043d\u0442\u0440: \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0439 \u0434\u043e\u043c", fg_color="#31465d", command=self.center_map_to_selected_house).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="-", width=34, command=lambda: self.change_network_map_zoom(-1)).pack(side="left", padx=(12, 4), pady=8)
        ctk.CTkButton(top, text="+", width=34, command=lambda: self.change_network_map_zoom(1)).pack(side="left", padx=4, pady=8)
        self.network_zoom_label = ctk.CTkLabel(top, text="\u041c\u0430\u0441\u0448\u0442\u0430\u0431: 13", text_color="#9eb4ca")
        self.network_zoom_label.pack(side="left", padx=(8, 0))
        self.network_map_search_entry = ctk.CTkEntry(top, width=250, placeholder_text="Поиск адреса на карте")
        self.network_map_search_entry.pack(side="left", padx=(12, 6), pady=8)
        self.network_map_search_entry.bind("<Return>", lambda _e: self.focus_map_on_address())
        self.network_map_search_btn = ctk.CTkButton(top, text="Найти адрес", width=110, fg_color="#345b7e", command=self.focus_map_on_address)
        self.network_map_search_btn.pack(side="left", padx=(0, 6), pady=8)
        ctk.CTkButton(top, text="\u041d\u043e\u0432\u0430\u044f \u0430\u0432\u0430\u0440\u0438\u044f \u043f\u043e \u0434\u043e\u043c\u0443", fg_color="#8b1a1a", command=self.create_network_incident).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="\u0417\u0430\u043a\u0440\u044b\u0442\u044c \u0430\u0432\u0430\u0440\u0438\u044e", fg_color="#1f6a3a", command=self.resolve_network_incident).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(top, text="\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c", command=self.load_network_map_data).pack(side="left", padx=6, pady=8)

        content = ctk.CTkFrame(frame)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(1, weight=1)

        self.network_nodes_tree = ttk.Treeview(content, columns=("house_id", "address", "clients", "active", "status"), show="headings", height=9)
        for col, title, width in [
            ("house_id", "\u0414\u043e\u043c ID", 70),
            ("address", "\u0410\u0434\u0440\u0435\u0441", 340),
            ("clients", "\u041a\u043b\u0438\u0435\u043d\u0442\u043e\u0432", 90),
            ("active", "\u0410\u0432\u0430\u0440\u0438\u0439", 80),
            ("status", "\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435", 100),
        ]:
            self.network_nodes_tree.heading(col, text=title)
            self.network_nodes_tree.column(col, width=width)
        self.network_nodes_tree.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        self.network_nodes_tree.bind("<<TreeviewSelect>>", self.on_select_network_node)

        self.network_incidents_tree = ttk.Treeview(content, columns=("id", "house", "title", "desc", "severity", "status", "clients", "started"), show="headings", height=9)
        for col, title, width in [
            ("id", "ID", 50),
            ("house", "\u0414\u043e\u043c", 90),
            ("title", "\u0410\u0432\u0430\u0440\u0438\u044f", 170),
            ("desc", "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435", 220),
            ("severity", "\u041a\u0440\u0438\u0442\u0438\u0447.", 90),
            ("status", "\u0421\u0442\u0430\u0442\u0443\u0441", 90),
            ("clients", "\u041a\u043b\u0438\u0435\u043d\u0442\u043e\u0432", 90),
            ("started", "\u041d\u0430\u0447\u0430\u043b\u043e", 130),
        ]:
            self.network_incidents_tree.heading(col, text=title)
            self.network_incidents_tree.column(col, width=width)
        self.network_incidents_tree.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 6))

        self.network_map_host = ctk.CTkFrame(content, fg_color="#10151d", corner_radius=8)
        self.network_map_host.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(6, 0))
        self.network_map_host.grid_columnconfigure(0, weight=1)
        self.network_map_host.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.network_map_host, text="Интерактивная карта WebView", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 6))
        self.network_map_hint = ctk.CTkLabel(
            self.network_map_host,
            text="Карта открывается в отдельном окне: плавный drag/zoom и поиск адреса.",
            text_color="#9eb4ca",
        )
        self.network_map_hint.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))
        map_btns = ctk.CTkFrame(self.network_map_host, fg_color="transparent")
        map_btns.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 12))
        ctk.CTkButton(map_btns, text="Открыть карту", fg_color="#1f6aa5", command=self.open_webview_map).pack(side="left", padx=(0, 8))
        self.network_canvas = None

        right_bottom = ctk.CTkFrame(content)
        right_bottom.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(6, 0))
        right_bottom.grid_rowconfigure(1, weight=1)
        right_bottom.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right_bottom, text="\u0417\u043e\u043d\u0430 \u0432\u043b\u0438\u044f\u043d\u0438\u044f (\u043a\u043b\u0438\u0435\u043d\u0442\u044b \u0434\u043e\u043c\u0430)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        self.network_affected_tree = ttk.Treeview(right_bottom, columns=("id", "name", "phone"), show="headings")
        self.network_affected_tree.heading("id", text="CID")
        self.network_affected_tree.heading("name", text="\u041a\u043b\u0438\u0435\u043d\u0442")
        self.network_affected_tree.heading("phone", text="\u0422\u0435\u043b\u0435\u0444\u043e\u043d")
        self.network_affected_tree.column("id", width=60)
        self.network_affected_tree.column("name", width=220)
        self.network_affected_tree.column("phone", width=140)
        self.network_affected_tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def load_network_map_data(self):
        if not self.conn:
            return
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT h.house_id, h.full_address, h.latitude, h.longitude,
                   COUNT(c.customer_id) AS clients_count,
                   SUM(CASE WHEN i.status='Активна' THEN 1 ELSE 0 END) AS active_incidents
            FROM city_houses h
            LEFT JOIN customers c ON c.house_id = h.house_id
            LEFT JOIN house_incidents i ON i.house_id = h.house_id
            GROUP BY h.house_id, h.full_address, h.latitude, h.longitude
            ORDER BY clients_count DESC, h.full_address
        """)
        self.network_nodes_rows = cursor.fetchall()
        cursor.execute("""
            SELECT i.incident_id, i.house_id, i.title, i.description, i.severity, i.status, i.started_at,
                   (SELECT COUNT(*) FROM customers c WHERE c.house_id=i.house_id) AS affected_clients
            FROM house_incidents i
            ORDER BY i.started_at DESC
        """)
        self.network_incidents_rows = cursor.fetchall()
        cursor.close()
        self.render_network_nodes()
        self.render_network_incidents()
        self.draw_network_canvas()
        self.load_affected_customers()

    def render_network_nodes(self):
        for item in self.network_nodes_tree.get_children():
            self.network_nodes_tree.delete(item)
        for row in self.network_nodes_rows:
            active = int(row.get("active_incidents") or 0)
            status = "АВАРИЯ" if active > 0 else "OK"
            self.network_nodes_tree.insert("", "end", iid=str(row["house_id"]),
                                           values=(row["house_id"], row["full_address"][:90], row.get("clients_count") or 0, active, status))

    def render_network_incidents(self):
        for item in self.network_incidents_tree.get_children():
            self.network_incidents_tree.delete(item)
        for row in self.network_incidents_rows:
            started = row["started_at"].strftime("%d.%m %H:%M") if isinstance(row["started_at"], datetime) else str(row["started_at"])
            self.network_incidents_tree.insert("", "end", iid=str(row["incident_id"]),
                                               values=(row["incident_id"], row["house_id"], row["title"][:80], (row.get("description") or "")[:100], row["severity"],
                                                       row["status"], row.get("affected_clients") or 0, started))

    def on_select_network_node(self, _event=None):
        self.load_affected_customers()

    def on_network_canvas_enter(self, _event=None):
        if self.network_canvas is None:
            return
        try:
            self.network_canvas.focus_set()
        except Exception:
            pass

    def on_network_canvas_resize(self, _event=None):
        if getattr(self, "network_map_resize_job", None):
            try:
                self.after_cancel(self.network_map_resize_job)
            except Exception:
                pass
        self.network_map_resize_job = self.after(240, self.draw_network_canvas)

    def schedule_network_map_draw(self, delay=40):
        if getattr(self, "network_map_draw_job", None):
            try:
                self.after_cancel(self.network_map_draw_job)
            except Exception:
                pass
        self.network_map_draw_job = self.after(delay, self.draw_network_canvas)

    def on_network_canvas_mousewheel(self, event):
        if self.network_canvas is None:
            return "break"
        delta = 0
        if hasattr(event, "delta") and event.delta:
            delta = 1 if event.delta > 0 else -1
        elif getattr(event, "num", None) == 4:
            delta = 1
        elif getattr(event, "num", None) == 5:
            delta = -1
        if delta:
            self.change_network_map_zoom(delta)
        return "break"

    def on_network_canvas_drag_start(self, event):
        if self.network_canvas is None:
            return
        self.network_map_drag_last = (event.x, event.y)
        self.network_map_drag_accum_dx = 0
        self.network_map_drag_accum_dy = 0

    def on_network_canvas_drag_move(self, event):
        if self.network_canvas is None:
            return
        if not self.network_map_drag_last:
            self.network_map_drag_last = (event.x, event.y)
            return
        last_x, last_y = self.network_map_drag_last
        dx = event.x - last_x
        dy = event.y - last_y
        self.network_map_drag_last = (event.x, event.y)
        if dx == 0 and dy == 0:
            return
        self.network_canvas.move("all", dx, dy)
        self.network_map_drag_accum_dx += dx
        self.network_map_drag_accum_dy += dy

    def on_network_canvas_drag_end(self, _event=None):
        if self.network_canvas is None:
            return
        rows = [r for r in getattr(self, "network_nodes_rows", []) if r.get("latitude") and r.get("longitude")]
        if rows and (self.network_map_drag_accum_dx or self.network_map_drag_accum_dy):
            center_lat, center_lon = self._get_network_map_center(rows)
            self.network_map_center = self._shift_center_by_pixels(
                center_lat,
                center_lon,
                -self.network_map_drag_accum_dx,
                -self.network_map_drag_accum_dy,
                self.network_map_zoom,
            )
        self.network_map_drag_last = None
        self.network_map_drag_accum_dx = 0
        self.network_map_drag_accum_dy = 0
        self.schedule_network_map_draw(180)

    def change_network_map_zoom(self, delta):
        self.network_map_zoom = max(11, min(17, int(self.network_map_zoom) + delta))
        if hasattr(self, "network_zoom_label"):
            self.network_zoom_label.configure(text=f"\u041c\u0430\u0441\u0448\u0442\u0430\u0431: {self.network_map_zoom}")
        self.schedule_network_map_draw(160)

    def focus_map_on_address(self):
        query = self.network_map_search_entry.get().strip() if hasattr(self, "network_map_search_entry") else ""
        if not query:
            messagebox.showinfo("Карта", "Введите адрес для поиска.")
            return
        self.network_map_search_btn.configure(state="disabled", text="Поиск...")

        def worker():
            err = None
            rows = []
            try:
                rows = self.geocode_search(query, limit=1)
            except Exception as ex:
                err = str(ex)

            def on_done():
                self.network_map_search_btn.configure(state="normal", text="Найти адрес")
                if err:
                    messagebox.showerror("Карта", f"Не удалось найти адрес:\n{err}")
                    return
                if not rows:
                    messagebox.showinfo("Карта", "Адрес не найден.")
                    return
                row = rows[0]
                lat = float(row.get("lat", 0) or 0)
                lon = float(row.get("lon", 0) or 0)
                if not lat or not lon:
                    messagebox.showwarning("Карта", "У найденного адреса нет координат.")
                    return
                self.network_map_center = (lat, lon)
                self.network_map_zoom = max(self.network_map_zoom, 15)
                if hasattr(self, "network_zoom_label"):
                    self.network_zoom_label.configure(text=f"Масштаб: {self.network_map_zoom}")
                self.schedule_network_map_draw(20)

            self.after(0, on_done)

        threading.Thread(target=worker, daemon=True).start()

    def center_map_to_abakan(self):
        self.network_map_center = (53.7209, 91.4424)
        self.schedule_network_map_draw(120)

    def center_map_to_selected_house(self):
        sel = self.network_nodes_tree.selection() if hasattr(self, "network_nodes_tree") else []
        if not sel:
            messagebox.showinfo("\u041a\u0430\u0440\u0442\u0430", "\u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u043e\u043c \u0432 \u043b\u0435\u0432\u043e\u043c \u0441\u043f\u0438\u0441\u043a\u0435.")
            return
        house_id = int(sel[0])
        row = next((r for r in self.network_nodes_rows if int(r["house_id"]) == house_id), None)
        if not row or not row.get("latitude") or not row.get("longitude"):
            messagebox.showwarning("\u041a\u0430\u0440\u0442\u0430", "\u0414\u043b\u044f \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0433\u043e \u0434\u043e\u043c\u0430 \u043d\u0435\u0442 \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442.")
            return
        self.network_map_center = (float(row["latitude"]), float(row["longitude"]))
        self.schedule_network_map_draw(120)

    def _get_network_map_center(self, rows):
        if self.network_map_center:
            return self.network_map_center
        return (
            sum(float(r["latitude"]) for r in rows) / len(rows),
            sum(float(r["longitude"]) for r in rows) / len(rows),
        )

    def _latlon_to_world(self, lat_value, lon_value, zoom):
        sin_lat = max(min(math.sin(math.radians(lat_value)), 0.9999), -0.9999)
        world = 256 * (2 ** zoom)
        x = (lon_value + 180.0) / 360.0 * world
        y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * world
        return x, y

    def _world_to_latlon(self, x_value, y_value, zoom):
        world = 256 * (2 ** zoom)
        lon = (x_value / world) * 360.0 - 180.0
        n = math.pi - (2.0 * math.pi * y_value) / world
        lat = math.degrees(math.atan(math.sinh(n)))
        return lat, lon

    def _shift_center_by_pixels(self, center_lat, center_lon, dx, dy, zoom):
        cx, cy = self._latlon_to_world(center_lat, center_lon, zoom)
        return self._world_to_latlon(cx + dx, cy + dy, zoom)

    def _project_to_static_map(self, lat, lon, center_lat, center_lon, zoom, width, height):
        cx, cy = self._latlon_to_world(center_lat, center_lon, zoom)
        px, py = self._latlon_to_world(lat, lon, zoom)
        return (px - cx) + (width / 2), (py - cy) + (height / 2)

    def _fetch_yandex_static_map(self, center_lat, center_lon, zoom, width, height):
        width = max(200, min(int(width), 560))
        height = max(180, min(int(height), 360))
        params = {
            "ll": f"{center_lon:.6f},{center_lat:.6f}",
            "z": str(int(zoom)),
            "size": f"{width},{height}",
            "l": "map",
            "lang": "ru_RU",
            "scale": "1",
        }
        ykey = os.getenv("YANDEX_MAPS_API_KEY", "62d9f365-7a46-4faa-a631-8f50f06091e6").strip()
        if ykey:
            params["apikey"] = ykey

        cache_key = (params["ll"], params["z"], params["size"])
        self.network_map_current_key = cache_key
        if cache_key in self.network_map_image_cache:
            self.network_map_photo = self.network_map_image_cache[cache_key]
            self.network_map_last_params = cache_key
            return width, height, True

        self.network_map_pending_request = (cache_key, params)
        self._kick_network_map_loader()

        return width, height, False

    def _kick_network_map_loader(self):
        if self.network_map_loading or not self.network_map_pending_request:
            return
        cache_key, params = self.network_map_pending_request
        self.network_map_pending_request = None
        self.network_map_loading = True

        def worker():
            content = None
            try:
                response = requests.get("https://static-maps.yandex.ru/v1", params=params, timeout=4)
                response.raise_for_status()
                content = response.content
            except Exception:
                try:
                    fallback_params = {
                        "ll": params["ll"],
                        "z": params["z"],
                        "size": params["size"],
                        "l": "map",
                        "lang": "ru_RU",
                    }
                    response = requests.get("https://static-maps.yandex.ru/1.x/", params=fallback_params, timeout=4)
                    response.raise_for_status()
                    content = response.content
                except Exception:
                    content = None

            def on_done():
                self.network_map_loading = False
                if content:
                    try:
                        image = Image.open(io.BytesIO(content)).convert("RGB")
                        photo = ImageTk.PhotoImage(image=image)
                        self.network_map_image_cache[cache_key] = photo
                        if len(self.network_map_image_cache) > 40:
                            for old_key in list(self.network_map_image_cache.keys())[:-24]:
                                self.network_map_image_cache.pop(old_key, None)
                    except Exception:
                        pass

                if self.network_map_pending_request:
                    self._kick_network_map_loader()

                if self.network_map_current_key == cache_key:
                    self.draw_network_canvas()

            self.after(0, on_done)

        threading.Thread(target=worker, daemon=True).start()

    def draw_network_canvas(self):
        if self.network_canvas is None:
            return
        rows = [r for r in getattr(self, "network_nodes_rows", []) if r.get("latitude") and r.get("longitude")]
        if not rows:
            self.network_map_last_render_key = None
            self.network_canvas.delete("all")
            self.network_canvas.create_text(
                250,
                170,
                text="\u041d\u0435\u0442 \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442 \u0434\u043e\u043c\u043e\u0432. \u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 API \u0430\u0434\u0440\u0435\u0441\u043e\u0432 \u043f\u0440\u0438 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438.",
                fill="#8899aa",
                font=("Segoe UI", 12),
            )
            return

        canvas_width = max(200, self.network_canvas.winfo_width() - 2)
        canvas_height = max(180, self.network_canvas.winfo_height() - 2)
        center_lat, center_lon = self._get_network_map_center(rows)
        map_loaded = False
        try:
            map_w, map_h, map_loaded = self._fetch_yandex_static_map(center_lat, center_lon, self.network_map_zoom, canvas_width, canvas_height)
            render_key = (round(center_lat, 6), round(center_lon, 6), int(self.network_map_zoom), map_w, map_h, map_loaded,
                          tuple((int(r["house_id"]), int(r.get("clients_count") or 0), int(r.get("active_incidents") or 0)) for r in rows))
            if self.network_map_last_render_key == render_key:
                return
            self.network_map_last_render_key = render_key
            self.network_canvas.delete("all")
            x0 = (canvas_width - map_w) // 2
            y0 = (canvas_height - map_h) // 2
            if map_loaded and self.network_map_photo is not None:
                self.network_canvas.create_image(x0, y0, anchor="nw", image=self.network_map_photo)
            else:
                self.network_canvas.create_rectangle(x0, y0, x0 + map_w, y0 + map_h, fill="#121722", outline="")
                self.network_canvas.create_text(
                    x0 + 16,
                    y0 + 14,
                    anchor="nw",
                    fill="#9eb4ca",
                    text="Загрузка карты...",
                    font=("Segoe UI", 11, "bold"),
                )
        except Exception:
            self.network_map_last_render_key = None
            self.network_canvas.delete("all")
            map_w, map_h = canvas_width, canvas_height
            x0, y0 = 0, 0
            self.network_canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="#121722", outline="")
            self.network_canvas.create_text(
                16,
                12,
                anchor="nw",
                fill="#f19999",
                text="\u041a\u0430\u0440\u0442\u0430 \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u0430, \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u044b \u0442\u043e\u043b\u044c\u043a\u043e \u0441\u0442\u0430\u0442\u0443\u0441\u044b \u0434\u043e\u043c\u043e\u0432",
                font=("Segoe UI", 10, "bold"),
            )

        self.network_canvas.create_rectangle(x0 + 10, y0 + 10, x0 + 360, y0 + 36, fill="#10151d", outline="")
        self.network_canvas.create_text(
            x0 + 18,
            y0 + 23,
            anchor="w",
            fill="#dce6f2",
            text="\u0417\u0435\u043b\u0435\u043d\u044b\u0439: \u0441\u0442\u0430\u0431\u0438\u043b\u044c\u043d\u043e | \u041a\u0440\u0430\u0441\u043d\u044b\u0439: \u0430\u0432\u0430\u0440\u0438\u044f | \u0427\u0438\u0441\u043b\u043e: \u043a\u043b\u0438\u0435\u043d\u0442\u043e\u0432",
            font=("Segoe UI", 10),
        )

        for r in rows:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
            px, py = self._project_to_static_map(lat, lon, center_lat, center_lon, self.network_map_zoom, map_w, map_h)
            px += x0
            py += y0
            if px < x0 - 30 or py < y0 - 30 or px > x0 + map_w + 30 or py > y0 + map_h + 30:
                continue
            clients = int(r.get("clients_count") or 0)
            active = int(r.get("active_incidents") or 0)
            color = "#d34a4a" if active > 0 else "#32b06a"
            radius = 11 + min(clients, 40) * 0.35
            self.network_canvas.create_oval(px - radius, py - radius, px + radius, py + radius, fill=color, outline="#ecf1f7", width=1)
            self.network_canvas.create_text(px, py, text=str(clients), fill="white", font=("Segoe UI", 9, "bold"))

    def load_affected_customers(self):
        for item in self.network_affected_tree.get_children():
            self.network_affected_tree.delete(item)
        sel = self.network_nodes_tree.selection()
        if not sel:
            return
        house_id = int(sel[0])
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id, name, phone FROM customers WHERE house_id=%s ORDER BY name", (house_id,))
        for row in cursor.fetchall():
            self.network_affected_tree.insert("", "end", values=row)
        cursor.close()

    def create_network_incident(self):
        sel = self.network_nodes_tree.selection()
        if not sel:
            messagebox.showinfo("Авария", "Сначала выберите дом в левом списке.")
            return
        house_id = int(sel[0])
        modal = self.open_modal("Новая авария по дому", "560x430")
        result = {"ok": False, "title": "", "severity": "Средняя", "desc": ""}
        body = ctk.CTkFrame(modal)
        body.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        body.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(body, text=f"Дом ID: {house_id}").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ctk.CTkLabel(body, text="Название аварии").grid(row=1, column=0, sticky="w")
        title_entry = ctk.CTkEntry(body, height=34)
        title_entry.insert(0, "Нет связи в доме")
        title_entry.grid(row=2, column=0, sticky="ew", pady=(4, 8))
        ctk.CTkLabel(body, text="Критичность").grid(row=3, column=0, sticky="w")
        severity_combo = ctk.CTkComboBox(body, values=["Низкая", "Средняя", "Высокая", "Критическая"], height=34)
        severity_combo.set("Средняя")
        severity_combo.grid(row=4, column=0, sticky="ew", pady=(4, 8))
        ctk.CTkLabel(body, text="Описание").grid(row=5, column=0, sticky="w")
        desc_entry = ctk.CTkTextbox(body, height=120)
        desc_entry.grid(row=6, column=0, sticky="nsew", pady=(4, 8))
        body.grid_rowconfigure(6, weight=1)
        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=16, pady=(0, 14))
        def submit():
            result["title"] = title_entry.get().strip()
            result["severity"] = severity_combo.get().strip() or "Средняя"
            result["desc"] = desc_entry.get("0.0", "end").strip()
            result["ok"] = bool(result["title"])
            modal.destroy()
        ctk.CTkButton(actions, text="Создать аварию", fg_color="#8b1a1a", command=submit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="Отмена", command=modal.destroy).pack(side="left")
        modal.wait_window()
        if not result["ok"]:
            return
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO house_incidents (house_id, title, severity, status, description, started_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (house_id, result["title"], result["severity"], "Активна", result["desc"] or "", datetime.now()))
        self.conn.commit()
        cursor.close()
        self.log_house_affected_customers(house_id, f"Авария дома: {result['title']}")
        self.load_network_map_data()

    def resolve_network_incident(self):
        sel = self.network_incidents_tree.selection()
        if not sel:
            messagebox.showinfo("Авария", "Выберите инцидент в списке справа.")
            return
        incident_id = int(sel[0])
        comment = self.prompt_single_line("Закрытие аварии", "Комментарий при закрытии:", "Связь восстановлена")
        if comment is None:
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT house_id, title FROM house_incidents WHERE incident_id=%s", (incident_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return
        house_id, title = row[0], row[1]
        cursor.execute(
            "UPDATE house_incidents SET status='Закрыта', resolved_at=%s, description=CONCAT(IFNULL(description,''), %s) WHERE incident_id=%s",
            (datetime.now(), f"\n[Закрытие] {comment}", incident_id))
        self.conn.commit()
        cursor.close()
        self.log_house_affected_customers(house_id, f"Авария закрыта: {title}")
        self.load_network_map_data()

    def log_house_affected_customers(self, house_id, details):
        cursor = self.conn.cursor()
        cursor.execute("SELECT customer_id FROM customers WHERE house_id=%s", (house_id,))
        customer_ids = [r[0] for r in cursor.fetchall()]
        cursor.close()
        for cid in customer_ids:
            self.log_customer_event(cid, "Диагностика", details)

    def _build_network_map_payload(self):
        houses = []
        rows = [r for r in getattr(self, "network_nodes_rows", []) if r.get("latitude") and r.get("longitude")]
        for r in rows:
            houses.append({
                "house_id": int(r["house_id"]),
                "address": (r.get("full_address") or "").strip(),
                "lat": float(r["latitude"]),
                "lon": float(r["longitude"]),
                "clients": int(r.get("clients_count") or 0),
                "active": int(r.get("active_incidents") or 0),
            })
        if houses:
            center_lat = sum(h["lat"] for h in houses) / len(houses)
            center_lon = sum(h["lon"] for h in houses) / len(houses)
        else:
            center_lat, center_lon = 53.7209, 91.4424
        return {
            "center": {"lat": center_lat, "lon": center_lon},
            "zoom": int(self.network_map_zoom if hasattr(self, "network_map_zoom") else 13),
            "houses": houses,
        }

    def _write_webview_payload(self, payload):
        payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        changed = payload_json != self.map_webview_payload_hash
        if changed:
            with open(self.map_webview_payload_path, "w", encoding="utf-8") as f:
                f.write(payload_json)
            self.map_webview_payload_hash = payload_json
        return changed

    def _stop_webview_map_process(self):
        if self.map_webview_refresh_job:
            try:
                self.after_cancel(self.map_webview_refresh_job)
            except Exception:
                pass
            self.map_webview_refresh_job = None
        proc = getattr(self, "map_webview_process", None)
        if not proc:
            return
        try:
            if proc.poll() is None:
                proc.terminate()
        except Exception:
            pass
        self.map_webview_process = None

    def _restart_webview_map_silent(self):
        self.map_webview_refresh_job = None
        if not (self.map_webview_process and self.map_webview_process.poll() is None):
            return
        self.open_webview_map(force_restart=True, silent=True)

    def sync_webview_map_window(self):
        if not (self.map_webview_process and self.map_webview_process.poll() is None):
            return
        payload = self._build_network_map_payload()
        if not payload["houses"]:
            return
        try:
            changed = self._write_webview_payload(payload)
        except Exception:
            return
        if not changed:
            return
        if self.map_webview_refresh_job:
            try:
                self.after_cancel(self.map_webview_refresh_job)
            except Exception:
                pass
        # debounce: merge frequent updates into one restart
        self.map_webview_refresh_job = self.after(350, self._restart_webview_map_silent)

    def open_webview_map(self, force_restart=False, silent=False):
        payload = self._build_network_map_payload()
        if not payload["houses"]:
            if not silent:
                messagebox.showinfo("Карта", "Нет домов с координатами для отображения.")
            return
        try:
            self._write_webview_payload(payload)
        except Exception as ex:
            if not silent:
                messagebox.showerror("Карта", f"Не удалось сохранить данные карты:\n{ex}")
            return

        if force_restart:
            self._stop_webview_map_process()

        if self.map_webview_process and self.map_webview_process.poll() is None:
            if not silent:
                messagebox.showinfo("Карта", "Окно карты уже открыто.")
            return

        launcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map_webview.py")
        if not os.path.exists(launcher):
            if not silent:
                messagebox.showerror("Карта", f"Не найден модуль WebView:\n{launcher}")
            return
        try:
            self.map_webview_process = subprocess.Popen([sys.executable, launcher, self.map_webview_payload_path])
            if hasattr(self, "network_map_hint"):
                self.network_map_hint.configure(text="Карта открыта. Обновление выполняется автоматически.")
        except Exception as ex:
            self.map_webview_process = None
            if not silent:
                messagebox.showerror("Карта", f"Не удалось открыть WebView карту:\n{ex}")

    def open_abakan_map(self):
        # Backward compatibility for old button/action names.
        self.open_webview_map()


    def log_customer_event(self, customer_id, event_type, details, actor=None):
        if not self.conn or not customer_id:
            return
        actor_name = actor or self.operator.get("full_name", "Оператор")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO customer_events (customer_id, event_type, details, actor, event_time) VALUES (%s, %s, %s, %s, %s)",
                (customer_id, event_type, details, actor_name, datetime.now()))
            self.conn.commit()
            cursor.close()
        except Exception:
            pass

    def start_diag_thread(self):
        cust_str = self.diag_cust_combo.get()
        if ' [IP: ' not in cust_str: return
        customer_id = int(cust_str.split(' - ')[0]) if ' - ' in cust_str else None
        ip_address = cust_str.split('[IP: ')[1].replace(']', '')
        self.diag_result.delete("0.0", "end")
        self.diag_result.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] PING {ip_address}\n")
        self.btn_run_diag.configure(state="disabled")
        self.log_customer_event(customer_id, "Диагностика", f"Запущен PING по IP {ip_address}")
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
            "model": "openai/gpt-oss-120b:free",
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
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()

    if login_app.user_data:
        operator_info = login_app.user_data
        app = ISPAutomationSystem(operator_data=operator_info)
        app.mainloop()
