# Replacing the ghost artwork

All artwork lives in this folder. The code never hard-codes art, so you can swap files freely.

## Files

| File | Used for |
|------|----------|
| `ghost.png` | Base image. Used for every state that has no frames of its own. |
| `<state>_<n>.png` | Animation frames for one state. `n` starts at 0. |
| `ghost.ico` | Tray icon is taken from the art; this file is only the `.exe` icon. |

States: `idle`, `floating`, `sleeping`, `fleeing`.

Example: a two-frame floating animation and a sleeping pose:

```
ghost.png
floating_0.png
floating_1.png
sleeping_0.png
```

Frames play at 4 fps (`ANIM_FPS` in `ghostlet/ghost.py`) and loop.

## Rules for the art

- PNG with a transparent background.
- Draw it facing **right**. Ghostlet mirrors it when the ghost moves left.
- Any size works; 32×32 is the default. All frames of one state should be the same size.
- The "Ghost size" setting scales the art by a whole number with hard pixel edges, so keep it small.

## After changing files

- From source: restart Ghostlet.
- Packaged `.exe`: rebuild it (`python -m PyInstaller ghostlet.spec`) — the art is baked in.
- For a new `.exe` icon, replace `ghost.ico` (256×256 recommended).

If a file is missing or unreadable, Ghostlet falls back to `ghost.png`, then to a built-in placeholder.
Note: `sleeping_0.png` is the placeholder's sleeping pose. Replace it or delete it when you swap `ghost.png`.

To regenerate the placeholder files: `python tools/make_placeholder.py`.
