import json

from ghostlet import settings
from ghostlet.settings import Settings


def test_missing_file_gives_defaults(tmp_path):
    s = settings.load(tmp_path / "nope.json")
    assert s == Settings()
    assert s.idle_timeout == 60 and s.ghost_count == 1 and s.launch_at_startup is False


def test_round_trip(tmp_path):
    path = tmp_path / "sub" / "settings.json"
    s = Settings(enabled=False, idle_timeout=120, ghost_count=3, ghost_scale=4, opacity=50, launch_at_startup=True, props=False)
    settings.save(s, path)
    assert settings.load(path) == s


def test_corrupt_json_gives_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("{not json", encoding="utf-8")
    assert settings.load(path) == Settings()
    path.write_text("[1, 2]", encoding="utf-8")
    assert settings.load(path) == Settings()


def test_invalid_values_are_clamped_or_ignored(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({
        "enabled": "yes",  # wrong type: default kept
        "idle_timeout": 1,  # below min
        "ghost_count": 99,  # above max
        "ghost_scale": True,  # bool is not a number here
        "opacity": 55.7,
        "launch_at_startup": 1,
        "unknown": 5,
    }), encoding="utf-8")
    s = settings.load(path)
    assert s.enabled is True
    assert s.idle_timeout == 5
    assert s.ghost_count == settings.MAX_GHOSTS == 5
    assert s.ghost_scale == Settings().ghost_scale
    assert s.opacity == 55
    assert s.launch_at_startup is False


def test_non_finite_numbers_ignored(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"idle_timeout": Infinity, "opacity": NaN}', encoding="utf-8")
    assert settings.load(path) == Settings()
