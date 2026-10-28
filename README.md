<div align="center">

<img src="docs/ghost.png" width="128" alt="Ghostlet pixel-art ghost">

# Ghostlet

**Step away from your PC, and a tiny ghost moves in.**

![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026-ff6b00?style=for-the-badge)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078d4?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt-41cd52?style=for-the-badge&logo=qt&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</div>

Leave your mouse alone for a minute and a little pixel ghost floats up around your cursor.
It drifts around, and if you stay away long enough it dozes off. When you come back, it
panics and flees off the screen. 👻

| <img src="docs/ghost.png" width="96" alt="Awake ghost"> | <img src="docs/sleeping_0.png" width="96" alt="Sleeping ghost"> |
|:---:|:---:|
| *floating about* | *zzz…* |

## Why you'll like it

- **Never in the way.** Clicks pass straight through the ghosts, and they never take focus.
- **Lives in your tray.** It has no window to manage. Right-click the ghost icon for Settings,
  Pause or Exit.
- **Featherweight.** Ghostlet checks idle time once a second and only animates while ghosts
  are out.
- **Private.** Ghostlet is fully offline: no accounts, no telemetry, no keylogging. Details in
  [SECURITY.md](SECURITY.md).
- **Yours to tweak.** You can change the idle time, ghost count (up to 5), size, opacity and
  whether it starts at sign-in.
- **Bring your own art.** Drop in new PNG frames; see the
  [art guide](ghostlet/assets/README.md).

## Get it

**Just want the ghost?** Grab `Ghostlet.exe` from Releases and double-click it. You don't need
Python.

**Run from source:**

```powershell
pip install -r requirements-dev.txt
python run_ghostlet.py
```

**Build the exe yourself:**

```powershell
python -m PyInstaller ghostlet.spec
```

Your exe is at `dist\Ghostlet.exe`.

## Contributing

PRs, pixel art and spooky ideas are welcome! Start with [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
