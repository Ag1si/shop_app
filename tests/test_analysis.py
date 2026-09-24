"""Unit-тесты для analysis.py (без графиков, только данные)."""

import unittest
import os
import tempfile
from storage import ExcelStorage
from models import Customer, Product, Order
import analysis


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        tmp.close()
        os.unlink(tmp.name)
        self.storage = ExcelStorage(tmp.name)
        self.path = tmp.name

        self.storage.add_customer(Customer("Иван", "i@mail.ru", "+79991234567"))
        self.storage.add_customer(Customer("Пётр", "p@mail.ru", "+79991234568"))
        self.storage.add_product(Product("Товар1", 100))
        self.storage.add_product(Product("Товар2", 200))
        self.storage.add_order(Order(1, "2024-01-01", [(1, 1)]))
        self.storage.add_order(Order(1, "2024-01-02", [(1, 2)]))
        self.storage.add_order(Order(2, "2024-01-03", [(2, 1)]))

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_top_customers(self):
        df = analysis.top_customers(self.storage, n=5)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["customer_name"], "Иван")
        self.assertEqual(df.iloc[0]["orders_count"], 2)

    def test_sales_dynamics(self):
        df = analysis.sales_dynamics(self.storage)
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df["orders_count"]), [1, 1, 1])


if __name__ == "__main__":
    unittest.main()