#!/usr/bin/python

import sys
from multiprocessing import Process
from pathlib import Path
from threading import Lock
from typing import TypeAlias

from PySide6.QtCore import (QCoreApplication, QMetaObject, QPoint, QSize, Qt)
from PySide6.QtGui import QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel,
	QLayout, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
	QVBoxLayout, QWidget)

from logger import Logger

LOGGER: Logger = Logger("QuickBacUI")
# LOGGER.verbose_enabled = True

PC_ASPECT_RATIO: float = 3840 / 2160
PHONE_ASPECT_RATIO: float = 1080 / 2400


CropResult: TypeAlias = tuple[tuple[int, int], tuple[int, int]]


class QuickBackUI(QWidget):
	def __init__(self, /):
		super().__init__()
		
		# TODO: does this help with stutters?
		self.update_lock: Lock = Lock()
		
		self.current_image_path: Path | None = None
		self.current_image: QImage | None = None
		self.finished_image: QImage | None = None
		
		if not self.objectName():
			self.setObjectName(u"mainWidget")
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
		self.offset.setToolTip("offset")
		self.offset.setMinimum(0)
		self.offset.setMaximum(200)
		self.offset.setValue(100)
		self.offset.setOrientation(Qt.Orientation.Horizontal)
		
		self.verticalLayout.addWidget(self.offset)
		
		self.controls = QHBoxLayout()
		self.controls.setObjectName(u"controls")
		self.controls.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
		self.groupBox = QGroupBox(self)
		self.groupBox.setObjectName(u"groupBox")
		group_box_size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
		group_box_size_policy.setHorizontalStretch(2)
		self.groupBox.setSizePolicy(group_box_size_policy)
		self.verticalLayout_2 = QVBoxLayout(self.groupBox)
		self.verticalLayout_2.setObjectName(u"verticalLayout_2")
		self.horizontal = QRadioButton(self.groupBox)
		self.horizontal.setObjectName(u"horizontal")
		self.horizontal.setChecked(True)
		
		self.verticalLayout_2.addWidget(self.horizontal)
		
		self.vertical = QRadioButton(self.groupBox)
		self.vertical.setObjectName(u"vertical")
		
		self.verticalLayout_2.addWidget(self.vertical)
		
		self.controls.addWidget(self.groupBox)
		
		self.groupBox_2 = QGroupBox(self)
		self.groupBox_2.setObjectName(u"groupBox_2")
		group_box_2_size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
		group_box_2_size_policy.setHorizontalStretch(2)
		self.groupBox_2.setSizePolicy(group_box_2_size_policy)
		self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
		self.verticalLayout_3.setObjectName(u"verticalLayout_3")
		self.crop = QRadioButton(self.groupBox_2)
		self.crop.setObjectName(u"crop")
		self.crop.setChecked(True)
		
		self.verticalLayout_3.addWidget(self.crop)
		
		self.fill = QRadioButton(self.groupBox_2)
		self.fill.setObjectName(u"fill")
		
		self.verticalLayout_3.addWidget(self.fill)
		
		self.controls.addWidget(self.groupBox_2)
		
		self.verticalLayout.addLayout(self.controls)
		
		self.buttons = QHBoxLayout()
		self.buttons.setObjectName(u"buttons")
		self.buttons.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
		self.center = QPushButton(self)
		self.center.setObjectName(u"center")
		
		self.buttons.addWidget(self.center)
		
		self.export_2 = QPushButton(self)
		self.export_2.setObjectName(u"export_2")
		
		self.buttons.addWidget(self.export_2)
		
		self.verticalLayout.addLayout(self.buttons)
		
		self._retranslate_ui()
		
		QMetaObject.connectSlotsByName(self)
		
		self.vertical.toggled.connect(self.resize_current_image)
		self.horizontal.toggled.connect(self.resize_current_image)
		self.fill.toggled.connect(self.resize_current_image)
		self.crop.toggled.connect(self.resize_current_image)
		self.offset.valueChanged.connect(self.resize_current_image)
		
		self.center.clicked.connect(self.reset_offset)
		self.export_2.clicked.connect(self.export)
		
		self.reset()
	
	def _retranslate_ui(self):
		self.setWindowTitle(QCoreApplication.translate("mainWidget", u"QuickBac", None))
		self.image.setText(QCoreApplication.translate("mainWidget", u"TEXT", None))
		self.groupBox.setTitle(QCoreApplication.translate("mainWidget", u"Wanted", None))
		self.horizontal.setText(QCoreApplication.translate("mainWidget", u"Horizontal", None))
		self.vertical.setText(QCoreApplication.translate("mainWidget", u"Vertical", None))
		self.groupBox_2.setTitle(QCoreApplication.translate("mainWidget", u"Mode", None))
		self.crop.setText(QCoreApplication.translate("mainWidget", u"Crop", None))
		self.fill.setText(QCoreApplication.translate("mainWidget", u"Fill", None))
		self.center.setText(QCoreApplication.translate("mainWidget", u"Center", None))
		self.export_2.setText(QCoreApplication.translate("mainWidget", u"Export", None))
	
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
	
	def horizontal_crop(self, offset_percentage: float) -> CropResult:
		if self.current_image.width() / self.current_image.height() > PC_ASPECT_RATIO:
			target_height: int = self.current_image.height()
			target_width: int = round(target_height * PC_ASPECT_RATIO)
			x_offset: int = round((target_width - self.current_image.width()) / 2 * offset_percentage)
			y_offset: int = 0
		else:
			target_width: int = self.current_image.width()
			target_height: int = round(target_width / PC_ASPECT_RATIO)
			y_offset: int = round((target_height - self.current_image.height()) / 2 * offset_percentage)
			x_offset: int = 0
		
		return (target_width, target_height), (x_offset, y_offset)
	
	def vertical_crop(self, offset_percentage: float) -> CropResult:
		if self.current_image.width() / self.current_image.height() > PHONE_ASPECT_RATIO:
			target_height: int = self.current_image.height()
			target_width: int = round(target_height * PHONE_ASPECT_RATIO)
			x_offset: int = round((target_width - self.current_image.width()) / 2 * offset_percentage)
			y_offset: int = 0
		else:
			target_width: int = self.current_image.width()
			target_height: int = round(target_width / PHONE_ASPECT_RATIO)
			y_offset: int = round((target_height - self.current_image.height()) / 2 * offset_percentage)
			x_offset: int = 0
		
		return (target_width, target_height), (x_offset, y_offset)
	
	def resize_current_image(self) -> None:
		if not self.current_image or not self.update_lock.acquire(blocking=False):
			return
		
		offset_percentage: float = self.offset.value() / 100
		
		x_offset: int = 0
		y_offset: int = 0
		colour: QColor = QColor(255, 0, 0)
		
		base_image: QImage = QImage(QSize(1, 1), QImage.Format.Format_RGB32)
		
		if self.horizontal.isChecked():
			if self.crop.isChecked():
				(target_width, target_height), (x_offset, y_offset) = self.horizontal_crop(offset_percentage)
			else:
				colour = self.current_image.pixelColor(QPoint(0, 0))
				target_height: int = self.current_image.height()
				target_width: int = round(target_height * PC_ASPECT_RATIO)
				x_offset = round((target_width - self.current_image.width()) / 2 * offset_percentage)
		else:
			if self.crop.isChecked():
				(target_width, target_height), (x_offset, y_offset) = self.vertical_crop(offset_percentage)
			else:
				colour = self.current_image.pixelColor(QPoint(0, 0))
				target_width: int = self.current_image.width()
				target_height: int = round(target_width / PHONE_ASPECT_RATIO)
				y_offset = round((target_height - self.current_image.height()) / 2 * offset_percentage)
		
		base_image = base_image.scaled(QSize(target_width, target_height))
		base_image.fill(colour)
		
		painter: QPainter = QPainter(base_image)
		painter.drawImage(QPoint(x_offset, y_offset), self.current_image)
		painter.end()
		
		LOGGER.verbose_log("scaling to", target_width, target_height, x_offset, y_offset)
		
		self.finished_image = base_image
		
		scaled_image: QImage = base_image.scaled(
			self.image.size(),
			aspectMode=Qt.AspectRatioMode.KeepAspectRatio
		)
		
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
	

if __name__ == '__main__':
	app: QApplication = QApplication(sys.argv)
	ui: QuickBackUI = QuickBackUI()
	ui.show()
	sys.exit(app.exec())
	
