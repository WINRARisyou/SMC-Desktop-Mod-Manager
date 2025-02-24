import os
import sys
def resource_path(relative_path):
	""" Get absolute path to resource, works for development and PyInstaller """
	try:
		base_path = sys._MEIPASS # Temp directory for PyInstaller
	except AttributeError:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)