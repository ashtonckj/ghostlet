"""Small normal window for editing settings. Every change is applied immediately."""
from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from ghostlet import __version__
from ghostlet.settings import LIMITS

# (ghost_scale, label): whole-number multiples of the art keep pixels crisp; "1×" is the default 2.
SIZE_OPTIONS = [(1, "0.5×"), (2, "1×"), (3, "1.5×"), (4, "2×"), (6, "3×")]


class SettingsWindow(QWidget):
    def __init__(self, settings, on_change, ghost_pixmap, on_test):
        super().__init__(None, Qt.Window)
        self.setObjectName("settings")  # style.qss targets #settings
        self.setWindowTitle("Ghostlet")
        self.setWindowIcon(QIcon(ghost_pixmap))
        self.on_change = on_change

        ghost = QLabel()
        ghost.setPixmap(ghost_pixmap.scaled(ghost_pixmap.size() * 2, Qt.KeepAspectRatio, Qt.FastTransformation))
        title = QLabel("Ghostlet")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        self.version_label = QLabel(f"v{__version__}")
        self.version_label.setObjectName("version")
        header = QWidget()
        head = QHBoxLayout(header)
        head.setContentsMargins(0, 0, 0, 0)
        # Ghost and version get slots of equal width, so the stretching title is centred in the window.
        self.version_label.setFixedWidth(ghost.pixmap().width())
        self.version_label.setAlignment(Qt.AlignRight)
        head.addWidget(ghost)
        head.addWidget(title, 1)
        head.addWidget(self.version_label, 0, Qt.AlignBottom)

        self.enabled = QCheckBox("Show ghosts when I'm idle")
        self.props = QCheckBox("Pumpkins and graves")
        self.launch_at_startup = QCheckBox("Launch at Windows sign-in")
        self.check_updates = QCheckBox("Check for updates")
        # The size slider walks SIZE_OPTIONS by index, so it only offers crisp sizes.
        self.ghost_scale, self.size_label, size_row = self._slider(0, len(SIZE_OPTIONS) - 1)
        self.ghost_count, self.count_label, count_row = self._slider(*LIMITS["ghost_count"])
        self.idle_timeout = self._spin("idle_timeout", " s")
        self.opacity = self._spin("opacity", " %")

        dev = QGroupBox("Dev settings")
        test = QPushButton("Test spawn")
        test.setToolTip("Summon the ghosts now. Moving the mouse won't scare them for 3 s.")
        test.clicked.connect(on_test)
        QHBoxLayout(dev).addWidget(test)

        close = QDialogButtonBox(QDialogButtonBox.Close)
        close.rejected.connect(self.close)

        form = QFormLayout(self)
        form.setSizeConstraint(QLayout.SetFixedSize)  # fixed size that follows the style's metrics
        form.setHorizontalSpacing(14)
        form.addRow(header)
        form.addRow(self.enabled)
        form.addRow(self.props)
        form.addRow(self.launch_at_startup)
        form.addRow(self.check_updates)
        form.addRow("Entity size:", size_row)
        form.addRow("Number of ghosts:", count_row)
        form.addRow("Idle timeout:", self.idle_timeout)
        form.addRow("Ghost opacity:", self.opacity)
        form.addRow(dev)
        form.addRow(close)

        self.show_settings(settings)
        for box in (self.enabled, self.props, self.launch_at_startup, self.check_updates):
            box.toggled.connect(self._changed)
        for spin in (self.idle_timeout, self.opacity):
            spin.valueChanged.connect(self._changed)
        for slider in (self.ghost_scale, self.ghost_count):
            slider.valueChanged.connect(self._refresh_labels)
            slider.valueChanged.connect(self._changed)

    def _spin(self, name, suffix=""):
        spin = QSpinBox()
        spin.setRange(*LIMITS[name])
        spin.setSuffix(suffix)
        return spin

    def _slider(self, lo, hi):
        """A horizontal slider with its current value shown on the right."""
        slider = QSlider(Qt.Horizontal)
        slider.setRange(lo, hi)
        slider.setMinimumWidth(110)
        label = QLabel()
        label.setMinimumWidth(40)
        row = QWidget()
        box = QHBoxLayout(row)
        box.setContentsMargins(0, 0, 0, 0)
        box.addWidget(slider)
        box.addWidget(label)
        return slider, label, row

    def _refresh_labels(self):
        self.size_label.setText(SIZE_OPTIONS[self.ghost_scale.value()][1])
        self.count_label.setText(str(self.ghost_count.value()))

    def show_settings(self, s):
        """Refresh widgets without firing change callbacks."""
        self.settings = s
        for name in ("enabled", "props", "launch_at_startup", "check_updates"):
            box = getattr(self, name)
            box.blockSignals(True)
            box.setChecked(getattr(s, name))
            box.blockSignals(False)
        for name in ("idle_timeout", "opacity"):
            spin = getattr(self, name)
            spin.blockSignals(True)
            spin.setValue(getattr(s, name))
            spin.blockSignals(False)
        # A hand-edited settings file may hold a scale with no option: show the nearest.
        nearest = min(range(len(SIZE_OPTIONS)), key=lambda i: abs(SIZE_OPTIONS[i][0] - s.ghost_scale))
        for slider, value in ((self.ghost_scale, nearest), (self.ghost_count, s.ghost_count)):
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
        self._refresh_labels()

    def _changed(self):
        self.on_change(replace(
            self.settings,
            enabled=self.enabled.isChecked(),
            idle_timeout=self.idle_timeout.value(),
            ghost_count=self.ghost_count.value(),
            ghost_scale=SIZE_OPTIONS[self.ghost_scale.value()][0],
            opacity=self.opacity.value(),
            launch_at_startup=self.launch_at_startup.isChecked(),
            props=self.props.isChecked(),
            check_updates=self.check_updates.isChecked(),
        ))
