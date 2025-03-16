# Creating a Self-Extracting Executable for Audio Downloader

This guide explains how to create a self-extracting executable package for the Audio Downloader application that can be easily distributed and installed on Windows machines.

## Prerequisites

1. **7-Zip**: Download and install from [7-Zip website](https://www.7-zip.org/)
2. **7zS.sfx**: Download the 7-Zip extra package from [here](https://www.7-zip.org/a/7z2301-extra.7z) and extract `7zS.sfx` to the project directory
3. **Python**: Make sure Python is installed on your system

## Steps to Create the Package

1. Make sure all the required files are in your project directory:
   - `audio_downloader.py`
   - `audio_downloader_gui.py`
   - `audio_downloader_requirements.txt`
   - `create_icon.py` (to generate an icon if needed)
   - `create_package.bat` (the packaging script)
   - `create_shortcut.ps1` (for creating desktop shortcuts)
   - `install.bat` (installation script)
   - `INSTALL_README.txt` (instructions for users)
   - `run_audio_downloader.bat` (direct launcher)
   - `7zS.sfx` (from 7-Zip extras)

2. Run the packaging script:
   ```
   create_package.bat
   ```

3. The script will:
   - Create an icon if one doesn't exist
   - Copy all necessary files to a temporary package directory
   - Create a ZIP archive of these files
   - Create a self-extracting executable using 7zS.sfx
   - Clean up temporary files

4. The final output will be `AudioDownloader_Setup.exe` in your project directory

## Distributing the Package

Simply share the `AudioDownloader_Setup.exe` file with your users. When they run it:

1. They will be prompted to extract the files
2. The installation script will automatically run
3. Required Python packages will be installed
4. A desktop shortcut will be created

## Requirements for End Users

End users must have:
1. Windows 10 or 11
2. Python 3.6 or higher installed and added to PATH

## Troubleshooting

If users encounter issues:
- Make sure they have Python installed and added to PATH
- They may need to run the installer as administrator
- If the automatic installation fails, they can follow the manual installation instructions in INSTALL_README.txt 