# -*- mode: python ; coding: utf-8 -*-

hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'requests',
    'queue', 
    'urllib3'
    'urllib.parse',
    'hashlib',
    'json',
    're',
    'os',
    'sys',
    'subprocess',
]

# Анализ скрипта
a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('FutureMinds.ico', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5'],
    noarchive=False,
    optimize=2,
)

# Упаковка
pyz = PYZ(a.pure)

# Создание EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FutureMinds',
    debug=False,
    bootloader_ignore_signals=True, 
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./FutureMinds.ico',
    version='version.txt'
)

exe.manifest = "pixelToo Lab"


try:
    exec(open('launcher.py').read())
except Exception as e:
    with open('error.txt', 'w', encoding='utf-8') as f:
        f.write(f"ERROR: {e}\n")
