import json
import os
from . import onlineModList
settingsPath = os.path.join(os.path.dirname(__file__), "settings.json")
settings = {}
if os.path.exists(settingsPath):
	with open(settingsPath) as f:
		settings = json.load(f)

modlistSettings = settings.get("modlist")
if modlistSettings:
	onlineModList.settings = modlistSettings