from tkinter import *
from tkinter import messagebox
from constants import K, PL_BD_NAME
from MainWindow import *
from Sql import SqlBd
import os

class MenuWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("Окно авторизации")
        width, height = 300, 300
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)

        self.btn_entry = Button(self, text="Войти", font=("Segoe UI", 15),
                               command=lambda: self.button_click(1))
        self.btn_entry.pack(expand=True, fill=BOTH, padx=10 * K, pady=10 * K)

        self.btn_registrion = Button(self, text="Зарегистрироваться", font=("Segoe UI", 15),
                               command=lambda: self.button_click(2))
        self.btn_registrion.pack(expand=True, fill=BOTH, padx=10 * K, pady=10 * K)

        self.btn_exit = Button(self, text="Выход", font=("Segoe UI", 15),
                               command=lambda: self.button_click(3))
        self.btn_exit.pack(expand=True, fill=BOTH, padx=10 * K, pady=10 * K)

    def button_click(self, type):
        if type == 2:
            self.withdraw()
            RegistrationWindow(self)
        elif type == 1:
            self.withdraw()
            EntryWindow(self)
        elif type == 3:
            self.destroy()
        else:
            print(f"Передан неверный параметр type {type}")

class RegistrationWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.bd = SqlBd(PL_BD_NAME)
        self.bd.create_table(f"""
            CREATE TABLE {PL_BD_NAME} (
                login VARCHAR(45),
                password VARCHAR(45)
            );
        """)
        self.title("Регистрация")
        width, height = 320, 340
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)

        for c in range(2): self.columnconfigure(index=c, weight=1)
        for r in range(6): self.rowconfigure(index=r, weight=1)

        self.lbl_login = Label(self, text="Введите логин: ", font=("Segoe UI", 11))
        self.lbl_login.grid(column=0, row=0, sticky="NSEW", padx=10 * K, pady=6)

        self.entry_login = Entry(self, justify="center", font=("Segoe UI", 11))
        self.entry_login.grid(column=1, row=0, sticky="EW", padx=10 * K, pady=6)

        self.lbl_password = Label(self, text="Введите пароль: ", font=("Segoe UI", 11))
        self.lbl_password.grid(column=0, row=1, sticky="NSEW", padx=5 * K, pady=6)

        self.entry_password = Entry(self, show="*", justify="center", font=("Segoe UI", 11))
        self.entry_password.grid(column=1, row=1, sticky="EW", padx=10 * K, pady=6)

        self.lbl_password2 = Label(self, text="Повторите пароль: ", font=("Segoe UI", 11))
        self.lbl_password2.grid(column=0, row=2, sticky="NSEW", padx=5 * K, pady=6)

        self.entry_password2 = Entry(self, show="*", justify="center", font=("Segoe UI", 11))
        self.entry_password2.grid(column=1, row=2, sticky="EW", padx=10 * K, pady=6)

        self.enabled = IntVar()
        self.check_btn = Checkbutton(self, text="Запомнить данные", variable=self.enabled, font=("Segoe UI", 11))
        self.check_btn.grid(column=0, row=3, columnspan=2, sticky="S", padx=10 * K, pady=6)

        self.btn_reg = Button(self, text="Зарегистрироваться", font=("Segoe UI", 15),
                             command=lambda: self.click_registration(
                                 self.entry_login.get(),
                                 self.entry_password.get(),
                                 self.entry_password2.get()))
        self.btn_reg.grid(column=0, row=4, columnspan=2, sticky="NSEW", padx=10 * K, pady=8)

        self.btn_back = Button(self, text="Назад", font=("Segoe UI", 15), command=self.click_back)
        self.btn_back.grid(column=0, row=5, columnspan=2, sticky="NSEW", padx=10 * K, pady=8)

    def click_registration(self, login, password, password2):
        if not self.check_login(login):
            return
        if not self.check_password(password):
            return
        if password != password2:
            messagebox.showinfo(title="Ошибка", message="Пароли не совпадают!")
            return

        if self.enabled.get():
            self.remember_user(login, password)
        else:
            if os.path.exists("user_data.txt"):
                os.remove("user_data.txt")
        self.bd.set_data(f"""INSERT INTO {PL_BD_NAME} (login, password) 
            VALUES ('{login}', '{password}')""")
        messagebox.showinfo(title="Регистрация", message="Регистрация прошла успешно! Введите пароль.")
        self.destroy()
        EntryWindow(self.master, initial_login=login)

    def check_login(self, login):
        if not (6 <= len(login) <= 20):
            messagebox.showinfo(title="Неверный логин", message="Длина логина должна быть от 6 до 20 символов!")
            return False
        if login[0] in "0123456789":
            messagebox.showinfo(title="Неверный логин", message="Логин не должен начинаться с цифр!")
            return False
        users_logins = self.bd.select_request(f"SELECT * FROM {PL_BD_NAME}")
        for lg in users_logins:
            if lg[0] == login:
                messagebox.showinfo(title="Неверный логин", message="Такой логин уже занят!")
                return False
        return True

    def check_password(self, password):
        alp = "qwertyuioplkjhgfdsazxcvbnm"
        russian_alp = "йцукенгшщзхъэждлорпавыфячсмитьбюё"
        numbers = "0123456789"
        if not (6 <= len(password) <= 20):
            messagebox.showinfo(title="Неверный пароль", message="Длина пароля должна быть от 6 до 20 символов!")
            return False
        numbers_count = sum(password.count(num) for num in numbers)
        if numbers_count == 0:
            messagebox.showinfo(title="Неверный пароль", message="Пароль должен содержать цифры!")
            return False
        alp_lower = sum(password.count(ch) for ch in alp)
        alp_upper = sum(password.count(ch.upper()) for ch in alp)
        if alp_lower == 0 or alp_upper == 0:
            messagebox.showinfo(title="Неверный пароль", message="Пароль должен содержать латинские буквы в разных регистрах!")
            return False
        if any(c in password.lower() for c in russian_alp):
            messagebox.showinfo(title="Неверный пароль", message="Пароль не должен содержать русские буквы!")
            return False
        return True

    def click_back(self):
        self.destroy()
        self.master.deiconify()

    def remember_user(self, login, password):
        with open("user_data.txt", "w") as f:
            f.write(login + " " + password)

class EntryWindow(Toplevel):
    def __init__(self, master, initial_login=""):
        super().__init__(master)
        self.master = master
        self.enabled = IntVar()
        login = ""
        password = ""
        if initial_login:
            login = initial_login
            self.enabled.set(0)
        elif os.path.isfile("user_data.txt"):
            with open("user_data.txt", "r") as f:
                login, password = f.readline().split()
            self.enabled.set(1)
        else:
            self.enabled.set(0)
        self.bd = SqlBd(PL_BD_NAME)
        self.bd.create_table(f"""
            CREATE TABLE {PL_BD_NAME} (
                login VARCHAR(45),
                password VARCHAR(45)
            );
        """)
        self.title("Вход")
        width, height = 300, 300
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)

        for c in range(2): self.columnconfigure(index=c, weight=1)
        for r in range(5): self.rowconfigure(index=r, weight=1)

        self.lbl_login = Label(self, text="Введите логин: ", font=("Segoe UI", 11))
        self.lbl_login.grid(column=0, row=0, sticky="NSEW", padx=10 * K, pady=10 * K)

        self.entry_login = Entry(self, justify="center", font=("Segoe UI", 11))
        self.entry_login.insert(0, login)
        self.entry_login.grid(column=1, row=0, sticky="EW", padx=10 * K, pady=10 * K)

        self.lbl_password = Label(self, text="Введите пароль: ", font=("Segoe UI", 11))
        self.lbl_password.grid(column=0, row=1, sticky="NSEW", padx=5 * K, pady=10 * K)

        self.entry_password = Entry(self, show="*", justify="center", font=("Segoe UI", 11))
        self.entry_password.insert(0, password)
        self.entry_password.grid(column=1, row=1, sticky="EW", padx=10 * K, pady=10 * K)

        self.check_btn = Checkbutton(self, text="Запомнить данные", variable=self.enabled, font=("Segoe UI", 11))
        self.check_btn.grid(column=0, row=2, columnspan=2, sticky="S", padx=10 * K, pady=10 * K)

        self.btn_entry = Button(self, text="Войти", font=("Segoe UI", 15),
                               command=lambda: self.click_entry(self.entry_login.get(), self.entry_password.get()))
        self.btn_entry.grid(column=0, row=3, columnspan=2, sticky="NSEW", padx=10 * K, pady=10 * K)

        self.btn_back = Button(self, text="Назад", font=("Segoe UI", 15), command=self.click_back)
        self.btn_back.grid(column=0, row=4, columnspan=2, sticky="NSEW", padx=10 * K, pady=10 * K)

    def click_entry(self, login, password):
        if self.check_data(login, password):
            if self.enabled.get():
                self.remember_user(login, password)
            else:
                if os.path.exists("user_data.txt"):
                    os.remove("user_data.txt")
            self.destroy()               # Закрываем окно входа
            self.master.destroy()        # <-- Закрываем MenuWindow, чтобы не висел
            MainWindow(login)            # Открываем главное окно приложения
        else:
            messagebox.showinfo(title="Ошибка", message="Неверный логин или пароль!")

    def check_data(self, login, password):
        users_data = self.bd.select_request(f"SELECT * FROM {PL_BD_NAME}")
        for l, p in users_data:
            if l == login and p == password:
                return True
        return False

    def click_back(self):
        self.destroy()
        self.master.deiconify()

    def remember_user(self, login, password):
        with open("user_data.txt", "w") as f:
            f.write(login + " " + password)
