"""Load and save user settings as JSON. Invalid or missing values fall back to defaults."""
import json
import math
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

MAX_GHOSTS = 5
# (min, max) for every numeric setting; out-of-range values are clamped.
LIMITS = {
    "idle_timeout": (5, 3600),
    "ghost_count": (1, MAX_GHOSTS),
    "ghost_scale": (1, 6),
    "opacity": (10, 100),
}


@dataclass
class Settings:
    enabled: bool = True
    idle_timeout: int = 60  # seconds
    ghost_count: int = 1
    ghost_scale: int = 2  # art is drawn at its native size times this
    opacity: int = 90  # percent
    launch_at_startup: bool = False


def default_path():
    return Path(os.environ.get("APPDATA") or Path.home()) / "Ghostlet" / "settings.json"


def load(path):
    s = Settings()
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return s
    if not isinstance(data, dict):
        return s
    for f in fields(Settings):
        value = data.get(f.name)
        if isinstance(getattr(s, f.name), bool):
            if isinstance(value, bool):
                setattr(s, f.name, value)
        elif isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            lo, hi = LIMITS[f.name]
            setattr(s, f.name, max(lo, min(hi, int(value))))
    return s


def save(settings, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
    os.replace(tmp, path)  # atomic, so a crash never leaves a half-written file
