if [ "$1" == "" ]; then
	echo "video URL required"
	exit 1
fi

yt-dlp -x --audio-format opus --audio-quality 0 --add-metadata --embed-thumbnail -o "%(title)s.%(ext)s" "$1"
