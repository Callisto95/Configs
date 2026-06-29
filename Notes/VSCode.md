# VSCode

## Code-OSS

My variant of using code. Since it's not a Microsoft branded release, the marketplace is severely lacking. Install both `code-marketplace` and `code-features` (both AUR) to unblock everything necessary.

> [!WARNING]
> This is not permitted as per the TOS of the code marketplace. Use with care.

### code-features

`code-features` should run with every update of VSCode, but sometimes it's not enough.

```bash
sudo code-features-update -s
```

to manually refresh.

## XDG Open With System

```bash
cd ~/.vscode/extensions/
git clone https://github.com/ottomated/vs-code-open-from-explorer.git
```

This adds a "Open with System" to the right click menu of every file. With this, you can open e.g. PDF's in Okular without opening the folder, then opening the file.

For some reason this extensions got pulled from the marketplace.
