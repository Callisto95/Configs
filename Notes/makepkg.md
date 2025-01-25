# MakePKG

## Building options

### Multi-Threading

makepgk only uses a single thread by default, which causes compilation to take a long time.

By including `--jobs=$(nproc)` in `MAKEFLAGS`, multi-threading is enabled.

If using all threads is too annoying, because other applications become slow during compilation, use `MAKEFLAGS="--jobs=$(($(nproc)-2))"` the maximum amount of threads - 2.

### Native Packages

While not really necessary, using the `CFLAGS=-march=native -mtune=native` / `RUSTFLAGS="-C target-cpu=native"` options will optimize the package for your CPU (other flags excluded).

Not ideal for sharing the package, but I don't think you'll do that anyway.

## Compression

Compression is configured by the `PKGEXT` environment variable or the `PKGEXT` config option. This is literally the extension of the compressed file.

To change the compression algorithm used, change `PKGEXT` to e.g. `pkg.tar.lz4`.

`PKGEXT=pkg.tar` disabled compression altogether.

### Configuring Compression

Within `/etc/makepgk.conf` there is the system wide `PKGEXT`. The environment variable of `PKGEXT` takes precidence over the extension set in `/etc/makepgk.conf`.

The commands for compression are configured by `COMPRESS[algorithm]` (e.g. `COMPRESSLZ4` for lz4).
