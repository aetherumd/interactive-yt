from PySide6 import QtCore
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage

from components.ui import QAdjustable

from backend.info_handling import *
from backend.options import *

from typing import *
from ast import literal_eval

import yt, re

class MakePlotPanel(Publisher, QAdjustable):
    """
    Gives options related to plot creation, depending on selected plot type.

    TODO:
        Implement functionality for options in options.PlotOption
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)

        for op in PlotOption:
            self.add_field(op)
        
        self.__init_layout__()

    def __init_layout__(self):   
        """
        TODO:
            make inputs for the quantities in options.PlotOption    
        """
        self.widgets = dict()
        self.entries = list()
        
        layout = QVBoxLayout(self)

        plot_type = QComboBox()
        for entry in ["Slice Plot", "Projection Plot", "Particle Plot"]:
            plot_type.addItem(entry)
        self.widgets.update({PlotOption.PLOT_TYPE: plot_type})
        plot_type.currentIndexChanged.connect(self.plot_type_handler)

        sliceprojpane = SliceProjectionPlotPanel(self.broker)
        self.widgets.update({PlotTypeOption.SLICE_PLOT: sliceprojpane})

        particlepane = ParticlePlotPanel(self.broker)
        self.widgets.update({PlotTypeOption.PARTICLE_PLOT: particlepane})
        particlepane.setVisible(False)

        file_pane = QWidget()
        fp_layout = QHBoxLayout(file_pane)

        folder_dialog = QPushButton("Open folder")
        folder_dialog.clicked.connect(self.open_folder_dialog)

        file_dialog = QPushButton("Open file")
        file_dialog.clicked.connect(self.open_file_dialog)

        fp_layout.addWidget(folder_dialog)
        fp_layout.addWidget(file_dialog)

        self.widgets.update({PlotOption.DATASET: file_pane})

        make_plot = QPushButton("Make plot")
        make_plot.clicked.connect(self.plot)

        self.widgets.update({Data.PLOT: make_plot})

        for wgt in self.widgets.values():
            layout.addWidget(wgt)
    
    @QtCore.Slot()
    def plot_type_handler(self):
        plot_select = self.widgets.get(PlotOption.PLOT_TYPE)
        if type(plot_select) is QComboBox:
            select = plot_select.currentIndex()
            if select == 0:
                self.publish(PlotOption.PLOT_TYPE, PlotTypeOption.SLICE_PLOT)
                self.get_widget(PlotTypeOption.SLICE_PLOT).setVisible(True)
                self.get_widget(PlotTypeOption.PARTICLE_PLOT).setVisible(False)
            elif select == 1:
                self.publish(PlotOption.PLOT_TYPE, PlotTypeOption.PROJECTION_PLOT)
                self.get_widget(PlotTypeOption.SLICE_PLOT).setVisible(True)
                self.get_widget(PlotTypeOption.PARTICLE_PLOT).setVisible(False)
            elif select == 2:
                self.publish(PlotOption.PLOT_TYPE, PlotTypeOption.PARTICLE_PLOT)
                self.get_widget(PlotTypeOption.SLICE_PLOT).setVisible(False)
                self.get_widget(PlotTypeOption.PARTICLE_PLOT).setVisible(True)

    @QtCore.Slot()
    def open_file_dialog(self):
        f = QFileDialog()
        f.setFileMode(QFileDialog.FileMode.ExistingFile)
        f.exec()
        s = f.selectedFiles()[0]
        if (s != None):
            ds = yt.load(s)
            self.publish(PlotOption.DATASET, ds)

    @QtCore.Slot()
    def open_folder_dialog(self):
        f = QFileDialog()
        f.setFileMode(QFileDialog.FileMode.Directory)
        f.exec()
        s = f.selectedFiles()[0]
        if (s != None):
            ds = yt.load(s)
            self.publish(PlotOption.DATASET, ds)

    @QtCore.Slot()
    def plot(self):
        self.publish(UserAction.CREATE_PLOT, True)

class SliceProjectionPlotPanel(Publisher, Subscriber, QAdjustable):
    """
    Gives options related to slice & projection plot creation.

    TODO:
        Implement functionality for options in options.SliceProjPlotOption
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)

        for op in SliceProjPlotOption:
            self.add_field(op)

        self.subscribe([PlotOption.DATASET])

        self.__init_layout__()

    def __init_layout__(self):      
        """
        TODO:
            make inputs for the quantities in options.SliceProjPlotOption    
        """
        layout = QVBoxLayout(self)

        direction = QLineEdit("")
        direction.setText("x")
        self.widgets.update({SliceProjPlotOption.NORMAL: direction})
        direction.textChanged.connect(self.direction_manager)
        
        field = QComboBox()
        ds = self.query(PlotOption.DATASET)
        if ds is not None:
            for entry in ds.fields:
                field.addItem(entry)
        self.widgets.update({SliceProjPlotOption.FIELDS: field})
        field.currentIndexChanged.connect(self.field_manager)
        
        
        for wgt in self.widgets.values():
            layout.addWidget(wgt)

    
    @QtCore.Slot()
    def direction_manager(self):
        dir = self.widgets.get(SliceProjPlotOption.NORMAL)
        if type(dir) is QLineEdit:
            txt = dir.text()
            card = r"x|y|z"
            vec = r"(\(((\s*([0-9]+(?:\.[0-9]*)?)\s*,){2}\s*([0-9]+(?:\.[0-9]*)?)\s*\s*)\))"
            if(re.fullmatch(card, txt)):
                self.publish(SliceProjPlotOption.NORMAL, txt)
            elif (re.fullmatch(vec, txt)):
                self.publish(SliceProjPlotOption.NORMAL, literal_eval(txt))

    @QtCore.Slot()
    def field_manager(self):
        field = self.widgets.get(SliceProjPlotOption.FIELDS)
        if type(field) is QComboBox:
            "TODO THIS DOESNT WORK!!"
            self.publish(SliceProjPlotOption.FIELDS, literal_eval(field.currentText()))
    
    def handle_update(self, name):
        match name:
            case PlotOption.DATASET:
                ds = self.query(name)
                if type(ds) is not None:
                    field = self.widgets.get(SliceProjPlotOption.FIELDS)
                    if type(field) is QComboBox:
                        field.clear()    
                        for entry in ds.field_list:
                            field.addItem(str(entry))

class ParticlePlotPanel(Publisher, Subscriber, QAdjustable):
    """
    Gives options related to particle plot creation.

    TODO:
        Implement functionality for options in options.ParticlePlotOption
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)

        for op in ParticlePlotOption:
            self.add_field(op)

        self.subscribe([PlotOption.DATASET])

        self.__init_layout__()

    def __init_layout__(self):      
        """
        TODO:
            make inputs for the quantities in options.ParticlePlotOption    
        """
        layout = QVBoxLayout(self)

        x_field = QComboBox()
        y_field = QComboBox()
        z_field = QComboBox()
        weight_field = QComboBox()

        ds = self.query(PlotOption.DATASET)
        if ds is not None:
            for entry in ds.fields:
                x_field.addItem(entry)
                y_field.addItem(entry)
                z_field.addItem(entry)
                weight_field.addItem(entry)

        self.widgets.update({ParticlePlotOption.X_FIELD: x_field})
        self.widgets.update({ParticlePlotOption.Y_FIELD: y_field})
        self.widgets.update({ParticlePlotOption.Z_FIELDS: z_field})
        self.widgets.update({PlotOption.WEIGHT_FIELD: weight_field})

        x_field.currentIndexChanged.connect(self.x_field_manager)
        y_field.currentIndexChanged.connect(self.y_field_manager)
        z_field.currentIndexChanged.connect(self.z_field_manager)
        weight_field.currentIndexChanged.connect(self.weight_field_manager)

        for wgt in self.widgets.values():
            layout.addWidget(wgt)

    @QtCore.Slot()
    def x_field_manager(self):
        field = self.widgets.get(ParticlePlotOption.X_FIELD)
        if type(field) is QComboBox:
            self.publish(ParticlePlotOption.X_FIELD, literal_eval(field.currentText()))
    
    @QtCore.Slot()
    def y_field_manager(self):
        field = self.widgets.get(ParticlePlotOption.Y_FIELD)
        if type(field) is QComboBox:
            self.publish(ParticlePlotOption.Y_FIELD, literal_eval(field.currentText()))

    @QtCore.Slot()
    def z_field_manager(self):
        field = self.widgets.get(ParticlePlotOption.Z_FIELDS)
        if type(field) is QComboBox:
            self.publish(ParticlePlotOption.Z_FIELDS, literal_eval(field.currentText()))

    @QtCore.Slot()
    def weight_field_manager(self):
        field = self.widgets.get(PlotOption.WEIGHT_FIELD)
        if type(field) is QComboBox:
            self.publish(PlotOption.WEIGHT_FIELD, literal_eval(field.currentText()))
    
    def handle_update(self, name):
        match name:
            case PlotOption.DATASET:
                ds = self.query(name)
                if type(ds) is not None:
                    boxes = [
                        self.widgets.get(ParticlePlotOption.X_FIELD),
                        self.widgets.get(ParticlePlotOption.Y_FIELD),
                        self.widgets.get(ParticlePlotOption.Z_FIELDS),
                        self.widgets.get(PlotOption.WEIGHT_FIELD),
                             ]
                    for field in boxes:
                        if type(field) is QComboBox:
                            field.clear()    
                            for entry in ds.field_list:
                                field.addItem(str(entry))
                                
class ImagePanel(Subscriber, QAdjustable):
    """
    Renders the user-created image.

    Subscribed to Data.IMAGE, writes new image to screen.

    TODO: 
        add a plot history option? maybe should be its own class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)
        self.subscribe([Data.IMAGE])
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)
        image = self.add_widget("image", QLabel(self))
        image.setScaledContents(True)
        layout.addWidget(image)
    
    def handle_update(self, name: str):
        match name:
            case Data.IMAGE:
                self.set_img(self.query(name))
            case _:
                pass
    
    def set_img(self, img: QImage):
        self.get_widget("image").setPixmap(QPixmap.fromImage(img))

        
class EditPlotPanel(Publisher, QAdjustable):
    """
    Gives options related to editing plots.

    TODO:
        Implement functionality for options in options.UserAction except for CREATE_PLOT
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)
        
        for op in UserAction:
            self.add_field(op)

        self.__init_layout__()

    def __init_layout__(self):
        layout = QVBoxLayout(self)

        x_region = self.add_widget("x_region",QAdjustable())
        x_region_layout = QHBoxLayout(x_region) 
        x_region.add_widget("x_minus",QPushButton("-"))
        x_input = x_region.add_widget("x_input",QLineEdit("0.0"))
        x_region.add_widget("x_plus",QPushButton("+"))

        for i in x_region.widgets.values():
          x_region_layout.addWidget(i)

        y_region = self.add_widget("y_region",QAdjustable())
        y_region_layout = QHBoxLayout(y_region) 
        y_region.add_widget("y_minus",QPushButton("-"))
        y_input = y_region.add_widget("y_input",QLineEdit("0.0"))
        y_region.add_widget("y_plus",QPushButton("+"))

        for i in y_region.widgets.values():
          y_region_layout.addWidget(i)

        zoom_region = self.add_widget("zoom_region",QAdjustable())
        zoom_region_layout = QHBoxLayout(zoom_region) 
        zoom_region.add_widget("zoom_minus",QPushButton("-"))
        zoom_input = zoom_region.add_widget("zoom_input",QLineEdit("0.0"))
        zoom_region.add_widget("zoom_plus",QPushButton("+"))

        for i in zoom_region.widgets.values():
          zoom_region_layout.addWidget(i)
        
        layout.addWidget(QLabel("x"))
        layout.addWidget(x_region)
        layout.addWidget(QLabel("y"))
        layout.addWidget(y_region)
        layout.addWidget(QLabel("zoom"))
        layout.addWidget(zoom_region)

        x_region.get_widget("x_minus").clicked.connect(self.x_minus_update_handler)
        x_region.get_widget("x_plus").clicked.connect(self.x_plus_update_handler)
        y_region.get_widget("y_minus").clicked.connect(self.y_minus_update_handler)
        y_region.get_widget("y_plus").clicked.connect(self.y_plus_update_handler)
        zoom_region.get_widget("zoom_minus").clicked.connect(self.zoom_minus_update_handler)
        zoom_region.get_widget("zoom_plus").clicked.connect(self.zoom_plus_update_handler)


    @QtCore.Slot()
    def x_plus_update_handler(self):
        data = abs(float(self.get_widget("x_region").get_widget("x_input").text()))
        self.publish(UserAction.PAN_REL_X,data)

    @QtCore.Slot()
    def x_minus_update_handler(self):
        data = -1 * abs(float(self.get_widget("x_region").get_widget("x_input").text()))
        self.publish(UserAction.PAN_REL_X,data)

    @QtCore.Slot()
    def y_plus_update_handler(self):
        data = abs(float(self.get_widget("y_region").get_widget("y_input").text()))
        self.publish(UserAction.PAN_REL_Y,data)

    @QtCore.Slot()
    def y_minus_update_handler(self):
        data = -1 * abs(float(self.get_widget("y_region").get_widget("y_input").text()))
        self.publish(UserAction.PAN_REL_Y,data)

    @QtCore.Slot()
    def zoom_plus_update_handler(self):
        data = 1 + abs(float(self.get_widget("zoom_region").get_widget("zoom_input").text()))
        self.publish(UserAction.ZOOM,data)

    @QtCore.Slot()
    def zoom_minus_update_handler(self):
        data = 1 - abs(float(self.get_widget("zoom_region").get_widget("zoom_input").text()))
        self.publish(UserAction.ZOOM,data)
