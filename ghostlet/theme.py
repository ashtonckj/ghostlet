"""Pixel-art look for every normal window: settings, tray menu and message boxes.

Restyle by editing assets/ui/style.qss; `{ui}` in it expands to the assets/ui folder.
Every .ttf/.otf in assets/ui/ is registered, and style.qss chooses which font each part uses
by family name (`font-family`), so adding a font means dropping the file in and naming it there.
"""
from PySide6.QtGui import QFont, QFontDatabase

from ghostlet.assets import ASSET_DIR

UI_DIR = ASSET_DIR / "ui"


def apply(app):
    for path in sorted(UI_DIR.iterdir()):
        if path.suffix.lower() in (".ttf", ".otf"):
            QFontDatabase.addApplicationFont(str(path))  # unreadable fonts are skipped
    font = QFont()
    font.setStyleStrategy(QFont.NoAntialias)  # hard pixel edges; family and size come from the QSS
    app.setFont(font)
    try:
        qss = (UI_DIR / "style.qss").read_text(encoding="utf-8")
        app.setStyleSheet(qss.replace("{ui}", UI_DIR.as_posix()))
    except OSError:
        pass  # missing theme: keep the plain Qt look
