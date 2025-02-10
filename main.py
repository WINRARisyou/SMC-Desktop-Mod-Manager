### WINRARisyou was here
### Give credit if you use this code
### DEFS ###
devMode = False
managerVersion = "1.0.0"
import atexit
import ctypes
import json
import os
import platform
import requests
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from zipfile import ZipFile
import webbrowser

global latestGameVersion
#response = requests.get("https://levelsharesquare.com/api/accesspoint/gameversion/SMC")
#latestGameVersion = response.json().get("version")

response = requests.get("https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/current_version.json", timeout=10)

if response.status_code != 200:
	latestManagerVersion = "Could not get latest mod manager version"
else:
	latestManagerVersion = response.json().get("version")

if latestManagerVersion == None:
	latestManagerVersion = "Could not get latest mod manager version"

global onWindows
onWindows = platform.system() == "Windows"
if onWindows:
	ctypes.windll.shcore.SetProcessDpiAwareness(2)

def restoreGameFiles():
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

	"""Restores original game files"""
	for root, dirs, files in os.walk(os.path.join(temp_dir, "Unmodified Game Files")):
		for file in files:
			relativePath = os.path.relpath(os.path.join(root, file), os.path.join(temp_dir, "Unmodified Game Files"))
			gameFilesPath = os.path.join(gamePath, "www", relativePath)
			unmodifiedFilePath = os.path.join(root, file)
			if os.path.exists(unmodifiedFilePath):
				shutil.copy2(unmodifiedFilePath, gameFilesPath)
				if devMode:	print(f"Restored {gameFilesPath} from {unmodifiedFilePath}\n")

def onExit():
	# Remove temporary directory
	shutil.rmtree(temp_dir, ignore_errors=True)
	# Delete files that were marked as missing
	for file in modFiles:
		if os.path.exists(file):
			os.remove(file)

atexit.register(onExit)
temp_dir = tempfile.mkdtemp()
os.mkdir(temp_dir + "/Unmodified Game Files")

### /DEFS ###
### MISC DEFS ###
# Read settings.json
if os.path.exists("settings.json"):
	with open("settings.json") as f:
		settings = json.load(f)
else:
	with open("settings.json", "w") as f:
		if os.path.exists(os.path.expandvars("%appdata%") + "\\itch\\apps\\super-mario-construct") and onWindows:
			if devMode: print("Super Mario Construct installed via itch.io app")
			json.dump({"GameLocation": f"{os.path.expandvars("%appdata%") + "\\itch\\apps\\super-mario-construct"}", "ModsLocation": "Mods"}, f, indent=4)
		else:
			json.dump({"GameLocation": "", "ModsLocation": "Mods"}, f, indent=4)
	with open("settings.json") as f:
		settings = json.load(f)

global allModVersions
allModVersions = {}
global modFiles
modFiles = []
global modifiedFiles
modifiedFiles = {}
global modVars
modVars = {}
global SelectedMod
SelectedMod = None
### /MISC DEFS ###
### MISC FUNCTIONS ###
def backupOriginalFile(gameFilesPath, unmodifiedFilePath):
	if os.path.exists(gameFilesPath):
		print(f"Backing up {gameFilesPath} to {unmodifiedFilePath}")
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
	window.after(100, lambda: window.focus_set())

def copyModFile():
	copyModFiles = filedialog.askopenfiles()
	if copyModFiles:
		for file in copyModFiles:
			if file.name.endswith(".zip"):
				shutil.copy2(file.name, modsPath)
				if devMode:	print(f"Copied {file.name} to {modsPath}")
				refreshModsConfig()
			else:
				print("Invalid file type. Please select a .zip file.")
				messagebox.showerror("Error", "Invalid file type. Please select a .zip file.")

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
			allModVersions[modName] = modData.get("GameVersion")
			updateModsConfig(modName, modData, f"{os.path.basename(modFolder)}.zip")
			if modsConfig.get(modID, {}).get("Enabled", False): # Use modID to check if enabled
				AssetsFolder = modData.get("AssetsFolder")
				if AssetsFolder:
					assetsPath = os.path.join(modFolder, AssetsFolder)
					if os.path.exists(assetsPath):
						processAssetsFolder(modID, assetsPath)
					else:
						print(f"Cannot find assets folder \"{assetsPath}\" for mod \"{modName}\"!")
						messagebox.showerror("Error", f"Cannot find assets folder \"{assetsPath}\" for mod \"{modName}\"!")
				else:
					print("\"AssetsFolder\" not specified in mod.json")
					messagebox.showerror("Error", f"\"AssetsFolder\" not specified in mod.json")
			else:
				print(f"Mod {modName} is not enabled or not specified in mods.json")
		else:
			print(f"\"Name\" or \"ID\" not specified in mod.json")
			messagebox.showerror("Error", f"\"Name\" or \"ID\" not specified in mod.json")
	else:
		print(f"mod.json not found in {modFolder}")
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
	Process a file in the mod's assets folder.
	modID: The ID of the mod.
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

	if not os.path.exists(os.path.dirname(gameFilesPath)): # This means a mod created the directory
		print(f"Marking {os.path.dirname(gameFilesPath)} for deletion")
		modFiles.append(os.path.dirname(gameFilesPath))

	os.makedirs(os.path.dirname(gameFilesPath), exist_ok=True)

	backupOriginalFile(gameFilesPath, unmodifiedFilePath)

	# get the previous mod priority
	previousModPriority = modifiedFiles.get(relativePath, None)
	if previousModPriority is None or modPriority < previousModPriority:
		shutil.copy2(modFilePath, gameFilesPath)
		modifiedFiles[relativePath] = modPriority
		if devMode: print(f"{modID} (Priority: {modPriority}) replaced {gameFilesPath}")
	else:
		if devMode:	print(f"Skipping {modFilePath} because a higher-priority mod ({previousModPriority}) already modified it.")

def refreshModsConfig():
	"""Refresh mods.json by unpacking zip files and reading their mod.json."""
	global modsConfig
	modsConfig = {} # Clear existing modsConfig

	# Get a list of all mod zip files
	mod_zips = [item for item in os.listdir(modsPath) if item.endswith(".zip") and os.path.isfile(os.path.join(modsPath, item))]

	# Sort mods alphabetically
	mod_zips.sort()

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
			shutil.rmtree(item_path)
	os.mkdir(temp_dir + "/" + "Unmodified Game Files")

	if devMode:
		print("Mods configuration refreshed.")

def runGame(reset=False):
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

	for item in os.listdir(modsPath):
		if not item:
			print("No items found!")
			messagebox.showerror("Error", "No items found!")
		if item.endswith(".zip") and os.path.isfile(modsPath + "/" + item):
			modFolderName = item[0:len(item)-4] # chop off .zip
			with ZipFile(modsPath + "/" + item, "r") as zip:
				zip.extractall(temp_dir + "/" + modFolderName)
				parseModFolder(temp_dir + "/" + modFolderName)
				if devMode:	print(modFolderName + " extracted and parsed\n")
		else:
			pass
	#print(allModVersions)
	#for mod in allModVersions:
	#	if allModVersions[mod] != latestGameVersion and modsConfig[mod]["Enabled"]:
	#		msg = tk.messagebox.askyesnocancel(title="Possible Mod Incompatability", message=f"Mod \"{mod}\" may not be compatible with the current game version ({latestGameVersion}), as it was built for {allModVersions[mod]}.\nDo you want to disable it?", icon="warning")
	#		match msg:
	#			case False:
	#				break
	#			case True:
	#				print('disable')
	#				restoreGameFiles()
	#				modsConfig[mod]["Enabled"] = False
	#				createModList(sortModsByPriority(modsConfig))
	#				with open(mods_json_path, "w") as f:
	#					json.dump(modsConfig, f, indent=4)
	#					parseModFolder(temp_dir + "/" + modFolderName)
	#					saveAndPlay()
	#				return
	#			case _:
	#				restoreGameFiles()
	#				return
	runGame()

def setGameLocation():
	"""Saves the game location to settings.json."""
	gamePath = filedialog.askdirectory()
	if gamePath and validateGameFolder(gamePath):
		settings["GameLocation"] = gamePath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent=4)
		messagebox.showinfo("Restarting", "SMC Desktop Mod Manager will now restart to apply the changes.")
		# restart program
		os.execl(sys.executable, sys.executable, *sys.argv)
	elif not gamePath == "":
		setGameLocation()

def sortModsByPriority(modsConfig):
	"""Sort mods by priority."""
	return sorted(modsConfig.items(), key=lambda item: item[1].get("Priority", 0), reverse=False)

def setModsLocation():
	"""Saves the mods folder location to settings.json."""
	modsPath = filedialog.askdirectory()
	if modsPath and validateModsFolder(modsPath):
		settings["ModsLocation"] = modsPath
		with open("settings.json", "w") as f:
			json.dump(settings, f, indent=4)
	else:
		setModsLocation()

def startGame():
	runGame(True)

def updateModsConfig(modName, modData, fileName):
	"""Update mods.json with new mod data."""
	modID = modData.get("ID") # Get the mod's ID from modData
	if modID not in modsConfig:
		modsConfig[modID] = {}
	# update mod data
	modsConfig[modID]["FileName"] = fileName
	modsConfig[modID]["Enabled"] = modData.get("Enabled", modsConfig[modID].get("Enabled", False))
	modsConfig[modID]["Priority"] = modData.get("Priority", modsConfig[modID].get("Priority", 0))
	modsConfig[modID]["Version"] = modData.get("Version", modsConfig[modID].get("Version", "1.0"))
	modsConfig[modID]["GameAbbreviation"] = modData.get("GameAbbreviation", modsConfig[modID].get("GameAbbreviation", "SMC"))
	modsConfig[modID]["GameVersion"] = modData.get("GameVersion", modsConfig[modID].get("GameVersion", ""))
	modsConfig[modID]["Description"] = modData.get("Description", modsConfig[modID].get("Description", ""))
	modsConfig[modID]["Name"] = modName # Store the mod name for display purposes
	with open(mods_json_path, "w") as f:
		json.dump(modsConfig, f, indent=4)
	if devMode: print(f"Updated {modName} (ID: {modID}) in mods.json")
### /MISC FUNCTIONS ###
### MAIN ###
## GET PATHS ##
gamePath = settings.get("GameLocation")
modsPath = settings.get("ModsLocation")

# Read or create mods.json

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

# Create a File menu
filesMenuBar = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="File", menu=filesMenuBar)

# Add commands to the File menu
filesMenuBar.add_command(label="Set Game Location", command=setGameLocation)
filesMenuBar.add_command(label="Set Mods Folder Location", command=setModsLocation)
if devMode: filesMenuBar.add_command(label="Open Temp Folder", command=lambda: os.startfile(temp_dir))
filesMenuBar.add_separator()
filesMenuBar.add_command(label="Refresh Mods", command=refreshModsConfig)
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
		modID = None
		for id, data in modsConfig.items():
			if data.get("FileName") == mod:
				modID = id
				break
		warning = messagebox.askokcancel("Warning", f"Are you sure you want to delete \"{modsConfig[modID].get('Name')}\"?\nIt will be removed from your system, and you will have to redownload it.", icon="warning")
		if warning:
			if mod:
				os.remove(os.path.join(modsPath, mod))
				if modID:
					del modsConfig[modID]
				else:
					if devMode:	print("Mod not found in mods.json")
				with open(mods_json_path, "w") as f:
					json.dump(modsConfig, f, indent=4)
				refreshModsConfig()
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
			SelectedMod = sortedMods[index][1].get("FileName")
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
				modListbox.insert(tk.END, f"{checked}{modName} - {modData.get('Version', '')})")

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

### TODO
### Find way to get installed game version from www/data.json
#gameVersionLabel = tk.Label(window, text="")
#gameVersionLabel.pack(pady=10)
#gameVersionLabel.config(text=f"Latest Game Version: {latestGameVersion}")
managerVersionLabel = tk.Label(window, text="")
managerVersionLabel.pack()
managerVersionLabel.config(text=f"Mod Manager Version: {managerVersion}")

latestManagerVersionLabel = tk.Label(window, text="")
latestManagerVersionLabel.pack(pady=0)
latestManagerVersionLabel.config(text=f"Latest Mod Manager Version: {latestManagerVersion}")

if managerVersion != latestManagerVersion and latestManagerVersion != "Could not get latest mod manager version":
	def download_update():
		webbrowser.open("https://github.com/WINRARisyou/SMC-Desktop-Mod-Manager/releases/latest")
	msg = messagebox.askyesno("Update Available", f"An update is available for the mod manager.\nCurrent version: {managerVersion}\nLatest version: {latestManagerVersion}\nDo you want to download it?", icon="info")
	if msg:
		download_update()

# Run it!!1!
window.mainloop()
## /GUI ##
### /MAIN ###
### WINRARisyou was here