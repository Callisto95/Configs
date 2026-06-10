# Internet Stuff

This is all for NetworkManager!

## Set Static IPv6

```bash
nmcli con mod "Wired connection 1" ipv6.addr-gen-mode eui64 ipv6.token ::1
nmcli con up "Wired connection 1"
```
