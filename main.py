import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem

ROAST_DEGREES = {
    1: "Слабая",
    2: "Средняя",
    3: "Сильная",
}
SHAPES = {
    0: "Молотый",
    1: "Зерновой"
}
HORIZONTAL_HEADERS = ["ID", "Сорт", "Степень обжарки", "Молотый/зерновой", "Описание вкуса", "Цена", "Объем упаковки"]


class Coffee(QMainWindow):
    def __init__(self):
        super().__init__()

        with open("main.ui") as f:
            uic.loadUi(f, self)

        self.fill_in_table()

    def fill_in_table(self):
        tb: QTableWidget = self.coffee_table

        tb.clear()
        tb.setRowCount(0)

        tb.setColumnCount(len(HORIZONTAL_HEADERS))
        tb.setHorizontalHeaderLabels(HORIZONTAL_HEADERS)

        query = """SELECT * FROM coffee;"""
        with sqlite3.connect("coffee.sqlite") as conn:
            cursor = conn.cursor()
            for i, row in enumerate(cursor.execute(query)):
                tb.setRowCount(tb.rowCount() + 1)
                for j, value in enumerate(row):
                    if j == 2:
                        value = ROAST_DEGREES[value]
                    elif j == 3:
                        value = SHAPES[value]

                    tb.setItem(i, j, QTableWidgetItem(str(value)))
        tb.resizeColumnsToContents()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
