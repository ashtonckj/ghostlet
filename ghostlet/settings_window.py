"""Small normal window for editing settings. Every change is applied immediately."""
from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLayout,
    QSpinBox,
    QWidget,
)

from ghostlet.settings import LIMITS


class SettingsWindow(QWidget):
    def __init__(self, settings, on_change, ghost_pixmap):
        super().__init__(None, Qt.Window)
        self.setObjectName("settings")  # style.qss targets #settings
        self.setWindowTitle("Ghostlet Settings")
        self.setWindowIcon(QIcon(ghost_pixmap))
        self.on_change = on_change

        ghost = QLabel()
        ghost.setPixmap(ghost_pixmap.scaled(ghost_pixmap.size() * 2, Qt.KeepAspectRatio, Qt.FastTransformation))
        title = QLabel("Ghostlet")
        title.setObjectName("title")

        self.enabled = QCheckBox("Show ghosts when I'm idle")
        self.idle_timeout = self._spin("idle_timeout", " s")
        self.ghost_count = self._spin("ghost_count")
        self.ghost_scale = self._spin("ghost_scale", "×")
        self.opacity = self._spin("opacity", " %")
        self.props = QCheckBox("Pumpkins and graves")
        self.launch_at_startup = QCheckBox("Launch at Windows sign-in")
        close = QDialogButtonBox(QDialogButtonBox.Close)
        close.rejected.connect(self.close)

        form = QFormLayout(self)
        form.setSizeConstraint(QLayout.SetFixedSize)  # fixed size that follows the style's metrics
        form.addRow(ghost, title)
        form.addRow(self.enabled)
        form.addRow("Idle timeout:", self.idle_timeout)
        form.addRow("Number of ghosts:", self.ghost_count)
        form.addRow("Ghost size:", self.ghost_scale)
        form.addRow("Ghost opacity:", self.opacity)
        form.addRow(self.props)
        form.addRow(self.launch_at_startup)
        form.addRow(close)

        self.show_settings(settings)
        for box in (self.enabled, self.props, self.launch_at_startup):
            box.toggled.connect(self._changed)
        for spin in (self.idle_timeout, self.ghost_count, self.ghost_scale, self.opacity):
            spin.valueChanged.connect(self._changed)

    def _spin(self, name, suffix=""):
        spin = QSpinBox()
        spin.setRange(*LIMITS[name])
        spin.setSuffix(suffix)
        return spin

    def show_settings(self, s):
        """Refresh widgets without firing change callbacks."""
        self.settings = s
        for name in ("enabled", "props", "launch_at_startup"):
            box = getattr(self, name)
            box.blockSignals(True)
            box.setChecked(getattr(s, name))
            box.blockSignals(False)
        for name in ("idle_timeout", "ghost_count", "ghost_scale", "opacity"):
            spin = getattr(self, name)
            spin.blockSignals(True)
            spin.setValue(getattr(s, name))
            spin.blockSignals(False)

    def _changed(self):
        self.on_change(replace(
            self.settings,
            enabled=self.enabled.isChecked(),
            idle_timeout=self.idle_timeout.value(),
            ghost_count=self.ghost_count.value(),
            ghost_scale=self.ghost_scale.value(),
            opacity=self.opacity.value(),
            launch_at_startup=self.launch_at_startup.isChecked(),
            props=self.props.isChecked(),
        ))
