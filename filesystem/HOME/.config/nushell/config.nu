# config.nu
#
# Installed by:
# version = "0.104.1"
#
# This file is used to override default Nushell settings, define
# (or import) custom commands, or run any other startup tasks.
# See https://www.nushell.sh/book/configuration.html
#
# This file is loaded after env.nu and before login.nu
#
# You can open this file in your default editor using:
# config nu
#
# See `help config nu` for more options
#
# You can remove these comments if you want or leave
# them for future reference.

use std/util "path add"

$env.config.buffer_editor = "kate"
$env.config.show_banner = false

$env.config.datetime_format.normal = "%Y-%m-%d %H:%M-%S"
$env.config.datetime_format.table = "%Y-%m-%d %H:%M-%S"

$env.config.display_errors.exit_code = true

# use 'keybinds listen'
$env.config.keybindings = [
	# CTRL + backspace
	{
		name: delete_word
		modifier: Control
		keycode: Char_h
		mode: emacs
		event: {
			edit: BackspaceWord
		}
	},
]

# better tab completions
# see env.nu -> must be generated before this file
# otherwise Nu refuses to load
source ~/.cache/carapace/init.nu

# change git remote from UnknownUser to Callisto
def updateGitRemote []: nothing -> nothing {
	let result = git rev-parse --is-inside-work-tree err> /dev/null | complete
	
	if $result.exit_code != 0 {
		print "not in a git repository"
		return null
	}
	
	git remote get-url origin | sed 's/UnknownUser/Callisto/g' | xargs git remote set-url origin
	
	print "URL updated, checking";
	git remote get-url origin
}

oh-my-posh init nu --config ~/.config/posh.json
