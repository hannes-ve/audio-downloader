AUDIO DOWNLOADER - INSTALLATION INSTRUCTIONS
==========================================

This package contains the Audio Downloader application, which allows you to download audio from YouTube and other sources.

REQUIREMENTS:
------------
- Windows 10/11
- Python 3.6 or higher (must be installed and added to PATH)

INSTALLATION:
------------
1. Double-click on "install.bat" to start the installation process
2. The script will:
   - Check if Python is installed
   - Install required Python packages
   - Create a desktop shortcut

TROUBLESHOOTING:
---------------
If you encounter any issues during installation:

1. Make sure Python is installed and added to PATH
   - Download from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. If you get permission errors:
   - Right-click on "install.bat"
   - Select "Run as administrator"

3. If the desktop shortcut doesn't work:
   - Open a command prompt in the installation folder
   - Run: python audio_downloader_gui.py

MANUAL INSTALLATION:
------------------
If the automatic installation fails, you can install manually:

1. Open a command prompt in this folder
2. Run: pip install -r audio_downloader_requirements.txt
3. Run: python audio_downloader_gui.py

For further assistance, please contact support or visit the project repository. 