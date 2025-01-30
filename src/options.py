from enum import Enum
from typing import *

V3Option = Union[
"PlotOption",
"SliceProjPlotOption",
"ParticlePlotOption",
"Data",
"UserAction",
]

class PlotTypeOption(Enum):
    SLICE_PLOT = 1,
    PROJECTION_PLOT = 2,
    PARTICLE_PLOT = 3,
    PARTICLE_PHASE_PLOT = 4

def data_tuple(data: Any, default: Any):
    return data, default

class PlotOption(Enum):
    PLOT_TYPE = 1, data_tuple(
        data=None,
        default=PlotTypeOption.SLICE_PLOT
    ),
    DATASET = 2, data_tuple(
        data=None,
        default=None
    ),
    CENTER = 3, data_tuple(
        data=None,
        default=[0.5, 0.5, 0.5]
    ),
    WIDTH = 4, data_tuple(
        data=None,
        default=None
    ),
    AXES_UNIT = 5, data_tuple(
        data=None,
        default=None
    ),
    ORIGIN = 6, data_tuple(
        data=None,
        default=None
    ),
    FONT_SIZE = 7, data_tuple(
        data=None,
        default=18
    ),
    FIELD_PARAMETERS = 8, data_tuple(
        data=None,
        default=None
    ),
    WINDOW_SIZE = 9, data_tuple(
        data=None,
        default=8.0
    ),
    ASPECT = 10, data_tuple(
        data=None,
        default=None
    ),
    DATA_SOURCE = 11, data_tuple(
        data=None,
        default=None
    ),
    BUFF_SIZE = 12, data_tuple(
        data=None,
        default=(800,800)
    ),
    WEIGHT_FIELD = 13, data_tuple(
        data=None,
        default=None
    ),
    SAVE_TO = 14, data_tuple(
        data=None,
        default="tmp.png"
    ),

class SliceProjPlotOption(Enum):
    NORMAL = 1, data_tuple(
        data=None,
        default="x"
    ),
    FIELDS = 2, data_tuple(
        data=None,
        default=None
    ),

class ParticlePlotOption(Enum):
    X_FIELD = 1, data_tuple(
        data=None,
        default=None
    ),
    Y_FIELD = 2, data_tuple(
        data=None,
        default=None
    ),
    Z_FIELDS = 3, data_tuple(
        data=None,
        default=None
    ),
    COLOR = 4, data_tuple(
        data=None,
        default="b"
    ),
    DEPTH = 5, data_tuple(
        data=None,
        default=None
    ),
    X_BINS = 6, data_tuple(
        data=None,
        default=None
    ),
    Y_BINS = 7, data_tuple(
        data=None,
        default=None
    ),
    DEPOSITION = 8, data_tuple(
        data=None,
        default=None
    ),
    FIGURE_SIZE = 9, data_tuple(
        data=None,
        default=None
    )

class Data(Enum):
    IMAGE = 1, data_tuple(
        data=None,
        default=None
    ),
    PLOT = 2, data_tuple(
        data=None,
        default=None
    ),

class UserAction(Enum):
    CREATE_PLOT = 1, data_tuple(
        data=None,
        default=False
    ),
    PAN_X = 2, data_tuple(
        data=None,
        default=0.0
    ),
    PAN_Y = 3, data_tuple(
        data=None,
        default=0.0
    ),
    PAN_REL_X = 4, data_tuple(
        data=None,
        default=0.0
    ),
    PAN_REL_Y = 5, data_tuple(
        data=None,
        default=0.0
    ),
    ZOOM = 6, data_tuple(
        data=None,
        default=1.0
    ),
    AXES_UNIT = 7, data_tuple(
        data=None,
        default=None
    ),
    IMG_UNIT = 8, data_tuple(
        data=None,
        default=None
    ),
    CENTER = 9, data_tuple(
        data=None,
        default=(0.5, 0.5)
    ),
    FLIP_HORIZONTAL = 10, data_tuple(
        data=None,
        default=False
    ),
    FLIP_VERTICAL = 11, data_tuple(
        data=None,
        default=False
    ),
    SWAP_AXES = 12, data_tuple(
        data=None,
        default=False
    ),
