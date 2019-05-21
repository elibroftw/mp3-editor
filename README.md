# MP3 Editor
My own mp3 editor made in python that can automatically set metadata and album cover given the filename. 


# How to use
- pip install -r requirements.txt
- Have ffmpeg installed to PATH.
- Run main.py is for a command line interface (GUI for later)
- All the useful functions are in functions.py (if you want to do everything with code)
- Make sure to create a config.txt file to store your API keys and music directory. Will turn into .env later.
- For the album cover feature, you need to have your own Spotify API.

# Note
This has been untested on Linux and Mac.

# config.txt format

MUSIC_LOCATION = path/no quotation marks/music directory

SPOTIFY_CLIENT_ID = your_client_id

SPOTIFY_SECRET = your_secret

LASTFM_API = not_needed

LASTFM_SECRET = not_needed
