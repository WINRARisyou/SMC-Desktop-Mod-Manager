### DEFS ###
import json
import os
from PIL import Image, ImageTk
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from . import createSubWindow as subWindow
devMode = False
downloadLocation = None
onWindows = None
installedMods = None
selectedMod = None
showOutput = False
refreshModsConfig = None
### /DEFS ###
### FUNCTIONS
def createWindow(baseWindow, gameVersion, modlistData):
	onlineMods = subWindow.createSubWindow(baseWindow, "Online Mod List", "icons/icon-512.png", [890, 534]) # Create a sub-window

	# Left Panel: Mod List
	modListFrame = tk.Frame(onlineMods)
	modListFrame.pack(side="left", fill="y", padx=10, pady=10)

	modListScrollbar = ttk.Scrollbar(modListFrame, orient="vertical")
	modListScrollbar.pack(side="right", fill="y")

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
	downloadButton = ttk.Button(downloadFrame, text="Download", command=lambda: downloadMod(selectedMod, gameVersion))
	downloadButton.config(state="disabled")
	downloadButton.pack(padx=0, pady=0, anchor="e")

	# Populate Mod List
	modListbox = tk.Listbox(modListFrame, width=25, yscrollcommand=modListScrollbar.set)
	modListbox.pack(side="left", fill="both", expand=True)
	modListScrollbar.config(command=modListbox.yview)

	for mod in modlistData:
		modListbox.insert(tk.END, mod["Mod Name"])

	modListbox.bind(
		"<<ListboxSelect>>", 
		lambda e: 
			onModSelect(modListbox, modlistData, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion),
			downloadButton.config(state="normal")
	)

def downloadFile(url, filename, downloadLocation):
	"""Download a file from a URL and save it to the specified directory."""
	response = requests.get(url, stream=True)
	if devMode: print(url)
	if response.status_code == 200:
		filePath = os.path.join(downloadLocation, filename)
		with open(filePath, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192): # if y'all are crazy and have absurdly large images we're gonna need to have a talk
				file.write(chunk)
		if devMode: print(f"Downloaded: {filename}")
	else:
		if devMode: print(f"Failed to download: {filename} (Status Code: {response.status_code})")

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

def loadMods(jsonFilePath, jsonURL="https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/modlist.json"):
	"""Fetch the JSON file, parse it, and download the mods."""
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
			messagebox.showerror("Error", "Could not access the online mod list at this time. Please try again later.")
			return "cannotAccessModList"

		# Iterate through the mods and download them
		for modID, modData in data.items():
			if modID == "assetsURL":
				continue # Skip the assetsURL entry

			FileName = modData.get("FileName", "")
			modName = modData.get("Name")
			modVersion = modData.get("Version", "1.0")
			modGameVersion = modData.get("GameVersion", "")
			modDescription = modData.get("Description", "")
			if not FileName:
				print(f"Skipping mod {modID}: No \"FileName\" specified.")
				continue
			
			if assetsURL.endswith("/"):
				fileURL = f"{assetsURL}{FileName}"
				screenshotsURL = f"{assetsURL}{modID}"
			else:
				fileURL = f"{assetsURL}/{FileName}"
				screenshotsURL = f"{assetsURL}/{modID}"
			if devMode and showOutput:
				print("------------------------")
				print(f"File URL: {fileURL}")
				print(f"File Name: {FileName}")
				print(f"Mod ID: {modID}")
				print(f"Mod Name: {modName}")
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
				"Mod Version": modVersion,
				"Mod Game Version": modGameVersion,
				"Mod Description": modDescription,
				"Mod Manager Images Folder URL": screenshotsURL
			})
	except requests.exceptions.RequestException as e:
		print(f"Error fetching JSON: {e}")
	except json.JSONDecodeError as e:
		print(f"Error parsing JSON: {e}")
	return modlistData

def onModSelect(modListbox, modlistData, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion):
	selectedIndex = modListbox.curselection()
	if selectedIndex:
		mod = modlistData[selectedIndex[0]]
		showModDetails(mod, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion)

def showModDetails(mod, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion):
	global selectedMod
	selectedMod = mod
	modNameLabel.config(text=mod["Mod Name"])
	modDescriptionLabel.config(text=mod["Mod Description"])
	installedVersionLabel.config(text=f"Installed Mod Version: {getInstalledModVersion(mod["Mod ID"])}")
	latestVersionLabel.config(text=f"Latest Mod Version: {mod["Mod Version"]}")
	installedGameVersionLabel.config(text=f"Installed Game Version: {gameVersion}")
	modGameVersionLabel.config(text=f"Mod Target Version {mod["Mod Game Version"]}")
	modIconLabel.config(image="", text="Loading Icon...")
	modIconLabel.image = None
	loadModIcon(selectedMod, modIconLabel)
### /FUNCTIONS ###