#!/bin/bash

DIR="$(dirname "$0")"

case "$1" in
	"start")
		# "$DIR"/scx.sh "start";
		notify-send --app-name "GameMode" "GameMode started";
		;;
	"end")
		# "$DIR"/scx.sh "stop";
		notify-send --app-name "GameMode" "GameMode ended";
		;;
	*)
		echo "unknown mode";
		exit 1;
	;;
esac
