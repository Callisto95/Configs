# Pacman (ppackage manager)

Most of these notes disable checks, **USE WITH CAUTION!**

## [file] exists in both [package a] and [package b]

Use `--overwrite [file]` to skip conflict checks for that file. 

## Remove package, but break dependency

`pacman -Rdd` disables dependency checks.

## Parallel Downloads

Set `ParallelDownloads` in the config.
