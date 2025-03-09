# How to Create a Mod Repository
Creating a mod repository for DMM involves creating a `stats.json` file and a `modlist.json` file. Below is a step-by-step guide on how to create a mod repository using these JSON files.

## Step 1: Create `stats.json`
Create a new file named `stats.json` in your repository's directory. This file will contain metadata about your mod repository.

### Define the Repository Metadata
Copy and paste the following JSON structure into your `stats.json` file:

```json
{
	"Mod Repo Version": "1.0",
	"Mod Repo Name": "Your Repository Name",
	"Mod Repo Description": "A brief description of your repository.",
	"Mod Repo Author": "Your Name"
}
```

- **Mod Repo Version**: The version of your mod repository.
- **Mod Repo Name**: The name of your mod repository.
- **Mod Repo Description**: A brief description of your mod repository.
- **Mod Repo Author**: The author of the mod repository.

### Example:

```json
{
	"Mod Repo Version": "1.0",
	"Mod Repo Name": "WINRAR's test mod repo",
	"Mod Repo Description": "A test mod repo for SMC DMM.",
	"Mod Repo Author": "WINRARisyou"
}
```

## Step 2: Create `modlist.json`

Create a new file named `modlist.json` in your repository's directory. This file will contain a list of all the mods in your repository.

### Define the Mod List

Copy and paste the following JSON structure into your `modlist.json` file:

```json
{
	"assetsURL": ["https://yourassetsurl"],
	"your.mod.id": {
		"FileName": "yourmod.zip",
		"Version": "1.0",
		"GameVersion": "Game Version your mod is built for",
		"Description": "A brief description of your mod.",
		"Name": "Your Mod Name",
		"Author": "Your Name"
	},
	"your.next.mod.id": {
		"FileName": "yourmod.zip",
		"Version": "1.0",
		"GameVersion": "Game Version your mod is built for",
		"Description": "A brief description of your mod.",
		"Name": "Your Mod Name",
		"Author": "Your Name"
	},
	...
}
```

- **assetsURL**: A list of URLs where the mod assets are hosted.
- **your.mod.id**: The ID of the mod you are adding to your repo.
  - **FileName**: The name of the mod file.
  - Everything below should already be in the mod file, just unpack the mod zip and take it from mod.json
  - **Version**: The version of your mod.
  - **GameVersion**: The version of the game your mod is compatible with.
  - **Description**: A brief description of your mod.
  - **Name**: The name of your mod.
  - **Author**: The author of the mod.

### Example:

```json
{
	"assetsURL": ["https://winrarisyou.github.io/SMC-DMM-Test"],
	"winrarisyou.testmod": {
		"FileName": "testmod.zip",
		"Version": "0.1",
		"GameVersion": "v8.beta29.6",
		"Description": "Test mod to confirm local mod repos work.",
		"Name": "Test Mod",
		"Author": "WINRARisyou"
	},
	"winrarisyou.testmod2": {
		"FileName": "testmod.zip",
		"Version": "0.1",
		"GameVersion": "v8.beta29.6",
		"Description": "Secondary test mod.",
		"Name": "Test Mod",
		"Author": "WINRARisyou"
	},
}
```

## Step 3: Add Your Mods
Mods need to be placed in a directory that has the name of the mod id, so if the mod is "winrarisyou.testmod," you need a folder structure that looks like this

```
root/
├── winrarisyou.testmod/
│	├─ testmod.zip
│	└─ icon.png
└── winrarisyou.testmod2/
	├─ testmod.zip
	└─ icon.zip

```
You can view [the main modlist](https://archive.org/download/SMC-DMM-Mods)  as an example of what the structure should look like (`modlist.json` is stored in a different, hardcoded location for the main modlist, so it isn't there).

## Step 4: Test Your Repository
Load your repository into the game and test it to make sure everything works as intended.
## Step 5: Share
Share your repository with others by providing the URL to your `stats.json` and `modlist.json` files (if your stats.json is at `https://example.com/stats.json`, then the repo URL is `https://example.json`).
<br>
Make sure to include instructions on how to add the repository to the game.