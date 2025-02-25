import os
import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from . import createSubWindow as subWindow, resourcePath as resPath

devMode = True

def createWindow(baseWindow, gameVersion):
	onlineMods = subWindow.createSubWindow(baseWindow, "Online Mod List", "icons/icon-512.png", [832, 480])  # Create a sub-window
	onlineMods.iconphoto(True, tk.PhotoImage(file=resPath.resource_path("icons/icon-512.png")))
	onlineMods.title("Online Mod List")
	onlineMods.geometry("832x480")

	# Frame to hold mod entries
	modsFrame = tk.Frame(onlineMods)
	modsFrame.pack(fill="both", expand=True, padx=10, pady=10)

	# Canvas and scrollbar for mod list
	canvas = tk.Canvas(modsFrame)
	scrollbar = ttk.Scrollbar(modsFrame, orient="vertical", command=canvas.yview)
	scrollable_frame = tk.Frame(canvas)

	scrollable_frame.bind(
		"<Configure>",
		lambda e: canvas.configure(
			scrollregion=canvas.bbox("all")
		)
	)

	canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
	canvas.configure(yscrollcommand=scrollbar.set)

	canvas.pack(side="left", fill="both", expand=True)
	scrollbar.pack(side="right", fill="y")

	# Load mods and display them
	modlistData = loadMods("tests/downloadtest/modlist.json")
	for mod in modlistData:
		modFrame = tk.Frame(scrollable_frame)
		modFrame.pack(fill="x", pady=5)

		# Load mod icon
		icon_url = f"{mod['Mod Manager Images Folder URL']}/icon.png"
		icon_image = downloadImage(icon_url)
		if icon_image:
			icon_label = tk.Label(modFrame, image=icon_image)
			icon_label.image = icon_image  # Keep a reference to avoid garbage collection
			icon_label.pack(side="left", padx=5)

		# Mod info
		modInfoFrame = tk.Frame(modFrame)
		modInfoFrame.pack(side="left", fill="x", expand=True)

		modNameLabel = tk.Label(modInfoFrame, text=mod["Mod Name"], font=("Arial", 12, "bold"))
		modNameLabel.pack(anchor="w")

		modDescriptionLabel = tk.Label(modInfoFrame, text=mod["Mod Description"], wraplength=400, justify="left")
		modDescriptionLabel.pack(anchor="w")

		modVersionLabel = tk.Label(modInfoFrame, text=f"Mod Version: {mod['Mod Version']}")
		modVersionLabel.pack(anchor="w")

		modGameVersionLabel = tk.Label(modInfoFrame, text=f"Game Version: {mod['Mod Game Version']}")
		modGameVersionLabel.pack(anchor="w")

		# Check if the mod is installed and show installed version
		installedModVersion = getInstalledModVersion(mod["Mod ID"])
		if installedModVersion:
			installedModVersionLabel = tk.Label(modInfoFrame, text=f"Installed Version: {installedModVersion}")
			installedModVersionLabel.pack(anchor="w")

		# Warning if game versions don't match
		if mod["Mod Game Version"] != gameVersion and mod["Mod Game Version"].endswith("*"):
			modVer = mod["Mod Game Version"][:-1]
			if not gameVersion.startswith(modVer):
				warningLabel = tk.Label(modInfoFrame, text="Warning: Mod game version does not match installed game version!", fg="red")
				warningLabel.pack(anchor="w")
		else:
			warningLabel = tk.Label(modInfoFrame, text="Warning: Mod game version does not match installed game version!", fg="red")
			warningLabel.pack(anchor="w")


		# Download button
		downloadButton = ttk.Button(modFrame, text="Download", command=lambda m=mod: downloadMod(m, gameVersion))
		downloadButton.pack(side="right", padx=5)

def downloadImage(url):
	try:
		response = requests.get(url, stream=True)
		if response.status_code == 200:
			image = Image.open(response.raw)
			image = image.resize((64, 64), Image.ANTIALIAS)
			return ImageTk.PhotoImage(image)
		else:
			print(f"Failed to download image: {url} (Status Code: {response.status_code})")
			return None
	except Exception as e:
		print(f"Error downloading image: {e}")
		return None

def getInstalledModVersion(mod_id):
	# TODO
	# This function should check if the mod is installed and return its version
	...

def downloadMod(mod, gameVersion):
	if mod["Mod Game Version"] != gameVersion:
		warning = messagebox.askyesno("Warning", "The mod game version does not match the installed game version. Do you want to continue?")
		if not warning:
			return

	downloadFile(mod["File URL"], mod["File Name"], "Mods")
	messagebox.showinfo("Success", f"Mod {mod['Mod Name']} downloaded successfully!")

def downloadFile(url, filename, downloadLocation):
	"""Download a file from a URL and save it to the specified directory."""
	response = requests.get(url, stream=True)
	if devMode: print(url)
	if response.status_code == 200:
		file_path = os.path.join(downloadLocation, filename)
		with open(file_path, 'wb') as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)
		if devMode: print(f"Downloaded: {filename}")
	else:
		if devMode: print(f"Failed to download: {filename} (Status Code: {response.status_code})")

def loadMods(json_file_path, json_url="https://winrarisyou.github.io/SMC-Desktop-Mod-Manager/files/modlist.json"):
	"""Fetch the JSON file, parse it, and download the mods."""
	modlistData = []
	try:
		if not os.path.exists(json_file_path):
			response = requests.get(json_url)
			response.raise_for_status()  # Raise an error for bad status codes
			data = response.json()
		else:
			# assume it's a testing environment and override online download
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
			mod_name = modData.get("Name")
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

			screenshots_url = file_url[:-4]
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