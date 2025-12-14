Отлично! Делаем **CarService** — автосервис с учётом заказ-нарядов, полностью на **PyQt6 + SQLAlchemy 2.0**, без веба и фреймворков. Вот готовый, рабочий каркас проекта с чётким разделением ответственности и ручным подходом.

---

## 📁 Структура проекта

```
car_service/
├─ config.py
├─ models.py
├─ crud.py
├─ views/
│  ├─ __init__.py
│  ├─ main_window.py
│  ├─ order_dialog.py
├─ main.py
└─ requirements.txt
```

---

## 📄 `requirements.txt`

```txt
PyQt6==6.7.*
SQLAlchemy==2.0.*
```

Установка:  
```bash
pip install -r requirements.txt
```

---

## 🔑 `config.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Путь к БД в корне проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "service.db")

# Создаём engine (SQLite)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Создаём sessionmaker (не сессию!)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

## 🧱 `models.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    car_info = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Добавим позже, если понадобятся связанные таблицы (например, запчасти, работы)

    def __repr__(self):
        return f"<Order(id={self.id}, customer='{self.customer_name}', car='{self.car_info}')>"
```

---

## 🛠 `crud.py`

```python
from sqlalchemy.orm import Session
from models import Order

class OrderCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create_order(self, customer_name: str, car_info: str, description: str = None) -> Order:
        order = Order(
            customer_name=customer_name,
            car_info=car_info,
            description=description
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def get_all_orders(self) -> list[Order]:
        return self.session.query(Order).order_by(Order.id.desc()).all()

    def get_order_by_id(self, order_id: int) -> Order | None:
        return self.session.query(Order).filter(Order.id == order_id).first()

    def update_order(self, order_id: int, customer_name: str, car_info: str, description: str = None) -> Order | None:
        order = self.get_order_by_id(order_id)
        if order:
            order.customer_name = customer_name
            order.car_info = car_info
            order.description = description
            self.session.commit()
            self.session.refresh(order)
        return order

    def delete_order(self, order_id: int) -> bool:
        order = self.get_order_by_id(order_id)
        if order:
            self.session.delete(order)
            self.session.commit()
            return True
        return False
```

---

## 👁 `views/__init__.py`

Пустой файл — нужен для импорта.

---

## 🖥 `views/main_window.py`

```python
from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QToolBar, QPushButton, QMessageBox, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from views.order_dialog import OrderDialog
from crud import OrderCRUD
from config import SessionLocal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CarService — Заказ-наряды")
        self.resize(800, 500)

        # Сессия
        self.session = SessionLocal()
        self.crud = OrderCRUD(self.session)

        # Модель для таблицы
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Клиент", "Авто", "Описание"])

        # Таблица
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_row_double_clicked)

        # Кнопки
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_order)
        self.edit_btn = QPushButton("Изменить")
        self.edit_btn.clicked.connect(self.edit_selected)
        self.del_btn = QPushButton("Удалить")
        self.del_btn.clicked.connect(self.delete_selected)

        # Панель инструментов
        toolbar = QToolBar()
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.del_btn)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        # Центральный виджет
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Загрузка данных
        self.load_data()

    def load_data(self):
        self.model.removeRows(0, self.model.rowCount())
        orders = self.crud.get_all_orders()
        for order in orders:
            row = [
                QStandardItem(str(order.id)),
                QStandardItem(order.customer_name),
                QStandardItem(order.car_info),
                QStandardItem(order.description or ""),
            ]
            for item in row:
                item.setEditable(False)
            self.model.appendRow(row)

    def add_order(self):
        dialog = OrderDialog()
        if dialog.exec():
            data = dialog.get_data()
            self.crud.create_order(
                customer_name=data["customer"],
                car_info=data["car"],
                description=data["description"]
            )
            self.load_data()

    def get_selected_order_id(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ в таблице.")
            return None
        row = indexes[0].row()
        return int(self.model.item(row, 0).text())

    def edit_selected(self):
        order_id = self.get_selected_order_id()
        if order_id is None:
            return
        order = self.crud.get_order_by_id(order_id)
        if not order:
            return

        dialog = OrderDialog(
            customer=order.customer_name,
            car=order.car_info,
            description=order.description
        )
        if dialog.exec():
            data = dialog.get_data()
            self.crud.update_order(
                order_id=order_id,
                customer_name=data["customer"],
                car_info=data["car"],
                description=data["description"]
            )
            self.load_data()

    def delete_selected(self):
        order_id = self.get_selected_order_id()
        if order_id is None:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот заказ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.crud.delete_order(order_id)
            self.load_data()

    def on_row_double_clicked(self, index):
        self.edit_selected()

    def closeEvent(self, event):
        self.session.close()
        event.accept()
```

---

## ✍️ `views/order_dialog.py`

```python
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox, QVBoxLayout, QWidget
)

class OrderDialog(QDialog):
    def __init__(self, customer="", car="", description=""):
        super().__init__()
        self.setWindowTitle("Заказ-наряд")

        self.customer_input = QLineEdit(customer)
        self.car_input = QLineEdit(car)
        self.desc_input = QTextEdit(description)

        form = QFormLayout()
        form.addRow("Клиент:", self.customer_input)
        form.addRow("Авто:", self.car_input)
        form.addRow("Описание работ:", self.desc_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        # Валидация при нажатии OK
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.validate)

    def validate(self):
        if not self.customer_input.text().strip() or not self.car_input.text().strip():
            self.customer_input.setStyleSheet("border: 1px solid red")
            self.car_input.setStyleSheet("border: 1px solid red")
            return
        self.accept()

    def get_data(self):
        return {
            "customer": self.customer_input.text().strip(),
            "car": self.car_input.text().strip(),
            "description": self.desc_input.toPlainText().strip()
        }
```

---

## 🚀 `main.py`

```python
import sys
import os
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from models import Base
from config import engine

# Создаём таблицы при первом запуске
if not os.path.exists("service.db"):
    Base.metadata.create_all(bind=engine)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
```

---

## ✅ Как запустить

1. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запусти:
   ```bash
   python main.py
   ```

---

## 🔒 Заметки

- Все сессии открываются и закрываются вручную в `MainWindow`.
- Нет глобального синглтона — каждый компонент управляет своей сессией.
- SQLite используется как файл `service.db` в корне проекта.
- Поддержка двойного клика по строке → редактирование.
- Простая валидация: клиент и авто — обязательны.

---

Хочешь расширить? Можно добавить:
- Фильтрацию по дате/клиенту
- Экспорт в Excel
- Историю изменений
- Связанные таблицы: «Работы», «Запчасти», «Мастера»

Готов помочь с любым шагом! 🛠