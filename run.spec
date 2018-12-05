# -*- mode: python -*-

block_cipher = None


a = Analysis(['run.py'],
             pathex=['C:\\Documents and Settings\\testor\\Desktop\\FQM'],
             binaries=[],
             datas=[('arabic_reshaper\*', 'arabic_reshaper')],
             hiddenimports=["'email.mime.multipart'", "'win32com.client'", "'pythoncom'", "'email.mime.message'", "'email.mime.text'", "'email.mime.image'", "'email.mime.audio'", "'sqlalchemy.sql.default_comparator'", "'jinja2'"],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='favicon.ico')
