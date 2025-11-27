# STSH

Spotify-to-MP3 downloader. Exports Spotify playlists to MP3.

## Prerequisites

- Python 3 (conda recommended)
- Install dependencies: `pip install -r requirements.txt`
- FFmpeg (for audio conversion)

## Usage

1. Export playlist: https://exportify.net → download CSV
2. Place CSV(s) in `playlists/` directory
3. Run: `main.py`
4. Output: `my_music/` directory with MP3s (320kbps) with full metadata tags
5. Logs: `log/` directory with timestamped log files

Script processes all CSV files in `playlists/` in alphabetical order. Automatically skips tracks already present in `my_music/`.

**Metadata:** MP3s are automatically tagged with title, artist, album, release year, and album art (if available in CSV).

## Configuration

Edit `main.py`:
- `playlists_dir`: Directory containing CSV files (default: `playlists`)
- `output_dir`: Output directory (default: `my_music`)