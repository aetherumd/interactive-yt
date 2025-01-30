from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
import sys, yt, typing
from enum import Enum
from typing import *
from options import *
import yt.data_objects
import yt.data_objects.static_output
from info_handling import EventBroker, Publisher, Subscriber
import re
from ast import literal_eval

PlotType = Union[ 
    yt.AxisAlignedSlicePlot,
    yt.OffAxisSlicePlot,
    yt.AxisAlignedProjectionPlot,
    yt.OffAxisProjectionPlot,
    yt.ParticleProjectionPlot,
    yt.ParticlePhasePlot
]

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

class YtWindow(QAdjustable):
    """
    Frontend handler.

    Contains top-level widgets, leaves information processing to its children.
    """
    def __init__(self):
        super().__init__()
        self.broker = EventBroker()
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

        left = self.add_widget("left", QWidget())
        right = self.add_widget("right", QWidget())

        left_layout = QVBoxLayout(left)
        right_layout = QVBoxLayout(right)

        img_pane = self.add_widget("img_pane", ImagePanel(self.broker))
        make_plot_pane = self.add_widget("make_plot_panel", MakePlotPanel(self.broker))
        edit_plot_pane = self.add_widget("edit_plot_panel", EditPlotPanel(self.broker))
        self.plot_maker = PlotMaker(self.broker)
        self.plot_manager = PlotManager(self.broker)

        left_layout.addWidget(img_pane)
        right_layout.addWidget(make_plot_pane)
        right_layout.addWidget(edit_plot_pane)

        layout.addWidget(left)
        layout.addWidget(right)

        ## Testing code
        ##self.broker.publish(Data.IMAGE, QImage("tmp.png"))
        ##test = Test(self.broker)

        left.setFixedWidth(self.width()//2-1)
        left.setFixedHeight(self.width()//2-1)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        left = self.widgets.get("left")
        if type(left) is QWidget:
            left.setFixedWidth(event.size().width()//2)
            left.setFixedHeight(event.size().width()//2)
            
            left.setMaximumWidth(event.size().width() - left.width())

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

class PlotMaker(Subscriber, Publisher):
    """
    Backend element responsible for making plots.

    Subscribed to UserAction.CREATE_PLOT, creates new plot based on user-selected
    arguments.

    TODO: 
        It is possible to consolidate create_slice_plot() and create_projection_plot().
        Not sure if we want to do so.
        
        Not sure if its possible to do particle_plot as well as its a method not a constructor.
        Something to look into.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribe([UserAction.CREATE_PLOT])
        
        for op in Data:
            self.add_field(op)

    def handle_update(self, name: V3Option):
        match name:
            case UserAction.CREATE_PLOT:
                print("BBBB")
                success: bool = False
                match self.query(PlotOption.PLOT_TYPE):
                    case PlotTypeOption.SLICE_PLOT:
                        success = self.create_slice_plot()
                    case PlotTypeOption.PROJECTION_PLOT:
                        success = self.create_projection_plot()
                    case PlotTypeOption.PARTICLE_PLOT:
                        success = self.create_particle_plot()
                    case _:
                        pass
                if success:
                    plot : PlotType = self.query(Data.PLOT)
                    if plot is not None:
                        path: str = self.query(PlotOption.SAVE_TO)
                        plot.save(path)
                        self.publish(Data.IMAGE, QImage(path))
            case _:
                pass

    def create_slice_plot(self):
        ds = self.query(PlotOption.DATASET)
        normal = self.query(SliceProjPlotOption.NORMAL)
        fields = self.query(SliceProjPlotOption.FIELDS)
        print(ds)
        print(normal)
        print(fields)
        if ds is not None and normal is not None and fields is not None:
            params = {
                "center": self.query(PlotOption.CENTER),
                "width": self.query(PlotOption.WIDTH),
                "axes_unit": self.query(PlotOption.AXES_UNIT),
                "origin": self.query(PlotOption.ORIGIN),
                "fontsize": self.query(PlotOption.FONT_SIZE),
                "field_parameters": self.query(PlotOption.FIELD_PARAMETERS),
                "window_size": self.query(PlotOption.WINDOW_SIZE),
                "aspect": self.query(PlotOption.ASPECT),
                "data_source": self.query(PlotOption.DATA_SOURCE),
                "buff_size": self.query(PlotOption.BUFF_SIZE),
            }
            
            existing_params = {key: value for key, value in params.items() if value is not None}
            plot = yt.SlicePlot(
                ds, normal, fields, **existing_params 
            )
            self.publish(Data.PLOT, plot)
            return True
        return False

    def create_projection_plot(self):
        ds = self.query(PlotOption.DATASET)
        normal = self.query(SliceProjPlotOption.NORMAL)
        fields = self.query(SliceProjPlotOption.FIELDS)
        if ds is not None and normal is not None and fields is not None:
            params = {
                "center": self.query(PlotOption.CENTER),
                "width": self.query(PlotOption.WIDTH),
                "axes_unit": self.query(PlotOption.AXES_UNIT),
                "origin": self.query(PlotOption.ORIGIN),
                "fontsize": self.query(PlotOption.FONT_SIZE),
                "field_parameters": self.query(PlotOption.FIELD_PARAMETERS),
                "window_size": self.query(PlotOption.WINDOW_SIZE),
                "aspect": self.query(PlotOption.ASPECT),
                "data_source": self.query(PlotOption.DATA_SOURCE),
                "buff_size": self.query(PlotOption.BUFF_SIZE),
            }

            existing_params = {key: value for key, value in params.items() if value is not None}

            plot = yt.ProjectionPlot(
                ds, normal, fields, **existing_params
            )

            self.publish(Data.PLOT, plot)
            return True
        return False

    def create_particle_plot(self):
        ds = self.query(PlotOption.DATASET)
        x_field = self.query(ParticlePlotOption.X_FIELD)
        y_field = self.query(ParticlePlotOption.Y_FIELD)
        
        if ds is not None and x_field is not None and y_field is not None:

            params = {
                "z_fields": self.query(ParticlePlotOption.Z_FIELDS),
                "color": self.query(ParticlePlotOption.COLOR),
                "weight_field": self.query(PlotOption.WEIGHT_FIELD),
                "fontsize": self.query(PlotOption.FONT_SIZE),
                "data_source": self.query(PlotOption.DATA_SOURCE),
                "center": self.query(PlotOption.CENTER),
                "width": self.query(PlotOption.WIDTH),
                "depth": self.query(ParticlePlotOption.DEPTH),
                "axes_unit": self.query(PlotOption.AXES_UNIT),
                "origin": self.query(PlotOption.ORIGIN),
                "window_size": self.query(PlotOption.WINDOW_SIZE),
                "aspect": self.query(PlotOption.ASPECT),
                "x_bins": self.query(ParticlePlotOption.X_BINS),
                "y_bins": self.query(ParticlePlotOption.Y_BINS),
                "deposition": self.query(ParticlePlotOption.DEPOSITION),
                "figure_size": self.query(ParticlePlotOption.FIGURE_SIZE),
            }

            existing_params = {key: value for key, value in params.items() if value is not None}

            plot = yt.ParticlePlot(
                ds, x_field, y_field, **existing_params
            )
            
            self.publish(Data.PLOT, plot)
            return True
        return False

class PlotManager(Subscriber, Publisher):
    """
    Backend element responsible for handling user-input plot manipulation.

    TODO:
        Do we need to handle particle phase plots? If yes, what are they good for.

        Add functionality for annotations.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activated = False
        self.subscribe([Data.PLOT, 
                        UserAction.PAN_X,
                        UserAction.PAN_Y,
                        UserAction.PAN_REL_X,
                        UserAction.PAN_REL_Y,
                        UserAction.ZOOM,
                        UserAction.AXES_UNIT,
                        UserAction.IMG_UNIT,
                        UserAction.CENTER,
                        UserAction.FLIP_HORIZONTAL,
                        UserAction.FLIP_VERTICAL,
                        UserAction.SWAP_AXES,
                        ])

    def handle_update(self, name: V3Option):
        if not self.activated and name is Data.PLOT:
            self.activated = True
        if self.activated:
            match self.query(PlotOption.PLOT_TYPE):
                case PlotTypeOption.SLICE_PLOT | PlotTypeOption.PROJECTION_PLOT | PlotTypeOption.PARTICLE_PLOT:
                    plot: PlotType = self.query(Data.PLOT)
                    data = self.query(name)
                    if plot is not None and data is not None:
                        match name:
                            case UserAction.PAN_X:
                                plot.pan((data, 0))
                            case UserAction.PAN_Y:
                                plot.pan((0, data))
                            case UserAction.PAN_REL_X:
                                plot.pan_rel((data, 0))
                            case UserAction.PAN_REL_Y:
                                plot.pan_rel((0, data))
                            case UserAction.ZOOM:
                                plot.zoom(data)
                            case UserAction.AXES_UNIT:
                                plot.set_axes_unit(data)
                            case UserAction.IMG_UNIT:
                                plot.set_unit(data)
                            case UserAction.CENTER:
                                plot.set_center(data)
                            case UserAction.FLIP_HORIZONTAL:
                                plot.flip_horizontal()
                            case UserAction.FLIP_VERTICAL:
                                plot.flip_vertical()
                            case UserAction.SWAP_AXES:
                                plot.swap_axes()
                            case _:
                                pass
                        path: str = self.query(PlotOption.SAVE_TO)
                        plot.save(path)
                        self.publish(Data.IMAGE, QImage(path))
                case PlotTypeOption.PARTICLE_PHASE_PLOT:
                    phase_plot: yt.ParticlePhasePlot = self.query(PlotOption.PLOT_TYPE)
                    data = self.query(name)
                    match name:
                        case UserAction.IMG_UNIT:
                            phase_plot.set_unit(data)
                        case _:
                            pass
                case _:
                    pass

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
        print("AAA")
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
        print(self.query(SliceProjPlotOption.NORMAL))

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
                print(type(ds))
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
                print(type(ds))
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
        layout = QHBoxLayout(self)

class Test(Publisher):
    """
    Testing basic functionality.

    To use, make sure that PATH is set to the desired dataset.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ds = yt.load("PATH")
        self.add_field(PlotOption.DATASET)
        self.add_field(SliceProjPlotOption.FIELDS)
        
        self.publish(PlotOption.DATASET, ds)
        print("published dataset")
        self.publish(SliceProjPlotOption.NORMAL, "x")
        self.publish(SliceProjPlotOption.FIELDS, [("ramses", "HeII")])
        print("published fields")
        self.publish(UserAction.CREATE_PLOT, True)
        print("created plot")

        self.publish(UserAction.ZOOM, 10)
        print("done")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    ytw = YtWindow()
    ytw.resize(600,600)
    ytw.show()

    sys.exit(app.exec())