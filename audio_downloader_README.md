# Audio Downloader

A simple GUI application for downloading audio from various sources including YouTube.

## Features

- Download audio from YouTube videos
- Download audio from direct URLs
- Select custom save location
- Real-time download progress updates
- Support for multiple download methods (pytube, youtube-dl, yt-dlp)

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages (automatically installed with pip):
  - PyQt5
  - requests
  - pytube
  - yt-dlp

### Option 1: Run from Source

1. Clone this repository:
```
git clone https://github.com/hannes-ve/audio-downloader.git
cd audio-downloader
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Run the application:
```
python audio_downloader_gui.py
```

### Option 2: Standalone Windows Executable

1. Download the latest release from the [Releases](https://github.com/hannes-ve/audio-downloader/releases) page.
2. Extract the ZIP file to a location of your choice.
3. Run `audio_downloader.exe`.

## Building from Source

To build the standalone executable:

1. Install PyInstaller:
```
pip install pyinstaller
```

2. Build the executable:
```
pyinstaller --onefile --windowed --icon=icon.ico --name="Audio Downloader" audio_downloader_gui.py
```

## Usage

1. Enter the URL of the YouTube video or direct audio file link in the URL field.
2. (Optional) Click "Browse" to select a custom save location.
3. Click "Download" to start the download process.
4. Wait for the download to complete - a notification will appear when finished.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses [pytube](https://github.com/pytube/pytube) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloads
- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI
