# Adding and replacing artwork

All artwork lives in this folder. Ghostlet scans it at startup, so adding a design means
dropping in a file. You don't need to edit any code or keep a list.

```
assets/
  ghost.png, sleeping.png, ...   the original ghost design
  ghosts/                          one folder per extra design (an expression, a colour, ...)
    happy/ghost.png
    happy/sleeping.png           its own sleeping pose (optional)
    grumpy/ghost.png               no sleeping image: it sleeps with this face
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

Every ghost gets a random design each time it appears: the original one in this folder or
any folder in `ghosts/`. The first ghost stays near your cursor. With "Number of ghosts"
above 1, the others roam the whole screen.

A design is a folder, not a single PNG, so that its awake face, sleeping face and any
animation frames stay together. For a new expression, make a folder and put its PNGs in it.

Each design (this folder for the original, or a `ghosts/<name>/` folder) uses these files:

| File | Used for |
|------|----------|
| `ghost.png` | Base image. Used for every state that has no frames of its own. Any one PNG in the folder works instead, such as `ghost_cool.png`; `ghost.png` wins if both exist. A folder with no usable PNG is skipped. |
| `<state>_<n>.png` | Animation frames for one state. `n` starts at 0. |

States: `idle`, `floating`, `sleeping`, `fleeing`.

Example: a two-frame floating animation and a sleeping pose:

```
ghost.png
floating_0.png
floating_1.png
sleeping.png
```

Frames play at 4 fps (`ANIM_FPS` in `ghostlet/ghost.py`) and loop.

Every file except `ghost.png` is optional:

| What you put in the folder | What the ghost does when asleep |
|------|------|
| only `ghost.png` | keeps its awake face |
| `sleeping.png` | shows that one sleeping pose |
| `sleeping_0.png`, `sleeping_1.png`, ... | plays them as a sleeping animation |

The same goes for `idle_`, `floating_` and `fleeing_` frames.

## Checking your art

In Settings → **Dev settings**:

- **Test spawn** summons the ghosts and props right away. Moving the mouse won't scare them
  for 3 s, so you get a look. The extra ghosts appear one by one over 20 s.
- Ghosts only fall asleep after about 2 minutes. To see your sleeping art sooner, lower
  `SLEEP_AFTER` in `ghostlet/ghost.py` while testing.
- Changing **Entity size** shows a ghost and a prop by your cursor for 3 s at the new size.

Restart Ghostlet after adding files. It only scans the folders when it starts.

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
- Every `.ttf` or `.otf` file in `ui/` is loaded, and `style.qss` says which font each part uses, by
  family name: `04B_30` for all text and `KiwiSoda` for the "Ghostlet" title. To switch a font, drop
  the file in `ui/` and change its `font-family` in `style.qss`. Consolas is the fallback if a font
  is missing. A font anywhere else, such as the project root, is ignored.
- To find a font's family name, install it or open it in Windows' font viewer. It is often not the
  file name (`04B_30__.TTF` is `04b`).
- `04B_30` is drawn on an 8 px grid, so keep its sizes at multiples of 8 to stay crisp. KiwiSoda
  draws small, so the title is set bigger (`font-size` under `#title`).
- Keep each font's license file next to it, and check the license allows shipping the font in
  a public repository.

## After changing files

- From source: restart Ghostlet.
- Packaged `.exe`: exit Ghostlet from the tray, then rebuild it
  (`python -m PyInstaller ghostlet.spec`) — the art is baked in.
- For a new `.exe` icon, replace `ghost.ico` (256×256 recommended).

If a file is missing or unreadable, Ghostlet falls back to `ghost.png`, then to a built-in placeholder.
An empty `props/` folder falls back to the built-in pumpkin and grave.
Note: `sleeping.png` is the placeholder's sleeping pose. Replace it or delete it when you swap `ghost.png`.

To regenerate the placeholder files: `python tools/make_placeholder.py`. This **overwrites**
`ghost.png`, `sleeping.png`, `props/pumpkin.png` and `props/grave.png`.
