import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QTableView, QHeaderView
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from maingui import Ui_MainWindow

#PHOTO VIEWER && ZOOM IMAGE
class PhotoViewer(QtWidgets.QGraphicsView):
	photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

	def __init__(self, parent):
		super(PhotoViewer, self).__init__(parent)
		self._zoom = 0
		self._empty = True
		self._scene = QtWidgets.QGraphicsScene(self)
		self._photo = QtWidgets.QGraphicsPixmapItem()
		self._scene.addItem(self._photo)
		self.setScene(self._scene)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
		self.setFrameShape(QtWidgets.QFrame.NoFrame)

	def hasPhoto(self):
		return not self._empty

	def fitInView(self, scale=True):
		rect = QtCore.QRectF(self._photo.pixmap().rect())
		if not rect.isNull():
			self.setSceneRect(rect)
			if self.hasPhoto():
				unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
				self.scale(1 / unity.width(), 1 / unity.height())
				viewrect = self.viewport().rect()
				scenerect = self.transform().mapRect(rect)
				factor = min(viewrect.width() / scenerect.width(),
							 viewrect.height() / scenerect.height())
				self.scale(factor, factor)
			self._zoom = 0

	def setPhoto(self, pixmap=None):
		self._zoom = 0
		if pixmap and not pixmap.isNull():
			self._empty = False
			self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
			self._photo.setPixmap(pixmap)
		else:
			self._empty = True
			self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
			self._photo.setPixmap(QtGui.QPixmap())
		self.fitInView()

	def wheelEvent(self, event):
		if self.hasPhoto():
			if event.angleDelta().y() > 0:
				factor = 1.25
				self._zoom += 1
			else:
				factor = 0.8
				self._zoom -= 1
			if self._zoom > 0:
				self.scale(factor, factor)
			elif self._zoom == 0:
				self.fitInView()
			else:
				self._zoom = 0

	def toggleDragMode(self):
		if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
			self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
		elif not self._photo.pixmap().isNull():
			self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

	def mousePressEvent(self, event):
		if self._photo.isUnderMouse():
			self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
		super(PhotoViewer, self).mousePressEvent(event)

#-------------------##---------Main Window------------##-------------------------#
class MainWindow(QtWidgets.QWidget):
	def __init__(self):
		#INIT
		self.main_ui = QMainWindow()
		self.ui = Ui_MainWindow()
		super(MainWindow, self).__init__()

		self.ui.setupUi(self.main_ui)
		self.ui.stackedWidget.setCurrentWidget(self.ui.main)
		
		#Publish image
		self.viewer = PhotoViewer(self)
		self.ui.gridLayout_14.addWidget(self.viewer, 0, 0, 1, 2)

		#BUTTON
		self.ui.click_to_search.clicked.connect(self.search)
		self.ui.backbutton1.clicked.connect(self.main_screen)
		self.ui.start_lookup.clicked.connect(self.main_screen)
		self.ui.start_lookup_2.clicked.connect(self.information)
		self.ui.backbutton2.clicked.connect(self.search)
		self.ui.find_path.clicked.connect(self.main_screen)
		self.ui.refresh.clicked.connect(self.refresh)
		
	def refresh(self):
		self.viewer.setPhoto(QtGui.QPixmap('ToDrawMap.png'))
	
	def main_screen(self):
		self.ui.stackedWidget.setCurrentWidget(self.ui.main)

	def search(self):
		self.ui.stackedWidget.setCurrentWidget(self.ui.search_bar)
		buildings = ('A4', '402 Academic Affair A4', '202 purpose Room A4', 'B9', '202 B9', '101 B9', 'C5', 'Hall A5', 'B6','303 B6','205 B6','Admintrasion A4', '505 library A4', 'library A2')
		model = QStandardItemModel(len(buildings), 1)
		for row, building in enumerate(buildings):
			item = QStandardItem(building)
			model.setItem(row, 0, item)
		filter_proxy_model = QSortFilterProxyModel()
		filter_proxy_model.setSourceModel(model)
		filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
		filter_proxy_model.setFilterKeyColumn(0)
		
		self.ui.destination.setStyleSheet('font-size: 25px; height: 40px;')
		self.ui.destination.textChanged.connect(filter_proxy_model.setFilterRegExp)
		self.ui.departure.setStyleSheet('font-size: 25px; height: 40px;')
		self.ui.departure.textChanged.connect(filter_proxy_model.setFilterRegExp)
		

		self.ui.room_building.setStyleSheet('font-size: 35px;')
		self.ui.room_building.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.ui.room_building.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.ui.room_building.horizontalHeader().hide()
		self.ui.room_building.verticalHeader().hide()
		self.ui.room_building.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.ui.room_building.setModel(filter_proxy_model)
		self.ui.room_building.clicked.connect(self.cell_was_clicked)

	def cell_was_clicked(self):
		#GET VALUE IN CELL
		index = self.ui.room_building.selectionModel().currentIndex()
		value = index.sibling(index.row(),index.column()).data()
	def information(self):
		self.ui.stackedWidget.setCurrentWidget(self.ui.page_info)
	
	def show(self):
		self.main_ui.showMaximized()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main_win = MainWindow()
	main_win.show()
	sys.exit(app.exec_())
