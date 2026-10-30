"""Regenerate the placeholder art in ghostlet/assets/ from the ASCII art in ghostlet/assets.py.

Run from the project root:  python tools/make_placeholder.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

from ghostlet.assets import (
    ASSET_DIR,
    GHOST,
    GHOST_ASLEEP,
    PROP_ART,
    UI_ART,
    art_to_image,
)

app = QGuiApplication(sys.argv)
ASSET_DIR.mkdir(exist_ok=True)
ghost = art_to_image(GHOST)
ghost.save(str(ASSET_DIR / "ghost.png"))
art_to_image(GHOST_ASLEEP).save(str(ASSET_DIR / "sleeping.png"))
# Exe/tray icon, upscaled with hard pixel edges.
ghost.scaled(256, 256, Qt.KeepAspectRatio, Qt.FastTransformation).save(str(ASSET_DIR / "ghost.ico"))
(ASSET_DIR / "props").mkdir(exist_ok=True)
for name, art in PROP_ART.items():
    art_to_image(art).save(str(ASSET_DIR / "props" / f"{name}.png"))
for name, art in UI_ART.items():
    img = art_to_image(art)
    img.scaled(img.size() * 2, Qt.KeepAspectRatio, Qt.FastTransformation).save(str(ASSET_DIR / "ui" / f"{name}.png"))
print("Wrote placeholder art to", ASSET_DIR)
