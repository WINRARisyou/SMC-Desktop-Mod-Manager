import os
import requests
import json
devMode = False
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

def loadMods(json_file_path):
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
			return {"File URL": file_url, "File Name": file_name, "Mod Version": mod_id, "Mod Version": mod_version}

	except requests.exceptions.RequestException as e:
		print(f"Error fetching JSON: {e}")
	except json.JSONDecodeError as e:
		print(f"Error parsing JSON: {e}")
