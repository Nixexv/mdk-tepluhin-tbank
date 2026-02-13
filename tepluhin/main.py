
import tkinter as tk
from tkinter import messagebox
import json, os, random
from datetime import datetime
import qrcode
from PIL import Image, ImageTk

USERS_FILE = "users.json"
CARD_BG = "card_bg.png"
QR_FILE = "generated_qr.png"

# ---------- utils ----------
def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_card():
    return "4276 " + " ".join(
        "".join(str(random.randint(0, 9)) for _ in range(4))
        for _ in range(3)
    )

def placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg="grey")

    def focus_in(e):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.config(fg="black")

    def focus_out(e):
        if not entry.get():
            entry.insert(0, text)
            entry.config(fg="grey")

    entry.bind("<FocusIn>", focus_in)
    entry.bind("<FocusOut>", focus_out)

# ---------- data ----------
users = load_json(USERS_FILE, {})
current_user = None

for u in users:
    users[u].setdefault("card", generate_card())
save_json(USERS_FILE, users)

# ---------- UI ----------
root = tk.Tk()
root.title("Уралсиб")
root.geometry("1000x540")
root.resizable(False, False)

# ---------- QR (появляется по кнопке) ----------
qr_label = None

def generate_qr():
    global qr_label
    img = qrcode.make("https://www.uralsib.ru")
    img.save(QR_FILE)

    qr_img = ImageTk.PhotoImage(
        Image.open(QR_FILE).resize((130, 130))
    )

    if qr_label:
        qr_label.config(image=qr_img)
        qr_label.image = qr_img
    else:
        qr_label = tk.Label(root, image=qr_img, bg="white")
        qr_label.image = qr_img
        qr_label.place(relx=1, x=-20, y=20, anchor="ne")

# ---------- левая панель ----------
left = tk.Frame(root, width=260, bg="#2a163f")
left.pack(side="left", fill="y")

tk.Label(left, text="Уралсиб",
         fg="white", bg="#2a163f",
         font=("Arial", 18, "bold")).pack(pady=20)

entry_login = tk.Entry(left)
entry_login.pack(pady=6)
placeholder(entry_login, "Логин")

entry_pass = tk.Entry(left)
entry_pass.pack(pady=6)
placeholder(entry_pass, "Пароль")

def login():
    global current_user
    u, p = entry_login.get(), entry_pass.get()
    if u in users and users[u]["password"] == p:
        current_user = u
        update_balance()
        card_lbl.config(text=f"💳 {users[u]['card']}")
        messagebox.showinfo("Вход", f"Добро пожаловать, {u}")
    else:
        messagebox.showerror("Ошибка", "Неверные данные")

def register():
    u, p = entry_login.get(), entry_pass.get()
    if u in users:
        messagebox.showerror("Ошибка", "Пользователь существует")
        return
    users[u] = {
        "password": p,
        "balance": 10000,
        "history": [],
        "card": generate_card()
    }
    save_json(USERS_FILE, users)
    messagebox.showinfo("Регистрация",
                        f"Аккаунт создан\n\n💳 {users[u]['card']}")

tk.Button(left, text="ВОЙТИ", command=login).pack(pady=6)
tk.Button(left, text="РЕГИСТРАЦИЯ", command=register).pack()

# ---------- центр ----------
center = tk.Frame(root)
center.pack(expand=True, fill="both")

# фон-карта (ПОДНЯТА ВЫШЕ)


card = tk.Frame(center, bg="white", padx=20, pady=15)
card.pack(pady=40)

balance_lbl = tk.Label(card, text="Баланс: — ₽",
                       font=("Arial", 12, "bold"))
balance_lbl.pack()

card_lbl = tk.Label(card, text="💳 —",
                    font=("Arial", 10))
card_lbl.pack(pady=4)

entry_card = tk.Entry(card)
entry_card.pack(pady=4)
placeholder(entry_card, "Картаполучателя")
entry_amount = tk.Entry(card)
entry_amount.pack(pady=4)
placeholder(entry_amount, "Сумма")

entry_msg = tk.Entry(card)
entry_msg.pack(pady=4)
placeholder(entry_msg, "Сообщение")

def update_balance():
    balance_lbl.config(
        text=f"Баланс: {users[current_user]['balance']} ₽"
    )

def transfer():
    card_to = entry_card.get()
    if not entry_amount.get().isdigit():
        messagebox.showerror("Ошибка", "Введите сумму")
        return

    amount = int(entry_amount.get())
    receiver = None

    for u in users:
        if users[u]["card"] == card_to:
            receiver = u
            break

    if not receiver:
        messagebox.showerror("Ошибка", "Карта не найдена")
        return

    users[current_user]["balance"] -= amount
    users[receiver]["balance"] += amount

    save_json(USERS_FILE, users)
    update_balance()
    messagebox.showinfo("Успех", "Перевод выполнен")

tk.Button(card, text="ПЕРЕВЕСТИ",
          font=("Arial", 11, "bold"),
          command=transfer).pack(pady=6)

# 🔥 КНОПКА QR
tk.Button(card, text="Оплатить по QR",
          command=generate_qr).pack(pady=4)

root.mainloop()