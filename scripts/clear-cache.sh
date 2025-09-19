#!/bin/sh

echo "clearing pacman and yay cache"
yay -Sc --noconfirm
# yes | paru -Scd

echo "clearing coredumps"
sudo rm -r /var/lib/systemd/coredump/

echo "clearing thumbnail cache"
THUMBNAIL_CACHE_DIR="$HOME/.cache/thumbnails"

for dir in $THUMBNAIL_CACHE_DIR/*; do
	rm -r "$dir"
	sleep 0.5
	mkdir "$dir"
done

echo "clearing cargo cache"
# requires: cargo install cargo-cache
cargo cache -a

echo "done"
