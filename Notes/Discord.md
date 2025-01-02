# Discord

**I use Vesktop, not base Discord! Check your client for solutions!**

## Screenshare

**Discord Canary has massively improved and working screen share! Check if these updates have been applied!**

Discord screen share is broken. If the stream is started, a black screen is the only thing that is streamed.

Furthermore, if started from a terminal, Vesktop prints a lot of error messages:

```
[44568:0102/014719.253596:ERROR:gbm_pixmap_wayland.cc(82)] Cannot create bo with format= YUV_420_BIPLANAR and usage=SCANOUT_CPU_READ_WRITE
[44568:0102/014719.253693:ERROR:gpu_channel.cc(503)] Buffer Handle is null.
```

Add `--disable-gpu-memory-buffer-video-frames` to `$XDG_CONFIG_HOME/vesktop-flags.conf` (most likely `~/.config/vesktop-flags.conf`).

**However**, both

```
--disable-features=UseMultiPlaneFormatForSoftwareVideo
--disable-features=UseMultiPlaneFormatForHardwareVideo
```

cause issues with the stream. Near unwatchable artifacts, but then back to black screen.

(I'm mentioning this, because some issue threads mention these as solution)
