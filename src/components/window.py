from PySide6.QtWidgets import *
import yt
from typing import *

from components.panels import *
from components.ui import QAdjustable

from backend.plot_management import PlotMaker, PlotManager
from backend.options import *
from backend.info_handling import *

PlotType = Union[ 
    yt.AxisAlignedSlicePlot,
    yt.OffAxisSlicePlot,
    yt.AxisAlignedProjectionPlot,
    yt.OffAxisProjectionPlot,
    yt.ParticleProjectionPlot,
    yt.ParticlePhasePlot
]

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