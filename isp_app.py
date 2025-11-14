import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database  # модуль с БД


class ISPAutomationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Система интернет-провайдера СКАТ")
        self.root.geometry("1100x750")
        self.root.configure(bg='#f5f5f5')

        # База данных
        self.conn = database.get_connection()  # вместо sqlite3.connect + self.create_tables()

        # Оформление
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Цвета
        self.primary_color = '#3a7ca5'
        self.secondary_color = '#2f6690'
        self.accent_color = '#d9dcd6'
        self.background_color = '#f5f5f5'
        self.text_color = '#333333'
        self.success_color = '#4caf50'
        self.warning_color = '#ff9800'
        self.error_color = '#f44336'

        # Стили
        self.style.configure('.', background=self.background_color, foreground=self.text_color)
        self.style.configure('TFrame', background=self.background_color)
        self.style.configure('TLabel', background=self.background_color, font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6,
                             background=self.primary_color, foreground='white')
        self.style.map('TButton',
                       background=[('active', self.secondary_color), ('disabled', '#cccccc')],
                       foreground=[('disabled', '#888888')])
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'),
                             foreground=self.primary_color)
        self.style.configure('Treeview', rowheight=28, font=('Segoe UI', 9))
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'),
                             background=self.primary_color, foreground='white')
        self.style.map('Treeview.Heading',
                       background=[('active', self.secondary_color)])
        self.style.configure('TNotebook', background=self.background_color)
        self.style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10),
                             background=self.accent_color, foreground=self.text_color)
        self.style.map('TNotebook.Tab',
                       background=[('selected', self.primary_color), ('active', self.secondary_color)],
                       foreground=[('selected', 'white')])
        self.style.configure('TCombobox', fieldbackground='white', background='white')
        self.style.configure('TEntry', fieldbackground='white')
        self.style.configure('TLabelframe', font=('Segoe UI', 10, 'bold'),
                             foreground=self.primary_color)
        self.style.configure('TLabelframe.Label', foreground=self.primary_color)

        # Главный контейнер
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Строка состояния
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var,
                                    relief=tk.SUNKEN, anchor=tk.W,
                                    font=('Segoe UI', 9), foreground='#666666')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        self.status_var.set("Готово")

        # Вкладки
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создание вкладок
        self.create_dashboard_tab()
        self.create_customer_tab()
        self.create_plans_tab()
        self.create_complaints_tab()
        self.create_billing_tab()
        self.create_troubleshooting_tab()

        # Загрузка данных
        self.load_customers()
        self.load_plans()
        self.load_complaints()
        # Доп. строка состояния (как в оригинале)
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var,
                                    relief=tk.SUNKEN, anchor=tk.W,
                                    font=('Segoe UI', 9), foreground='#666666')
        self.status_bar.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.status_var.set("Готово")

    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Панель")

        # Заголовок
        header_frame = ttk.Frame(self.dashboard_tab)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        header = ttk.Label(header_frame, text="Панель интернет-сервиса СКАТ — Добро пожаловать, админ!",
                           style='Header.TLabel')
        header.pack(side=tk.LEFT)

        # Кнопка обновления
        refresh_btn = ttk.Button(header_frame, text="Обновить", command=self.update_dashboard_stats,
                                 style='Accent.TButton')
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Статистика
        stats_frame = ttk.LabelFrame(self.dashboard_tab, text="Обзор системы", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        # Клиенты
        customer_frame = ttk.Frame(stats_frame, style='Card.TFrame')
        customer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(customer_frame, text="Клиенты", font=('Segoe UI', 11, 'bold'),
                  foreground=self.primary_color).pack(pady=(5, 10))

        self.total_customers_label = ttk.Label(customer_frame, text="Всего: 0", font=('Segoe UI', 10))
        self.total_customers_label.pack(pady=5)

        self.active_customers_label = ttk.Label(customer_frame, text="Активных: 0", font=('Segoe UI', 10))
        self.active_customers_label.pack(pady=5)

        # Тарифы
        plans_frame = ttk.Frame(stats_frame, style='Card.TFrame')
        plans_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(plans_frame, text="Тарифы", font=('Segoe UI', 11, 'bold'),
                  foreground=self.primary_color).pack(pady=(5, 10))

        self.total_plans_label = ttk.Label(plans_frame, text="Доступно: 0", font=('Segoe UI', 10))
        self.total_plans_label.pack(pady=5)

        self.popular_plan_label = ttk.Label(plans_frame, text="Популярный: нет", font=('Segoe UI', 10))
        self.popular_plan_label.pack(pady=5)

        # Обращения
        complaints_frame = ttk.Frame(stats_frame, style='Card.TFrame')
        complaints_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(complaints_frame, text="Обращения", font=('Segoe UI', 11, 'bold'),
                  foreground=self.primary_color).pack(pady=(5, 10))

        self.open_complaints_label = ttk.Label(complaints_frame, text="Открыто: 0", font=('Segoe UI', 10))
        self.open_complaints_label.pack(pady=5)

        self.resolved_complaints_label = ttk.Label(complaints_frame, text="Решено: 0", font=('Segoe UI', 10))
        self.resolved_complaints_label.pack(pady=5)

        # Недавние события
        activity_frame = ttk.LabelFrame(self.dashboard_tab, text="Недавняя активность", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree_scroll = ttk.Scrollbar(activity_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.activity_tree = ttk.Treeview(activity_frame, columns=('type', 'details', 'date'),
                                          show='headings', yscrollcommand=tree_scroll.set)
        self.activity_tree.heading('type', text='Тип активности')
        self.activity_tree.heading('details', text='Детали')
        self.activity_tree.heading('date', text='Дата')
        self.activity_tree.column('type', width=150, anchor=tk.W)
        self.activity_tree.column('details', width=400, anchor=tk.W)
        self.activity_tree.column('date', width=150, anchor=tk.W)
        self.activity_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll.config(command=self.activity_tree.yview)

        # Цвета строк
        self.activity_tree.tag_configure('customer', background='#e3f2fd')
        self.activity_tree.tag_configure('plan', background='#e8f5e9')
        self.activity_tree.tag_configure('complaint', background='#fff3e0')
        self.activity_tree.tag_configure('billing', background='#f3e5f5')

        self.update_dashboard_stats()

    def create_customer_tab(self):
        self.customer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.customer_tab, text="Клиенты")

        paned = ttk.PanedWindow(self.customer_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левая часть — форма
        left_pane = ttk.Frame(paned)
        paned.add(left_pane, weight=1)

        management_frame = ttk.LabelFrame(left_pane, text="Управление клиентами", padding=10)
        management_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        form_frame = ttk.Frame(management_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.customer_name = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.customer_name.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Адрес:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.customer_address = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.customer_address.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.customer_phone = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.customer_phone.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Эл. почта:").grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.customer_email = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.customer_email.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Тариф:").grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        self.customer_plan = ttk.Combobox(form_frame, width=28, font=('Segoe UI', 10))
        self.customer_plan.grid(row=4, column=1, padx=5, pady=8, sticky=tk.EW)

        buttons_frame = ttk.Frame(management_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

        ttk.Button(buttons_frame, text="Добавить клиента", command=self.add_customer).pack(side=tk.LEFT, padx=5,
                                                                                           fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Обновить клиента", command=self.update_customer).pack(side=tk.LEFT, padx=5,
                                                                                              fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Удалить клиента", command=self.delete_customer).pack(side=tk.LEFT, padx=5,
                                                                                             fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Очистить форму", command=self.clear_customer_form).pack(side=tk.LEFT, padx=5,
                                                                                                fill=tk.X, expand=True)

        # Правая часть — список
        right_pane = ttk.Frame(paned)
        paned.add(right_pane, weight=2)

        list_frame = ttk.LabelFrame(right_pane, text="Список клиентов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll_y = ttk.Scrollbar(list_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.customers_tree = ttk.Treeview(list_frame, columns=('id', 'name', 'address', 'phone', 'email', 'plan'),
                                           show='headings', yscrollcommand=tree_scroll_y.set,
                                           xscrollcommand=tree_scroll_x.set)

        self.customers_tree.heading('id', text='ID')
        self.customers_tree.heading('name', text='Имя')
        self.customers_tree.heading('address', text='Адрес')
        self.customers_tree.heading('phone', text='Телефон')
        self.customers_tree.heading('email', text='Эл. почта')
        self.customers_tree.heading('plan', text='Тариф')

        self.customers_tree.column('id', width=50, anchor=tk.CENTER)
        self.customers_tree.column('name', width=150, anchor=tk.W)
        self.customers_tree.column('address', width=200, anchor=tk.W)
        self.customers_tree.column('phone', width=100, anchor=tk.W)
        self.customers_tree.column('email', width=150, anchor=tk.W)
        self.customers_tree.column('plan', width=150, anchor=tk.W)

        self.customers_tree.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y.config(command=self.customers_tree.yview)
        tree_scroll_x.config(command=self.customers_tree.xview)

        self.customers_tree.bind('<<TreeviewSelect>>', self.on_customer_select)

        self.customers_tree.tag_configure('oddrow', background='#f5f5f5')
        self.customers_tree.tag_configure('evenrow', background='white')

    def create_plans_tab(self):
        self.plans_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plans_tab, text="Тарифы")

        paned = ttk.PanedWindow(self.plans_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_pane = ttk.Frame(paned)
        paned.add(left_pane, weight=1)

        management_frame = ttk.LabelFrame(left_pane, text="Управление тарифами", padding=10)
        management_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        form_frame = ttk.Frame(management_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Название тарифа:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.plan_name = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.plan_name.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Скорость:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.plan_speed = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.plan_speed.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Цена:").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.plan_price = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.plan_price.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Лимит трафика:").grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.plan_data_limit = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.plan_data_limit.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Описание:").grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        self.plan_description = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.plan_description.grid(row=4, column=1, padx=5, pady=8, sticky=tk.EW)

        buttons_frame = ttk.Frame(management_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

        ttk.Button(buttons_frame, text="Добавить тариф", command=self.add_plan).pack(side=tk.LEFT, padx=5, fill=tk.X,
                                                                                     expand=True)
        ttk.Button(buttons_frame, text="Обновить тариф", command=self.update_plan).pack(side=tk.LEFT, padx=5, fill=tk.X,
                                                                                        expand=True)
        ttk.Button(buttons_frame, text="Удалить тариф", command=self.delete_plan).pack(side=tk.LEFT, padx=5, fill=tk.X,
                                                                                       expand=True)
        ttk.Button(buttons_frame, text="Очистить форму", command=self.clear_plan_form).pack(side=tk.LEFT, padx=5,
                                                                                            fill=tk.X, expand=True)

        right_pane = ttk.Frame(paned)
        paned.add(right_pane, weight=2)

        list_frame = ttk.LabelFrame(right_pane, text="Доступные тарифы", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll_y = ttk.Scrollbar(list_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.plans_tree = ttk.Treeview(list_frame,
                                       columns=('id', 'name', 'speed', 'price', 'data_limit', 'description'),
                                       show='headings', yscrollcommand=tree_scroll_y.set,
                                       xscrollcommand=tree_scroll_x.set)

        self.plans_tree.heading('id', text='ID')
        self.plans_tree.heading('name', text='Название')
        self.plans_tree.heading('speed', text='Скорость')
        self.plans_tree.heading('price', text='Цена')
        self.plans_tree.heading('data_limit', text='Лимит трафика')
        self.plans_tree.heading('description', text='Описание')

        self.plans_tree.column('id', width=50, anchor=tk.CENTER)
        self.plans_tree.column('name', width=150, anchor=tk.W)
        self.plans_tree.column('speed', width=100, anchor=tk.W)
        self.plans_tree.column('price', width=80, anchor=tk.E)
        self.plans_tree.column('data_limit', width=100, anchor=tk.W)
        self.plans_tree.column('description', width=250, anchor=tk.W)

        self.plans_tree.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y.config(command=self.plans_tree.yview)
        tree_scroll_x.config(command=self.plans_tree.xview)

        self.plans_tree.bind('<<TreeviewSelect>>', self.on_plan_select)

        self.plans_tree.tag_configure('oddrow', background='#f5f5f5')
        self.plans_tree.tag_configure('evenrow', background='white')

    def create_complaints_tab(self):
        self.complaints_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.complaints_tab, text="Обращения")

        paned = ttk.PanedWindow(self.complaints_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_pane = ttk.Frame(paned)
        paned.add(left_pane, weight=1)

        management_frame = ttk.LabelFrame(left_pane, text="Управление обращениями", padding=10)
        management_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        form_frame = ttk.Frame(management_frame)
        form_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.complaint_customer = ttk.Combobox(form_frame, width=25, font=('Segoe UI', 10))
        self.complaint_customer.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.NW)
        self.complaint_description = tk.Text(form_frame, width=40, height=5, wrap=tk.WORD,
                                             font=('Segoe UI', 10), padx=5, pady=5)
        self.complaint_description.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Статус:").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.complaint_status = ttk.Combobox(form_frame, width=25, font=('Segoe UI', 10),
                                             values=['Открыто', 'В работе', 'Решено'])
        self.complaint_status.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Решение:").grid(row=3, column=0, padx=5, pady=8, sticky=tk.NW)
        self.complaint_resolution = tk.Text(form_frame, width=40, height=5, wrap=tk.WORD,
                                            font=('Segoe UI', 10), padx=5, pady=5)
        self.complaint_resolution.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)

        buttons_frame = ttk.Frame(management_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

        ttk.Button(buttons_frame, text="Добавить обращение", command=self.add_complaint).pack(side=tk.LEFT, padx=5,
                                                                                              fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Обновить обращение", command=self.update_complaint).pack(side=tk.LEFT, padx=5,
                                                                                                 fill=tk.X, expand=True)
        ttk.Button(buttons_frame, text="Отметить как решённое", command=self.resolve_complaint).pack(side=tk.LEFT,
                                                                                                     padx=5, fill=tk.X,
                                                                                                     expand=True)
        ttk.Button(buttons_frame, text="Очистить форму", command=self.clear_complaint_form).pack(side=tk.LEFT, padx=5,
                                                                                                 fill=tk.X, expand=True)

        right_pane = ttk.Frame(paned)
        paned.add(right_pane, weight=2)

        list_frame = ttk.LabelFrame(right_pane, text="Обращения клиентов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll_y = ttk.Scrollbar(list_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.complaints_tree = ttk.Treeview(list_frame, columns=('id', 'customer', 'date', 'status', 'description'),
                                            show='headings', yscrollcommand=tree_scroll_y.set,
                                            xscrollcommand=tree_scroll_x.set)

        self.complaints_tree.heading('id', text='ID')
        self.complaints_tree.heading('customer', text='Клиент')
        self.complaints_tree.heading('date', text='Дата')
        self.complaints_tree.heading('status', text='Статус')
        self.complaints_tree.heading('description', text='Описание')

        self.complaints_tree.column('id', width=50, anchor=tk.CENTER)
        self.complaints_tree.column('customer', width=150, anchor=tk.W)
        self.complaints_tree.column('date', width=100, anchor=tk.W)
        self.complaints_tree.column('status', width=100, anchor=tk.W)
        self.complaints_tree.column('description', width=400, anchor=tk.W)

        self.complaints_tree.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y.config(command=self.complaints_tree.yview)
        tree_scroll_x.config(command=self.complaints_tree.xview)

        self.complaints_tree.bind('<<TreeviewSelect>>', self.on_complaint_select)

        self.complaints_tree.tag_configure('Открыто', foreground=self.error_color)
        self.complaints_tree.tag_configure('В работе', foreground=self.warning_color)
        self.complaints_tree.tag_configure('Решено', foreground=self.success_color)

    def create_billing_tab(self):
        self.billing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.billing_tab, text="Счета")

        paned = ttk.PanedWindow(self.billing_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_pane = ttk.Frame(paned)
        paned.add(left_pane, weight=1)

        management_frame = ttk.LabelFrame(left_pane, text="Управление счетами", padding=10)
        management_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        form_frame = ttk.Frame(management_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.billing_customer = ttk.Combobox(form_frame, width=25, font=('Segoe UI', 10))
        self.billing_customer.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Сумма:").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.billing_amount = ttk.Entry(form_frame, width=25, font=('Segoe UI', 10))
        self.billing_amount.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(form_frame, text="Срок оплаты (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.billing_due_date = ttk.Entry(form_frame, width=25, font=('Segoe UI', 10))
        self.billing_due_date.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        buttons_frame = ttk.Frame(management_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

        ttk.Button(buttons_frame, text="Создать счёт", command=self.generate_bill).pack(side=tk.LEFT, padx=5, fill=tk.X,
                                                                                        expand=True)
        ttk.Button(buttons_frame, text="Отметить как оплаченный", command=self.mark_bill_paid).pack(side=tk.LEFT,
                                                                                                    padx=5, fill=tk.X,
                                                                                                    expand=True)
        ttk.Button(buttons_frame, text="Очистить форму", command=self.clear_billing_form).pack(side=tk.LEFT, padx=5,
                                                                                               fill=tk.X, expand=True)

        right_pane = ttk.Frame(paned)
        paned.add(right_pane, weight=2)

        list_frame = ttk.LabelFrame(right_pane, text="Счета клиентов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll_y = ttk.Scrollbar(list_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.bills_tree = ttk.Treeview(list_frame, columns=('id', 'customer', 'amount', 'due_date', 'status'),
                                       show='headings', yscrollcommand=tree_scroll_y.set,
                                       xscrollcommand=tree_scroll_x.set)

        self.bills_tree.heading('id', text='ID')
        self.bills_tree.heading('customer', text='Клиент')
        self.bills_tree.heading('amount', text='Сумма')
        self.bills_tree.heading('due_date', text='Срок оплаты')
        self.bills_tree.heading('status', text='Статус')

        self.bills_tree.column('id', width=50, anchor=tk.CENTER)
        self.bills_tree.column('customer', width=150, anchor=tk.W)
        self.bills_tree.column('amount', width=100, anchor=tk.E)
        self.bills_tree.column('due_date', width=100, anchor=tk.W)
        self.bills_tree.column('status', width=100, anchor=tk.W)

        self.bills_tree.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y.config(command=self.bills_tree.yview)
        tree_scroll_x.config(command=self.bills_tree.xview)

        self.bills_tree.bind('<<TreeviewSelect>>', self.on_bill_select)

        self.bills_tree.tag_configure('Оплачен', foreground=self.success_color)
        self.bills_tree.tag_configure('Не оплачен', foreground=self.error_color)

        self.load_bills()

    def create_troubleshooting_tab(self):
        self.troubleshooting_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.troubleshooting_tab, text="Диагностика")

        header_frame = ttk.Frame(self.troubleshooting_tab)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        header = ttk.Label(header_frame, text="Диагностика подключения к интернету", style='Header.TLabel')
        header.pack(side=tk.LEFT)

        issue_frame = ttk.LabelFrame(self.troubleshooting_tab, text="Выберите проблему", padding=10)
        issue_frame.pack(fill=tk.X, padx=10, pady=10)

        self.issue_var = tk.StringVar()

        ttk.Radiobutton(issue_frame, text="Нет подключения к интернету", variable=self.issue_var,
                        value="no_connection").pack(anchor=tk.W, padx=5, pady=3, fill=tk.X)
        ttk.Radiobutton(issue_frame, text="Низкая скорость интернета", variable=self.issue_var,
                        value="slow_speed").pack(anchor=tk.W, padx=5, pady=3, fill=tk.X)
        ttk.Radiobutton(issue_frame, text="Периодически пропадает связь", variable=self.issue_var,
                        value="intermittent").pack(anchor=tk.W, padx=5, pady=3, fill=tk.X)
        ttk.Radiobutton(issue_frame, text="Нет доступа к конкретному сайту", variable=self.issue_var,
                        value="specific_website").pack(anchor=tk.W, padx=5, pady=3, fill=tk.X)
        ttk.Radiobutton(issue_frame, text="Проблемы с роутером", variable=self.issue_var,
                        value="router").pack(anchor=tk.W, padx=5, pady=3, fill=tk.X)

        ttk.Button(issue_frame, text="Диагностировать", command=self.run_troubleshooting,
                   style='Accent.TButton').pack(pady=10, fill=tk.X)

        self.results_frame = ttk.LabelFrame(self.troubleshooting_tab, text="Шаги устранения неполадок", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_scroll = ttk.Scrollbar(self.results_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(self.results_frame, wrap=tk.WORD, height=10,
                                    font=('Segoe UI', 10), yscrollcommand=text_scroll.set,
                                    padx=5, pady=5)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        text_scroll.config(command=self.results_text.yview)

        self.schedule_button = ttk.Button(self.troubleshooting_tab, text="Назначить визит техника",
                                          command=self.schedule_technician, state=tk.DISABLED,
                                          style='Accent.TButton')
        self.schedule_button.pack(pady=10, padx=10, fill=tk.X)

    # Загрузка данных
    def load_customers(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT c.customer_id, c.name, c.address, c.phone, c.email, p.name 
        FROM customers c LEFT JOIN plans p ON c.plan_id = p.plan_id
        ''')
        rows = cursor.fetchall()

        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)

        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.customers_tree.insert('', tk.END, values=row, tags=(tag,))

        customer_names = [row[1] for row in rows]
        self.complaint_customer['values'] = customer_names
        self.billing_customer['values'] = customer_names

        cursor.execute('SELECT plan_id, name FROM plans')
        plans = cursor.fetchall()
        self.customer_plan['values'] = [f"{p[0]} - {p[1]}" for p in plans]

        self.status_var.set(f"Загружено клиентов: {len(rows)}")

    def load_plans(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM plans')
        rows = cursor.fetchall()

        for item in self.plans_tree.get_children():
            self.plans_tree.delete(item)

        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.plans_tree.insert('', tk.END, values=row, tags=(tag,))

        self.customer_plan['values'] = [f"{row[0]} - {row[1]}" for row in rows]

        self.status_var.set(f"Загружено тарифов: {len(rows)}")

    def load_complaints(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT co.complaint_id, c.name, co.date, co.status, co.description 
        FROM complaints co JOIN customers c ON co.customer_id = c.customer_id
        ''')
        rows = cursor.fetchall()

        for item in self.complaints_tree.get_children():
            self.complaints_tree.delete(item)

        for row in rows:
            self.complaints_tree.insert('', tk.END, values=row, tags=(row[3],))

        self.status_var.set(f"Загружено обращений: {len(rows)}")

    def load_bills(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT b.bill_id, c.name, b.amount, b.due_date, 
               CASE WHEN b.paid = 1 THEN 'Оплачен' ELSE 'Не оплачен' END as status
        FROM billing b JOIN customers c ON b.customer_id = c.customer_id
        ''')
        rows = cursor.fetchall()

        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)

        for row in rows:
            self.bills_tree.insert('', tk.END, values=row, tags=(row[4],))

        self.status_var.set(f"Загружено счетов: {len(rows)}")

    def update_dashboard_stats(self):
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM customers')
        total_customers = cursor.fetchone()[0]
        self.total_customers_label.config(text=f"Всего: {total_customers}")

        cursor.execute('SELECT COUNT(*) FROM customers WHERE plan_id IS NOT NULL')
        active_customers = cursor.fetchone()[0]
        self.active_customers_label.config(text=f"Активных: {active_customers}")

        cursor.execute('SELECT COUNT(*) FROM plans')
        total_plans = cursor.fetchone()[0]
        self.total_plans_label.config(text=f"Доступно: {total_plans}")

        cursor.execute('''
        SELECT p.name, COUNT(c.customer_id) as customer_count
        FROM plans p LEFT JOIN customers c ON p.plan_id = c.plan_id
        GROUP BY p.plan_id
        ORDER BY customer_count DESC
        LIMIT 1
        ''')
        popular_plan = cursor.fetchone()
        if popular_plan and popular_plan[1] > 0:
            self.popular_plan_label.config(text=f"Популярный: {popular_plan[0]} ({popular_plan[1]})")
        else:
            self.popular_plan_label.config(text="Популярный: нет")

        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status != 'Решено'")
        open_complaints = cursor.fetchone()[0]
        self.open_complaints_label.config(text=f"Открыто: {open_complaints}")

        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Решено'")
        resolved_complaints = cursor.fetchone()[0]
        self.resolved_complaints_label.config(text=f"Решено: {resolved_complaints}")

        cursor.execute('''
        SELECT 'Новый клиент' as type, name as details, registration_date as date
        FROM customers
        ORDER BY registration_date DESC
        LIMIT 5
        ''')
        customer_activity = cursor.fetchall()

        cursor.execute('''
        SELECT 'Новое обращение' as type, 
               (SELECT name FROM customers WHERE customer_id = c.customer_id) || ' - ' || 
               SUBSTR(c.description, 1, 30) || '...' as details, 
               c.date
        FROM complaints c
        ORDER BY c.date DESC
        LIMIT 5
        ''')
        complaint_activity = cursor.fetchall()

        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)

        for activity in customer_activity:
            self.activity_tree.insert('', tk.END, values=activity, tags=('customer',))

        for activity in complaint_activity:
            self.activity_tree.insert('', tk.END, values=activity, tags=('complaint',))

        self.status_var.set("Панель обновлена")

    # Операции с клиентами
    def add_customer(self):
        name = self.customer_name.get()
        address = self.customer_address.get()
        phone = self.customer_phone.get()
        email = self.customer_email.get()
        plan = self.customer_plan.get()

        if not name or not address or not phone or not email:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        try:
            cursor = self.conn.cursor()
            plan_id = None
            if plan:
                plan_id = int(plan.split(' - ')[0])
            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT INTO customers (name, address, phone, email, plan_id, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, address, phone, email, plan_id, registration_date))

            self.conn.commit()
            self.load_customers()
            self.update_dashboard_stats()
            self.clear_customer_form()
            messagebox.showinfo("Успех", "Клиент успешно добавлен")

            self.log_activity(f"Добавлен клиент: {name}")
            self.status_var.set(f"Клиент {name} успешно добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить клиента: {str(e)}")
            self.status_var.set("Ошибка добавления клиента")

    def update_customer(self):
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите клиента для обновления")
            return

        customer_id = self.customers_tree.item(selected[0])['values'][0]
        name = self.customer_name.get()
        address = self.customer_address.get()
        phone = self.customer_phone.get()
        email = self.customer_email.get()
        plan = self.customer_plan.get()

        if not name or not address or not phone or not email:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        try:
            cursor = self.conn.cursor()
            plan_id = None
            if plan:
                plan_id = int(plan.split(' - ')[0])
            cursor.execute('''
            UPDATE customers 
            SET name=?, address=?, phone=?, email=?, plan_id=?
            WHERE customer_id=?
            ''', (name, address, phone, email, plan_id, customer_id))

            self.conn.commit()
            self.load_customers()
            self.update_dashboard_stats()
            messagebox.showinfo("Успех", "Данные клиента обновлены")

            self.log_activity(f"Обновлён клиент: {name}")
            self.status_var.set(f"Клиент {name} обновлён")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить клиента: {str(e)}")
            self.status_var.set("Ошибка обновления клиента")

    def delete_customer(self):
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите клиента для удаления")
            return

        customer_id = self.customers_tree.item(selected[0])['values'][0]
        customer_name = self.customers_tree.item(selected[0])['values'][1]

        if not messagebox.askyesno("Подтверждение", f"Удалить клиента {customer_name}?"):
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM complaints WHERE customer_id=?', (customer_id,)),
            cursor.execute('DELETE FROM billing WHERE customer_id=?', (customer_id,))
            cursor.execute('DELETE FROM customers WHERE customer_id=?', (customer_id,))

            self.conn.commit()
            self.load_customers()
            self.load_complaints()
            self.load_bills()
            self.update_dashboard_stats()
            self.clear_customer_form()
            messagebox.showinfo("Успех", "Клиент удалён")

            self.log_activity(f"Удалён клиент: {customer_name}")
            self.status_var.set(f"Клиент {customer_name} удалён")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить клиента: {str(e)}")
            self.status_var.set("Ошибка удаления клиента")

    def clear_customer_form(self):
        self.customer_name.delete(0, tk.END)
        self.customer_address.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)
        self.customer_plan.set('')
        self.status_var.set("Форма клиента очищена")

    def on_customer_select(self, event):
        selected = self.customers_tree.selection()
        if not selected:
            return

        values = self.customers_tree.item(selected[0])['values']
        self.clear_customer_form()

        self.customer_name.insert(0, values[1])
        self.customer_address.insert(0, values[2])
        self.customer_phone.insert(0, values[3])
        self.customer_email.insert(0, values[4])

        if values[5]:
            for plan in self.customer_plan['values']:
                if values[5] in plan:
                    self.customer_plan.set(plan)
                    break

        self.status_var.set(f"Выбран клиент: {values[1]}")

    # Операции с тарифами
    def add_plan(self):
        name = self.plan_name.get()
        speed = self.plan_speed.get()
        price = self.plan_price.get()
        data_limit = self.plan_data_limit.get()
        description = self.plan_description.get()

        if not name or not speed or not price:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        try:
            price_float = float(price)
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO plans (name, speed, price, data_limit, description)
            VALUES (?, ?, ?, ?, ?)
            ''', (name, speed, price_float, data_limit, description))

            self.conn.commit()
            self.load_plans()
            self.update_dashboard_stats()
            self.clear_plan_form()
            messagebox.showinfo("Успех", "Тариф добавлен")

            self.log_activity(f"Добавлен тариф: {name}")
            self.status_var.set(f"Тариф {name} добавлен")
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            self.status_var.set("Ошибка: цена должна быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить тариф: {str(e)}")
            self.status_var.set("Ошибка добавления тарифа")

    def update_plan(self):
        selected = self.plans_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите тариф для обновления")
            return

        plan_id = self.plans_tree.item(selected[0])['values'][0]
        name = self.plan_name.get()
        speed = self.plan_speed.get()
        price = self.plan_price.get()
        data_limit = self.plan_data_limit.get()
        description = self.plan_description.get()

        if not name or not speed or not price:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        try:
            price_float = float(price)
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE plans 
            SET name=?, speed=?, price=?, data_limit=?, description=?
            WHERE plan_id=?
            ''', (name, speed, price_float, data_limit, description, plan_id))

            self.conn.commit()
            self.load_plans()
            self.load_customers()
            self.update_dashboard_stats()
            messagebox.showinfo("Успех", "Тариф обновлён")

            self.log_activity(f"Обновлён тариф: {name}")
            self.status_var.set(f"Тариф {name} обновлён")
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            self.status_var.set("Ошибка: цена должна быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить тариф: {str(e)}")
            self.status_var.set("Ошибка обновления тарифа")

    def delete_plan(self):
        selected = self.plans_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите тариф для удаления")
            return

        plan_id = self.plans_tree.item(selected[0])['values'][0]
        plan_name = self.plans_tree.item(selected[0])['values'][1]

        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM customers WHERE plan_id=?', (plan_id,))
        customer_count = cursor.fetchone()[0]

        if customer_count > 0:
            messagebox.showerror("Ошибка", f"Нельзя удалить тариф. {customer_count} клиентов его используют.")
            self.status_var.set(f"Нельзя удалить тариф — используется {customer_count} клиентами")
            return

        if not messagebox.askyesno("Подтверждение", f"Удалить тариф {plan_name}?"):
            return

        try:
            cursor.execute('DELETE FROM plans WHERE plan_id=?', (plan_id,))
            self.conn.commit()
            self.load_plans()
            self.update_dashboard_stats()
            self.clear_plan_form()
            messagebox.showinfo("Успех", "Тариф удалён")

            self.log_activity(f"Удалён тариф: {plan_name}")
            self.status_var.set(f"Тариф {plan_name} удалён")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить тариф: {str(e)}")
            self.status_var.set("Ошибка удаления тарифа")

    def clear_plan_form(self):
        self.plan_name.delete(0, tk.END)
        self.plan_speed.delete(0, tk.END)
        self.plan_price.delete(0, tk.END)
        self.plan_data_limit.delete(0, tk.END)
        self.plan_description.delete(0, tk.END)
        self.status_var.set("Форма тарифа очищена")

    def on_plan_select(self, event):
        selected = self.plans_tree.selection()
        if not selected:
            return

        values = self.plans_tree.item(selected[0])['values']
        self.clear_plan_form()

        self.plan_name.insert(0, values[1])
        self.plan_speed.insert(0, values[2])
        self.plan_price.insert(0, values[3])
        self.plan_data_limit.insert(0, values[4])
        self.plan_description.insert(0, values[5])

        self.status_var.set(f"Выбран тариф: {values[1]}")

    # Операции с обращениями
    def add_complaint(self):
        customer = self.complaint_customer.get()
        description = self.complaint_description.get("1.0", tk.END).strip()
        status = self.complaint_status.get() or 'Открыто'

        if not customer or not description:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT customer_id FROM customers WHERE name=?', (customer,))
            customer_row = cursor.fetchone()

            if not customer_row:
                messagebox.showerror("Ошибка", "Клиент не найден")
                return

            customer_id = customer_row[0]
            complaint_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT INTO complaints (customer_id, description, date, status)
            VALUES (?, ?, ?, ?)
            ''', (customer_id, description, complaint_date, status))

            self.conn.commit()
            self.load_complaints()
            self.update_dashboard_stats()
            self.clear_complaint_form()
            messagebox.showinfo("Успех", "Обращение добавлено")

            self.log_activity(f"Добавлено обращение: {customer}")
            self.status_var.set(f"Добавлено обращение для {customer}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить обращение: {str(e)}")
            self.status_var.set("Ошибка добавления обращения")

    def update_complaint(self):
        selected = self.complaints_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите обращение для обновления")
            return

        complaint_id = self.complaints_tree.item(selected[0])['values'][0]
        customer = self.complaint_customer.get()
        description = self.complaint_description.get("1.0", tk.END).strip()
        status = self.complaint_status.get()
        resolution = self.complaint_resolution.get("1.0", tk.END).strip()

        if not customer or not description:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT customer_id FROM customers WHERE name=?', (customer,))
            customer_row = cursor.fetchone()

            if not customer_row:
                messagebox.showerror("Ошибка", "Клиент не найден")
                return

            customer_id = customer_row[0]
            cursor.execute('''
            UPDATE complaints 
            SET customer_id=?, description=?, status=?, resolution=?
            WHERE complaint_id=?
            ''', (customer_id, description, status, resolution, complaint_id))

            self.conn.commit()
            self.load_complaints()
            self.update_dashboard_stats()
            messagebox.showinfo("Успех", "Обращение обновлено")

            self.log_activity(f"Обновлено обращение #{complaint_id}")
            self.status_var.set(f"Обращение #{complaint_id} обновлено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить обращение: {str(e)}")
            self.status_var.set("Ошибка обновления обращения")

    def resolve_complaint(self):
        selected = self.complaints_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите обращение для закрытия")
            return

        complaint_id = self.complaints_tree.item(selected[0])['values'][0]
        resolution = self.complaint_resolution.get("1.0", tk.END).strip()

        if not resolution:
            messagebox.showerror("Ошибка", "Введите решение перед отметкой как решённое")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE complaints 
            SET status='Решено', resolution=?
            WHERE complaint_id=?
            ''', (resolution, complaint_id))

            self.conn.commit()
            self.load_complaints()
            self.update_dashboard_stats()
            messagebox.showinfo("Успех", "Обращение отмечено как решённое")

            self.log_activity(f"Решено обращение #{complaint_id}")
            self.status_var.set(f"Обращение #{complaint_id} решено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось закрыть обращение: {str(e)}")
            self.status_var.set("Ошибка закрытия обращения")

    def clear_complaint_form(self):
        self.complaint_customer.set('')
        self.complaint_description.delete("1.0", tk.END)
        self.complaint_status.set('Открыто')
        self.complaint_resolution.delete("1.0", tk.END)
        self.status_var.set("Форма обращения очищена")

    def on_complaint_select(self, event):
        selected = self.complaints_tree.selection()
        if not selected:
            return

        values = self.complaints_tree.item(selected[0])['values']
        self.clear_complaint_form()

        self.complaint_customer.set(values[1])
        self.complaint_description.insert("1.0", values[4])
        self.complaint_status.set(values[3])

        cursor = self.conn.cursor()
        cursor.execute('SELECT resolution FROM complaints WHERE complaint_id=?', (values[0],))
        resolution = cursor.fetchone()

        if resolution and resolution[0]:
            self.complaint_resolution.insert("1.0", resolution[0])

        self.status_var.set(f"Выбрано обращение #{values[0]}")

    # Операции со счетами
    def generate_bill(self):
        customer = self.billing_customer.get()
        amount = self.billing_amount.get()
        due_date = self.billing_due_date.get()

        if not customer or not amount or not due_date:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        try:
            amount_float = float(amount)
            cursor = self.conn.cursor()
            cursor.execute('SELECT customer_id FROM customers WHERE name=?', (customer,))
            customer_row = cursor.fetchone()

            if not customer_row:
                messagebox.showerror("Ошибка", "Клиент не найден")
                return

            customer_id = customer_row[0]
            cursor.execute('''
            INSERT INTO billing (customer_id, amount, due_date)
            VALUES (?, ?, ?)
            ''', (customer_id, amount_float, due_date))

            self.conn.commit()
            self.load_bills()
            self.clear_billing_form()
            messagebox.showinfo("Успех", "Счёт создан")

            self.log_activity(f"Создан счёт для: {customer}")
            self.status_var.set(f"Счёт создан для {customer}")
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом")
            self.status_var.set("Ошибка: сумма должна быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать счёт: {str(e)}")
            self.status_var.set("Ошибка создания счёта")

    def mark_bill_paid(self):
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите счёт для отметки оплаты")
            return

        bill_id = self.bills_tree.item(selected[0])['values'][0]
        customer = self.bills_tree.item(selected[0])['values'][1]

        if self.bills_tree.item(selected[0])['values'][4] == 'Оплачен':
            messagebox.showinfo("Информация", "Этот счёт уже отмечен как оплаченный")
            return

        try:
            cursor = self.conn.cursor()
            payment_date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
            UPDATE billing 
            SET paid=1, payment_date=?
            WHERE bill_id=?
            ''', (payment_date, bill_id))

            self.conn.commit()
            self.load_bills()
            messagebox.showinfo("Успех", "Счёт отмечен как оплаченный")

            self.log_activity(f"Счёт #{bill_id} отмечен оплаченным для {customer}")
            self.status_var.set(f"Счёт #{bill_id} оплачен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отметить оплату: {str(e)}")
            self.status_var.set("Ошибка отметки оплаты")

    def clear_billing_form(self):
        self.billing_customer.set('')
        self.billing_amount.delete(0, tk.END)
        self.billing_due_date.delete(0, tk.END)
        self.status_var.set("Форма счёта очищена")

    def on_bill_select(self, event):
        selected = self.bills_tree.selection()
        if not selected:
            return

        values = self.bills_tree.item(selected[0])['values']
        self.clear_billing_form()

        self.billing_customer.set(values[1])
        self.billing_amount.insert(0, values[2])
        self.billing_due_date.insert(0, values[3])

        self.status_var.set(f"Выбран счёт #{values[0]}")

    # Диагностика
    def run_troubleshooting(self):
        issue = self.issue_var.get()

        if not issue:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите проблему для диагностики")
            return

        self.results_text.delete(1.0, tk.END)
        self.schedule_button.config(state=tk.DISABLED)

        steps = []

        if issue == "no_connection":
            steps.extend([
                "1. Проверьте, включён ли роутер и индикаторы горят нормально.",
                "2. Перезагрузите роутер: отключите питание на 30 секунд и включите снова.",
                "3. Проверьте все кабельные соединения между устройствами и роутером.",
                "4. Подключите другое устройство, чтобы исключить проблему конкретного устройства.",
                "5. Уточните, нет ли аварии/работ в вашем районе."
            ])
        elif issue == "slow_speed":
            steps.extend([
                "1. Запустите тест скорости (например, speedtest.net) и зафиксируйте результат.",
                "2. Перезагрузите роутер и модем.",
                "3. Отключите устройства, которые могут расходовать полосу пропускания.",
                "4. Подключитесь по Ethernet, чтобы исключить проблему Wi-Fi.",
                "5. Проверьте фоновые загрузки/обновления на устройствах."
            ])
        elif issue == "intermittent":
            steps.extend([
                "1. Проверьте, нет ли ослабленных или повреждённых кабелей.",
                "2. Переставьте роутер в центральную точку вдали от помех.",
                "3. Смените Wi-Fi-канал, чтобы избежать перегрузки.",
                "4. Обновите прошивку роутера.",
                "5. Отслеживайте, не проявляется ли проблема в определённое время суток."
            ])
        elif issue == "specific_website":
            steps.extend([
                "1. Проверьте, не лежит ли сайт у всех (например, downdetector.com).",
                "2. Откройте сайт в другом браузере.",
                "3. Очистите кэш и cookies браузера.",
                "4. Попробуйте с другого устройства/сети.",
                "5. Проверьте настройки фаервола/антивируса."
            ])
        elif issue == "router":
            steps.extend([
                "1. Сделайте power-cycle роутера (обесточьте на 30 секунд).",
                "2. Проверьте наличие обновлений прошивки.",
                "3. При необходимости выполните сброс к заводским настройкам.",
                "4. Убедитесь, что роутер не перегревается (обеспечьте вентиляцию).",
                "5. Проверьте работу индикаторов."
            ])

        steps.append("\nЕсли проблема не решена — рекомендуется помощь техника.")

        self.results_text.insert(tk.END, "\n".join(steps))
        self.schedule_button.config(state=tk.NORMAL)

        self.log_activity(f"Диагностика выполнена: {issue}")
        self.status_var.set(f"Выполнена диагностика: {issue.replace('_', ' ')}")

    def schedule_technician(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM customers')
        customers = [row[0] for row in cursor.fetchall()]

        if not customers:
            messagebox.showerror("Ошибка", "Нет клиентов для назначения визита")
            return

        schedule_dialog = tk.Toplevel(self.root)
        schedule_dialog.title("Назначение визита техника")
        schedule_dialog.geometry("400x300")
        schedule_dialog.resizable(False, False)

        window_width = schedule_dialog.winfo_reqwidth()
        window_height = schedule_dialog.winfo_reqheight()
        position_right = int(schedule_dialog.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(schedule_dialog.winfo_screenheight() / 2 - window_height / 2)
        schedule_dialog.geometry(f"+{position_right}+{position_down}")

        ttk.Label(schedule_dialog, text="Клиент:").pack(pady=5)
        customer_var = tk.StringVar()
        customer_dropdown = ttk.Combobox(schedule_dialog, textvariable=customer_var, values=customers)
        customer_dropdown.pack(pady=5, padx=10, fill=tk.X)

        ttk.Label(schedule_dialog, text="Дата (ГГГГ-ММ-ДД):").pack(pady=5)
        date_entry = ttk.Entry(schedule_dialog)
        date_entry.pack(pady=5, padx=10, fill=tk.X)

        ttk.Label(schedule_dialog, text="Время (ЧЧ:ММ):").pack(pady=5)
        time_entry = ttk.Entry(schedule_dialog)
        time_entry.pack(pady=5, padx=10, fill=tk.X)

        ttk.Label(schedule_dialog, text="Описание проблемы:").pack(pady=5)
        issue_text = tk.Text(schedule_dialog, height=5, width=40)
        issue_text.pack(pady=5, padx=10, fill=tk.X)

        def confirm_schedule():
            customer = customer_var.get()
            date = date_entry.get()
            time = time_entry.get()
            issue = issue_text.get("1.0", tk.END).strip()

            if not customer or not date or not time or not issue:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")
                return

            messagebox.showinfo("Назначено",
                                f"Визит техника назначен для {customer} на {date} в {time}\n\nПроблема: {issue}")
            schedule_dialog.destroy()

            self.log_activity(f"Назначен визит техника: {customer}")
            self.status_var.set(f"Техник назначен: {customer}")

        ttk.Button(schedule_dialog, text="Назначить", command=confirm_schedule).pack(pady=10, padx=10, fill=tk.X)

    # Вспомогательное: лог активности
    def log_activity(self, activity):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'клиент' in activity.lower():
            tag = 'customer'
        elif 'тариф' in activity.lower():
            tag = 'plan'
        elif 'обращен' in activity.lower() or 'техник' in activity.lower():
            tag = 'complaint'
        elif 'счёт' in activity.lower() or 'счет' in activity.lower():
            tag = 'billing'
        else:
            tag = ''

        self.activity_tree.insert('', 0, values=(activity.split(':')[0], activity, timestamp), tags=(tag,))
