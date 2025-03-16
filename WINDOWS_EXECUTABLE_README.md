# Creating a Windows Executable for Audio Downloader

This guide explains how to create a standalone Windows executable for the Audio Downloader application that can be easily distributed and run on Windows 10/11 machines without requiring Python to be installed.

## Prerequisites

1. **Windows 10/11 Machine**: The executable should be built on a Windows machine for best compatibility
2. **Python 3.6 or higher**: Install from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
3. **Project Files**: All the Audio Downloader project files

## Step-by-Step Instructions

### 1. Set Up the Environment

1. Clone or copy the project files to your Windows machine
2. Open Command Prompt as Administrator
3. Navigate to the project directory:
   ```
   cd path\to\audio-downloader-python
   ```

### 2. Install Required Dependencies

Install all the required packages:

```
pip install -r audio_downloader_requirements.txt
```

Make sure PyInstaller is installed:

```
pip install pyinstaller
```

### 3. Create an Icon (Optional)

Run the icon creation script:

```
python create_icon.py
```

This will create an `icon.ico` file in the project directory.

### 4. Create the Executable

Run PyInstaller with the following command:

```
pyinstaller --onefile --windowed --icon=icon.ico --name="Audio Downloader" audio_downloader_gui.py
```

Options explained:
- `--onefile`: Creates a single executable file
- `--windowed`: Prevents a console window from appearing when the application runs
- `--icon=icon.ico`: Uses the specified icon for the executable
- `--name="Audio Downloader"`: Sets the name of the output executable

### 5. Find the Executable

After PyInstaller completes, the executable will be located in the `dist` folder:

```
dist\Audio Downloader.exe
```

This is your standalone executable that can be distributed to users.

## Distribution

Simply share the `Audio Downloader.exe` file with your users. They can run it directly without installing Python or any dependencies.

## Troubleshooting

1. **Antivirus Warnings**: PyInstaller executables may be flagged by antivirus software because they're self-extracting archives. This is normal and you may need to add an exception.

2. **Missing DLLs**: If users encounter missing DLL errors, you may need to include additional DLLs with the `--add-data` option in PyInstaller.

3. **Slow Startup**: If the executable is slow to start, try using the `--noupx` option when creating it:
   ```
   pyinstaller --onefile --windowed --noupx --icon=icon.ico --name="Audio Downloader" audio_downloader_gui.py
   ```

4. **Large File Size**: The executable will be larger than your original code (typically 30-50MB) because it includes Python and all dependencies.

## Advanced Options

For more control over the build process, you can create a `.spec` file:

```
pyi-makespec --onefile --windowed --icon=icon.ico audio_downloader_gui.py
```

Then edit the generated `.spec` file and build using:

```
pyinstaller Audio\ Downloader.spec
```

This allows for more customization, such as adding hidden imports or additional data files.

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller GitHub](https://github.com/pyinstaller/pyinstaller) 