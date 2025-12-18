from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QToolBar, QPushButton, QMessageBox, QVBoxLayout, QWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from views.order_dialog import OrderDialog
from crud import OrderCRUD
from config import get_db_session


class MainWindow(QMainWindow):
    """
    Стандартное пустое окно в Qt.
    Внутри него все что нужно для работы автосервиса:
    таблица, кнопки, логика загрузки и редактирования.
    """
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

        # это полоска сверху окна куда можно класть кнопки
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
        """
        Загрузка данных
        """
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


    def add_order(self):
        """
        Добавление заказа
        """
        dialog = OrderDialog()
        if dialog.exec():
            data = dialog.get_data()
            with get_db_session() as session:
                OrderCRUD.create_order(
                    session,
                    customer_name=data["customer"],
                    car_info=data["car"],
                    description=data["description"]
                )
            self.load_data()

    def get_selected_order_id(self):
        """
        Получение id выбранного заказа
        """
        indexes =  self.table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ в таблице.")
            return None
        row = indexes[0].row()
        return self.model.item(row, 0).text()

    def edit_selected(self):
        """
        Редактирование данных.
        Почти как add_order, но загружает существующие данные в диалог
        """
        order_id = self.get_selected_order_id()
        if order_id is None:
            return

        with get_db_session() as session:
            order = OrderCRUD.get_order_by_id(session, order_id)
            if not order:
                QMessageBox.warning(self, "Ошибка", "Заказ не найден.")
                return

            dialog = OrderDialog(
                customer=order.custdomer_name,
                car=order.car_info,
                description=order.description
            )
            if dialog.exec():
                data=dialog.get_data()
                OrderCRUD.update_order(
                    session,
                    order_id=order_id,
                    customer_name=data["customer"],
                    car_info=data["car"],
                    description=data["description"]
                )
        self.load_data()

    def delete_selected(self):
        """
        Удаление заказа
        При подтверждении - открывает сессию - удаляет заказ через OrderCRUD.delete_order()
        """
        order_id = self.get_selected_order_id()
        if order_id is None:
            return
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены что хотите удалить этот заказ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            with get_db_session() as session:
                success = OrderCRUD.delete_order(session, order_id)
                if not success:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить заказ.")
            self.load_data()

    def on_row_double_clicked(self, index):
        """
        Позволяет редактировать заказ двойным кликом
        """
        self.edit_selected()


