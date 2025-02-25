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
selected_mod = None
def handleScroll(element, event):
	if event.num == 4:
		element.yview_scroll(-1, "units")
	elif event.num == 5:
		element.yview_scroll(1, "units")
	else:
		element.yview_scroll(int(-1*(event.delta/120)), "units") # For Windows and macOS

def createWindow(baseWindow, gameVersion, modlistData):
	onlineMods = subWindow.createSubWindow(baseWindow, "Online Mod List", "icons/icon-512.png", [832, 480]) # Create a sub-window
	onlineMods.iconphoto(True, tk.PhotoImage(file=resPath.resource_path("icons/icon-512.png")))
	onlineMods.title("Online Mod List")
	onlineMods.geometry("832x480")

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

	modGameVersionLabel = tk.Label(versionFrame, text="Mod Game Version")
	modGameVersionLabel.pack(anchor="e")

	# Download Button
	downloadButton = ttk.Button(detailsFrame, text="Download", command=lambda: downloadMod(selected_mod, gameVersion))
	downloadButton.pack(side="right", padx=5)

	# Populate Mod List
	for mod in modlistData:
		modButton = ttk.Button(modListScrollableFrame, text=mod["Mod Name"], command=lambda m=mod: showModDetails(m, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, gameVersion))
		modButton.pack(fill="x", pady=5)

def showModDetails(mod, modNameLabel, modDescriptionLabel, installedVersionLabel, latestVersionLabel, installedGameVersionLabel, modGameVersionLabel, gameVersion):
	global selected_mod
	selected_mod = mod
	modNameLabel.config(text=mod["Mod Name"])
	modDescriptionLabel.config(text=mod["Mod Description"])
	installedVersionLabel.config(text=f"Installed Mod Version: {getInstalledModVersion(mod['Mod ID'])}")
	latestVersionLabel.config(text=f"Latest Mod Version: {mod['Mod Version']}")
	installedGameVersionLabel.config(text=f"Installed Game Version: {gameVersion}")
	modGameVersionLabel.config(text=f"Mod Game Version: {mod['Mod Game Version']}")

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

def getInstalledModVersion(mod_id):
	# TODO
	# This function should check if the mod is installed and return its version
	...

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
		file_path = os.path.join(downloadLocation, filename)
		with open(file_path, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)
		if devMode: print(f"Downloaded: {filename}")
	else:
		if devMode: print(f"Failed to download: {filename} (Status Code: {response.status_code})")

def loadMods(json_file_path, json_url="https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/modlist.json"):
	"""Fetch the JSON file, parse it, and download the mods."""
	modlistData = []
	try:
		if not os.path.exists(json_file_path) or json_file_path == "":
			response = requests.get(json_url)
			response.raise_for_status() # Raise an error for bad status codes
			data = response.json()
		else:
			# assume it"s a testing environment and override online download
			with open(json_file_path, "r") as file:
				data = json.load(file)

		# Get the base assets URL
		assets_url = data.get("assetsURL", "")
		if not assets_url:
			print("Error: \"assetsURL\" not found in JSON.")
			return

		# Iterate through the mods and download them
		for mod_id, modData in data.items():
			if mod_id == "assetsURL":
				continue # Skip the assetsURL entry

			file_name = modData.get("FileName", "")
			mod_name = modData.get("Name")
			mod_version = modData.get("Version", "1.0")
			mod_game_version = modData.get("GameVersion", "")
			mod_description = modData.get("Description", "")
			if not file_name:
				print(f"Skipping mod {mod_id}: No \"FileName\" specified.")
				continue

			if assets_url.endswith("/"):
				file_url = f"{assets_url}{file_name}"
				screenshots_url = f"{assets_url}{mod_id}"
			else:
				file_url = f"{assets_url}/{file_name}"
				screenshots_url = f"{assets_url}/{mod_id}"

			print("------------------------")
			print(f"File URL: {file_url}")
			print(f"File Name: {file_name}")
			print(f"Mod ID: {mod_id}")
			print(f"Mod Name: {mod_name}")
			print(f"Mod Version: {mod_version}")
			print(f"Mod Game Version: {mod_game_version}")
			print(f"Mod Description: {mod_description}")
			print(f"Mod Manager Images Folder URL: {screenshots_url}")
			print("------------------------")

			modlistData.append({
				"File URL": file_url,
				"File Name": file_name,
				"Mod ID": mod_id,
				"Mod Name": mod_name,
				"Mod Version": mod_version,
				"Mod Game Version": mod_game_version,
				"Mod Description": mod_description,
				"Mod Manager Images Folder URL": screenshots_url
			})
	except requests.exceptions.RequestException as e:
		print(f"Error fetching JSON: {e}")
	except json.JSONDecodeError as e:
		print(f"Error parsing JSON: {e}")
	return modlistData