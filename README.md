<div align="center">

<img src="docs/ghost.png" alt="Ghostlet ghost">

# Ghostlet

**Step away from your PC. Tiny ghosts move in.** 👻

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026-orange?labelColor=383838&style=for-the-badge)](https://hacktoberfest.com/)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078d4?labelColor=383838&style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?labelColor=383838&style=for-the-badge&logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?labelColor=383838&style=for-the-badge)

</div>

Leave your mouse alone for a minute and pixel ghosts float up around your cursor, while pumpkins, graves and spooky friends pile up along the bottom of your screen. Come back and they panic, grab the decorations and run away! 🎃

## 👻 Meet the ghosts

Each ghost picks a random look.

<div align="center">

| <img src="docs/ghosts/default.png" alt="classic ghost"> | <img src="docs/ghosts/cool.png" alt="cool ghost"> | <img src="docs/ghosts/crying.png" alt="crying ghost"> |
|:-:|:-:|:-:|
| classic | cool | crying |
| <img src="docs/ghosts/hunt.png" alt="hunting ghost"> | <img src="docs/ghosts/love.png" alt="loving ghost"> | <img src="docs/ghosts/magic.png" alt="magic ghost"> |
| hunting | loving | magic |
| <img src="docs/ghosts/peeping.png" alt="peeping ghost"> | <img src="docs/ghosts/shiver.png" alt="shivering ghost"> | <img src="docs/ghosts/sleeping.png" alt="sleeping ghost"> |
| peeping | shivering | sleeping |

<img src="docs/ghosts/rare.png" alt="the rare witch ghost">

✨ **The rare one!** 10× less likely to show up than any other ghost. ✨

</div>

## 🎃 Spooky props

<div align="center">

| <img src="docs/props/grave_cross.png" alt="grave_cross"> | <img src="docs/props/grave_tall.png" alt="grave_tall"> | <img src="docs/props/grave_wide.png" alt="grave_wide"> | <img src="docs/props/grave_short.png" alt="grave_short"> |
|:-:|:-:|:-:|:-:|
| cross grave | tall grave | wide grave | short grave |
| <img src="docs/props/pumpkin.png" alt="pumpkin"> | <img src="docs/props/pumpkin_1.png" alt="red pumpkin"> | <img src="docs/props/skeleton.png" alt="skeleton"> | <img src="docs/props/spider.png" alt="spider"> |
| pumpkin | red pumpkin | skeleton | spider |

The longer you're away, the more pile up. When you're back, the ghosts carry them off.

</div>

## 💾 Get it

Grab `Ghostlet.exe` from [Releases](https://github.com/ashtonckj/ghostlet/releases) and double-click it. No Python needed.

Ghostlet lives in your tray (bottom-right). Right-click the ghost for **Settings**.

<details>
<summary>Run from source or build the exe</summary>

```powershell
pip install -r requirements-dev.txt
python run_ghostlet.py
python -m PyInstaller ghostlet.spec
```

The last line builds `dist\Ghostlet.exe`. Exit Ghostlet from the tray first, or Windows won't let it overwrite the running file.

</details>

## ✨ Good to know

- 🖱️ Clicks go straight through the ghosts, and they never steal focus.
- 🎚️ Settings: up to 10 ghosts, size, opacity and idle time. **Test spawn** shows them right away.
- 🔒 No accounts, no telemetry. The only network use is an update check on GitHub, with one checkbox to turn it off. See [SECURITY.md](SECURITY.md).
- 🎨 Add your own ghosts and props by dropping a PNG in a folder, no code. See the [art guide](ghostlet/assets/README.md).

## 💜 Contributing

Pixel art, ideas and PRs are welcome! Start with [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under [MIT](LICENSE).
