### WINRARisyou was here
### Give credit if you use this code
### IMPORTS ###
devMode = True
global managerVersion
managerVersion = "2.0.0-alpha"
import argparse
import atexit
import ctypes
import json
import orjson
import os
import platform
import requests
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from zipfile import ZipFile
import webbrowser
from modules import *
from modules import resourcePath as resPath
### /IMPORTS ###
### GLOBALS ###
global onWindows
onWindows = platform.system() == "Windows"
if onWindows: ctypes.windll.shcore.SetProcessDpiAwareness(2)

def onExit():
	# Remove temporary directory
	shutil.rmtree(temp_dir, ignore_errors=True)
	# Delete files that were marked as missing
	for file in modFiles:
		if os.path.exists(file):
			os.remove(file)
	# Save window size
	global settings
	winWidth = settings.get("Width")
	winHeight = settings.get("Height")
	settings = {}
	with open("settings.json", "r") as f:
		settings = json.load(f)
	with open("settings.json", "w") as f:
		settings["Width"] = winWidth
		settings["Height"] = winHeight
		json.dump(settings, f, indent="\t")
	# nuke modifiedFiles.json
	if os.path.exists(os.path.join(gamePath, "modifiedFiles.json")):
		os.remove(os.path.join(gamePath, "modifiedFiles.json"))

atexit.register(onExit)
temp_dir = tempfile.mkdtemp()
os.mkdir(os.path.join(temp_dir, "Unmodified Game Files"))

# Create the main window. moved up for the console window
window = TkinterDnD.Tk() #DnD stands for drag and drop
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Enable separate console window")
args = parser.parse_args()
# Initialize debug window if requested
if args.debug:
	devMode = True
	consoleWindow = debugWindow.DebugWindow(window)

global allModVersions
allModVersions = {}
global criticallyOutdated
criticallyOutdated = False
global gamePath
gamePath = None
global gameVersion
gameVersion = None
global latestGameVersion, latestManagerVersion
latestGameVersion = latestManagerVersion = None
global installedMods
installedMods = {}
global mods_json_path
mods_json_path = None
global modsPath
modsPath = None
global modFiles
modFiles = []
global modifiedFiles
modifiedFiles = {}
global modVars
modVars = {}
global outdatedMods
outdatedMods = []
global SelectedMod, settings
SelectedMod = settings = None
global updateType
updateType = None
global winWidth, winHeight
winWidth = winHeight = 0
global modListbox
modListbox = None
global onlineModData
onlineModData = []
### /GLOBALS ###
### FUNCTIONS ###
def backupOriginalFile(gameFilesPath, unmodifiedFilePath):
	if os.path.exists(gameFilesPath):
		if devMode: print(f"Backing up {gameFilesPath} to {unmodifiedFilePath}")
		os.makedirs(os.path.dirname(unmodifiedFilePath), exist_ok=True)
		if not os.path.exists(unmodifiedFilePath):
			shutil.copy(gameFilesPath, unmodifiedFilePath)
	else:
		# If the game file doesn't exist, mark it for deletion when the game is closed
		print(f"Marking {gameFilesPath} for deletion")
		if not os.path.isdir(gameFilesPath):
			modFiles.append(gameFilesPath)

def bringWindowToFront():
	window.attributes("-topmost", True)
	window.after(10, lambda: window.focus_set())
	window.after(11, lambda: window.attributes("-topmost", False))

def checkForModUpdates():
	def changeText(mod):
		global modListbox, outdatedMods
		for i in range(modListbox.size()):
			if modListbox.get(i).startswith(f"⬜ {mod["Mod Name"]}") or modListbox.get(i).startswith(f"✅ {mod["Mod Name"]}"):
				modListbox.itemconfig(i, {"fg": "orange"})
				outdatedMods.append(mod["Mod ID"])
				break

	for modID in modsConfig:
		installedMods[modID] = modsConfig[modID]["Version"]
	global onlineModData
	for mod in onlineModData:
		if mod["Mod ID"] in installedMods:
			print(f"{mod["Mod ID"]} is installed")
			if mod["Mod ID"] in outdatedMods:
				outdatedMods.remove(mod["Mod ID"])
				for i in range(modListbox.size()):
					if modListbox.get(i).startswith(f"⬜ {mod["Mod Name"]}") or modListbox.get(i).startswith(f"✅ {mod["Mod Name"]}"):
						modListbox.itemconfig(i, {"fg": "black"})
						break
			onlineModVersion = int("".join(filter(str.isdigit, mod["Mod Version"])))
			installedModVersion = int("".join(filter(str.isdigit, installedMods[mod["Mod ID"]])))
			if onlineModVersion > installedModVersion and len(str(onlineModVersion)) == len(str(installedModVersion)):
				if devMode: print("online   ", onlineModVersion)
				if devMode: print("installed", installedModVersion)
				if devMode: print(f"{mod["Mod ID"]} has an update")
				changeText(mod)
			
			if len(str(onlineModVersion)) > len(str(installedModVersion)):
				if devMode: print(f"online mod version is longer than installed mod version")
				if devMode: print("before normalization")
				if devMode: print("online   ", onlineModVersion)
				if devMode: print("installed", installedModVersion)
				for i in range(abs(len(str(onlineModVersion)) - len(str(installedModVersion)))):
					installedModVersion *= 10
				if devMode: print("after normalization")
				if devMode: print("online   ", onlineModVersion)
				if devMode: print("installed", installedModVersion)
			
			elif len(str(installedModVersion)) > len(str(onlineModVersion)):
				if devMode: print(f"installed mod version is longer than online mod version")
				if devMode: print("before normalization")
				if devMode: print("installed", installedModVersion)
				if devMode: print("online   ", onlineModVersion)
				for i in range(abs(len(str(onlineModVersion)) - len(str(installedModVersion)))):
					onlineModVersion *= 10
				if devMode: print("after normalization")
				if devMode: print("installed", installedModVersion)
				if devMode: print("online   ", onlineModVersion)
			
			if onlineModVersion > installedModVersion:
				print(f"{mod["Mod ID"]} has an update")
				changeText(mod)
		else:
			print(mod["Mod ID"])
			if mod["Mod ID"] in outdatedMods:
				outdatedMods.remove(mod["Mod ID"])
				print(outdatedMods)

def copyModFile():
	copyModFiles = filedialog.askopenfiles(title="Please select Mod File(s)", filetypes=[("ZIP files", "*.zip")], multiple=True)
	if copyModFiles:
		for file in copyModFiles:
			if file.name.endswith(".zip"):
				shutil.copy2(file.name, modsPath)
				if devMode:	print(f"Copied {file.name} to {modsPath}")
				refreshModsConfig()
			else:
				print("Invalid file type. Please select a .zip file.")
				messagebox.showerror("Error", "Invalid file type. Please select a .zip file.")

def crashDetection():
	if os.path.exists(os.path.join(gamePath, "modifiedFiles.json")):
		with open(os.path.join(gamePath, "modifiedFiles.json"), "r") as file:
			modifiedFiles = json.load(file)

			# remove the pyinstaller directory if compiled
			if "_MEIPASS" in modifiedFiles and os.path.exists(modifiedFiles["_MEIPASS"]):
				shutil.rmtree(modifiedFiles["_MEIPASS"])
				
			oldTempDir = modifiedFiles["oldTempDir"]

			# delete any lingering mod files
			for modFile in modifiedFiles["modFiles"]:
				if devMode: print(os.path.join(gamePath, "www", modFile))
				if os.path.exists(os.path.join(gamePath, "www", modFile)):
					if os.path.isdir(os.path.join(gamePath, "www", modFile)):
						shutil.rmtree(os.path.join(gamePath, "www", modFile))
					else:
						os.remove(os.path.join(gamePath, "www", modFile))

			# copy unmodified files back, otherwise warn user that files couldn't be recovered
			if os.path.exists(oldTempDir):
				for gameFile in modifiedFiles["gameFiles"]:
					if devMode: print(os.path.join(oldTempDir, "Unmodified Game Files", gameFile))
					if devMode: print(os.path.join(gamePath, "www", gameFile))
					shutil.copy2(os.path.join(oldTempDir, "Unmodified Game Files", gameFile), os.path.join(gamePath, "www", gameFile))
				shutil.rmtree(oldTempDir)
				messagebox.showinfo("Crashed last exit", "DMM crashed the last time it ran, and it has detected some lingering mod files.\nIt has attempted crash recovery, but everything may not have been fixed.\nPlease launch without mods, and if everything is normal, then continue on with your day. Otherwise, you will need to redownload SMC (your levels will stay intact).")
			else:
				messagebox.showwarning("Crashed last exit", "DMM crashed the last time it ran, and it has detected some lingering mod files.\nIt has attempted crash recovery, but some game files could not be recovered.\nYou will need to redownload SMC to fix any files that mods changed (your levels will stay intact).")
		if os.path.exists(os.path.join(gamePath, "modifiedFiles.json")):
			os.remove(os.path.join(gamePath, "modifiedFiles.json"))

def makeWebRequest(url: str, timeout: int, exceptionText: str):
	"""
	Makes a web request to the desired URL.\n
	:param url: URL of the web request
	:param timeout: Time in seconds before the request should time out
	:param exceptionText: Text to return if the request fails
	"""
	try:
		response = requests.get(url, timeout=timeout)
		if response == None or not response.ok:
			if devMode:
				print(f"Request failed, response status code: {response.status_code}")
			return exceptionText
		return response
	except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
		if devMode: print(f"Request failed, exception: {e}")
		return exceptionText

def openGameFolder():
	if onWindows:
		os.startfile(gamePath)
	else:
		subprocess.Popen(["xdg-open", gamePath])

def openModFolder():
	if onWindows:
		os.startfile(modsPath)
	else:
		subprocess.Popen(["xdg-open", modsPath])

def parseModFolder(modFolder):
	# Get mod.json
	modJSONPath = os.path.join(modFolder, "mod.json")
	if os.path.exists(modJSONPath):
		with open(modJSONPath, "r") as f:
			modData = json.load(f)
		modName = modData.get("Name")
		modID = modData.get("ID") # Get the mod's ID
		if modName and modID:
			global allModVersions
			allModVersions[modID] = modData.get("GameVersion")
			if modsConfig.get(modID, {}).get("Enabled", False): # Use modID to check if enabled
				AssetsFolder = modData.get("AssetsFolder")
				if AssetsFolder:
					assetsPath = os.path.join(modFolder, AssetsFolder)
					if os.path.exists(assetsPath):
						processAssetsFolder(modID, assetsPath)
					else:
						if devMode: print(f"Cannot find assets folder \"{assetsPath}\" for mod \"{modName}\"!")
						messagebox.showerror("Error", f"Cannot find assets folder \"{assetsPath}\" for mod \"{modName}\"!")
				else:
					if devMode: print("\"AssetsFolder\" not specified in mod.json")
					messagebox.showerror("Error", f"\"AssetsFolder\" not specified in mod.json")
			else:
				print(f"Mod {modName} is not enabled in mods.json")
		else:
			if devMode: print(f"\"Name\" or \"ID\" not specified in mod.json")
			messagebox.showerror("Error", f"\"Name\" or \"ID\" not specified in mod.json")
	else:
		if devMode: print(f"mod.json not found in {modFolder}")
		messagebox.showerror("Error", f"mod.json not found in {modFolder}")

def processAssetsFolder(modID, assetsPath):
	"""Process the assets folder of a mod."""
	global modifiedFiles
	if "modifiedFiles" not in globals():
		modifiedFiles = {}

	modPriority = modsConfig[modID]["Priority"]
	for root, dirs, files in os.walk(assetsPath):
		for file in files:
			processFile(modID, modPriority, root, file, assetsPath)

def processFile(modID, modPriority, root, file, assetsPath):
	"""
	Process a file in the mod's assets folder.\n
	:param modID: The ID of the mod.
	:param modPriority: The mod's priority.
	:param root: The root directory of the file.
	:param file: The file to process.
	:param assetsPath: The path to the mod's assets folder.
	"""
	# Get file paths
	relativePath = os.path.relpath(os.path.join(root, file), assetsPath)
	gameFilesPath = os.path.join(gamePath, "www", relativePath)
	unmodifiedFilePath = os.path.join(temp_dir, "Unmodified Game Files", relativePath)
	modFilePath = os.path.join(root, file)

	if not os.path.exists(os.path.dirname(gameFilesPath)): # This means a mod created the directory
		print(f"Marking {os.path.dirname(gameFilesPath)} for deletion")
		modFiles.append(os.path.dirname(gameFilesPath))

	os.makedirs(os.path.dirname(gameFilesPath), exist_ok=True)

	backupOriginalFile(gameFilesPath, unmodifiedFilePath)

	# get the previous mod priority
	previousModPriority = modifiedFiles.get(relativePath, None)
	if devMode: print(f"Current mod priority is {modPriority}, previous mod priority is {previousModPriority}")
	if previousModPriority is None or modPriority < previousModPriority:
		shutil.copy2(modFilePath, gameFilesPath)
		modifiedFiles[relativePath] = modPriority
		if devMode: print(f"{modID} (Priority: {modPriority}) replaced {gameFilesPath}")
	else:
		if devMode:	print(f"Skipping {modFilePath} because a higher-priority mod ({previousModPriority}) already modified it.")
	
	moddedFiles = []
	for path in modFiles:
		moddedFiles.append(os.path.relpath(os.path.join(path), os.path.join(gamePath, "www")))
	
	gameFiles = []
	for path in modifiedFiles:
		if not path in moddedFiles:
			gameFiles.append(path)

	with open(os.path.join(gamePath, "modifiedFiles.json"), "w"):
		if getattr(sys, "frozen", False):
			pyinstallerPath = sys._MEIPASS
			with open(os.path.join(gamePath, "modifiedFiles.json"), "w") as f:
				json.dump({"_MEIPASS": pyinstallerPath, "oldTempDir": temp_dir, "modFiles": moddedFiles, "gameFiles": gameFiles}, f, indent="\t")
		else:
			with open(os.path.join(gamePath, "modifiedFiles.json"), "w") as f:
				json.dump({"oldTempDir": temp_dir, "modFiles": moddedFiles, "gameFiles": gameFiles}, f, indent="\t")

def readSettingsJSON():
	global gamePath, settings, mods_json_path, modsPath, winWidth, winHeight
	if os.path.exists("settings.json"):
		with open("settings.json") as f:
			settings = json.load(f)
		gamePath = settings.get("GameLocation")
		modsPath = settings.get("ModsLocation")
		if settings.get("Width") == None or type(settings.get("Width")) != int:
			with open("settings.json", "w") as f:
				settings["Width"] = 832
				json.dump(settings, f, indent="\t")
		if settings.get("Height") == None or type(settings.get("Height")) != int:
			with open("settings.json", "w") as f:
				settings["Height"] = 480
				json.dump(settings, f, indent="\t")
		winWidth = settings.get("Width")
		winHeight = settings.get("Height")
		mods_json_path = os.path.join(modsPath, "mods.json")
	else:
		with open("settings.json", "w") as f:
			if os.path.exists(os.path.expandvars("%appdata%") + "\\itch\\apps\\super-mario-construct") and onWindows:
				if devMode: print("Super Mario Construct installed via itch.io app")
				json.dump({"GameLocation": f"{os.path.expandvars("%appdata%") + "\\itch\\apps\\super-mario-construct"}", "ModsLocation": "Mods", "Width": 832, "Height": 480, "Modlist": { "Custom Mod Repos": [] }}, f, indent="\t")
			elif os.path.exists(os.path.expanduser("~") + "/.config/itch/apps/super-mario-construct") and not onWindows:
				if devMode: print("Super Mario Construct installed via itch.io app")
				json.dump({"GameLocation": f"{os.path.expanduser("~") + "/.config/itch/apps/super-mario-construct"}", "ModsLocation": "Mods", "Width": 832, "Height": 480, "Modlist": { "Custom Mod Repos": [] }}, f, indent="\t")
			else:
				if os.path.exists("Super Mario Construct.exe"):
					if devMode: print("Super Mario Construct installed in current directory")
					json.dump({"GameLocation": f"{os.getcwd()}", "ModsLocation": "Mods", "Width": 832, "Height": 480, "Modlist": { "Custom Mod Repos": [] }}, f, indent="\t")
				else:
					json.dump({"GameLocation": "", "ModsLocation": "Mods", "Width": 832, "Height": 480, "Modlist": { "Custom Mod Repos": [] }}, f, indent="\t")
		with open("settings.json") as f:
			settings = json.load(f)
		gamePath = settings.get("GameLocation")
		modsPath = settings.get("ModsLocation")
		winWidth = settings.get("Width")
		winHeight = settings.get("Height")
		mods_json_path = os.path.join(modsPath, "mods.json")

def refreshModsConfig():
	"""Refresh mods.json by unpacking zip files and reading their mod.json."""
	global installedMods, modifiedFiles, modsConfig, modVars
	modVars = {modID: tk.BooleanVar(value=modData.get("Enabled", False)) for modID, modData in sortModsByPriority(modsConfig)}
	oldModsConfig = modsConfig.copy()
	
	# save the current mod enabled states to oldModsConfig
	for modID, var in modVars.items():
		oldModsConfig[modID]["Enabled"] = var.get()
		if modID in outdatedMods:
			outdatedMods.remove(modID)
	modsConfig = {} # Clear existing modsConfig

	# Get a list of all mod zip files
	mod_zips = [item for item in os.listdir(modsPath) if item.endswith(".zip") and os.path.isfile(os.path.join(modsPath, item))]
	potential_mod_folders = [item for item in os.listdir(modsPath) if os.path.isdir(os.path.join(modsPath, item))]
	# Sort mods alphabetically
	mod_zips.sort()

	# Assign priorities alphabetically (lower alphabetically, higher priority number)
	for priority, item in enumerate(potential_mod_folders, start=1):
		modFolderName = item
		if os.path.exists(os.path.join(modsPath, modFolderName, "mod.json")):
			if devMode: print(f"Mod found in folder {modFolderName}!")
			modJSONPath = os.path.join(modsPath, modFolderName, "mod.json")
			with open(modJSONPath, "r") as f:
				modData = json.load(f)
			modName = modData.get("Name")
			modID = modData.get("ID") # Get the mod's ID
			if modName and modID:
				modData["Priority"] = oldModsConfig.get(modID, {}).get("Priority", priority - 1)
				modData["Enabled"] = oldModsConfig.get(modID, {}).get("Enabled", False)
				updateModsConfig(modName, modData, f"{modsPath}/{modFolderName}")
				if devMode: print(f"Folder \"{modFolderName}\" parsed\n")

	# Assign priorities alphabetically (lower alphabetically, higher priority number)
	for priority, item in enumerate(mod_zips, start=1):
		modFolderName = item[:-4] # Remove .zip extension
		with ZipFile(os.path.join(modsPath, item), "r") as zip:
			# Extract only mod.json
			zip.extract("mod.json", path=os.path.join(temp_dir, modFolderName))
			modJSONPath = os.path.join(temp_dir, modFolderName, "mod.json")
			if os.path.exists(modJSONPath):
				with open(modJSONPath, "r") as f:
					try:
						modData = json.load(f)
					except json.JSONDecodeError as e:
						if devMode: print(f"Error parsing {modJSONPath} ({modFolderName}):\n{e}")
						messagebox.showerror("Parsing Error", f"Mod {modFolderName}.zip could not be parsed. Perhaps its mod.json is malformed?")
						continue
					except Exception as e:
						if devMode: print(f"Unexpected error: {e}")
						if devMode: messagebox.showerror("Error", f"Unexpected error while reading {modFolderName}'s mods.json:\n{e}")
						else: messagebox.showerror("Error", f"An unexpected error occured while parsing {modFolderName}.zip. It has been skipped.")
						continue
				modName = modData.get("Name")
				modID = modData.get("ID") # Get the mod's ID
				if modName and modID:
					modData["Priority"] = oldModsConfig.get(modID, {}).get("Priority", priority - 1) # Keep old priority if exists
					modData["Enabled"] = oldModsConfig.get(modID, {}).get("Enabled", False) # Keep old enabled status if exists
					updateModsConfig(modName, modData, f"{modFolderName}.zip")
					if devMode: print(f"{modFolderName} extracted and parsed\n")

	# Save the updated modsConfig to mods.json
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent="\t")

	# Update the mod list in the GUI
	sortedMods = sortModsByPriority(modsConfig)
	createModList(sortedMods)
	
	# Clear the temp folder
	# Clear the contents of temp_dir without deleting the directory itself or Unmodified Game Files
	for item in os.listdir(temp_dir):
		item_path = os.path.join(temp_dir, item)
		if os.path.isfile(item_path) or os.path.islink(item_path):
			os.remove(item_path)
		elif os.path.isdir(item_path):
			if not item_path.endswith("Unmodified Game Files"):
				shutil.rmtree(item_path)
	installedMods = {}
	for modID in modsConfig:
		installedMods[modID] = modsConfig[modID]["Version"]
	onlineModList.installedMods = installedMods
	checkForModUpdates()
	if devMode:
		print("Mods configuration refreshed.")
onlineModList.refreshModsConfig = refreshModsConfig
def restoreGameFiles():
	"""Restores original game files"""
	for file in modFiles[:]:
		if os.path.exists(file):
			print(f"Removing {file}")
			if os.path.isdir(file):
				shutil.rmtree(file, ignore_errors=True)
			else:
				os.remove(file)
			# remove file from mod files list
			if os.path.exists(file):
				print(f"Unable to remove {file}")
			else:
				modFiles.remove(file)

	for root, dirs, files in os.walk(os.path.join(temp_dir, "Unmodified Game Files")):
		for file in files:
			relativePath = os.path.relpath(os.path.join(root, file), os.path.join(temp_dir, "Unmodified Game Files"))
			gameFilesPath = os.path.join(gamePath, "www", relativePath)
			unmodifiedFilePath = os.path.join(root, file)
			if os.path.exists(unmodifiedFilePath):
				shutil.copy2(unmodifiedFilePath, gameFilesPath)
				if devMode:	print(f"Restored {gameFilesPath} from {unmodifiedFilePath}\n")
	# Clear modifiedFiles when game is closed. Fixes issue #3
	global modifiedFiles
	modifiedFiles = {}
	if os.path.exists(os.path.join(gamePath, "modifiedFiles.json")):
		os.remove(os.path.join(gamePath, "modifiedFiles.json"))

def runGame():
	gameExecutable = None
	global onWindows, refreshButton
	if onWindows:
		gameExecutable = os.path.join(gamePath, "Super Mario Construct.exe")
	else:
		gameExecutable = os.path.join(gamePath, "Super Mario Construct")
		os.chmod(gameExecutable, 0o755)
	if os.path.exists(gameExecutable):
		process = subprocess.Popen([gameExecutable], cwd=gamePath)
		window.iconify() # Minimize the GUI
		refreshButton.config(state="disabled")
		while process.poll() is None:
			window.update() # Keep the GUI responsive
			window.after(100) # Wait for 100ms before checking again
		if devMode:
			print("Game exited")
			print("------------------------")
		restoreGameFiles()
		bringWindowToFront()
		window.deiconify()
		refreshButton.config(state="normal")

	else:
		print(f"Game executable not found at {gameExecutable}")
		messagebox.showerror("Error", f"Game executable not found at {gamePath}")

def saveAndPlay():
	global modifiedFiles, modVars
	# Save the current mod states to modsConfig
	for modID, var in modVars.items():
		modsConfig[modID]["Enabled"] = var.get()

	# Write the updated modsConfig to mods.json
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent="\t")

	for item in modsConfig:
		if not item:
			print("No items found!")
			messagebox.showerror("Error", "No mods found!")
		if modsConfig[item]["Enabled"]:
			if "FileName" in modsConfig[item]:
				print(modsConfig[item]["FileName"])
				if modsConfig[item]["FileName"].endswith(".zip") and os.path.isfile(os.path.join(modsPath, modsConfig[item]["FileName"])):
					modFolderName = modsConfig[item]["FileName"][0:len(item)-4] # chop off .zip
					print(modFolderName)
					with ZipFile(os.path.join(modsPath, modsConfig[item]["FileName"]), "r") as zip:
						zip.extractall(os.path.join(temp_dir, modFolderName))
						parseModFolder(os.path.join(temp_dir, modFolderName))
						if devMode:	print(modFolderName + " extracted and parsed\n")
			elif "FolderPath" in modsConfig[item]:
				modFolderPath = modsConfig[item]["FolderPath"]
				if devMode: print(modFolderPath)
				parseModFolder(os.path.join(modFolderPath))
				if devMode:	print(modFolderPath + " extracted and parsed\n")
			else:
				pass
	for mod in allModVersions:
		if allModVersions[mod] != gameVersion and modsConfig[mod]["Enabled"]:
			if allModVersions[mod].endswith("*"):
				modVersion = allModVersions[mod][:-1]
				if gameVersion.startswith(modVersion):
					continue
			msg = tk.messagebox.askyesnocancel(title="Possible Mod Incompatability", message=f"Mod \"{modsConfig[mod]["Name"]}\" may not be compatible with the current Game Version ({gameVersion}), as it was built for {allModVersions[mod]}.\nDo you want to disable it?", icon="warning")
			match msg:
				case False:
					pass
				case True:
					restoreGameFiles()
					modsConfig[mod]["Enabled"] = False
					createModList(sortModsByPriority(modsConfig))
					with open(mods_json_path, "w") as f:
						json.dump(modsConfig, f, indent="\t")
						parseModFolder(os.path.join(temp_dir, modFolderName))
						saveAndPlay()
					return
				case _:
					restoreGameFiles()
					return
	runGame()

def setGameLocation():
	global gameVersion, gameVersionLabel
	"""Saves the game location to settings.json."""
	newGamePath = filedialog.askdirectory(title="Please select game folder")
	if newGamePath and validateGameFolder(newGamePath):
		settings["GameLocation"] = newGamePath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent="\t")
		readSettingsJSON()
		newGamePath = settings.get("GameLocation")
		gameVersion = getInstalledGameVersion()
		gameVersionLabel.config(text=f"Installed Game Version: {gameVersion}")
	elif not newGamePath == "":
		setGameLocation()

def setupOnlineModList():
	"""Sets up the online mod list."""
	jsonURL = "https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/modlist.json"
	if devMode and not getattr(sys, "frozen", False): jsonFilePath = "tests/downloadtest/modlist.json"
	else: jsonFilePath = None

	onlineModList.parentWindow = window
	onlineModList.downloadLocation = modsPath
	for modID in modsConfig:
		installedMods[modID] = modsConfig[modID]["Version"]
	onlineModList.installedMods = installedMods
	onlineModList.devMode = devMode

	global onlineModData
	onlineModData = onlineModList.loadMods(jsonFilePath, jsonURL)

def setModsLocation():
	"""Saves the mods folder location to settings.json."""
	newModsPath = filedialog.askdirectory()
	if newModsPath and validateModsFolder(newModsPath):
		settings["ModsLocation"] = newModsPath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent="\t")
		readSettingsJSON()
		refreshModsConfig()
	elif not newModsPath == "":
		setModsLocation()

def sortModsByPriority(modsConfig):
	"""Sort mods by priority."""
	return sorted(modsConfig.items(), key=lambda item: item[1].get("Priority", 0), reverse=False)

def updateModsConfig(modName, modData, fileName):
	"""Update mods.json with new mod data."""
	modID = modData.get("ID") # Get the mod's ID from modData
	if modID not in modsConfig:
		modsConfig[modID] = {}
	# update mod data
	if not fileName.endswith("zip"):
		modsConfig[modID]["FolderPath"] = fileName
	else:
		modsConfig[modID]["FileName"] = fileName
	modsConfig[modID]["Enabled"] = modData.get("Enabled", modsConfig[modID].get("Enabled", False))
	modsConfig[modID]["Priority"] = modData.get("Priority", modsConfig[modID].get("Priority", 0))
	modsConfig[modID]["Version"] = modData.get("Version", modsConfig[modID].get("Version", "1.0"))
	modsConfig[modID]["GameAbbreviation"] = modData.get("GameAbbreviation", modsConfig[modID].get("GameAbbreviation", "SMC"))
	modsConfig[modID]["GameVersion"] = modData.get("GameVersion", modsConfig[modID].get("GameVersion", ""))
	modsConfig[modID]["Description"] = modData.get("Description", modsConfig[modID].get("Description", ""))
	modsConfig[modID]["Name"] = modName # Store the mod name for display purposes
	modsConfig[modID]["Author"] = modData.get("Author", modsConfig[modID].get("Author", "Author Unknown"))
	with open(mods_json_path, "w") as f:
		print(mods_json_path)
		json.dump(modsConfig, f, indent="\t")
	if devMode: print(f"Updated {modName} (ID: {modID}) in mods.json")

def updateOnlineModData(newData):
	global onlineModData
	onlineModData = newData
onlineModList.updateOnlineModData = updateOnlineModData

def findGameVer(data):
	lastNearestIndex = -1 # Track the last occurrence of "nearest"

	if isinstance(data, list):
		for i in range(len(data) - 2): # Ensure we don't go out of bounds
			if data[i] == "nearest":
				lastNearestIndex = i # Update the last found index

		# If we found "nearest", return the value after the next item
		if lastNearestIndex != -1 and lastNearestIndex + 2 < len(data):
			if isinstance(data[lastNearestIndex + 2], str):
				return data[lastNearestIndex + 2]

		# Recursively search nested lists
		for item in data:
			if isinstance(item, list):
				result = findGameVer(item)
				if result:
					return result

	elif isinstance(data, dict):
		for value in data.values():
			result = findGameVer(value)
			if result:
				return result

	return None

def getInstalledGameVersion():
	dataFile = os.path.join(gamePath, "www/data.json")
	if os.path.exists(dataFile):
		try:
			with open(dataFile, "rb") as f:
				data = orjson.loads(f.read())
			return findGameVer(data) or "Unknown"
		except Exception as e:
			if devMode:	print(f"Error reading data.json: {e}")
			return "Error Retrieving Version"
	else:
		return "Game Version Not Found"

def getLatestVersion():
	keywordsToIgnore = ["alpha", "april-fools", "beta", "dev", "pre-release", "pre_release", "release-candidate", "release_candidate", "test", "apf", "a" "b", "d", "pre", "rc", "t"]
	for keyword in keywordsToIgnore:
		if keyword in managerVersion.lower():
			if devMode: print(f"Keyword: \"{keyword}\" found in version: {managerVersion}, not checking version")
			return
	if latestManagerVersion == "Could not get latest mod manager version":
		return
	latestVersionInt = int(latestManagerVersion.replace(".", ""))
	managerVersionInt = int(managerVersion.replace(".", ""))
	
	def askMsg():
		msg = None
		match updateType:
			case "normal":
				msg = messagebox.askyesno("Update Available", f"An update is available.\nInstalled version: {managerVersion}\nLatest version: {latestManagerVersion}\nDo you want to download it?", icon="info")
			case "bugfix":
				msg = messagebox.askyesno("Update Available", f"A bugfix update is available.\nInstalled version: {managerVersion}\nLatest version: {latestManagerVersion}\nDo you want to download it?", icon="info")
			case "critical": # hope to never have to use this one
				msg = messagebox.askyesno("Update Available", f"A CRITICAL update is available. It fixes severe issues and playing on your version could have major issues.\nInstalled version: {managerVersion}\nLatest version: {latestManagerVersion}\nPlease download the update.", icon="warning")
				if msg:
					webbrowser.open("https://github.com/WINRARisyou/SMC-Desktop-Mod-Manager/releases/latest")
				else:
					if messagebox.askyesno("Confirm", "Are you sure you want to continue?", icon="warning"):
						global criticallyOutdated
						criticallyOutdated = True
					else:
						askMsg()
						return
			case _:
				msg = messagebox.askyesno("Update Available", f"An update is available.\nInstalled version: {managerVersion}\nLatest version: {latestManagerVersion}\nDo you want to download it?", icon="info")
		
		if msg:
			webbrowser.open("https://github.com/WINRARisyou/SMC-Desktop-Mod-Manager/releases/latest")

	if latestVersionInt > managerVersionInt and len(str(latestVersionInt)) == len(str(managerVersionInt)):
		if devMode: print("latestVersionInt and managerVersionInt are same length, so we can evaluate as is.")
		askMsg()
		return
	
	if len(latestManagerVersion.replace(".", "")) > len(managerVersion.replace(".", "")):
		for i in range(abs(len(latestManagerVersion.replace(".", "")) - len(managerVersion.replace(".", "")))):
			managerVersionInt *= 10
		if devMode: print(f"Current version as integer (when normalized to match latest version's length): {managerVersionInt}")

	elif len(managerVersion.replace(".", "")) > len(latestManagerVersion.replace(".", "")):
		for i in range(abs(len(latestManagerVersion.replace(".", "")) - len(managerVersion.replace(".", "")))):
			latestVersionInt *= 10
		if devMode: print(f"Latest version as integer (when normalized to match current version's length): {latestVersionInt}")

	if managerVersionInt < latestVersionInt and latestManagerVersion != "Could not get latest Mod Manager Version":
		askMsg()

def handleFileDrop(event):
	files = window.tk.splitlist(event.data)
	for file in files:
		# handle zip file drop
		if os.path.isfile(file) and file.endswith(".zip"):
			
			if os.path.exists(os.path.join(modsPath, os.path.basename(file))):
				overwrite = messagebox.askyesno("Overwrite Mod", f"The mod you are trying to import already exists. Do you want to overwrite it?")
				if overwrite:
					shutil.copy2(file, modsPath)
					if devMode: print(f"Overwrote {modsPath} with {file}")
					refreshModsConfig()
			else:
				shutil.copy2(file, modsPath)
				if devMode: print(f"Copied {file} to {modsPath}")
				refreshModsConfig()
		# handle folder mod drop
		elif os.path.isdir(file):
			dest = os.path.join(modsPath, os.path.basename(file))
			if os.path.exists(dest):
				overwrite = messagebox.askyesno("Overwrite Mod", f"The mod you are trying to import already exists. Do you want to overwrite it?")
				if overwrite:
					shutil.rmtree(dest)
				else:
					return
			shutil.copytree(file, dest)
			if devMode: print(f"Copied folder {file} to {dest}")
			refreshModsConfig()
		else:
			messagebox.showerror("Invalid File", f"Unsupported file type: {file}")

def windowResized(event):
	settings["Width"] = window.winfo_width()
	settings["Height"] = window.winfo_height()
### /FUNCTIONS ###
### MAIN ###
## GET PATHS ##
readSettingsJSON()

# Read or create mods.json
mods_json_path = os.path.join(modsPath, "mods.json")
if not os.path.exists(modsPath):
	os.mkdir(modsPath)
if not os.path.exists(mods_json_path) or os.path.getsize(mods_json_path) == 0:
	with open(mods_json_path, "w") as f:
		json.dump({}, f, indent="\t")
try:
	with open(mods_json_path) as f:
		modsConfig = json.load(f)
except json.JSONDecodeError as e:
	print(f"Error reading mods.json: {e}")
	modsConfig = {}
	messagebox.showerror("Error", f"Error reading mods.json: {e}\nTry deleting mods.json and see if the error persists.")

# Check if SMC exists in the game path
def validateGameFolder(path):
	"""Check if SMC exists in the specified path."""
	if not os.path.exists(os.path.join(path, "Super Mario Construct.exe")) and onWindows:
		print(f"Super Mario Construct not found at {path}!")
		messagebox.showerror("Error", f"Super Mario Construct not found at {path}!")
		return False
	elif not os.path.exists(os.path.join(path, "Super Mario Construct")) and not onWindows:
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

# Set minimum window size
window.minsize(480, 480)
window.bind("<Configure>", windowResized)

icon_path = resPath.resource_path("icons/icon-512.png")
icon_image = tk.PhotoImage(file=icon_path) # Keep a reference
window.iconphoto(True, icon_image)
window.title("SMC Desktop Mod Manager")
window.geometry(f"{winWidth}x{winHeight}")

# Create menu bar
menuBar = tk.Menu(window)
window.config(menu=menuBar)
filesMenuBar = tk.Menu(menuBar, tearoff=0)
toolsMenuBar = tk.Menu(menuBar, tearoff=0)
helpMenuBar = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="File", menu=filesMenuBar)
menuBar.add_cascade(label="Tools", menu=toolsMenuBar)
menuBar.add_cascade(label="Help", menu=helpMenuBar)

# File Menu
filesMenuBar.add_command(label="Set Game Location", command=setGameLocation)
filesMenuBar.add_command(label="Set Mods Folder Location", command=setModsLocation)
filesMenuBar.add_command(label="Open Game Folder", command=openGameFolder)
filesMenuBar.add_command(label="Open Mods Folder", command=openModFolder)
filesMenuBar.add_command(label="Import Mod", command=copyModFile)
filesMenuBar.add_separator()
filesMenuBar.add_command(label="Exit", command=window.quit)

# Tools Menu
toolsMenuBar.add_command(label="Online Mod list", command=lambda: onlineModList.createWindow(onlineModList.parentWindow, gameVersion, onlineModData))
toolsMenuBar.add_command(label="Check for Mod Updates", command=checkForModUpdates)
toolsMenuBar.add_command(label="Refresh Mods", command=refreshModsConfig)
if devMode:
	toolsMenuBar.add_separator()
	toolsMenuBar.add_command(label="Open Temp Folder", command=lambda: os.startfile(temp_dir))

# Help menu
helpMenuBar.add_command(label="About", command=lambda: aboutWindow.createAboutWindow(window))
helpMenuBar.add_command(label="Report a Bug", command=lambda: webbrowser.open("https://github.com/WINRARisyou/SMC-Desktop-Mod-Manager/issues/new?template=bug-report-template.md"))
helpMenuBar.add_command(label="Create a Mod", command=lambda: webbrowser.open("https://github.com/WINRARisyou/SMC-Desktop-Mod-Manager/tree/main/Example%20Mods#how-to-create-a-mod"))

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
	global modListbox
	modListScrollbar = ttk.Scrollbar(frame, orient="vertical")
	modListbox = tk.Listbox(frame, width=50, height=10, activestyle="dotbox", yscrollcommand=modListScrollbar.set)
	modListbox.pack(side="left", padx=5)

	modListbox.drop_target_register(DND_FILES)
	modListbox.dnd_bind("<<Drop>>", handleFileDrop)

	modListScrollbar.pack(side="left", fill="y")
	modListScrollbar.config(command=modListbox.yview)

	# frame for buttons
	buttonFrame = tk.Frame(frame)
	buttonFrame.pack(side="left", padx=5)

	# buttons for priority adjustments
	upButton = ttk.Button(buttonFrame, text="↑", width=3, command=lambda: moveMod(-1))
	upButton.pack(fill="none", pady=2)

	# refresh button
	global refreshButton
	refreshButton = ttk.Button(buttonFrame, text="🔄", width=3, command=refreshModsConfig)
	refreshButton.pack(fill="none", pady=2)

	downButton = ttk.Button(buttonFrame, text="↓", width=3, command=lambda: moveMod(1))
	downButton.pack(fill="none", pady=2)

	# Place delete mod button in mod info frame
	global SelectedMod
	deleteModButton = ttk.Button(buttonFrame, text="🗑", width=3, command=lambda: deleteMod(SelectedMod))
	deleteModButton.pack(fill="none")
	deleteModButton.config(state="disabled")

	# Frame for mod info label
	modInfoFrame = tk.Frame(frame)
	modInfoFrame.pack(side="right", padx=10, fill="both", expand=True)

	# Add a canvas and scrollbar for the mod info label
	canvas = tk.Canvas(modInfoFrame, width=100, height=200)
	scrollbar = ttk.Scrollbar(modInfoFrame, orient="vertical", command=canvas.yview)
	scrollable_frame = tk.Frame(canvas)

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
	modInfoLabel = tk.Label(scrollable_frame, text="", justify="center", anchor="n")
	modInfoLabel.bind("<Configure>", lambda e: modInfoLabel.config(wraplength=(modInfoLabel.winfo_width() - 10)))
	modInfoLabel.pack(fill="both", expand=True)
	scrollable_frame.pack(fill="both", expand=True)

	# Store checkboxes' states
	global modVars
	modVars = {modID: tk.BooleanVar(value=modData.get("Enabled", False)) for modID, modData in sortedMods}
	def deleteMod(mod):
		global modVars
		if devMode: print(mod)
		if devMode: print(SelectedMod)
		if devMode: print(mod and modsPath in os.path.join(modsPath, mod))
		modID = None
		for id, data in modsConfig.items():
			if data.get("FileName") == mod:
				modID = id
				break
			if data.get("FolderPath") == mod:
				modID = id
				break
		warning = messagebox.askokcancel("Warning", f"Are you sure you want to delete \"{modsConfig[modID].get("Name")}\"?\nIt will be removed from your system, and you will have to redownload it.", icon="warning")
		if warning:
			if mod:
				if os.path.isdir(os.path.join(modsPath, mod)):
					if not mod and modsPath in os.path.join(modsPath, mod) or mod == modsPath:
						messagebox.showerror("Error", "Invalid mod path. Mod not removed.")
					else:
						shutil.rmtree(os.path.join(modsPath, mod))
				else:
					os.remove(os.path.join(modsPath, mod))
				if modID:
					del modsConfig[modID]
				else:
					if devMode:	print("Mod not found in mods.json")
				with open(mods_json_path, "w") as f:
					json.dump(modsConfig, f, indent="\t")
				if deleteModButton.winfo_exists():
					deleteModButton.config(state="disabled")
				refreshModsConfig()
			else:
				messagebox.showerror("Error", "No mod selected.")
		if devMode:	print(f"Deleted {mod}")

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
					json.dump(modsConfig, f, indent="\t")

				# Refresh UI & reselect moved item
				updateModList()
				modListbox.selection_set(newIndex)
	
	def onModSelect(event):
		selected = modListbox.curselection()
		if selected:
			global SelectedMod
			deleteModButton.config(state="normal")
			index = selected[0]
			modID, modData = sortedMods[index]
			if sortedMods[index][1].get("FileName") != None:
				SelectedMod = sortedMods[index][1].get("FileName")
			else:
				SelectedMod = sortedMods[index][1].get("FolderPath")
			description = modData.get("Description", "No description available.")
			if description == "":
				description = "No description available."
			modInfoLabel.config(text=f"{description}")
			canvas.yview_moveto(0)
	
	def toggleModState():
		selected = modListbox.curselection()
		if selected:
			index = selected[0]
			modID, modData = sortedMods[index]
			modVars[modID].set(not modVars[modID].get()) # Toggle state
			updateModList()

	def updateModList():
		global outdatedMods, modListbox
		modListbox.delete(0, tk.END)


		for modID, modData in sortedMods:
			modName = modData.get("Name") # Get the mod name for display
			checked = "✅ " if modVars[modID].get() else "⬜ "
			displayText = f"{checked}{modName} - {modData.get("Version", "")} - {modData.get("Author", "Author Unknown")}"
			if devMode: displayText += f" (Priority: {modData["Priority"]})"
			modListbox.insert(tk.END, displayText)
			# Re-apply color if it was previously set
			if modID in outdatedMods:
				modListbox.itemconfig(tk.END, {"fg": "orange"})
			else:
				modListbox.itemconfig(tk.END, {"fg": "black"})

		# Check if the mods list can be scrolled
		if not modListbox.size() > 10:
			modListScrollbar.pack_forget()
			modListbox.config(width=50)
		else:
			modListScrollbar.pack(after=modListbox)
			modListbox.config(width=47)

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
	PlayBtn = ttk.Button(buttonsFrame, text="Play Without Mods", command=runGame)
	PlayBtn.pack(side="left", padx=5)

	# Initialize the mod list
	updateModList()

	# Check if the mods list can be scrolled
	if not modListbox.size() > 10:
		modListScrollbar.pack_forget()
	else:
		modListbox.config(width=47)
		
# Label to show mod info on click
modInfoLabel = tk.Label(window, text="", justify="left")
modInfoLabel.pack_forget()

# Sort mods by priority and create mod list
sortedMods = sortModsByPriority(modsConfig)
createModList(sortedMods)

gameVersion = getInstalledGameVersion()

latestGameVersion = makeWebRequest("https://levelsharesquare.com/api/accesspoint/gameversion/SMC", 5, "Could not get latest Game Version")
if type(latestGameVersion) != str: latestGameVersion = latestGameVersion.json().get("version") 

latestManagerVersion = makeWebRequest("https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/current_version.json", 10, "Could not get latest Mod Manager Version")
updateType = None
if type(latestManagerVersion) != str: updateType = latestManagerVersion.json().get("updateType")
if type(latestManagerVersion) != str: latestManagerVersion = latestManagerVersion.json().get("version")

global gameVersionLabel
gameFrame = tk.Frame(window)
gameFrame.pack(side="left", padx=5, pady=0)
gameVersionLabel = tk.Label(gameFrame, text=f"Installed Game Version: {gameVersion}")
gameVersionLabel.pack(pady=0, anchor="w")
latestGameVersionLabel = tk.Label(gameFrame, text=f"Latest Game Version: {latestGameVersion}")
latestGameVersionLabel.pack(pady=0, anchor="w")

managerFrame = tk.Frame(window)
managerFrame.pack(side="right", padx=5, pady=0)
managerVersionLabel = tk.Label(managerFrame, text=f"Mod Manager Version: {managerVersion}")
managerVersionLabel.pack(pady=0, anchor="e")
latestManagerVersionLabel = tk.Label(managerFrame, text=f"Latest Mod Manager Version: {latestManagerVersion}")
latestManagerVersionLabel.pack(pady=0, anchor="e")

getLatestVersion()

if criticallyOutdated:
	managerVersionLabel.config(fg="red")
	tooltip.Tooltip(managerVersionLabel, bg=window.cget("bg"), text="You are critically out of date. Please update the mod manager.", borderColor="black", borderWidth=1, wraplength=270)
## /GUI ##
## ONLINE MOD LIST ##
setupOnlineModList()
if onlineModData == "cannotAccessModList" or onlineModData == False:
	toolsMenuBar.entryconfig("Online Mod list", state="disabled")
	toolsMenuBar.entryconfig("Check for Mod Updates", state="disabled")
## /ONLINE MOD LIST ##
### Run it!!1!
crashDetection()
checkForModUpdates()
window.mainloop()
### /MAIN ###
### WINRARisyou was here