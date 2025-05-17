from __future__ import annotations

import os
import re
from argparse import ArgumentParser, Namespace
from enum import StrEnum
from os.path import basename

import jxlpy
from PIL import Image
from tabulate import tabulate

EOL_OFFSET: int = -1

MIN_HORIZONTAL_SIZE: tuple[int, int] = (2560, 1440)
IDEAL_HORIZONTAL_SIZE: tuple[int, int] = (3840, 2160)

MIN_VERTICAL_SIZE: tuple[int, int] = (1080, 2400)
IDEAL_VERTICAL_SIZE: tuple[int, int] = (1080, 2400)

# regexes for name extensions
# version is optional, can be 'protogen-1' or 'protogen-v1'
# version and numbering is not supported
VERSION_AND_NUMBER: str = "-[v]?[0-9]{1,2}"
UPSCALING_FACTOR: str = "_x[0-9]{1,2}"

# all allowed files, anything else will not be considered
IMAGE_FILE_EXTENSIONS: tuple[str, str, str, str] = (".png", ".jpg", ".jpeg", ".jxl")

IGNORE_FILE: str = "bac_manage_ignored_files.txt"
ignored: list[str] = []

parser = ArgumentParser()
parser.add_argument("directory", action="store", type=str, default=".", nargs="?", help="the main working directory")
parser.add_argument(
	"--include-sorted",
	action="store_true",
	dest="include_sorted",
	help="get all files, even if they're sorted (have an equivalent in non originals folder)"
)
parser.add_argument(
	"--only-non-ideal",
	action="store_true",
	dest="only_non_ideal",
	help="prints all images, which don't have an ideal size"
)
# TODO
# parser.add_argument(
# 	"--find-dangling",
# 	action="store_true",
# 	dest="find_dangling",
# 	help="finds all images, which are sorted, but have no original"
# )
# TODO
# parser.add_argument(
# 	"--find-unsorted",
# 	action="store_true",
# 	dest="find_unsorted",
# 	help="finds all images, which are in the originals folder, but not sorted"
# )
parser.add_argument(
	"--skip",
	action="store",
	type=str,
	default=None,
	dest="skip",
	help="directories, which should be skipped. Comma separated"
)

args: Namespace = parser.parse_args()
args.directory = os.path.abspath(os.path.expanduser(args.directory))
if args.skip is None:
	args.skip = []
else:
	args.skip = args.skip.split(",")

if os.path.exists(IGNORE_FILE):
	with open(IGNORE_FILE, "r") as image:
		ignored = [line[:EOL_OFFSET] for line in image.readlines()]


class Directories(StrEnum):
	ORIGINALS: str = os.path.join(args.directory, "originals")
	UPSCALED: str = os.path.join(args.directory, "upscaled")
	ICONS: str = os.path.join(args.directory, "icons")
	HORIZONTAL: str = os.path.join(args.directory, "16x9")
	VERTICAL: str = os.path.join(args.directory, "21x9")


class File:
	def __init__(self, file_name: str, folder: str, name_extension: str = "", meta_file: bool = False):
		# meta files are non-existing files
		# they're used in the ignored file
		self.meta_file: bool = meta_file
		
		self._raw_file_name: str = file_name
		self._directory: str = folder
		
		# name does not include file ending (e.g. '.png')
		dot_index: int = file_name.rfind('.')
		
		# name_extension are e.g. '_x3' for upscaled images or 'v2' / '-2' for images with multiple versions
		if len(name_extension) > 0:
			self.name: str = file_name[:dot_index][:-len(name_extension)]
		else:
			self.name: str = file_name[:dot_index]
		
		# previously mentioned: '_x3' / 'v2' / '-2'
		self.name_extension: str = name_extension
		# previously mentioned: '.png'
		self.extension: str = file_name[dot_index + 1:]
		
		# meta files do not have a size, their purpose is to skip actual files
		if self.meta_file:
			# essentially random defaults, just to have these properties
			self.size: tuple[int, int] = (0, 0)
			self.is_horizontal: bool = True
			self.is_too_small: bool = False
			self.is_ideal_size: bool = True
			return
		
		self.size: tuple[int, int] = self._get_size()
		self.is_horizontal: bool = self.x > self.y
		
		if self.is_horizontal:
			self.is_too_small: bool = self.size < MIN_HORIZONTAL_SIZE
			self.is_ideal_size: bool = self.size >= IDEAL_HORIZONTAL_SIZE
		else:
			self.is_too_small: bool = self.size < MIN_VERTICAL_SIZE
			self.is_ideal_size: bool = self.size >= IDEAL_VERTICAL_SIZE
	
	@property
	def x(self) -> int:
		return self.size[0]
	
	@property
	def y(self) -> int:
		return self.size[1]
	
	@property
	def directory(self) -> str:
		# the directories are saved as absolute paths, but mostly required as just the name
		return basename(self._directory)
	
	@property
	def absolute_path(self) -> str:
		return self._directory
	
	def _get_size(self) -> tuple[int, int]:
		if self.extension == "jxl":
			# not saving content like this causes a segfault
			with open(os.path.join(self._directory, self._raw_file_name), "rb") as jxl:
				content: bytes = jxl.read()
			
			decoder: jxlpy.JXLPyDecoder = jxlpy.JXLPyDecoder(content)
			info: dict[str, int] = decoder.get_info()
			
			return info["xsize"], info["ysize"]
		
		img: Image = Image.open(os.path.join(self._directory, self._raw_file_name))
		size = img.size
		img.close()
		return size
	
	def __str__(self) -> str:
		# definitely not overloaded str method
		if self.meta_file:
			return f"{self.name}{self.name_extension}.{self.extension} (meta)"
		
		return (f"{self.name}{self.name_extension}.{self.extension} @{self.directory} | {self.x}x{self.y}"
				f"({"H" if self.is_horizontal else "V"}) | ideal: {"yes" if self.is_ideal_size else "no"}")
	
	def __repr__(self) -> str:
		return f"{self.name}.{self.extension}"
	
	def __eq__(self, other) -> bool:
		if isinstance(other, File):
			# this is needed for filtering
			# also this is why the name must be extracted
			return self.name == other.name
		else:
			return self.name == other
	
	def __lt__(self, other) -> bool:
		return self.name.lower() < other.name_.lower()
	
	def __gt__(self, other):
		return self.name.lower() > other.name_.lower()
	
	def __hash__(self):
		return hash(self.name)
	
	@classmethod
	def unknown_name_extension(cls, file: str, directory: str, possible_extension_regex: str) -> File:
		# the part behind the name is unknown, extract the name with the given regex
		dotindex: int = file.rfind(".")
		pure_file_name: str = file[:dotindex]
		
		result = re.search(f".*({possible_extension_regex})", pure_file_name)
		
		if result is None or len(result.groups()) != 1:
			return cls(file, directory, "")
		
		return cls(file, directory, result.group(1))
	
	@classmethod
	def from_directory(cls, directory: str, possible_extension_regex: str = None) -> list[File]:
		# shorthand: multiple files with the same name extension in the same directory
		images: list[str] = [file for file in os.listdir(directory) if file.endswith(IMAGE_FILE_EXTENSIONS)]
		images.sort()
		
		if possible_extension_regex is None:
			return [cls(path, directory) for path in images]
		
		return [cls.unknown_name_extension(path, directory, possible_extension_regex) for path in images]
	
	def to_table_data(self) -> list[str]:
		# ["File", "Folder", "Resolution", "Rotation", "Ideal"]
		return [self.name, self.directory, f"{self.x}x{self.y}", "Horizontal" if self.is_horizontal else "Vertical",
			"yes" if self.is_ideal_size else "no"]


def in_any(src: list[File], *others: list[File]) -> list[File]:
	for other in others:
		src = [i for i in src if i in other]
	
	return src


def not_in_any(src: list[File], *others: list[File]) -> list[File]:
	for other in others:
		src = [i for i in src if i not in other]
	
	return src


originals: list[File] = File.from_directory(Directories.ORIGINALS, VERSION_AND_NUMBER)
upscaled: list[File] = File.from_directory(Directories.UPSCALED, f"{VERSION_AND_NUMBER}{UPSCALING_FACTOR}")
horizontals: list[File] = File.from_directory(Directories.HORIZONTAL, VERSION_AND_NUMBER)
verticals: list[File] = File.from_directory(Directories.VERTICAL, VERSION_AND_NUMBER)
icons: list[File] = File.from_directory(Directories.ICONS, VERSION_AND_NUMBER)

ignored: list[File] = [File(ign, "", meta_file=True) for ign in ignored]


"""
TODO:

- find too small images
- find smaller than ideal images
- find untracked images
	- in originals
	- in folders
"""


# TODO: changed default behaviour
if not args.skip:
	args.skip = "originals"

directories = zip(
	["originals", "upscaled", "verticals", "horizontals", "icons"],
	[originals, upscaled, verticals, horizontals, icons]
)

for directory in directories:
	if directory[0] in args.skip:
		print(f"skipping folder: {directory[0]}")
		continue
	
	images: list[File] = not_in_any(directory[1], ignored)
	bad_images: list[File] = []
	for image in images:
		if image.is_too_small or (args.only_non_ideal and not image.is_ideal_size):
			bad_images.append(image)
	
	if bad_images:
		print(
			tabulate(
				[img.to_table_data() for img in bad_images],
				headers=["File", "Folder", "Resolution", "Rotation", "Ideal"],
				tablefmt="rounded_outline"
			)
		)

with open(IGNORE_FILE, 'w') as image:
	image.writelines([f"{line}\n" for line in ignored])
