# CNC X/Y axis swap (SLB-EXT, wall mount)

Start here: [xy-swap-instructions.md](xy-swap-instructions.md). It refers to files in `C:\downloads`. The same files are in this repo:

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
