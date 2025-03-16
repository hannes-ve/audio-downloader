# Building Windows Executable with GitHub Actions

This guide explains how to use GitHub Actions to automatically build a Windows executable for the Audio Downloader application, even if you're developing on macOS.

## Setup Instructions

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in (or create an account if you don't have one)
2. Click the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "audio-downloader-python")
4. Choose whether to make it public or private
5. Click "Create repository"

### 2. Push Your Code to GitHub

From your local project directory:

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit the files
git commit -m "Initial commit"

# Add the GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/audio-downloader-python.git

# Push to GitHub
git push -u origin main
```

### 3. GitHub Actions Workflow

The workflow file (`.github/workflows/build.yml`) has already been created in your repository. This file tells GitHub Actions how to build your Windows executable.

The workflow will:
1. Run on a Windows virtual machine
2. Install Python and required dependencies
3. Create the icon for your application
4. Build the executable using PyInstaller
5. Upload the executable as an artifact
6. Create and upload a ZIP file containing the executable

### 4. Trigger the Workflow

The workflow will automatically run when you push to the `main` branch. You can also trigger it manually:

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select the "Build Windows Executable" workflow
4. Click "Run workflow" and select the branch to run it on
5. Click the green "Run workflow" button

### 5. Download the Executable

After the workflow completes:

1. Go to the "Actions" tab in your repository
2. Click on the completed workflow run
3. Scroll down to the "Artifacts" section
4. Download either:
   - `Audio-Downloader-Windows` (the raw .exe file)
   - `Audio-Downloader-Windows-ZIP` (the .exe file in a ZIP archive)

## Troubleshooting

### Workflow Fails

If the workflow fails:

1. Click on the failed workflow run
2. Examine the logs to see what went wrong
3. Make necessary changes to your code
4. Push the changes to GitHub to trigger the workflow again

### Missing Dependencies

If the build fails due to missing dependencies:

1. Make sure all required packages are listed in `audio_downloader_requirements.txt`
2. Check if any packages require special handling in PyInstaller

## Advantages of This Approach

- No need to install Windows or additional software on your Mac
- Builds in a clean Windows environment for maximum compatibility
- Automatically creates a new build when you update your code
- Easy to share the executable with others

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [GitHub Artifacts Documentation](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts) 