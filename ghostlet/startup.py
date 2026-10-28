"""Launch at Windows sign-in via the per-user Run registry key (no admin needed)."""
import sys
import winreg
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
NAME = "Ghostlet"


def command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    # Running from source: use pythonw so no console window opens at sign-in.
    exe = Path(sys.executable)
    pythonw = exe.with_name("pythonw.exe")
    script = Path(__file__).resolve().parent.parent / "run_ghostlet.py"
    return f'"{pythonw if pythonw.exists() else exe}" "{script}"'


def set_enabled(on):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if on:
            winreg.SetValueEx(key, NAME, 0, winreg.REG_SZ, command())
        else:
            try:
                winreg.DeleteValue(key, NAME)
            except FileNotFoundError:
                pass
