import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

ACCENT = "#5a2ea6"
CTA = "#ff6a3c"
BG_DARK = "#111118"
CARD = "#1c1c26"


class MobileAppPrototype(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Эмуляция экрана смартфона
        self.title("Личный кабинет СКАТ")
        self.geometry("360x640")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        self.customer = None
        self.messages_cache = []
        self.chat_poll_job = None
        self.home_poll_job = None
        self.autopay_enabled = 0

        self.frames = {}
        self.create_login_screen()
        self.create_home_screen()
        self.create_chat_screen()

        self.show_frame("login")

    # ---------------- UI scaffolding ----------------
    def show_frame(self, name):
        for f in self.frames.values():
            f.pack_forget()
        if name == "chat":
            self.start_chat_polling()
            self.stop_home_polling()
        elif name == "home":
            self.stop_chat_polling()
            self.start_home_polling()
        else:
            self.stop_chat_polling()
            self.stop_home_polling()
        self.frames[name].pack(fill="both", expand=True)
        if name == "login":
            self.phone_entry.focus_set()

    def create_login_screen(self):
        frame = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.frames["login"] = frame

        ctk.CTkLabel(frame, text="СКАТ Провайдер", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(60, 6))
        ctk.CTkLabel(frame, text="Мобильный кабинет абонента", text_color="gray").pack(pady=(0, 35))

        self.phone_entry = ctk.CTkEntry(frame, placeholder_text="Номер телефона (+79...)", width=280, height=45)
        self.phone_entry.pack(pady=12)
        self.phone_entry.bind("<Control-v>", lambda e: self.phone_entry.event_generate("<<Paste>>"))
        self.phone_entry.bind("<Command-v>", lambda e: self.phone_entry.event_generate("<<Paste>>"))
        self.phone_entry.bind("<FocusIn>", lambda e: self.phone_entry.select_range(0, "end"))

        ctk.CTkButton(frame, text="Войти", width=280, height=45, fg_color=ACCENT,
                      command=self.check_login).pack(pady=12)

        self.login_error = ctk.CTkLabel(frame, text="", text_color="#ff6666")
        self.login_error.pack()

    def create_home_screen(self):
        outer = ctk.CTkScrollableFrame(self, fg_color=BG_DARK)
        self.frames["home"] = outer

        top = ctk.CTkFrame(outer, fg_color=CARD)
        top.pack(fill="x", padx=12, pady=(10, 6))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Ваш счет", text_color="lightgray").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        self.lbl_account = ctk.CTkLabel(top, text="", wraplength=260, font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_account.grid(row=1, column=0, sticky="w", padx=10)

        refresh_btn = ctk.CTkButton(top, text="Обновить", width=74, fg_color="#2a2a36",
                                    command=self.load_home_data)
        refresh_btn.grid(row=0, column=2, rowspan=2, padx=6, pady=10)

        chat_btn = ctk.CTkButton(top, text="Чат", width=58, height=34, fg_color=ACCENT, command=lambda: self.show_frame("chat"))
        chat_btn.grid(row=0, column=1, rowspan=2, padx=4, pady=10)

        self.lbl_balance = ctk.CTkLabel(top, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_balance.grid(row=2, column=0, sticky="w", padx=10, pady=(4, 2))
        self.lbl_due = ctk.CTkLabel(top, text="", text_color="lightgray", font=ctk.CTkFont(size=11), wraplength=240, justify="left")
        self.lbl_due.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 8))

        ctk.CTkButton(outer, text="Пополнить счет", fg_color=CTA, hover_color="#ff7f55",
                      height=44, command=self.fake_pay).pack(fill="x", padx=12, pady=6)

        quick = ctk.CTkFrame(outer, fg_color=CARD)
        quick.pack(fill="x", padx=12, pady=6)
        quick.grid_columnconfigure((0, 1, 2), weight=1, uniform="q")
        self.btn_finance = ctk.CTkButton(quick, text="Финансы", fg_color="#2a2a36", height=36,
                                         command=self.show_finance_info)
        self.btn_finance.grid(row=0, column=0, padx=6, pady=10, sticky="ew")
        self.btn_promised = ctk.CTkButton(quick, text="Обещанный\nплатеж", fg_color="#2a2a36", height=36,
                                          command=self.request_promised_payment)
        self.btn_promised.grid(row=0, column=1, padx=6, pady=10, sticky="ew")
        self.btn_autopay = ctk.CTkButton(quick, text="Автоплатеж\nOFF", fg_color="#2a2a36", height=36,
                                         command=self.toggle_autopay)
        self.btn_autopay.grid(row=0, column=2, padx=6, pady=10, sticky="ew")

        self.services_card = ctk.CTkFrame(outer, fg_color=CARD)
        self.services_card.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(self.services_card, text="Мои услуги", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))
        self.services_body = ctk.CTkLabel(self.services_card, text="", justify="left")
        self.services_body.pack(anchor="w", padx=10, pady=(0, 10))

        actions = ctk.CTkFrame(outer, fg_color=CARD)
        actions.pack(fill="x", padx=12, pady=6)
        actions.grid_columnconfigure((0, 1), weight=1, uniform="act")
        ctk.CTkButton(actions, text="Сменить тариф", fg_color=ACCENT, command=self.request_plan_change).grid(
            row=0, column=0, padx=6, pady=10, sticky="ew")
        ctk.CTkButton(actions, text="Подключить услугу", fg_color="#2a2a36", command=self.request_addon).grid(
            row=0, column=1, padx=6, pady=10, sticky="ew")

        self.requests_card = ctk.CTkFrame(outer, fg_color=CARD)
        self.requests_card.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(self.requests_card, text="Мои заявки", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 4))
        self.requests_body = ctk.CTkLabel(self.requests_card, text="Заявок пока нет", justify="left", wraplength=310)
        self.requests_body.pack(anchor="w", padx=10, pady=(0, 10))

    def create_chat_screen(self):
        frame = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.frames["chat"] = frame

        header = ctk.CTkFrame(frame, fg_color=CARD)
        header.pack(fill="x")
        ctk.CTkButton(header, text="Назад", width=60, fg_color="#2a2a36",
                      command=lambda: self.show_frame("home")).pack(side="left", padx=8, pady=8)
        ctk.CTkLabel(header, text="Служба поддержки", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)

        self.chat_area = ctk.CTkScrollableFrame(frame, fg_color=BG_DARK)
        self.chat_area.pack(fill="both", expand=True, padx=8, pady=6)

        bottom = ctk.CTkFrame(frame, fg_color=CARD)
        bottom.pack(fill="x", padx=8, pady=(0, 8))
        bottom.grid_columnconfigure(0, weight=1)
        self.chat_entry = ctk.CTkEntry(bottom, placeholder_text="Сообщение...", height=40)
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=8)
        ctk.CTkButton(bottom, text="▶", width=50, fg_color=ACCENT, command=self.send_message).grid(row=0, column=1, padx=(0, 8), pady=8)

    # ---------------- Logic ----------------
    def check_login(self):
        phone = self.phone_entry.get().strip()
        if not phone:
            self.login_error.configure(text="Введите номер телефона")
            return
        customer = database.get_customer_by_phone(phone)
        if not customer:
            self.login_error.configure(text="Абонент не найден")
            return
        self.customer = customer
        self.login_error.configure(text="")
        self.load_home_data()
        self.show_frame("home")

    def load_home_data(self):
        if not self.customer:
            return
        cid = self.customer["customer_id"]
        finance = database.get_customer_finance_summary(cid)
        due = finance.get("due") or 0
        self.lbl_account.configure(text=f"Лицевой счет № {cid}")
        self.lbl_balance.configure(text=f"-{due:,.2f} ₽".replace(",", " "))
        next_due = finance.get("next_due")
        due_text = f"К оплате {due:,.2f} ₽"
        if next_due:
            due_text += f"\nдо {next_due}"
        self.lbl_due.configure(text=due_text)
        self.autopay_enabled = database.get_customer_autopay(cid)
        self.btn_autopay.configure(
            text=f"Автоплатеж\n{'ON' if self.autopay_enabled else 'OFF'}",
            fg_color="#1f6a3a" if self.autopay_enabled else "#2a2a36"
        )

        # тариф/услуги
        conn = database.get_connection()
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT p.name, p.speed, p.price
                FROM customers c
                LEFT JOIN plans p ON c.plan_id = p.plan_id
                WHERE c.customer_id = %s
            """, (cid,))
            plan = cur.fetchone()
            cur.close()
            conn.close()
        else:
            plan = None
        if plan and plan["name"]:
            self.services_body.configure(
                text=f"Домашний интернет\nТариф: {plan['name']}\nСкорость: {plan.get('speed')}\nСтоимость: {plan.get('price')} ₽")
        else:
            self.services_body.configure(text="Услуги не назначены")

        requests_rows = database.get_customer_self_service_requests(cid, limit=5)
        if not requests_rows:
            self.requests_body.configure(text="Заявок пока нет")
        else:
            type_map = {
                "promised_payment": "Обещанный платеж",
                "plan_change": "Смена тарифа",
                "addon": "Доп. услуга",
                "autopay": "Автоплатеж"
            }
            lines = []
            for r in requests_rows:
                title = type_map.get(r.get("request_type"), r.get("request_type"))
                status = r.get("status") or "Новая"
                line = f"#{r.get('request_id')} {title}: {status}"
                if r.get("comment"):
                    line += f" ({r.get('comment')})"
                lines.append(line)
            self.requests_body.configure(text="\n".join(lines))

    def render_chat(self, messages):
        for w in self.chat_area.winfo_children():
            w.destroy()
        if not messages:
            ctk.CTkLabel(self.chat_area, text="Диалог пуст. Напишите первым.", text_color="gray").pack(pady=10)
            return
        for msg in messages:
            is_client = msg["sender_type"] == "client"
            wrap = ctk.CTkFrame(self.chat_area, fg_color=BG_DARK)
            wrap.pack(fill="x", pady=4)
            bubble = ctk.CTkFrame(wrap, fg_color=ACCENT if is_client else "#2a2a36", corner_radius=10)
            bubble.pack(anchor="e" if is_client else "w", padx=6)
            ctk.CTkLabel(bubble, text=msg.get("sender_name") or ("Я" if is_client else "Поддержка"),
                         font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=8, pady=(6, 0))
            ctk.CTkLabel(bubble, text=msg["text"], wraplength=250, justify="left").pack(anchor="w", padx=8, pady=4)
            ts = msg["created_at"].strftime("%H:%M %d.%m") if isinstance(msg["created_at"], datetime) else str(msg["created_at"])
            ctk.CTkLabel(bubble, text=ts, text_color="lightgray", font=ctk.CTkFont(size=10)).pack(anchor="e", padx=8, pady=(0, 6))

    def load_messages(self):
        if not self.customer:
            return
        cid = self.customer["customer_id"]
        msgs = database.fetch_messages(cid)
        self.messages_cache = msgs
        self.render_chat(msgs)
        database.mark_messages_read(cid, "client")

    def send_message(self):
        if not self.customer:
            return
        text = self.chat_entry.get().strip()
        if not text:
            return
        database.save_message(self.customer["customer_id"], "client", text, self.customer.get("name"))
        self.chat_entry.delete(0, "end")
        self.load_messages()
        self.load_home_data()  # обновим баланс/состояние на всякий случай

    def start_chat_polling(self):
        self.stop_chat_polling()
        def tick():
            if self.customer:
                latest = database.fetch_messages(self.customer["customer_id"])
                if len(latest) != len(self.messages_cache):
                    self.messages_cache = latest
                    self.render_chat(latest)
                    database.mark_messages_read(self.customer["customer_id"], "client")
            self.chat_poll_job = self.after(3000, tick)
        self.chat_poll_job = self.after(3000, tick)

    def stop_chat_polling(self):
        if self.chat_poll_job:
            self.after_cancel(self.chat_poll_job)
            self.chat_poll_job = None

    def start_home_polling(self):
        self.stop_home_polling()
        def tick():
            if self.customer:
                self.load_home_data()
            self.home_poll_job = self.after(5000, tick)
        self.home_poll_job = self.after(5000, tick)

    def stop_home_polling(self):
        if self.home_poll_job:
            self.after_cancel(self.home_poll_job)
            self.home_poll_job = None

    def fake_pay(self):
        messagebox.showinfo("Пополнение", "Переход к оплате (заглушка).")

    def show_finance_info(self):
        if not self.customer:
            return
        finance = database.get_customer_finance_summary(self.customer["customer_id"])
        due = finance.get("due") or 0
        next_due = finance.get("next_due")
        text = f"К оплате: {due} ₽"
        if next_due:
            text += f"\nСрок оплаты: {next_due}"
        text += f"\nАвтоплатеж: {'включен' if self.autopay_enabled else 'выключен'}"
        messagebox.showinfo("Финансы", text)

    def request_promised_payment(self):
        if not self.customer:
            return
        amount_dialog = ctk.CTkInputDialog(text="Сумма обещанного платежа (₽):", title="Обещанный платеж")
        amount = (amount_dialog.get_input() or "").strip()
        if not amount:
            return
        days_dialog = ctk.CTkInputDialog(text="На сколько дней отсрочка (напр. 5):", title="Обещанный платеж")
        days = (days_dialog.get_input() or "").strip()
        if not days:
            days = "5"
        payload = {"amount": amount, "days": days}
        req_id = database.create_self_service_request(self.customer["customer_id"], "promised_payment", payload,
                                                      actor_name=self.customer.get("name") or "Клиент")
        messagebox.showinfo("Готово", f"Заявка #{req_id} на обещанный платеж отправлена в поддержку.")

    def toggle_autopay(self):
        if not self.customer:
            return
        new_state = 0 if self.autopay_enabled else 1
        database.set_customer_autopay(self.customer["customer_id"], new_state, actor_name=self.customer.get("name") or "Клиент")
        self.autopay_enabled = new_state
        self.btn_autopay.configure(
            text=f"Автоплатеж\n{'ON' if self.autopay_enabled else 'OFF'}",
            fg_color="#1f6a3a" if self.autopay_enabled else "#2a2a36"
        )
        messagebox.showinfo("Автоплатеж", f"Автоплатеж {'включен' if new_state else 'выключен'}.")

    def request_plan_change(self):
        if not self.customer:
            return
        plans = database.get_available_plans()
        if not plans:
            messagebox.showwarning("Тарифы", "Нет доступных тарифов.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Смена тарифа")
        modal.geometry("340x220")
        modal.resizable(False, False)
        ctk.CTkLabel(modal, text="Выберите новый тариф", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(15, 8))
        values = [f"{p['plan_id']} - {p['name']} ({p['speed']}, {p['price']} ₽)" for p in plans]
        combo = ctk.CTkComboBox(modal, values=values, width=300)
        combo.set(values[0])
        combo.pack(pady=8)

        def submit():
            selected = combo.get()
            plan_id = int(selected.split(" - ")[0]) if " - " in selected else None
            req_id = database.create_self_service_request(
                self.customer["customer_id"], "plan_change",
                {"target_plan_id": plan_id, "selected": selected},
                actor_name=self.customer.get("name") or "Клиент"
            )
            modal.destroy()
            messagebox.showinfo("Готово", f"Заявка #{req_id} на смену тарифа отправлена.")

        ctk.CTkButton(modal, text="Отправить заявку", fg_color=ACCENT, command=submit).pack(pady=12)
        ctk.CTkButton(modal, text="Отмена", fg_color="#2a2a36", command=modal.destroy).pack()

    def request_addon(self):
        if not self.customer:
            return
        addon_dialog = ctk.CTkInputDialog(
            text="Какую услугу хотите подключить? (например: Белый IP, Антивирус)",
            title="Подключение услуги"
        )
        addon = (addon_dialog.get_input() or "").strip()
        if not addon:
            return
        req_id = database.create_self_service_request(
            self.customer["customer_id"], "addon", {"service": addon},
            actor_name=self.customer.get("name") or "Клиент"
        )
        messagebox.showinfo("Готово", f"Заявка #{req_id} на подключение услуги отправлена.")


if __name__ == "__main__":
    app = MobileAppPrototype()
    app.mainloop()
