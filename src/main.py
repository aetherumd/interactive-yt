import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import *
from window_v2 import YTWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = YTWindow()
    widget.resize(300,300)
    widget.show()

    sys.exit(app.exec())