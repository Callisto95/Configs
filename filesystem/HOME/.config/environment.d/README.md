# Environment Variables

## KDE Plasma

For some unknown reason, Plasma doesn't take the `PATH` variable in `environment.d`, it must be set in `$HOME/.config/plasma-workspace/env/<file>.sh` via a `export PATH=/your/path` line.
