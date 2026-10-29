# Contributing to Ghostlet

Thanks for wanting to help the ghosts! Code, artwork, bug reports and ideas are all welcome.

## Ground rules

1. **Privacy is not negotiable.** No network calls, telemetry, analytics, keylogging,
   screenshots, or file scanning. A PR that adds any of these will be closed.
2. **Stay light.** Ghostlet sits in the background all day. Do no work while no ghosts
   are visible beyond the 1-second idle check. Animate only while something is on screen.
3. **Keep it small.** No new dependency without discussing it in an issue first. Prefer the
   standard library and PySide6.
4. **One pixel look everywhere.** UI styling goes in `ghostlet/assets/ui/style.qss`, using its
   palette and square corners, never in Python code.
5. **Match the code around you**: naming, comment style, and plain functions over class hierarchies.
6. **Never steal focus or block clicks.** Overlays must stay click-through and must not activate.

For anything bigger than a bug fix, please open an issue first so we can agree on the approach.

## Dev setup

You need Windows 10/11 and Python 3.10+.

```powershell
git clone <your fork URL>
cd ghostlet
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python run_ghostlet.py
```

Tip: set **Idle timeout** to 5 s in Settings so you don't wait a minute for every test.

## Tests

```powershell
python -m pytest
```

Movement, state and settings logic is plain Python (no Qt) so it is quick to test. Put new
logic there and add a test. Any new branch, loop or parsing code needs at least one test.

Things tests can't cover still need a manual check on Windows before you open a PR:

- Ghosts appear after the idle timeout and flee when you move the mouse.
- You can click through the ghosts, and they never take focus.
- Settings changes take effect, and the settings survive a restart.
- The tray menu works, and a second launch opens Settings instead of starting a second copy.

## Building the exe

```powershell
python -m PyInstaller ghostlet.spec
```

Output: `dist\Ghostlet.exe`. If you add files under `ghostlet/assets/`, they are bundled
automatically.

## Artwork

New ghosts, frames and pixel art are very welcome. See
[ghostlet/assets/README.md](ghostlet/assets/README.md) for file names and rules. Please only
submit art you made yourself, or art whose license lets us ship it under MIT, and say which
in your PR.

After changing the placeholder art in `ghostlet/assets.py`, run
`python tools/make_placeholder.py` to regenerate the PNGs, the icon and the README images.

## Project layout

```
run_ghostlet.py            entry script (source and PyInstaller)
ghostlet.spec              PyInstaller build config
ghostlet/
  app.py                   tray, single instance, idle polling, animation loop
  ghost.py                 ghost states and motion (pure Python, tested)
  settings.py              load/save/validate settings (tested)
  settings_window.py       settings window
  theme.py                 pixel-art look: loads assets/ui/style.qss and the UI font
  overlay.py               transparent click-through ghost window
  assets.py                artwork loading + built-in placeholder art
  idle.py                  Win32 idle time
  startup.py               launch-at-sign-in registry entry
  assets/                  main ghost art, ghost.ico, art guide
    ghosts/<name>/         extra ghost designs for roaming ghosts (scanned at startup)
    props/                 pumpkins, graves, ... (every PNG is used, scanned at startup)
    ui/                    style.qss + pixel icons for the settings window and tray menu
docs/                      README images
tools/make_placeholder.py  regenerates placeholder art and README images
tests/                     pytest tests
```

## Pull requests

- Keep each PR to one change, with a short description of what changed and why.
- Run `python -m pytest`, and do the manual check above if you touched app or overlay code.
- Add screenshots or a GIF for visual changes.
- Update the README or this file if behaviour or setup changes.

## Hacktoberfest 2026

Ghostlet joins in the spirit of Hacktoberfest 2026. Note that this year Hacktoberfest **does not
count pull requests** toward rewards; see [hacktoberfest.com](https://hacktoberfest.com). So
please contribute because you want to, and keep PRs meaningful. Low-effort or
AI-generated spam PRs will be closed.

## Security

Found a vulnerability? Please don't open a public issue. See [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
