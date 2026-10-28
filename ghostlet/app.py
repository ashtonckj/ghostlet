"""Ghostlet entry point: tray icon, single-instance guard, idle polling and ghost animation."""
import ctypes
import getpass
import random
import sys
from dataclasses import replace

from PySide6.QtCore import QElapsedTimer, QObject, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QGuiApplication, QIcon
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from ghostlet import __version__, assets, idle, settings, startup, theme
from ghostlet.ghost import IDLE, PROP_KINDS, Ghost, Prop, prop_spots
from ghostlet.overlay import SpriteWindow
from ghostlet.settings import MAX_GHOSTS
from ghostlet.settings_window import SettingsWindow

SERVER_NAME = f"ghostlet-{getpass.getuser()}"
POLL_MS = 1000  # idle check while no ghosts are out
FRAME_MS = 33  # ~30 fps only while ghosts are visible
EXTRA_PROPS = 2  # props per haunt = ghost count + this; ghosts carry the extras stacked


class Ghostlet(QObject):
    def __init__(self, server):
        super().__init__()
        self.path = settings.default_path()
        self.settings = settings.load(self.path)
        self.paused = False
        self.ghosts = []
        self.props = []
        self.last_idle = 0.0
        self.settings_window = None

        self.frames = assets.load_frames()
        self.icon = QIcon(self.frames[IDLE][0])
        self.prop_art = assets.load_props()
        self.windows = [SpriteWindow() for _ in range(MAX_GHOSTS)]
        self.prop_windows = [SpriteWindow() for _ in range(MAX_GHOSTS + EXTRA_PROPS)]
        self._rescale()

        self.server = server
        server.newConnection.connect(self._on_second_instance)

        self.clock = QElapsedTimer()
        self.poll_timer = QTimer(self, interval=POLL_MS, timeout=self.poll)
        self.frame_timer = QTimer(self, interval=FRAME_MS, timeout=self.tick)
        self.frame_timer.setTimerType(Qt.PreciseTimer)
        self.poll_timer.start()

        self._build_tray()
        if self.settings.launch_at_startup:
            self._set_startup(True)  # refresh the path in case the exe moved
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.show_settings()  # no tray: make sure the app is reachable

    # --- tray -------------------------------------------------------------
    def _build_tray(self):
        menu = QMenu()
        menu.addAction("Settings", self.show_settings)
        self.pause_action = menu.addAction("Pause", self.toggle_pause)
        self.startup_action = QAction("Launch at Windows sign-in", menu, checkable=True)
        self.startup_action.setChecked(self.settings.launch_at_startup)
        self.startup_action.toggled.connect(self._startup_toggled)
        menu.addAction(self.startup_action)
        menu.addAction("About Ghostlet", self.about)
        menu.addSeparator()
        menu.addAction("Exit", self.exit)
        self.menu = menu  # keep a reference; the tray does not own it

        self.tray = QSystemTrayIcon(self.icon)
        self.tray.setToolTip("Ghostlet")
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: reason == QSystemTrayIcon.DoubleClick and self.show_settings()
        )
        self.tray.show()

    def show_settings(self):
        if not self.settings_window:
            self.settings_window = SettingsWindow(self.settings, self.apply_settings, self.frames[IDLE][0])
        w = self.settings_window
        w.show()
        w.setWindowState(w.windowState() & ~Qt.WindowMinimized)
        w.raise_()
        w.activateWindow()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_action.setText("Resume" if self.paused else "Pause")
        self.tray.setToolTip("Ghostlet (paused)" if self.paused else "Ghostlet")
        if self.paused:
            self.scare()

    def _startup_toggled(self, on):
        if on != self.settings.launch_at_startup:
            self.apply_settings(replace(self.settings, launch_at_startup=on))

    def about(self):
        QMessageBox.about(
            None,
            "About Ghostlet",
            f"<b>Ghostlet {__version__}</b><br>A tiny ghost that keeps you company while you're away."
            "<br><br>Runs fully offline. No accounts, analytics or telemetry."
            "<br>Only the time of your last input is read; no keys, screens or files.",
        )

    def exit(self):
        for w in self.windows + self.prop_windows:
            w.hide()
        self.tray.hide()
        QApplication.quit()

    def _on_second_instance(self):
        sock = self.server.nextPendingConnection()
        if sock:
            sock.disconnected.connect(sock.deleteLater)
        self.show_settings()

    # --- settings ---------------------------------------------------------
    def apply_settings(self, new):
        old, self.settings = self.settings, new
        if new.launch_at_startup != old.launch_at_startup and not self._set_startup(new.launch_at_startup):
            self.settings = new = replace(new, launch_at_startup=old.launch_at_startup)
        try:
            settings.save(new, self.path)
        except OSError:
            pass  # keep running with in-memory settings; next change retries the save
        if new.ghost_scale != old.ghost_scale:
            self._rescale()
        for w in self.windows + self.prop_windows:
            w.setWindowOpacity(new.opacity / 100)
        if not new.enabled:
            self.scare()
        # Keep both UIs in sync with the effective settings.
        self.startup_action.blockSignals(True)
        self.startup_action.setChecked(new.launch_at_startup)
        self.startup_action.blockSignals(False)
        if self.settings_window:
            self.settings_window.show_settings(new)

    def _set_startup(self, on):
        try:
            startup.set_enabled(on)
            return True
        except OSError as e:
            QMessageBox.warning(None, "Ghostlet", f"Could not change the sign-in setting:\n{e}")
            return False

    def _rescale(self):
        scale = self.settings.ghost_scale
        self.scaled = {
            state: [pm.scaled(pm.size() * scale, Qt.KeepAspectRatio, Qt.FastTransformation) for pm in pms]
            for state, pms in self.frames.items()
        }
        self.scaled_props = {
            kind: pm.scaled(pm.size() * scale, Qt.KeepAspectRatio, Qt.FastTransformation)
            for kind, pm in self.prop_art.items()
        }
        for w in self.windows + self.prop_windows:
            w.setWindowOpacity(self.settings.opacity / 100)

    # --- ghosts -----------------------------------------------------------
    def poll(self):
        if self.ghosts or self.paused or not self.settings.enabled:
            return
        if idle.idle_seconds() >= self.settings.idle_timeout:
            pos = QCursor.pos()
            rng = random.Random()
            self.ghosts = [Ghost(pos.x(), pos.y(), rng) for _ in range(self.settings.ghost_count)]
            if self.settings.props:
                self._spawn_props(pos, rng)
            self.last_idle = idle.idle_seconds()
            self.clock.start()
            self.frame_timer.start()

    def _spawn_props(self, pos, rng):
        screen = QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()
        area = screen.availableGeometry()  # excludes the taskbar
        count = len(self.ghosts) + EXTRA_PROPS
        for x in prop_spots(area.left() + 40, area.right() - 40, count, rng):
            kind = rng.choice(PROP_KINDS)
            h = self.scaled_props[kind].height()
            self.props.append(Prop(kind, x, area.bottom() - h / 2))

    def scare(self):
        pos = QCursor.pos()
        for g in self.ghosts:
            g.flee(pos.x(), pos.y())
        # Hand props out round-robin; a ghost's extra props hang below the previous one.
        ghost_h = self.scaled[IDLE][0].height()
        below = [ghost_h * 0.2] * len(self.ghosts)  # tuck the first prop under the ghost's tail
        for i, p in enumerate(self.props):
            n = i % len(self.ghosts)
            h = self.scaled_props[p.kind].height()
            p.grab(self.ghosts[n], below[n] + h / 2)
            below[n] += h * 0.7  # sprites have transparent padding rows

    def tick(self):
        dt = min(self.clock.restart() / 1000, 0.1)  # cap so a stall never teleports ghosts
        now_idle = idle.idle_seconds()
        if now_idle < self.last_idle:  # any keyboard/mouse input resets the idle clock
            self.scare()
        self.last_idle = now_idle

        for g in self.ghosts:
            g.update(dt)
        for p in self.props:
            p.update(dt)
        if all(g.gone for g in self.ghosts):
            self.ghosts, self.props = [], []
            self.frame_timer.stop()
            for w in self.windows + self.prop_windows:
                w.hide()
            return

        # Props first: windows shown later stack on top, so ghosts hold props from above.
        for p, w in zip(self.props, self.prop_windows):
            w.set_frame(self.scaled_props[p.kind], p.alpha)
            w.move(int(p.x - w.width() / 2), int(p.y - w.height() / 2))
            if w.isHidden():
                w.show()
        for g, w in zip(self.ghosts, self.windows):
            frames = self.scaled[g.state]
            w.set_frame(frames[g.frame(len(frames))], g.alpha, g.facing_left)
            w.move(int(g.x - w.width() / 2), int(g.y - w.height() / 2))
            if w.isHidden():
                w.show()


def _signal_running_instance():
    """If Ghostlet is already running, ask it to show Settings and return True."""
    sock = QLocalSocket()
    sock.connectToServer(SERVER_NAME)
    if not sock.waitForConnected(300):
        return False
    ctypes.windll.user32.AllowSetForegroundWindow(-1)  # ASFW_ANY: let it bring Settings to front
    sock.write(b"show")
    sock.waitForBytesWritten(300)
    sock.disconnectFromServer()
    return True


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Ghostlet")
    app.setQuitOnLastWindowClosed(False)  # lives in the tray
    if _signal_running_instance():
        return 0
    theme.apply(app)
    server = QLocalServer()
    QLocalServer.removeServer(SERVER_NAME)  # clear a stale name left by a crash
    server.listen(SERVER_NAME)
    ghostlet = Ghostlet(server)  # noqa: F841 - must stay alive while the app runs
    return app.exec()
