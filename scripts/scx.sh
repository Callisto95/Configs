#!/bin/bash

# https://lib.rs/crates/scx_loader

set -e

SCHEDULER="${2:-scx_lavd}"

case "$1" in
	"stop")
		dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.scx.Loader.StopScheduler;
		;;
	"start")
		dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.scx.Loader.StartScheduler string:"$SCHEDULER" uint32:0;
		;;
	"get")
		dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.freedesktop.DBus.Properties.Get string:org.scx.Loader string:CurrentScheduler;
		;;
	"list")
		dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.freedesktop.DBus.Properties.Get string:org.scx.Loader string:SupportedSchedulers;
		;;
	"switch")
		dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.scx.Loader.SwitchScheduler string:"$SCHEDULER" uint32:2;
		;;
	*)
		echo "unknown command";
		exit 1;
		;;
esac
