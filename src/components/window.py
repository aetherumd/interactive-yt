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

        tabbar = QTabBar()
        tabbar.addTab("make plot")
        tabbar.addTab("edit plot")
        self.add_widget("tabbar", tabbar)
        tabbar.currentChanged.connect(self.tab_bar_clicked)

        img_pane = self.add_widget("img_pane", ImagePanel(self.broker))
        make_plot_pane = self.add_widget("make_plot_panel", MakePlotPanel(self.broker))
        edit_plot_pane = self.add_widget("edit_plot_panel", EditPlotPanel(self.broker))

        self.plot_maker = PlotMaker(self.broker)
        self.plot_manager = PlotManager(self.broker)

        left_layout.addWidget(img_pane)
        right_layout.addWidget(tabbar)
        right_layout.addWidget(make_plot_pane)
        right_layout.addWidget(edit_plot_pane)
        edit_plot_pane.setVisible(False)

        layout.addWidget(left)
        layout.addWidget(right)

        ## Testing code
        ##self.broker.publish(Data.IMAGE, QImage("tmp.png"))
        ##test = Test(self.broker)

        left.setFixedWidth(self.width()//2-1)
        left.setFixedHeight(self.width()//2-1)
    
    @QtCore.Slot()
    def tab_bar_clicked(self):
        print("hello")
        tabbar = self.get_widget("tabbar")
        if type(tabbar) is QTabBar:
            print(tabbar.currentIndex())
            match tabbar.currentIndex():
                case 0:
                    mpp = self.get_widget("make_plot_panel")
                    epp = self.get_widget("edit_plot_panel")
                    if isinstance(mpp, QWidget) and isinstance(epp, QWidget):
                        mpp.setVisible(True)
                        epp.setVisible(False)
                case 1:
                    mpp = self.get_widget("make_plot_panel")
                    epp = self.get_widget("edit_plot_panel")
                    if isinstance(mpp, QWidget) and isinstance(epp, QWidget):
                        mpp.setVisible(False)
                        epp.setVisible(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        left = self.widgets.get("left")
        if type(left) is QWidget:
            left.setFixedWidth(event.size().width()//2)
            left.setFixedHeight(event.size().width()//2)
            
            left.setMaximumWidth(event.size().width() - left.width())

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