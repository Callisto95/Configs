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
if [[ -e $HOME/.zsh/zsh-prompt ]]; then
	source $HOME/.zsh/zsh-prompt
fi

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
if [[ -f ~/.p10k.zsh ]]; then
	source ~/.p10k.zsh
fi

# change ENV vars
export DEBUG=""

# aliases
alias cls='clear'
alias ex="exit"

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
gcm() {
	git commit -m "$*"
}
gacm() {
	if [[ $# == 0 ]]; then
		git commit --amend -m "$(git log --format=%B -n 1 HEAD)"
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
		if [[ -f "$file" ]] || [[ -d "$file" ]] || [[ "$file" == *\** ]]; then
			git add "$file"
		else
			echo "'$file' is not a file"
		fi
	done
}
grst() {
	if [[ $# -eq 0 ]]; then
		git reset --staged .
		return 0
	fi

	for file in $*; do
		if [[ -f "$file" ]] || [[ -d "$file" ]] || [[ "$file" == *\** ]]; then
			git restore --staged $file
		else
			echo "'$file' is not a file"
		fi
	done
}
gpu() {
	if [[ "$1" == "-f" ]]; then
		git push origin $(get_branch) -f
	elif [[ "$1" != "" ]]; then
		git push origin "$1"
	else
		git push origin $(get_branch)
	fi
	git push origin --tags
}
gpl() {
	git fetch;
	
	if [[ $1 != "" ]]; then
		git pull origin $1
	else
		git pull origin $(get_branch)
	fi
}
gbr() {
	if [[ $1 != "" ]]; then
		git checkout -b "$1"
	else
		git branch -a
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
