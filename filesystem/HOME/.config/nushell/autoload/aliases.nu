alias mount-fstab = mount -a
alias cls = clear
alias df = df -h
alias oxipng = oxipng -preserve -fix
alias jpegoptim = jpegoptim --preserve
alias bandcamp-dl-album = bandcamp-dl --template '%{artist}/%{album}/%{title}'
alias bandcamp-dl-single = bandcamp-dl --template '%{artist}/%{album}/%{artist}-%{title}'
alias removeRating = setfattr -x user.baloo.rating
def restartPlasma []: nothing -> nothing {
	killall plasmashell
	kstart plasmashell
}
alias zipList = zipinfo -1
alias zipContent = zipinfo
alias dmesg = sudo dmesg --color=always | less -R

# Rust utils
alias cat = bat
#alias ls = eza # Nu's ls is a lot different
#alias find = fd # fd is very different
alias grep = rg
#alias curl = xh # XH is too different

alias pacFilesOfPackage = pacman -Ql
def pacPackageOfFile [file]: nothing -> nothing {
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
