"""One small transparent, click-through, always-on-top window per ghost."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget


class GhostWindow(QWidget):
    def __init__(self):
        super().__init__(
            None,
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool  # no taskbar button
            | Qt.WindowTransparentForInput  # clicks go to the window underneath
            | Qt.WindowDoesNotAcceptFocus
            | Qt.NoDropShadowWindowHint,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.pixmap = None
        self.alpha = 1.0
        self.flip = False

    def set_frame(self, pixmap, alpha, flip):
        if pixmap is not self.pixmap:
            self.pixmap = pixmap
            self.setFixedSize(pixmap.size())
        self.alpha, self.flip = alpha, flip
        self.update()

    def paintEvent(self, event):
        if not self.pixmap:
            return
        p = QPainter(self)
        p.setOpacity(self.alpha)
        if self.flip:
            p.translate(self.width(), 0)
            p.scale(-1, 1)
        p.drawPixmap(0, 0, self.pixmap)
