# Fancontrol

## Temperatures

There are temperatures with the same name, but *very* different functions. TSI from CPU is one such case. I have written them with `{index}` where a variable number can be (e.g. `TSI{inedx}_TEMP` can be `TSI0_TEMP`, `TSI1_TEMP`, ...).

### CPU

There are some choices:

- `Tctl` (temperature control index, not an actual sensor): A temperature index; fluctuates a lot, use averaging. **This one should be used.**
- on-die sensors (e.g. `Tccd1`): fluctuates massively and nearly instantly; not recommended.
- `CPUTIN`: sensor near the CPU on the motherboard. Lower accuracy, lower fluctuation.
- `SYSTIN` (system temperature index): In my case always stuck on one temperature. Use `Tctl` instead.
- TSI (`TSI{index}_TEMP`): CPU package temperature. `TSI0_TEMP` mirrors `SMBUSMASTER 0` on my machine, while `TSI1_TEMP` is static. Same usage as `Tctl`, but with real measurements. Should still not be used.

`CPUTIN`, while not fluctuating as much as `Tctl` for example, doesn't react fast enough to changes to the CPU temperature / load. It stays colder and warmer for far longer than what is actually happening.

### Other

- `AUXTIN{index}`: random sensors. Can apparently be PSU temperature, but are wildly incorrect. Simply ignore.
- SMBusMaster (`SMBUSMASTER {index}`): Either CPU or chipset temperature, depending the motherboard. CPU measurement has the same issues as `CPUTIN`.
- `PCH_CHIP_TEMP`: **Intel only:** South bridge (chipset) temperature. Has other variations as well (e.g. `PCH_CPU_TEMP`, `PCH_CHIP_CPU_MAX_TEMP`). If an AMD processor is present, always 0.
