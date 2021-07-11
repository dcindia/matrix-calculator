# -*- mode: python ; coding: utf-8 -*-
from kivymd import hooks_path as kivymd_hooks_path
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal
block_cipher = None

depedencies = get_deps_minimal(audio=None, video=None, window=True)

def get_dependencies(included, mode):
    extras = depedencies[mode]
    included.extend(extras)
    return included

a = Analysis(['./../main.py'],
             pathex=['./../'],
             binaries=get_dependencies([], 'binaries'),
             datas=[('./../matrixcalculator.kv','.'),('./../assets/','assets')],
             hiddenimports=get_dependencies([], 'hiddenimports'),
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=get_dependencies(['pillow', 'numpy', 'docutils', 'pigments', 'gi', 'tcl', 'tk', 'PIL', 'ffpyplayer'], 'excludes'),
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='MatrixCalculator.AppImage',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)
