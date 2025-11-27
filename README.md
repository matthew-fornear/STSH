# STSH

Spotify-to-MP3 downloader. Exports Spotify playlists to MP3.

## Prerequisites

- Python 3 (conda recommended)
- `yt-dlp`: `pip install yt-dlp`
- FFmpeg (for audio conversion)

## Usage

1. Export playlist: https://exportify.net → download CSV
2. Place CSV(s) in `playlists/` directory
3. Run: `main.py`
4. Output: `my_music/` directory with MP3s (320kbps)

Script processes all CSV files in `playlists/` in alphabetical order.

## Configuration

Edit `main.py`:
- `playlists_dir`: Directory containing CSV files (default: `playlists`)
- `output_dir`: Output directory (default: `my_music`)

