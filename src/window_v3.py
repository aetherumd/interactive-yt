from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage
import sys, yt, typing
from enum import Enum
from typing import Any

import yt.data_objects
import yt.data_objects.static_output
from info_handling import EventBroker, Publisher, Subscriber

"""
biggest problems atm:
strings as keys are inconsistent at best, maybe try enums?
layouts
"""

class PlotOption(Enum):
    SLICE_PLOT = 1,
    PROJECTION_PLOT = 2,
    PARTICLE_PLOT = 3,
    PARTICLE_PHASE_PLOT = 4

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
        self.subscribe(["img"])
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)
        image = self.add_widget("image", QLabel(self))
        image.setScaledContents(True)
    
    def handle_update(self, name: str):
        match name:
            case "img":
                self.set_img(self.query("img"))
            case _:
                pass
    
    def set_img(self, img: QImage):
        self.get_widget("image").setPixmap(QPixmap.fromImage(img))

class PlotMaker(Subscriber, Publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribe(["create_plot"])
        self.add_field("plot", None, None)
        self.add_field("img", None, None)

    def handle_update(self, name: str):
        match name:
            case "create_plot":
                success: bool = False
                match self.query("plot_type"):
                    case PlotOption.SLICE_PLOT:
                        success = self.create_slice_plot()
                    case PlotOption.PROJECTION_PLOT:
                        success = self.create_projection_plot()
                    case PlotOption.PARTICLE_PLOT:
                        success = self.create_particle_plot()
                    case _:
                        pass
                if success:
                    plot : yt.AxisAlignedSlicePlot | yt.OffAxisSlicePlot | yt.AxisAlignedProjectionPlot |  yt.OffAxisProjectionPlot | yt.ParticleProjectionPlot | yt.ParticlePhasePlot = self.query("plot")
                    if plot is not None:
                        path: str = self.query("img_name")
                        plot.save(path)
                        self.publish("img", QImage(path))
            case _:
                pass

    def create_slice_plot(self):
        ds = self.query("dataset")
        normal = self.query("normal")
        fields = self.query("fields")
        if ds is not None and normal is not None and fields is not None:
            params = {
                "center": self.query("center", "center"),
                "width": self.query("width", None),
                "axes_unit": self.query("axes_unit", None),
                "origin": self.query("origin", "center-window"),
                "fontsize": self.query("fontsize", 18),
                "field_parameters": self.query("field_parameters", None),
                "window_size": self.query("windows_size", 8.0),
                "aspect": self.query("aspect", None),
                "data_source": self.query("data_source", None),
                "buff_size": self.query("buff_size", (800, 800)),
            }

            # TODO fix query jank

            existing_params = {key: value for key, value in params.items() if value is not None}

            plot = yt.SlicePlot(
                ds, normal, fields, **existing_params 
            )
            self.publish("plot", plot)
            return True
        return False

    def create_projection_plot(self):
        ds = self.query("dataset")
        normal = self.query("normal")
        fields = self.query("fields")
        if ds is not None and normal is not None and fields is not None:
            plot = yt.ProjectionPlot(
                ds, normal, fields, 
                center = self.query("center", "center"),
                width = self.query("width", None),
                axes_unit = self.query("axes_unit", None),
                origin = self.query("origin", "center-window"),
                fontsize = self.query("fontsize", 18),
                field_parameters = self.query("field_parameters", None),
                window_size = self.query("windows_size", 8.0),
                aspect = self.query("aspect", None),
                data_source = self.query("data_source", None),
                buff_size = self.query("buff_size", (800, 800)),
            )
            
            # TODO fix query jank

            self.publish("plot", plot)
            return True
        return False

    def create_particle_plot(self):
        ds = self.query("dataset")
        field_x = self.query("normal")
        field_y = self.query("fields")
        
        if ds is not None and field_x is not None and field_y is not None:
            plot = yt.ParticlePlot(
                ds, field_x, field_y, 
                z_fields = self.query("z_fields", None),
                color = self.query("particle_plot_color", "b"),
                weight_field = self.query("weight_field", None),
                fontsize = self.query("fontsize", 18),
                data_source = self.query("data_source", None),
                center = self.query("center", "center"),
                width = self.query("width", None),
                depth = self.query("depth", None),
                axes_unit = self.query("axes_unit", None),
                origin = self.query("origin", None), # TODO : figure these ones out
                window_size = self.query("windows_size", 8.0),
                aspect = self.query("aspect", None),
                x_bins = self.query("x_bins", None),
                y_bins = self.query("y_bins", None),
                deposition = self.query("deposition", None),
                figure_size = self.query("figure_size", None),
            )
            
            # TODO fix query jank
            
            self.publish("plot", plot)
            return True
        return False

class PlotManager(Subscriber, Publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activated = False
        self.subscribe(["plot", 
                        "pan_x", 
                        "pan_y", 
                        "pan_rel_x", 
                        "pan_rel_y", 
                        "zoom", 
                        "axes_unit", 
                        "img_unit", 
                        "center", 
                        "flip_horizontal", 
                        "flip_vertical", 
                        "swap_axes"])

    def handle_update(self, name: str):
        if not self.activated and name == "plot":
            self.activated = True
        if self.activated:
            match self.query("plot_type"):
                case PlotOption.SLICE_PLOT | PlotOption.PROJECTION_PLOT | PlotOption.PARTICLE_PLOT:
                    plot: yt.AxisAlignedSlicePlot | yt.OffAxisSlicePlot | yt.AxisAlignedProjectionPlot |  yt.OffAxisProjectionPlot | yt.ParticleProjectionPlot = self.query("plot")
                    data = self.query(name)
                    if plot is not None and data is not None:
                        match name:
                            case "pan_x":
                                plot.pan((data, 0))
                            case "pan_y":
                                plot.pan((0, data))
                            case "pan_rel_x":
                                plot.pan_rel((data, 0))
                            case "pan_rel_y":
                                plot.pan_rel((0, data))
                            case "zoom":
                                plot.zoom(data)
                            case "axes_unit":
                                plot.set_axes_unit(data)
                            case "img_unit":
                                plot.set_unit(data)
                            case "center":
                                plot.set_center(data)
                            case "flip_horizontal":
                                plot.flip_horizontal()
                            case "flip_vertical":
                                plot.flip_vertical()
                            case "swap_axes":
                                plot.swap_axes()
                            # TODO: add functionality for annotations
                            case _:
                                pass
                        if plot is not None:
                            path: str = self.query("img_name")
                            plot.save(path)
                            self.publish("img", QImage(path))
                case PlotOption.PARTICLE_PHASE_PLOT:
                    phase_plot: yt.ParticlePhasePlot = self.query("data_source")
                    data = self.query(name)
                    match name:
                        case "img_unit":
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
        self.add_field("plot_type", PlotOption.SLICE_PLOT, None)
        self.add_field("dataset", None, None)
        self.add_field("center", (0.5,0.5,0.5), None)
        self.add_field("zoom", 1.0, None)
        self.add_field("normal", "x", None)
        self.add_field("width", None, None)
        self.add_field("weight_field", None, None)
        self.add_field("data_source", None, None)
        self.add_field("buff_size", None, None)
        self.add_field("moment", None, None)
        self.add_field("img_name", "tmp.png", None)
        self.add_field("create_plot", None, None)
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class SliceProjectionPlotPanel(Publisher, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)
        self.add_field("fields", None, None)
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class ParticlePlotPanel(Publisher, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)
        self.add_field("field_x", None, None)
        self.add_field("field_y", None, None)
        self.add_field("field_z", None, None)
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class EditPlotPanel(Publisher, QAdjustable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)
        self.add_field("pan_x", 0, 0)
        self.add_field("pan_y", 0, 0)
        self.add_field("pan_rel_x", 0, 0)
        self.add_field("pan_rel_y", 0, 0)
        self.add_field("zoom", 1, 1)
        self.add_field("axes_unit", None, None)
        self.add_field("img_unit", None, None)
        self.__init_layout__()

    def __init_layout__(self):
        layout = QHBoxLayout(self)

class Test(Publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ds = yt.load("C:\\Users\\jonat\\PycharmProjects\\gems\\review\\ricotti_simulation\\output_00273")
        self.add_field("dataset", None, None)
        self.add_field("fields", [], None)
        
        self.publish("dataset", ds)
        self.publish("fields", [("ramses", "HeII")])
        self.publish("create_plot", True)

        self.publish("zoom", 10)

        # kinda works !

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    ytw = YtWindow()
    ytw.resize(600,600)
    ytw.show()

    sys.exit(app.exec())