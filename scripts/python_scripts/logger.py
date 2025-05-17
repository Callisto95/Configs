from colorama import Fore, Style


class Logger:
	_verbose_enabled: bool = False
	
	@property
	def verbose_enabled(self) -> bool:
		return Logger._verbose_enabled
	
	@verbose_enabled.setter
	def verbose_enabled(self, value: bool) -> None:
		Logger._verbose_enabled = value
	
	def __init__(self, name: str):
		self.name = name
	
	def verbose_log(self, *args, **kwargs) -> None:
		if not Logger._verbose_enabled:
			return
		self.log(*args, **kwargs)
	
	@staticmethod
	def log(*args, **kwargs) -> None:
		print(*args, **kwargs)
	
	def _coloured_output(self, type_name: str, colour: Fore, *args, **kwargs) -> None:
		print(colour, f"[{type_name}][{self.name}]", *args, Style.RESET_ALL, **kwargs)
	
	def warn(self, *args, **kwargs) -> None:
		self._coloured_output("warn", Fore.YELLOW, *args, **kwargs)
	
	def error(self, *args, **kwargs) -> None:
		self._coloured_output("error", Fore.RED, *args, **kwargs)
	
	def info(self, *args, **kwargs) -> None:
		self._coloured_output("info", Fore.CYAN, *args, **kwargs)


__all__ = ["Logger"]
