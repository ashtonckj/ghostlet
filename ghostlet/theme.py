"""Pixel-art look for every normal window: settings, tray menu and message boxes.

Restyle by editing assets/ui/style.qss; `{ui}` in it expands to the assets/ui folder.
Drop a pixel font (.ttf/.otf) into assets/ui/ and it is used automatically.
"""
from PySide6.QtGui import QFont, QFontDatabase

from ghostlet.assets import ASSET_DIR

UI_DIR = ASSET_DIR / "ui"


def apply(app):
    try:
        qss = (UI_DIR / "style.qss").read_text(encoding="utf-8")
        app.setStyleSheet(qss.replace("{ui}", UI_DIR.as_posix()))
    except OSError:
        pass  # missing theme: keep the plain Qt look

    font = QFont("Consolas")  # fallback when no pixel font is bundled
    for path in sorted([*UI_DIR.glob("*.ttf"), *UI_DIR.glob("*.otf")]):
        families = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(str(path)))
        if families:
            font = QFont(families[0])
            break
    font.setPixelSize(14)
    font.setStyleStrategy(QFont.NoAntialias)  # hard pixel edges
    # Windows gives menus and message boxes their own font, so set each.
    # Must come after setStyleSheet, which resets these per-class fonts.
    for widget_class in (None, "QMenu", "QMessageBox", "QMessageBoxLabel"):
        app.setFont(font, widget_class)
