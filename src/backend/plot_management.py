from PySide6.QtWidgets import *
from PySide6.QtGui import QImage
from typing import *

from backend.info_handling import *
from backend.options import *

import yt

PlotType = Union[ 
    yt.AxisAlignedSlicePlot,
    yt.OffAxisSlicePlot,
    yt.AxisAlignedProjectionPlot,
    yt.OffAxisProjectionPlot,
    yt.ParticleProjectionPlot,
    yt.ParticlePhasePlot
]

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
                    plot: PlotType = self.query(Data.PLOT)
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
