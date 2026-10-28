from PySide6.QtGui import QColor

from ghostlet.assets import GHOST, GHOST_ASLEEP, art_to_image


def test_placeholder_is_32x32_with_transparent_background():
    for art in (GHOST, GHOST_ASLEEP):
        assert len(art) == 32 and all(len(row) == 32 for row in art)
    img = art_to_image(GHOST)
    assert (img.width(), img.height()) == (32, 32)
    assert img.pixelColor(0, 0).alpha() == 0
    assert img.pixelColor(16, 20) == QColor("#f4f6ff")
