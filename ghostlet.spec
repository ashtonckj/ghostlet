# PyInstaller build config. Build with:  python -m PyInstaller ghostlet.spec
# Output: dist/Ghostlet.exe (single file, no console, Python + PySide6 bundled).
# Only what is imported plus `datas` is packed, so docs/, tests/ and tools/ never end up inside.
import os

a = Analysis(
    ["run_ghostlet.py"],
    datas=[("ghostlet/assets", "ghostlet/assets")],
)

# PySide6's build hooks bundle Qt parts Ghostlet never uses (about 16 MB): the software OpenGL
# fallback, Qt Quick/QML and PDF. Ghostlet only draws with Qt Widgets. Add a name here to drop more.
UNUSED = {"opengl32sw.dll", "qt6quick.dll", "qt6qml.dll", "qt6qmlmodels.dll", "qt6pdf.dll", "qpdf.dll"}
a.binaries = [b for b in a.binaries if os.path.basename(b[0]).lower() not in UNUSED]
a.datas = [d for d in a.datas if not d[0].lower().endswith(".md")]  # the art guide is for developers

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="Ghostlet",
    console=False,
    icon="ghostlet/assets/ghost.ico",
    upx=False,
)
