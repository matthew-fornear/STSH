#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
import os

# Spotify API credentials - Get these from https://developer.spotify.com/dashboard
CLIENT_ID = 'your_client_id_here'
CLIENT_SECRET = 'your_client_secret_here'
REDIRECT_URI = 'http://localhost:8888/callback'

# Scopes needed to read user data
SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative'

def setup_spotify_client():
    """Initialize Spotify client with OAuth"""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))

def get_all_saved_tracks(sp):
    """Get all saved/liked tracks from user's library"""
    print("Fetching saved tracks...")
    tracks = []
    offset = 0
    limit = 50
    
    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        if not results['items']:
            break
            
        tracks.extend(results['items'])
        offset += limit
        print(f"  Fetched {len(tracks)} tracks so far...")
        
        if not results['next']:
            break
    
    print(f"✓ Total saved tracks: {len(tracks)}")
    return tracks

def get_all_playlists(sp):
    """Get all user's playlists"""
    print("\nFetching playlists...")
    playlists = []
    offset = 0
    limit = 50
    
    while True:
        results = sp.current_user_playlists(limit=limit, offset=offset)
        if not results['items']:
            break
            
        playlists.extend(results['items'])
        offset += limit
        
        if not results['next']:
            break
    
    print(f"✓ Found {len(playlists)} playlists")
    return playlists

def get_playlist_tracks(sp, playlist_id):
    """Get all tracks from a specific playlist"""
    tracks = []
    offset = 0
    limit = 100
    
    while True:
        results = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
        if not results['items']:
            break
            
        tracks.extend(results['items'])
        offset += limit
        
        if not results['next']:
            break
    
    return tracks

def track_to_csv_row(item, playlist_name='Liked Songs'):
    """Convert Spotify track object to CSV row"""
    track = item['track']
    
    # Handle missing data gracefully
    if not track:
        return None
    
    artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
    album = track.get('album', {})
    
    return {
        'Track URI': track.get('uri', ''),
        'Track Name': track.get('name', ''),
        'Artist URI(s)': ', '.join([artist['uri'] for artist in track.get('artists', [])]),
        'Artist Name(s)': artists,
        'Album URI': album.get('uri', ''),
        'Album Name': album.get('name', ''),
        'Album Artist URI(s)': ', '.join([artist['uri'] for artist in album.get('artists', [])]),
        'Album Artist Name(s)': ', '.join([artist['name'] for artist in album.get('artists', [])]),
        'Album Release Date': album.get('release_date', ''),
        'Album Image URL': album['images'][0]['url'] if album.get('images') else '',
        'Disc Number': track.get('disc_number', ''),
        'Track Number': track.get('track_number', ''),
        'Track Duration (ms)': track.get('duration_ms', ''),
        'Track Preview URL': track.get('preview_url', ''),
        'Explicit': track.get('explicit', False),
        'Popularity': track.get('popularity', ''),
        'ISRC': track.get('external_ids', {}).get('isrc', ''),
        'Added By': item.get('added_by', {}).get('id', ''),
        'Added At': item.get('added_at', ''),
        'Playlist Name': playlist_name
    }

def export_to_csv(tracks, filename):
    """Export tracks to CSV file"""
    if not tracks:
        print(f"No tracks to export for {filename}")
        return
    
    fieldnames = [
        'Track URI', 'Track Name', 'Artist URI(s)', 'Artist Name(s)',
        'Album URI', 'Album Name', 'Album Artist URI(s)', 'Album Artist Name(s)',
        'Album Release Date', 'Album Image URL', 'Disc Number', 'Track Number',
        'Track Duration (ms)', 'Track Preview URL', 'Explicit', 'Popularity',
        'ISRC', 'Added By', 'Added At', 'Playlist Name'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tracks)
    
    print(f"✓ Exported to {filename}")

def main():
    # Create output directory
    os.makedirs('playlists', exist_ok=True)
    
    # Setup Spotify client
    sp = setup_spotify_client()
    
    # Get user info
    user = sp.current_user()
    print(f"\n🎵 Logged in as: {user['display_name']}\n")
    
    # Export saved/liked tracks
    saved_tracks = get_all_saved_tracks(sp)
    csv_rows = [track_to_csv_row(item, 'Liked Songs') for item in saved_tracks]
    csv_rows = [row for row in csv_rows if row]  # Filter out None values
    export_to_csv(csv_rows, 'playlists/Liked_Songs.csv')
    
    # Export all playlists
    playlists = get_all_playlists(sp)
    
    for playlist in playlists:
        name = playlist['name']
        playlist_id = playlist['id']
        print(f"\nProcessing playlist: {name}")
        
        tracks = get_playlist_tracks(sp, playlist_id)
        csv_rows = [track_to_csv_row(item, name) for item in tracks]
        csv_rows = [row for row in csv_rows if row]
        
        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f'playlists/{safe_name}.csv'
        
        export_to_csv(csv_rows, filename)
    
    print("\n✓ All exports complete! Check the 'playlists' folder.")

if __name__ == "__main__":
    main()