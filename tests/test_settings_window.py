import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402

from ghostlet import __version__  # noqa: E402
from ghostlet.settings import Settings  # noqa: E402
from ghostlet.settings_window import SIZE_OPTIONS, SettingsWindow  # noqa: E402

app = QApplication.instance() or QApplication([])


def make(settings, changes, tests):
    return SettingsWindow(settings, changes.append, QPixmap(32, 32), lambda: tests.append("test"))


def test_size_slider_snaps_to_nearest_option_and_reports_scale():
    changes, tests = [], []
    w = make(Settings(ghost_scale=5), changes, tests)  # 5 has no option
    assert SIZE_OPTIONS[w.ghost_scale.value()][0] == 4
    assert changes == []  # loading never fires a change
    w.ghost_scale.setValue(0)
    assert changes[-1].ghost_scale == 1 and w.size_label.text() == "0.5×"


def test_defaults_ghost_count_slider_and_test_button():
    changes, tests = [], []
    w = make(Settings(), changes, tests)
    assert w.size_label.text() == "1×"
    assert w.ghost_count.value() == 5 and w.count_label.text() == "5"
    w.ghost_count.setValue(w.ghost_count.maximum())
    assert changes[-1].ghost_count == 10
    {b.text(): b for b in w.findChildren(QPushButton)}["Test spawn"].click()
    assert tests == ["test"]
    assert "Skip 2 min" not in {b.text() for b in w.findChildren(QPushButton)}


def test_version_shown_beside_title():
    w = make(Settings(), [], [])
    assert w.version_label.text() == f"v{__version__}"
