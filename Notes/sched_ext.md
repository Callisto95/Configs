# sched_ext

> [!NOTE]
> CachyOS' inbuilt scheduler outperforms scx_lavd. If you're on CachyOS, don't change the scheduler.

`sched_ext` is a feature of the kernel to dynamically change the scheduler.

The script `scx.sh` is designed to better handle the calls to the `scx_loader` (installed with `scx-scheds`, must be enabled with systemctl).

## Schedulers

`scx_loader` comes with 3 schedulers: scx_bpfland, scx_rusty, and scx_lavd. As far as I can tell `scx_lavd` seems to be the best general purpose scheduler **for gaming**, which is why the scx script uses it by default.

## Verifying

`/sys/kernel/sched_ext/state` show the state (just enabled/disabled).

`/sys/kernel/sched_ext/root/ops` show the scheduler being used (note: root is currently the only user, which can change the scheduler, which is why they're in the path; this may change!).
