from abc import ABC, abstractmethod

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QImage, QPainter

from python_scripts.quickbac.data import ImageModifier, PC_ASPECT_RATIO, PHONE_ASPECT_RATIO


class HorizontalFiller(ImageModifier):
	def modify(self, current_image: QImage, offset_percent: float) -> QImage:
		height: int = current_image.height()
		width: int = round(height * PC_ASPECT_RATIO)
		x_offset = round((width - current_image.width()) / 2 * offset_percent)
		
		base_image: QImage = QImage(QSize(width, height), QImage.Format.Format_RGB32)
		
		left_colour: QColor = current_image.pixelColor(0, 0)
		right_colour: QColor = current_image.pixelColor(current_image.width() - 1, 0)
		
		painter: QPainter = QPainter(base_image)
		
		painter.fillRect(QRect(0, 0, width, height), right_colour)
		painter.fillRect(QRect(0, 0, round(x_offset + current_image.width() / 2), height), left_colour)
		
		painter.drawImage(x_offset, 0, current_image)
		
		painter.end()
		
		return base_image


class VerticalFiller(ImageModifier):
	def modify(self, current_image: QImage, offset_percent: float) -> QImage:
		width: int = current_image.width()
		height: int = round(width / PHONE_ASPECT_RATIO)
		y_offset = round((height - current_image.height()) / 2 * offset_percent)
		
		base_image: QImage = QImage(QSize(width, height), QImage.Format.Format_RGB32)
		
		upper_colour: QColor = current_image.pixelColor(0, 0)
		lower_colour: QColor = current_image.pixelColor(0, current_image.height() - 1)
		
		painter: QPainter = QPainter(base_image)
		
		painter.fillRect(QRect(0, 0, width, height), lower_colour)
		painter.fillRect(QRect(0, 0, width, round(y_offset + current_image.height() / 2)), upper_colour)
		
		painter.drawImage(0, y_offset, current_image)
		
		painter.end()
		
		return base_image
