"""Seconds since the last keyboard/mouse input, via Win32 GetLastInputInfo.

Only the timestamp of the last input is read; no keys or positions are captured.
"""
import ctypes
from ctypes import wintypes


class _LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32
_kernel32.GetTickCount.restype = wintypes.DWORD


def idle_seconds():
    info = _LASTINPUTINFO(ctypes.sizeof(_LASTINPUTINFO), 0)
    if not _user32.GetLastInputInfo(ctypes.byref(info)):
        return 0.0
    # Both counters are 32-bit milliseconds and wrap every ~49.7 days.
    return ((_kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF) / 1000.0
