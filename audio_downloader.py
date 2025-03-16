#!/usr/bin/env python3
import os
import sys
import requests
from urllib.parse import urlparse
import argparse
import re
import subprocess
import shutil

def is_youtube_url(url):
    """
    Check if the URL is a YouTube URL.
    
    Args:
        url (str): The URL to check
        
    Returns:
        bool: True if it's a YouTube URL, False otherwise
    """
    youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
    return bool(re.match(youtube_regex, url))

def download_with_youtube_dl(url, output_path=None):
    """
    Download audio from a YouTube video using youtube-dl or yt-dlp.
    
    Args:
        url (str): The YouTube URL
        output_path (str, optional): Path where the audio file should be saved.
    
    Returns:
        str: Path to the downloaded audio file
    """
    # Check if youtube-dl or yt-dlp is installed
    youtube_dl_cmd = None
    for cmd in ['yt-dlp', 'youtube-dl']:
        if shutil.which(cmd):
            youtube_dl_cmd = cmd
            break
    
    if not youtube_dl_cmd:
        print("Neither yt-dlp nor youtube-dl is installed.")
        print("Please install one of them with:")
        print("  pip install yt-dlp")
        print("  or")
        print("  pip install youtube-dl")
        sys.exit(1)
    
    # Build command
    if output_path:
        output_template = output_path
    else:
        output_template = "%(title)s.%(ext)s"
    
    # Command to download only audio in mp3 format
    cmd = [
        youtube_dl_cmd,
        "-x",  # Extract audio
        "--audio-format", "mp3",  # Convert to mp3
        "--audio-quality", "0",  # Best quality
        "-o", output_template,  # Output template
        url  # URL to download
    ]
    
    print(f"Downloading audio from YouTube using {youtube_dl_cmd}: {url}")
    
    try:
        # Run the command
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Check if the command was successful
        if process.returncode != 0:
            stderr = process.stderr.read()
            print(f"Error: {stderr}")
            sys.exit(1)
        
        # If no specific output path was given, try to find the downloaded file
        if not output_path:
            print("\nDownload complete!")
            return None  # We don't know the exact filename as it's determined by youtube-dl
        else:
            print(f"\nDownload complete! Audio saved to: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"Error downloading with {youtube_dl_cmd}: {e}")
        sys.exit(1)

def download_from_youtube(url, output_path=None):
    """
    Try to download audio from a YouTube video using pytube.
    If that fails, fall back to youtube-dl/yt-dlp.
    
    Args:
        url (str): The YouTube URL
        output_path (str, optional): Path where the audio file should be saved.
                                     If not provided, it will use the video title.
    
    Returns:
        str: Path to the downloaded audio file
    """
    try:
        try:
            from pytube import YouTube
            # Attempt to use pytube first
            print(f"Attempting to download with pytube: {url}")
            yt = YouTube(url)
            
            try:
                # Get the title of the video for the filename
                video_title = yt.title
                safe_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                
                # Get the audio stream with the highest quality
                audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                
                if not audio_stream:
                    print("No audio stream found for this video. Falling back to youtube-dl/yt-dlp.")
                    return download_with_youtube_dl(url, output_path)
                
                # Determine output path
                if not output_path:
                    output_path = f"{safe_title}.mp3"
                
                # Download the audio
                print(f"Downloading audio stream...")
                downloaded_file = audio_stream.download(filename=output_path)
                
                print(f"\nDownload complete! Audio saved to: {output_path}")
                return output_path
            except Exception as e:
                print(f"Error with pytube: {e}")
                print("Falling back to youtube-dl/yt-dlp...")
                return download_with_youtube_dl(url, output_path)
                
        except ImportError:
            print("pytube library not found. Using youtube-dl/yt-dlp instead.")
            return download_with_youtube_dl(url, output_path)
            
    except Exception as e:
        print(f"Error downloading from YouTube: {e}")
        sys.exit(1)

def download_audio(url, output_path=None):
    """
    Download an audio file from a URL and save it locally.
    
    Args:
        url (str): The URL of the audio file to download
        output_path (str, optional): Path where the file should be saved.
                                    If not provided, it will be extracted from the URL.
    
    Returns:
        str: Path to the downloaded file
    """
    # Check if it's a YouTube URL
    if is_youtube_url(url):
        return download_from_youtube(url, output_path)
    
    try:
        # Send a GET request to the URL
        print(f"Downloading from: {url}")
        response = requests.get(url, stream=True)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Determine the filename if output_path is not provided
        if not output_path:
            # Try to get filename from Content-Disposition header
            if 'Content-Disposition' in response.headers:
                import re
                filename_match = re.search(r'filename="(.+)"', response.headers['Content-Disposition'])
                if filename_match:
                    output_path = filename_match.group(1)
            
            # If still no output_path, extract filename from URL
            if not output_path:
                parsed_url = urlparse(url)
                output_path = os.path.basename(parsed_url.path)
            
            # If path is still empty or doesn't have an extension, use a default name
            if not output_path or '.' not in output_path:
                output_path = "downloaded_audio.mp3"
        
        # Save the file
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    
                    # Display progress
                    if total_size > 0:
                        percent = int(100 * downloaded / total_size)
                        sys.stdout.write(f"\rDownload progress: {percent}% ({downloaded} / {total_size} bytes)")
                        sys.stdout.flush()
        
        print(f"\nDownload complete! File saved to: {output_path}")
        return output_path
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download audio files from a URL")
    parser.add_argument("url", help="URL of the audio file to download (works with YouTube URLs)")
    parser.add_argument("-o", "--output", help="Output filename (optional)")
    
    args = parser.parse_args()
    
    download_audio(args.url, args.output)

if __name__ == "__main__":
    main()
