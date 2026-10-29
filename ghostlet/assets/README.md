# Adding and replacing artwork

All artwork lives in this folder. Ghostlet scans it at startup, so adding a design means
dropping in a file. You don't need to edit any code or keep a list.

```
assets/
  ghost.png, sleeping_0.png, ...   the main ghost that stays by your cursor
  ghosts/
    blue/ghost.png                 a roaming ghost design (one folder per design)
    gold_crown_rare/ghost.png      "rare" in the name = 10x less likely to appear
  props/
    pumpkin.png                    every PNG in here is a prop
    pumpkin_big_1.png
    pumpkin_small_grin.png
    grave_cross.png
    pumpkin_gold_rare.png          rare works for props too
  ghost.ico                        .exe icon only
```

## Ghosts

The first ghost stays near your cursor and always uses the main ghost art in this folder.
With "Number of ghosts" above 1, the extra ghosts roam the whole screen, each using a randomly
picked design: the main ghost or any folder in `ghosts/`.

Each design (this folder for the main ghost, or a `ghosts/<name>/` folder) uses these files:

| File | Used for |
|------|----------|
| `ghost.png` | Base image. Used for every state that has no frames of its own. |
| `<state>_<n>.png` | Animation frames for one state. `n` starts at 0. |

States: `idle`, `floating`, `sleeping`, `fleeing`.

Example: a two-frame floating animation and a sleeping pose:

```
ghost.png
floating_0.png
floating_1.png
sleeping_0.png
```

Frames play at 4 fps (`ANIM_FPS` in `ghostlet/ghost.py`) and loop.

## Props (pumpkins, graves, anything)

- Every PNG in `props/` is a prop. Ghostlet picks one at random each time a prop appears.
  You can name the files anything you like.
- Want bigger pumpkins? Draw a bigger PNG, for example 24×24 instead of 16×16. Props show at
  their drawn size times the "Ghost size" setting and are never stretched to match each other.
- Props stand on the bottom edge of the screen, so leave no empty rows under the drawing.
- 3 props appear at first, then one more every 30 s, up to 12 (`START_PROPS`, `PROP_EVERY`
  and `MAX_PROPS` in `ghostlet/ghost.py`). When you come back, the ghosts carry them all off.
- To make a design appear more or less often, there is one knob: put `rare` in the name.

## Rules for the art

- PNG with a transparent background.
- Draw ghosts facing **right**. Ghostlet mirrors them when they move left. Props are never mirrored.
- Any size works; 32×32 is the default for ghosts and 16×16 for props. All frames of one state
  should be the same size. Keep everything under about 64×64, or it gets huge at "Ghost size" 6×.
- The "Ghost size" setting scales the art by a whole number with hard pixel edges, so keep it small.

## Settings window and tray menu

The pixel look of the normal windows lives in `ui/`:

- `ui/style.qss` sets colours, borders and sizes. It is a Qt style sheet (CSS-like), and
  `{ui}` in it points at this `ui/` folder. Keep corners square for the pixel look.
- `ui/check.png`, `ui/up.png` and `ui/down.png` are the checkbox tick and the number-box arrows.
- To use a pixel font, drop a `.ttf` or `.otf` file into `ui/`. It is picked up automatically,
  and Consolas is used without one. Include the font's license file next to it.

## After changing files

- From source: restart Ghostlet.
- Packaged `.exe`: rebuild it (`python -m PyInstaller ghostlet.spec`) — the art is baked in.
- For a new `.exe` icon, replace `ghost.ico` (256×256 recommended).

If a file is missing or unreadable, Ghostlet falls back to `ghost.png`, then to a built-in placeholder.
An empty `props/` folder falls back to the built-in pumpkin and grave.
Note: `sleeping_0.png` is the placeholder's sleeping pose. Replace it or delete it when you swap `ghost.png`.

To regenerate the placeholder files: `python tools/make_placeholder.py`. This **overwrites**
`ghost.png`, `sleeping_0.png`, `props/pumpkin.png` and `props/grave.png`.
