# Git

## AutoSign commits with SSH key

- `user.signingkey` must point to your **private** ssh key. (`gh ssh-add` requires the public key)
- `commit.gpgSign` must be `true`
- `gpg.format` must be `ssh`
