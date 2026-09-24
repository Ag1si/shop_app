"""
Модуль моделей данных.

Содержит классы Customer, Product, Order и их наследников.
Демонстрирует инкапсуляцию, наследование и полиморфизм.
"""

import re
from datetime import datetime


class Person:
    """Базовый класс для людей (наследование)."""

    def __init__(self, name: str):
        """
        Parameters
        ----------
        name : str
            Имя человека.
        """
        self._name = name

    @property
    def name(self) -> str:
        """Имя (инкапсуляция через property)."""
        return self._name

    def __str__(self) -> str:
        return self._name


class Customer(Person):
    """Клиент интернет-магазина."""

    EMAIL_RE = re.compile(r"^[\w\.\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
    PHONE_RE = re.compile(r"^\+?\d{10,15}$")

    def __init__(self, name: str, email: str, phone: str, customer_id: int | None = None):
        """
        Parameters
        ----------
        name : str
            Имя клиента.
        email : str
            Email клиента.
        phone : str
            Телефон клиента.
        customer_id : int, optional
            Идентификатор.
        """
        super().__init__(name)
        if not self.validate_email(email):
            raise ValueError(f"Некорректный email: {email}")
        if not self.validate_phone(phone):
            raise ValueError(f"Некорректный телефон: {phone}")
        self._email = email
        self._phone = phone
        self.id = customer_id

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Проверка email регулярным выражением."""
        return bool(cls.EMAIL_RE.match(email or ""))

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Проверка телефона регулярным выражением."""
        return bool(cls.PHONE_RE.match(phone or ""))

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> str:
        return self._phone

    def to_dict(self) -> dict:
        """Сериализация в словарь."""
        return {"id": self.id, "name": self.name, "email": self.email, "phone": self.phone}

    def __repr__(self) -> str:
        return f"Customer(id={self.id}, name={self.name!r}, email={self.email!r})"


class Product:
    """Товар."""

    def __init__(self, name: str, price: float, product_id: int | None = None):
        """
        Parameters
        ----------
        name : str
            Название товара.
        price : float
            Цена товара.
        product_id : int, optional
            Идентификатор.
        """
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        self.id = product_id
        self.name = name
        self.price = float(price)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "price": self.price}

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name!r}, price={self.price})"


class Order:
    """Заказ клиента."""

    def __init__(self, customer_id: int, date: str, items: list[tuple[int, int]],
                 order_id: int | None = None):
        """
        Parameters
        ----------
        customer_id : int
            ID клиента.
        date : str
            Дата в формате YYYY-MM-DD.
        items : list[tuple[int, int]]
            Список (product_id, quantity).
        order_id : int, optional
            ID заказа.
        """
        self.id = order_id
        self.customer_id = customer_id
        self.date = date
        self.items = items

    def total(self, prices: dict[int, float]) -> float:
        """
        Стоимость заказа.

        Parameters
        ----------
        prices : dict[int, float]
            Словарь product_id -> price.
        """
        return sum(prices.get(pid, 0.0) * qty for pid, qty in self.items)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "date": self.date,
            "items": self.items,
        }

    def __repr__(self) -> str:
        return f"Order(id={self.id}, customer_id={self.customer_id}, date={self.date!r})"


class OnlineOrder(Order):
    """Онлайн-заказ (полиморфизм: другой способ расчёта)."""

    def total(self, prices: dict[int, float]) -> float:
        """Стоимость онлайн-заказа со скидкой 5%."""
        base = super().total(prices)
        return round(base * 0.95, 2)


class VipCustomer(Customer):
    """VIP-клиент с бонусом (наследование)."""

    def __init__(self, *args, discount: float = 0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self.discount = discount

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["discount"] = self.discount
        return d


# ------------------ Сортировки ------------------

def bubble_sort_orders(orders: list[Order], key=lambda o: o.date) -> list[Order]:
    """
    Собственная сортировка (пузырьком).

    Parameters
    ----------
    orders : list[Order]
    key : callable

    Returns
    -------
    list[Order]
    """
    arr = list(orders)
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if key(arr[j]) > key(arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def quick_sort_orders(orders: list[Order], key=lambda o: o.date) -> list[Order]:
    """
    Рекурсивная быстрая сортировка.

    Parameters
    ----------
    orders : list[Order]
    key : callable

    Returns
    -------
    list[Order]
    """
    if len(orders) <= 1:
        return list(orders)
    pivot = orders[len(orders) // 2]
    left = [o for o in orders if key(o) < key(pivot)]
    mid = [o for o in orders if key(o) == key(pivot)]
    right = [o for o in orders if key(o) > key(pivot)]
    return quick_sort_orders(left, key) + mid + quick_sort_orders(right, key)


def parse_date(s: str) -> datetime:
    """Парсинг даты с обработкой ошибок."""
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Неверный формат даты: {s}") from e