import os
from argparse import ArgumentParser, Namespace
from enum import auto, Flag, StrEnum
from math import log10
from os import getcwd, makedirs, remove
from os.path import abspath, exists, expanduser, isfile
from shutil import copy2, copyfile
from zipfile import ZipFile

from colorama import Fore, Style


def info(message: str) -> None:
	print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")


def error(message: str) -> None:
	print(f"{Fore.RED}{message}{Style.RESET_ALL}")


def warning(message: str) -> None:
	print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")


def normalize_path(path: str) -> str:
	return abspath(expanduser(path))


def backup(source_file: str, target_name: str, backup_directory: str = None) -> None:
	if backup_directory is None:
		backup_directory = f"{getcwd()}/backup"
	
	if not exists(backup_directory):
		os.makedirs(backup_directory)
	
	copy2(source_file, f"{backup_directory}/{target_name}")


def undo_backup(source_file: str, target: str, backup_directory: str = None) -> bool:
	if backup_directory is None:
		backup_directory = f"{getcwd()}/backup"
	
	backup_file: str = f"{backup_directory}/{source_file}"
	
	if not exists(backup_directory) or not exists(backup_file):
		return False
	
	copy2(backup_file, target)
	remove(backup_file)
	return True


class ExitCode(Flag):
	MISSING_ZIP = auto()
	INVALID_ZIP = auto()


class Mode(StrEnum):
	ADD = "add"
	REMOVE = "remove"


BASE_DIR: str = normalize_path("~/.config/zipinstall/")

parser = ArgumentParser("ZipInstall")

parser.add_argument("mode", type=str, choices=["add", "remove"], help="The mode of ZipInstall")
parser.add_argument("zip_file", type=str, help="The zip file to install / uninstall")
parser.add_argument("target_dir", type=str, help="The directory in which the zip file will be installed")
parser.add_argument("-o", "--allow-overwrite", action="store_true", dest="allow_overwrite", help="[add]: Existing files will be overwritten, backups of the original files are kept")
parser.add_argument("-u", "--undo-backup", action="store_true", dest="undo_backup", help="[remove]: Undo an addition, while also restoring backups of the original files")

args: Namespace = parser.parse_args()

if not exists(args.zip_file):
	error(f"zip file '{args.zip_file}' does not exist!")
	exit(ExitCode.MISSING_ZIP)

if not isfile(args.zip_file):
	error(f"zip file '{args.zip_file}' is not a file!")
	exit(ExitCode.INVALID_ZIP)

args.zip_file = normalize_path(args.zip_file)

if not exists(args.target_dir):
	warning("target directory does not exist, creating it")
	makedirs(args.target_dir)

args.target_dir = normalize_path(args.target_dir)

zip_file: ZipFile = ZipFile(args.zip_file)

file_amount: int = len(zip_file.filelist)
iterator_width: int = 1 + int(log10(file_amount))

for index, file in enumerate(zip_file.filelist):
	index += 1
	new_file_path: str = f"{args.target_dir}/{file.filename}"
	
	if args.mode == Mode.ADD:
		if exists(new_file_path):
			if args.allow_overwrite:
				info(f"file '{new_file_path}' already exists; overwriting, but creating backup")
				backup(new_file_path, file.filename)
			else:
				warning(f"file '{new_file_path}' already exists, skipping!")
				continue
		
		print(f"[{index:>{iterator_width}}/{file_amount}] installing {file.filename}")
		with zip_file.open(file.filename) as file_content, open(new_file_path, "wb") as new_file:
			new_file.write(file_content.read())
	elif args.mode == Mode.REMOVE:
		if args.undo_backup:
			if undo_backup(file.filename, new_file_path):
				info(f"backup of file '{file.filename}' found")
				continue
			else:
				info(f"no backup of file '{file.filename}' found")
		
		if not exists(new_file_path):
			warning(f"file '{new_file_path}' does not exist!")
			continue
		
		print(f"[{index:>{iterator_width}}/{file_amount}] removing {file.filename}")
		remove(new_file_path)
	else:
		# handled by argparse choice option
		error("you should never see this")
