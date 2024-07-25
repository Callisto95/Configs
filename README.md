# My Configs

Take what you need, everything is free. You may like it.

## Notes about some files

All files are either self explanatory (such as the files in `/etc/`), but for the others you really need to know what they're for. I try to name them appropriately, but some are not well named.

## Zsh

I have two Zsh config files: `.zshrc` and `.oh-my-zshrc`. The `.zshrc` file is for generic configuration, although it has some Oh-My-Zsh init code. The `.oh-my-zsh` file handles everything for Oh-My-Zsh.

Since a few plugins are packaged in Arch's packages, a link must be created in `$ZSH_CUSTOM` (`$HOME/.oh-my-zsh/custom`), which points to `/usr/share/zsh/plugins` (`$HOME/.oh-my-zsh/custom/plugins` -> `/usr/share/zsh/plugins`).

There is also `.zsh/zsh-config`, which has some old setup from Manjaro (I think). It has Zsh `setopt`'s as well as `bindkey`'s.

## Fancontrol

`fancontrol` must be configured by yourself. The config works *for me*, not for you!

## Other Notes

Within the `Notes` folder are various files about issues I wanted to write down.
