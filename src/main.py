from PySide6 import QtWidgets
from components.window import YtWindow
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    ytw = YtWindow()
    ytw.resize(600,600)
    ytw.show()

    sys.exit(app.exec())