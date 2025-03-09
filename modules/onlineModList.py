### DEFS ###
import json
import os
from PIL import Image, ImageTk
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from . import createSubWindow as subWindow
global assetsURL
assetsURL = None
global gameVersion
gameVersion = None
global onlineMods
onlineMods = None

devMode = False
downloadLocation = None
installedMods = None
parentWindow = None
settings = {}
onWindows = None
refreshModsConfig = None
selectedMod = None
showOutput = False
### /DEFS ###
### FUNCTIONS
def createWindow(baseWindow, gameVer, modlistData, customModRepo=False):
	global onlineMods
	onlineMods = subWindow.createSubWindow(baseWindow, "Online mod list", "icons/icon-512.png", [890, 534]) # Create a sub-window
	menuBar = tk.Menu(onlineMods)
	onlineMods.config(menu=menuBar)

	if customModRepo:
		menuBar.add_command(label="Info", command=lambda: showModRepoDetails())

	optionsMenuBar = tk.Menu(menuBar, tearoff=0)
	menuBar.add_cascade(label="Options", menu=optionsMenuBar)

	addModRepo = tk.Menu(optionsMenuBar, tearoff=0)
	optionsMenuBar.add_cascade(label="Customs", menu=addModRepo)

	addModRepo.add_command(label="View custom mod repos", command=lambda: viewCustomModRepos())
	addModRepo.add_command(label="Select custom mod repo", command=lambda: selectCustomModRepo())

	global gameVersion
	gameVersion = gameVer

	# Left Panel: Mod List
	modlistFrame = tk.Frame(onlineMods)
	modlistFrame.pack(side="left", fill="y", padx=10, pady=10)

	modlistScrollbar = ttk.Scrollbar(modlistFrame, orient="vertical")
	modlistScrollbar.pack(side="right", fill="y")

	# TODO: Mod Screenshots
	# Center: Screenshots
	# screenshotsFrame = tk.Frame(onlineMods, borderwidth=5, relief="solid")
	# screenshotsFrame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
	# screenshotsLabel = tk.Label(screenshotsFrame, text="Screenshots", font=("Arial", 16))
	# screenshotsLabel.pack(pady=10)

	# Bottom: Mod Details and Download
	detailsFrame = tk.Frame(onlineMods)
	detailsFrame.pack(side="bottom", fill="x", padx=10, pady=10)

	# Mod Icon and Info
	modInfoFrame = tk.Frame(detailsFrame)
	modInfoFrame.pack(side="top", fill="x", expand=True)

	modIconLabel = tk.Label(modInfoFrame, text="No Mod Selected", anchor="e")
	modIconLabel.pack(side="left", padx=5)

	modDetailsFrame = tk.Frame(modInfoFrame)
	modDetailsFrame.pack(side="left", fill="x", expand=True)

	modNameLabel = tk.Label(modDetailsFrame, text="No Mod Selected", font=("Arial", 12, "bold"))
	modNameLabel.pack(anchor="w")
	
	modAuthorLabel = tk.Label(modDetailsFrame, text="No Mod Selected", font=("Arial", 10, "bold"))
	modAuthorLabel.pack(anchor="w")

	modDescriptionLabel = tk.Label(modDetailsFrame, text="No Mod Selected", wraplength=400, justify="left")
	modDescriptionLabel.pack(anchor="w")

	# Version Info
	versionFrame = tk.Frame(detailsFrame)
	versionFrame.pack(side="top", fill="x", padx=10, pady=5)

	installedVersionLabel = tk.Label(versionFrame, text="No Mod Selected")
	installedVersionLabel.pack(anchor="w")

	latestVersionLabel = tk.Label(versionFrame, text="No Mod Selected")
	latestVersionLabel.pack(anchor="w")

	installedGameVersionLabel = tk.Label(versionFrame, text="No Mod Selected")
	installedGameVersionLabel.pack(anchor="w")

	modGameVersionLabel = tk.Label(versionFrame, text="No Mod Selected")
	modGameVersionLabel.pack(anchor="w")

	# Download Button
	downloadFrame = tk.Frame(onlineMods)
	downloadFrame.pack(after=modGameVersionLabel, side="right", padx=0, pady=0)
	downloadButton = ttk.Button(downloadFrame, text="Download", command=lambda: downloadMod(selectedMod, gameVer))
	downloadButton.config(state="disabled")
	downloadButton.pack(padx=0, pady=0, anchor="e")

	# Populate Mod List
	modlistbox = tk.Listbox(modlistFrame, width=25, yscrollcommand=modlistScrollbar.set)
	modlistbox.pack(side="left", fill="both", expand=True)
	modlistScrollbar.config(command=modlistbox.yview)

	for mod in modlistData:
		modlistbox.insert(tk.END, mod["Mod Name"])

	modlistbox.bind(
		"<<ListboxSelect>>", 
		lambda e: 
			onModSelect(modlistbox, modlistData, modNameLabel, modAuthorLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVer),
			downloadButton.config(state="normal")
	)

def downloadFile(url, filename, downloadLocation):
	"""Download a file from a URL and save it to the specified directory."""
	response = requests.get(url, stream=True)
	response.raise_for_status()
	if devMode: print(f"Downloading mod from {url}")
	if response.status_code == 200:
		filePath = os.path.join(downloadLocation, filename)
		with open(filePath, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192): # if y'all are crazy and have absurdly large mods (which is what this is for) we're gonna need to have a talk
				file.write(chunk)
		if devMode: print(f"Downloaded: {filename} from {url}")
	else:
		if devMode: print(f"Failed to download: {filename} from {url} (Status Code: {response.status_code})")
		raise Exception(f"Failed to download: {filename} from {url} (Status Code: {response.status_code})")

def downloadImage(url):
	try:
		response = requests.get(url, stream=True)
		if response.status_code == 200:
			image = Image.open(response.raw)
			image = image.resize((96, 96), Image.Resampling.LANCZOS)
			return ImageTk.PhotoImage(image)
		else:
			print(f"Failed to get image: {url} (Status Code: {response.status_code})")
			return None
	except Exception as e:
		print(f"Error downloading image: {e}")
		return None

def downloadMod(mod, gameVersion):
	if mod["Mod Game Version"] != gameVersion:
			if mod["Mod Game Version"].endswith("*"):
				modVer = mod["Mod Game Version"][:-1]
				if not gameVersion.startswith(modVer):
					warning = messagebox.askyesno("Warning", "The mod game version does not match the installed game version. Do you want to continue?")
					if not warning:
						return
			else:
				warning = messagebox.askyesno("Warning", "The mod game version does not match the installed game version. Do you want to continue?")
				if not warning:
					return
	try:
		downloadFile(mod["File URL"], mod["File Name"], downloadLocation)
	except Exception as err:
		messagebox.showerror("Download Failure", "An error occured and the mod couldn't be downloaded. Sorry!")
		return
	messagebox.showinfo("Success", f"Mod {mod["Mod Name"]} downloaded successfully!")
	refreshModsConfig()

def getInstalledModVersion(modID):
	if modID in installedMods:
		return installedMods[modID]
	else:
		return "Mod Not Installed"

def loadModIcon(mod, modIconLabel):
	def fetchIcon():
		iconURL = f"{mod['Mod Manager Images Folder URL']}/icon.png"
		iconImage = downloadImage(iconURL)
		if iconImage is not None:
			try:
				# make a blank 128x128 image
				baseImage = Image.new("RGBA", (128, 128))

				# get the PIL Image from the PhotoImage
				tkinterImage = ImageTk.getimage(iconImage)

				# paste the actual icon onto the center of the blank image
				baseImage.paste(tkinterImage, ((128 - tkinterImage.width) // 2, (128 - tkinterImage.height) // 2))

				# convert the padded image back into a tkinter PhotoImage
				baseImage = ImageTk.PhotoImage(baseImage)

				# update the label
				modIconLabel.config(image=baseImage)
				modIconLabel.image = baseImage
			except Exception as e:
				if devMode: print(f"Error processing image: {e}")
				modIconLabel.config(image="", text="No Icon Found")
				modIconLabel.image = None
		else:
			modIconLabel.config(image="", text="No Icon Found")
			modIconLabel.image = None
	thread = threading.Thread(target=fetchIcon)
	thread.start()

def loadMods(jsonFilePath=None, jsonURL="https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/modlist.json"):
	"""
	Fetches the mod list from a JSON file and parses it.
	
	:param jsonFilePath str: The path to a local JSON file to use instead of fetching it online.
	:param jsonURL str: The URL to a JSON file.

	:excepts: requests.exceptions.RequestException, json.JSONDecodeError

	:returns: A dictionary containing data from the mod list.
	:rtype: dict
	:returns "cannotAccessModList": If no valid asset URLs are in the mod list.
	:rtype: str
	:returns False: If an error occurs while fetching the JSON.
	:rtype: bool
	"""
	modlistData = []
	try:
		if jsonFilePath != None:
			# assume it's a testing environment and override online download
			if os.path.exists(jsonFilePath):
				with open(jsonFilePath, "r") as file:
					data = json.load(file)
		else:
			response = requests.get(jsonURL)
			response.raise_for_status() # Raise an error for bad status codes
			data = response.json()

		# Get all the asset urls
		global assetsURL
		assetsURL = None
		assetURLs = data.get("assetsURL", [])
		if not assetURLs:
			print("Error: \"assetsURL\" not found in JSON.")
			return
		
		def checkAssetURL(url):
			try:
				response = requests.get(url)
				response.raise_for_status()
				return url
			except requests.exceptions.RequestException as e:
				if devMode: print(f"Error fetching assets URL {url}: {e}")
				return None
		
		for url in data.get("assetsURL", []):
			result = checkAssetURL(url)

			if result != None:
				assetsURL = result
				if devMode: print(f"Using asset URL: {assetsURL}")
				break
			else:
				continue
		if assetsURL == None:
			if devMode: print("No valid asset url found :/")
			return "cannotAccessModList"

		# Iterate through the mods and download them
		for modID, modData in data.items():
			if modID == "assetsURL":
				continue # Skip the assetsURL entry

			FileName = modData.get("FileName", "")
			modName = modData.get("Name", "Unnamed Mod")
			modAuthor = modData.get("Author", "Unknown Author")
			modVersion = modData.get("Version", "Unknown")
			modGameVersion = modData.get("GameVersion", "Unknown")
			modDescription = modData.get("Description", "No Description.")
			if not FileName:
				print(f"Skipping mod {modID}: No \"FileName\" specified.")
				continue
			
			if assetsURL.endswith("/"):
				fileURL = f"{assetsURL}{modID}/{FileName}"
				screenshotsURL = f"{assetsURL}{modID}"
			else:
				fileURL = f"{assetsURL}/{modID}/{FileName}"
				screenshotsURL = f"{assetsURL}/{modID}"
			if devMode and showOutput:
				print("------------------------")
				print(f"File URL: {fileURL}")
				print(f"File Name: {FileName}")
				print(f"Mod ID: {modID}")
				print(f"Mod Name: {modName}")
				print(f"Mod Author: {modAuthor}")
				print(f"Mod Version: {modVersion}")
				print(f"Mod Game Version: {modGameVersion}")
				print(f"Mod Description: {modDescription}")
				print(f"Mod Manager Images Folder URL: {screenshotsURL}")
				print("------------------------")

			modlistData.append({
				"File URL": fileURL,
				"File Name": FileName,
				"Mod ID": modID,
				"Mod Name": modName,
				"Mod Author": modAuthor,
				"Mod Version": modVersion,
				"Mod Game Version": modGameVersion,
				"Mod Description": modDescription,
				"Mod Manager Images Folder URL": screenshotsURL
			})
	except requests.exceptions.RequestException as e:
		print(f"Error fetching JSON: {e}")
		return False
	except json.JSONDecodeError as e:
		print(f"Error parsing JSON: {e}")
		return False
	return modlistData

def onModSelect(modlistbox, modlistData, modNameLabel, modAuthorLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion):
	selectedIndex = modlistbox.curselection()
	if selectedIndex:
		mod = modlistData[selectedIndex[0]]
		showModDetails(mod, modNameLabel, modAuthorLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion)

def readSettings():
	settingsPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
	with open(settingsPath, "r") as f:
		settings = json.load(f)
		return(settings.get("Modlist"))

def showModDetails(mod, modNameLabel, modAuthorLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion):
	global selectedMod
	selectedMod = mod
	modNameLabel.config(text=mod["Mod Name"])
	modAuthorLabel.config(text=f"By: {mod["Mod Author"]}")
	modDescriptionLabel.config(text=mod["Mod Description"])
	installedVersionLabel.config(text=f"Installed Mod Version: {getInstalledModVersion(mod["Mod ID"])}")
	latestVersionLabel.config(text=f"Latest Mod Version: {mod["Mod Version"]}")
	installedGameVersionLabel.config(text=f"Installed Game Version: {gameVersion}")
	modGameVersionLabel.config(text=f"Mod Target Version {mod["Mod Game Version"]}")
	modIconLabel.config(image="", text="Loading Icon...")
	modIconLabel.image = None
	loadModIcon(selectedMod, modIconLabel)

def showModRepoDetails():
	repoInfo = subWindow.createSubWindow(onlineMods, "Mod Repo Details", "icons/icon-512.png", [640, 190])
	assetURLs = None
	global assetsURL
	if assetsURL.endswith("/"):
		assetURLs = requests.get(f"{assetsURL}modlist.json").json()
	else:
		assetURLs = requests.get(f"{assetsURL}/modlist.json").json()
		
	assetURL_Labels = []
	assetURL_Labels.append(tk.Label(repoInfo, text=f"Using Asset URL: {assetsURL}"))

	for url in assetURLs.get("assetsURL", []):
		assetURL_Labels.append(tk.Label(repoInfo, text=f"Asset URL: {url}"))
	for label in assetURL_Labels:
		label.pack()
	modRepoStatistics = requests.get(f"{assetsURL}/stats.json")
	modRepoStatistics.raise_for_status()
	modRepoStatistics = modRepoStatistics.json()
	modRepoStatisticsLabels = []
	for key, value in modRepoStatistics.items():
		modRepoStatisticsLabels.append(tk.Label(repoInfo, text=f"{key}: {value}"))
	for label in modRepoStatisticsLabels:
		label.pack()
### /FUNCTIONS ###

### SETTINGS ###
def addToCombobox(selectedItem, combobox):
	value = selectedItem.get()
	if devMode: print("Selected value:", value)
	if devMode: print(combobox.cget("values"))
	comboboxValues = list(combobox.cget("values"))
	if value not in comboboxValues:
		comboboxValues.append(value)
	else:
		return
	combobox.config(values=comboboxValues)
	writeSettings(comboboxValues)

def viewCustomModRepos():
	selectedItem = tk.StringVar()
	modlistWindow = subWindow.createSubWindow(onlineMods, "View custom mod lists", icon="icons/icon-512.png", size=[607, 38])
	modRepoCombobox = ttk.Combobox(modlistWindow, textvariable=selectedItem, values=[], width=25)
	
	# get saved mod list urls
	modlistSettings = readSettings()

	if modlistSettings:
		modRepoCombobox.config(values=modlistSettings.get("Custom Mod Repos", []))
	if len(modRepoCombobox.cget("values")) >= 1:
		modRepoCombobox.set(modRepoCombobox.cget("values")[0])
	
	modRepoCombobox.pack(side="left", anchor="w", padx=5)
	addURLbutton = ttk.Button(modlistWindow, text="Add URL to list", command=lambda: addToCombobox(selectedItem, modRepoCombobox))
	addURLbutton.pack(side="left", anchor="w")
	removeURLbutton = ttk.Button(modlistWindow, text="Remove URL from list", command=lambda: removeFromCombobox(selectedItem, modRepoCombobox))
	removeURLbutton.pack(side="left", anchor="w")

def selectCustomModRepo():
	selectedItem = tk.StringVar()
	modlistWindow = subWindow.createSubWindow(onlineMods, "View custom mod lists", icon="icons/icon-512.png", size=[489, 38])
	modRepoCombobox = ttk.Combobox(modlistWindow, textvariable=selectedItem, values=[], width=25)
	
	# get saved mod list urls
	modlistSettings = readSettings()

	if modlistSettings:
		modRepoCombobox.config(values=modlistSettings.get("Custom Mod Repos", []))
	if len(modRepoCombobox.cget("values")) >= 1:
		modRepoCombobox.set(modRepoCombobox.cget("values")[0])

	modRepoCombobox.pack(side="left", anchor="w", padx=5)
	useSelectedModListbutton = ttk.Button(modlistWindow, text="Use selected mod repo", command=lambda: useCustomModRepo(modlistWindow, selectedItem, modRepoCombobox))
	useSelectedModListbutton.pack(side="left", anchor="w")

def removeFromCombobox(selectedItem, combobox):
	value = selectedItem.get()
	if devMode: print("Selected value:", value)
	if devMode: print(combobox.cget("values"))
	comboboxValues = list(combobox.cget("values"))
	if value in comboboxValues:
		comboboxValues.remove(value)
	else:
		return
	combobox.config(values=comboboxValues)
	if len(combobox.cget("values")) >= 1:
		combobox.set(comboboxValues[0])
	else:
		combobox.set("")
	writeSettings(comboboxValues)

def useCustomModRepo(modlistWindow, selectedItem, combobox):
	if len(combobox.cget("values")) < 1:
		return
	if devMode: print("using custom mod repo")
	refreshModsConfig()
	newModData = loadMods(None, f"{selectedItem.get()}/modlist.json")
	if newModData == "cannotAccessModList":
		messagebox.showerror("Error", "Cannot access mod list. Please check the URL and try again.")
		return
	if newModData == False:
		messagebox.showerror("Error", "An error occured while fetching the mod list. Please try again later.")
		return
	modlistWindow.destroy()
	onlineMods.destroy()
	createWindow(parentWindow, gameVersion, newModData, True)

def writeSettings(newSettings):
	settingsPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
	settings = {}
	with open(settingsPath, "r") as f:
		settings = json.load(f)
	
	with open(settingsPath, "w") as f:
		if "Modlist" not in settings:
			settings["Modlist"] = {}
		settings["Modlist"]["Custom Mod Repos"] = newSettings
		json.dump(settings, f, indent="\t")
### /SETTINGS ###