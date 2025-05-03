# ClamAV

Before anything, read [the Arch Wiki](https://wiki.archlinux.org/title/ClamAV)

Now, section 2.2.1 has problems for me. The `notify-send` is configured to wait until the notification is closed. This will cause `clamd` to hang. Remove the `-w` flag.

`OnAccessMountPath` literally refers to mount paths. `clamd` will not scan beyond mount points, if not specified. (Most likely) put ALL mount points in there.
