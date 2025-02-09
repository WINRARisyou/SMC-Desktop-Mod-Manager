# Super Mario Construct Desktop Mod Manager
Way to manage replacing game files in Super Mario Construct

## How to Use

1. **Set Game Location**: 
	- Open the application.
	- Go to `File` > `Set Game Location`.
	- Select the folder where `Super Mario Construct.exe` is located (`%appdata%\itch\apps\super-mario-construct` if you installed via itch.io app).

2. **Set Mods Folder Location**: 
	- Go to `File` > `Set Mods Folder Location` (By default, it will be in the same directory as the executable).
	- Select the folder where your mods are stored.

3. **Enable/Disable Mods**:
	- The main window will display a list of available mods.
	- Double click the checkboxes to enable or disable mods.
	- Use the up and down arrows to adjust the priority of the mods.
    - Mods higher in the list will take priority over others if they modify the same file

4. **Save and Play**:
	- Click the `Save & Play` button to apply the selected mods and start the game.
	- Click the `Play Without Mods` button to start the game without applying any mods.

## Building from Source
1. **Clone the reposity**
	- You can either run:
	```sh
	git clone https://github.com/WINRARisyou/SMC-Desktop-Mod-Manager
	```
	or you can download this repository as a .zip file, and unpack it wherever you want.

2. **Install Dependencies**:
	- Run the `install-deps.bat` script to install the required Python modules.

3. **Build the Executable**:
	- Use PyInstaller to build the executable.
	- Open a command prompt and navigate to the project directory.
	- Execute the following command:

	```sh
	pyinstaller Super Mario Construct Mod Manager.spec
	```

4. **Run the Application**:
	- After building, the executable will be located in the `dist` folder.
	- Run the executable to start the mod manager.
	- You can also run `main.py` to run without building the executable

## Making Mods
Open [the readme in example mods](Example%20Mods/README.md) to find out how to make some