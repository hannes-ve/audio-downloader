import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sys", "PyQt5", "requests", "urllib", "re", "subprocess", "shutil"],
    "excludes": ["tkinter"],
    "include_files": ["audio_downloader.py"],
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Audio Downloader",
    version="1.0.0",
    description="Audio Downloader Application",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "audio_downloader_gui.py", 
            base=base,
            target_name="audio_downloader.exe",
            icon="icon.ico"  # You'll need to add an icon file
        )
    ]
)
