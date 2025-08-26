# remount based on /etc/fstab
alias mount-fstab = mount -a
# clear screen
alias cls = clear
# df, human readable
alias df = df -h
alias oxipng = oxipng --preserve --fix
alias jpegoptim = jpegoptim --preserve
alias bandcamp-dl-album = bandcamp-dl --template '%{artist}/%{album}/%{title}'
alias bandcamp-dl-single = bandcamp-dl --template '%{artist}/%{album}/%{artist}-%{title}'
# remove KDE's rating
alias removeRating = setfattr -x user.baloo.rating
# kill, then restart PlasmaShell
def restartPlasma []: nothing -> nothing {
	killall plasmashell
	kstart plasmashell
}
# only get files within zip
alias zipList = zipinfo -1
# dmesg, but colours
def dmesg []: nothing -> nothing {
	sudo dmesg --color=always | less -R
}

# Rust utils

# bat instead of cat
alias cat = bat
# RipGrep instead of grep
alias grep = rg

#alias ls = eza # Nu's ls is a lot different
#alias find = fd # fd is very different
#alias curl = xh # XH is too different

# list all files provided by the package
alias pacFilesOfPackage = pacman -Ql
# get the package of the given file
def pacPackageOfFile [file: string]: nothing -> nothing {
	if ($file | path exists) {
		pacman -Qo $"($file)"
		return
	}
	
	print $"file '($file)' does not exist, assuming it's an app"
	
	let commands = which $file
	
	if not ($commands | is-empty) {
		pacPackageOfFile $commands.0.path
	} else {
		print "command not found"
	}
}
# generate a password with the given length
def generatePassword [length: int = 64, --no-copy]: nothing -> string {
	let password: string = open /dev/urandom | tr -dc ";,.\"\'-={}[]()123456789\\\\/!@#$%abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" | head $"-c($length)"
	if not $no_copy {
		wl-copy -n $password
	}
	$password
}
