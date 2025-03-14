#!/bin/sh

func () {
	ssh-add -D;
	
	sshkeys=("fujitsu-admin" "fujitsu-fabric" "fujitsu-steam" "github-sign")
	
	for key in "${sshkeys[@]}"; do
		ssh-add "$HOME/.ssh/$key" &
	done
	
	curl -s https://github.com > /dev/null 2> /dev/null;
	
	while [[ $? -ne 0 ]];
	do
		sleep 5;
		curl -s https://github.com > /dev/null 2> /dev/null;
	done
	
	LOGSEQ_LOG_FILE="$HOME/scripts/logseq-sync.log";
	LOGSEQ_SETTING_SYNC_LOG_FILE="$HOME/scripts/logseq-setting-sync.log";
	echo "Login $(date '+%F %R'):" >> "$LOGSEQ_LOG_FILE";
	echo "Login $(date '+%F %R'):" >> "$LOGSEQ_SETTING_SYNC_LOG_FILE";
	
	git -C "$HOME/Documents/logseq-TU-BS" pull origin main >> "$LOGSEQ_LOG_FILE" 2>> "$LOGSEQ_LOG_FILE";
	
	if [[ $? -ne 0 ]]; then
		notify-send --app-name="LogSeq Sync" --urgency="critical" --icon="logseq" "Sync failed!";
	fi
	
	git -C "$HOME/.logseq" pull origin main >> "$LOGSEQ_SETTING_SYNC_LOG_FILE" 2>> "$LOGSEQ_SETTING_SYNC_LOG_FILE";
	
	if [[ $? -ne 0 ]]; then
		notify-send --app-name="LogSeq Setting Sync" --urgency="critical" --icon="logseq" "Setting Sync failed!";
	fi
}

func &
