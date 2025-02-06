### DEFS ###
import atexit
import ctypes
import json
import os
import shutil
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog
from zipfile import	ZipFile
ctypes.windll.shcore.SetProcessDpiAwareness(2)
def onExit():
	# Restore original game files
	for root, dirs, files in os.walk(os.path.join(temp_dir, "Unmodified Game Files")):
		for file in files:
			relativePath = os.path.relpath(os.path.join(root, file), os.path.join(temp_dir, "Unmodified Game Files"))
			gameFilePath = os.path.join(gamePath, "www", relativePath)
			unmodifiedFilePath = os.path.join(root, file)
			if os.path.exists(unmodifiedFilePath):
				shutil.copy2(unmodifiedFilePath, gameFilePath)
				print(f"Restored {gameFilePath} from {unmodifiedFilePath}")
	shutil.rmtree(temp_dir, ignore_errors=True)
atexit.register(onExit)
temp_dir = tempfile.mkdtemp()
os.mkdir(temp_dir + "/Unmodified Game Files")
### /DEFS ###
### MISC DEFS ###
def onButtonClick():
	label.config(text="Button Clicked!")

# Read settings.json
if not os.path.exists("settings.json"):
	with open("settings.json", "w") as f:
		json.dump({"GameLocation": "", "ModsLocation": ""}, f, indent=4)
	with open("settings.json") as f:
		settings = json.load(f)
else:
	with open("settings.json") as f:
		settings = json.load(f)

# Define functions to set game and mods location
def setGameLocation():
	gamePath = filedialog.askdirectory()
	if gamePath:
		settings["GameLocation"] = gamePath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent=4)
		print(f"Game location set to: {gamePath}")

def setModsLocation():
	modsPath = filedialog.askdirectory()
	if modsPath:
		settings["ModsLocation"] = modsPath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent=4)
		print(f"Mods location set to: {modsPath}")
	os.mkdir(modsPath + "/" + "Unmodified Game Files")
### /MISC DEFS ###
### FUNCTIONS ###

# Parse a mod folder
def parseModFolder(modFolder):
	modJSONPath = os.path.join(modFolder, "mod.json")
	if os.path.exists(modJSONPath):
		with open(modJSONPath, "r") as f:
			modData = json.load(f)
		AssetsFolder = modData.get("AssetsFolder")
		if AssetsFolder:
			assetsPath = os.path.join(modFolder, AssetsFolder)
			if os.path.exists(assetsPath):
				for root, dirs, files in os.walk(assetsPath):
					for file in files:
						relativePath = os.path.relpath(os.path.join(root, file), assetsPath)
						gameFilePath = os.path.join(gamePath, "www", relativePath)
						unmodifiedFilePath = os.path.join(temp_dir, "Unmodified Game Files", relativePath)

						# Create directories in Unmodified Game Files if they don't exist
						os.makedirs(os.path.dirname(unmodifiedFilePath), exist_ok=True)

						# Copy the original game file to Unmodified Game Files if it doesn't already exist
						if not os.path.exists(unmodifiedFilePath):
							if os.path.exists(gameFilePath):
								shutil.copy2(gameFilePath, unmodifiedFilePath)
								#print(f"Copied {gameFilePath} to {unmodifiedFilePath}")
							else:
								print(f"Game file {gameFilePath} does not exist!")

						# Replace the game file with the mod file
						modFilePath = os.path.join(root, file)
						if os.path.exists(modFilePath):
							shutil.copy2(modFilePath, gameFilePath)
							#print(f"Replaced {gameFilePath} with {modFilePath}")
						else:
							print(f"Mod file {modFilePath} does not exist!")
			else:
				print(f"Assets folder {assetsPath} does not exist!")
		else:
			print("\"AssetsFolder\" not specified in mod.json")
	else:
		print(f"mod.json not found in {modFolder}")

def runGame():
	gameExecutable = os.path.join(gamePath, "Super Mario Construct.exe")
	if os.path.exists(gameExecutable):
		process = subprocess.Popen([gameExecutable], cwd=gamePath)
		process.wait()
		onExit()
	else:
		print(f"Game executable not found at {gameExecutable}")

def applyMods():
	# Sort mods by priority
	sorted_mods = sorted(mods_config.items(), key=lambda x: x[1]["Priority"], reverse=True)
	for mod_name, mod_info in sorted_mods:
		if mod_info["Enabled"]:
			modFolderName = mod_name
			modFolderPath = os.path.join(temp_dir, modFolderName)
			if os.path.exists(modFolderPath):
				parseModFolder(modFolderPath)
			else:
				print(f"Mod folder {modFolderPath} does not exist!")

### /FUNCTIONS ###
### MAIN ###
## GET PATHS ##
gamePath = settings.get("GameLocation")
modsPath = settings.get("ModsLocation")

# Read or create mods.json
mods_json_path = os.path.join(modsPath, "mods.json")
print(mods_json_path)
if not os.path.exists(mods_json_path):
	with open(mods_json_path, "w") as f:
		json.dump({}, f, indent=4)

with open(modsPath + "/" + "mods.json", "r") as f:
	mods_config = json.load(f)

# Check if SMC exists in the game path
if not os.path.exists(gamePath + "/Super Mario Construct.exe"):
	print(f"Super Mario Construct not found at {gamePath}!")
	#exit()

# Check if the mods path exists
if not os.path.exists(modsPath) or modsPath == "":
	print(f"Mods Folder does not exist!")
	#exit()
else:
	print(f"\nFiles and Folders in {modsPath}")
	for item in os.listdir(modsPath):
		if not item:
			print("No items found!")

		if item.endswith(".zip") and os.path.isfile(modsPath + "/" + item):
			modFolderName = item[0:len(item)-4]
			with ZipFile(modsPath + "/" + item, "r") as zip:
				zip.extractall(temp_dir + "/" + modFolderName)
				#print(f"Extracted {item} to {temp_dir}/{modFolderName}")
		else:
			pass
			#print(f"\"{item}\" is not a .zip file.")

applyMods()
runGame()

# print(f"\nFiles and Folders in {gamePath}")
# for item in os.listdir(gamePath + "/www"):
# 	print(item)
## /GET PATHS ##


## GUI ##
# Create the main window
window = tk.Tk()
window.iconphoto(False, tk.PhotoImage(file='icon.png'))
window.title("SMC Desktop Mod Loader")
window.geometry("832x480")

# Create a menu bar
menuBar = tk.Menu(window)
window.config(menu=menuBar)

# Create a File menu
filesMenuBar = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="File", menu=filesMenuBar)

# Add commands to the File menu
filesMenuBar.add_command(label="Set Game Location", command=setGameLocation)
filesMenuBar.add_command(label="Set Mods Folder Location", command=setModsLocation)
filesMenuBar.add_separator()
filesMenuBar.add_command(label="Exit", command=window.quit)
# Create a label
label = tk.Label(window, text="Hello, Tkinter!")
label.pack(pady=10)

# Create a button
button = tk.Button(window, text="Click Me", command=onButtonClick)
button.pack(pady=10)

# Run the application
window.mainloop()
## /GUI ##
### /MAIN ###