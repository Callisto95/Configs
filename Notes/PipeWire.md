# PipeWire

## pipewire-media-session to WirePlumber

I just updated from `pipewire-media-session` to WirePlumber.

It destroyed everything. KDE took ~15 seconds to be useful, no audio, everything that accessed audio froze, and that's just what I remember.

`systemctl --user status pipewire-pulse` reports something along the lines of `Host is down`. This is effectively the root cause, as other units depend on it. Interestingly `pipewire.service` reports everything is fine.

What I remember to fix it:

1. delete `/etc/pipewire`
2. reinstall everything pipewire related: `sudo pacman -S $(pacman -Qs pipewire)`. This will regenerate all configs.
3. reboot
