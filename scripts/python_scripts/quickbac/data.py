from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from PySide6.QtGui import QImage

PC_ASPECT_RATIO: float = 3840 / 2160
PHONE_ASPECT_RATIO: float = 1080 / 2400

ZOOM_NORMAL: int = 500


@dataclass
class Modification:
	target_width: int
	target_height: int
	x_offset: int
	y_offset: int


class ImageModifier(ABC):
	@abstractmethod
	def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
		pass


class ImageProcessorFactory:
	def __init__(self):
		self.modfiers: dict[tuple[bool, bool], ImageModifier] = { }
	
	def register(self, horizontal: bool, crop: bool, modifier: ImageModifier) -> None:
		self.modfiers[(horizontal, crop)] = modifier
	
	def get(self, horizontal: bool, crop: bool) -> ImageModifier:
		return self.modfiers[(horizontal, crop)]


@dataclass
class Offsets:
	primary: float
	secondary: float
	zoom: float
