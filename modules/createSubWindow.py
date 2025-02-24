import tkinter as tk
from . import resourcePath as resPath
def createSubWindow(baseWindow: str, name: str, icon: str, size:list=[640,360]):
	"""
	:param baseWindow (str): The root window the sub window is attatched to.
	:param name (str): The name of the window.
	:param icon (str): The path to the icon the window uses.
	:param size (list): The width and height of the window, i.e. [640,360]
	:return tk.TopLevel: A callback to the created sub window
	"""
	subWindow = tk.Toplevel(baseWindow)  # Create a sub-window
	subWindow.iconphoto(True, tk.PhotoImage(file=resPath.resource_path(f"{icon}")))
	subWindow.title(f"{name}")
	subWindow.geometry(f"{size[0]}x{size[1]}")
	subWindow.attributes('-topmost', True)
	subWindow.after(10, lambda: subWindow.focus_set())
	subWindow.after(11, lambda: subWindow.attributes('-topmost', False))
	return subWindow