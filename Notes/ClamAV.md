# ClamAV

Before anything, read [the Arch Wiki](https://wiki.archlinux.org/title/ClamAV)

Now, section 2.2.1 has problems for me. The `notify-send` is configured to wait until the notification is closed. This will cause `clamd` to hang. Remove the `-w` flag.

`OnAccessMountPath` literally refers to mount paths. `clamd` will not scan beyond mount points, if not specified. (Most likely) put ALL mount points in there.

## Caviats

ClamAV reports a lot of false postives and uses quite a bit of RAM and CPU.

False postives are especially common when using heuristic detection.

Either a lot of time has to be used to configure it correctly, or it **will** report many false postives.
