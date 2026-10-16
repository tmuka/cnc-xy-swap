# CNC X/Y axis swap (SLB-EXT, wall mount)

Swapping the X and Y axes on a wall-mounted grblHAL machine, so that X is the dual-motor auto-squared gantry and Y is the vertical axis, with the home corner unchanged. Done and tested on 2026-10-15 (homing, jogging, ATC tool changes).

## The machine

This started as a **[Onefinity](https://www.onefinitycnc.com) X-50 Journeyman**. It was later upgraded with a **[Sienci](https://sienci.com) SLB-EXT** ([grblHAL](https://github.com/grblHAL)) controller and **Sienci AltMill** hybrid stepper motors (closed-loop, with integrated drivers) and limit switches. It's wall mounted, runs **[ncSender](https://ncsender.xyz) Pro** on a Raspberry Pi 5, and has a [Rapid Change ATC](https://rapidchangeatc.com/) and a toolsetter.

**The settings, offsets, firmware and backups in this repo apply only to this machine.** Steps/mm, travel, directions, keep-out zones, ATC positions and work offsets all depend on its frame, motors, drivers and wiring. Don't flash the `.hex` or send the `$` settings to another machine as-is.

## What may help others

The process carries over to other machines more than the numbers do. If you're swapping or reassigning axes on a grblHAL board (especially a ganged/auto-squared axis), see:

- [xy-swap-instructions.md](xy-swap-instructions.md): the full procedure. It covers the safe order (settings before rewiring, no motion until the switches are tested), rewiring at the SLB-EXT, switch and jog tests, homing, and converting the sender config, macros and work offsets.
- [CLAUDE.md](CLAUDE.md): the working notes from doing this with Claude Code. They cover what was checked against the grblHAL source (motor numbering for ganged axes, `$8`/`$3` interaction, the shared enable pin behind `$37`), web builder pitfalls (vendor profile duplicating defaults and dropping plugins), and problems hit along the way.
- [converted/swap_ncs.py](converted/swap_ncs.py): an example of converting an ncSender backup to new axes (new X = -old Y, new Y = old X).

Lessons that came up during the swap:
- Confirm the new firmware actually took (`$I` build date and `$PINS`) before changing settings. The first flash attempt failed silently.
- [Flashing from ncSender](https://docs.ncsender.xyz/settings/firmware/) on Linux/Raspberry Pi needs a udev rule for the STM32 DFU device (`0483:df11`), or the flash fails with "insufficient permissions":
  ```
  SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="df11", MODE="0664", GROUP="plugdev", TAG+="uaccess"
  ```
  Save it as `/etc/udev/rules.d/50-stm32-dfu.rules`, then run `sudo udevadm control --reload-rules && sudo udevadm trigger`.
- The firmware Sienci ATCi keep-out zone blocked the Rapid Change ATC from entering the rack, so it was turned off (`$683`). [ncSender's own keep-out zone](https://docs.ncsender.xyz/features/keepout-zone/), which plugins can bypass, is the alternative.

## Files

The instructions refer to files in `C:\downloads`. The same files are in this repo:

| File | Contents |
|---|---|
| `original/STM32F4xx_LONGBOARD32_EXT.json` | Web builder config before the change (was `STM32F4xx_LONGBOARD32_EXT (1).json`) |
| `original/firmware-settings-2026-10-15.txt` | `$$` backup before the change |
| `original/ncsender-backup-tsmcnc5-20261015-194447.ncsbackup` | ncSender backup before the change |
| `converted/STM32F4xx_LONGBOARD32_EXT_XY_swapped.json` | Web builder config to flash (X ganged + auto-square) |
| `converted/builder-export-verified.json` | Web builder's own Save-board export, checked to match the intended config. This is the state to generate firmware from. |
| `original/offsets-2026-10-15.txt` | `$#` work offsets before the change |
| `converted/work-offsets-after-swap.txt` | G10 commands setting G54-G59 in the new axes, plus `G92.1` |
| `converted/firmware-xy-swap-20261015.hex` | Firmware built from the verified builder state. This is the file to flash. |
| `converted/xy-swap-commands.txt` | The 11 `$` settings to send after flashing |
| `converted/full-settings-after-swap.txt` | All settings with the swap applied. Use only if flashing reset settings to defaults. |
| `converted/ncsender-backup-tsmcnc5-XY-swapped.ncsbackup` | ncSender backup to restore after the change |
| `converted/swap_ncs.py` | Script that produced the converted ncSender backup |
| `CLAUDE.md` | Handoff notes for continuing with Claude Code |

Web builder: https://svn.io-engineering.com:8443/index.html
