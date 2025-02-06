### DEFS ###
devMode = True
import atexit
import ctypes
import json
import os
import requests
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from zipfile import ZipFile

global currentGameVersion
response = requests.get("https://levelsharesquare.com/api/accesspoint/gameversion/SMC")
currentGameVersion = response.json().get("version")
ctypes.windll.shcore.SetProcessDpiAwareness(2)

def restoreGameFiles():
	"""Restores original game files"""
	for root, dirs, files in os.walk(os.path.join(temp_dir, "Unmodified Game Files")):
		for file in files:
			relativePath = os.path.relpath(os.path.join(root, file), os.path.join(temp_dir, "Unmodified Game Files"))
			gameFilesPath = os.path.join(gamePath, "www", relativePath)
			unmodifiedFilePath = os.path.join(root, file)
			if os.path.exists(unmodifiedFilePath):
				shutil.copy2(unmodifiedFilePath, gameFilesPath)
				if devMode:
					print(f"Restored {gameFilesPath} from {unmodifiedFilePath}\n")

def onExit():
	pass
	#shutil.rmtree(temp_dir, ignore_errors=True)

atexit.register(onExit)
temp_dir = tempfile.mkdtemp()
os.mkdir(temp_dir + "/Unmodified Game Files")

### /DEFS ###
### MISC DEFS ###
global modVars
modVars = {}
def saveAndPlay():
	global modifiedFiles, modVars
	modifiedFiles = {}
	# Save the current mod states to modsConfig
	for modName, var in modVars.items():
		modsConfig[modName]["Enabled"] = var.get()
		print(f"\n{modsConfig}")

	# Write the updated modsConfig to mods.json
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent=4)

	for item in os.listdir(modsPath):
		if not item:
			print("No items found!")
			messagebox.showerror("Error", "No items found!")
		if item.endswith(".zip") and os.path.isfile(modsPath + "/" + item):
			modFolderName = item[0:len(item)-4] # chop off .zip
			with ZipFile(modsPath + "/" + item, "r") as zip:
				zip.extractall(temp_dir + "/" + modFolderName)
				parseModFolder(temp_dir + "/" + modFolderName)
				if devMode:
					print(modFolderName + " extracted and parsed\n")
		else:
			pass
	runGame()

# Read settings.json
if os.path.exists("settings.json"):
	with open("settings.json") as f:
		settings = json.load(f)
else:
	with open("settings.json", "w") as f:
		json.dump({"GameLocation": "", "ModsLocation": "Mods"}, f, indent=4)
	with open("settings.json") as f:
		settings = json.load(f)

# Set game and mods location
def setGameLocation():
	"""Saves the game location to settings.json."""
	gamePath = filedialog.askdirectory()
	if gamePath and validateGameFolder(gamePath):
		settings["GameLocation"] = gamePath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent=4)
	else:
		setGameLocation()

def setModsLocation():
	"""Saves the mods folder location to settings.json."""
	modsPath = filedialog.askdirectory()
	if modsPath and validateModsFolder(modsPath):
		settings["ModsLocation"] = modsPath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent=4)
	else:
		setModsLocation()
### /MISC DEFS ###
### FUNCTIONS ###
# Function to update mods.json with new mod data
def updateModsConfig(modName, modData):
	"""Update mods.json with new mod data."""
	if modName not in modsConfig:
		modsConfig[modName] = {}
	# update mod data
	modsConfig[modName]["Enabled"] = modData.get("Enabled", modsConfig[modName].get("Enabled", False))
	modsConfig[modName]["Priority"] = modData.get("Priority", modsConfig[modName].get("Priority", 0))
	modsConfig[modName]["Version"] = modData.get("Version", modsConfig[modName].get("Version", "1.0"))
	modsConfig[modName]["GameAbbreviation"] = modData.get("GameAbbreviation", modsConfig[modName].get("GameAbbreviation", ""))
	modsConfig[modName]["GameVersion"] = modData.get("GameVersion", modsConfig[modName].get("GameVersion", ""))
	modsConfig[modName]["Description"] = modData.get("Description", modsConfig[modName].get("Description", ""))
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent=4)
	if devMode:
		print(f"Updated {modName} in mods.json")

# Sort mods by priority
def sortModsByPriority(modsConfig):
	"""Sort mods by priority."""
	return sorted(modsConfig.items(), key=lambda item: item[1].get("Priority", 0), reverse=False)

def refreshModsConfig():
	"""Refresh mods.json by unpacking zip files and reading their mod.json."""
	global modsConfig
	modsConfig = {}  # Clear existing modsConfig

	# Get a list of all mod zip files
	mod_zips = [item for item in os.listdir(modsPath) if item.endswith(".zip") and os.path.isfile(os.path.join(modsPath, item))]
	
	# Sort mods alphabetically
	mod_zips.sort()

	# Assign priorities alphabetically (lower alphabetically, higher priority number)
	for priority, item in enumerate(mod_zips, start=1):
		modFolderName = item[:-4]  # Remove .zip extension
		with ZipFile(os.path.join(modsPath, item), "r") as zip:
			# Extract only mod.json
			zip.extract("mod.json", path=os.path.join(temp_dir, modFolderName))
			modJSONPath = os.path.join(temp_dir, modFolderName, "mod.json")
			if os.path.exists(modJSONPath):
				with open(modJSONPath, "r") as f:
					modData = json.load(f)
				modName = modData.get("Name")
				if modName:
					modData["Priority"] = priority - 1  # Assign priority
					updateModsConfig(modName, modData)
					if devMode:
						print(f"{modFolderName} extracted and parsed\n")
	
	# Save the updated modsConfig to mods.json
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent=4)
	
	# Update the mod list in the GUI
	sortedMods = sortModsByPriority(modsConfig)
	createModList(sortedMods)
	
	# Clear the temp folder
	# Clear the contents of temp_dir without deleting the directory itself
	for item in os.listdir(temp_dir):
		item_path = os.path.join(temp_dir, item)
		if os.path.isfile(item_path) or os.path.islink(item_path):
			os.unlink(item_path)
		elif os.path.isdir(item_path):
			shutil.rmtree(item_path)
	os.mkdir(temp_dir + "/Unmodified Game Files")
	
	if devMode:
		print("Mods configuration refreshed.")
	
	# Save the updated modsConfig to mods.json
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent=4)
	
	# Update the mod list in the GUI
	sortedMods = sortModsByPriority(modsConfig)
	createModList(sortedMods)
	
	if devMode:
		print("Mods configuration refreshed.")

def toggleMod(modName, var):
	modsConfig[modName]["Enabled"] = var.get()
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent=4)

def showModInfo(modName, modData):
	info = f"Name: {modName}\nVersion: {modData.get('Version', '1.0')}\nDescription: {modData.get('Description', '')}"
	modInfoLabel.config(text=info)
	modInfoLabel.pack()

def hideModInfo():
	modInfoLabel.pack_forget()

# Parse a mod folder
def parseModFolder(modFolder):
	# Get mod.json
	modJSONPath = os.path.join(modFolder, "mod.json")
	if os.path.exists(modJSONPath):
		with open(modJSONPath, "r") as f:
			modData = json.load(f)
		modName = modData.get("Name")
		if modName:
			updateModsConfig(modName, modData)

			if modsConfig.get(modName, {}).get("Enabled", False):
				AssetsFolder = modData.get("AssetsFolder")
				if AssetsFolder:
					assetsPath = os.path.join(modFolder, AssetsFolder)
					if os.path.exists(assetsPath):
						processAssetsFolder(modName, assetsPath)
					else:
						print(f"Cannot find assets folder \"{assetsPath}\" for mod \"{modName}\"!")
						messagebox.showerror("Error", f"Cannot find assets folder \"{assetsPath}\" for mod \"{modName}\"!")
				else:
					print("\"AssetsFolder\" not specified in mod.json")
					messagebox.showerror("Error", f"\"AssetsFolder\" not specified in mod.json")
			else:
				print(f"Mod {modName} is not enabled or not specified in mods.json")
		else:
			print(f"\"Name\" not specified in mod.json")
			messagebox.showerror("Error", f"\"Name\" not specified in mod.json")
	else:
		print(f"mod.json not found in {modFolder}")
		messagebox.showerror("Error", f"mod.json not found in {modFolder}")

def processAssetsFolder(modName, assetsPath):
	"""Process the assets folder of a mod."""
	global modifiedFiles
	if "modifiedFiles" not in globals():
		modifiedFiles = {}

	modPriority = modsConfig[modName]["Priority"]
	for root, dirs, files in os.walk(assetsPath):
		for file in files:
			processFile(modName, modPriority, root, file, assetsPath)

def processFile(modName, modPriority, root, file, assetsPath):
	"""
	Process a file in the mod's assets folder.
	modName: The name of the mod.
	modPriority: The mod's priority.
	root: The root directory of the file.
	file: The file to process.
	assetsPath: The path to the mod's assets folder.
	"""
	# Get file paths
	relativePath = os.path.relpath(os.path.join(root, file), assetsPath)
	gameFilesPath = os.path.join(gamePath, "www", relativePath)
	unmodifiedFilePath = os.path.join(temp_dir, "Unmodified Game Files", relativePath)
	modFilePath = os.path.join(root, file)

	backupOriginalFile(gameFilesPath, unmodifiedFilePath)

	# get the previous mod priority
	previousModPriority = modifiedFiles.get(relativePath, None)
	if previousModPriority is None or modPriority < previousModPriority:
		shutil.copy2(modFilePath, gameFilesPath)
		modifiedFiles[relativePath] = modPriority
		if devMode:
			print(f"{modName} ({modPriority}) replaced {gameFilesPath}")
	else:
		if devMode:
			print(f"Skipping {modFilePath} because a higher-priority mod ({previousModPriority}) already modified it.")


def backupOriginalFile(gameFilesPath, unmodifiedFilePath):
	print(f"Backing up {gameFilesPath} to {unmodifiedFilePath}")
	os.makedirs(os.path.dirname(unmodifiedFilePath), exist_ok=True)
	if not os.path.exists(unmodifiedFilePath) and os.path.exists(gameFilesPath):
		shutil.copy(gameFilesPath, unmodifiedFilePath)

def startGame():
	runGame(True)

def runGame(reset=False):
	gameExecutable = os.path.join(gamePath, "Super Mario Construct.exe")
	if os.path.exists(gameExecutable):
		process = subprocess.Popen([gameExecutable], cwd=gamePath)
		while process.poll() is None:
			window.update()  # Keep the GUI responsive
			window.after(100)  # Wait for 100ms before checking again
		if devMode:
			print("Game exited")
		if devMode:
			print("------------------------")
		restoreGameFiles()
	else:
		print(f"Game executable not found at {gameExecutable}")
		messagebox.showerror("Error", f"Game executable not found at {gamePath}")

### /FUNCTIONS ###
### MAIN ###
## GET PATHS ##
gamePath = settings.get("GameLocation")
modsPath = settings.get("ModsLocation")

# Read or create mods.json
local_appdata_path = os.path.expandvars("%localappdata")
mods_json_path = modsPath + "/mods.json"
if not os.path.exists(modsPath):
	os.mkdir(modsPath)
if not os.path.exists(mods_json_path) or os.path.getsize(mods_json_path) == 0:
	with open(mods_json_path, "w") as f:
		json.dump({}, f, indent=4)
try:
	with open(mods_json_path) as f:
		modsConfig = json.load(f)
except json.JSONDecodeError as e:
	print(f"Error reading mods.json: {e}")
	modsConfig = {}
	messagebox.showerror("Error", f"Error reading mods.json: {e}")

# Check if SMC exists in the game path
def validateGameFolder(path):
	"""Check if SMC exists in the specified path."""
	if not os.path.exists(path + "/Super Mario Construct.exe"):
		print(f"Super Mario Construct not found at {path}!")
		messagebox.showerror("Error", f"Super Mario Construct not found at {path}!")
		return False
	else:
		return True

# Check if the mods path exists
def validateModsFolder(path):
	"""Check if the mods folder exists."""
	if not os.path.exists(path) or path == "":
		print(f"Mods Folder does not exist!")
		messagebox.showerror("Error", "Mods Folder does not exist!")
		return False
	else:
		return True
## /GET PATHS ##

## GUI ##
# Create the main window
window = tk.Tk()
def resource_path(relative_path):
	""" Get absolute path to resource, works for development and PyInstaller """
	try:
		base_path = sys._MEIPASS  # Temp directory for PyInstaller --onefile
	except AttributeError:
		base_path = os.path.abspath(".")  # Normal execution
	return os.path.join(base_path, relative_path)
icon_path = resource_path("icon.png")
window.iconphoto(True, tk.PhotoImage(file=icon_path))
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

# Frame to hold mod entries
modsFrame = tk.Frame(window)
modsFrame.pack(fill="both", expand=True, padx=10, pady=10)

# Create mod list in the GUI
def createModList(sortedMods):
	# clear mod list
	for widget in modsFrame.winfo_children():
		widget.destroy()

	# frame for Listbox and buttons
	frame = tk.Frame(modsFrame)
	frame.pack(fill="x", pady=2)

	# listbox to display mods
	modListbox = tk.Listbox(frame, width=50, height=10, activestyle="dotbox")
	modListbox.pack(side="left", padx=5)

	# frame for buttons
	buttonFrame = tk.Frame(frame)
	buttonFrame.pack(side="left", padx=5)

	# buttons for priority adjustments
	upButton = ttk.Button(buttonFrame, text="↑", width=3, command=lambda: moveMod(-1))
	upButton.pack(fill="none", pady=2)

	# refresh button
	refreshButton = ttk.Button(buttonFrame, text="🔄", width=3, command=refreshModsConfig)
	refreshButton.pack(fill="none", pady=2)

	downButton = ttk.Button(buttonFrame, text="↓", width=3, command=lambda: moveMod(1))
	downButton.pack(fill="none", pady=2)

	# Frame for mod info label
	modInfoFrame = tk.Frame(frame)
	modInfoFrame.pack(side="right", padx=10, fill="both", expand=True)

	# Add a canvas and scrollbar for the mod info label
	canvas = tk.Canvas(modInfoFrame, width=100, height=200)
	scrollbar = ttk.Scrollbar(modInfoFrame, orient="vertical", command=canvas.yview)
	scrollable_frame = tk.Frame(canvas	)

	# Configure the canvas to use the scrollbar
	scrollable_frame.bind(
		"<Configure>",
		lambda e: canvas.configure(
			scrollregion=canvas.bbox("all")
		)
	)

	canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
	canvas.configure(yscrollcommand=scrollbar.set)

	# Pack the canvas and scrollbar
	canvas.pack(side="left", fill="both", expand=True)
	scrollbar.pack(side="right", fill="y")

	# Mod info label inside the scrollable frame
	global modInfoLabel
	modInfoLabel = tk.Label(scrollable_frame, text="", justify="center", wraplength=200)  # Adjusted wraplength
	modInfoLabel.pack(fill="both", expand=True)


	# Store checkboxes' states
	global modVars
	modVars = {modName: tk.BooleanVar(value=modData.get("Enabled", False)) for modName, modData in sortedMods}
	def updateModList():
		modListbox.delete(0, tk.END)
		for modName, modData in sortedMods:
			checked = "✅ " if modVars[modName].get() else "⬜ "
			modListbox.insert(tk.END, f"{checked}{modName} - {modData.get('Version', '')} (Priority: {modData['Priority']})")

	def toggleModState():
		selected = modListbox.curselection()
		print(selected)
		if selected:
			index = selected[0]
			print(index)
			modName, modData = sortedMods[index]
			print(sortedMods[index])
			modVars[modName].set(not modVars[modName].get())  # Toggle state
			print(modVars[modName].get())
			print(sortedMods[index])
			updateModList()

	def moveMod(direction):
		selected = modListbox.curselection()
		if selected:
			index = selected[0]
			newIndex = index + direction

			if 0 <= newIndex < len(sortedMods):
				# Swap mods in the sorted list
				sortedMods[index], sortedMods[newIndex] = sortedMods[newIndex], sortedMods[index]

				# Update priority values accordingly
				sortedMods[index][1]["Priority"], sortedMods[newIndex][1]["Priority"] = (
					sortedMods[newIndex][1]["Priority"],
					sortedMods[index][1]["Priority"],
				)

				 # Save updated priorities to mods.json
				with open(mods_json_path, "w") as f:
					json.dump(modsConfig, f, indent=4)

				# Refresh UI & reselect moved item
				updateModList()
				modListbox.selection_set(newIndex)

	def onModSelect(event):
		selected = modListbox.curselection()
		if selected:
			index = selected[0]
			modName, modData = sortedMods[index]
			description = modData.get("Description", "No description available.")
			modInfoLabel.config(text=f"{description}")
			canvas.yview_moveto(0)

	# Bind selection event to update mod info label
	modListbox.bind("<<ListboxSelect>>", onModSelect)

	# Bind double-click to toggle mod state
	modListbox.bind("<Double-Button-1>", lambda e: toggleModState())

	# Frame for buttons
	buttonsFrame = tk.Frame(modsFrame)
	buttonsFrame.pack(pady=10)

	# Save & Play button
	SavePlayBtn = ttk.Button(buttonsFrame, text="Save & Play", command=saveAndPlay)
	SavePlayBtn.pack(side="left", padx=5)

	# Play Without Mods button
	PlayBtn = ttk.Button(buttonsFrame, text="Play Without Mods", command=startGame)
	PlayBtn.pack(side="left", padx=5)

	# Initialize the mod list
	updateModList()

# Label to show mod info on hover
modInfoLabel = tk.Label(window, text="", justify="left")
modInfoLabel.pack_forget()

# Sort mods by priority and create mod list
sortedMods = sortModsByPriority(modsConfig)
createModList(sortedMods)

# Create a label
gameVersionLabel = tk.Label(window, text="")
gameVersionLabel.pack(pady=10)
gameVersionLabel.config(text=f"Current Game Version: {currentGameVersion}")


# Run the application
window.mainloop()
## /GUI ##
### /MAIN ###