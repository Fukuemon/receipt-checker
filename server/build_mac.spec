# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app_execute.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/fuku079/.pyenv/versions/miniforge3-23.3.1-1/envs/auto_receipt/lib/python3.10/site-packages/customtkinter', 'customtkinter/')],
    hookspath=['./hooks'],
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
    [],
    exclude_binaries=True,
    name='receipt_checker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='receipt_checker',
)
app = BUNDLE(
    coll,
    name='receipt_checker.app',
    icon="static/receipt_checker.ico",
    bundle_identifier=None,
)
