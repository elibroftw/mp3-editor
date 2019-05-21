# MP3 Editor
My own mp3 editor made in python that can automatically set metadata and album cover given the filename. For the album cover feature, you need to have your own Spotify API. I may or may not add Oauth.


# How to use
`pip install -r requirements.txt`
main.py is a command line interface.
All the useful functions are in functions.py (if you want to do everything with code)
Make sure to create a config.txt file to store your API keys and music directory.

Format of config.txt:

MUSIC_LOCATION = path/no quotation marks/music directory

SPOTIFY_CLIENT_ID = your_client_id

SPOTIFY_SECRET = your_secret

LASTFM_API = not_needed

LASTFM_SECRET = not_needed
