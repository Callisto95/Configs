# Zswap

The short form is, that zswap is compressed RAM. The linux-zen kernel has it enabled by default, but it uses ZSTD for compression.

ZSTD is fine. LZ4 is faster, while not compressing as much. This is why I use LZ4 instead of ZSTD, except for initcpio images, although there is very little difference between the two (~5MB).

## Check zswap

`cat /sys/module/zswap/parameters/*` gives you all current zswap options.

`/sys/module/zswap/parameters/enabled` should return `Y`, if zswap is enabled.

## initcpio

ZSTD is loaded by default. LZ4 is not. That means LZ4 has to be loaded *explicitly*. This can easily be done in `/etc/mkinitcpio.conf` within the `MODULES` setting.

I'm loading `lz4` and `lz4_compress`, because someone else did. All of the questions are years old though.

I'm also using the newer `zsmalloc` allocator, because it works better under low-memory situations, which is what zswap is for. `z3fold` is the common alternative. **Both have to loaded within initcpio explicitly**.

## Coniguration, you (maybe) want to change

`zswap.max_pool_percent`: The maximum amount of RAM zswap is allowed to use. The less RAM you have, the higher this value should be, although 70 seems to be a good maximum.
