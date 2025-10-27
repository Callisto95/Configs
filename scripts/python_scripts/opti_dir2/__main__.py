from argparse import ArgumentParser, Namespace
from os import cpu_count
from pathlib import Path

from colorama import Fore, Style

from python_scripts import pretty_print_bytes
from python_scripts.logger import Logger
from python_scripts.opti_dir2.opti_dir2 import (CJXL, DWebp, EnvVar, ImageFixer, Jpeg2Png, JpegOptim, OptimizationMode,
	optimize_directory, optimize_files, OptimizerFactory, Oxipng)

LOGGER: Logger = Logger("opti-dir2")


def create_factory(mode: OptimizationMode) -> OptimizerFactory:
	factory: OptimizerFactory = OptimizerFactory()
	
	factory.register_preprocessor(None, ImageFixer())
	
	factory.register_processor("png", Oxipng())
	
	if mode == OptimizationMode.SAFE:
		factory.register_processor("jpeg", JpegOptim())
	else:
		factory.register_processor("jpeg", Jpeg2Png())
		factory.register_processor("jpeg", Oxipng())
	factory.register_alias("jpeg", "jpg")
	
	if mode != OptimizationMode.SAFE:
		factory.register_processor("webp", DWebp())
		factory.register_processor("webp", Oxipng())
	
	if mode == OptimizationMode.JXL:
		factory.register_postprocessor(None, CJXL())
	
	return factory


def main() -> None:
	parser: ArgumentParser = ArgumentParser()
	parser.add_argument("directory", type=str, default=".", nargs="?", help="Where to optimize images")
	parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
	parser.add_argument(
		"-t",
		"--threads",
		type=int,
		action="store",
		dest="threads",
		default=cpu_count() - 2,
		help="The amount of threads to use"
	)
	parser.add_argument(
		"-m",
		"--mode",
		action="store",
		dest="mode",
		default="safe",
		choices=[mode.name.lower() for mode in OptimizationMode],
		help="The mode controls enabled features"
	)
	parser.add_argument(
		"-s",
		"--single",
		action="store_true",
		dest="single",
		help="Only work on a single file"
	)
	args: Namespace = parser.parse_args()
	args.directory = Path(args.directory).expanduser().resolve()
	LOGGER.verbose_enabled = args.verbose
	
	EnvVar.print_verbose()
	
	if not args.single and not args.directory.is_dir():
		LOGGER.info("resolving directory from given file")
		args.directory = args.directory.parent
	
	if 1 > args.threads:
		LOGGER.info("negative amount of threads given, using 1")
		args.threads = 1
	
	LOGGER.verbose_log(f"using {args.threads} threads for '{args.directory}'")
	
	factory: OptimizerFactory = create_factory(OptimizationMode[args.mode.upper()])  # this is not an issue
	
	if LOGGER.verbose_enabled:
		registered_file_types: set[str] = factory.get_registered_file_types()
		
		LOGGER.verbose_log(f"registered file types: {", ".join(registered_file_types)}")
		
		LOGGER.verbose_log("aliases:")
		for file_type in [t for t in registered_file_types if factory.get_alias(t) is not None]:
			LOGGER.verbose_log(f"\t{factory.get_alias(file_type)} ==> {file_type}")
		
		for file_type in [t for t in registered_file_types if factory.get_alias(t) is None]:
			f: Path = Path(f"a.{file_type}")
			
			LOGGER.verbose_log(f"|> {file_type}:")
			LOGGER.verbose_log(f"\tpre : {[p.__class__.__name__ for p in factory.get_preprocessors(f)]}")
			LOGGER.verbose_log(f"\tpro : {[p.__class__.__name__ for p in factory.get_processors(f)]}")
			LOGGER.verbose_log(f"\tpost: {[p.__class__.__name__ for p in factory.get_postprocessors(f)]}")
	
	if args.single:
		if not args.directory.is_file():
			LOGGER.error(f"given file '{args.directory}' is not a file")
			exit(1)
		if not args.directory.exists():
			LOGGER.error(f"given file '{args.directory}' does not exist")
			exit(1)
		images = optimize_files([args.directory], args.threads, factory)
	else:
		images = optimize_directory(
			args.directory,
			args.threads,
			factory
		)
	
	if len(images) == 0:
		LOGGER.info("nothing to optimize")
		return
	
	delta: int = sum([i.size_delta for i in images])
	original_file_size: int = sum([i.old_size for i in images])
	processed_file_size: int = sum([i.new_size for i in images])
	
	if delta > 0:
		delta_percent: float = (delta / original_file_size) * 100
		prefix: str = "+"
		colour: str = Fore.RED
	else:
		delta_percent: float = 100 - ((processed_file_size / original_file_size) * 100)
		prefix: str = "-"
		colour: str = Fore.CYAN
	
	base_format: str = f"({{colour}}{{prefix}}{{delta_bytes}} | {{prefix}}{{delta_percent:.2f}}%{Style.RESET_ALL})"
	formatted_size_delta: str = base_format.format(
		colour=colour,
		prefix=prefix,
		delta_bytes=pretty_print_bytes(delta),
		delta_percent=delta_percent
	)
	
	LOGGER.log(
		pretty_print_bytes(original_file_size),
		"->",
		pretty_print_bytes(processed_file_size),
		formatted_size_delta
	)


if __name__ == '__main__':
	main()
