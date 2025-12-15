from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QToolBar, QPushButton, QMessageBox, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from views.order_dialog import OrderDialog
from crud import OrderCRUD
from config import get_db_session


class MainWindow(QMainWindow):
    pass

