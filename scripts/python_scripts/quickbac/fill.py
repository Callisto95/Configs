from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QImage, QPainter

from python_scripts.quickbac.alpha import get_colour
from python_scripts.quickbac.data import ImageModifier, Offsets, PC_ASPECT_RATIO, PHONE_ASPECT_RATIO


class HorizontalFiller(ImageModifier):
	def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
		if current_image.width() / current_image.height() > PC_ASPECT_RATIO:
			width: int = round(current_image.width() * offsets.zoom)
			height: int = round(width / PC_ASPECT_RATIO)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.primary)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.secondary)
		else:
			height: int = round(current_image.height() * offsets.zoom)
			width: int = round(height * PC_ASPECT_RATIO)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.primary)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.secondary)
		
		left_colour: QColor = get_colour(current_image, 0, 0)
		right_colour: QColor = get_colour(current_image, current_image.width() - 1, 0)
		
		base_image: QImage = QImage(QSize(width, height), QImage.Format.Format_RGB32)
		
		painter: QPainter = QPainter(base_image)
		
		painter.fillRect(QRect(0, 0, width, height), right_colour)
		painter.fillRect(QRect(0, 0, round(x_offset + current_image.width() / 2), height), left_colour)
		
		painter.drawImage(x_offset, y_offset, current_image)
		
		painter.end()
		
		return base_image


class VerticalFiller(ImageModifier):
	def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
		if current_image.width() / current_image.height() > PHONE_ASPECT_RATIO:
			width: int = round(current_image.width() * offsets.zoom)
			height: int = round(width / PHONE_ASPECT_RATIO)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.primary)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.secondary)
		else:
			height: int = round(current_image.height() * offsets.zoom)
			width: int = round(height * PHONE_ASPECT_RATIO)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.primary)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.secondary)
		
		upper_colour: QColor = get_colour(current_image, 0, 0)
		lower_colour: QColor = get_colour(current_image, 0, current_image.height() - 1)
		
		base_image: QImage = QImage(QSize(width, height), QImage.Format.Format_RGB32)
		
		painter: QPainter = QPainter(base_image)
		
		painter.fillRect(QRect(0, 0, width, height), lower_colour)
		painter.fillRect(QRect(0, 0, width, round(y_offset + current_image.height() / 2)), upper_colour)
		
		painter.drawImage(x_offset, y_offset, current_image)
		
		painter.end()
		
		return base_image
