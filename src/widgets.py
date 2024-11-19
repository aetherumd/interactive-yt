import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage, QPicture
import yt
import numpy
import enum

class Panel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class PlotMakerPanel(Panel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
class PlotEditorPanel(Panel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    