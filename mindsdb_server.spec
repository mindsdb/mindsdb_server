from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import sysconfig
site_packages_path = sysconfig.get_paths()["purelib"]

block_cipher = None

a = Analysis(['entrypoint.py'],
             pathex=[site_packages_path],
             binaries=[],
             datas=[(f'{site_packages_path}/sacremoses/data/perluniprops',
                     'sacremoses/data/perluniprops'),
                    (f'{site_packages_path}/imagehash/VERSION',
                     'imagehash'),
                    (f'{site_packages_path}/flask_restx/templates',
                     'flask_restx/templates')
                    ],
             hiddenimports=['torch',
                            'torchvision',
                            'lightwood',
                            'numpy',
                            'pandas'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='mindsdb_server',
          debug=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='mindsdb_server')
