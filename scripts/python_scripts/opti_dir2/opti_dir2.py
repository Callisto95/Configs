from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from asyncio import Future
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from enum import auto, Enum
from os import environ, listdir, utime
from os.path import getmtime, getsize, islink
from pathlib import Path
from subprocess import CompletedProcess, run
from time import sleep
from typing import Any, TypeVar

from progress.bar import IncrementalBar

from python_scripts.logger import Logger

LOGGER: Logger = Logger("opti-dir2")
CLEAR_LINE: str = "\r\u001B[0J"
_T = TypeVar("_T")


class NotNoneList[_T](list[_T]):
	def append(self, __object: _T):
		if __object is None:
			return
		super().append(__object)


# STDOUT_TO_DEVNULL: dict[str, int] = { "stdout": DEVNULL, "stderr": DEVNULL }
CAPTURE_OUTPUT: dict[str, int] = { "capture_output": True, "text": True }


def get_env(name: str, fallback: str) -> str:
	value: str = environ.setdefault(name, fallback)
	LOGGER.verbose_log(f"ENV: {name}: {value}")
	return value


OXIPNG_OPTIMIZATION_LEVEL: str = get_env("OXI_OPT_LEVEL", "2")
JXL_DISTANCE: str = get_env("JXL_DISTANCE", "1")
DELETED_IMAGE_FOLDER: Path = Path("deleted-images")


def delete_file(file: Path) -> None:
	if not (DELETED_IMAGE_FOLDER.exists() and DELETED_IMAGE_FOLDER.is_dir()):
		DELETED_IMAGE_FOLDER.mkdir()
	
	file.rename(DELETED_IMAGE_FOLDER / file.name)


def replace_file_type(file: Path, target: str) -> Path:
	return file.with_suffix(f".{target}")


class StepFailed(Exception):
	def __init__(self, step: ImageOptimizer, result: CompletedProcess[Any], image: Path):
		super().__init__(
			f"Step {step.__class__.__name__} on '{image}' has failed with {result.returncode}: {result.stderr}"
		)


class OptimizationMode(Enum):
	SAFE = auto()
	GENERAL = auto()
	ALL = auto()


@dataclass
class OptimizationResult:
	new_image: Path
	old_image: Path | None
	process: CompletedProcess[Any]
	
	def has_error(self) -> bool:
		return self.process.returncode != 0


class ImageOptimizer(ABC):
	@abstractmethod
	def optimize(self, image: Path) -> OptimizationResult:
		pass


class Oxipng(ImageOptimizer):
	def optimize(self, image: Path) -> OptimizationResult:
		process: CompletedProcess = run(
			[
				"oxipng",
				f"--opt={OXIPNG_OPTIMIZATION_LEVEL}",
				"--preserve",
				"--filters",
				"0-9", "--fix",
				"--threads=1",
				image
			],
			**CAPTURE_OUTPUT
		)
		
		return OptimizationResult(image, None, process)


class JpegOptim(ImageOptimizer):
	def optimize(self, image: Path) -> OptimizationResult:
		process: CompletedProcess = run(["jpegoptim", "--preserve", image], **CAPTURE_OUTPUT)
		return OptimizationResult(image, None, process)


class CJXL(ImageOptimizer):
	def optimize(self, image: Path) -> OptimizationResult:
		target: Path = replace_file_type(image, "jxl")
		
		process: CompletedProcess = run(["cjxl", "-d", JXL_DISTANCE, "-e", "7", image, target], **CAPTURE_OUTPUT)
		
		return OptimizationResult(target, image, process)


class Jpeg2Png(ImageOptimizer):
	def optimize(self, image: Path) -> OptimizationResult:
		target: Path = replace_file_type(image, "png")
		
		process: CompletedProcess = run(["jpeg2png", "--threads", "1", image, "--output", target], **CAPTURE_OUTPUT)
		
		return OptimizationResult(target, image, process)


class DWebp(ImageOptimizer):
	def optimize(self, image: Path) -> OptimizationResult:
		target: Path = replace_file_type(image, "png")
		
		process: CompletedProcess = run(
			["dwebp", image, "-o", target],
			**CAPTURE_OUTPUT
		)
		
		return OptimizationResult(target, image, process)


class ImageFixer(ImageOptimizer):
	JPEG = b"\xFF\xD8\xFF"
	PNG = b"\x89\x50\x4E\x47"
	WEBP_START = b"\x52\x49\x46\x46"
	WEBP_END = b"\x57\x45\x42\x50"
	
	# ! this needs to be updated accordingly
	HEADER_LENGTH: int = len(WEBP_START) * 3
	
	@classmethod
	def optimize(cls, image: Path) -> OptimizationResult:
		with open(image, "rb") as file:
			header: bytes = file.read(cls.HEADER_LENGTH)
		
		if header[0:3] == cls.JPEG:
			target = image.with_suffix(".jpg")  # while 'jpeg' should be used, everything uses jpg
		elif header[0:4] == cls.PNG:
			target = image.with_suffix(".png")
		elif header[0:4] == cls.WEBP_START and header[8:12] == cls.WEBP_END:
			target = image.with_suffix(".webp")
		else:
			target = image
		
		if image != target:
			LOGGER.verbose_log(f"{CLEAR_LINE}Found bad file extension: '{image}' -> '{target}'")
			image.rename(target)
		
		# Note: the target *is* the image. The extension was just wrong.
		# Therefore, there is nothing to delete.
		return OptimizationResult(target, None, CompletedProcess([], 0))


class OptimizerFactory:
	_preprocessors: dict[str | None, list[ImageOptimizer]] = { }
	_processors: dict[str | None, list[ImageOptimizer]] = { }
	_postprocessors: dict[str | None, list[ImageOptimizer]] = { }
	_aliases: dict[str, str] = { }
	
	def get_registered_file_types(self) -> set[str]:
		file_types: list[str | None] = (list(self._preprocessors.keys())
										+ list(self._processors.keys())
										+ list(self._postprocessors.keys())
										+ list(self._aliases.keys()))
		
		exclusive_file_types: set[str | None] = set(file_types)
		
		if None in exclusive_file_types:
			exclusive_file_types.remove(None)
		
		return exclusive_file_types
	
	@staticmethod
	def _register(file_type: str, target: dict[str | None, list[ImageOptimizer]], processor: ImageOptimizer) -> None:
		if file_type in target:
			target[file_type].append(processor)
		else:
			target[file_type] = [processor]
	
	def register_preprocessor(self, file_type: str | None, preprocessor: ImageOptimizer) -> None:
		self._register(file_type, self._preprocessors, preprocessor)
	
	def register_processor(self, file_type: str, processor: ImageOptimizer) -> None:
		self._register(file_type, self._processors, processor)
	
	def register_postprocessor(self, file_type: str | None, postprocessor: ImageOptimizer) -> None:
		self._register(file_type, self._postprocessors, postprocessor)
	
	def _get_processors(self, image: Path, source: dict[str | None, list[ImageOptimizer]]) -> list[ImageOptimizer]:
		# processors: list[ImageOptimizer] = source.get(None, [])
		# if None in source:
		# 	processors: list[ImageOptimizer] = source[None]
		# else:
		# 	processors: list[ImageOptimizer] = []
		
		file_type: str = image.suffix[1:]
		file_type: str = self._aliases.get(file_type, file_type)
		
		# if file_type in self._aliases:
		# 	file_type = self._aliases[file_type]
		
		return source.get(None, []) + source.get(file_type, [])
		
		# if file_type in source:
		# 	return processors + source[file_type]
		# else:
		# 	return processors
	
	def get_preprocessors(self, image: Path) -> list[ImageOptimizer]:
		return self._get_processors(image, self._preprocessors)
	
	def get_processors(self, image: Path) -> list[ImageOptimizer]:
		return self._get_processors(image, self._processors)
	
	def get_postprocessors(self, image: Path) -> list[ImageOptimizer]:
		return self._get_processors(image, self._postprocessors)
	
	def register_alias(self, base: str, alias: str) -> None:
		self._aliases[alias] = base


def optimize_image(image: Path, factory: OptimizerFactory) -> Path:
	to_be_deleted_images: NotNoneList[Path] = NotNoneList()
	
	mtime: float = getmtime(image)
	
	try:
		# the steps must be separated
		# a step may change the image, which is not picked up when they're combined
		# e.g. ImageFixer turning a png into a png
		for step in factory.get_preprocessors(image):
			result: OptimizationResult = step.optimize(image)
			
			if result.has_error():
				raise StepFailed(step, result.process, image)
			
			to_be_deleted_images.append(result.old_image)
			image = result.new_image
		
		for step in factory.get_processors(image):
			result: OptimizationResult = step.optimize(image)
			
			if result.has_error():
				raise StepFailed(step, result.process, image)
			
			to_be_deleted_images.append(result.old_image)
			image = result.new_image
		
		for step in factory.get_postprocessors(image):
			result: OptimizationResult = step.optimize(image)
			
			if result.has_error():
				raise StepFailed(step, result.process, image)
			
			to_be_deleted_images.append(result.old_image)
			image = result.new_image
		
		# mtime and atime needs to be set
		utime(image, (mtime, mtime))
		
		for to_delete in to_be_deleted_images:
			delete_file(to_delete)
	except StepFailed as exc:
		LOGGER.error(exc)
	
	return image


def show_progress_bar(tasks: list[Future[Path]]) -> None:
	all_tasks: int = len(tasks)
	
	terminal_width: int = shutil.get_terminal_size()[0]
	
	progress_bar_offset_base: int = len('Progress |')  # left side
	progress_bar_offset_numbers: int = 3 + 2 * len(str(all_tasks))  # '| ' and '/' + numbers
	
	progress_bar_width: int = terminal_width - progress_bar_offset_base - progress_bar_offset_numbers
	
	bar: IncrementalBar = IncrementalBar("Progress", max=all_tasks, width=progress_bar_width, color="cyan")
	
	while True:
		done_tasks: int = len(list(filter(lambda task: task.done(), tasks)))
		
		bar.goto(done_tasks)
		
		if done_tasks == all_tasks:
			bar.color = "green"
			bar.update()
			break
		
		sleep(1)


def optimize_directory(
	directory: Path,
	threads: int,
	factory: OptimizerFactory,
	do_progress_bar: bool = True
) -> tuple[int, int]:
	images: list[Path] = [
		Path(directory / f) for f in listdir(directory)
		if f.endswith(tuple(factory.get_registered_file_types())) and not islink(f)
	]
	
	if len(images) == 0:
		return 0, 0
	
	original_file_size: int = sum(map(getsize, images))
	
	executor: ThreadPoolExecutor = ThreadPoolExecutor(threads)
	
	tasks: list[Future[Path]] = []
	
	for image in images:
		tasks.append(executor.submit(optimize_image, image, factory))
	
	executor.shutdown(wait=not do_progress_bar)
	
	if do_progress_bar:
		show_progress_bar(tasks)
	
	processed_images: list[Path] = [task.result() for task in tasks]
	
	processed_file_size: int = sum(map(getsize, filter(lambda f: f.exists(), processed_images)))
	
	return original_file_size, processed_file_size
