from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from PySide6.QtGui import QImage

PC_ASPECT_RATIOS: list[tuple[int, int]] = [
	(3840, 2160)
]
PHONE_ASPECT_RATIOS: list[tuple[int, int]] = [
	(1080, 2400),
	(1116, 2484)
]
# UI initializes this with 0
PC_ASPECT_RATIO_INDEX: int = -1
PHONE_ASPECT_RATIO_INDEX: int = -1


def get_current_pc_ratio() -> float:
	ratio: tuple[int, int] = PC_ASPECT_RATIOS[PC_ASPECT_RATIO_INDEX]
	return ratio[0] / ratio[1]


def get_current_phone_ratio() -> float:
	ratio: tuple[int, int] = PHONE_ASPECT_RATIOS[PHONE_ASPECT_RATIO_INDEX]
	return ratio[0] / ratio[1]


def next_pc_ratio() -> tuple[int, int]:
	global PC_ASPECT_RATIO_INDEX
	PC_ASPECT_RATIO_INDEX += 1
	
	if PC_ASPECT_RATIO_INDEX == len(PC_ASPECT_RATIOS):
		PC_ASPECT_RATIO_INDEX = 0
	
	return PC_ASPECT_RATIOS[PC_ASPECT_RATIO_INDEX]


def next_phone_ratio() -> tuple[int, int]:
	global PHONE_ASPECT_RATIO_INDEX
	PHONE_ASPECT_RATIO_INDEX += 1
	
	if PHONE_ASPECT_RATIO_INDEX == len(PHONE_ASPECT_RATIOS):
		PHONE_ASPECT_RATIO_INDEX = 0
	
	return PHONE_ASPECT_RATIOS[PHONE_ASPECT_RATIO_INDEX]


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
