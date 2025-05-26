#!/usr/bin/python

from multiprocessing import Process
from pathlib import Path
from threading import Lock

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
	QLayout, QPushButton, QRadioButton, QScrollBar, QSizePolicy, QVBoxLayout, QWidget)

from python_scripts.logger import Logger

from python_scripts.quickbac.data import ImageModifier, ImageProcessorFactory

LOGGER: Logger = Logger("QuickBacUI")
# LOGGER.verbose_enabled = True


class QuickBackUI(QWidget):
	def __init__(self, decider: ImageProcessorFactory):
		super().__init__()
		
		self.decider: ImageProcessorFactory = decider
		
		# TODO: does this help with stutters?
		self.update_lock: Lock = Lock()
		
		self.current_image_path: Path | None = None
		self.current_image: QImage | None = None
		self.finished_image: QImage | None = None
		
		if not self.objectName():
			self.setObjectName(u"main_widget")
		self.setEnabled(True)
		self.resize(1000, 950)
		self.setMinimumSize(QSize(1000, 0))
		self.setAcceptDrops(True)
		self.verticalLayout = QVBoxLayout(self)
		self.verticalLayout.setObjectName(u"verticalLayout")
		self.image = QLabel(self)
		self.image.setObjectName(u"image")
		size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
		size_policy.setHorizontalStretch(0)
		size_policy.setVerticalStretch(0)
		size_policy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
		self.image.setSizePolicy(size_policy)
		self.image.setMinimumSize(QSize(0, 360))
		self.image.setAcceptDrops(False)
		self.image.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
		self.image.setScaledContents(False)
		self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.image.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
		
		self.verticalLayout.addWidget(self.image)
		
		self.offset = QScrollBar(self)
		self.offset.setObjectName(u"offset")
		self.offset.setMinimum(0)
		self.offset.setMaximum(200)
		self.offset.setValue(100)
		self.offset.setOrientation(Qt.Orientation.Horizontal)
		
		self.verticalLayout.addWidget(self.offset)
		
		self.group_controls = QHBoxLayout()
		self.group_controls.setObjectName(u"group_controls")
		self.group_controls.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
		self.group_wanted = QGroupBox(self)
		self.group_wanted.setObjectName(u"group_wanted")
		self.verticalLayout_2 = QVBoxLayout(self.group_wanted)
		self.verticalLayout_2.setObjectName(u"verticalLayout_2")
		self.horizontal = QRadioButton(self.group_wanted)
		self.horizontal.setObjectName(u"horizontal")
		self.horizontal.setChecked(True)
		
		self.verticalLayout_2.addWidget(self.horizontal)
		
		self.vertical = QRadioButton(self.group_wanted)
		self.vertical.setObjectName(u"vertical")
		
		self.verticalLayout_2.addWidget(self.vertical)
		
		self.group_controls.addWidget(self.group_wanted)
		
		self.group_mode = QGroupBox(self)
		self.group_mode.setObjectName(u"group_mode")
		self.verticalLayout_3 = QVBoxLayout(self.group_mode)
		self.verticalLayout_3.setObjectName(u"verticalLayout_3")
		self.crop = QRadioButton(self.group_mode)
		self.crop.setObjectName(u"crop")
		self.crop.setChecked(True)
		
		self.verticalLayout_3.addWidget(self.crop)
		
		self.fill = QRadioButton(self.group_mode)
		self.fill.setObjectName(u"fill")
		
		self.verticalLayout_3.addWidget(self.fill)
		
		self.group_controls.addWidget(self.group_mode)
		
		self.group_guides = QGroupBox(self)
		self.group_guides.setObjectName(u"group_guides")
		self.gridLayout = QGridLayout(self.group_guides)
		self.gridLayout.setObjectName(u"gridLayout")
		self.vertical_50_percent = QCheckBox(self.group_guides)
		self.vertical_50_percent.setObjectName(u"vertical_50_percent")
		
		self.gridLayout.addWidget(self.vertical_50_percent, 0, 1, 1, 1)
		
		self.vertical_33_percent = QCheckBox(self.group_guides)
		self.vertical_33_percent.setObjectName(u"vertical_33_percent")
		
		self.gridLayout.addWidget(self.vertical_33_percent, 0, 0, 1, 1)
		
		self.horizontal_33_percent = QCheckBox(self.group_guides)
		self.horizontal_33_percent.setObjectName(u"horizontal_33_percent")
		
		self.gridLayout.addWidget(self.horizontal_33_percent, 1, 0, 1, 1)
		
		self.horizontal_50_percent = QCheckBox(self.group_guides)
		self.horizontal_50_percent.setObjectName(u"horizontal_50_percent")
		
		self.gridLayout.addWidget(self.horizontal_50_percent, 1, 1, 1, 1)
		
		self.vertical_66_percent = QCheckBox(self.group_guides)
		self.vertical_66_percent.setObjectName(u"vertical_66_percent")
		
		self.gridLayout.addWidget(self.vertical_66_percent, 0, 2, 1, 1)
		
		self.horizontal_66_percent = QCheckBox(self.group_guides)
		self.horizontal_66_percent.setObjectName(u"horizontal_66_percent")
		
		self.gridLayout.addWidget(self.horizontal_66_percent, 1, 2, 1, 1)
		
		self.group_controls.addWidget(self.group_guides)
		
		self.verticalLayout.addLayout(self.group_controls)
		
		self.buttons = QHBoxLayout()
		self.buttons.setObjectName(u"buttons")
		self.buttons.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
		self.button_cancel = QPushButton(self)
		self.button_cancel.setObjectName(u"button_cancel")
		
		self.buttons.addWidget(self.button_cancel)
		
		self.button_export = QPushButton(self)
		self.button_export.setObjectName(u"button_export")
		
		self.buttons.addWidget(self.button_export)
		
		self.verticalLayout.addLayout(self.buttons)
		
		self._retranslate_ui()
		
		QMetaObject.connectSlotsByName(self)
		
		self.vertical.toggled.connect(self.resize_current_image)
		self.horizontal.toggled.connect(self.resize_current_image)
		self.fill.toggled.connect(self.resize_current_image)
		self.crop.toggled.connect(self.resize_current_image)
		self.offset.valueChanged.connect(self.resize_current_image)
		self.vertical_33_percent.checkStateChanged.connect(self.resize_current_image)
		self.vertical_50_percent.checkStateChanged.connect(self.resize_current_image)
		self.vertical_66_percent.checkStateChanged.connect(self.resize_current_image)
		self.horizontal_33_percent.checkStateChanged.connect(self.resize_current_image)
		self.horizontal_50_percent.checkStateChanged.connect(self.resize_current_image)
		self.horizontal_66_percent.checkStateChanged.connect(self.resize_current_image)
		
		self.button_cancel.clicked.connect(self.reset_offset)
		self.button_export.clicked.connect(self.export)
		
		self.reset()
	
	def _retranslate_ui(self):
		self.setWindowTitle(QCoreApplication.translate("main_widget", u"QuickBac", None))
		self.image.setText(QCoreApplication.translate("main_widget", u"IMAGE HERE", None))
		self.group_wanted.setTitle(QCoreApplication.translate("main_widget", u"Wanted", None))
		self.horizontal.setText(QCoreApplication.translate("main_widget", u"Horizontal", None))
		self.vertical.setText(QCoreApplication.translate("main_widget", u"Vertical", None))
		self.group_mode.setTitle(QCoreApplication.translate("main_widget", u"Mode", None))
		self.crop.setText(QCoreApplication.translate("main_widget", u"Crop", None))
		self.fill.setText(QCoreApplication.translate("main_widget", u"Fill", None))
		self.group_guides.setTitle(QCoreApplication.translate("main_widget", u"Guides", None))
		self.vertical_50_percent.setText(QCoreApplication.translate("main_widget", u"v 50%", None))
		self.vertical_33_percent.setText(QCoreApplication.translate("main_widget", u"v 33%", None))
		self.horizontal_33_percent.setText(QCoreApplication.translate("main_widget", u"h 33%", None))
		self.horizontal_50_percent.setText(QCoreApplication.translate("main_widget", u"h 50%", None))
		self.vertical_66_percent.setText(QCoreApplication.translate("main_widget", u"v 66%", None))
		self.horizontal_66_percent.setText(QCoreApplication.translate("main_widget", u"h 66%", None))
		self.button_cancel.setText(QCoreApplication.translate("main_widget", u"Center", None))
		self.button_export.setText(QCoreApplication.translate("main_widget", u"Export", None))
	
	def export(self) -> None:
		if not self.current_image:
			return
		
		dialog = QFileDialog(self, "Export as", str(self.current_image_path.parent))
		url, _ = dialog.getSaveFileUrl()
		
		if url:
			LOGGER.info("exporting image as", url.toLocalFile())
			# quality 0 compresses the image, causing the UI to freeze
			# offload to another thread to keep the UI running
			Process(target=lambda: self.finished_image.save(url.toLocalFile(), quality=0)).start()
	
	def draw_guides(self, image: QImage) -> None:
		painter: QPainter = QPainter(image)
		
		painter.setPen(QColor(255, 0, 0))
		
		def draw_vertical_line(x_position: float) -> None:
			x: int = round(x_position)
			painter.drawLine(x, 0, x, image.height())
		
		if self.vertical_33_percent.isChecked():
			draw_vertical_line(image.width() / 3)
		if self.vertical_50_percent.isChecked():
			draw_vertical_line(image.width() / 2)
		if self.vertical_66_percent.isChecked():
			draw_vertical_line(image.width() / 3 * 2)
		
		def draw_horizontal_line(y_position: float) -> None:
			y: int = round(y_position)
			painter.drawLine(0, y, image.width(), y)
		
		if self.horizontal_33_percent.isChecked():
			draw_horizontal_line(image.height() / 3)
		if self.horizontal_50_percent.isChecked():
			draw_horizontal_line(image.height() / 2)
		if self.horizontal_66_percent.isChecked():
			draw_horizontal_line(image.height() / 3 * 2)
		
		painter.end()
	
	def resize_current_image(self) -> None:
		if not self.current_image or not self.update_lock.acquire(blocking=False):
			return
		
		modifier: ImageModifier = self.decider.get(self.horizontal.isChecked(), self.crop.isChecked())
		modified_image: QImage = modifier.modify(self.current_image, self.offset.value() / 100)
		
		LOGGER.verbose_log("scaling to", modified_image.size())
		
		self.finished_image = modified_image
		
		scaled_image: QImage = modified_image.scaled(
			self.image.size(),
			aspectMode=Qt.AspectRatioMode.KeepAspectRatio
		)
		
		self.draw_guides(scaled_image)
		
		self.image.setPixmap(QPixmap.fromImage(scaled_image))
		self.setWindowTitle(f"QuickBac - {self.finished_image.width()}x{self.finished_image.height()}")
		self.update_lock.release()
	
	def reset_offset(self) -> None:
		self.offset.setValue(100)
	
	def reset(self) -> None:
		self.current_image = None
		self.finished_image = None
		self.current_image_path = None
		self.image.setPixmap(QPixmap())
		
		self.offset.setValue(100)
		
		self.vertical_33_percent.setChecked(False)
		self.vertical_50_percent.setChecked(False)
		self.vertical_66_percent.setChecked(False)
		self.horizontal_33_percent.setChecked(False)
		self.horizontal_50_percent.setChecked(False)
		self.horizontal_66_percent.setChecked(False)
	
	def resizeEvent(self, event, /) -> None:
		self.resize_current_image()
	
	def dropEvent(self, event: QDropEvent, /) -> None:
		self.reset()
		
		file_path: str = event.mimeData().urls()[0].toLocalFile()
		self.current_image_path = Path(file_path)
		self.current_image = QImage(self.current_image_path)
		
		LOGGER.info(f"new image: {file_path}")
		
		self.resize_current_image()
	
	@staticmethod
	def _accept_event(event: QDragEnterEvent | QDragMoveEvent) -> None:
		if event.mimeData().hasUrls and len(event.mimeData().urls()) == 1:
			event.accept()
		else:
			event.ignore()
	
	def dragEnterEvent(self, event: QDragEnterEvent, /) -> None:
		self._accept_event(event)
	
	def dragMoveEvent(self, event: QDragMoveEvent, /) -> None:
		self._accept_event(event)
