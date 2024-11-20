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
        self.attributes = {
            "sliceplot": True, # True -> slice plot, False -> projection plot 
            "direction": [1,0,0],
            "width": 100, 
            "datasource": None,
            "ds_fields": [],
            "imagepath": "tmp.png",
        }

    def __init_layout__(self):
        self.widgets = {}
        layout = QHBoxLayout(self)

        left = self.widgets["left"] = QWidget()
        left_layout = QVBoxLayout(left)

        image = self.widgets["image"] = QLabel()
        image.setScaledContents(True)
        self.set_image()

        right = self.widgets["right"] = QWidget()
        right_layout = QVBoxLayout(right)

        tab_menu = self.widgets["tab_menu"] = QTabBar()
        
        tab_menu.addTab("make plot")
        tab_menu.addTab("edit plot")

        tab_menu.tabBarClicked.connect(self.tab_switch)
        scroll_area = self.widgets["scroll_area"] = QScrollArea()

        action_bar = self.widgets["action_bar"] = QWidget()
        action_bar_layout = QHBoxLayout(action_bar)

        plot_button = self.widgets["plot_button"] = QPushButton("plot")
        plot_button.clicked.connect(self.plot)
        
        file_select = self.widgets["file_select"] = QPushButton("select file")
        file_select.clicked.connect(self.open_file_dialog)

        action_bar_layout.addWidget(plot_button)
        action_bar_layout.addWidget(file_select)

        left_layout.addWidget(image)

        right_layout.addWidget(tab_menu)
        right_layout.addWidget(scroll_area)
        right_layout.addWidget(action_bar)

        layout.addWidget(left)
        layout.addWidget(right)
        
        self.widgets["left"].setFixedWidth(self.width()//2-1)
        self.widgets["left"].setFixedHeight(self.width()//2-1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.widgets["left"].setFixedWidth(event.size().width()//2)
        self.widgets["left"].setFixedHeight(event.size().width()//2)
        

    def set_image(self, image_path=""):
        if image_path == "":
            self.widgets["image"].setPixmap(QPixmap.fromImage(QImage(self.get_attribute("imagepath"))))
        else:
            self.widgets["image"].setPixmap(QPixmap.fromImage(QImage(image_path)))

    def get_attribute(self, attribute):
        return self.attributes.get(attribute)
    
    def set_attribute(self, attribute, val):
        self.attributes[attribute] = val


    @QtCore.Slot()
    def tab_switch(self, i):
        scroll_area = self.widgets["scroll_area"]
        match i:
            case 0:
                plot_maker_panel = self.widgets["scroll_area_widget"] = PlotMakerPanel(self)
                pb = self.widgets["plot_button"]
                try:
                    pb.clicked.disconnect()
                    pb.clicked.connect(plot_maker_panel.update_fields)
                    pb.clicked.connect(self.plot)
                except:
                    print("plot_button connect failed")

            case 1:
                plot_maker_panel = self.widgets["scroll_area_widget"] = PlotEditorPanel(self)
                pb = self.widgets["plot_button"]


    @QtCore.Slot()
    def plot(self):
        if self.get_attribute("data_source") != None:
            temp = yt.SlicePlot(self.get_attribute("data_source"), self.get_attribute("direction"), self.get_attribute("field"))
            temp.save(self.get_attribute("image_path"))
            self.set_image(self.get_attribute("image_path"))

    @QtCore.Slot()
    def open_file_dialog(self):
        f = FileDialog()
        f.exec()
        s = f.filesSelected()[0]
        if (s != None):
            ds = yt.load(s)
            self.set_attribute("ds", ds)
            self.set_attribute("fields", ds.field_list)

class FileDialog(QFileDialog):
    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.ExistingFiles)
        btns = self.findChildren(QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                files.append(os.path.join(str(self.directory().absolutePath()),str(i.data())))
                print(files)
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles
    
class PlotMakerPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    def __init_layout__():
        pass
    
    @QtCore.Slot()
    def update_fields():
        pass

class PlotEditorPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def __init_layout__():
        pass

    @QtCore.Slot()
    def update_fields():
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    ytw = YTWindow()
    ytw.resize(600,600)
    ytw.show()

    sys.exit(app.exec())