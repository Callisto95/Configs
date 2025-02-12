# Minecraft

## Wayland

I'm using an HDR display (although it's only HDR-10). Nonetheless I want to make use of it. Since X is, well X, it cannot handle it. Minecraft uses XWayland by default I had to change it.

The official Minecraft release bundles glfw (a rendering library), which defaults to XWayland. It's necessary to use a different version to enable pure Wayland.

While the official glfw package should be enough, that's not the case. The AUR package `glfw-wayland-minecraft-cursorfix` (NOT `-libdecor`) is required. The official package doesn't start, the libdecor version is nearly just black and white (I had that happen with `-cursorfix` as well, but tabbing out and back in fixed it).

**DO NOT INSTALL THE `glfw-wayland-minecraft-cursorfix` package globally. It decreases XWayland performance significantly.**

Instead make the package (just `makepgk`, not `makepgk -i` / `makepgk -si`), extract the `libglfw.so` file and use that as your glfw library.

Then the glfw overwrite must be enabled. Check your launcher for details. I recommend Prismlauncher for this.

## Borderless Mods

(At least) the mod (Borderless Fullscreen)[https://modrinth.com/mod/borderless-fullscreen] breaks GLFW stuff. Completely unusable.

(Cubes Without Borders)[https://modrinth.com/mod/cubes-without-borders] works fine.

## Create and Shaders

**This is about the Fabric version, not the Forge one!**

Water wheel cause immense lag and weird rendering issues, even when just placed. Install `Iris Flywheel Compat`, run `/flywheel backend instancing`, then restart.

## Distant Horizons on Servers

This is not officially supported, but you can link `Distant_Horizons_server_data/[server name]/[level]/DistantHorizons.sqlite` to a local worlds' `DistantHorizons.sqlite`. That way you can generate your own LOD's and load them when on the server.

Obviously modified terrain is not in the LOD's, but is updated when it's loaded on the server.
