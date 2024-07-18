# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
	source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# enable Oh-My-Zsh
source $HOME/.oh-my-zshrc

# Use powerline
USE_POWERLINE="true"
# Source zsh-configuration
if [[ -e $HOME/.zsh/zsh-config ]]; then
	source $HOME/.zsh/zsh-config
fi

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
if [[ -f ~/.p10k.zsh ]]; then
	source ~/.p10k.zsh
fi

# these cannot be in environment.d
PATH="$HOME/custom_commands:$HOME/.cargo/bin:$PATH";
LS_COLORS='rs=0:fi=38;5;2:di=01;34:ln=01;38;2;255;255;0:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32;48;2;128;52;190:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.swp=00;90:*.tmp=00;90:*.dpkg-dist=00;90:*.dpkg-old=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:'

# keep HISTFILE from adding timestamps
echo "" > "$HOME/.oh-my-zsh/lib/history.zsh"

# generic aliases
alias cls="clear"
alias ex="exit"
alias ls="eza"
alias df="df -h" # human readable
alias cat="bat"
alias removeRating="setfattr -x user.baloo.rating"
restartPlasma() {
	killall plasmashell;
	kstart plasmashell;
}
alias listZip="zipinfo -i"
alias zipContent="zipinfo"
alias dmesg="sudo dmesg --color=always | less -R"
alias cjxl="cjxl -q 100 -e 7"


# pacman
# Q -> F for remote packages
# +q for names only
alias pacFilesOfPackage="pacman -Ql"
alias pacPackageOfFile="pacman -Qo"
alias pacFullRm="pacman -Rsn"
alias pacAllOrphans="pacman -Qdt"

# git
get_branch() {
	branch=$(git rev-parse --abbrev-ref HEAD 2> /dev/null)
	if [[ $? -eq 0 ]]; then
		echo $branch
	else
		echo "not a git repo"
		return 1
	fi
}
branch_exists() {
	if [[ $(git ls-remote origin "$1") == "" ]]; then
		# branch doesn't exist
		echo 1
	else
		# branch exists
		echo 0
	fi
}
gcm() {
	git commit -m "$*"
}
gacm() {
	if [[ $# == 0 ]]; then
		git commit --amend --no-edit
	else
		git commit --amend -m "$*"
	fi
}
ga() {
	if [[ $# -eq 0 ]]; then
		git add .
		return 0
	fi

	for file in $*; do
		git add "$file"
	done
}
grst() {
	if [[ $# -eq 0 ]]; then
		git reset --staged .
		return 0
	fi

	for file in $*; do
		git restore --staged $file
	done
}
gpu() {
	if [[ "$1" == "-f" ]]; then
		git push origin $(get_branch) --force
	elif [[ "$1" != "" ]]; then
		git push origin "$1"
	else
		git push origin $(get_branch)
	fi
	
	# also push tags
	git push origin --tags
}
gpl() {
	if [[ $1 != "" ]]; then
		git pull origin $1
	else
		git pull origin $(get_branch)
	fi
	
	# also "pull" tags
	git fetch --tags;
}
gbr() {
	if [[ "$1" == "" ]]; then
		git --no-pager branch --all
	elif [[ "$1" == "-d" ]]; then
		git branch --delete "$2"
	else
		if [[ $(branch_exists "$1") -eq 0 ]]; then
			git checkout "$1"
		else
			git checkout -b "$1"
		fi
	fi
}
alias sc="clear && git status"
alias s="git status"
alias gf="git fetch origin"
alias gdf="git diff"
alias gr="git reset"
alias gck="git checkout"
alias glog='git log --graph'

# python
alias act="source ./venv/bin/activate"
alias nvenv="python -m venv venv"
alias py="python"
