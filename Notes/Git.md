# Git

## AutoSign commits with SSH key

- `user.signingkey` must point to your **private** ssh key. (`gh ssh-add` requires the public key)
- `commit.gpgSign` must be `true`
- `gpg.format` must be `ssh`

## Cherry-Pick

`git cherry-pick [hash1]..[hash2]` does **NOT** include commit [hash1]. Use `git cherry-pick [hash1]^..[hash2]`.

Then `git cherry-pick --continue`, go through all commits and fix conflicts.

`git cherry-pick --abort` to reset ALL changes made during the cherry-pick.
