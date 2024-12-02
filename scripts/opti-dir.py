#!/usr/bin/python

from __future__ import annotations

import os
import shutil
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from concurrent.futures import Future, ThreadPoolExecutor
from multiprocessing import cpu_count
from os import listdir
from os.path import abspath, basename, expanduser, getsize, join
from shutil import which
from subprocess import CompletedProcess, DEVNULL, run
from time import sleep
from typing import Any, Callable

from colorama import Fore, Style
from progress.bar import Bar, IncrementalBar
from progress.spinner import PixelSpinner, Spinner

MINIMUM_PROGRESS_BAR_WIDTH: int = 30
STDOUT_TO_DEVNULL: dict[str, int] = { "stdout": DEVNULL, "stderr": DEVNULL }


class FileFilter:
	@staticmethod
	def jpeg(path: str) -> bool:
		return path.endswith((".jpg", ".jpeg"))
	
	@staticmethod
	def jxl(path: str) -> bool:
		return path.endswith(".jxl")
	
	@staticmethod
	def png(path: str) -> bool:
		return path.endswith(".png")
	
	@staticmethod
	def any(path: str) -> bool:
		# .jxl files are considered optimized
		return path.endswith((".jpg", ".jpeg", ".png"))


class Executable(ABC):
	def __init__(self, binary_name: str, image_filter: Callable[[str], bool]):
		self.binary: str = binary_name
		self.available: bool = self.executable_is_available(binary_name)
		self.filter: Callable[[str], bool] = image_filter
	
	@abstractmethod
	def _execute(self, image: str) -> tuple[CompletedProcess, str]:
		pass
	
	@staticmethod
	def executable_is_available(command: str) -> bool:
		path: str | None = which(command)
		if path is None:
			print(f"{command} not installed")
			return False
		return True
	
	def run(self, image: str, previous_result: CompletedProcess | None = None) -> tuple[CompletedProcess | None, str]:
		"""Run the associated program on the given image
		:param image: The image to optimize (either visual clarity or size)
		:param previous_result: Convenience: If either the filter or the program is not available, return this.
		:return: The process result or None if the file doesn't match or the program isn't available, and the new
		image path.
		"""
		if self.available and self.filter(image):
			result, image = self._execute(image)
			if result is None:
				result = previous_result
			return result, image
		
		return previous_result, image


class OxiPng(Executable):
	def __init__(self):
		super().__init__("oxipng", FileFilter.png)
	
	def _execute(self, image: str) -> tuple[CompletedProcess, str]:
		return (
			run(
				["oxipng", "--opt=2", "--preserve", "--filters", "0-9", "--fix", "--threads=1", image],
				**STDOUT_TO_DEVNULL
			),
			image
		)


class JpegOptim(Executable):
	def __init__(self):
		super().__init__("jpegoptim", FileFilter.jpeg)
	
	def _execute(self, image: str) -> tuple[CompletedProcess, str]:
		return run(["jpegoptim", "--preserve", image], **STDOUT_TO_DEVNULL), image


class CJXL(Executable):
	def __init__(self):
		super().__init__("cjxl", FileFilter.any)
	
	def _execute(self, image: str) -> tuple[CompletedProcess, str]:
		target: str = replace_file_type(image, "jxl")
		return (
			run(["cjxl", "-q", "100", "-e", "7", image, target], **STDOUT_TO_DEVNULL),
			target
		)


class Jpeg2Png(Executable):
	def __init__(self):
		super().__init__("jpeg2png", FileFilter.jpeg)
	
	def _execute(self, image: str) -> tuple[CompletedProcess, str]:
		target: str = replace_file_type(image, "png")
		return run(["jpeg2png", image, "-o", target], **STDOUT_TO_DEVNULL), target


class Executables:
	OXIPNG: Executable = OxiPng()
	JPEGOPTIM: Executable = JpegOptim()
	CJXL: Executable = CJXL()
	JPEG2PNG: Executable = Jpeg2Png()


class Feature:
	def __init__(self, name: str, display_name: str, requirement: Executable | None = None):
		self.name: str = name
		self.display_name: str = display_name if display_name is not None else name
		self.enabled: bool = False
		self.requirement: Executable = requirement
	
	def enable(self) -> None:
		if self.requirement is not None and not self.requirement.available:
			print(f"Feature {self.display_name} requires {self.requirement.binary}, but it is not available")
			exit(1)
		
		self.enabled = True
	
	def __eq__(self, other):
		if isinstance(other, Feature):
			return self.name == other.name
		if isinstance(other, str):
			return self.name == other
		return False
	
	def __str__(self) -> str:
		return f"{self.name} ({self.display_name})"


class Features:
	JXL_ENCODE: Feature = Feature("cjxl", "encode to JXL", Executables.CJXL)
	DELETE_ORIGINAL: Feature = Feature("rm", "remove original")
	JPEG_BETTER_DECODE: Feature = Feature("j2p", "better jpeg decoding", Executables.JPEG2PNG)
	FIX_IMAGES: Feature = Feature("fix", "try to fix bad image extensions")
	META_ENABLE_ALL: Feature = Feature("all", "meta: enable all features")
	
	@classmethod
	def all(cls) -> list[Feature]:
		return [cls.JXL_ENCODE, cls.DELETE_ORIGINAL, cls.JPEG_BETTER_DECODE, cls.FIX_IMAGES, cls.META_ENABLE_ALL]
	
	@classmethod
	def get(cls, name: str) -> Feature | None:
		for f in cls.all():
			if f.name == name:
				return f
		return None
	
	@classmethod
	def enable_all(cls) -> None:
		for feature in cls.all():
			feature.enable()
	
	@classmethod
	def get_all_filtered(cls, enabled: bool) -> list[Feature]:
		return [f for f in cls.all() if f.enabled == enabled]


def filter_tasks(maybe: list[Future[Any]]) -> int:
	return len([t for t in maybe if t.done()])


def get_size_of_files(images: list[str]) -> int:
	return sum(getsize(image) for image in images)


def pretty_print_bytes(byte_amount: int) -> str:
	if byte_amount < 0:
		return f"-{pretty_print_bytes(-byte_amount)}"
	
	units: list[str] = ["B", "KiB", "MiB", "GiB", "TiB"]
	
	unit_index: int = 0
	
	while byte_amount > 1024:
		byte_amount = byte_amount / 1024
		unit_index += 1
	
	return f"{byte_amount:.1f} {units[unit_index]}"


def replace_file_type(file: str, target: str) -> str:
	return f"{file[:file.rfind(".")]}.{target}"


class FileHeaders:
	# https://en.wikipedia.org/wiki/List_of_file_signatures
	JPEG: bytes = b"\xFF\xD8\xFF"
	PNG: bytes = b"\x89\x50\x4E\x47"
	
	
MAX_LENGTH: int = max(len(FileHeaders.JPEG), len(FileHeaders.PNG))


def fix_image(image: str) -> str:
	original: str = image
	
	with open(image, "rb") as file:
		header: bytes = file.read(MAX_LENGTH)
	
	if header.startswith(FileHeaders.JPEG) and FileFilter.png(image):
		image = replace_file_type(image, "jpg")
	elif header.startswith(FileHeaders.PNG) and FileFilter.jpeg(image):
		image = replace_file_type(image, "png")
	
	if original != image:
		print(f"\r\u001B[0JFound bad file extension: {original} -> {image}")
		shutil.move(original, image)
	
	return image


def run_wrapper(image: str) -> tuple[CompletedProcess, str | None]:
	original: str = image
	result: CompletedProcess | None = None
	
	if Features.FIX_IMAGES.enabled:
		image = fix_image(image)
		# this version *is* the real image
		original = image
	
	if Features.JPEG_BETTER_DECODE.enabled:
		result, image = Executables.JPEG2PNG.run(image)
	
	result, image = Executables.OXIPNG.run(image, result)
	result, image = Executables.JPEGOPTIM.run(image, result)
	
	if Features.JXL_ENCODE.enabled:
		tmp: str = image
		result, image = Executables.CJXL.run(image, result)
		
		# remove intermediary png from jpeg2png
		if Features.JPEG_BETTER_DECODE.enabled and FileFilter.jpeg(original):
			os.remove(tmp)
	
	if Features.DELETE_ORIGINAL.enabled and original != image:
		os.remove(original)
	
	return result, image


def do_optimize(files: list[str], filter: Callable[[str], bool]) -> tuple[list[str], list[Future], int]:
	images: list[str] = [file for file in files if filter(file)]
	image_size: int = get_size_of_files(images)
	
	tasks: list[Future] = []
	
	for image in images:
		task: Future = EXECUTOR.submit(run_wrapper, image)
		tasks.append(task)
	
	return images, tasks, image_size


def start_optimizations() -> tuple[list[Future], int]:
	print(f"using {args.threads} threads for {basename(args.directory)}")
	files: list[str] = listdir(args.directory)
	files = [join(args.directory, file) for file in files if FileFilter.any(file)]
	
	tasks: list[Future] = []
	
	image_size: int = 0
	
	pngs: list[str] = []
	if Executables.OXIPNG.available:
		pngs, new_tasks, new_image_size = do_optimize(files, FileFilter.png)
		
		tasks += new_tasks
		image_size += new_image_size
		
		if len(pngs) > 0:
			print(f"optimizing {len(pngs)} PNG's...")
	else:
		print("skipping png optimization")
	
	jpgs: list[str] = []
	if Executables.JPEGOPTIM.available or Executables.JPEG2PNG.available:
		jpgs, new_tasks, new_image_size = do_optimize(files, FileFilter.jpeg)
		
		tasks += new_tasks
		image_size += new_image_size
		
		if len(jpgs) > 0:
			print(f"optimizing {len(jpgs)} JPG's...")
	else:
		print("skipping jpeg optimization")
	
	if len(pngs) == 0 and len(jpgs) == 0:
		print("nothing to optimize")
		exit(0)
	
	return tasks, image_size


def do_progress_bar(tasks: list[Future[tuple[CompletedProcess, str | None]]]) -> None:
	all_tasks: int = len(tasks)
	
	terminal_width: int = shutil.get_terminal_size()[0]
	
	progress_bar_offset_base: int = 10  # 'Progress |' - left side
	progress_bar_offset_numbers: int = 3 + 2 * len(str(all_tasks))  # '| ' and '/' + numbers
	
	progress_bar_width: int = terminal_width - progress_bar_offset_base - progress_bar_offset_numbers
	is_bar: bool = progress_bar_width >= MINIMUM_PROGRESS_BAR_WIDTH
	
	if is_bar:
		bar: Bar = IncrementalBar(
			"Progress", max=all_tasks, width=progress_bar_width, color='cyan'
		)
	else:
		bar: Spinner = PixelSpinner("Processing ")
	
	done: int = 0
	counter: int = 0
	while done != all_tasks:
		if is_bar:
			done = filter_tasks(tasks)
			bar.goto(done)
			
			if done == all_tasks:
				bar.color = "green"
				bar.update()
				break
			
			sleep(1)
		else:
			counter += 1
			if counter == 10:
				done = filter_tasks(tasks)
				counter = 0
			bar.next()
			sleep(0.1)
	
	bar.finish()


def main() -> None:
	tasks, original_size = start_optimizations()
	
	do_progress_bar(tasks)
	
	failed_tasks: list[Future] = [task for task in tasks if task.result()[0].returncode != 0]
	
	if len(failed_tasks) > 0:
		print(f"some tasks ({len(failed_tasks)}) have failed!")
		
		print("failed images:")
		for task in failed_tasks:
			print(f"\t{task.result()[0].args[-1]}")
	
	current_size: int = get_size_of_files([task.result()[1] for task in tasks])
	
	size_difference: float = 100 - ((current_size / original_size) * 100)
	is_less: bool = size_difference < 0
	size_difference: float = abs(size_difference)
	
	print(
		pretty_print_bytes(original_size),
		"->",
		pretty_print_bytes(current_size),
		"(",
		f"{Fore.RED if is_less else Fore.CYAN}{pretty_print_bytes(current_size - original_size)}",
		"|",
		f"{"+" if is_less else "-"}{size_difference:.2f}%{Style.RESET_ALL}",
		")"
	)


parser = ArgumentParser()
parser.add_argument(
	"directory", type=str, default=".", action="store", nargs="?", help="where the images to be optimized are located"
)
parser.add_argument(
	"-t",
	"--threads",
	dest="threads",
	type=int,
	default=cpu_count() - 2,
	action="store",
	help="the amount of used threads. Defaults to [all - 2]"
)
parser.add_argument(
	"-f",
	"--features",
	dest="features",
	type=str,
	default="",
	action="store",
	help=f"comma separated list of enabled features. Available features: "
		 f"{",".join([str(f) for f in Features.all()])}"
)
args = parser.parse_args()

if args.threads < 1:
	print("negative thread amount; using 1")
	args.threads = 1

args.directory = abspath(expanduser(args.directory))

for feature in args.features.split(","):
	f: Feature | None = Features.get(feature)
	if f is None:
		if feature != "":
			print(f"Given feature '{feature}' does not exist, skipping")
	else:
		f.enable()

if Features.META_ENABLE_ALL.enabled:
	Features.enable_all()

if Features.JPEG_BETTER_DECODE.enabled:
	print(f"{Fore.YELLOW}jpeg2png enabled. This will most likely increase file size!{Style.RESET_ALL}")

if len((enabled_features := Features.get_all_filtered(True))) > 0:
	print(f"enabled features: {", ".join([str(f) for f in enabled_features])}")

EXECUTOR: ThreadPoolExecutor = ThreadPoolExecutor(args.threads)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\rShutting down, this may take a while...")
		print("To cancel the optimization, CTRL+C again.")
		
		EXECUTOR.shutdown(cancel_futures=True)
