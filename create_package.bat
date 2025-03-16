@echo off
echo Creating Audio Downloader Package
echo ================================
echo.

:: Check if 7-Zip is installed
where 7z >nul 2>&1
if %errorlevel% neq 0 (
    echo 7-Zip is not installed or not in PATH.
    echo Please install 7-Zip from https://www.7-zip.org/
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

:: Create icon if it doesn't exist
if not exist icon.ico (
    echo Creating icon...
    python create_icon.py
)

:: Create package directory
if not exist package mkdir package

:: Copy files to package directory
echo Copying files to package directory...
copy audio_downloader.py package\
copy audio_downloader_gui.py package\
copy audio_downloader_requirements.txt package\
copy install.bat package\
copy create_shortcut.ps1 package\
copy INSTALL_README.txt package\
copy run_audio_downloader.bat package\
if exist icon.ico copy icon.ico package\

:: Create ZIP archive
echo Creating ZIP archive...
cd package
7z a -tzip ..\AudioDownloader.zip *
cd ..

:: Create self-extracting executable
echo Creating self-extracting executable...
echo ;!@Install@!UTF-8! > config.txt
echo Title="Audio Downloader Installer" >> config.txt
echo BeginPrompt="Do you want to install Audio Downloader?" >> config.txt
echo RunProgram="install.bat" >> config.txt
echo ;!@InstallEnd@! >> config.txt

copy /b 7zS.sfx + config.txt + AudioDownloader.zip AudioDownloader_Setup.exe

:: Clean up
echo Cleaning up...
del config.txt
del AudioDownloader.zip
rmdir /s /q package

echo.
echo Package created successfully: AudioDownloader_Setup.exe
echo.
echo Note: You need to distribute 7zS.sfx with your package.
echo Download it from: https://www.7-zip.org/a/7z2301-extra.7z
echo.
echo Press any key to exit...
pause > nul 