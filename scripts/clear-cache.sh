#!/bin/sh

echo "clearing pip cache"
python -m pip cache purge

echo "clearing pacman and yay cache"
yes | yay -Sc

echo "clearing coredumps"
sudo rm -r /var/lib/systemd/coredump/

echo "clearing thumbnail cache"
THUMBNAIL_CACHE_DIR="$HOME/.cache/thumbnails"

for dir in $THUMBNAIL_CACHE_DIR/*; do
	rm -r "$dir"
	sleep 0.5
	mkdir "$dir"
done

# for file in `find "$THUMBNAIL_CACHE_DIR" -type f`; do
# 	rm "$file"
# done

echo "done"
