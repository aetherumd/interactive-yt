import sys
import os
import yt
from PySide6 import QtCore, QtGui 
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLabel

class MovImgWidget(QWidget):
	def __init__(self):
		super().__init__()
		#self.dir_btns = {}
		self.layout = QVBoxLayout(self)
		self.image_section = QLabel()
		"""self.controls_section = QWidget()
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
		
		self.dir_btns['up'].clicked.connect(self.move_up)
		self.dir_btns['down'].clicked.connect(self.move_down)
		self.dir_btns['left'].clicked.connect(self.move_left)
		self.dir_btns['right'].clicked.connect(self.move_right)
		self.dir_btns['in'].clicked.connect(self.zoom_in)
		self.dir_btns['out'].clicked.connect(self.zoom_out)

		self.layout.addWidget(self.image_section)"""
		self.layout.addWidget(self.controls_section)

	def update_image(self):
		for i in os.listdir("img"):
			os.remove(f"img/{i}")

		self.plot.save("img/")
		image = os.listdir("img")[0]

		self.image_section.setPixmap(QtGui.QPixmap(f"img/{image}"))

	@QtCore.Slot()
	def move_up(self):
		self.plot.pan_rel((0,-0.1))
		self.update_image()

	@QtCore.Slot()
	def move_down(self):
		self.plot.pan_rel((0,0.1))
		self.update_image()

	@QtCore.Slot()
	def move_left(self):
		self.plot.pan_rel((-0.1,0))
		self.update_image()

	@QtCore.Slot()
	def move_right(self):
		self.plot.pan_rel((0.1,0))
		self.update_image()

	@QtCore.Slot()
	def zoom_in(self):
		self.plot.zoom(2.0)
		self.update_image()

	@QtCore.Slot()
	def zoom_out(self):
		self.plot.zoom(0.5)
		self.update_image()

if __name__ == "__main__":
	app = QApplication([])
	
	ds = yt.load('ricotti_sim/output_00273-001/output_00273')
	p = yt.ProjectionPlot(ds,'y',('gas','density'))

	widget = MyWidget()
	widget.plot = p
	widget.update_image()
	widget.show()

	sys.exit(app.exec())
