from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
from typing import *
from backend.options import *

class QAdjustable(QWidget):
    """
    Inheritable class for interactive_yt widgets.

    Has built-in child widget management, and stores widgets regardless if they
    are used. This functionality is necessary for how we are handling switching
    tabs (I believe).

    TODO: 
        add resizing
    """
    def __init__(self):
        super().__init__()
        self.widgets: dict[QWidget] = dict()

    def add_widget(self, name: V3Option, w: QWidget) -> QWidget:
        self.widgets[name] = w
        return w

    def get_widget(self, name: V3Option) -> QWidget:
        return self.widgets[name]
