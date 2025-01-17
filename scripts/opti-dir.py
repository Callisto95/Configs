#!/usr/bin/python

from __future__ import annotations

import shutil
from argparse import ArgumentParser, Namespace
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from multiprocessing import cpu_count
from os import listdir, utime
from os.path import basename, getmtime, getsize
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, DEVNULL, run
from time import sleep
from typing import Callable

from colorama import Fore, Style
from progress.bar import Bar, IncrementalBar
from progress.spinner import PixelSpinner, Spinner

EXECUTOR: ThreadPoolExecutor | None = None
MINIMUM_PROGRESS_BAR_WIDTH: int = 30
STDOUT_TO_DEVNULL: dict[str, int] = { "stdout": DEVNULL, "stderr": DEVNULL }
DELETED_IMAGE_FOLDER: Path = Path("./deleted-images/").expanduser().resolve().absolute()


class FileFilter:
	@staticmethod
	def jpeg(path: Path) -> bool:
		return path.suffix in (".jpg", ".jpeg")
	
	# jxl and png: using '==' for safety
	# -> prevent weird 'character is in string' testing behaviour
	@staticmethod
	def jxl(path: Path) -> bool:
		return path.suffix == ".jxl"
	
	@staticmethod
	def png(path: Path) -> bool:
		return path.suffix == ".png"
	
	@staticmethod
	def any(path: Path) -> bool:
		# .jxl files are considered optimized
		return path.suffix in (".jpg", ".jpeg", ".png")


def exec_oxipng(image: Path) -> tuple[CompletedProcess, Path]:
	return run(
		["oxipng", "--opt=2", "--preserve", "--filters", "0-9", "--fix", "--threads=1", image],
		**STDOUT_TO_DEVNULL
	), image


def exec_jpegoptim(image: Path) -> tuple[CompletedProcess, Path]:
	return run(["jpegoptim", "--preserve", image], **STDOUT_TO_DEVNULL), image


def exec_cjxl(image: Path) -> tuple[CompletedProcess, Path]:
	target: Path = replace_file_type(image, "jxl")
	return (
		run(["cjxl", "-q", "100", "-e", "7", image, target], **STDOUT_TO_DEVNULL),
		target
	)


def exec_jpeg2png(image: Path) -> tuple[CompletedProcess, Path]:
	target: Path = replace_file_type(image, "png")
	
	if InternalFeatures.USE_16_BIT.enabled:
		return run(
			["jpeg2png", "--threads", "1", "--16-bits-png", "--iterations", "150", image, "--output", target],
			**STDOUT_TO_DEVNULL
		), target
	else:
		return run(["jpeg2png", "--threads", "1", image, "--output", target], **STDOUT_TO_DEVNULL), target


@dataclass
class Executable:
	binary: str
	filter: Callable[[Path], bool]
	execute: Callable[[Path], tuple[CompletedProcess, Path]]
	available: bool = field(init=False)
	
	def __post_init__(self):
		self.available = self.executable_is_available(self.binary)
	
	@staticmethod
	def executable_is_available(command: str) -> bool:
		path: str | None = which(command)
		if path is None:
			print(f"{command} not installed")
			return False
		return True
	
	def run(self, image: Path, previous_result: CompletedProcess | None = None) -> tuple[CompletedProcess | None,
	Path]:
		"""Run the associated program on the given image
		:param image: The image to optimize (either visual clarity or size)
		:param previous_result: Convenience: If either the filter or the program is not available, return this.
		:return: The process result or None if the file doesn't match or the program isn't available, and the new
		image path.
		"""
		if self.available and self.filter(image):
			result, image = self.execute(image)
			if result is None:
				result = previous_result
			return result, image
		
		return previous_result, image


class Executables(Executable, Enum):
	OXIPNG = "oxipng", FileFilter.png, exec_oxipng
	JPEGOPTIM = "jpegoptim", FileFilter.jpeg, exec_jpegoptim
	CJXL = "cjxl", FileFilter.any, exec_cjxl
	JPEG2PNG = "jpeg2png", FileFilter.jpeg, exec_jpeg2png


@dataclass
class Feature:
	name_: str  # name is used by Enum
	display_name: str
	requirement: Executable | None = None
	enabled: bool = field(init=False, default=False)
	
	def enable(self) -> None:
		if self.requirement is not None and not self.requirement.available:
			print(f"Feature {self.display_name} requires {self.requirement.binary}, but it is not available")
			exit(1)
		
		self.enabled = True
	
	def __eq__(self, other):
		if isinstance(other, Feature):
			return self.name_ == other.name_
		if isinstance(other, str):
			return self.name_ == other
		return False
	
	def __str__(self) -> str:
		return f"{self.name_} ({self.display_name})"


class Features(Feature, Enum):
	JXL_ENCODE = "cjxl", "encode to JXL", Executables.CJXL
	DELETE_ORIGINAL = "rm", "remove original"
	JPEG_BETTER_DECODE = "j2p", "better jpeg decoding", Executables.JPEG2PNG
	FIX_IMAGES = "fix", "try to fix bad image extensions"
	
	@classmethod
	def get(cls, name: str) -> Feature | None:
		for f in cls:
			if f.name_ == name:
				return f
		return None
	
	@classmethod
	def enable_all(cls) -> None:
		for f in cls:
			f.enable()
	
	@classmethod
	def filter(cls, enabled: bool) -> list[Feature]:
		return list(filter(lambda f: f.enabled == enabled, cls))
	
	# fuck python
	def __str__(self):
		return str(self.value)


class InternalFeatures(Feature, Enum):
	USE_16_BIT = "16-bit", "if 16-bit colour depth should be used"
	
	def __str__(self) -> str:
		return str(self.value)


@dataclass
class FeatureSet:
	name_: str
	description: str
	features: list[Feature]
	
	def enable_set(self) -> None:
		for feature in self.features:
			feature.enable()
	
	def __str__(self) -> str:
		return f"{self.name_} ({self.description}: {",".join([f.name_ for f in self.features])})"


class FeatureSets(FeatureSet, Enum):
	ALL = "all", "enable all features", [f for f in Features]
	GENERAL_PICTURE = "general", "general image improvements", [
		Features.DELETE_ORIGINAL, Features.JPEG_BETTER_DECODE, Features.FIX_IMAGES
	]  # delete original is fine, because it only deletes the image if jpeg better decode ran
	safe = "safe", "general, non-destructive image improvements", [Features.FIX_IMAGES]
	
	def __str__(self) -> str:
		return str(self.value)
	
	@classmethod
	def get(cls, name: str) -> FeatureSet | None:
		for feature_set in cls:
			if feature_set.name_ == name:
				return feature_set
		
		return None


def filter_tasks(tasks: list[Future]) -> int:
	return len(list(filter(lambda task: task.done(), tasks)))


def get_size_of_files(images: list[Path]) -> int:
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


def replace_file_type(file: Path, target: str) -> Path:
	return file.with_suffix(f".{target}")


class FileHeaders(bytes, Enum):
	# https://en.wikipedia.org/wiki/List_of_file_signatures
	JPEG = b"\xFF\xD8\xFF"
	PNG = b"\x89\x50\x4E\x47"


# second entry is sometimes skipped? explicit naming
MAX_HEADER_LENGTH: int = max(len(FileHeaders.JPEG), len(FileHeaders.PNG))


def fix_image(image: Path) -> Path:
	original: Path = image
	
	with image.open("rb") as file:
		header: bytes = file.read(MAX_HEADER_LENGTH)
	
	if header.startswith(FileHeaders.JPEG) and FileFilter.png(image):
		image = replace_file_type(image, "jpg")
	elif header.startswith(FileHeaders.PNG) and FileFilter.jpeg(image):
		image = replace_file_type(image, "png")
	
	if original != image:
		print(f"\r\u001B[0JFound bad file extension: {original} -> {image}")
		original.rename(image)
	# shutil.move(original, image)
	
	return image


def delete_image(image: Path) -> None:
	image.replace(DELETED_IMAGE_FOLDER / image.name)


def run_wrapper(image: Path) -> tuple[CompletedProcess, Path]:
	original: Path = Path(image)
	result: CompletedProcess | None = None
	
	if Features.FIX_IMAGES.enabled:
		image = fix_image(image)
		# this version *is* the real image
		original = image
	
	if Features.JPEG_BETTER_DECODE.enabled:
		# preserve modification time
		modification_time: float = getmtime(image)
		
		result, image = Executables.JPEG2PNG.run(image)
		
		# (access time, modification time) - just set both to modification_time
		utime(image, (modification_time, modification_time))
	
	result, image = Executables.OXIPNG.run(image, result)
	result, image = Executables.JPEGOPTIM.run(image, result)
	
	if Features.JXL_ENCODE.enabled:
		tmp: Path = image
		result, image = Executables.CJXL.run(image, result)
		
		# remove intermediary png from jpeg2png
		if Features.JPEG_BETTER_DECODE.enabled and FileFilter.jpeg(original):
			delete_image(tmp)
	
	if Features.DELETE_ORIGINAL.enabled and original != image:
		delete_image(original)
	
	return result, image


def do_optimize(files: list[Path], file_filter: Callable[[Path], bool]) -> tuple[list[Path], list[Future], int]:
	images: list[Path] = [file for file in files if file_filter(file)]
	image_size: int = get_size_of_files(images)
	
	tasks: list[Future] = []
	
	for image in images:
		task: Future = EXECUTOR.submit(run_wrapper, image)
		tasks.append(task)
	
	return images, tasks, image_size


def initialize_optimizations(directory: Path, threads: int) -> tuple[list[Future], int]:
	print(f"using {threads} threads for {basename(directory)}")
	
	files: list[Path] = [Path(path) for path in listdir(directory)]
	files = [(directory / file) for file in files if FileFilter.any(file)]
	
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


def do_progress_bar(tasks: list[Future[tuple[CompletedProcess, Path]]]) -> None:
	all_tasks: int = len(tasks)
	
	terminal_width: int = shutil.get_terminal_size()[0]
	
	progress_bar_offset_base: int = 10  # 'Progress |' - left side
	progress_bar_offset_numbers: int = 3 + 2 * len(str(all_tasks))  # '| ' and '/' + numbers
	
	progress_bar_width: int = terminal_width - progress_bar_offset_base - progress_bar_offset_numbers
	is_bar: bool = progress_bar_width >= MINIMUM_PROGRESS_BAR_WIDTH
	
	if is_bar:
		bar: Bar = IncrementalBar("Progress", max=all_tasks, width=progress_bar_width, color='cyan')
	else:
		bar: Spinner = PixelSpinner("Processing ")
	
	try:
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
	except KeyboardInterrupt as kbe:
		if is_bar:
			bar.color = "red"
		raise kbe


def parse_args() -> Namespace:  # NOSONAR
	parser = ArgumentParser()
	parser.add_argument(
		"directory",
		type=str,
		default=".",
		action="store",
		nargs="?",
		help="where the images to be optimized are located"
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
		help="comma separated list of features to enable. Available features: "
			 f"{", ".join([str(f) for f in Features])}"
	)
	parser.add_argument(
		"-s",
		"--feature-set",
		dest="feature_set",
		default=None,
		type=str,
		action="store",
		help="name of the feature set to enable. Available feature sets: "
			 f"{", ".join([str(fs) for fs in FeatureSets])}"
	)
	parser.add_argument(
		"--16",
		dest="use_16_bit",
		action="store_true",
		help="allow jpeg2png to create 16-bit png's (this will create massive png's!)"
	)
	args = parser.parse_args()
	
	args.directory = Path(args.directory).expanduser().resolve().absolute()
	
	if args.threads < 1:
		print("negative thread amount; using 1")
		args.threads = 1
	
	if args.use_16_bit:
		InternalFeatures.USE_16_BIT.enable()
	
	bad_feature: bool = False
	for feature in args.features.split(","):
		if (f := Features.get(feature)) is not None:
			f.enable()
		else:
			if feature != "":
				print(f"Given feature '{feature}' does not exist!")
				bad_feature = True
	
	if bad_feature:
		exit(1)
	
	if args.feature_set is not None:
		if (feature_set := FeatureSets.get(args.feature_set)) is not None:
			feature_set.enable_set()
		else:
			print(f"Given feature set '{args.feature_set}' does not exist!")
			exit(1)
	
	if Features.JPEG_BETTER_DECODE.enabled:
		print(f"{Fore.YELLOW}jpeg2png enabled. This will increase file size of jpeg's!{Style.RESET_ALL}")
	
	if Features.DELETE_ORIGINAL.enabled and not (DELETED_IMAGE_FOLDER.exists() and DELETED_IMAGE_FOLDER.is_dir()):
		DELETED_IMAGE_FOLDER.mkdir()
	
	if len((enabled_features := Features.filter(True))) > 0:
		print(f"enabled features: {", ".join([str(f) for f in enabled_features])}")
	
	global EXECUTOR
	EXECUTOR = ThreadPoolExecutor(args.threads)
	
	return args


def main() -> None:
	args: Namespace = parse_args()
	
	tasks, original_size = initialize_optimizations(args.directory, args.threads)
	
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
		f"{f"{Fore.RED}+" if is_less else Fore.CYAN}{pretty_print_bytes(current_size - original_size)}",
		"|",
		f"{"+" if is_less else "-"}{size_difference:.2f}%{Style.RESET_ALL}",
		")"
	)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\rShutting down, this may take a while...")
		print("To cancel the optimization, CTRL+C again.")
		
		EXECUTOR.shutdown(cancel_futures=True)
