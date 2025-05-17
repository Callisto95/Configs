from argparse import ArgumentParser, Namespace
from os import listdir
from os.path import abspath, expanduser
from typing import Any

from jxlpy import JXLPyDecoder
from PIL import Image

parser: ArgumentParser = ArgumentParser()
parser.add_argument("directory", type=str, default=".", nargs="?")
args: Namespace = parser.parse_args()

args.directory = abspath(expanduser(args.directory))


def get_jxl_size(file: str) -> tuple[int, int]:
	with open(file, "rb") as jxl:
		content = jxl.read()
	image: JXLPyDecoder = JXLPyDecoder(content)
	
	info: dict[str, Any] = image.get_info()
	return info['xsize'], info['ysize']


def get_other_size(file: str) -> tuple[int, int]:
	image: Image = Image.open(file)
	
	return image.size


# (y / x) is used instead of (x / y), as this former is a finite number
PERFECT_DIV: float = 9 / 16
MAXIMUM_DELTA: float = 0.0002

MINIMUM: float = PERFECT_DIV - MAXIMUM_DELTA
MAXIMUM: float = PERFECT_DIV + MAXIMUM_DELTA

for file in listdir(args.directory):
	if file.endswith(".jxl"):
		size = get_jxl_size(f"{args.directory}/{file}")
	elif file.endswith((".png", ".jpg", ".jpeg")):
		size = get_other_size(f"{args.directory}/{file}")
	else:
		continue
	
	div: float = size[1] / size[0]
	# truncate number
	div: float = float(f"{div:.4f}")
	
	if MINIMUM <= div <= MAXIMUM:
		print("\u001B[32m[ OK ]", end="")
	else:
		print("\u001B[31m[FAIL]", end="")
	print(f"\u001B[0m {file} ({div})")
