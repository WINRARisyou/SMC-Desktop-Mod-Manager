### WINRARisyou was here
### Give credit if you use this code
### DEFS ###
devMode = True
global managerVersion
managerVersion = "1.0.3a"
import atexit
import ctypes
import json
import orjson
import os
from PIL import Image, ImageTk
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

atexit.register(onExit)
temp_dir = tempfile.mkdtemp()
os.mkdir(os.path.join(temp_dir, "Unmodified Game Files"))
### /DEFS ###
### GLOBALS ###
# Read settings.json
global allModVersions
allModVersions = {}
global gamePath
gamePath = None
global gameVersion
gameVersion = None
global latestGameVersion, latestManagerVersion
latestGameVersion = latestManagerVersion = None
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
global SelectedMod
SelectedMod = None
global settings
settings = None
### /GLOBALS ###
### MISC FUNCTIONS ###
def backupOriginalFile(gameFilesPath, unmodifiedFilePath):
	if os.path.exists(gameFilesPath):
		if devMode: print(f"Backing up {gameFilesPath} to {unmodifiedFilePath}")
		os.makedirs(os.path.dirname(unmodifiedFilePath), exist_ok=True)
		if not os.path.exists(unmodifiedFilePath):
			shutil.copy(gameFilesPath, unmodifiedFilePath)
	else:
		# If the game file or directory doesn't exist, mark it for deletion when the game is closed
		print(f"Marking {gameFilesPath} for deletion")
		if not os.path.isdir(gameFilesPath):
			modFiles.append(gameFilesPath)

def bringWindowToFront():
	window.attributes('-topmost', True)
	window.after(10, lambda: window.focus_set())
	window.after(11, lambda: window.attributes('-topmost', False))

def copyModFile():
	copyModFiles = filedialog.askopenfiles(title="Please select mod files")
	if copyModFiles:
		for file in copyModFiles:
			if file.name.endswith(".zip"):
				shutil.copy2(file.name, modsPath)
				if devMode:	print(f"Copied {file.name} to {modsPath}")
				refreshModsConfig()
			else:
				print("Invalid file type. Please select a .zip file.")
				messagebox.showerror("Error", "Invalid file type. Please select a .zip file.")

def createAboutWindow():
	about = tk.Toplevel(window)  # Create a sub-window
	about.iconphoto(True, tk.PhotoImage(file=resource_path("icons/icon-512.png")))
	about.title("About")
	about.geometry("640x700")
	about.resizable(False, False)
	banner_image = Image.open(resource_path("images/banner2.png"))  # Open the image file
	scaling_factor = getScalingFactor()
	new_width = int(640 * scaling_factor)  # Adjust width for DPI scaling
	original_width, original_height = banner_image.size
	new_height = int((new_width / original_width) * original_height)  # Maintain aspect ratio
	banner_image = banner_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
	banner_photo = ImageTk.PhotoImage(banner_image)  # Convert to a format tkinter can use

	# Display the image in a Label
	banner_label = tk.Label(about, image=banner_photo)
	banner_label.image = banner_photo  # Keep a reference to avoid garbage collection
	banner_label.pack(pady=0)
	info = tk.Label(about, wraplength=int(480 * scaling_factor), text="SMC Desktop Mod Manager is a user-friendly tool designed to simplify modding for Super Mario Construct. You can easily manage, install, and organize your mods with just a few clicks, the Mod Manager takes the hassle out of file management, letting you focus on customizing your gameplay.")
	info.pack(pady=10)


	creditsFrame = tk.Frame(about)
	creditsFrame.pack(pady=0)
	creditsFrame.config(background="#1e1e1e")
	creditsLabel = tk.Label(creditsFrame, text="Credits:\nTODO")
	creditsLabel.pack(pady=0)

def downloadFile(url, filename):
	"""Download a file from a URL and save it to the specified directory."""
	response = requests.get(url, stream=True)
	if devMode: print(url)
	if response.status_code == 200:
		file_path = os.path.join(onlineDownloadDir, filename)
		with open(file_path, 'wb') as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)
		if devMode: print(f"Downloaded: {filename}")
	else:
		if devMode: print(f"Failed to download: {filename} (Status Code: {response.status_code})")

def loadMods():
	"""Fetch the JSON file, parse it, and download the mods."""
	try:
		# response = requests.get(json_url)
		# response.raise_for_status()  # Raise an error for bad status codes
		# data = response.json()
		with open(json_file_path, 'r') as file:
			data = json.load(file)

		# Get the base assets URL
		assets_url = data.get("assetsURL", "")
		if not assets_url:
			print("Error: 'assetsURL' not found in JSON.")
			return

		# Iterate through the mods and download them
		for mod_id, modData in data.items():
			if mod_id == "assetsURL":
				continue  # Skip the assetsURL entry

			file_name = modData.get("FileName", "")
			mod_version = modData.get("Version", "1.0")
			mod_game_version = modData.get("GameVersion", "")
			mod_description = modData.get("Description", "")
			if not file_name:
				print(f"Skipping mod {mod_id}: No \"FileName\" specified.")
				continue

			if assets_url.endswith("/"):
				file_url = f"{assets_url}{file_name}"
			else:
				file_url = f"{assets_url}/{file_name}"
			
			print("------------------------")
			print(f"File URL: {file_url}")
			print(f"File Name: {file_name}")
			print(f"Mod Version: {mod_id}")
			print(f"Mod Version: {mod_version}")
			print(f"Mod Game Version: {mod_game_version}")
			print(f"Mod Description: {mod_description}")
			print("------------------------")
			#downloadFile(file_url, file_name)

	except requests.exceptions.RequestException as e:
		print(f"Error fetching JSON: {e}")
	except json.JSONDecodeError as e:
		print(f"Error parsing JSON: {e}")

def makeWebRequest(url: str, timeout: int, exceptionText: str):
	"""
	Makes a web request to the desired URL.\n
	:param url: URL of the web request
	:param timeout: Time in seconds before the request should time out
	:param exceptionText: Text to return of the request fails
	"""
	try:
		response = requests.get(url, timeout=timeout)
		if response == None:
			return exceptionText
		return response
	except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError,):
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

def readSettingsJSON():
	global gamePath, settings, mods_json_path, modsPath
	if os.path.exists("settings.json"):
		with open("settings.json") as f:
			settings = json.load(f)
		gamePath = settings.get("GameLocation")
		modsPath = settings.get("ModsLocation")
		mods_json_path = os.path.join(modsPath, "mods.json")
	else:
		with open("settings.json", "w") as f:
			if os.path.exists(os.path.expandvars("%appdata%") + "\\itch\\apps\\super-mario-construct") and onWindows:
				if devMode: print("Super Mario Construct installed via itch.io app")
				json.dump({"GameLocation": f"{os.path.expandvars("%appdata%") + "\\itch\\apps\\super-mario-construct"}", "ModsLocation": "Mods"}, f, indent=4)
			else:
				json.dump({"GameLocation": "", "ModsLocation": "Mods"}, f, indent=4)
		with open("settings.json") as f:
			settings = json.load(f)
		gamePath = settings.get("GameLocation")
		modsPath = settings.get("ModsLocation")
		mods_json_path = os.path.join(modsPath, "mods.json")

def refreshModsConfig():
	"""Refresh mods.json by unpacking zip files and reading their mod.json."""
	global modsConfig
	modsConfig = {} # Clear existing modsConfig

	# Get a list of all mod zip files
	mod_zips = [item for item in os.listdir(modsPath) if item.endswith(".zip") and os.path.isfile(os.path.join(modsPath, item))]
	potential_mod_folders = [item for item in os.listdir(modsPath) if os.path.isdir(os.path.join(modsPath, item))]
	# Sort mods alphabetically
	mod_zips.sort()
	
	# Assign priorities alphabetically (lower alphabetically, higher priority number)
	for priority, item in enumerate(potential_mod_folders, start=1):
		modFolderName = item

		if not os.path.exists(os.path.join(modsPath, modFolderName, "mod.json")):
			if devMode: print("Not a folder mod")
		else:
			if devMode: print("Mod found in folder!")
			modJSONPath = os.path.join(modsPath, modFolderName, "mod.json")
			with open(modJSONPath, "r") as f:
				modData = json.load(f)
			modName = modData.get("Name")
			modID = modData.get("ID") # Get the mod's ID
			if modName and modID:
				modData["Priority"] = priority - 1 # Assign priority
				updateModsConfig(modName, modData, f"{modsPath}/{modFolderName}")
				if devMode:	print(f"Folder \"{modFolderName}\" parsed\n")

	# Assign priorities alphabetically (lower alphabetically, higher priority number)
	for priority, item in enumerate(mod_zips, start=1):
		modFolderName = item[:-4] # Remove .zip extension
		with ZipFile(os.path.join(modsPath, item), "r") as zip:
			# Extract only mod.json
			zip.extract("mod.json", path=os.path.join(temp_dir, modFolderName))
			modJSONPath = os.path.join(temp_dir, modFolderName, "mod.json")
			if os.path.exists(modJSONPath):
				with open(modJSONPath, "r") as f:
					modData = json.load(f)
				modName = modData.get("Name")
				modID = modData.get("ID") # Get the mod's ID
				if modName and modID:
					modData["Priority"] = priority - 1 # Assign priority
					updateModsConfig(modName, modData, f"{modFolderName}.zip")
					if devMode:	print(f"{modFolderName} extracted and parsed\n")

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
			if not item_path.endswith("Unmodified Game Files"):
				shutil.rmtree(item_path)

	if devMode:
		print("Mods configuration refreshed.")

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

def runGame():
	gameExecutable = None
	global onWindows
	global refreshButton
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
		json.dump(modsConfig, f, indent=4)

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
					break
			msg = tk.messagebox.askyesnocancel(title="Possible Mod Incompatability", message=f"Mod \"{modsConfig[mod]["Name"]}\" may not be compatible with the current game version ({gameVersion}), as it was built for {allModVersions[mod]}.\nDo you want to disable it?", icon="warning")
			match msg:
				case False:
					pass
				case True:
					restoreGameFiles()
					modsConfig[mod]["Enabled"] = False
					createModList(sortModsByPriority(modsConfig))
					with open(mods_json_path, "w") as f:
						json.dump(modsConfig, f, indent=4)
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
			json.dump(settings, f, indent=4)
		readSettingsJSON()
		newGamePath = settings.get("GameLocation")
		gameVersion = getInstalledGameVersion()
		gameVersionLabel.config(text=f"Installed Game Version: {gameVersion}")
	elif not newGamePath == "":
		setGameLocation()

def sortModsByPriority(modsConfig):
	"""Sort mods by priority."""
	return sorted(modsConfig.items(), key=lambda item: item[1].get("Priority", 0), reverse=False)

def setModsLocation():
	"""Saves the mods folder location to settings.json."""
	newModsPath = filedialog.askdirectory()
	if newModsPath and validateModsFolder(newModsPath):
		settings["ModsLocation"] = newModsPath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent=4)
		readSettingsJSON()
		refreshModsConfig()
	elif not newModsPath == "":
		setModsLocation()

def startGame():
	runGame()

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
	with open(mods_json_path, "w") as f:
		print(mods_json_path)
		json.dump(modsConfig, f, indent=4)
	if devMode: print(f"Updated {modName} (ID: {modID}) in mods.json")

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
			if devMode:	print(f"Error reading game version: {e}")
			return "Error Reading Version"
	else:
		return "Game Version Not Found"

def getLatestVersion():
	keywordsToIgnore = ["beta", "dev", "pre-release", "pre_release", "alpha", "test", "b", "d", "pre", "a", "t"]
	for keyword in keywordsToIgnore:
		if keyword in managerVersion.lower():
			if devMode: print(f"Keyword: \"{keyword}\" found in version: {managerVersion}, not checking version")
			return
	if latestManagerVersion == "Could not get latest mod manager version":
		return
	latestVersionInt = int(latestManagerVersion.replace(".", ""))
	managerVersionInt = int(managerVersion.replace(".", ""))
	
	def askMsg():
		msg = messagebox.askyesno("Update Available", f"An update is available for the mod manager.\nCurrent version: {managerVersion}\nLatest version: {latestManagerVersion}\nDo you want to download it?", icon="info")
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

	if managerVersionInt < latestVersionInt and latestManagerVersion != "Could not get latest mod manager version":
		askMsg()

def getScalingFactor():
	"""Get the system's DPI scaling factor."""
	root = tk.Tk()
	root.tk.call('tk', 'scaling')  # Get the default scaling factor
	scaling_factor = root.tk.call('tk', 'scaling') / 1.5
	root.destroy()
	return scaling_factor

def handleDrop(event):
	files = window.tk.splitlist(event.data)
	for file in files:
		if os.path.isfile(file) and file.endswith('.zip'):
			# handle zip file drop
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
		elif os.path.isdir(file):
			# handle folder mod drop
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
### /MISC FUNCTIONS ###
### MAIN ###
## GET PATHS ##
readSettingsJSON()

# Read or create mods.json
mods_json_path = os.path.join(modsPath, "mods.json")
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
# Create the main window
window = TkinterDnD.Tk()
def resource_path(relative_path):
	""" Get absolute path to resource, works for development and PyInstaller """
	try:
		base_path = sys._MEIPASS # Temp directory for PyInstaller --onefile
	except AttributeError:
		base_path = os.path.abspath(".") # Normal execution
	return os.path.join(base_path, relative_path)

window.iconphoto(True, tk.PhotoImage(file=resource_path("icons/icon-512.png")))
window.title("SMC Desktop Mod Loader")
window.geometry("832x480")

# Create a menu bar
menuBar = tk.Menu(window)
window.config(menu=menuBar)

# Create menubar
filesMenuBar = tk.Menu(menuBar, tearoff=0)
aboutMenu = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="File", menu=filesMenuBar)
menuBar.add_command(label="About", command=createAboutWindow)

# Add commands to the File menu
filesMenuBar.add_command(label="Set Game Location", command=setGameLocation)
filesMenuBar.add_command(label="Set Mods Folder Location", command=setModsLocation)
if devMode: filesMenuBar.add_separator()
if devMode: filesMenuBar.add_command(label="Open Temp Folder", command=lambda: os.startfile(temp_dir))
filesMenuBar.add_separator()
filesMenuBar.add_command(label="Refresh Mods", command=refreshModsConfig)
filesMenuBar.add_command(label="Open Game folder", command=openGameFolder)
filesMenuBar.add_command(label="Open Mods folder", command=openModFolder)
filesMenuBar.add_command(label="Import mod", command=copyModFile)
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

	modListbox.drop_target_register(DND_FILES)
	modListbox.dnd_bind('<<Drop>>', handleDrop)

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
	modInfoLabel = tk.Label(scrollable_frame, text="", justify="center", wraplength=200)
	modInfoLabel.pack(fill="both", expand=True)

	# Store checkboxes' states
	global modVars
	modVars = {modID: tk.BooleanVar(value=modData.get("Enabled", False)) for modID, modData in sortedMods}
	def deleteMod(mod):
		print(mod)
		print(SelectedMod)
		print(mod and modsPath in os.path.join(modsPath, mod))
		modID = None
		for id, data in modsConfig.items():
			if data.get("FileName") == mod:
				modID = id
				break
			if data.get("FolderPath") == mod:
				modID = id
				break
		warning = messagebox.askokcancel("Warning", f"Are you sure you want to delete \"{modsConfig[modID].get('Name')}\"?\nIt will be removed from your system, and you will have to redownload it.", icon="warning")
		if warning:
			if mod:
				if os.path.isdir(os.path.join(modsPath, mod)):
					if not mod and modsPath in os.path.join(modsPath, mod):
						messagebox.showerror("Error", "Invalid mod path. Mod not removed.")
					else:
						pass
						#shutil.rmtree(os.path.join(modsPath, mod))
				else:
					os.remove(os.path.join(modsPath, mod))
				if modID:
					del modsConfig[modID]
				else:
					if devMode:	print("Mod not found in mods.json")
				with open(mods_json_path, "w") as f:
					json.dump(modsConfig, f, indent=4)
				refreshModsConfig()
				if deleteModButton.winfo_exists():
					deleteModButton.config(state="disabled")
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
					json.dump(modsConfig, f, indent=4)

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
		modListbox.delete(0, tk.END)
		for modID, modData in sortedMods:
			modName = modData.get("Name") # Get the mod name for display
			checked = "✅ " if modVars[modID].get() else "⬜ "
			if devMode:
				modListbox.insert(tk.END, f"{checked}{modName} - {modData.get('Version', '')} (Priority: {modData['Priority']})")
			else:
				modListbox.insert(tk.END, f"{checked}{modName} - {modData.get('Version', '')}")

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
# Label to show mod info on click
modInfoLabel = tk.Label(window, text="", justify="left")
modInfoLabel.pack_forget()

# Sort mods by priority and create mod list
sortedMods = sortModsByPriority(modsConfig)
createModList(sortedMods)

gameVersion = getInstalledGameVersion()

latestGameVersion = makeWebRequest("https://levelsharesquare.com/api/accesspoint/gameversion/SMC", 5, "Could not get latest game version")
if type(latestGameVersion) != str: latestGameVersion = latestGameVersion.json().get("version")

latestManagerVersion = makeWebRequest("https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/current_version.json", 10, "Could not get latest mod manager version")
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



json_url = "https://raw.githubusercontent.com/WINRARisyou/SMC-Desktop-Mod-Manager/refs/heads/gh-pages/files/modlist.json"
json_file_path = "tests/downloadtest/modlist.json"

# Directory to save downloaded mods
onlineDownloadDir = modsPath
loadMods()

# Run it!!1!
window.mainloop()
## /GUI ##
### /MAIN ###
### WINRARisyou was here