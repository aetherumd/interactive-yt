from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
import os, sys, yt
from enum import Enum

class YTWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.__init_attributes__()
        self.__init_layout__()

    def __init_attributes__(self):
        pass

    def __init_layout__(self):
        pass

    def set_attributes(attribute, value):
        pass

    def get_attributes(attribute):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)


class ImageWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def __init_layout__(self):
        pass

    @QtCore.Slot()
    def set_image(self, image_path="tmp.png"):
        pass

class MenuWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    def __init_layout__(self):
        pass

    @QtCore.Slot()
    def open_file_dialog(self):
        pass

class PlotMakerWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    def __init_layout__(self):
        pass

class PlotEditorWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    def __init_layout__(self):
        pass
