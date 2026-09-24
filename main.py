"""
Точка входа приложения.
"""

from storage import ExcelStorage
from gui import ShopApp


def main():
    """Запуск GUI."""
    storage = ExcelStorage()
    app = ShopApp(storage)
    app.mainloop()


if __name__ == "__main__":
    main()