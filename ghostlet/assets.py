"""Load ghost artwork from ghostlet/assets/, falling back to a built-in placeholder.

File naming (see assets/README.md):
  ghost.png            base image, used for any state without its own frames
  <state>_<n>.png      animation frames, e.g. floating_0.png, floating_1.png
  <state>.png          a single pose for that state, e.g. sleeping.png
  ghosts/<name>/       extra ghost designs for roaming ghosts, same file names as above
  props/*.png          every PNG here is a prop (pumpkin, grave, ...), picked at random
"""
from pathlib import Path

from PySide6.QtGui import QColor, QImage, QPixmap

from ghostlet.ghost import SLEEPING, STATES

ASSET_DIR = Path(__file__).parent / "assets"
GHOST_DIR = ASSET_DIR / "ghosts"
PROP_DIR = ASSET_DIR / "props"

# Built-in placeholders; also what tools/make_placeholder.py writes to disk.
PALETTE = {
    "K": "#2b2b3a",  # outline
    "E": "#2b2b3a",  # eyes
    "W": "#f4f6ff",  # ghost body
    "S": "#c9cfe8",  # ghost shade
    "P": "#ffb3c7",  # blush
    "O": "#ff8c1a",  # pumpkin
    "D": "#c25a00",  # pumpkin ridge
    "G": "#4a8c2a",  # stem, grass
    "L": "#b4b8cc",  # stone
    "R": "#8a8fa8",  # stone shade
}
GHOST = [
    "................................",
    "................................",
    "................................",
    "................................",
    "............KKKKKKKK............",
    "..........KKWWWWWWWWKK..........",
    ".........KWWWWWWWWWWWWK.........",
    "........KWWWWWWWWWWWWWWK........",
    ".......KWWWWWWWWWWWWWWWWK.......",
    "......KWWWWWWWWWWWWWWWWWWK......",
    ".....KWWWWWWWWWWWWWWWWWWWWK.....",
    ".....KWWWWWWWWWWWWWWWWWWWWK.....",
    ".....KWWWWWEEWWWWWWEEWWWWWK.....",
    ".....KWWWWWEEWWWWWWEEWWWWWK.....",
    ".....KWWWPPWWWWWWWWWWPPWWWK.....",
    ".....KWWWWWWWWWWWWWWWWWWWWK.....",
    ".....KWWWWWWWWWKKWWWWWWWWWK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWWWWWWWWWWWWWWSSK.....",
    ".....KWWWWWKKWWWWWWKKWWWWSK.....",
    "......KWWWK..KWWWWK..KWWSK......",
    ".......KKK....KKKK....KKK.......",
    "................................",
    "................................",
    "................................",
]
GHOST_ASLEEP = GHOST[:12] + [GHOST[12].replace("E", "W")] + GHOST[13:]  # eyes half closed


def _mirror(half):
    return [row + row[::-1] for row in half]


# 16x16 props, drawn as left halves and mirrored.
PROP_ART = {
    "pumpkin": _mirror([
        "........",
        "........",
        "........",
        "........",
        ".......G",
        "...KKKKG",
        "..KOODOO",
        ".KOODOOO",
        ".KODKKOO",
        ".KODKKOO",
        ".KODOOOO",
        ".KODKOKO",
        ".KODKKKK",
        ".KOODOOO",
        "..KOODOO",
        "...KKKKK",
    ]),
    "grave": _mirror([
        "........",
        "........",
        "....KKKK",
        "...KLLLL",
        "..KLLLLL",
        "..KLLLKK",
        "..KLLKKK",
        "..KLLLKK",
        "..KLLLKK",
        "..KLLLLL",
        "..KLLLLL",
        "..KRLLLL",
        "..KRRRRR",
        ".GKGGGGG",
        "GGGGGGGG",
        "GGGGGGGG",
    ]),
}

# Pixel UI icons used by assets/ui/style.qss; written at 2x by tools/make_placeholder.py.
UI_ART = {
    "check": [
        "......K",
        ".....KK",
        "K...KK.",
        "KK.KK..",
        ".KKK...",
        "..K....",
    ],
    "up": [
        "..K..",
        ".KKK.",
        "KKKKK",
    ],
    "down": [
        "KKKKK",
        ".KKK.",
        "..K..",
    ],
}


def art_to_image(rows):
    img = QImage(len(rows[0]), len(rows), QImage.Format_ARGB32)
    img.fill(0)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in PALETTE:
                img.setPixelColor(x, y, QColor(PALETTE[ch]))
    return img


def _load(path):
    pm = QPixmap(str(path))
    return None if pm.isNull() else pm


def _frame_number(path):
    suffix = path.stem.rsplit("_", 1)[-1]
    return int(suffix) if suffix.isdigit() else None


def load_props():
    """Return {name: QPixmap} for every PNG in props/; the built-in art if there are none."""
    props = {p.stem: pm for p in sorted(PROP_DIR.glob("*.png")) if (pm := _load(p))}
    return props or {name: QPixmap.fromImage(art_to_image(art)) for name, art in PROP_ART.items()}


def load_ghost_variants():
    """Return {name: frames}: "default" (the main ghost) plus one per folder in ghosts/."""
    variants = {"default": load_frames()}
    if GHOST_DIR.is_dir():
        for folder in sorted(GHOST_DIR.iterdir()):
            if folder.is_dir():
                frames = load_frames(folder, builtin=False)
                if frames:  # a folder with no usable image is skipped, never drawn as the placeholder
                    variants[folder.name] = frames
    return variants


def _find_base(folder):
    """ghost.png, else the first PNG that isn't a numbered animation frame (e.g. ghost_cool.png)."""
    preferred = folder / "ghost.png"
    if preferred.exists():
        return preferred
    for p in sorted(folder.glob("*.png")):
        is_state_frame = p.stem in STATES or (p.stem.split("_")[0] in STATES and _frame_number(p) is not None)
        if not is_state_frame:
            return p
    return None


def load_frames(folder=ASSET_DIR, builtin=True):
    """Return {state: [QPixmap, ...]}; every state gets at least one frame.

    With builtin=False a folder that has no usable image returns None instead of the placeholder.
    """
    base_file = _find_base(folder)
    base = _load(base_file) if base_file else None
    frames = {}
    for state in STATES:
        files = sorted(
            (p for p in folder.glob(f"{state}_*.png") if _frame_number(p) is not None),
            key=_frame_number,
        )
        if not files and (folder / f"{state}.png").exists():
            files = [folder / f"{state}.png"]  # a single pose can skip the _0 suffix
        found = [pm for pm in map(_load, files) if pm]
        if not found and not base:
            if not builtin:
                return None
            found = [QPixmap.fromImage(art_to_image(GHOST_ASLEEP if state == SLEEPING else GHOST))]
        frames[state] = found or [base]
    return frames
