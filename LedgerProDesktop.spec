# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('database/schema.sql', 'database'),
        ('database/schema_mysql.sql', 'database'),
        ('config.json', '.')
    ],
    hiddenimports=[
        'PySide6.QtPrintSupport',
        'PySide6.QtPdf',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'reportlab',
        'pymysql',
        'bcrypt',
        'matplotlib',
        'pandas',
        'openpyxl'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'scipy',
        'kivy',
        'kivymd',
        'tkinter',
        'IPython',
        'notebook',
        'tornado',
        'pytest',
        'unittest',
        'sphinx',
        'jedi',
        'sympy',
        'pyarrow',
        'numba',
        'llvmlite',
        'fsspec'
    ],
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
    name='TSL SwiftBill ERP',
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
    icon=['tsl_icon.ico'],
)
