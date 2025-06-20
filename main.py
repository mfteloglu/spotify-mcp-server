import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Initialize FastMCP server
mcp = FastMCP('spotify-mcp-server')

# Initialize Spotify client - move this inside the functions or make it global
def get_spotify_client():
    """Get authenticated Spotify client"""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="user-modify-playback-state user-read-playback-state user-library-modify user-library-read",
        cache_path=".spotify_cache"
    ))

@mcp.tool()
def spotify_play():
    """Start playback on the user's active device."""
    try:
        sp = get_spotify_client()
        # Check if there's an active device
        devices = sp.devices()
        if not devices['devices']:
            return 'error: No active devices found. Please open Spotify on a device first.'
        
        # Start playback
        sp.start_playback()
        return 'Playback started successfully'
    except spotipy.exceptions.SpotifyException as e:
        return f'Spotify error: {str(e)}'
    except Exception as e:
        return f'error: {str(e)}'

@mcp.tool()
def spotify_stop():
    """Stop playback on the user's active device."""
    try:
        sp = get_spotify_client()
        # Check if there's an active device
        devices = sp.devices()
        if not devices['devices']:
            return 'error: No active devices found. Please open Spotify on a device first.'
        
        # Pause playback
        sp.pause_playback()
        return 'Playback stopped successfully'  # Fixed: was returning 'started'
    except spotipy.exceptions.SpotifyException as e:
        return f'Spotify error: {str(e)}'
    except Exception as e:
        return f'error: {str(e)}'

@mcp.tool()
def spotify_current_track():
    """Get information about the currently playing track."""
    try:
        sp = get_spotify_client()
        current = sp.current_playback()
        if current and current['item']:
            track = current['item']
            return f"Currently playing: {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}"
        else:
            return "No track currently playing"
    except Exception as e:
        return f'error: {str(e)}'
    
@mcp.tool()
def spotify_like_current_track():
    """Add the currently playing track to your Liked Songs."""
    try:
        sp = get_spotify_client()
        current = sp.current_playback()
        if current and current['item']:
            track_id = current['item']['id']
            sp.current_user_saved_tracks_add([track_id])
            return f"Added '{current['item']['name']}' to your Liked Songs."
        else:
            return "No track currently playing."
    except spotipy.exceptions.SpotifyException as e:
        return f'Spotify error: {str(e)}'
    except Exception as e:
        return f'error: {str(e)}'
    
if __name__ == "__main__":
    print("Starting Spotify MCP Server...")
    print(f"Client ID configured: {'Yes' if SPOTIPY_CLIENT_ID else 'No'}")
    print(f"Client Secret configured: {'Yes' if SPOTIPY_CLIENT_SECRET else 'No'}")
    print(f"Redirect URI: {SPOTIPY_REDIRECT_URI}")
    
    # Run the MCP server
    mcp.run(transport='stdio')