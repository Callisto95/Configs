#!/usr/bin/python

import shutil
from argparse import ArgumentParser
from concurrent.futures import Future, ThreadPoolExecutor
from multiprocessing import cpu_count
from os import listdir
from os.path import expanduser, getsize, join
from shutil import which
from subprocess import DEVNULL, run
from time import sleep

from progress import colors
from progress.bar import Bar, IncrementalBar
from progress.spinner import PixelSpinner, Spinner

MINIMUM_PROGRESS_BAR_WIDTH: int = 10


OPTIPNG_AVAILABLE: bool = which("optipng") is not None
JPEGOPTIM_AVAILABLE: bool = which("jpegoptim") is not None

if not OPTIPNG_AVAILABLE or not JPEGOPTIM_AVAILABLE:
	print("neither jpegoptim nor optipng are installed")
	exit(1)

if not OPTIPNG_AVAILABLE:
	print("optipng not installed!")
if not JPEGOPTIM_AVAILABLE:
	print("jpegoptim not installed!")

parser = ArgumentParser()
parser.add_argument("directory",
	type=str,
	default=".",
	action="store",
	nargs="?",
	help="where the unoptimized images are located")
parser.add_argument("-t",
	"--threads",
	dest="threads",
	type=int,
	default=cpu_count() - 2,
	action="store",
	help="the amount of used threads. Defaults to [all - 2]")
args = parser.parse_args()

args.directory = expanduser(args.directory)

if args.threads < 1:
	print("negative thread value, using 1")
	args.threads = 1


def is_png(path: str) -> bool:
	return path.endswith(".png")


def is_jpg(path: str) -> bool:
	return path.endswith(".jpg") or path.endswith(".jpeg")


def done_tasks(maybe: list[Future]) -> int:
	return len([t for t in maybe if t.done()])


def get_size_of_files(directory: str) -> int:
	return sum([getsize(f"{directory}/{file}") for file in listdir(directory) if is_jpg(file) or is_png(file)])


def pretty_print_bytes(byte_amount: int) -> str:
	if byte_amount < 0:
		return f"-{pretty_print_bytes(-byte_amount)}"
	
	units: list[str] = ["B", "KiB", "MiB", "GiB", "TiB"]
	
	unit_index: int = 0
	
	while byte_amount > 1024:
		byte_amount = byte_amount / 1024
		unit_index += 1
	
	return f"{byte_amount:.1f} {units[unit_index]}"


def main(executor: ThreadPoolExecutor) -> list[Future]:
	print(f"using {args.threads} threads for {args.directory}")
	files: list[str] = listdir(args.directory)
	files = [join(args.directory, file) for file in files]
	tasks: list[Future] = []
	
	pngs: list[str] = []
	if OPTIPNG_AVAILABLE:
		pngs = [file for file in files if is_png(file)]
		
		if len(pngs) > 0:
			print(f"optimizing {len(pngs)} PNG's...")
			for png in pngs:
				task = executor.submit(run, ["optipng", "-preserve", "-fix", png], stdout=DEVNULL, stderr=DEVNULL)
				tasks.append(task)
	
	jpgs: list[str] = []
	if JPEGOPTIM_AVAILABLE:
		jpgs = [file for file in files if is_jpg(file)]
		
		if len(jpgs) > 0:
			print(f"optimizing {len(jpgs)} JPG's...")
			for jpg in jpgs:
				task = executor.submit(run, ["jpegoptim", "--preserve", jpg], stdout=DEVNULL, stderr=DEVNULL)
				tasks.append(task)
	
	if len(pngs) == 0 and len(jpgs) == 0:
		print("nothing to optimize")
	
	return tasks


def mainw() -> None:
	with ThreadPoolExecutor(max_workers=args.threads) as executor:
		try:
			original_size: int = get_size_of_files(args.directory)
			
			if original_size == 0:
				original_size = 1
			
			tasks: list[Future] = main(executor)
			all_tasks: int = len(tasks)
			
			terminal_width: int = shutil.get_terminal_size()[0]
			
			progress_bar_offset_base: int = 10  # 'Progress |' - left side
			progress_bar_offset_numbers: int = 3 + 2 * len(str(all_tasks))  # '| ' and '/' + numbers
			
			progress_bar_width: int = terminal_width - progress_bar_offset_base - progress_bar_offset_numbers
			is_bar: bool = progress_bar_width >= MINIMUM_PROGRESS_BAR_WIDTH
			
			if is_bar:
				bar: Bar = IncrementalBar("Progress",
					max=all_tasks,
					width=progress_bar_width,
					color='cyan')
			else:
				bar: Spinner = PixelSpinner("Processing ")
			
			done: int = 0
			counter: int = 0
			while done != all_tasks:
				if is_bar:
					done = done_tasks(tasks)
					bar.goto(done)
					
					if done == all_tasks:
						bar.color = "green"
						bar.update()
						break
					
					sleep(1)
				else:
					counter += 1
					if counter == 10:
						done = done_tasks(tasks)
						counter = 0
					bar.next()
					sleep(0.1)
				
			bar.finish()
			
			current_size: int = get_size_of_files(args.directory)
			
			failed: list = [task for task in tasks if task.result().returncode != 0]
			
			if len(failed) > 0:
				print(f"some tasks ({len(failed)}) have failed!")
				
				print("failed images:")
				for task in failed:
					print(f"\t{task.result().args[-1]}")
			
			if len(tasks) > 0:
				print(f"{pretty_print_bytes(original_size)} -> {pretty_print_bytes(current_size)} ("
					f"{pretty_print_bytes(current_size - original_size)} | "
					f"-{(1 - (current_size / original_size)) * 100:.2f}%)")
		
		except KeyboardInterrupt:
			print("\rKeyboardInterrupt, aborting! This may take a while.")
			executor.shutdown(cancel_futures=True)


if __name__ == '__main__':
	try:
		mainw()
	except KeyboardInterrupt:
		print("Caught a Keyboard interrupt. Most likely because the executor took too long.")
