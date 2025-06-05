# Solutions to some problems

Some problems require wild solutions, which is why I document them here.

## amdgpu crashes

The amdgpu driver seems to be quite bad when it comes to stability when undervolting. The kernel parameters in `/etc/default/grub` may fix them.

Maybe the crashes came from a bad kernel? I have had very few crashes in recent times, even when using normal settings.

(I don't know where I measured the wattage, but all came from the same game)

Some notes about my undervolting experience (I have a XFX Speedster 6900XT, your settings may vary):

- undervolting at -25 mV seems fine (@ 170W)
- -75 mV (@ 147W), -70: meta-stable: very few crashes, but crashes nonetheless
- current: -60 mV: seems stable
- unstable: -90 mV

Maybe having other GPU accelerated apps open causes instability? FireFox and YouTube while playing seems to crash more, however this may just be pure speculation.

## P10K: Python virtualenv shows name and version

> [!NOTE]
> P10K has ceased development, use Oh-My-Posh.

I don't like the default way P10K shows the venv version (name *and* version). Thanks to Romkatv (creator of P10K) with the modified `POWERLEVEL9K_VIRTUALENV_CONTENT_EXPANSION` this is no longer the case (just the version).

## OS Error 24: Too many open files

`ulimit -n [amount]` changes the amount of allowed open files within the **current** shell. The values can be seen via `ulimit -Hn` (hard limit) and `ulimit -Sn` (soft limit).

Changing it permanently can be done in `/etc/security/limits.conf`: `* hard nofile [amount]`.

## Feral Interactive Gamemode

Run `gamemoded -t` to test gamemode. If you get errors renicing threads, you have to change `/etc/security/limits.d/10-gamemode.conf` (create the file if needed).

It's required to change the limits of the gamemode group. Add `@gamemode - nice -20` (or any max nice value) and reboot.

## Font rendering in KDE

Use full hinting. Everything else leads to worse rendering. (May be different on 4K screens)

## Invalid database signature

The CachyOS admin key seems to be problematic (at least for me). I now had two occurences, where it corrupted (or something).

```
Signature from "X <x@x.com>" is invalid
error: database 'core' is not valid (invalid or corrupted database (PGP signature))
```

The easiest way: refresh the mirrorlist, then run `sudo pacman -Syu archlinux-keyring && sudo pacman -Syyu`

I vaguely remember a second way:

```bash
sudo rm -rf /etc/pacman.d/gnupg/
sudo gpg --refresh-keys
sudo pacman-key --init
sudo pacman-key --populate archlinux
```

Also from a Reddit thread:

```bash
sudo rm -rf /var/lib/pacman/sync
sudo pacman -Syyu
```

## Application overrides

Instead of editing applications in `/usr/share/applications/`, copy the file to `~/.local/share/applications/`, then make your edits.

Your user setting will take priority over the system defaults.

KDE: If you have a shortcut to that application, it is required to remove and set it again. Otherwise the original application is started. This is also required if the `.desktop` file is modified. KDE keeps the old version.
