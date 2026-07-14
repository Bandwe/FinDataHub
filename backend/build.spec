# -*- mode: python ; coding: utf-8 -*-

import os


backend_dir = os.path.abspath(SPECPATH)
static_dir = os.path.join(backend_dir, 'static')

datas = []
if os.path.isdir(static_dir):
    datas.append((static_dir, 'static'))

hiddenimports = [
    'openpyxl.cell._writer',
    'openpyxl.styles',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.np_datetime',
]

a = Analysis(
    ['desktop_entry.py'],
    pathex=[backend_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'pytest'],
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
    name='FinDataHub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
