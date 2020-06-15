# -*- mode: python -*-

block_cipher = None


a = Analysis(['run.py'],
             pathex=['/Users/mrf3/Documents/FQM'],
             binaries=[],
             datas=[('arabic_reshaper/*', 'arabic_reshaper')],
             hiddenimports=[
                'app.gui', 'PyQt5', 'PyQt5.QtWidgets', 'email.mime.multipart', 'win32com.client',
                'email.mime.message', 'email.mime.text', 'email.mime.image', 'email.mime.audio',
                'sqlalchemy.sql.default_comparator', 'jinja2', 'logging.config'
            ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=False ,
          icon='/Users/mrf3/Documents/FQM/static/images/favicon.ico')
