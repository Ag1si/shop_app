"""
GUI на tkinter для системы учёта заказов.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models import Customer, Product, Order
from storage import ExcelStorage
import analysis


class ShopApp(tk.Tk):
    """Главное окно приложения."""

    def __init__(self, storage: ExcelStorage):
        super().__init__()
        self.storage = storage
        self.title("Учёт заказов — интернет-магазин (Excel)")
        self.geometry("980x640")

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_customers = ttk.Frame(nb)
        self.tab_products = ttk.Frame(nb)
        self.tab_orders = ttk.Frame(nb)
        self.tab_analysis = ttk.Frame(nb)

        nb.add(self.tab_customers, text="Клиенты")
        nb.add(self.tab_products, text="Товары")
        nb.add(self.tab_orders, text="Заказы")
        nb.add(self.tab_analysis, text="Анализ")

        self._build_customers_tab()
        self._build_products_tab()
        self._build_orders_tab()
        self._build_analysis_tab()

    # ---------- Клиенты ----------
    def _build_customers_tab(self):
        f = self.tab_customers
        form = ttk.LabelFrame(f, text="Новый клиент")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Имя:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.c_name = ttk.Entry(form, width=25)
        self.c_name.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Email:").grid(row=0, column=2, sticky="w", padx=5)
        self.c_email = ttk.Entry(form, width=25)
        self.c_email.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Телефон:").grid(row=0, column=4, sticky="w", padx=5)
        self.c_phone = ttk.Entry(form, width=15)
        self.c_phone.grid(row=0, column=5, padx=5)

        ttk.Button(form, text="Добавить", command=self.add_customer).grid(row=0, column=6, padx=5)

        search_frame = ttk.Frame(f)
        search_frame.pack(fill="x", padx=10)
        ttk.Label(search_frame, text="Поиск:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_customers).pack(side="left")
        ttk.Button(search_frame, text="Сбросить", command=self.refresh_customers).pack(side="left", padx=5)

        btns = ttk.Frame(f)
        btns.pack(fill="x", padx=10, pady=5)
        ttk.Button(btns, text="Экспорт CSV", command=self.export_customers_csv).pack(side="left")
        ttk.Button(btns, text="Импорт CSV", command=self.import_customers_csv).pack(side="left", padx=5)
        ttk.Button(btns, text="Удалить выбранного", command=self.delete_customer).pack(side="left", padx=5)

        cols = ("id", "name", "email", "phone")
        self.cust_tree = ttk.Treeview(f, columns=cols, show="headings", height=15)
        for c in cols:
            self.cust_tree.heading(c, text=c)
            self.cust_tree.column(c, width=180)
        self.cust_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def add_customer(self):
        """Добавить клиента с обработкой ошибок."""
        try:
            c = Customer(self.c_name.get().strip(),
                         self.c_email.get().strip(),
                         self.c_phone.get().strip())
            self.storage.add_customer(c)
            self.c_name.delete(0, "end")
            self.c_email.delete(0, "end")
            self.c_phone.delete(0, "end")
            self.refresh_customers()
            messagebox.showinfo("OK", "Клиент добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить: {e}")

    def refresh_customers(self, data=None):
        self.cust_tree.delete(*self.cust_tree.get_children())
        for c in (data if data is not None else self.storage.get_customers()):
            self.cust_tree.insert("", "end", values=(c.id, c.name, c.email, c.phone))

    def search_customers(self):
        self.refresh_customers(self.storage.search_customers(self.search_var.get()))

    def delete_customer(self):
        sel = self.cust_tree.selection()
        if not sel:
            return
        cid = self.cust_tree.item(sel[0])["values"][0]
        try:
            self.storage.delete_customer(int(cid))
            self.refresh_customers()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def export_customers_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.storage.export_customers_csv(path)
            messagebox.showinfo("OK", f"Экспортировано в {path}")

    def import_customers_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            n = self.storage.import_customers_csv(path)
            self.refresh_customers()
            messagebox.showinfo("OK", f"Импортировано: {n}")

    # ---------- Товары ----------
    def _build_products_tab(self):
        f = self.tab_products
        form = ttk.LabelFrame(f, text="Новый товар")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Название:").grid(row=0, column=0, padx=5)
        self.p_name = ttk.Entry(form, width=30)
        self.p_name.grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Цена:").grid(row=0, column=2, padx=5)
        self.p_price = ttk.Entry(form, width=15)
        self.p_price.grid(row=0, column=3, padx=5)
        ttk.Button(form, text="Добавить", command=self.add_product).grid(row=0, column=4, padx=5)

        cols = ("id", "name", "price")
        self.prod_tree = ttk.Treeview(f, columns=cols, show="headings", height=18)
        for c in cols:
            self.prod_tree.heading(c, text=c)
            self.prod_tree.column(c, width=200)
        self.prod_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def add_product(self):
        try:
            p = Product(self.p_name.get().strip(), float(self.p_price.get()))
            self.storage.add_product(p)
            self.p_name.delete(0, "end")
            self.p_price.delete(0, "end")
            self.refresh_products()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_products(self):
        self.prod_tree.delete(*self.prod_tree.get_children())
        for p in self.storage.get_products():
            self.prod_tree.insert("", "end", values=(p.id, p.name, p.price))

    # ---------- Заказы ----------
    def _build_orders_tab(self):
        f = self.tab_orders
        form = ttk.LabelFrame(f, text="Новый заказ")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Клиент:").grid(row=0, column=0, padx=5)
        self.o_customer = ttk.Combobox(form, width=25, state="readonly")
        self.o_customer.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Дата (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        self.o_date = ttk.Entry(form, width=15)
        self.o_date.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Товар:").grid(row=1, column=0, padx=5, pady=5)
        self.o_product = ttk.Combobox(form, width=25, state="readonly")
        self.o_product.grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Кол-во:").grid(row=1, column=2, padx=5)
        self.o_qty = ttk.Entry(form, width=10)
        self.o_qty.grid(row=1, column=3, padx=5)

        ttk.Button(form, text="Добавить позицию", command=self.add_item).grid(row=1, column=4, padx=5)
        ttk.Button(form, text="Создать заказ", command=self.create_order).grid(row=1, column=5, padx=5)

        self.items_list = tk.Listbox(f, height=6)
        self.items_list.pack(fill="x", padx=10, pady=5)
        self.current_items = []

        sort_frame = ttk.Frame(f)
        sort_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(sort_frame, text="Сортировать по дате (bubble)",
                   command=lambda: self.refresh_orders("date")).pack(side="left")
        ttk.Button(sort_frame, text="Сортировать по ID",
                   command=lambda: self.refresh_orders("id")).pack(side="left", padx=5)

        cols = ("id", "customer", "date", "items", "total")
        self.order_tree = ttk.Treeview(f, columns=cols, show="headings", height=12)
        for c in cols:
            self.order_tree.heading(c, text=c)
            self.order_tree.column(c, width=150)
        self.order_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def add_item(self):
        try:
            product_label = self.o_product.get()
            qty = int(self.o_qty.get())
            if qty <= 0:
                raise ValueError("Количество должно быть > 0")
            pid = int(product_label.split("|")[0].strip())
            self.current_items.append((pid, qty))
            self.items_list.insert("end", f"{product_label} x{qty}")
            self.o_qty.delete(0, "end")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def create_order(self):
        try:
            cust_label = self.o_customer.get()
            if not cust_label:
                raise ValueError("Выберите клиента")
            cid = int(cust_label.split("|")[0].strip())
            date = self.o_date.get().strip()
            if not self.current_items:
                raise ValueError("Добавьте позиции")
            order = Order(customer_id=cid, date=date, items=self.current_items)
            self.storage.add_order(order)
            self.current_items = []
            self.items_list.delete(0, "end")
            self.refresh_orders()
            messagebox.showinfo("OK", "Заказ создан")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_orders(self, sort_by: str | None = None):
        self.order_tree.delete(*self.order_tree.get_children())
        orders = self.storage.get_orders()
        customers = {c.id: c.name for c in self.storage.get_customers()}
        prices = {p.id: p.price for p in self.storage.get_products()}

        if sort_by == "date":
            from models import bubble_sort_orders
            orders = bubble_sort_orders(orders, key=lambda o: o.date)
        elif sort_by == "id":
            orders = sorted(orders, key=lambda o: o.id or 0)

        for o in orders:
            items_str = ", ".join(f"{pid}x{qty}" for pid, qty in o.items)
            self.order_tree.insert("", "end", values=(
                o.id, customers.get(o.customer_id, "?"), o.date, items_str, o.total(prices)
            ))

    # ---------- Анализ ----------
    def _build_analysis_tab(self):
        f = self.tab_analysis
        ttk.Label(f, text="Аналитика и визуализация",
                  font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Button(f, text="Топ-5 клиентов",
                   command=lambda: analysis.plot_top_customers(self.storage, 5)
                   ).pack(pady=5, fill="x", padx=50)
        ttk.Button(f, text="Динамика заказов по датам",
                   command=lambda: analysis.plot_sales_dynamics(self.storage)
                   ).pack(pady=5, fill="x", padx=50)
        ttk.Button(f, text="Граф клиент-товар",
                   command=lambda: analysis.plot_customer_product_graph(self.storage)
                   ).pack(pady=5, fill="x", padx=50)

        ttk.Button(f, text="Экспорт всех данных JSON",
                   command=self.export_json).pack(pady=15, fill="x", padx=50)
        ttk.Button(f, text="Импорт JSON",
                   command=self.import_json).pack(pady=5, fill="x", padx=50)

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            self.storage.export_all_json(path)
            messagebox.showinfo("OK", f"Сохранено: {path}")

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            self.storage.import_all_json(path)
            self.refresh_all()

    # ---------- Общее ----------
    def refresh_all(self):
        self.refresh_customers()
        self.refresh_products()
        self.refresh_orders()
        self._refresh_comboboxes()

    def _refresh_comboboxes(self):
        custs = self.storage.get_customers()
        self.o_customer["values"] = [f"{c.id} | {c.name}" for c in custs]
        prods = self.storage.get_products()
        self.o_product["values"] = [f"{p.id} | {p.name} ({p.price})" for p in prods]