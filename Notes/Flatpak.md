# Flatpak

## Flatpak's use wrong cursor

1. Install `xdg-desktop-portal-gtk`, **even on KDE**.

2. Within `$XDG_CONFIG_HOME/xdg-desktop-portal/portals.conf` add `org.freedesktop.impl.portal.Settings=gtk` under `[preferred]`.

Notes:

- `$XDG_CONFIG_HOME` is most likely `$HOME/.config`
- `default` within `[preferred]` is most likely automatically set, but just in case add it yourself (KDE uses `KDE`, not `kde`)
- `/etc/xdg/xdg-desktop-portal/portals.conf` is the system override

3. (maybe not needed) Some Flatpak's do not have a theme / theme loader included, which is why a completely different cursor theme us used. Technically, giving these apps access to `/usr/share/icons` would solve this, but the Flatpak doesn't allow that.

As a workaround it's possible to give all apps access to `$HOME/.icons/` with `flatpak --user --override --filsystem=$HOME/.icons/:ro`. Then copy everything from `/usr/share/icons` into `$HOME/.icons`. I have created a hook for that (see `etc/pacman.d/hooks/10-icons-sync.hook`).

## Overrides

The overrides are stored in `$HOME/.local/share/flatpak/overrides` or `/var/lib/flatpak/overrides`.
