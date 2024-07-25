# Minecraft

## Wayland

I'm using an HDR display (although it's only HDR-10). Nonetheless I want to make use of it. Since X is, well X, it cannot handle it. Minecraft uses XWayland by default I had to change it.

The official Minecraft release bundles glfw (a rendering library), which defaults to XWayland. It's necessary to use a different version to enable pure Wayland.

While the official glfw package should be enough, that's not the case. The AUR package `glfw-wayland-minecraft-cursorfix` (NOT `-libdecor`) is required. The official package doesn't start, the libdecor version is nearly just black and white.

Then the glfw overwrite must be enabled. Check your launcher for details. I recommend Prismlauncher for this.

## Create and Shaders

**This is about the Fabric version, not the Forge one!**

Water wheel cause immense lag, even when just placed. Install `Iris Flywheel Compat`, run `/flywheel backend instancing`, then restart.
