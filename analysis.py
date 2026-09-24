"""
Модуль анализа и визуализации данных.

Использует pandas, matplotlib, seaborn, networkx.
Строит отчёты и графики по данным из ExcelStorage.

Functions
---------
top_customers(storage, n)
    Топ-N клиентов по числу заказов.
sales_dynamics(storage)
    Динамика количества заказов по датам.
product_sales(storage)
    Топ товаров по суммарному количеству продаж.
plot_top_customers(storage, n)
    Столбчатая диаграмма топ-N клиентов.
plot_sales_dynamics(storage)
    Линейный график динамики заказов.
plot_customer_product_graph(storage)
    Двудольный граф связей клиентов и товаров.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

sns.set_theme(style="whitegrid")


# ---------------------------------------------------------------- #
#                        АНАЛИТИКА (данные)                        #
# ---------------------------------------------------------------- #

def top_customers(storage, n: int = 5) -> pd.DataFrame:
    """
    Топ-N клиентов по числу заказов.

    Parameters
    ----------
    storage : ExcelStorage
        Хранилище с методами get_customers() и get_orders().
    n : int, optional
        Сколько клиентов вернуть. По умолчанию 5.

    Returns
    -------
    pd.DataFrame
        Колонки: customer_id, customer_name, orders_count.
    """
    customers = storage.get_customers()
    orders = storage.get_orders()

    if not customers:
        return pd.DataFrame(columns=["customer_id", "customer_name", "orders_count"])

    counter = {}
    for o in orders:
        counter[o.customer_id] = counter.get(o.customer_id, 0) + 1

    rows = []
    for c in customers:
        rows.append({
            "customer_id": c.id,
            "customer_name": c.name,
            "orders_count": counter.get(c.id, 0),
        })

    df = (pd.DataFrame(rows)
          .sort_values("orders_count", ascending=False)
          .head(n)
          .reset_index(drop=True))
    return df


def sales_dynamics(storage) -> pd.DataFrame:
    """
    Динамика количества заказов по датам.

    Parameters
    ----------
    storage : ExcelStorage

    Returns
    -------
    pd.DataFrame
        Колонки: date, orders_count.
    """
    orders = storage.get_orders()
    if not orders:
        return pd.DataFrame(columns=["date", "orders_count"])

    df = pd.DataFrame([{"date": str(o.date)} for o in orders])
    grouped = df.groupby("date").size().reset_index(name="orders_count")
    return grouped.sort_values("date").reset_index(drop=True)


def product_sales(storage) -> pd.DataFrame:
    """
    Топ товаров по суммарному количеству продаж.

    Parameters
    ----------
    storage : ExcelStorage

    Returns
    -------
    pd.DataFrame
        Колонки: product_id, product_name, quantity.
    """
    products = {p.id: p.name for p in storage.get_products()}
    counter = {}
    for o in storage.get_orders():
        for pid, qty in o.items:
            counter[pid] = counter.get(pid, 0) + qty

    rows = [
        {
            "product_id": pid,
            "product_name": products.get(pid, f"id={pid}"),
            "quantity": qty,
        }
        for pid, qty in counter.items()
    ]
    if not rows:
        return pd.DataFrame(columns=["product_id", "product_name", "quantity"])
    df = pd.DataFrame(rows).sort_values("quantity", ascending=False)
    return df.reset_index(drop=True)


# ---------------------------------------------------------------- #
#                       ВИЗУАЛИЗАЦИЯ (графики)                     #
# ---------------------------------------------------------------- #

def plot_top_customers(storage, n: int = 5):
    """
    Столбчатая диаграмма топ-N клиентов по числу заказов.

    Parameters
    ----------
    storage : ExcelStorage
    n : int, optional
    """
    df = top_customers(storage, n)
    if df.empty:
        print("Нет данных для графика топ-клиентов")
        return

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="customer_name", y="orders_count", palette="viridis")
    plt.title(f"Топ-{n} клиентов по числу заказов")
    plt.xlabel("Клиент")
    plt.ylabel("Число заказов")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()


def plot_sales_dynamics(storage):
    """
    Линейный график динамики количества заказов.

    Parameters
    ----------
    storage : ExcelStorage
    """
    df = sales_dynamics(storage)
    if df.empty:
        print("Нет данных для графика динамики")
        return

    plt.figure(figsize=(9, 5))
    sns.lineplot(data=df, x="date", y="orders_count", marker="o")
    plt.title("Динамика количества заказов по датам")
    plt.xlabel("Дата")
    plt.ylabel("Количество заказов")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


def plot_customer_product_graph(storage):
    """
    Двудольный граф связей «клиент — товар» через networkx.

    Parameters
    ----------
    storage : ExcelStorage
    """
    orders = storage.get_orders()
    products = {p.id: p.name for p in storage.get_products()}
    customers = {c.id: c.name for c in storage.get_customers()}

    if not orders:
        print("Нет данных для графа")
        return

    G = nx.Graph()

    # узлы-клиенты
    for cid, cname in customers.items():
        G.add_node(f"C{cid}", label=cname, type="customer")

    # узлы-товары
    for pid, pname in products.items():
        G.add_node(f"P{pid}", label=pname, type="product")

    # рёбра клиент-товар
    for o in orders:
        for pid, _ in o.items:
            if pid in products:
                G.add_edge(f"C{o.customer_id}", f"P{pid}")

    if G.number_of_edges() == 0:
        print("Нет связей между клиентами и товарами")
        return

    pos = nx.spring_layout(G, seed=42)

    node_colors = [
        "#4C72B0" if G.nodes[node]["type"] == "customer" else "#DD8452"
        for node in G.nodes
    ]

    plt.figure(figsize=(10, 7))
    nx.draw_networkx(
        G, pos,
        node_color=node_colors,
        with_labels=False,
        node_size=600,
        edge_color="gray",
    )
    labels = {node: G.nodes[node]["label"] for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    plt.title("Граф связей клиентов и товаров")
    plt.axis("off")
    plt.tight_layout()
    plt.show()