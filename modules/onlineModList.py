import os
import requests
import json
import tkinter as tk
from . import createSubWindow as subWindow, resourcePath as resPath

def createWindow(baseWindow):
	onlineMods = subWindow.createSubWindow(baseWindow, "About", "icons/icon-512.png", [640,700])  # Create a sub-window
	onlineMods.iconphoto(True, tk.PhotoImage(file=resPath.resource_path("icons/icon-512.png")))
	onlineMods.title("Mod List")
	onlineMods.geometry("832x480")

devMode = True
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
			# assume it's a testing environment and override online 
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

			modlistData.append({
				"Mod ID": mod_id,
				"File URL": file_url,
				"File Name": file_name,
				"Mod Version": mod_version,
				"Mod Game Version": mod_game_version,
				"Mod Description": mod_description
			})
	except requests.exceptions.RequestException as e:
		print(f"Error fetching JSON: {e}")
	except json.JSONDecodeError as e:
		print(f"Error parsing JSON: {e}")
	return modlistData
