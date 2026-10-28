from PySide6.QtGui import QColor

from ghostlet.assets import GHOST, GHOST_ASLEEP, art_to_image


def test_placeholder_is_32x32_with_transparent_background():
    for art in (GHOST, GHOST_ASLEEP):
        assert len(art) == 32 and all(len(row) == 32 for row in art)
    img = art_to_image(GHOST)
    assert (img.width(), img.height()) == (32, 32)
    assert img.pixelColor(0, 0).alpha() == 0
    assert img.pixelColor(16, 20) == QColor("#f4f6ff")


def test_ui_art_rows_are_even_and_theme_images_exist():
    import re

    from ghostlet.assets import UI_ART
    from ghostlet.theme import UI_DIR

    for art in UI_ART.values():
        assert len({len(row) for row in art}) == 1
    qss = (UI_DIR / "style.qss").read_text(encoding="utf-8")
    for name in re.findall(r"url\(\{ui\}/([^)]+)\)", qss):
        assert (UI_DIR / name).exists(), name
