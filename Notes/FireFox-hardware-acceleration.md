# FireFix hardware acceleration

Set `media.ffmpeg.vaapi.enabled` to `true`. This will not improve performance of VP9 videos, which is what YouTube uses in most cases.

**You have to use an extension to force H.264 codec.** This will reduce decode speed and efficiency massively.
