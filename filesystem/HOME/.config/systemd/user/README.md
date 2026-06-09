# Systemd Service Files

## git-sync@

```bash
systemd-escape --path /FULL/PATH/TO/REPO
systemctl enable --now git-sync@[ESCAPED_PATH]
```
