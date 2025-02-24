from PIL import Image, ImageTk
import tkinter as tk
from . import createSubWindow as subWindow, resourcePath as resPath

def getScalingFactor():
	"""Get the system's DPI scaling factor."""
	root = tk.Tk()
	root.tk.call('tk', 'scaling') #default scaling factor
	scaling_factor = root.tk.call('tk', 'scaling') / 1.5
	root.destroy()
	return scaling_factor

def createAboutWindow(baseWindow):
	about = subWindow.createSubWindow(baseWindow, "About", "icons/icon-512.png", [640,700])
	about.resizable(False, False)
	banner_image = Image.open(resPath.resource_path("images/banner2.png"))
	scaling_factor = getScalingFactor()
	new_width = int(640 * scaling_factor)
	original_width, original_height = banner_image.size
	new_height = int((new_width / original_width) * original_height)
	banner_image = banner_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
	banner_photo = ImageTk.PhotoImage(banner_image)

	# Display the image in a Label
	banner_label = tk.Label(about, image=banner_photo)
	banner_label.image = banner_photo
	banner_label.pack(pady=0)
	info = tk.Label(about, wraplength=int(480 * scaling_factor), text="SMC Desktop Mod Manager (SMC-DMM) is a tool aimed at simplifying modding for Super Mario Construct. You can quickly manage, install, and organize your mods in just a few clicks, the Mod Manager does all the behind the scenes stuff for you, letting you focus on customizing your game.")
	info.pack(pady=10)

	creditsFrame = tk.Frame(about)
	creditsFrame.pack(pady=0)
	creditsFrame.config(background="#1e1e1e")
	creditsLabel = tk.Label(creditsFrame, text="Credits:\nTODO")
	creditsLabel.pack(pady=0)