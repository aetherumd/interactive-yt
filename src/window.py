from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
from widgets import PlotMakerPanel, PlotEditorPanel
import yt
import os

class YTWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()

        self.direction = "y"
        self.field = ("ramses","HeII")
        self.data_source = ""

        self.init_layout()

    @QtCore.Slot()
    def tabSwitchFn(self, i):
        if i == 0:
            self.panel_area.setWidget(PlotMakerPanel(self))
        elif i == 1:
            self.panel_area.setWidget(PlotEditorPanel(self))

        self.layout.addWidget(self.left)
        self.layout.addWidget(self.right)

    @QtCore.Slot()
    def plot(self):
        if self.data_source != None:
            temp = yt.SlicePlot(self.data_source, self.direction, self.field)
            temp.save("tmp.png")
            self.image_panel.setPixmap(QPixmap.fromImage(QImage(self.image_path)))
        

    def init_layout(self):
        self.left, self.right = QLabel(), QLabel()

        leftLO = QVBoxLayout()
        rightLO = QVBoxLayout()

        self.image_path = "tmp.png"

        self.image_panel = QLabel(alignment=Qt.AlignCenter)
        self.image_panel.setPixmap(QPixmap.fromImage(QImage(self.image_path)))
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

        plot_button = QPushButton("make plot")
        plot_button.clicked.connect(self.plot)

        file_button = QPushButton("select file")
        file_button.clicked.connect(self.open_file_dialog)

        ab_lo.addWidget(plot_button)
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
        
        self.setLayout(self.layout)
    
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
            self.data_source = yt.load(s)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.left.setFixedWidth(event.size().width()//2)
        self.left.setFixedHeight(event.size().width()//2)
        
    def set_data_source(self, data_source):
        self.data_source = data_source

    def set_image(self, image_path):
        self.image_path = image_path
        self.image_panel.setPixmap(QPixmap.fromImage(QImage(self.image_path)))


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