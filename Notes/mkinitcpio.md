# mkinitcpio

## Compression

### Zstd

`zstd` is the default, however it uses single threaded mode by default. Change `COMPRESSION_OPTIONS=()` to `COMPRESSION_OPTIONS=(-T0)` to use multithreading.

### LZ4

The base lz4 compression is fine. Using `COMPRESSION_OPTIONS=(-9)` compresses the kernel more, without increasing the compression time too much (it's lz4, so it's very fast anyway).
