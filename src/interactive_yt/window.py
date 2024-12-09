from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
import os, sys, yt
from enum import Enum
from interactive_yt import interface

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
            "data_source": None,
            "ds_fields": [],
            "ds_center": (0,0,0),
            "field": [("ramses", "HeII")],
            "image_path": "tmp.png",
            "plot_type": PlotOption.SLICE_PLOT,
            "ds_field_x": None,
            "ds_field_y": None,
            "ds_field_z": None,
        }

    def __init_layout__(self):
        self.widgets = {}
        layout = QHBoxLayout(self)

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
        scroll_area.setWidgetResizable(True)

        pmp = self.widgets["pmp"] = PlotMakerPanel(self)
        pep = self.widgets["pep"] = PlotEditorPanel(self)
        #this part was in the tab switch section, goes here now since we don't create a new
        #plot editor/plot maker on every switch
        
        scroll_area_widget = self.widgets["scroll_area_widget"] = pmp
        scroll_area.setWidget(scroll_area_widget)

        action_bar = self.widgets["action_bar"] = QWidget()
        action_bar_layout = QHBoxLayout(action_bar)

        plot_button = self.widgets["plot_button"] = QPushButton("plot")
        plot_button.clicked.connect(self.plot)
        
        file_select = self.widgets["file_select"] = QPushButton("select file")
        file_select.clicked.connect(self.open_file_dialog)

        action_bar_layout.addWidget(plot_button)
        action_bar_layout.addWidget(file_select)

        right_layout.addWidget(tab_menu)
        right_layout.addWidget(scroll_area)
        right_layout.addWidget(action_bar)

        layout.addWidget(image)
        layout.addWidget(right)
        
        self.widgets["image"].setFixedWidth(self.width()//2-1)
        self.widgets["image"].setFixedHeight(self.width()//2-1)
        
        self.tab_switch(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        """
        self.widgets["left"].setFixedWidth(event.size().width()//2)
        self.widgets["left"].setFixedHeight(event.size().width()//2)
        """
        self.widgets["right"].setMaximumWidth(event.size().width() - self.widgets["image"].width())
        self.widgets["scroll_area"].setMaximumWidth(event.size().width() - self.widgets["image"].width())
        #self.widgets["scroll_area_widget"].setMaximumWidth(event.size().width() - self.widgets["image"].width())
        self.widgets["scroll_area_widget"].resizeEvent(event)

    def set_image(self, image_path=""):
        if image_path == "":
            self.widgets["image"].setPixmap(QPixmap.fromImage(QImage(self.get_attribute("image_path"))))
        else:
            self.widgets["image"].setPixmap(QPixmap.fromImage(QImage(image_path)))

    def get_attribute(self, attribute):
        return self.attributes.get(attribute)
    
    def set_attribute(self, attribute, val):
        self.attributes[attribute] = val
        
    def update_image(self):
        for i in os.listdir("img"):
            os.remove(f"img/{i}")

        self.attributes["plot"].save("img/")
        image = os.listdir("img")[0]

        self.widgets["image"].setPixmap(QtGui.QPixmap(f"img/{image}"))

    @QtCore.Slot()
    def move_up(self):
        self.attributes["plot"].pan_rel((0,-0.1))
        self.update_image()

    @QtCore.Slot()
    def move_down(self):
        self.attributes["plot"].pan_rel((0,0.1))
        self.update_image()

    @QtCore.Slot()
    def move_left(self):
        self.attributes["plot"].pan_rel((-0.1,0))
        self.update_image()

    @QtCore.Slot()
    def move_right(self):
        self.attributes["plot"].pan_rel((0.1,0))
        self.update_image()

    @QtCore.Slot()
    def zoom_in(self):
        self.attributes["plot"].zoom(2.0)
        self.update_image()

    @QtCore.Slot()
    def zoom_out(self):
        self.attributes["plot"].zoom(0.5)
        self.update_image()
 
    @QtCore.Slot()
    def tab_switch(self, i):
        scroll_area = self.widgets["scroll_area"]
        match i:
            case 0:#plot maker
                plot_maker = self.widgets["scroll_area_widget"] = self.widgets["pmp"]
                print(type(plot_maker))
                if type(scroll_area.widget()) == PlotEditorPanel:
                    self.widgets["pep"] = scroll_area.takeWidget()
                    scroll_area.setWidget(plot_maker)
                    pb = self.widgets["plot_button"]
                    try:
                        pb.clicked.disconnect()
                        pb.clicked.connect(plot_maker.update_fields)
                        pb.clicked.connect(self.plot)
                    except:
                        print("plot_button connect failed")

            case 1:#plot editor
                plot_editor = self.widgets["scroll_area_widget"] = self.widgets["pep"]
                print(type(plot_editor))
                print(type(scroll_area.widget()))
                if type(scroll_area.widget()) == PlotMakerPanel:
                    self.widgets["pmp"] = scroll_area.takeWidget()
                    scroll_area.setWidget(plot_editor)
                    pb = self.widgets["plot_button"]
                    try:
                        pb.clicked.disconnect()
                        pb.clicked.connect(plot_editor.update_fields)
                        pb.clicked.connect(self.plot)
                    except:
                        print("plot_button connect failed")


    @QtCore.Slot()
    def plot(self):
        if self.get_attribute("data_source") != None:
            #TODO change image in init to image_section
            image_section = self.widgets["image"]
            plot = self.attributes["plot"] = None
            match self.get_attribute("plot_type"):
                case PlotOption.SLICE_PLOT:
                    plot = yt.SlicePlot(self.get_attribute("data_source"), self.get_attribute("direction"), self.get_attribute("field"))
                case PlotOption.PARTICLE_PLOT:
                    plot = yt.ParticlePlot(self.get_attribute("data_source"))
                case PlotOption.PROJECTION_PLOT:
                    plot = yt.ProjectionPlot(self.get_attribute("data_source"), self.get_attribute("direction"), self.get_attribute("field"))
            self.attributes["plot"] = plot
            self.update_image()
            

    @QtCore.Slot()
    def open_file_dialog(self):
        f = FileDialog()
        f.exec()
        s = f.filesSelected()[0]
        if (s != None):
            ds = yt.load(s)
            self.set_attribute("data_source", ds)
            self.set_attribute("ds_fields", ds.field_list)
            self.widgets["scroll_area_widget"].refresh()

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
        self.__init_layout__()
    
    def __init_layout__(self):
        self.widgets = {}
        self.entries = []
        
        wgts = {
            "Slice plot": (IOOption.CHECKBOX, True, "sliceplot"),
            "Direction": (IOOption.USER_ENTRY, "x", "direction"),
            "Field": (IOOption.DROPDOWN, self.parent.get_attribute("ds_fields"), "field"),
            "Plot Type": (IOOption.DROPDOWN, [PlotOption.SLICE_PLOT, PlotOption.PARTICLE_PLOT, PlotOption.PROJECTION_PLOT], "plot_type"),
        }

        layout = QVBoxLayout(self)

        for wgt_label in wgts.keys():
            t, v, a = wgts[wgt_label]
            entry = QWidget()
            entry_layout = QHBoxLayout(entry)

            w = QWidget()
            match t:
                case IOOption.DROPDOWN:
                    w = QComboBox()
                    for vi in v:
                        w.addItem(str(vi))
                case IOOption.USER_ENTRY:
                    w = QLineEdit()
                    w.setText(v)
                case IOOption.CHECKBOX:
                    w = QCheckBox()
                    w.setChecked(v)
            
            self.widgets[a] = (w, t, v)
            entry_layout.addWidget(QLabel(wgt_label))
            entry_layout.addWidget(w)

            self.entries.append(entry)

            layout.addWidget(entry)

    @QtCore.Slot()
    def refresh(self):
        field_select, t, v = self.widgets["field"]
        field_select.clear()
        dsf = self.parent.get_attribute("ds_fields")
        for f in dsf:
            field_select.addItem(str(f))
        self.widgets["field"] = (field_select, t, dsf)

    @QtCore.Slot()
    def update_fields(self):
        for wgt_label in self.widgets.keys():
            w, t, v = self.widgets[wgt_label]
            val = None
            match t:
                case IOOption.DROPDOWN:
                    if len(v) > 0:
                        val = v[w.currentIndex()]
                    else:
                        val = self.parent.get_attribute("field")
                case IOOption.USER_ENTRY:
                    val = w.text()
                case IOOption.CHECKBOX:
                    val = w.isChecked()
            self.parent.set_attribute(wgt_label, val)

    @QtCore.Slot()
    def update_plot_parameter_panel():
        pass
    #Todo - add classes? for each type of panel or probably just methods

class IOOption(Enum):
    DROPDOWN = 0,
    USER_ENTRY = 1,
    CHECKBOX = 2

class PlotOption(Enum):
    SLICE_PLOT = 0,
    PARTICLE_PLOT = 1,
    PROJECTION_PLOT = 2
    
class PlotEditorPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.__init_layout__()

    def __init_layout__(self):
        self.layout = QVBoxLayout(self)
        #zoom and pan section
        self.controls_section = QWidget()
        self.dir_btns = {}
        self.controls_layout = QVBoxLayout(self.controls_section)

        self.three_box1 = QWidget()
        self.three_layout1 = QHBoxLayout(self.three_box1)
        for i in ['up','left','right']:
            self.dir_btns[i] = QPushButton(i)
            self.three_layout1.addWidget(self.dir_btns[i])
        self.controls_layout.addWidget(self.three_box1)

        self.three_box2 = QWidget()
        self.three_layout2 = QHBoxLayout(self.three_box2)
        for i in ['down','in','out']:  
            self.dir_btns[i] = QPushButton(i)
            self.three_layout2.addWidget(self.dir_btns[i])
        self.controls_layout.addWidget(self.three_box2)
        

        self.layout.addWidget(self.controls_section)

        self.dir_btns['up'].clicked.connect(self.parent.move_down)
        self.dir_btns['down'].clicked.connect(self.parent.move_up)
        self.dir_btns['left'].clicked.connect(self.parent.move_left)
        self.dir_btns['right'].clicked.connect(self.parent.move_right)
        self.dir_btns['in'].clicked.connect(self.parent.zoom_in)
        self.dir_btns['out'].clicked.connect(self.parent.zoom_out)

    @QtCore.Slot()
    def update_fields():
        pass

    @QtCore.Slot()
    def refresh(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    ytw = YTWindow()
    ytw.resize(600,600)
    ytw.show()

    sys.exit(app.exec())
