# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files
import pathlib
import os

block_cipher = None
datas = []
datas += collect_data_files("babelfish")
datas += collect_data_files("guessit")
datas += collect_data_files("autosync")
datas += collect_data_files("imageio_ffmpeg")
datas += [('saved_models/', 'saved_models')]

files_to_analyze = [
  os.path.join('autosync','ui.py')
]

path_exts = [
  #os.path.join(HOMEPATH, 'scipy', 'extra-dll'),
]

a = Analysis(
  files_to_analyze,
  pathex=path_exts,
  binaries=[],
  datas=datas,
  hiddenimports=[
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree',
    'sklearn.tree._utils',
    'babelfish.converters.alpha3b',
    'babelfish.converters.alpha3t',
    'babelfish.converters.alpha2',
    'babelfish.converters.name',
    'babelfish.converters.countryname',
    'babelfish.converters.opensubtitles',
    'babelfish.converters.scope',
    'babelfish.converters.type',
  ],
  hookspath=[],
  runtime_hooks=[],
  excludes=[
    'pytest'
  ],
  win_no_prefer_redirects=False,
  win_private_assemblies=False,
  cipher=block_cipher
)

for i in range(len(a.binaries)):
  dest, origin, kind = a.binaries[i]
  if '_pywrap_tensorflow_internal' in dest:
    a.binaries[i] = ('tensorflow.python.' + dest, origin, kind)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
  pyz,
  a.scripts,
  exclude_binaries=True,
  name='CaptionPal',
  debug=False,
  strip=False,
  upx=True,
  console=True
)

coll = COLLECT(
  exe,
  a.binaries,
  a.zipfiles,
  a.datas,
  strip=False,
  upx=True,
  name='CaptionPal'
)
