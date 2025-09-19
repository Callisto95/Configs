# ZRAM

Zram is swap in RAM.

> [!WARNING]
> Do not use in conjunction with zswap
> It will work, but it's discouraged

Systemd has a `systemd-zram-generator`. See https://wiki.archlinux.org/title/Zram#Using_zram-generator for the config and usage.

> [!NOTE]
> `lz4hc` is supported

> [!NOTE]
> More than one compression algorithm can be given. Use `compression-algorithm=<ALG1> <ALG2>` for that.
> The first available will be used
