import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import *
from window import YTWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = YTWindow()
    widget.resize(600,600)
    widget.show()

    sys.exit(app.exec())