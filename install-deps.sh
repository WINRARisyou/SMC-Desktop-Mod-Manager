#!/bin/bash
echo "Installing required Python modules..." && set -o noexec

pip install atexit
pip install ctypes
pip install json
pip install orjson
pip install os
pip install pyinstaller
pip install requests
pip install shutil
pip install subprocess
pip install sys
pip install tempfile
pip install tkinter
pip install zipfile

echo "Installation complete."