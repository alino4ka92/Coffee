import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtCore


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()
        self.update()

    def update(self):
        result = self.cur.execute("SELECT * FROM Coffee").fetchall()
        if not result:
            return
        self.table.setRowCount(len(result))
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
