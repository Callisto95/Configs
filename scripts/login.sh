#!/bin/sh

sshkeys=("KEY1" "KEY2")

for key in "${sshkeys[@]}"; do
	ssh-add "$HOME/.ssh/$key"
done
