from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
import sys, yt, typing
from enum import Enum
from typing import *
from v_3_options import *
import yt.data_objects
import yt.data_objects.static_output
from info_handling import EventBroker, Publisher, Subscriber

"""
biggest problems atm:
strings as keys are inconsistent at best, maybe try enums?
layouts
"""

PlotType = Union[ 
    yt.AxisAlignedSlicePlot,
    yt.OffAxisSlicePlot,
    yt.AxisAlignedProjectionPlot,
    yt.OffAxisProjectionPlot,
    yt.ParticleProjectionPlot,
    yt.ParticlePhasePlot
]

class QAdjustable(QWidget):
    def __init__(self):
        super().__init__()
        self.widgets: dict[QWidget] = dict()

    def add_widget(self, name: str, w: QWidget) -> QWidget:
        self.widgets[name] = w
        return w

    def get_widget(self, name: str) -> QWidget:
        return self.widgets[name]

class YtWindow(QAdjustable):
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

        test = Test(self.broker)

class ImagePanel(Subscriber, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)
        self.subscribe([Data.IMAGE])
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)
        image = self.add_widget("image", QLabel(self))
        image.setScaledContents(True)
    
    def handle_update(self, name: str):
        match name:
            case Data.IMAGE:
                self.set_img(self.query(name))
            case _:
                pass
    
    def set_img(self, img: QImage):
        self.get_widget("image").setPixmap(QPixmap.fromImage(img))

class PlotMaker(Subscriber, Publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribe([UserAction.CREATE_PLOT])
        
        for op in Data:
            self.add_field(op)

    def handle_update(self, name: V3Option):
        match name:
            case UserAction.CREATE_PLOT:
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
                            # TODO: add functionality for annotations
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
                        # TODO: add functionality for annotations
                        case _:
                            pass
                case _:
                    pass

class MakePlotPanel(Publisher, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)

        for op in PlotOption:
            self.add_field(op)
        
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class SliceProjectionPlotPanel(Publisher, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)

        for op in SliceProjPlotOption:
            self.add_field(op)

        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class ParticlePlotPanel(Publisher, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)

        for op in ParticlePlotOption:
            self.add_field(op)

        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class EditPlotPanel(Publisher, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)
        
        for op in UserAction:
            self.add_field(op)

        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class Test(Publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ds = yt.load("C:\\Users\\jonat\\PycharmProjects\\gems\\review\\ricotti_simulation\\output_00273")
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
        # kinda works !

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    ytw = YtWindow()
    ytw.resize(600,600)
    ytw.show()

    sys.exit(app.exec())