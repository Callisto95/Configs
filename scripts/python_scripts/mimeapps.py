from mimetypes import guess_file_type
from gi.repository import Gio
import sys
import os
from subprocess import run

if len(sys.argv) != 2:
	print('Error: Exactly one command line argument needed')
	sys.exit(1)

if os.path.exists(sys.argv[1]):
	mime = guess_file_type(sys.argv[1])[1]
	
	if mime is None:
		print("type could not be guessed, falling back to xdg-mime")

		proc = run(["xdg-mime", "query", "filetype", sys.argv[1]], capture_output=True)
		mime = proc.stdout.decode("UTF-8").strip()
else:
	mime = sys.argv[1]

print("MIME-type:", mime)
print()

for app in Gio.app_info_get_all_for_type(mime):
	print(app.get_id())
