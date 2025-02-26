import os
import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from . import createSubWindow as subWindow, resourcePath as resPath

devMode = False
downloadLocation = None
onWindows = None
selectedMod = None
installedMods = None
showOutput = False
def handleScroll(element, event):
	if event.num == 4:
		element.yview_scroll(-1, "units")
	elif event.num == 5:
		element.yview_scroll(1, "units")
	else:
		element.yview_scroll(int(-1*(event.delta/120)), "units") # For Windows and macOS

def createWindow(baseWindow, gameVersion, modlistData):
	onlineMods = subWindow.createSubWindow(baseWindow, "Online Mod List", "icons/icon-512.png", [1440, 720]) # Create a sub-window

	# Left Panel: Mod List
	modListFrame = tk.Frame(onlineMods)
	modListFrame.pack(side="left", fill="y", padx=10, pady=10)

	modListCanvas = tk.Canvas(modListFrame)
	modListScrollbar = ttk.Scrollbar(modListFrame, orient="vertical", command=modListCanvas.yview)
	modListScrollableFrame = tk.Frame(modListCanvas)

	modListCanvas.bind_all("<MouseWheel>", lambda e: handleScroll(modListCanvas, e))
	modListCanvas.bind_all("<Button-4>", lambda e: handleScroll(modListCanvas, e))
	modListCanvas.bind_all("<Button-5>", lambda e: handleScroll(modListCanvas, e))

	modListScrollableFrame.bind(
		"<Configure>",
		lambda e: modListCanvas.configure(
			scrollregion=modListCanvas.bbox("all")
		)
	)

	modListCanvas.create_window((0, 0), window=modListScrollableFrame, anchor="nw")
	modListCanvas.configure(yscrollcommand=modListScrollbar.set)

	modListCanvas.pack(side="left", fill="both", expand=True)
	modListScrollbar.pack(side="right", fill="y")

	# Center: Screenshots
	screenshotsFrame = tk.Frame(onlineMods)
	screenshotsFrame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

	screenshotsLabel = tk.Label(screenshotsFrame, text="Screenshots", font=("Arial", 16))
	screenshotsLabel.pack(pady=10)

	# Bottom: Mod Details and Download
	detailsFrame = tk.Frame(onlineMods)
	detailsFrame.pack(side="bottom", fill="x", padx=10, pady=10)

	# Mod Icon and Info
	modInfoFrame = tk.Frame(detailsFrame)
	modInfoFrame.pack(side="left", fill="x", expand=True)

	modIconLabel = tk.Label(modInfoFrame, text="Mod Icon") # Placeholder
	modIconLabel.pack(side="left", padx=5)

	modDetailsFrame = tk.Frame(modInfoFrame)
	modDetailsFrame.pack(side="left", fill="x", expand=True)

	modNameLabel = tk.Label(modDetailsFrame, text="Mod Name", font=("Arial", 12, "bold"))
	modNameLabel.pack(anchor="w")

	modDescriptionLabel = tk.Label(modDetailsFrame, text="Mod Description", wraplength=400, justify="left")
	modDescriptionLabel.pack(anchor="w")

	# Version Info
	versionFrame = tk.Frame(detailsFrame)
	versionFrame.pack(side="right", padx=10)

	installedVersionLabel = tk.Label(versionFrame, text="Installed Mod Version")
	installedVersionLabel.pack(anchor="e")

	latestVersionLabel = tk.Label(versionFrame, text="Latest Mod Version")
	latestVersionLabel.pack(anchor="e")

	installedGameVersionLabel = tk.Label(versionFrame, text="Installed Game Version")
	installedGameVersionLabel.pack(anchor="e")

	modGameVersionLabel = tk.Label(versionFrame, text="Mod Target Version")
	modGameVersionLabel.pack(anchor="e")

	# Download Button
	downloadButton = ttk.Button(detailsFrame, text="Download", command=lambda: downloadMod(selectedMod, gameVersion))
	downloadButton.pack(side="right", padx=5)

	# Populate Mod List
	for mod in modlistData:
		modButton = ttk.Button(modListScrollableFrame, text=mod["Mod Name"], command=lambda m=mod: showModDetails(m, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion))
		modButton.pack(fill="x", pady=5)

def loadModIcon(mod, modIconLabel):
	iconURL = f"{mod['Mod Manager Images Folder URL']}/icon.png"
	iconImage = downloadImage(iconURL)
	if iconImage != None:
		modIconLabel.config(image=iconImage)
		modIconLabel.image = iconImage
	else:
		modIconLabel.config(image="", text="No Icon Found")
		modIconLabel.image = None

def showModDetails(mod, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, modIconLabel, gameVersion):
	global selectedMod
	selectedMod = mod
	modNameLabel.config(text=mod["Mod Name"])
	modDescriptionLabel.config(text=mod["Mod Description"])
	installedVersionLabel.config(text=f"Installed Mod Version: {getInstalledModVersion(mod["Mod ID"])}")
	latestVersionLabel.config(text=f"Latest Mod Version: {mod["Mod Version"]}")
	installedGameVersionLabel.config(text=f"Installed Game Version: {gameVersion}")
	modGameVersionLabel.config(text=f"Mod Target Version {mod["Mod Game Version"]}")
	loadModIcon(selectedMod, modIconLabel)

	# TODO: Load and display screenshots	
def downloadImage(url):
	try:
		response = requests.get(url, stream=True)
		if response.status_code == 200:
			image = Image.open(response.raw)
			image = image.resize((64, 64), Image.Resampling.LANCZOS)
			return ImageTk.PhotoImage(image)
		else:
			print(f"Failed to get image: {url} (Status Code: {response.status_code})")
			return None
	except Exception as e:
		print(f"Error downloading image: {e}")
		return None

def getInstalledModVersion(modID):
	if modID in installedMods:
		return installedMods[modID]
	else:
		return "Mod Not Installed"

def downloadSelectedMod():
	...

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

	downloadFile(mod["File URL"], mod["File Name"], downloadLocation)
	messagebox.showinfo("Success", f"Mod {mod["Mod Name"]} downloaded successfully!")

def downloadFile(url, filename, downloadLocation):
	"""Download a file from a URL and save it to the specified directory."""
	response = requests.get(url, stream=True)
	if devMode: print(url)
	if response.status_code == 200:
		filePath = os.path.join(downloadLocation, filename)
		with open(filePath, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)
		if devMode: print(f"Downloaded: {filename}")
	else:
		if devMode: print(f"Failed to download: {filename} (Status Code: {response.status_code})")

def loadMods(jsonFilePath, jsonURL="https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/modlist.json"):
	"""Fetch the JSON file, parse it, and download the mods."""
	modlistData = []
	try:
		if not os.path.exists(jsonFilePath) or jsonFilePath == "":
			response = requests.get(jsonURL)
			response.raise_for_status() # Raise an error for bad status codes
			data = response.json()
		else:
			# assume it"s a testing environment and override online download
			with open(jsonFilePath, "r") as file:
				data = json.load(file)

		# Get the base assets URL
		assetsURL = data.get("assetsURL", "")
		if not assetsURL:
			print("Error: \"assetsURL\" not found in JSON.")
			return

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