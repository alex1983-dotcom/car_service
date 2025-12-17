from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QToolBar, QPushButton, QMessageBox, QVBoxLayout, QWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from views.order_dialog import OrderDialog
from crud import OrderCRUD
from config import get_db_session


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 500)


        # это невидимый контейнер для данных таблицы
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Клиент", "Авто", "Описание"])

        # это видимая таблица
        self.table = QTableView()
        self.table.setModel(self.model)

        # пользователь может видеть только целые строки, а не отдельные ячейки
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # чтобы пользователь не мог случайно что-то поменять
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        # это сигнал: это сигнал, когда пользователь дважды кликает по строке - вызывается метод `on_row_double_clicked`
        self.table.doubleClicked.connect(self.on_row_double_clicked)

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_order)
        self.edit_btn = QPushButton("Изменить")
        self.edit_btn.clicked.connect(self.edit_selected)
        self.del_btn = QPushButton("Удалить")
        self.del_btn.clicked.connect(self.delete_selected)

        toolbar = QToolBar()
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.del_btn)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        central_widget = QWidget()
        layout = QVBoxLayout() # макет
        layout.addWidget(self.table)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.load_data()

    def load_data(self):
        self.model.removeRows(0, self.model.rowCount())
        with get_db_session() as session:
            orders = OrderCRUD.get_all_orders(session)
        for order in orders:
            row = [
                QStandardItem(str(order.id)),
                QStandardItem(order.customer_name),
                QStandardItem(order.car_info),
                QStandardItem(order.description or "")
            ]
            for item in row:
                item.setEditable(False)
            self.model.appendRow(row)



