from PySide6 import QtCore
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QPixmap, QImage, QRegularExpressionValidator
from PySide6.QtWidgets import *

from components.ui import QAdjustable
from backend.info_handling import *
from backend.options import *

from ast import literal_eval
import yt, re

class MakePlotPanel(Publisher, Subscriber, QAdjustable):
    """
    Gives options related to plot creation, depending on selected plot type.

    TODO:
        Implement functionality for options in options.PlotOption
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QAdjustable.__init__(self)

        self.subscribe([PlotOption.CELL_FIELDS, PlotOption.EPF])

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
        plot_type.addItems(["Slice Plot", "Projection Plot", "Particle Plot"])
        self.widgets.update({PlotOption.PLOT_TYPE: plot_type})
        plot_type.currentIndexChanged.connect(self.plot_type_handler)

        sliceprojpane = SliceProjectionPlotPanel(self.broker)
        self.widgets.update({PlotTypeOption.SLICE_PLOT: sliceprojpane})

        particlepane = ParticlePlotPanel(self.broker)
        self.widgets.update({PlotTypeOption.PARTICLE_PLOT: particlepane})
        particlepane.setVisible(False)

        file_pane = QWidget()
        fp_layout = QVBoxLayout(file_pane)

        self.f = QFileDialog(self)

        self.open_type = QListWidget()
        self.open_type.addItems(["Folder", "File"])
        self.open_type.currentItemChanged.connect(self.file_type_handler)
        h = self.open_type.sizeHintForRow(0)
        self.open_type.setFixedHeight(2 * h + 10)

        file_dialog = QPushButton("Open File/Folder")
        file_dialog.clicked.connect(self.open_file_dialog)

        fp_layout.addWidget(self.open_type)
        fp_layout.addWidget(file_dialog)

        file_pane.setLayout(fp_layout)

        self.widgets.update({PlotOption.DATASET: file_pane})

        field_pane = QWidget()
        field_layout = QVBoxLayout(field_pane)

        self.field_type = QListWidget()
        self.field_type.addItems(["Cell Fields", "EPFs"])
        self.num_type = 0
        self.field_type.currentItemChanged.connect(self.field_type_handler)
        h = self.field_type.sizeHintForRow(0)
        self.field_type.setFixedHeight(2 * h + 10)

        self.l = QLineEdit(self)
        self.t = QLabel(self)
        field_dialog = QPushButton("Enter extra fields")
        field_dialog.clicked.connect(self.open_field_dialog)

        field_layout.addWidget(self.field_type)
        field_layout.addWidget(field_dialog)

        field_pane.setLayout(field_layout)

        self.widgets.update({PlotOption.CELL_FIELDS: field_pane})

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
    def file_type_handler(self):
        index = self.open_type.currentRow()
        if index == 0:
            self.f.setFileMode(QFileDialog.FileMode.Directory)
        else:
            self.f.setFileMode(QFileDialog.FileMode.ExistingFile)

    @QtCore.Slot()
    def open_file_dialog(self):
        self.f.exec()
        s = self.f.selectedFiles()[0]
        if s is not None:
            fields = self.query(PlotOption.CELL_FIELDS)
            epf = self.query(PlotOption.EPF)
            ds = yt.load(s, fields = fields, extra_particle_fields = epf)
            self.publish(PlotOption.DATASET, ds)

    def field_type_handler(self):
        index = self.field_type.currentRow()
        if index == 0:
            self.num_type = 0
        else:
            self.num_type = 1

    @QtCore.Slot()
    def open_field_dialog(self):
        popup = QDialog(self)
        popup_layout = QVBoxLayout()

        self.l.setPlaceholderText("Enter some text. Press enter when done.")
        self.l.setValidator(QRegularExpressionValidator(QRegularExpression("\[.*\]"), self.l))
        self.l.returnPressed.connect(self.return_validate)

        popup_layout.addWidget(self.l)
        popup_layout.addWidget(self.t)
        popup.setLayout(popup_layout)

        popup.exec()

    def return_validate(self):
        self.t.setText(f"Entered: {self.l.text()}")

        if self.l.hasAcceptableInput():
            if self.num_type == 0:
                self.publish(PlotOption.CELL_FIELDS, self.l.text().lstrip("[").rstrip("]").split(","))
            else:
                self.publish(PlotOption.EPF, self.l.text().lstrip("[").rstrip("]").split(","))

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
            if field.currentText() is not "":
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
            if field.currentText() is not "":
                self.publish(ParticlePlotOption.X_FIELD, literal_eval(field.currentText()))
    
    @QtCore.Slot()
    def y_field_manager(self):
        field = self.widgets.get(ParticlePlotOption.Y_FIELD)
        if type(field) is QComboBox:
            if field.currentText() is not "":
                self.publish(ParticlePlotOption.Y_FIELD, literal_eval(field.currentText()))

    @QtCore.Slot()
    def z_field_manager(self):
        field = self.widgets.get(ParticlePlotOption.Z_FIELDS)
        if type(field) is QComboBox:
            if field.currentText() is not "":
                self.publish(ParticlePlotOption.Z_FIELDS, literal_eval(field.currentText()))

    @QtCore.Slot()
    def weight_field_manager(self):
        field = self.widgets.get(PlotOption.WEIGHT_FIELD)
        if type(field) is QComboBox:
            if field.currentText() is not "":
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
        layout = QHBoxLayout(self)
