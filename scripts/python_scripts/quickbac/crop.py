from abc import ABC, abstractmethod

from PySide6.QtGui import QImage, QPainter

from python_scripts.quickbac.data import ImageModifier, Modification, PC_ASPECT_RATIO, PHONE_ASPECT_RATIO


def crop_image(image: QImage, location: Modification) -> QImage:
	base_image: QImage = QImage(location.target_width, location.target_height, QImage.Format.Format_RGB32)
	
	painter: QPainter = QPainter(base_image)
	painter.drawImage(location.x_offset, location.y_offset, image)
	painter.end()
	
	return base_image


class HorizontalCropper(ImageModifier):
	def modify(self, current_image: QImage, offset_percentage: float) -> QImage:
		if current_image.width() / current_image.height() > PC_ASPECT_RATIO:
			target_height: int = current_image.height()
			target_width: int = round(target_height * PC_ASPECT_RATIO)
			x_offset: int = round((target_width - current_image.width()) / 2 * offset_percentage)
			y_offset: int = 0
		else:
			target_width: int = current_image.width()
			target_height: int = round(target_width / PC_ASPECT_RATIO)
			y_offset: int = round((target_height - current_image.height()) / 2 * offset_percentage)
			x_offset: int = 0
		
		return crop_image(current_image, Modification(target_width, target_height, x_offset, y_offset))


class VerticalCropper(ImageModifier):
	def modify(self, current_image: QImage, offset_percentage: float) -> QImage:
		if current_image.width() / current_image.height() > PHONE_ASPECT_RATIO:
			target_height: int = current_image.height()
			target_width: int = round(target_height * PHONE_ASPECT_RATIO)
			x_offset: int = round((target_width - current_image.width()) / 2 * offset_percentage)
			y_offset: int = 0
		else:
			target_width: int = current_image.width()
			target_height: int = round(target_width / PHONE_ASPECT_RATIO)
			y_offset: int = round((target_height - current_image.height()) / 2 * offset_percentage)
			x_offset: int = 0
		
		return crop_image(current_image, Modification(target_width, target_height, x_offset, y_offset))
