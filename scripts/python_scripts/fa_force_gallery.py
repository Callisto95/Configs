#!/usr/bin/python
from http.cookiejar import MozillaCookieJar
from os.path import abspath, expanduser, join

from bs4 import BeautifulSoup
import requests
from time import sleep
import json
import re
import os.path
from os import makedirs
import sys
from typing import Any
from colorama import Fore, Style

START_URL: str = f"https://furaffinity.net/view/{sys.argv[1]}" if sys.argv[1].isdigit() else sys.argv[1]
USER: str | None = None


with open(os.path.expanduser("~/.config/gallery-dl/config.json"), "r") as config_file:
	config = json.load(config_file)
	cookies = config["extractor"]["furaffinity"]["cookies"]
	
	# reference to a file, not hard-coded values
	if isinstance(cookies, str):
		cookies = abspath(expanduser(cookies))
		cookies = MozillaCookieJar(cookies)
		cookies.load()
	
	GALLERY_DIR: str = join(config["extractor"]["base-directory"], "fa_forced")


def make_request(current_url: str) -> requests.Response:
	return requests.get(current_url, cookies=cookies)


def get_buttons_from_page(current_url: str) -> tuple[Any, Any, Any]:
	global USER
	
	while (response := make_request(current_url)).status_code != 200:
		print("invalid response!")
		print(f"code: {response.status_code}, message: {response}")
		
		sleep(5)
	
	html = response.text
	
	bs = BeautifulSoup(html, features="html.parser")
	
	if USER is None:
		USER = bs.body.find('div', attrs={"class": "submission-id-sub-container"}).find('a').next.text
		makedirs(f"{GALLERY_DIR}/{USER}", exist_ok=True)
	
	buttons = bs.body.find_all('a', attrs={"class": "button standard mobile-fix"})
	
	# all buttons (with URL, ), has prev, has next
	
	prev_button = None
	next_button = None
	download_button = None
	
	for button in buttons:
		match button.text:
			case "Prev":
				prev_button = button
			case "Next":
				next_button = button
			case "Download":
				download_button = button
	
	return download_button, prev_button, next_button


def url_from_button(button) -> str:
	return f"https://www.furaffinity.net{button['href']}"


def download_from_button(button) -> None:
	regex_result = re.search(r".*/(.*)$", button['href'])
	
	if not regex_result:
		print("unknown download url")
		sys.exit(1)
	
	url: str = f"http:{button['href']}"
	path: str = f"{GALLERY_DIR}/{USER}/{regex_result.group(1)}"
	
	print(f"\r{path}", end="")
	
	if os.path.exists(path):
		print(f"\r{Fore.CYAN}{path}{Style.RESET_ALL}")
		return
	
	with open(path, "wb") as file:
		file.write(requests.get(url).content)
		print(f"\r{Fore.LIGHTGREEN_EX}{path}{Style.RESET_ALL}")


def main() -> None:
	current_url: str = START_URL
	
	base_url: str | None = None
	
	while True:
		download, prev, _next = get_buttons_from_page(current_url)
		
		if base_url is None:
			base_url = _next
		
		if download:
			download_from_button(download)
		
		if prev is None:
			break
		else:
			current_url = url_from_button(prev)
	
	print("finished previous, reversing to next...")
	current_url = url_from_button(base_url)
	while True:
		download, _, _next = get_buttons_from_page(current_url)
		
		if download:
			download_from_button(download)
		
		if _next is None:
			break
		else:
			current_url = url_from_button(_next)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\rKeyboardInterrupt!")
