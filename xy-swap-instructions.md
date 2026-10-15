# SLB-EXT X/Y axis swap (wall-mounted machine)

Backup used: `C:\downloads\firmware-settings-2026-10-15.txt`
Firmware config: `C:\downloads\STM32F4xx_LONGBOARD32_EXT_XY_swapped.json`
Commands to paste: `C:\downloads\xy-swap-commands.txt`

## Goal

|                | Before                          | After                            |
|----------------|---------------------------------|----------------------------------|
| Vertical axis (single motor)   | X, + = up, 1230 mm  | **Y**, + = up, 1230 mm           |
| Horizontal gantry (two motors) | Y, + = left, 812 mm | **X**, + = right, 812 mm         |
| Home corner    | bottom-left                     | bottom-left (no switches move)   |
| Machine coords | X 0..+1230, Y -812..0           | X 0..+812, Y 0..+1230            |

## 1. Flash the firmware

1. Load `STM32F4xx_LONGBOARD32_EXT_XY_swapped.json` in the web builder, build and flash.
   - The only firmware change is `Y_AUTO_SQUARE=1` -> `X_AUTO_SQUARE=1`.
   - The default values for X/Y steps, travel, direction and homing are also updated in case flashing resets your settings.

## 2. Rewire (power off)

| Item                          | Connect to             |
|-------------------------------|------------------------|
| Vertical motor                | **Y** motor connector  |
| Vertical limit switch         | **Y** limit input      |
| Gantry motor 1                | **X** motor connector  |
| Gantry motor 2                | **Y2** motor connector (unchanged) |
| Gantry limit switch 1         | **X** limit input      |
| Gantry limit switch 2         | **Y2** limit input (unchanged) |

In practice: swap the plugs between the X and Y connectors, for both the motors and the limit switches. Everything on Y2 stays where it is.

## 3. Settings to change

Send each line in the sender console, or paste `xy-swap-commands.txt`.

| Setting | Meaning                       | Old       | New        | Why |
|---------|-------------------------------|-----------|------------|-----|
| `$100`  | X steps/mm                    | 200.40000 | **80.20001**  | gantry drive is now X |
| `$101`  | Y steps/mm                    | 80.20001  | **200.40000** | vertical drive is now Y |
| `$130`  | X max travel                  | 1230.000  | **812.000**   | gantry travel |
| `$131`  | Y max travel                  | 812.000   | **1230.000**  | vertical travel |
| `$3`    | Step direction invert         | 6 (Y,Z)   | **4** (Z)     | gantry was + = left, now + = right; vertical stays + = up |
| `$23`   | Homing direction invert       | 1 (X)     | **3** (X,Y)   | both axes home toward negative (left / bottom) |
| `$37`   | Steppers kept enabled on alarm | 1 (X)    | **3** (X,Y)   | keeps the vertical axis held so it can't drop. X is included because the 2nd gantry motor shares Y's enable pin. |
| `$684`  | ATCi keep-out X min           | 750.00    | **700.00**    | was Y -850..-700 |
| `$685`  | ATCi keep-out Y min           | -850.00   | **750.00**    | was X 750..1230 |
| `$686`  | ATCi keep-out X max           | 1230.00   | **850.00**    | |
| `$687`  | ATCi keep-out Y max           | -700.00   | **1230.00**   | |

Keep-out conversion: new X = -(old Y), new Y = old X.

### Checked, no change needed
- `$110/$111` max rate (15000 both), `$120/$121` accel (700 both)
- `$160/$161` backlash, `$170/$171` auto-square offset, `$180/$181` homing feed, `$190/$191` homing seek: same values on both axes
- `$5=15` limit invert, `$744=7` / `$745=15` motor faults: all axes set
- `$8=0` ganged direction invert: it is relative to the main motor, and the same two motors are still ganged
- `$22`, `$27`, `$44=4` / `$45=3` homing cycles (Z, then X+Y together)
- `$770/$771` spindle offset: both 0

## 4. ncSender settings

Converted backup: `C:\downloads\ncsender-backup-tsmcnc5-XY-swapped.ncsbackup`
(the original `ncsender-backup-tsmcnc5-20261015-194447.ncsbackup` is unchanged)

Restore the converted backup in ncSender after the firmware change. Conversion used: new X = -(old Y), new Y = old X, Z unchanged.

| Item | Old | New |
|---|---|---|
| Home location (display) | back-left | **front-left** |
| Parking location | 663.243, -440.175, -5.004 | **440.175, 663.243, -5.004** |
| Keep-out zone (disabled) min / max | (700, -812) / (1155, -690) | **(690, 700) / (812, 1155)** |
| Rapid Change ATC orientation / direction | X / Negative | **Y** / Negative |
| Rapid Change ATC pocket 1 (slot1) | 1197.1909, -811.79416 | **811.79416, 1197.1909** |
| Rapid Change ATC toolsetter | 829.00012, -810.99914 | **810.99914, 829.00012** |
| Rapid Change ATC manual tool | 107.82808, -640.08762 | **640.08762, 107.82808** |
| Manual Tool Changer pocket 1 / toolsetter / parking (plugin disabled) | (883,-811) / (829,-811) / (107.829,-640.087) | **(811,883) / (811,829) / (640.087,107.829)** |

Z values (engagement, zones, toolsetter Z, safe Z) are unchanged.

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
- Keyboard jog bindings: arrows already map Up=+Y, Right=+X, which will now match the machine.
- Probe corner (BottomLeft, X side Left, Y side Front): these are relative to the workpiece, so they keep the same on-screen meaning. Physically they now point at a different corner than before. Confirm before probing.
- Direction choices in generator plugins (ToolBench planer `zigzagY`, BoxJoints `Y`, QuickCut jointer `y` / cutter `x`): the physical direction of these cuts rotates with the axes. Swap them if you want the same physical cut direction.
- RapidChange Solo config (pocket -1175, -511) isn't an installed plugin and looks like it came from another machine, so I left it alone.

## 5. Things stored in the controller
These positions use the old coordinates and must be set again:
- Work offsets (G54-G59) and G28/G30 positions: re-zero after homing

## 6. Test (bit raised, hand on the E-stop)
1. Power on, send `$$` and confirm the values above.
2. Before homing, jog a small distance (+X / -X / +Y / -Y): +X should go right and +Y up.
   - If the gantry goes the wrong way: `$3=5`. If the vertical axis goes the wrong way: `$3=6`.
   - If the two gantry motors fight each other: stop and set `$8=1`.
3. `$H`: Z homes first, then the gantry squares on both switches and the vertical axis homes to the bottom.
4. Jog toward the far corner and confirm soft limits stop it near X 812 / Y 1230.
5. Check the keep-out zone with a slow jog toward the tool rack.
6. Run macros 9004 (atc 8 bottom), 9002 (atc 1 top) and 9005 (TLS) with Z raised and check each lands over the right spot before letting the ATC run.
7. Run an air cut and compare the sender preview to the real motion.

To undo: flash the original JSON, put the plugs back, restore the old values from the firmware backup file, and restore the original ncSender backup.
