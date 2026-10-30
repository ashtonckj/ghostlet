"""Render crisp README previews of every ghost design and prop into docs/.

Run from the project root after adding or changing art:  python tools/make_previews.py
Browsers blur small PNGs when enlarging them, so the images are pre-scaled with hard edges.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from ghostlet import assets  # noqa: E402

DOCS = ROOT / "docs"
app = QApplication(sys.argv)


def save(pixmap, scale, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    pixmap.scaled(pixmap.size() * scale, Qt.KeepAspectRatio, Qt.FastTransformation).save(str(path))


for folder in ("ghosts", "props"):
    shutil.rmtree(DOCS / folder, ignore_errors=True)  # drop previews of designs that were removed
variants = assets.load_ghost_variants()
for name, frames in variants.items():
    save(frames["idle"][0], 3, DOCS / "ghosts" / f"{name}.png")
save(variants["default"]["idle"][0], 4, DOCS / "ghost.png")  # the big one at the top of the README
for name, pixmap in assets.load_props().items():
    save(pixmap, 4, DOCS / "props" / f"{name}.png")
print("Wrote", len(variants), "ghost and", len(assets.load_props()), "prop previews to", DOCS)
