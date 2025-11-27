#!/usr/bin/env python
import csv
import os
import glob
import time
import requests
from datetime import datetime
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC

def check_if_exists(track_name, artist_name, output_dir):
    """Check if a track already exists in output directory."""
    if not os.path.exists(output_dir):
        return False
    
    # Get all MP3 files in output directory
    existing_files = glob.glob(os.path.join(output_dir, "*.mp3"))
    
    # Normalize track and artist names for comparison
    track_lower = track_name.lower()
    artist_lower = artist_name.lower()
    
    for file_path in existing_files:
        filename = os.path.basename(file_path).lower()
        # Check if both track name and artist name appear in filename
        if track_lower in filename and artist_lower in filename:
            return True
    
    return False

def download_album_art(image_url, temp_dir='temp_art'):
    """Download album art image."""
    if not image_url:
        return None
    
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            # Determine file extension from URL or content type
            ext = 'jpg'
            if 'png' in image_url.lower() or 'image/png' in response.headers.get('content-type', ''):
                ext = 'png'
            
            art_path = os.path.join(temp_dir, f"art_{int(time.time())}.{ext}")
            with open(art_path, 'wb') as f:
                f.write(response.content)
            return art_path
    except Exception as e:
        print(f"  Warning: Could not download album art: {e}")
    
    return None

def tag_mp3(file_path, track_name, artist_name, album_name, release_date, album_art_path=None):
    """Add metadata tags to MP3 file."""
    try:
        audio = MP3(file_path, ID3=ID3)
        
        # Add ID3 tags if they don't exist
        if audio.tags is None:
            audio.add_tags()
        
        # Set metadata
        audio.tags.add(TIT2(encoding=3, text=track_name))
        audio.tags.add(TPE1(encoding=3, text=artist_name))
        if album_name:
            audio.tags.add(TALB(encoding=3, text=album_name))
        if release_date:
            year = release_date.split('-')[0] if release_date else None
            if year and year.isdigit():
                audio.tags.add(TDRC(encoding=3, text=year))
        
        # Add album art
        if album_art_path and os.path.exists(album_art_path):
            with open(album_art_path, 'rb') as f:
                art_data = f.read()
                mime_type = 'image/jpeg' if album_art_path.endswith('.jpg') else 'image/png'
                audio.tags.add(APIC(
                    encoding=3,
                    mime=mime_type,
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=art_data
                ))
        
        audio.save()
        return True
    except Exception as e:
        print(f"  Warning: Could not tag MP3: {e}")
        return False

def find_newest_mp3(output_dir, before_time):
    """Find the most recently created MP3 file after a given time."""
    mp3_files = glob.glob(os.path.join(output_dir, "*.mp3"))
    newest_file = None
    newest_time = before_time
    
    for file_path in mp3_files:
        mtime = os.path.getmtime(file_path)
        if mtime > newest_time:
            newest_time = mtime
            newest_file = file_path
    
    return newest_file if newest_time > before_time else None

def download_songs_from_csv(csv_file, output_dir='downloads', log_file=None):
    """
    Download songs from a Spotify CSV export via YouTube.
    
    Args:
        csv_file: Path to the CSV file with Spotify track data
        output_dir: Directory to save downloaded MP3s
        log_file: File handle for logging
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # yt-dlp options for best audio quality
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }
    
    # Read CSV and download each track
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            track_name = row.get('Track Name', '').strip()
            artist_name = row.get('Artist Name(s)', '').strip()
            album_name = row.get('Album Name', '').strip()
            
            if not track_name or not artist_name:
                msg = f"Skipping row {i}: Missing track or artist name"
                print(msg)
                if log_file:
                    log_file.write(f"{datetime.now().isoformat()} - {msg}\n")
                continue
            
            # Check if already downloaded
            if check_if_exists(track_name, artist_name, output_dir):
                msg = f"[{i}] Already exists: {track_name} - {artist_name}"
                print(f"\n{msg}")
                if log_file:
                    log_file.write(f"{datetime.now().isoformat()} - {msg}\n")
                continue
            
            # Get metadata from CSV
            album_image_url = row.get('Album Image URL', '').strip()
            release_date = row.get('Album Release Date', '').strip() or row.get('Release Date', '').strip()
            
            # Create search query
            search_query = f"{track_name} {artist_name} audio"
            print(f"\n[{i}] Searching: {track_name} - {artist_name}")
            
            # Record time before download to find new file
            before_time = time.time()
            
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    # Search YouTube and download first result
                    ydl.download([f"ytsearch1:{search_query}"])
                
                # Find the newly downloaded file
                downloaded_file = find_newest_mp3(output_dir, before_time)
                
                if downloaded_file:
                    # Download album art
                    album_art_path = None
                    if album_image_url:
                        print(f"  Downloading album art...")
                        album_art_path = download_album_art(album_image_url)
                    
                    # Tag the MP3 file
                    print(f"  Adding metadata tags...")
                    tag_mp3(downloaded_file, track_name, artist_name, album_name, release_date, album_art_path)
                    
                    # Clean up temporary album art
                    if album_art_path and os.path.exists(album_art_path):
                        try:
                            os.remove(album_art_path)
                        except:
                            pass
                    
                    msg = f"✓ Downloaded and tagged: {track_name} - {artist_name}"
                else:
                    msg = f"✓ Downloaded: {track_name} - {artist_name} (tagging skipped)"
                
                print(msg)
                if log_file:
                    log_file.write(f"{datetime.now().isoformat()} - {msg}\n")
                
            except Exception as e:
                msg = f"✗ Error downloading {track_name} - {artist_name}: {str(e)}"
                print(msg)
                if log_file:
                    log_file.write(f"{datetime.now().isoformat()} - {msg}\n")
                continue
    
    print(f"\n✓ Download complete! Files saved to: {output_dir}")

if __name__ == "__main__":
    playlists_dir = "playlists"
    output_dir = "my_music"
    log_dir = "log"
    
    # Create log directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log file with timestamp
    log_filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    # Find all CSV files in playlists directory
    csv_files = sorted(glob.glob(os.path.join(playlists_dir, "*.csv")))
    
    if not csv_files:
        print(f"No CSV files found in {playlists_dir}/")
        exit(1)
    
    print(f"Found {len(csv_files)} CSV file(s) to process")
    print(f"Log file: {log_path}\n")
    
    # Process each CSV in order
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Download session started: {datetime.now().isoformat()}\n")
        log_file.write(f"Output directory: {output_dir}\n")
        log_file.write(f"CSV files to process: {len(csv_files)}\n")
        log_file.write("-" * 60 + "\n\n")
        
        for csv_file in csv_files:
            playlist_name = os.path.basename(csv_file)
            print(f"{'='*60}")
            print(f"Processing: {playlist_name}")
            print(f"{'='*60}\n")
            
            log_file.write(f"\nProcessing playlist: {playlist_name}\n")
            log_file.write("-" * 60 + "\n")
            
            download_songs_from_csv(csv_file, output_dir, log_file)
        
        log_file.write(f"\n{'='*60}\n")
        log_file.write(f"Download session completed: {datetime.now().isoformat()}\n")
    
    print(f"\n{'='*60}")
    print("All playlists processed!")
    print(f"Log saved to: {log_path}")
    print(f"{'='*60}")