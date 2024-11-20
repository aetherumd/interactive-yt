from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
import yt
import os
from enum import Enum

class YTWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)

        self.attributes = {
            "sliceplot": True,
            "direction": "y",
            "field": ("ramses", "HeII"),
            "datasource": "",
            "savetofilename": "tmp.png",
            "ds": None,
            "fields": []
        }

        self.direction = "y"
        self.field = ("ramses","HeII")
        self.data_source = ""


        self.init_layout()

    @QtCore.Slot()
    def tabSwitchFn(self, i):
        if i == 0:
            p = PlotMakerPanel(self)
            self.panel_area.setWidget(p)
            self.plot_button.clicked.connect(p.update_parent_attributes)
        elif i == 1:
            self.panel_area.setWidget(PlotEditorPanel(self))

        self.layout.addWidget(self.left)
        self.layout.addWidget(self.right)

    @QtCore.Slot()
    def plot(self):
        if self.data_source != None:
            print(f"{self.get_attribute("ds")},{self.get_attribute("direction")},{self.get_attribute("field")}")
            temp = yt.SlicePlot(self.get_attribute("ds"), self.get_attribute("direction"), self.get_attribute("field"))
            temp.save(self.get_attribute("savetofilename"))
            #self.image_panel.setPixmap(QPixmap.fromImage(QImage(self.image_path)))
            self.set_image(self.get_attribute("savetofilename"))
        

    def init_layout(self):
        self.left, self.right = QLabel(), QLabel()

        leftLO = QVBoxLayout()
        rightLO = QVBoxLayout()

        self.image_panel = QLabel(alignment=Qt.AlignCenter)
        #self.image_panel.setPixmap(QPixmap.fromImage(QImage(self.get_attribute("savetofilename"))))
        self.set_image(self.get_attribute("savetofilename"))
        self.image_panel.setScaledContents(1)

        leftLO.addWidget(self.image_panel)
        self.left.setLayout(leftLO)

        menu = QTabBar()
        self.panel_area = QScrollArea()

        self.panel_area.setWidget(PlotMakerPanel(self))
        menu.addTab("make")
        menu.addTab("edit")
        menu.tabBarClicked.connect(self.tabSwitchFn)

        action_bar = QWidget()
        ab_lo = QHBoxLayout()

        self.plot_button = QPushButton("make plot")
        self.plot_button.clicked.connect(self.plot)

        file_button = QPushButton("select file")
        file_button.clicked.connect(self.open_file_dialog)

        ab_lo.addWidget(self.plot_button)
        ab_lo.addWidget(file_button)

        action_bar.setLayout(ab_lo)

        rightLO.addWidget(menu)
        rightLO.addWidget(self.panel_area)
        rightLO.addWidget(action_bar)
        
        self.right.setLayout(rightLO)

        self.left.setFixedWidth(self.width()//2)
        self.left.setFixedHeight(self.width()//2)

        self.layout.addWidget(self.left)
        self.layout.addWidget(self.right)
    
    @QtCore.Slot()
    def open_file_dialog(self):
        """
        fd = QFileDialog(self, directory="C:")
        fd.setFileMode(QFileDialog.AnyFile)

        if fd.exec():
            self.data_source = yt.load(fd.selectedFiles()[0])
        """
        f = FileDialog()

        f.exec()
        s = f.filesSelected()[0]
        if (s != None):
            #self.data_source = yt.load(s)
            ds = yt.load(s)
            self.set_attribute("ds", ds)
            self.set_attribute("fields", ds.field_list)
            self.panel_area.setWidget(PlotMakerPanel(self))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.left.setFixedWidth(event.size().width()//2)
        self.left.setFixedHeight(event.size().width()//2)
        
    def set_data_source(self, data_source):
        self.data_source = data_source
        self.set_attribute("datasource", data_source)

    def set_image(self, image_path):
        self.set_attribute("savetofilename", "imagepath")
        self.image_panel.setPixmap(QPixmap.fromImage(QImage(self.get_attribute("savetofilename"))))

    def get_attribute(self, attribute):
        return self.attributes.get(attribute)
    
    def set_attribute(self, attribute, val):
        self.attributes[attribute] = val


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
    
class Panel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class PlotMakerPanel(Panel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        self.layout = QVBoxLayout(self)
        self.wgts = {}
        
        self.__init_layout__()

    def __init_layout__(self):
        wgts = [
            (PanelOption.CHECK, "Slice Plot", "sliceplot"),

            (PanelOption.DROPDOWN, "Field", "field", self.parent.get_attribute("ds").field_list if self.parent.get_attribute("ds") != None else []),

            (PanelOption.INPUT, "Save to:", "savetofilename"),
        ]
        for wgt in wgts:
            w = QWidget()
            lo = QHBoxLayout(w)
            label = QLabel(wgt[1])
            lo.addWidget(label)
            q = QWidget()
            match wgt[0]:
                case PanelOption.CHECK:
                    q = QCheckBox()
                    q.setCheckState(Qt.Checked)
                case PanelOption.DROPDOWN:
                    q = QComboBox()
                    q.addItems(wgt[3])
                case PanelOption.INPUT:
                    q = QLineEdit()
            lo.addWidget(q)

            self.wgts[wgt[1]] = (q, wgt[0], wgt[2])

            self.layout.addWidget(w)
            
    def get_wgt_attribute(wgt, w):
        match w:
            case PanelOption.CHECK:
                wgt.checkState()
            case PanelOption.DROPDOWN:
                wgt.currentText()
            case PanelOption.INPUT:
                wgt.getText()

    def refresh(self):
        w, op, a = self.wgts["field"]
        w.clear()
        w.addItem(self.parent.get_attribute("ds").field_list)

    
    @QtCore.Slot()
    def update_parent_attributes(self):
        for wgt in self.wgts.keys:
            w, op, a = self.wgts[wgt]
            self.parent.set_attribute(a, self.get_wgt_attribute(wgt, op))



        
class PanelOption(Enum):
    CHECK = 1
    INPUT = 2
    DROPDOWN = 3

class PlotEditorPanel(Panel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    