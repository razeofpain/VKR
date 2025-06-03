from tkinter import *
from tkinter import ttk, messagebox
from constants import K, BD_NAME
from Sql import SqlBd
import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MainWindow(Tk):
    def __init__(self, user):
        super().__init__()

        self.user = "_" + user
        self.bd = SqlBd(BD_NAME + self.user)
        self.bd.create_table(f"""
            CREATE TABLE IF NOT EXISTS {BD_NAME + self.user} (
                data VARCHAR(45),
                category VARCHAR(45),
                sum VARCHAR(45),
                type VARCHAR(45),
                comment VARCHAR(90)
            );
        """)

        self.update_balance_from_db()

        self.title("Учет финансов")
        self.state('zoomed')
        self.configure(bg="#f4f4f4")

        self.style = ttk.Style(self)
        self.style.configure("Treeview", font=("Segoe UI", 11), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        header = Label(self, text="Учет финансов", font=("Segoe UI", 20, "bold"), bg="#f4f4f4")
        header.pack(pady=(20, 5))

        # --- Диаграммы и итоги ---
        self.diagram_frame = Frame(self, bg="#f4f4f4")
        self.diagram_frame.pack(pady=(5, 10), fill="both")

        self.expense_panel = Frame(self.diagram_frame, bg="#f4f4f4")
        self.expense_panel.pack(side="left", expand=True, fill="both", padx=(30, 15))

        self.expense_canvas = Frame(self.expense_panel, bg="#f4f4f4")
        self.expense_canvas.pack(fill="both", expand=True)
        self.expense_sum_lbl = Label(self.expense_panel, text="", font=("Segoe UI", 13, "bold"), bg="#f4f4f4")
        self.expense_sum_lbl.pack(pady=(5, 10))

        self.income_panel = Frame(self.diagram_frame, bg="#f4f4f4")
        self.income_panel.pack(side="left", expand=True, fill="both", padx=(15, 30))

        self.income_canvas = Frame(self.income_panel, bg="#f4f4f4")
        self.income_canvas.pack(fill="both", expand=True)
        self.income_sum_lbl = Label(self.income_panel, text="", font=("Segoe UI", 13, "bold"), bg="#f4f4f4")
        self.income_sum_lbl.pack(pady=(5, 10))

        self.balance_lbl = Label(self, text=f"Текущий баланс: {self.balance} руб.", font=("Segoe UI", 16, "bold"), bg="#f4f4f4")
        self.balance_lbl.pack(pady=(0, 20))

        # --- Форма ввода ---
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(form_frame, text="Сумма:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.sum_entry = Entry(form_frame, font=("Segoe UI", 12), justify="center", width=15)
        self.sum_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)

        ttk.Label(form_frame, text="Категория:", font=("Segoe UI", 12)).grid(row=0, column=2, sticky="e", padx=5, pady=5)

        self.expense_categories = [
            "Продукты", "ЖКХ", "Проезд", "Одежда и обувь", "Здоровье/Красота", "Подарки", "Отдых/Путешествие",
            "Бытовая химия", "Медицина", "Спорт", "Связь/Интернет", "Развлечения", "Автомобиль", "Платеж по кредиту",
            "Ремонт", "Аренда жилья", "Отпуск"
        ]
        self.income_categories = [
            "Заработная плата", "Премия", "Пособия", "Стипендия", "Пенсия", "Дивиденды",
            "Прибыль от занятия бизнесом", "проценты от сбережений в банке"
        ]

        self.expense_combobox = ttk.Combobox(form_frame, values=self.expense_categories, state="readonly", font=("Segoe UI", 12))
        self.expense_combobox.current(0)
        self.expense_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="we")

        self.income_combobox = ttk.Combobox(form_frame, values=self.income_categories, state="readonly", font=("Segoe UI", 12))
        self.income_combobox.current(0)
        self.income_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="we")
        self.income_combobox.grid_remove()

        ttk.Label(form_frame, text="Комментарий:", font=("Segoe UI", 12)).grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.comment_entry = Entry(form_frame, font=("Segoe UI", 12), justify="center", width=20)
        self.comment_entry.grid(row=0, column=5, sticky="we", padx=5, pady=5)

        form_frame.columnconfigure(3, weight=1)
        form_frame.columnconfigure(5, weight=2)

        self.r_var = StringVar(value="Расход")
        rb_frame = ttk.Frame(self)
        rb_frame.pack(pady=5)
        ttk.Radiobutton(rb_frame, text="Расход", variable=self.r_var, value="Расход", command=self.toggle_category).pack(side="left", padx=10)
        ttk.Radiobutton(rb_frame, text="Доход", variable=self.r_var, value="Доход", command=self.toggle_category).pack(side="left", padx=10)

        btn_frame = Frame(self, bg="#f4f4f4")
        btn_frame.pack(pady=8)
        Button(btn_frame, text="Добавить запись", font=("Segoe UI", 12), command=self.add_data).pack(side="left", padx=10)
        Button(btn_frame, text="Редактировать запись", font=("Segoe UI", 12), command=self.edit_data).pack(side="left", padx=10)
        Button(btn_frame, text="Удалить запись", font=("Segoe UI", 12), command=self.delete_data).pack(side="left", padx=10)

        table_frame = ttk.Frame(self)
        table_frame.pack(padx=20, pady=20, fill="both", expand=True)

        columns = ["Дата", "Категория", "Сумма", "Тип", "Комментарий"]
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.table.heading(col, text=col, command=lambda c=col: self.sort_by_column(c, False))
            self.table.column(col, anchor="center")
        self.table.pack(fill="both", expand=True)

        datas = self.bd.select_request(f"SELECT * FROM {BD_NAME + self.user}")
        for data in datas:
            self.table.insert("", END, values=data)

        self.create_diagram()

    def toggle_category(self):
        if self.r_var.get() == "Доход":
            self.expense_combobox.grid_remove()
            self.income_combobox.grid()
        else:
            self.income_combobox.grid_remove()
            self.expense_combobox.grid()

    def sort_by_column(self, col, reverse):
        data = [(self.table.set(k, col), k) for k in self.table.get_children("")]
        try:
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (_, k) in enumerate(data):
            self.table.move(k, '', index)
        self.table.heading(col, command=lambda: self.sort_by_column(col, not reverse))

    def add_data(self):
        data = datetime.datetime.now().strftime("%Y-%m-%d")
        category = self.income_combobox.get() if self.r_var.get() == "Доход" else self.expense_combobox.get()
        sm = self.sum_entry.get()
        comment = self.comment_entry.get()

        if sm == "":
            messagebox.showinfo(title="Ошибка", message="Введите сумму")
            return
        try:
            sm = abs(int(sm))
        except ValueError:
            messagebox.showinfo(title="Ошибка", message="Сумма должна быть числом")
            return

        t = self.r_var.get()

        values = [data, category, sm, t, comment]
        self.table.insert("", END, values=values)
        self.bd.set_data(f"""INSERT INTO {BD_NAME + self.user} (data, category, sum, type, comment) 
            VALUES ('{data}', '{category}', '{sm}', '{t}', '{comment}')""")

        self.update_balance()
        self.create_diagram()

    def edit_data(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Редактирование", "Сначала выберите запись для редактирования.")
            return

        old_values = self.table.item(selected[0])['values']

        # --- Новое окно, центр, увеличенный размер ---
        edit_width, edit_height = 600, 380
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (edit_width // 2)
        y = (screen_height // 2) - (edit_height // 2)

        edit_window = Toplevel(self)
        edit_window.title("Редактировать запись")
        edit_window.geometry(f"{edit_width}x{edit_height}+{x}+{y}")
        edit_window.resizable(False, False)
        edit_window.grab_set()
        font_label = ("Segoe UI", 13, "bold")
        font_entry = ("Segoe UI", 13)

        for i in range(5):
            edit_window.rowconfigure(i, weight=1, pad=16)
        for i in range(2):
            edit_window.columnconfigure(i, weight=1, pad=12)

        Label(edit_window, text="Дата (гггг-мм-дд):", font=font_label).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        date_entry = Entry(edit_window, font=font_entry, justify="center")
        date_entry.insert(0, old_values[0])
        date_entry.grid(row=0, column=1, sticky="we", padx=10, pady=10)

        Label(edit_window, text="Категория:", font=font_label).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        category_entry = Entry(edit_window, font=font_entry, justify="center")
        category_entry.insert(0, old_values[1])
        category_entry.grid(row=1, column=1, sticky="we", padx=10, pady=10)

        Label(edit_window, text="Сумма:", font=font_label).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        sum_entry = Entry(edit_window, font=font_entry, justify="center")
        sum_entry.insert(0, old_values[2])
        sum_entry.grid(row=2, column=1, sticky="we", padx=10, pady=10)

        Label(edit_window, text="Тип (Доход/Расход):", font=font_label).grid(row=3, column=0, sticky="e", padx=10, pady=10)
        type_entry = Entry(edit_window, font=font_entry, justify="center")
        type_entry.insert(0, old_values[3])
        type_entry.grid(row=3, column=1, sticky="we", padx=10, pady=10)

        Label(edit_window, text="Комментарий:", font=font_label).grid(row=4, column=0, sticky="e", padx=10, pady=10)
        comment_entry = Entry(edit_window, font=font_entry, justify="center")
        comment_entry.insert(0, old_values[4])
        comment_entry.grid(row=4, column=1, sticky="we", padx=10, pady=10)

        def save_edit():
            if not messagebox.askyesno("Подтверждение", "Сохранить изменения?"):
                return
            new_values = [
                date_entry.get(),
                category_entry.get(),
                sum_entry.get(),
                type_entry.get(),
                comment_entry.get()
            ]
            self.bd.set_data(f"""
                UPDATE {BD_NAME + self.user}
                SET data='{new_values[0]}', category='{new_values[1]}', sum='{new_values[2]}', type='{new_values[3]}', comment='{new_values[4]}'
                WHERE data='{old_values[0]}' AND category='{old_values[1]}' AND sum='{old_values[2]}' AND type='{old_values[3]}' AND comment='{old_values[4]}'
            """)
            self.table.item(selected[0], values=new_values)
            edit_window.destroy()
            self.update_balance()
            self.create_diagram()

        Button(edit_window, text="Сохранить изменения", font=("Segoe UI", 13, "bold"), bg="#4caf50", fg="white",
               command=save_edit).grid(row=5, column=0, columnspan=2, sticky="we", padx=20, pady=18)

    def delete_data(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Удаление", "Сначала выберите запись для удаления.")
            return
        if not messagebox.askyesno("Подтвердите удаление", "Удалить выбранную запись?"):
            return

        values = self.table.item(selected[0])['values']
        self.table.delete(selected[0])

        self.bd.set_data(f"""DELETE FROM {BD_NAME + self.user} 
            WHERE data='{values[0]}' AND category='{values[1]}' AND sum='{values[2]}' AND type='{values[3]}' AND comment='{values[4]}'""")

        self.update_balance()
        self.create_diagram()

    def update_balance(self):
        records = self.bd.select_request(f"SELECT sum, type FROM {BD_NAME + self.user}")
        balance = 0
        for sm, t in records:
            try:
                sm = int(sm)
            except ValueError:
                continue
            if t == "Доход":
                balance += sm
            else:
                balance -= sm
        self.balance_lbl.config(text=f"Текущий баланс: {balance} руб.")
        self.balance = balance

    def update_balance_from_db(self):
        records = self.bd.select_request(f"SELECT sum, type FROM {BD_NAME + self.user}")
        balance = 0
        for sm, t in records:
            try:
                sm = int(sm)
            except ValueError:
                continue
            if t == "Доход":
                balance += sm
            else:
                balance -= sm
        self.balance = balance

    def create_diagram(self):
        for widget in self.expense_canvas.winfo_children():
            widget.destroy()
        for widget in self.income_canvas.winfo_children():
            widget.destroy()

        datas = [self.table.item(i)["values"] for i in self.table.get_children()]
        expenses = {}
        incomes = {}

        for row in datas:
            if len(row) < 4: continue
            _, category, sm, typ = row[:4]
            try:
                sm = int(sm)
            except ValueError:
                continue
            if typ == "Доход":
                incomes[category] = incomes.get(category, 0) + sm
            else:
                expenses[category] = expenses.get(category, 0) + sm

        # --- Диаграмма расходов ---
        fig1 = Figure(figsize=(5.2, 3.5), dpi=100)
        ax1 = fig1.add_subplot(111)
        ax1.set_title("Диаграмма учета расходов")
        total_expense = sum(expenses.values())
        if expenses and total_expense > 0:
            wedges1, _ = ax1.pie(expenses.values(), labels=None, autopct=None)
            ax1.legend(wedges1, expenses.keys(), loc='center left', bbox_to_anchor=(1, 0.5), fontsize=11)
            legend_text = "\n".join([f"{cat}: {val} руб." for cat, val in expenses.items()])
            fig1.text(0.08, 0.5, legend_text, ha='left', va='center', fontsize=11,
                      bbox=dict(facecolor='#f4f4f4', alpha=0.85, boxstyle="round"))
        else:
            ax1.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=12)
        canvas1 = FigureCanvasTkAgg(fig1, master=self.expense_canvas)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, pady=10)
        self.expense_sum_lbl.config(
            text=f"Итого расходов: {total_expense} руб." if total_expense > 0 else "")

        # --- Диаграмма доходов ---
        fig2 = Figure(figsize=(5.2, 3.5), dpi=100)
        ax2 = fig2.add_subplot(111)
        ax2.set_title("Диаграмма учета доходов")
        total_income = sum(incomes.values())
        if incomes and total_income > 0:
            wedges2, _ = ax2.pie(incomes.values(), labels=None, autopct=None)
            ax2.legend(wedges2, incomes.keys(), loc='center left', bbox_to_anchor=(1, 0.5), fontsize=11)
            legend_text = "\n".join([f"{cat}: {val} руб." for cat, val in incomes.items()])
            fig2.text(0.08, 0.5, legend_text, ha='left', va='center', fontsize=11,
                      bbox=dict(facecolor='#f4f4f4', alpha=0.85, boxstyle="round"))
        else:
            ax2.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=12)
        canvas2 = FigureCanvasTkAgg(fig2, master=self.income_canvas)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, pady=10)
        self.income_sum_lbl.config(
            text=f"Итого доходов: {total_income} руб." if total_income > 0 else "")

