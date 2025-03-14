# GH Cli

## Auth

Run `gh auth setup-git` to use the GitHub cli as your credential manager (for `github.com` repositories). This then configures `~/.gitconfig` for you, so you may want to back up (though it's not really necessary).

## Sign commits with SSH key

This references GitHub's `verified` status for commits.

Generate a key with the comment only containing your e-mail. Then use `gh ssh-key add [PUBLIC keyfile] --title "[name in GitHub UI]" --type "signing"`.

If a authentication key is needed, the use `--type authentication`.

For signing every commit, see `Git.md/Autosign commits`.
