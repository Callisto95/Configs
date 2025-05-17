import json
import sys
from argparse import ArgumentParser, Namespace
from os.path import abspath, expanduser
from typing import Any

import requests
from requests import Response

from python_scripts.logger import Logger

LOGGER: Logger = Logger("discord-sticker-dl")


class Error404(Exception):
	pass


API_BASE_URL: str = "https://discord.com/api/v9"
CDN_BASE_URL: str = "https://cdn.discordapp.com"
CDN_EMOJI_URL: str = f"{CDN_BASE_URL}/emojis"
CDN_STICKER_URL: str = f"{CDN_BASE_URL}/stickers"

EMOJI_PACK_LIST_URL: str = f"{API_BASE_URL}/guilds/{{guild_id}}/emojis"
STICKER_PACK_LIST_URL: str = f"{API_BASE_URL}/guilds/{{guild_id}}/stickers"
EMOJI_REQUEST_URL: str = f"{CDN_EMOJI_URL}/{{id}}.png"
STICKER_REQUEST_URL: str = f"{CDN_STICKER_URL}/{{id}}.png"


HEADERS: dict[str, str] = {
	"Cookie": "COOKIE",
	"Authorization": "AUTH"
}


def gett(url: str, get_raw: bool = False) -> Any:
	response: Response = requests.get(url, headers=HEADERS)
	
	if response.status_code != 200:
		raise Error404(f"invalid response code {response.status_code}! '{url}'")
	
	if get_raw:
		return response.content
	
	return json.loads(response.content)


def download(guild_id: int, directory: str, pack_url: str, download_url: str) -> None:
	for thing in gett(pack_url.format(guild_id=guild_id)):
		id = thing["id"]
		name = thing["name"]
		
		url = download_url.format(guild_id=guild_id, id=id)
		LOGGER.verbose_log(f"requesting {url}, should be {name}/{id} of {pack_url}")
		
		if "emoji" in pack_url and thing["animated"]:
			extension = "gif"
		else:
			extension = "png"
		
		try:
			content = gett(url, get_raw=True)
		except Error404:
			LOGGER.warn("PNG not found, assuming it's a gif")
			content = gett(url.replace(".png", ".gif").replace(CDN_BASE_URL, "https://media.discordapp.net"), get_raw=True)
			extension = "gif"
		
		with open(f"{directory}/{name}-{id}.{extension}", "wb") as file:
			file.write(content)


def main() -> None:
	parser: ArgumentParser = ArgumentParser()
	parser.add_argument("guild_id", type=int)
	parser.add_argument("directory", nargs="?", default=".")
	args: Namespace = parser.parse_args()
	
	directory = abspath(expanduser(args.directory))
	
	guild_id: int = int(sys.argv[1])
	
	LOGGER.info(f"using guild {guild_id}")
	
	download(guild_id, directory, EMOJI_PACK_LIST_URL, EMOJI_REQUEST_URL)
	download(guild_id, directory, STICKER_PACK_LIST_URL, STICKER_REQUEST_URL)


if __name__ == '__main__':
	main()
	
