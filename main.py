import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtCore import QModelIndex
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
        self.add_row_btn.clicked.connect(self.init_add_form)
        self.edit_row_btn.clicked.connect(self.init_edit_form)

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

    def init_add_form(self):
        form = AddEditForm(self, self.add_row)
        form.show()

    def init_edit_form(self):
        tb: QTableWidget = self.coffee_table
        selected = tb.selectedIndexes()
        rows = set(map(QModelIndex.row, selected))
        if len(rows) > 1:
            self.statusBar.showMessage("Выбрано больше одной строки")
            return
        if not rows:
            self.statusBar.showMessage("Ничего не выбрано")
            return

        row_index = tuple(rows)[0]
        row_id = int(tb.item(row_index, 0).text())
        form = AddEditForm(self, self.add_row, True, row_id)

        with sqlite3.connect("coffee.sqlite") as conn:
            cursor = conn.cursor()
            query = """
            SELECT variety, roast_degree, ground_bean, taste_description, price, value
            FROM coffee
            WHERE id = ?;
            """
            form.fill_in_data(*cursor.execute(query, (row_id,)).fetchone())

        form.show()

    def add_row(self, variety: str, roast_deg: int, shape: int, taste_description: str, price: int, value: int,
                edit_mode: bool, row_id: int | None) -> None:
        with sqlite3.connect("coffee.sqlite") as conn:
            cursor = conn.cursor()
            if edit_mode:
                query = f"""
                UPDATE coffee
                SET variety = ?, roast_degree = ?, ground_bean = ?, taste_description = ?, price = ?, value = ?
                WHERE id = {row_id};
                """
            else:
                query = """
                INSERT INTO coffee(variety, roast_degree, ground_bean, taste_description, price, value) VALUES
                (?, ?, ?, ?, ?, ?);
                """
            cursor.execute(query,
                           (variety, roast_deg, shape, taste_description, price, value))
            conn.commit()


class AddEditForm(QMainWindow):
    def __init__(self, parent: Coffee, callback: (), edit_mode: bool = False, row_id: int = None):
        super().__init__(parent)
        with open("addEditCoffeeForm.ui") as f:
            uic.loadUi(f, self)

        self.row_id = row_id
        self.edit_mode = edit_mode

        self.callback = callback
        self.submit_btn.clicked.connect(self.add_edit_row)

    def add_edit_row(self):
        variety = self.variety.text().strip()
        roast_degree = self.roast_degree.currentIndex() + 1
        shape = self.shape.currentIndex()
        taste_description = self.taste_description.toPlainText().strip()
        price = self.price.text().strip()
        value = self.value.text().strip()

        ok, report = self.validate(variety, taste_description, price, value)
        if not ok:
            self.statusBar.showMessage(report)
            return
        price = int(price)
        value = int(value)

        self.callback(variety, roast_degree, shape, taste_description, price, value, self.edit_mode, self.row_id)
        self.parent().fill_in_table()
        self.close()

    def validate(self, variety: str, taste_description: str, price: str, value: str) -> (bool, str | None):
        try:
            assert variety, "Строка сорта пуста"
            assert taste_description, "Описание вкуса не заполнено"
            assert price.isdigit(), "Цена должна быть целым неотрицательным числом"
            assert value.isdigit() and int(value) > 0, "Объем должен быть натуральным числом"
        except AssertionError as e:
            return False, str(e)

        return True, None

    def fill_in_data(self, variety: str, roast_degree: int, shape: int, taste_description: str, price: int, value: int):
        self.variety.setText(variety)
        self.roast_degree.setCurrentIndex(roast_degree - 1)
        self.shape.setCurrentIndex(shape)
        self.taste_description.setPlainText(taste_description)
        self.price.setText(str(price))
        self.value.setText(str(value))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
