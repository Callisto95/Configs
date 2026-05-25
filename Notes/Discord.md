# Discord

## H.265 Videos aren't playing

By default, Discord won't play H.265 encoded videos. Use these launch options:

```bash
discord --enable-features=AcceleratedVideoDecodeLinuxGL,DefaultANGLEVulkan,VaapiIgnoreDriverChecks,Vulkan,VulkanFromANGLE --use-angle=vulkan --use-gl=angle
```
