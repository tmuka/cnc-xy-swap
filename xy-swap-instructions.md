# SLB-EXT X/Y axis swap (wall-mounted machine)

Files (repo path / original location in `C:\downloads`):

| Purpose | Repo | Downloads |
|---|---|---|
| Firmware `$$` backup (before) | `original/firmware-settings-2026-10-15.txt` | same name |
| Builder config (before) | `original/STM32F4xx_LONGBOARD32_EXT.json` | `STM32F4xx_LONGBOARD32_EXT (1).json` |
| ncSender backup (before) | `original/ncsender-backup-tsmcnc5-20261015-194447.ncsbackup` | same name |
| Builder config to flash | `converted/STM32F4xx_LONGBOARD32_EXT_XY_swapped.json` | same name |
| The 11 setting changes | `converted/xy-swap-commands.txt` | same name |
| Every setting, already swapped (use only if flashing reset your settings) | `converted/full-settings-after-swap.txt` | same name |
| ncSender backup to restore | `converted/ncsender-backup-tsmcnc5-XY-swapped.ncsbackup` | same name |

## Goal

|                | Before                          | After                            |
|----------------|---------------------------------|----------------------------------|
| Vertical axis (single motor)   | X, + = up, 1230 mm  | **Y**, + = up, 1230 mm           |
| Horizontal gantry (two motors) | Y, + = left, 812 mm | **X**, + = right, 812 mm         |
| Home corner    | bottom-left                     | bottom-left (no switches move)   |
| Machine coords | X 0..+1230, Y -812..0           | X 0..+812, Y 0..+1230            |

Coordinate conversion used everywhere: **new X = -(old Y), new Y = old X**, Z unchanged.

Confirmed starting point: today +X moves **up** and +Y moves **left**. The direction and homing values below are based on this.

## Order of work (summary)

1. Record what the machine has now (`$$`, `$#`, SD card files).
2. Flash the new firmware. **Don't move or home anything yet.**
3. Send the settings and check them with `$$`.
4. Power off and rewire.
5. Test switches, then jog, then home, then the ATC, then an air cut.
6. Restore the converted ncSender backup.

Nothing moves until step 5, so a mistake in steps 2-4 can't crash the machine.

## 1. Before you start

1. Make sure the `$$` output still matches `original/firmware-settings-2026-10-15.txt`. If you changed anything since, redo the conversion.
2. Send `$#` and save the output. It holds the work offsets (G54-G59), G28/G30 positions, G92 and the tool-length offset. These are **not** in `$$`, are in old coordinates, and need re-setting after the swap.
3. If you keep macros or `.nc`/`.macro` files on the controller's SD card that move to machine (`G53`) X/Y positions, list them. They need converting too. Nothing in this pack covers them.
4. Have a way to stop the machine within reach (E-stop) for every motion step.

## 2. Flash the firmware

1. Load `STM32F4xx_LONGBOARD32_EXT_XY_swapped.json` in the web builder, build and flash.
   - The only firmware change is `Y_AUTO_SQUARE=1` -> `X_AUTO_SQUARE=1`. grblHAL turns X ganging on automatically when X auto-square is set.
   - Checked against the grblHAL source (motor_pins.h): with 4 axes + 1 ganged there are 5 motors, and the ganged axis always takes the highest motor number (M4 = the board's Y2 connector). A stays on M3 (the A connector). This is the same arrangement Y2 uses today.
2. After flashing, connect and send `$$`. **Compare it with your backup before doing anything else.**
   - Normally the stored settings survive a flash, and only the 11 values below need changing.
   - If the settings were reset to builder defaults (for example, Z steps/mm shows 200 instead of 80.13, or rates/accelerations changed), paste all of `converted/full-settings-after-swap.txt`. It is your full backup with the swap already applied, minus the read-only MAC address line. An error on a single line (a setting the new firmware doesn't have) is harmless, but read any error that appears.
3. Don't home or jog yet. The machine is still wired the old way, and the settings below aren't in yet.

## 3. Settings to change

Send each line in the console, or paste `xy-swap-commands.txt`. Then send `$$` and check every value.

| Setting | Meaning                       | Old       | New        | Why |
|---------|-------------------------------|-----------|------------|-----|
| `$100`  | X steps/mm                    | 200.40000 | **80.20001**  | gantry drive is now X |
| `$101`  | Y steps/mm                    | 80.20001  | **200.40000** | vertical drive is now Y |
| `$130`  | X max travel                  | 1230.000  | **812.000**   | gantry travel |
| `$131`  | Y max travel                  | 812.000   | **1230.000**  | vertical travel |
| `$3`    | Step direction invert         | 6 (Y,Z)   | **4** (Z)     | gantry was + = left, now + = right; vertical stays + = up |
| `$23`   | Homing direction invert       | 1 (X)     | **3** (X,Y)   | both axes home toward negative (left / bottom), so the physical home corner is unchanged |
| `$37`   | Steppers kept enabled         | 1 (X)     | **3** (X,Y)   | after an alarm, keeps the vertical axis powered so it can't drop. X is included because the 2nd gantry motor shares Y's enable signal (pin PC7). With Y only, one side of the gantry would be held and the other free. |
| `$684`  | Keep-out X min                | 750.00    | **700.00**    | was Y -850..-700 |
| `$685`  | Keep-out Y min                | -850.00   | **750.00**    | was X 750..1230 |
| `$686`  | Keep-out X max                | 1230.00   | **850.00**    | |
| `$687`  | Keep-out Y max                | -700.00   | **1230.00**   | |

### Checked, no change needed
- `$110/$111` max rate (15000 both), `$120/$121` accel (700 both)
- `$160/$161` backlash, `$170/$171` dual-axis offset, `$180/$181` homing feed, `$190/$191` homing seek: same values on both axes
- `$5=15` limit invert: covers X and the X2 (squaring) switch, which uses the X bit
- `$744=7` / `$745=15` motor faults: X, Y and Z enabled. The gantry's second driver alarm now reports as X instead of Y.
- `$8=0` ganged direction invert: grblHAL applies it relative to the main motor after `$3` (driver.c), and the same two gantry motors are still ganged
- `$22`, `$27`, `$44=4` / `$45=3` homing cycles (Z first, then X and Y together)
- `$56-$59` parking (Z only), `$770/$771` spindle offset (both 0), `$490-$492` controller macros (empty)

### Settings worth knowing about (not changed)
- `$20=0` soft limits and `$21=0` hard limits are **off** on your machine, both before and after. Only **jogging** is limited to the travel (`$40=1`). A G-code program with a wrong coordinate will still drive into the end stops. That's why the converted macros and ATC positions are tested with Z raised first (step 5).

## 4. Rewire (power off)

| Item                          | Connect to             |
|-------------------------------|------------------------|
| Vertical motor's driver cable | **X** -> **Y** connector |
| Vertical limit switch         | **X** -> **Y** limit input |
| Gantry motor 1's driver cable | **Y** -> **X** connector |
| Gantry limit switch 1         | **Y** -> **X** limit input |
| Gantry motor 2                | Y2 connector, **unchanged** |
| Gantry limit switch 2         | Y2 limit input, **unchanged** |

**Important on the EXT board:** swap the **controller-to-driver signal cables** (step/dir/enable/alarm) at the SLB-EXT. Keep each motor wired to its own external driver. Each driver's microstep and current settings belong to its motor, and the very different steps/mm (200.4 vs 80.2) depend on them. Swapping motor wires at the driver outputs would put the wrong current and microstepping on each motor.

If the driver alarm/fault wires are separate from the motor cable, swap them along with the cables. They should follow their driver.

## 5. First power-up and tests

Keep the bit out (or Z fully retracted) and stay at the E-stop.

### 5a. Status check (no motion)
1. Power on and connect. Send `$$` and confirm the 11 values above.
2. The controller will probably start in alarm (homing required). Don't home yet.
3. Trigger each limit switch by hand and watch the status `Pn:` field (or ncSender's limit indicators):
   - Vertical switch -> must show **Y**
   - Gantry switch 1 -> must show **X**
   - Gantry switch 2 (Y2 input) -> should also show **X** (it's now the X squaring switch). If it shows nothing, check with ncSender's limit indicators. It must not show Y.
   - If a switch shows the wrong letter, fix the wiring before going on.

### 5b. Jog test (small moves, before homing)
1. Send `$X` to unlock.
2. Make sure there's clear room in every direction, then jog **1-10 mm** at a time:
   - +X -> gantry moves **right**; -X -> left
   - +Y -> spindle moves **up**; -Y -> down
   - Both gantry motors must move together. If one side moves the opposite way or the gantry racks or buzzes, **stop immediately** and set `$8=1`.
   - The directions are confirmed, so a reversal points to a wiring mix-up. Recheck the cables first. As a last resort: gantry the wrong way: `$3=5`. If the vertical axis goes the wrong way: `$3=6`. Fix the direction before homing, or homing will drive away from the switches.
   - A jog that is refused with a travel error before homing is normal (the position isn't known yet). Jog the other way first.

### 5c. Homing
1. `$H`: Z retracts first. Then the gantry moves **left** onto both X switches and squares, and the vertical axis moves **down** to its switch.
2. If any axis moves away from its switch, stop it (E-stop/reset) and recheck `$23`.
3. After homing, the position should read X0 Y0, and jogging to the far corner should stop near X 812 / Y 1230.

## 6. ncSender

Restore `converted/ncsender-backup-tsmcnc5-XY-swapped.ncsbackup` **after** the firmware swap. It replaces all ncSender settings with your Oct 15 backup, converted.

| Item | Old | New |
|---|---|---|
| Home location (display) | back-left | **front-left** (ncSender: X home = min, Y home = min) |
| Parking location | 663.243, -440.175, -5.004 | **440.175, 663.243, -5.004** |
| Keep-out zone (disabled in ncSender) min / max | (700, -812) / (1155, -690) | **(690, 700) / (812, 1155)** |
| Rapid Change ATC orientation / direction | X / Negative | **Y** / Negative |
| Rapid Change ATC pocket 1 | 1197.1909, -811.79416 | **811.79416, 1197.1909** |
| Rapid Change ATC toolsetter | 829.00012, -810.99914 | **810.99914, 829.00012** |
| Rapid Change ATC manual tool | 107.82808, -640.08762 | **640.08762, 107.82808** |
| Manual Tool Changer pocket 1 / toolsetter / parking (plugin disabled) | (883,-811) / (829,-811) / (107.829,-640.087) | **(811,883) / (811,829) / (640.087,107.829)** |

Z values (engagement, zones, toolsetter Z, safe Z) are unchanged.

Checked against the plugin source: Rapid Change ATC goes to each pocket with plain `G53 G0 X.. Y..` moves, and pocket n = pocket 1 Y - (n-1) x 45.001. So pocket 8 is at Y 882.18, which matches macro 9004.

Macros:

| Macro | Old | New |
|---|---|---|
| 9002 goto atc 1 top | `x[882.7+ 45*7] y-811.785` | `x811.785 y[882.7+ 45*7]` |
| 9004 goto atc 8 bottom | `x883 y-811.795` | `x811.795 y883` |
| 9005 goto TLS | `x829 y-811` | `x811 y829` |
| 9012 goto dial test indicator | `x718 y-811` | `x811 y718` |
| 9010 vertical fixture first hole | `X118.503 Y-685.985` | `X685.985 Y118.503` |
| 9006 Laser to Bit | `G54 G0 X1.245 Y129` | `G54 G0 X-129 Y1.245` |
| 9007 Bit to Laser | `G54 G0 X-1.245 Y-129` | `G54 G0 X129 Y-1.245` |
| 9011 Laser Y+38 -> **Laser X-38** | `G91 G0 Y38` | `G91 G0 X-38` |
| 9008 Laser Y-38 -> **Laser X+38** | `G91 G0 Y-38` | `G91 G0 X38` |

Commented-out coordinates in 9002/9005 were converted too. 9001, 9003, 9009 and 9013 have no X/Y machine positions and are unchanged.

Not changed, check by hand:
- Keyboard jog bindings: arrows already map Up=+Y, Right=+X, which now matches the machine.
- Probe corner (BottomLeft, X side Left, Y side Front): relative to the workpiece, so the on-screen meaning stays the same, but the physical corner differs from before. Confirm before probing.
- Direction choices in generator plugins (ToolBench planer `zigzagY`, BoxJoints `Y`, QuickCut jointer `y` / cutter `x`): the physical direction of these cuts rotates with the axes. Swap them if you want the same physical cut direction.
- RapidChange Solo config (pocket -1175, -511) isn't an installed plugin and looks like it came from another machine, so it was left alone.

## 7. ATC, toolsetter and macros (Z raised)

1. Run macros 9004 (atc 8 bottom), 9002 (atc 1 top), 9005 (TLS) and 9012 (dial indicator). Each first raises Z to machine Z-1 and then moves in X/Y. Confirm the spindle stops directly over the right spot.
2. First real tool change: turn rapid override down (25%) and watch the first unload/load end to end.
3. Run a toolsetter measurement and check that the reading matches what you'd expect.
4. Check the firmware keep-out zone: jog slowly toward the rack and confirm it stops at the zone edge (X 700-850, Y 750-1230).

## 8. Re-establish things stored in the controller
- Work offsets (G54-G59), G28/G30 positions: re-zero / re-set after homing (compare with the `$#` you saved).
- Laser offsets: macros 9006/9007 are converted, but verify the laser crosshair once.

## 9. Existing jobs and G-code files
Jobs created for the old orientation will now run **rotated 90°** on the machine compared with before. Their X now runs along the gantry instead of the vertical axis. Re-post jobs from CAM with the new axes, or at least check the preview and the work origin before running an old file. The first new job should be an air cut, so you can compare the preview with the real motion.

## Undo
Flash the original builder JSON, put the cables back, restore the old values from `original/firmware-settings-2026-10-15.txt`, and restore the original ncSender backup.
