"""Check GitHub Releases for a newer Ghostlet and swap the exe in place.

The only network use in Ghostlet: one HTTPS GET to api.github.com per check (it sends nothing
about you), and, when you click Update, one download of the new exe from this repo's Releases.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QMessageBox, QProgressDialog

from ghostlet import __version__

REPO = "ashtonckj/ghostlet"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"  # skips drafts and pre-releases
DOWNLOAD_PREFIX = f"https://github.com/{REPO}/releases/download/"  # only exes hosted here are run
RELEASES_PAGE = f"https://github.com/{REPO}/releases/latest"


def parse_version(tag):
    """'v1.2.3' -> (1, 2, 3); None if it is not a plain dotted number (e.g. '1.0-beta')."""
    m = re.fullmatch(r"v?(\d+(?:\.\d+)*)", str(tag).strip())
    if not m:
        return None
    parts = [int(n) for n in m.group(1).split(".")]
    while parts and parts[-1] == 0:  # 1.0 and 1.0.0 are the same version
        parts.pop()
    return tuple(parts)


def is_newer(tag, current=__version__):
    new, cur = parse_version(tag), parse_version(current)
    return new is not None and cur is not None and new > cur


def pick_asset(release):
    """The release's .exe asset hosted on this repo's Releases page, or None."""
    for asset in release.get("assets", []):
        url = str(asset.get("browser_download_url", ""))
        if str(asset.get("name", "")).lower().endswith(".exe") and url.startswith(DOWNLOAD_PREFIX):
            return asset
    return None


def verify(path, asset):
    """Raise ValueError unless the file is the program GitHub described (size, MZ header, sha256)."""
    size = path.stat().st_size
    if size != asset.get("size"):
        raise ValueError(f"download is {size} bytes, expected {asset.get('size')}")
    with open(path, "rb") as f:
        if f.read(2) != b"MZ":
            raise ValueError("download is not a Windows program")
        digest = str(asset.get("digest") or "")
        if digest.startswith("sha256:"):
            f.seek(0)
            h = hashlib.sha256()
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
            if h.hexdigest() != digest[7:].lower():
                raise ValueError("download is corrupt (checksum mismatch)")


def swap_in(new, current):
    """Put new where current is. Windows can rename a running exe but not overwrite it."""
    old = current.with_name(current.name + ".old")
    os.replace(current, old)
    try:
        os.replace(new, current)
    except OSError:
        os.replace(old, current)  # put the working copy back
        raise


def cleanup():
    """Remove leftovers of an update: the renamed old exe and any unfinished download."""
    if not getattr(sys, "frozen", False):
        return
    exe = Path(sys.executable)
    for suffix in (".old", ".new"):
        try:
            exe.with_name(exe.name + suffix).unlink(missing_ok=True)
        except OSError:
            pass  # the old copy may still be shutting down; the next start retries


class Updater(QObject):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner  # must have restart_into(exe)
        self.net = QNetworkAccessManager(self)
        self.busy = False  # a check or download is running
        self.box = None  # the open "update available" popup

    def _request(self, url):
        req = QNetworkRequest(QUrl(url))
        req.setRawHeader(b"Accept", b"application/vnd.github+json")
        req.setRawHeader(b"User-Agent", f"Ghostlet/{__version__}".encode())
        # GitHub sends downloads to another host; https-to-https only.
        req.setAttribute(QNetworkRequest.RedirectPolicyAttribute, QNetworkRequest.NoLessSafeRedirectPolicy)
        req.setTransferTimeout(20000)  # ms without any data
        return req

    def check(self, manual=False):
        """Look for a newer release. manual=True also reports 'up to date' and failures."""
        if self.busy:
            return
        self.busy = True
        reply = self.net.get(self._request(API_URL))
        reply.finished.connect(lambda: self._checked(reply, manual))

    def _say(self, kind, text):
        QMessageBox(kind, "Ghostlet", text).exec()

    def _checked(self, reply, manual):
        self.busy = False
        reply.deleteLater()
        try:
            if reply.error() != QNetworkReply.NoError:
                raise ValueError(reply.errorString())
            release = json.loads(bytes(reply.readAll()))
            tag = release["tag_name"]
            newer = is_newer(tag)
        except (ValueError, KeyError, TypeError) as e:
            if manual:
                self._say(QMessageBox.Warning, f"Couldn't check for updates:\n{e}")
            return
        if newer:
            self._offer(tag, pick_asset(release))
        elif manual:
            self._say(QMessageBox.Information, f"You're up to date (v{__version__}).")

    def _offer(self, tag, asset):
        if self.box and self.box.isVisible():
            return
        box = QMessageBox(
            QMessageBox.Information,
            "Ghostlet update",
            f"Ghostlet {tag} is available. You have v{__version__}.\n\nUpdate now?",
        )
        update = box.addButton("Update", QMessageBox.AcceptRole)
        box.addButton("Remind me later", QMessageBox.RejectRole)  # also what closing the window does
        box.setDefaultButton(update)
        box.setWindowFlag(Qt.WindowStaysOnTopHint)
        box.buttonClicked.connect(lambda: box.clickedButton() == update and self._start(tag, asset))
        self.box = box
        box.show()

    def _start(self, tag, asset):
        exe = Path(sys.executable)
        if not (getattr(sys, "frozen", False) and asset):
            QDesktopServices.openUrl(QUrl(RELEASES_PAGE))  # running from source, or no exe attached
            return
        new = exe.with_name(exe.name + ".new")
        try:
            out = open(new, "wb")
        except OSError as e:  # e.g. the exe lives in a folder we can't write to
            self._say(QMessageBox.Warning, f"Can't save the update next to Ghostlet:\n{e}\n\nDownload it from:\n{RELEASES_PAGE}")
            return
        self.busy = True
        bar = QProgressDialog(f"Downloading Ghostlet {tag}…", "Cancel", 0, 100)
        bar.setWindowTitle("Ghostlet update")
        bar.setMinimumDuration(0)
        bar.setAutoClose(False)
        bar.setAutoReset(False)
        bar.setValue(0)
        reply = self.net.get(self._request(asset["browser_download_url"]))
        bar.canceled.connect(reply.abort)
        reply.readyRead.connect(lambda: out.write(bytes(reply.readAll())))  # stream to disk, not RAM

        def progress(got, total):
            if total > 0:
                bar.setValue(int(got * 100 / total))

        reply.downloadProgress.connect(progress)
        reply.finished.connect(lambda: self._downloaded(reply, out, new, asset, bar))

    def _downloaded(self, reply, out, new, asset, bar):
        self.busy = False
        out.close()
        bar.close()
        reply.deleteLater()
        exe = Path(sys.executable)
        cancelled = reply.error() == QNetworkReply.OperationCanceledError
        try:
            if reply.error() != QNetworkReply.NoError:
                raise OSError(reply.errorString())
            verify(new, asset)
            swap_in(new, exe)
        except (OSError, ValueError) as e:
            try:
                new.unlink(missing_ok=True)
            except OSError:
                pass
            if not cancelled:
                self._say(QMessageBox.Warning, f"The update failed, so nothing was changed:\n{e}\n\nDownload it from:\n{RELEASES_PAGE}")
            return
        try:
            self.owner.restart_into(exe)
        except OSError as e:
            self._say(QMessageBox.Warning, f"Updated, but Ghostlet couldn't restart itself:\n{e}\n\nStart it again from:\n{exe}")
