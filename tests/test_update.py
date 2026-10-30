import hashlib
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication, QObject  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from ghostlet import update  # noqa: E402

app = QApplication.instance() or QApplication([])


def test_version_parsing_and_comparison():
    assert update.parse_version("v1.2.3") == (1, 2, 3)
    assert update.parse_version("1.0") == update.parse_version("v1.0.0") == (1,)
    assert update.parse_version("1.0-beta") is None and update.parse_version("latest") is None
    assert update.is_newer("v0.2.0", "0.1.0") and update.is_newer("1.10.0", "1.9.9")
    assert not update.is_newer("v0.1.0", "0.1.0") and not update.is_newer("v0.1.0", "0.2.0")
    assert not update.is_newer("1.0-beta", "0.1.0")  # junk tags never trigger an update
    assert not update.is_newer("v9.9.9", "dev")


def test_pick_asset_only_takes_exes_hosted_on_our_repo():
    good = {"name": "Ghostlet.exe", "browser_download_url": update.DOWNLOAD_PREFIX + "v1/Ghostlet.exe"}
    evil = {"name": "Ghostlet.exe", "browser_download_url": "https://evil.example/Ghostlet.exe"}
    other = {"name": "notes.txt", "browser_download_url": update.DOWNLOAD_PREFIX + "v1/notes.txt"}
    assert update.pick_asset({"assets": [other, evil, good]}) is good
    assert update.pick_asset({"assets": [other, evil]}) is None
    assert update.pick_asset({}) is None


def test_verify_checks_size_header_and_digest(tmp_path):
    data = b"MZ" + b"x" * 100
    f = tmp_path / "new.exe"
    f.write_bytes(data)
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    update.verify(f, {"size": len(data), "digest": digest})
    update.verify(f, {"size": len(data)})  # no digest published: size and header still checked
    with pytest.raises(ValueError, match="bytes"):
        update.verify(f, {"size": len(data) + 1})
    with pytest.raises(ValueError, match="checksum"):
        update.verify(f, {"size": len(data), "digest": "sha256:" + "0" * 64})
    f.write_bytes(b"ZZ" + b"x" * 100)
    with pytest.raises(ValueError, match="Windows program"):
        update.verify(f, {"size": len(data)})


def test_swap_in_keeps_old_copy_and_rolls_back_on_failure(tmp_path):
    cur, new = tmp_path / "Ghostlet.exe", tmp_path / "Ghostlet.exe.new"
    cur.write_bytes(b"old")
    new.write_bytes(b"new")
    update.swap_in(new, cur)
    assert cur.read_bytes() == b"new" and (tmp_path / "Ghostlet.exe.old").read_bytes() == b"old"
    assert not new.exists()

    with pytest.raises(OSError):  # the download vanished: the working exe must come back
        update.swap_in(tmp_path / "missing.new", cur)
    assert cur.read_bytes() == b"new"


class FakeGitHub(BaseHTTPRequestHandler):
    tag = "v9.9.9"

    def do_GET(self):
        body = json.dumps({"tag_name": self.tag, "assets": []}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def github(monkeypatch):
    server = HTTPServer(("127.0.0.1", 0), FakeGitHub)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(update, "API_URL", f"http://127.0.0.1:{server.server_port}/latest")
    opened = []
    monkeypatch.setattr(update.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()))
    yield opened
    server.shutdown()


def wait_for(condition, seconds=5):
    end = time.time() + seconds
    while time.time() < end and not condition():
        QCoreApplication.processEvents()
        time.sleep(0.01)
    return condition()


def test_newer_release_pops_up_and_update_button_acts(github):
    updater = update.Updater(QObject())
    FakeGitHub.tag = "v9.9.9"
    updater.check()
    assert wait_for(lambda: updater.box is not None)
    assert "v9.9.9" in updater.box.text()
    assert {b.text() for b in updater.box.buttons()} == {"Update", "Remind me later"}
    next(b for b in updater.box.buttons() if b.text() == "Update").click()
    assert github == [update.RELEASES_PAGE]  # not a packaged exe: sends you to the release page


def test_remind_me_later_does_nothing_and_old_tag_shows_no_popup(github):
    updater = update.Updater(QObject())
    FakeGitHub.tag = "v9.9.9"
    updater.check()
    assert wait_for(lambda: updater.box is not None)
    next(b for b in updater.box.buttons() if b.text() == "Remind me later").click()
    assert github == [] and not updater.busy

    updater.box = None
    FakeGitHub.tag = "v0.0.1"
    updater.check()
    assert wait_for(lambda: not updater.busy)
    assert updater.box is None
