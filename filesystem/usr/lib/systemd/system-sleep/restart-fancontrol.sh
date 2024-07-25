#!/bin/sh

if [[ "$1" == "post" ]]; then
	systemctl restart fancontrol
	echo "restarted fancontrol after $2"
fi
