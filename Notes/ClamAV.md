# ClamAV

Before anything, read [the Arch Wiki](https://wiki.archlinux.org/title/ClamAV)

Now, section 2.2.1 has problems for me. The `notify-send` command hangs, even if the notification is closed. Add a `&` at the end of the command to prevent massive lockups of `clamd`.

`OnAccessMountPath` literally refers to mount paths. `clamd` will not scan beyond mount points, if not specified. (Most likely) put ALL mount points in there.
