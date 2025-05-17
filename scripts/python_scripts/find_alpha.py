from argparse import ArgumentParser, Namespace
from os import listdir
from os.path import abspath, expanduser

import jxlpy
from PIL import Image, ImageFile

parser: ArgumentParser = ArgumentParser()
parser.add_argument("directory", default=".", type=str, nargs="?")

args: Namespace = parser.parse_args()
args.directory = abspath(expanduser(args.directory))

files: list[str] = listdir(args.directory)

images: list[str] = [file for file in files if file.endswith((".png", ".jpg", ".jpeg", ".jxl"))]

for image in images:
	if image.endswith(".jxl"):

		with open(image, "rb") as jxl:
			content = jxl.read()
		
		decoder: jxlpy.JXLPyDecoder = jxlpy.JXLPyDecoder(content)
		
		hasAlpha: bool = decoder.get_colorspace() == "RGBA"
	else:
		img: ImageFile = Image.open(image)
		
		hasAlpha: bool = len(img.split()) == 4
	
	if hasAlpha:
		print(f"Alpha found: {image}")
