# -*- mode: python ; coding: utf-8 -*-
#
# Rebuild with: pyinstaller almeida.spec
#
# Produces a single portable "Almeida - Estoque e Vendas.exe" under dist/.
# CustomTkinter's own theme/font data is collected automatically by the
# hook-customtkinter.py shipped in pyinstaller-hooks-contrib.
#
# The database and item images are intentionally NOT bundled here - they are
# created next to the .exe on first run (see src/app_paths.py) so the client's
# data survives between launches instead of living inside PyInstaller's
# disposable per-run extraction folder.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('src/database/schema.sql', 'src/database')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Almeida - Estoque e Vendas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/logo.ico'],
)
