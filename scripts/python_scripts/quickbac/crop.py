from PySide6.QtGui import QImage, QPainter

from python_scripts.quickbac.alpha import FALLBACK_BACKGROUND_COLOUR, is_alpha
from python_scripts.quickbac.data import (get_current_pc_ratio, get_current_phone_ratio, ImageModifier, Modification,
	Offsets)
from python_scripts.quickbac.ui import LOGGER


def crop_image(image: QImage, location: Modification) -> QImage:
	base_image: QImage = QImage(location.target_width, location.target_height, QImage.Format.Format_RGB32)
	
	if is_alpha(image):
		LOGGER.warn("image has alpha, filling background first")
		base_image.fill(FALLBACK_BACKGROUND_COLOUR)
	
	painter: QPainter = QPainter(base_image)
	painter.drawImage(location.x_offset, location.y_offset, image)
	painter.end()
	
	return base_image


class HorizontalCropper(ImageModifier):
	def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
		pc_aspect_ratio: float = get_current_pc_ratio()
		
		if current_image.width() / current_image.height() > pc_aspect_ratio:
			height: int = round(current_image.height() * offsets.zoom)
			width: int = round(height * pc_aspect_ratio)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.primary)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.secondary)
		else:
			width: int = round(current_image.width() * offsets.zoom)
			height: int = round(width / pc_aspect_ratio)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.primary)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.secondary)
		
		return crop_image(current_image, Modification(width, height, x_offset, y_offset))


class VerticalCropper(ImageModifier):
	def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
		phone_aspect_ratio: float = get_current_phone_ratio()
		
		if current_image.width() / current_image.height() > phone_aspect_ratio:
			height: int = round(current_image.height() * offsets.zoom)
			width: int = round(height * phone_aspect_ratio)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.primary)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.secondary)
		else:
			width: int = round(current_image.width() * offsets.zoom)
			height: int = round(width / phone_aspect_ratio)
			y_offset: int = round((height - current_image.height()) / 2 * offsets.primary)
			x_offset: int = round((width - current_image.width()) / 2 * offsets.secondary)
		
		return crop_image(current_image, Modification(width, height, x_offset, y_offset))
