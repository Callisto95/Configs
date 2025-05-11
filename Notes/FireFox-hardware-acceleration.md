# FireFix hardware acceleration

Set `media.ffmpeg.vaapi.enabled` to `true`. This will not improve performance of VP9 videos, which is what YouTube uses in most cases.

> [!IMPORTANT]
> You have to use an extension to force H.264 codec.

This will increase decode speed and efficiency massively.

However a video may get stuck on a particular frame and when skipping may wait on a frame in the future.
