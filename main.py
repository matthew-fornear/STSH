#!/usr/bin/env python
import csv
import os
import glob
from yt_dlp import YoutubeDL

def download_songs_from_csv(csv_file, output_dir='downloads'):
    """
    Download songs from a Spotify CSV export via YouTube.
    
    Args:
        csv_file: Path to the CSV file with Spotify track data
        output_dir: Directory to save downloaded MP3s
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
                print(f"Skipping row {i}: Missing track or artist name")
                continue
            
            # Create search query
            search_query = f"{track_name} {artist_name} audio"
            print(f"\n[{i}] Searching: {track_name} - {artist_name}")
            
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    # Search YouTube and download first result
                    ydl.download([f"ytsearch1:{search_query}"])
                print(f"✓ Downloaded: {track_name}")
                
            except Exception as e:
                print(f"✗ Error downloading {track_name}: {str(e)}")
                continue
    
    print(f"\n✓ Download complete! Files saved to: {output_dir}")

if __name__ == "__main__":
    playlists_dir = "playlists"
    output_dir = "my_music"
    
    # Find all CSV files in playlists directory
    csv_files = sorted(glob.glob(os.path.join(playlists_dir, "*.csv")))
    
    if not csv_files:
        print(f"No CSV files found in {playlists_dir}/")
        exit(1)
    
    print(f"Found {len(csv_files)} CSV file(s) to process\n")
    
    # Process each CSV in order
    for csv_file in csv_files:
        playlist_name = os.path.basename(csv_file)
        print(f"{'='*60}")
        print(f"Processing: {playlist_name}")
        print(f"{'='*60}\n")
        download_songs_from_csv(csv_file, output_dir)
    
    print(f"\n{'='*60}")
    print("All playlists processed!")
    print(f"{'='*60}")