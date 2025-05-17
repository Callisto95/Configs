from __future__ import annotations

import hashlib
import re
from argparse import ArgumentParser, Namespace
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from os import getcwd, listdir, makedirs, rename
from os.path import abspath, expanduser, getmtime, isfile

from PIL import Image
from psutil import cpu_count

TWITTER_PATTERN: re.Pattern = re.compile(r".*-\d{10,19}_\d\.(jpg|png)")

parser = ArgumentParser()
parser.add_argument("directory", nargs="?", default=getcwd())
args: Namespace = parser.parse_args()

args.directory = abspath(expanduser(args.directory))

print("loading files...")

EXECUTOR: ThreadPoolExecutor = ThreadPoolExecutor(cpu_count() - 2)
BUFFER_SIZE: int = 64 * 1024


# the underlying image data is hashed, not the entire file
# metadata is therefore ignored
def hash_file(file: str) -> tuple[int, str]:
	if file.endswith((".png", ".jpg", ".jpeg")):
		with Image.open(file) as f:
			hash_ = hash(f.tobytes())
	else:
		with open(file, "rb") as f:
			hash_ = hash(f.read())
	
	return hash_, file


futures: list[Future[tuple[int, str]]] = []
for file in listdir():
	if not isfile(file):
		continue
	
	futures.append(EXECUTOR.submit(hash_file, file))

EXECUTOR.shutdown()

hashes: list[tuple[int, str]] = [future.result() for future in futures]

print("done")

makedirs(f"{args.directory}/duplicates", exist_ok=True)

size: int = len(hashes)
removed: list[int] = []

for i in range(size):
	for j in range(i):
		if j not in removed and hashes[i][0] == hashes[j][0]:
			if TWITTER_PATTERN.match(hashes[i][1]) and not TWITTER_PATTERN.match(hashes[j][1]):
				keep_image = hashes[j]
				delete_image = hashes[i]
				delete_index = i
			elif not TWITTER_PATTERN.match(hashes[i][1]) and TWITTER_PATTERN.match(hashes[j][1]):
				keep_image = hashes[i]
				delete_image = hashes[j]
				delete_index = j
			elif getmtime(f"{args.directory}/{hashes[i][1]}") > getmtime(f"{args.directory}/{hashes[j][1]}"):
				keep_image = hashes[i]
				delete_image = hashes[j]
				delete_index = j
			else:
				keep_image = hashes[j]
				delete_image = hashes[i]
				delete_index = i
			
			removed.append(delete_index)
			print(f"{delete_image[1]} is {keep_image[1]}")
			rename(f"{args.directory}/{delete_image[1]}", f"{args.directory}/duplicates/{delete_image[1]}")
	
	print(f"{i}/{size}", end="\r")
