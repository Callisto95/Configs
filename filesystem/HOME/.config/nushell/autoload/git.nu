def sc []: nothing -> nothing {
	clear
	git status
}
alias s = git status
alias gf = git fetch origin
alias gdf = git diff
alias gwdf = git diff --word-diff
alias gr = git reset
alias gck = git checkout
alias gg = git log --graph --oneline
alias glog = git log --oneline
# long variants
alias ggl = git log --graph
alias glogl = git log

def get_branch []: nothing -> string {
	let result = git rev-parse --abbrev-ref HEAD err> /dev/null | complete
	
	if $result.exit_code == 0 {
		return ($result.stdout | str trim -c "\n")
	}
	
	error make { msg: "not a git repository" }
	return null
}
def branch_exists []: string -> bool {
	let result = git ls-remote origin $in | complete
	
	not ($result.stdout | is-empty)
}
def gcm [...messages: string]: nothing -> nothing {
	let message = $messages | str join " "
	
	git commit -m $"($message)" | ignore
}
def ga [...files: string]: nothing -> nothing {
	if ($files | is-empty) {
		git add .
		return
	}
	
	$files | each { |file| git add $file } | ignore
}
def grst [...files: string]: nothing -> nothing {
	if ($files | is-empty) {
		git restore --staged .
		return
	}
	
	$files | each { |file| git restore --staged $file } | ignore
}
def gpu [remote?: string, --force (-f)]: nothing -> nothing {
	let remote = $remote | default "origin"
	
	if $force {
		git push $remote (get_branch) --force
	} else {
		git push $remote (get_branch)
	}
	git push $remote --tags
}
def gpl [remote?: string, --force (-f)]: nothing -> nothing {
	let remote = $remote | default "origin"
	
	if $force {
		git pull $remote (get_branch) --force
	} else {
		git pull $remote (get_branch)
	}
	git pull $remote --tags
}
