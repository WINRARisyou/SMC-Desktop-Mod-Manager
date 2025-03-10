# -*- mode: python ; coding: utf-8 -*-
# linux tkinter location: config/.local/lib/python3.12/site-packages/tkinterdnd2 --- gitpod location: /workspace/.pyenv_mirror/user/current/lib/python3.12/site-packages/tkinterdnd2
a = Analysis(
	['main.py'],
	pathex=[],
	binaries=[('modules', 'modules'), (os.path.join(os.getenv('LOCALAPPDATA'), 'Programs\\Python\\Python313\\Lib\\site-packages\\tkinterdnd2'), 'tkinterdnd2')],
	datas=[('icons/icon-512.png', 'icons/.'), ('images','images')],
	hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL._tkinter_finder', 'PIL._imagingtk', 'tkinter.scrolledtext', 'tkinter.dnd', 'tkinterdnd2', 'TkinterDnD', 'tkdnd'],
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
	name='SuperMarioConstructModManager',
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
	icon=['icons\\icon-combined.ico'],
	version='versionFile.txt'
)
