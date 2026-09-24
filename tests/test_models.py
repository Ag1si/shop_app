"""Unit-тесты для models.py."""

import unittest
from models import (
    Customer, Product, Order, OnlineOrder,
    bubble_sort_orders, quick_sort_orders, parse_date,
)


class TestCustomer(unittest.TestCase):
    def test_valid_email(self):
        self.assertTrue(Customer.validate_email("a@b.com"))

    def test_invalid_email(self):
        self.assertFalse(Customer.validate_email("bad-email"))

    def test_valid_phone(self):
        self.assertTrue(Customer.validate_phone("+79991234567"))

    def test_invalid_phone(self):
        self.assertFalse(Customer.validate_phone("abc"))

    def test_create_customer(self):
        c = Customer("Иван", "ivan@mail.ru", "+79991234567", 1)
        self.assertEqual(c.name, "Иван")
        self.assertEqual(c.id, 1)

    def test_bad_email_raises(self):
        with self.assertRaises(ValueError):
            Customer("Иван", "bad", "+79991234567")


class TestProduct(unittest.TestCase):
    def test_negative_price(self):
        with self.assertRaises(ValueError):
            Product("X", -1)

    def test_ok(self):
        p = Product("X", 100)
        self.assertEqual(p.price, 100.0)


class TestOrder(unittest.TestCase):
    def test_total(self):
        o = Order(1, "2024-01-01", [(1, 2), (2, 1)])
        self.assertEqual(o.total({1: 10.0, 2: 5.0}), 25.0)

    def test_online_order_discount(self):
        o = OnlineOrder(1, "2024-01-01", [(1, 2)])
        self.assertEqual(o.total({1: 100.0}), 190.0)  # 200 * 0.95

    def test_parse_date(self):
        d = parse_date("2024-01-01")
        self.assertEqual(d.year, 2024)

    def test_parse_bad_date(self):
        with self.assertRaises(ValueError):
            parse_date("not-a-date")

    def test_bubble_sort(self):
        orders = [Order(1, "2024-03-01", []), Order(1, "2024-01-01", []), Order(1, "2024-02-01", [])]
        sorted_orders = bubble_sort_orders(orders)
        self.assertEqual([o.date for o in sorted_orders],
                         ["2024-01-01", "2024-02-01", "2024-03-01"])

    def test_quick_sort(self):
        orders = [Order(1, "2024-03-01", []), Order(1, "2024-01-01", []), Order(1, "2024-02-01", [])]
        sorted_orders = quick_sort_orders(orders)
        self.assertEqual([o.date for o in sorted_orders],
                         ["2024-01-01", "2024-02-01", "2024-03-01"])


if __name__ == "__main__":
    unittest.main()