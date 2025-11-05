# clear, then git status
def sc []: nothing -> nothing {
	clear
	git status
}
# git status
alias s = git status
# git fetch
alias gf = git fetch
# git diff
def gdf [a: string = ".", b?: string] {
	# workaround: force less (delta's pager) to enable alternate screen buffer
	
	if $b == null {
		git diff . | delta;
	} else {
		git diff $a $b;
	}
}
#alias gdf = git diff
# git word diff
def gdfw [] {
	git diff --word-diff --color=always | delta
}
#alias gdfw = git diff --word-diff
# git reset
alias gr = git reset
# git one-line graph
alias gg = git log --graph --oneline
# git graph - long
alias ggl = git log --graph
# git log one-line
alias glog = git log --oneline
# git log - long
alias glogl = git log

# get current branch
def get_branch []: nothing -> string {
	let result = git rev-parse --abbrev-ref HEAD err> /dev/null | complete
	
	if $result.exit_code == 0 {
		return ($result.stdout | str trim -c "\n")
	}
	
	error make { msg: "not a git repository" }
	return null
}
# check if given branch exists
def branch_exists []: string -> bool {
	let result = git branch --list $in | complete
	
	not ($result.stdout | is-empty)
}
# git checkout or create new branch
def gck [branch:string]: nothing -> nothing {
	if ($branch | branch_exists) {
		git checkout $branch
	} else {
		git checkout -b $branch
	}
}
# git commit with message
def gcm [...message: string]: nothing -> nothing {
	git commit -m ($message | str join " ")
}
# git amend to commit with optional message
def gacm [...message: string]: nothing -> nothing {
	if ($message | is-empty) {
		git commit --amend --no-edit
	} else {
		git commit --amend -m ($message | str join " ")
	}
}
# git add files or current dir
def ga [...files: string]: nothing -> nothing {
	if ($files | is-empty) {
		git add .
		return
	}
	
	$files | each { |file| git add $file } | ignore
}
# git restore files or current dir
def grst [...files: string]: nothing -> nothing {
	if ($files | is-empty) {
		git restore --staged .
		return
	}
	
	$files | each { |file| git restore --staged $file } | ignore
}
# git push
def gpu [remote?: string, --force (-f)]: nothing -> nothing {
	let remote = $remote | default "origin"
	
	if $force {
		git push $remote (get_branch) --force --tags
	} else {
		git push $remote (get_branch) --tags
	}
}
# git pull
def gpl [remote?: string, --force (-f)]: nothing -> nothing {
	let remote = $remote | default "origin"
	
	if $force {
		git pull $remote (get_branch) --force --tags
	} else {
		git pull $remote (get_branch) --tags
	}
}
def git_delta_variants [] { [ "file", "vscode", "idea", "pycharm", "clion" ] }
# git delta change link embed mode
def gitDeltaMode [mode: string@git_delta_variants]: nothing -> nothing {
	if $mode == "file" {
		git config delta.hyperlinks-file-link-format "file://{path}"
	} else if $mode == "vscode" {
		git config delta.hyperlinks-file-link-format "vscode://file/{path}:{line}"
	} else if $mode == "idea" {
		git config delta.hyperlinks-file-link-format "idea://open?file={path}&line={line}"
	} else if $mode == "pycharm" {
		git config delta.hyperlinks-file-link-format "pycharm://open?file={path}&line={line}"
	} else if $mode == "clion" {
		git config delta.hyperlinks-file-link-format "clion://open?file={path}&line={line}"
	}
}
