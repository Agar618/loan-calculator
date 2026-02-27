import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ------------------ Helpers ------------------

def mark_invalid(entry):
    entry.config(highlightthickness=2, highlightbackground="red")

def clear_mark(entry):
    entry.config(highlightthickness=0)
def format_percent_live(event):
    entry = event.widget
    raw = entry.get().replace("%", "")

    # If empty → force 0%
    if raw.strip() == "":
        entry.delete(0, tk.END)
        entry.insert(0, "0%")
        entry.icursor(1)
        return

    try:
        float(raw)
    except:
        # remove invalid character
        current = entry.get()
        cursor = entry.index(tk.INSERT)
        entry.delete(cursor-1)
        return

    entry.delete(0, tk.END)
    entry.insert(0, raw + "%")

    # keep cursor before %
    entry.icursor(len(raw))
def format_currency(event):
    entry = event.widget
    value = entry.get().replace(",", "")
    if value == "":
        return
    try:
        number = float(value)
    except:
        return
    entry.delete(0, tk.END)
    entry.insert(0, f"{int(number):,}")

def open_date_picker(entry):

    if hasattr(open_date_picker, "win") and open_date_picker.win.winfo_exists():
        return

    win = tk.Toplevel()
    open_date_picker.win = win
    win.title("Select Date")
    win.resizable(False, False)

    x = entry.winfo_rootx()
    y = entry.winfo_rooty() + entry.winfo_height()
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text="Day").grid(row=0, column=0)
    tk.Label(win, text="Month").grid(row=0, column=1)
    tk.Label(win, text="Year").grid(row=0, column=2)

    day = ttk.Combobox(win, values=list(range(1,32)), width=5, state="readonly")
    month = ttk.Combobox(win, values=list(range(1,13)), width=5, state="readonly")
    year = ttk.Combobox(win, values=list(range(2000,2101)), width=7, state="readonly")

    day.grid(row=1,column=0,padx=5,pady=5)
    month.grid(row=1,column=1,padx=5,pady=5)
    year.grid(row=1,column=2,padx=5,pady=5)

    # ---------- PREFILL VALUES ----------
    try:
        existing = datetime.strptime(entry.get(), "%Y-%m-%d")
    except:
        existing = datetime.today()

    day.set(existing.day)
    month.set(existing.month)
    year.set(existing.year)
    # -------------------------------------

    def set_date():
        entry.delete(0, tk.END)
        entry.insert(0, f"{int(year.get()):04d}-{int(month.get()):02d}-{int(day.get()):02d}")
        win.destroy()

    tk.Button(win, text="Select", command=set_date).grid(row=2,column=0,columnspan=3,pady=10)
def apply_theme(mode):

    entries = [entry_loan, entry_months, entry_rate, entry_start, entry_first]
    frames = [frame, btn_frame, table_frame]

    if mode == "dark":

        root.configure(bg="#1e1e1e")

        for f in frames:
            f.configure(bg="#1e1e1e")

        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b"
        )

        for e in entries:
            e.configure(
                bg="#2b2b2b",
                fg="white",
                insertbackground="white",
                highlightbackground="#555555",
                highlightcolor="#4a90e2",
                highlightthickness=1,
                bd=0
    )

        tree.tag_configure("odd", background="#2b2b2b")
        tree.tag_configure("even", background="#353535")

    else:  # LIGHT MODE

        root.configure(bg="#f0f0f0")

        for f in frames:
            f.configure(bg="#f0f0f0")

        style.configure("TLabel", background="#f0f0f0", foreground="black")
        style.configure("Treeview",
            background="white",
            foreground="black",
            fieldbackground="white"
        )

        for e in entries:
            e.configure(
                bg="white",
                fg="black",
                insertbackground="black",
                highlightbackground="#cccccc",
                highlightcolor="#4a90e2",
                highlightthickness=1,
                bd=0
    )

        tree.tag_configure("odd", background="white")
        tree.tag_configure("even", background="#eaeaea")
# ------------------ Main Logic ------------------

def generate_schedule():

    for row in tree.get_children():
        tree.delete(row)

    entries = [entry_loan, entry_months, entry_rate, entry_start, entry_first]
    for e in entries:
        clear_mark(e)

    # Individual validation
    try:
        loan = float(entry_loan.get().replace(",", ""))
    except:
        mark_invalid(entry_loan)
        messagebox.showerror("Input Error", "Зээлийн дүн буруу байна.")
        return

    try:
        months = int(entry_months.get())
    except:
        mark_invalid(entry_months)
        messagebox.showerror("Input Error", "Төлөх сар буруу байна.")
        return

    try:
        rate = float(entry_rate.get().replace("%","")) / 100
    except:
        mark_invalid(entry_rate)
        messagebox.showerror("Input Error", "Сарын хүү буруу байна.")
        return

    try:
        start_date = datetime.strptime(entry_start.get(), "%Y-%m-%d")
    except:
        mark_invalid(entry_start)
        messagebox.showerror("Input Error", "Эхлэх огноо буруу байна.")
        return

    try:
        pay_date = datetime.strptime(entry_first.get(), "%Y-%m-%d")
    except:
        mark_invalid(entry_first)
        messagebox.showerror("Input Error", "Төлөх өдөр буруу байна.")
        return

    balance = loan
    coef = 0
    cumulative = 1
    temp_date = pay_date

    for i in range(months):
        if i == 0:
            days = (temp_date - start_date).days
        else:
            prev_date = temp_date - relativedelta(months=1)
            days = (temp_date - prev_date).days

        factor = (days * rate * 12 / 365) + 1
        cumulative *= factor
        coef += 1 / cumulative
        temp_date += relativedelta(months=1)

    payment = loan / coef
    current_date = pay_date

    for i in range(months):

        if i == 0:
            days = (current_date - start_date).days
        else:
            prev_date = current_date - relativedelta(months=1)
            days = (current_date - prev_date).days

        interest = balance * (rate * 12 / 365 * days)
        principal = payment - interest

        tag = "even" if i % 2 == 0 else "odd"
        
        tree.insert("", "end", values=(
            i+1,
            current_date.strftime("%Y-%m-%d"),
            days,
            f"{payment:,.2f}",
            f"{interest:,.2f}",
            f"{principal:,.2f}",
            f"{balance:,.2f}"
        ), tags=tag,)

        balance -= principal
        current_date += relativedelta(months=1)
current_theme = "dark"

def toggle_theme():
    global current_theme

    current_theme = "light" if current_theme == "dark" else "dark"
    apply_theme(current_theme)
# ------------------ UI ------------------

root = tk.Tk()
root.configure(bg="white")
style = ttk.Style()
style.theme_use("clam")  # better for custom styling


style.map("Treeview",
    background=[("selected", "#4a6984")],
    foreground=[("selected", "white")]
)
root.geometry("610x500")
root.minsize(500,400)
root.title("Зээлийн хуваарь тооцоолох")

frame = tk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Зээлийн дүн").grid(row=0, column=0)
entry_loan = tk.Entry(frame)
entry_loan.grid(row=0, column=1)
entry_loan.bind("<KeyRelease>", format_currency)

ttk.Label(frame, text="Авсан сар").grid(row=1, column=0)
entry_months = tk.Entry(frame)
entry_months.grid(row=1, column=1)

ttk.Label(frame, text="Сарын хүү").grid(row=2, column=0)
entry_rate = tk.Entry(frame)
entry_rate.bind("<KeyRelease>", format_percent_live)
entry_rate.grid(row=2, column=1)

ttk.Label(frame, text="Авсан өдөр YYYY-MM-DD").grid(row=3, column=0)
entry_start = tk.Entry(frame)
entry_start.grid(row=3, column=1)
entry_start.bind("<Button-1>", lambda e: open_date_picker(entry_start))

ttk.Label(frame, text="Төлж эхлэх өдөр YYYY-MM-DD").grid(row=4, column=0)
entry_first = tk.Entry(frame)
entry_first.grid(row=4, column=1)
entry_first.bind("<Button-1>", lambda e: open_date_picker(entry_first))

today = datetime.today().strftime("%Y-%m-%d")
entry_start.insert(0, today)
entry_first.insert(0, today)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

ttk.Button(btn_frame, text="Тооцоолох", command=generate_schedule).pack(side="left", padx=5)
ttk.Button(btn_frame, text="🌙 / ☀", command=toggle_theme).pack(side="left", padx=5)

# ----- Table Container with Visible Scrollbar -----

table_frame = tk.Frame(root)
table_frame.pack(expand=True, fill="both", padx=10, pady=10)

scrollbar = tk.Scrollbar(table_frame)
scrollbar.pack(side="right", fill="y")

columns = ("№", "Төлөх огноо", "Хоног", "Төлөх дүн", "Хүү", "Үндсэн", "Үлдэгдэл")

tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
tree.tag_configure("odd", background="#2b2b2b")
tree.tag_configure("even", background="#353535")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", stretch=True)

tree.pack(side="left", expand=True, fill="both")

def resize_columns(event):
    total_width = tree.winfo_width()
    col_width = int(total_width / len(columns))
    for col in columns:
        tree.column(col, width=col_width)

tree.bind("<Configure>", resize_columns)
scrollbar.config(command=tree.yview)

apply_theme("dark")

root.mainloop()