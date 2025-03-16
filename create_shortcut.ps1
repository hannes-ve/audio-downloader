$WshShell = New-Object -ComObject WScript.Shell
$CurrentDir = (Get-Location).Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutFile = "$DesktopPath\Audio Downloader.lnk"
$Target = "pythonw.exe"
$Arguments = "$CurrentDir\audio_downloader_gui.py"
$IconLocation = "$CurrentDir\icon.ico"

# Create the shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $Target
$Shortcut.Arguments = $Arguments
$Shortcut.WorkingDirectory = $CurrentDir
$Shortcut.Description = "Audio Downloader Application"

# Set icon if it exists
if (Test-Path $IconLocation) {
    $Shortcut.IconLocation = $IconLocation
}

$Shortcut.Save()

Write-Host "Desktop shortcut created at: $ShortcutFile" 