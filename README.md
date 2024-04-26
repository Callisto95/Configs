# My Configs

Take what you need, everything is free. You may like it.

## Notes about some files

All files are either self explanatory (such as the files in `/etc/`), but for the others you really need to know what they're for. I try to name them appropriately, but some are not well named.

## Fancontrol

`fancontrol` must be configured by yourself. The config works *for me*, not for you.

## Solutions to some problems

Some problems require wild solutions, which is why I document them here.

### amdgpu crashes

The amdgpu driver seems to be quite bad when it comes to stability when undervolting. The kernel parameters in `/etc/default/grub` may fix them.

Some notes about my undervolting experience (I have a XFX Speedster 6900XT, your settings may vary):

- undervolting at -25 mV seems fine (@ 170W)
- currently running: -75 mV (@ 147W) - stable, no crashes yet
- unstable: -90 mV

### Flatpak's use wrong cursor

Some Flatpak's do not have a theme / theme loader included, which is why a completely different cursor theme us used. Technically, giving these apps access to `/usr/share/icons` would solve this, but the Flatpak team doesn't want that.

As a workaround it's possible to give all apps access to `$HOME/.icons/` and copy everything from `/usr/share/icons` into it. I have created a hook for that (see `etc/pacman.d/hooks/10-icons-sync.hook`).

### P10K: Python virtualenv shows name and version

I don't like the default way P10K shows the venv version (name *and* version). Thanks to Romkatv (creator of P10K) with the modified `POWERLEVEL9K_VIRTUALENV_CONTENT_EXPANSION` this is no longer the case (just the version).
