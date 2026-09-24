# Система учёта заказов (Excel + tkinter)

Прототип промышленной системы учёта заказов, клиентов и товаров
для менеджеров интернет-магазина.

## Возможности

- Регистрация клиентов и их контактных данных (email и телефон проверяются через regex).
- Добавление товаров и заказов.
- Просмотр, поиск и сортировка заказов (пузырьковая и быстрая сортировка).
- Экспорт и импорт данных в CSV и JSON.
- Визуализация: топ-5 клиентов, динамика заказов, граф связей «клиент — товар».
- Данные хранятся в Excel-файле `data/shop.xlsx` (без SQL).

## Структура проекта

```
shop_app/
├── main.py          # точка входа
├── models.py        # классы Customer, Product, Order, OnlineOrder, VipCustomer
├── storage.py       # ExcelStorage — работа с Excel (замена db.py)
├── gui.py           # tkinter-интерфейс (ShopApp)
├── analysis.py      # pandas + matplotlib + seaborn + networkx
├── requirements.txt
├── data/
│   └── shop.xlsx    # создаётся автоматически при первом запуске
└── tests/
    ├── __init__.py
    ├── test_models.py
    └── test_analysis.py
```

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

## Тесты

```bash
python -m unittest discover tests -v
```

## Технологии

- Python 3.10+
- tkinter (GUI)
- pandas, openpyxl (Excel)
- matplotlib, seaborn, networkx (визуализация)
- unittest (тесты)

## Автор

Ag1si — итоговая аттестация по Python, 2026