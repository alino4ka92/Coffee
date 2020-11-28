import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5 import QtCore

from UI.addEditCoffeeForm import Ui_MainWindow as Ui_AddEdit
from UI.mainWindow import Ui_MainWindow


class ValueError(Exception):
    pass


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()
        self.btn_add.clicked.connect(self.add_coffee)
        self.btn_edit.clicked.connect(self.edit_coffee)
        self.btn_delete.clicked.connect(self.delete_coffee)
        self.update()

    def update(self):
        result = self.cur.execute("SELECT * FROM Coffee").fetchall()
        self.result = list(result)

        self.table.setRowCount(len(result))
        if result:
            self.table.setColumnCount(len(result[0]))
        self.table.setHorizontalHeaderLabels(['ID', 'Название', 'Тип прожарки',
                                              'Тип кофе', 'Описание', 'Цена', 'Вес'])
        for i, elem in enumerate(result):
            result[i] = list(result[i])
            result[i][2] = \
                self.cur.execute(f"SELECT name FROM Roasting WHERE roasting_id={result[i][2]}").fetchall()[0][0]
            result[i][3] = self.cur.execute(f"SELECT name FROM Types WHERE type_id={result[i][3]}").fetchall()[0][0]
        for i, elem in enumerate(result):
            for j, item in enumerate(elem):
                cur_item = QTableWidgetItem(str(item))
                cur_item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table.setItem(i, j, cur_item)

        for i in [0, 1, 2, 3, 5, 6]:
            self.table.resizeColumnToContents(i)
        self.table.resizeRowsToContents()

    def add_coffee(self):
        self.statusbar.showMessage('')
        self.add_coffee_window = AddEditCoffeeWindow(-1)
        self.add_coffee_window.setWindowTitle('Добавить элемент')
        self.add_coffee_window.show()

    def edit_coffee(self):
        self.statusbar.showMessage('')
        row = self.table.currentRow()
        if row == -1:
            self.statusbar.showMessage('Выберите строку для редактирования')
            return
        cur_id, name, roasting_id, type_id, description, price, weight = self.result[row]

        self.edit_coffee_window = AddEditCoffeeWindow(cur_id)
        roasting_index = [i[0] for i in self.edit_coffee_window.roastings].index(roasting_id)
        self.edit_coffee_window.roasting.setCurrentIndex(roasting_index)
        type_index = [i[0] for i in self.edit_coffee_window.types].index(type_id)
        self.edit_coffee_window.coffee_type.setCurrentIndex(type_index)
        self.edit_coffee_window.name.setText(str(name))
        self.edit_coffee_window.description.setPlainText(str(description))
        self.edit_coffee_window.price.setValue(float(price))
        self.edit_coffee_window.weight.setValue(float(weight))
        self.edit_coffee_window.btn.setText('Редактировать')
        self.edit_coffee_window.setWindowTitle('Редактировать элемент')
        self.edit_coffee_window.show()

    def delete_coffee(self):
        self.statusbar.showMessage('')
        row = self.table.currentRow()
        if row == -1:
            self.statusbar.showMessage('Выберите элемент для удаления')
            return
        valid = QMessageBox.question(
            self, '', "Действительно удалить элемент?",
            QMessageBox.Yes, QMessageBox.No)
        if valid != QMessageBox.Yes:
            return
        cur_id, name, roasting_id, type_id, description, price, weight = self.result[row]
        self.cur.execute(f"DELETE FROM Coffee WHERE id={cur_id}")
        self.con.commit()
        self.update()
        self.statusbar.showMessage('Успешно, выделение переведено на последнюю строку')


class AddEditCoffeeWindow(QMainWindow, Ui_AddEdit):
    def __init__(self, edit_id):
        super().__init__()
        self.setupUi(self)
        self.edit_id = edit_id
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()
        self.roastings = self.cur.execute("SELECT * FROM Roasting").fetchall()
        for i in self.roastings:
            self.roasting.addItem(i[1])
        self.types = self.cur.execute("SELECT * FROM Types").fetchall()
        for i in self.types:
            self.coffee_type.addItem(i[1])
        self.btn.clicked.connect(self.add)

    def add(self):
        try:
            name = self.name.text()
            if not name:
                raise ValueError('введите непустое название кофе')
            roasting_id = self.roastings[self.roasting.currentIndex()][0]
            type_id = self.types[self.coffee_type.currentIndex()][0]
            description = self.description.toPlainText()
            price = self.price.value()
            weight = self.weight.value()
            if self.edit_id == -1:
                self.cur.execute(
                    "INSERT INTO Coffee(name, roasting_id, type_id, description, price, weight) VALUES(?, ?, ?, ?, ?, ?)",
                    (name, roasting_id, type_id, description, price, weight))
            else:
                self.cur.execute(f'DELETE FROM Coffee WHERE id={self.edit_id}')
                self.cur.execute(
                    "INSERT INTO Coffee(id, name, roasting_id, type_id, description, price, weight) VALUES(?,?,  ?, ?, ?, ?, ?)",
                    (self.edit_id, name, roasting_id, type_id, description, price, weight))
            self.con.commit()
            ex.update()
            ex.statusbar.showMessage('Успешно')
            self.hide()

        except ValueError as exception:
            self.statusbar.showMessage(f'Неправильный ввод: {exception}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
