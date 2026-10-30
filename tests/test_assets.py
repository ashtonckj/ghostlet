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


def test_every_font_family_named_in_the_qss_is_registered():
    import os
    import re

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QFontDatabase
    from PySide6.QtWidgets import QApplication

    from ghostlet import theme

    app = QApplication.instance() or QApplication([])
    theme.apply(app)
    qss = (theme.UI_DIR / "style.qss").read_text(encoding="utf-8")
    wanted = set(re.findall(r'font-family:\s*"([^"]+)"', qss))
    assert wanted  # the theme names its fonts
    have = {f.lower() for f in QFontDatabase.families()}
    for family in wanted:
        assert family.lower() in have, f"{family} is named in style.qss but no font file in assets/ui provides it"


def test_every_ghost_folder_is_drawn_from_its_own_png_not_the_placeholder():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication

    from ghostlet.assets import GHOST, GHOST_DIR, art_to_image, load_ghost_variants

    app = QApplication.instance() or QApplication([])
    fmt = QImage.Format_ARGB32
    placeholder = art_to_image(GHOST).convertToFormat(fmt)
    folders = {d.name for d in GHOST_DIR.iterdir() if d.is_dir()}
    variants = load_ghost_variants()
    assert set(variants) == folders | {"default"}, "a ghosts/ folder has no usable PNG and was skipped"
    for name in folders:
        shown = variants[name]["idle"][0].toImage().convertToFormat(fmt)
        assert shown != placeholder, f"ghosts/{name} is showing the built-in placeholder"


def test_ghost_folder_accepts_any_png_name_and_empty_folder_is_skipped(tmp_path, monkeypatch):
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication

    from ghostlet import assets

    app = QApplication.instance() or QApplication([])
    (tmp_path / "cool").mkdir()
    (tmp_path / "empty").mkdir()
    (tmp_path / "numbered").mkdir()
    img = QImage(8, 8, QImage.Format_ARGB32)
    img.fill(0xFF00FF00)
    img.save(str(tmp_path / "cool" / "ghost_cool.png"))
    img.save(str(tmp_path / "numbered" / "idle_0.png"))  # only a state frame, no base image
    monkeypatch.setattr(assets, "GHOST_DIR", tmp_path)
    variants = assets.load_ghost_variants()
    assert "cool" in variants and variants["cool"]["sleeping"][0].width() == 8
    assert "empty" not in variants and "numbered" not in variants
