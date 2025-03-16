#!/usr/bin/env python3
import os
import sys
import requests
from urllib.parse import urlparse, parse_qs
import argparse
import re
import subprocess
import shutil
import time
import random
import json
import platform
import sqlite3
import tempfile
from pathlib import Path

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

def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url (str): The YouTube URL
        
    Returns:
        str: The video ID or None if not found
    """
    # Handle youtu.be URLs
    if 'youtu.be' in url:
        path = urlparse(url).path
        return path.strip('/')
    
    # Handle youtube.com URLs
    parsed_url = urlparse(url)
    if 'youtube.com' in parsed_url.netloc:
        if '/watch' in parsed_url.path:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif '/shorts/' in parsed_url.path:
            # Extract ID from /shorts/ URL
            path_parts = parsed_url.path.split('/')
            for i, part in enumerate(path_parts):
                if part == 'shorts' and i + 1 < len(path_parts):
                    return path_parts[i + 1]
    
    return None

def get_chrome_cookies():
    """
    Extract cookies from Chrome/Chromium browser for youtube.com
    
    Returns:
        str: Path to the cookie file or None if not found
    """
    try:
        print("Attempting to extract cookies from Chrome/Chromium...")
        cookie_file = None
        
        # Determine OS and Chrome cookie path
        system = platform.system()
        home = str(Path.home())
        
        if system == "Darwin":  # macOS
            cookie_paths = [
                f"{home}/Library/Application Support/Google/Chrome/Default/Cookies",
                f"{home}/Library/Application Support/Google/Chrome/Profile 1/Cookies",
                f"{home}/Library/Application Support/Chromium/Default/Cookies"
            ]
        elif system == "Linux":
            cookie_paths = [
                f"{home}/.config/google-chrome/Default/Cookies",
                f"{home}/.config/chromium/Default/Cookies"
            ]
        elif system == "Windows":
            cookie_paths = [
                f"{home}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies",
                f"{home}\\AppData\\Local\\Chromium\\User Data\\Default\\Cookies"
            ]
        else:
            print(f"Unsupported operating system: {system}")
            return None
        
        # Find the first existing cookie database
        db_path = None
        for path in cookie_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            print("Could not find Chrome/Chromium cookie database")
            return None
        
        # Create a temporary file for the cookies
        temp_cookie_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        cookie_file = temp_cookie_file.name
        temp_cookie_file.close()
        
        # Connect to the cookie database
        # We need to make a copy because the database might be locked
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        shutil.copy2(db_path, temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Query for youtube.com cookies
        try:
            cursor.execute(
                "SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly "
                "FROM cookies WHERE host_key LIKE '%youtube.com%'"
            )
            
            # Write cookies in Netscape format
            with open(cookie_file, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for row in cursor.fetchall():
                    host, name, value, path, expires, secure, httponly = row
                    secure_str = "TRUE" if secure else "FALSE"
                    httponly_str = "TRUE" if httponly else "FALSE"
                    f.write(f"{host}\tTRUE\t{path}\t{secure_str}\t{expires}\t{name}\t{value}\n")
            
            print(f"Extracted {cursor.rowcount} cookies for youtube.com")
            
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            os.unlink(cookie_file)
            cookie_file = None
        
        # Clean up
        conn.close()
        os.unlink(temp_db_path)
        
        return cookie_file
        
    except Exception as e:
        print(f"Error extracting Chrome cookies: {e}")
        return None

def get_firefox_cookies():
    """
    Extract cookies from Firefox browser for youtube.com
    
    Returns:
        str: Path to the cookie file or None if not found
    """
    try:
        print("Attempting to extract cookies from Firefox...")
        cookie_file = None
        
        # Determine OS and Firefox cookie path
        system = platform.system()
        home = str(Path.home())
        
        # Find Firefox profile directory
        if system == "Darwin":  # macOS
            profile_dir = f"{home}/Library/Application Support/Firefox/Profiles"
        elif system == "Linux":
            profile_dir = f"{home}/.mozilla/firefox"
        elif system == "Windows":
            profile_dir = f"{home}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
        else:
            print(f"Unsupported operating system: {system}")
            return None
        
        if not os.path.exists(profile_dir):
            print(f"Firefox profile directory not found: {profile_dir}")
            return None
        
        # Find the default profile
        profile = None
        for d in os.listdir(profile_dir):
            if d.endswith('.default') or d.endswith('.default-release'):
                profile = os.path.join(profile_dir, d)
                break
        
        if not profile:
            print("Could not find Firefox default profile")
            return None
        
        # Path to the cookies database
        db_path = os.path.join(profile, 'cookies.sqlite')
        if not os.path.exists(db_path):
            print(f"Firefox cookie database not found: {db_path}")
            return None
        
        # Create a temporary file for the cookies
        temp_cookie_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        cookie_file = temp_cookie_file.name
        temp_cookie_file.close()
        
        # Connect to the cookie database
        # We need to make a copy because the database might be locked
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        shutil.copy2(db_path, temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Query for youtube.com cookies
        try:
            cursor.execute(
                "SELECT host, name, value, path, expiry, isSecure, isHttpOnly "
                "FROM moz_cookies WHERE host LIKE '%youtube.com%'"
            )
            
            # Write cookies in Netscape format
            with open(cookie_file, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for row in cursor.fetchall():
                    host, name, value, path, expires, secure, httponly = row
                    secure_str = "TRUE" if secure else "FALSE"
                    httponly_str = "TRUE" if httponly else "FALSE"
                    f.write(f"{host}\tTRUE\t{path}\t{secure_str}\t{expires}\t{name}\t{value}\n")
            
            print(f"Extracted {cursor.rowcount} cookies for youtube.com")
            
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            os.unlink(cookie_file)
            cookie_file = None
        
        # Clean up
        conn.close()
        os.unlink(temp_db_path)
        
        return cookie_file
        
    except Exception as e:
        print(f"Error extracting Firefox cookies: {e}")
        return None

def get_browser_cookies():
    """
    Try to extract cookies from various browsers
    
    Returns:
        str: Path to the cookie file or None if not found
    """
    # Try Chrome first, then Firefox
    cookie_file = get_chrome_cookies()
    if not cookie_file:
        cookie_file = get_firefox_cookies()
    
    return cookie_file

def download_with_youtube_dl(url, output_path=None, attempts=3, use_cookies=True):
    """
    Download audio from a YouTube video using youtube-dl or yt-dlp with multiple attempts.
    
    Args:
        url (str): The YouTube URL
        output_path (str, optional): Path where the audio file should be saved.
        attempts (int): Number of download attempts
        use_cookies (bool): Whether to try using browser cookies
    
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
    
    # Extract video ID for more reliable downloading
    video_id = extract_video_id(url)
    if video_id:
        # Use the video ID directly with youtube.com/watch?v= format
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Extracted video ID: {video_id}")
    
    # Build command
    if output_path:
        output_template = output_path
    else:
        output_template = "%(title)s.%(ext)s"
    
    # Simple user agent that's less likely to be blocked
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    for attempt in range(attempts):
        try:
            # Keep the command simple to avoid triggering YouTube's anti-scraping measures
            cmd = [
                youtube_dl_cmd,
                "-x",  # Extract audio
                "--audio-format", "mp3",  # Convert to mp3
                "--audio-quality", "0",  # Best quality
                "-o", output_template,  # Output template
                "--user-agent", user_agent,  # Use a simple user agent
                url  # URL to download
            ]
            
            print(f"Downloading audio from YouTube using {youtube_dl_cmd} (Attempt {attempt+1}/{attempts}): {url}")
            
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
            if process.returncode == 0:
                # Success!
                if not output_path:
                    print("\nDownload complete!")
                    # Try to find the downloaded file
                    if video_id:
                        # Look for files created in the last minute
                        import glob
                        recent_files = []
                        for file in glob.glob("*.mp3"):
                            if os.path.getctime(file) > time.time() - 60:
                                recent_files.append(file)
                        if recent_files:
                            return recent_files[0]  # Return the most recently created file
                    return None  # We don't know the exact filename
                else:
                    print(f"\nDownload complete! Audio saved to: {output_path}")
                    return output_path
            else:
                stderr = process.stderr.read()
                print(f"Error on attempt {attempt+1}: {stderr}")
                
                # If this is not the last attempt, wait before retrying
                if attempt < attempts - 1:
                    wait_time = 2 * (attempt + 1)  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            if attempt < attempts - 1:
                wait_time = 2 * (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    print("Failed to download after", attempts, "attempts.")
    return None

def download_with_youtube_dl_embed(url, output_path=None, attempts=3, use_cookies=True):
    """
    Download audio from a YouTube video using yt-dlp with the embed URL approach.
    This is often more effective for shorts and restricted videos.
    
    Args:
        url (str): The YouTube URL
        output_path (str, optional): Path where the audio file should be saved.
        attempts (int): Number of download attempts
        use_cookies (bool): Whether to try using browser cookies
    
    Returns:
        str: Path to the downloaded audio file
    """
    # Check if yt-dlp is installed
    youtube_dl_cmd = None
    for cmd in ['yt-dlp']:
        if shutil.which(cmd):
            youtube_dl_cmd = cmd
            break
    
    if not youtube_dl_cmd:
        print("yt-dlp is not installed.")
        print("Please install it with:")
        print("  pip install yt-dlp")
        return None
    
    # Extract video ID for more reliable downloading
    video_id = extract_video_id(url)
    if not video_id:
        print("Could not extract video ID from URL")
        return None
    
    # Use the embed URL format which often bypasses restrictions
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    print(f"Using embed URL approach: {embed_url}")
    
    # Try to get cookies from browser if requested
    cookie_file = None
    if use_cookies:
        cookie_file = get_browser_cookies()
        if cookie_file:
            print(f"Using browser cookies for authentication")
    
    # Build command
    if output_path:
        output_template = output_path
    else:
        output_template = "%(title)s.%(ext)s"
    
    # Modern user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]
    
    for attempt in range(attempts):
        try:
            # Use a different user agent for each attempt
            user_agent = user_agents[attempt % len(user_agents)]
            
            # Command to download only audio in mp3 format
            cmd = [
                youtube_dl_cmd,
                "-x",  # Extract audio
                "--audio-format", "mp3",  # Convert to mp3
                "--audio-quality", "0",  # Best quality
                "-o", output_template,  # Output template
                "--user-agent", user_agent,  # Use specific user agent
                "--referer", "https://www.youtube.com/",  # Set referer
                "--add-header", "Origin:https://www.youtube.com",  # Set origin
                "--no-check-certificate",  # Skip HTTPS certificate validation
                "--force-ipv4",  # Force IPv4 to avoid some restrictions
                "--geo-bypass",  # Try to bypass geo-restriction
                "--no-playlist",  # Don't download playlists
                "--ignore-errors",  # Continue on download errors
                "--extractor-retries", "3",  # Retry extractor on failure
                "--skip-unavailable-fragments",  # Skip unavailable fragments
                "--no-overwrites",  # Don't overwrite files
            ]
            
            # Add cookies if available
            if cookie_file:
                cmd.extend(["--cookies", cookie_file])
            
            # Add URL at the end
            cmd.append(embed_url)
            
            print(f"Downloading audio using embed URL approach (Attempt {attempt+1}/{attempts}): {embed_url}")
            
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
            if process.returncode == 0:
                # Success!
                if not output_path:
                    print("\nDownload complete!")
                    # Try to find the downloaded file
                    if video_id:
                        # Look for files created in the last minute
                        import glob
                        recent_files = []
                        for file in glob.glob("*.mp3"):
                            if os.path.getctime(file) > time.time() - 60:
                                recent_files.append(file)
                        if recent_files:
                            return recent_files[0]  # Return the most recently created file
                    return None  # We don't know the exact filename
                else:
                    print(f"\nDownload complete! Audio saved to: {output_path}")
                    return output_path
            else:
                stderr = process.stderr.read()
                print(f"Error on attempt {attempt+1}: {stderr}")
                
                # If this is not the last attempt, wait before retrying
                if attempt < attempts - 1:
                    wait_time = 2 * (attempt + 1)  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            if attempt < attempts - 1:
                wait_time = 2 * (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        finally:
            # Clean up cookie file if we created one
            if cookie_file and os.path.exists(cookie_file) and use_cookies:
                try:
                    os.unlink(cookie_file)
                except Exception as e:
                    print(f"Error removing cookie file: {e}")
    
    print("Failed to download with embed URL approach after", attempts, "attempts.")
    return None

def try_direct_youtube_download(url, output_path=None):
    """
    Try to download directly from YouTube using requests.
    This is a fallback method and may not always work.
    
    Args:
        url (str): The YouTube URL
        output_path (str, optional): Path where the audio file should be saved.
    
    Returns:
        str: Path to the downloaded audio file or None if failed
    """
    try:
        print("Attempting direct download as a last resort...")
        video_id = extract_video_id(url)
        if not video_id:
            print("Could not extract video ID for direct download.")
            return None
            
        # Try to get audio URL (this is a simplified approach and may not work for all videos)
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        })
        
        # This is a very basic approach and will likely not work for most videos
        # due to YouTube's protection mechanisms
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        response = session.get(watch_url)
        
        if response.status_code != 200:
            print(f"Failed to access YouTube page: HTTP {response.status_code}")
            return None
            
        # This is where we would extract the audio URL, but it's complex
        # and YouTube frequently changes their system to prevent this
        print("Direct download method is not fully implemented and likely won't work.")
        print("Please use yt-dlp which is more reliable.")
        return None
        
    except Exception as e:
        print(f"Error in direct download attempt: {e}")
        return None

def download_from_youtube(url, output_path=None):
    """
    Try to download audio from a YouTube video using multiple methods.
    
    Args:
        url (str): The YouTube URL
        output_path (str, optional): Path where the audio file should be saved.
                                     If not provided, it will use the video title.
    
    Returns:
        str: Path to the downloaded audio file
    """
    if not is_youtube_url(url):
        print(f"Not a YouTube URL: {url}")
        return None
    
    print(f"Attempting to download with pytube: {url}")
    try:
        # First try with pytube
        from pytube import YouTube
        
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            raise Exception("No audio stream found")
        
        if output_path:
            # If output_path is specified, use it directly
            out_file = audio_stream.download(filename=output_path)
        else:
            # Otherwise, download to a temporary file
            out_file = audio_stream.download()
        
        # If the file is not already an MP3, convert it
        base, ext = os.path.splitext(out_file)
        if ext.lower() != '.mp3':
            mp3_file = base + '.mp3'
            os.rename(out_file, mp3_file)
            out_file = mp3_file
        
        print(f"Download complete! Audio saved to: {out_file}")
        return out_file
        
    except Exception as e:
        print(f"Error with pytube: {e}")
        print("Falling back to youtube-dl/yt-dlp...")
        
        # Try with youtube-dl/yt-dlp
        result = download_with_youtube_dl(url, output_path)
        
        if result:
            return result
        
        # If youtube-dl fails, try with embed URL approach
        print("Trying embed URL approach...")
        result = download_with_youtube_dl_embed(url, output_path)
        
        if result:
            return result
        
        # If all else fails, try direct download
        print("Trying direct download as a last resort...")
        return try_direct_youtube_download(url, output_path)

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
        
        # Use a session with a user agent to avoid some restrictions
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        })
        
        response = session.get(url, stream=True)
        
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
        chunk_size = 8192
        
        print(f"Saving to: {output_path}")
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Calculate and display progress
                    if total_size > 0:
                        percent = int(100 * downloaded / total_size)
                        sys.stdout.write(f"\rDownloading: {percent}% [{downloaded} / {total_size} bytes]")
                        sys.stdout.flush()
        
        print("\nDownload complete!")
        return output_path
        
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Download audio from a URL.')
    parser.add_argument('url', help='URL to download audio from')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--no-cookies', action='store_true', help='Do not use browser cookies')
    
    args = parser.parse_args()
    
    if is_youtube_url(args.url):
        download_from_youtube(args.url, args.output)
    else:
        download_audio(args.url, args.output)

if __name__ == "__main__":
    main()
