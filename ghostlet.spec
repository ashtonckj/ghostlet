# PyInstaller build config. Build with:  python -m PyInstaller ghostlet.spec
# Output: dist/Ghostlet.exe (single file, no console, Python + PySide6 bundled).

a = Analysis(
    ["run_ghostlet.py"],
    datas=[("ghostlet/assets", "ghostlet/assets")],
)
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
