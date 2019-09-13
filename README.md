# Music File Editor
My own Music File editor made in python that can automatically set metadata and album cover given the filename.

# Features
- Metadata setter (auto, manual)
- Album art setter (auto [needs spotify API key], manual)
- Trimming options
- View album art

# How to use
- pip install -r requirements.txt
- Have ffmpeg installed to PATH.
- Run main.py is for a command line interface (GUI for later)
- All the useful functions are in functions.py (if you want to do everything with code)
- Make sure to create a config.json file to store your API keys and music directory. Will turn into .env later.
- For the album cover feature, you need to have your own Spotify API.

# Note
This has been untested on Linux and Mac.

# config.json format

{
    "MUSIC_LOCATION": "path/no quotation marks/music directory",
    "SPOTIFY_CLIENT_ID": "your_client_id",
    "SPOTIFY_SECRET": "your_secret",
    "LASTFM_API": "not_needed",
    "LASTFM_SECRET": "not_needed"
}
