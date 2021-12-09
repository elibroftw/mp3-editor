# Music File Editor
A command line music file editor that can automatically set metadata and album cover given the filename. It can also remove silence or trim music files in length if ffmpeg is installed.
- No longer maintained as the most important feature is the trimming and silence removal
- For metadata editing and album art setting (all audio types), see [Music Caster](https://github.com/elibroftw/music-caster/)
- If only metadata is required, you can use the [online version](http://elijahlopez.herokuapp.com/metadata-setter/)

# Features
- Metadata setter (auto, manual)
- Album cover setter (auto [needs spotify API key], manual)
- Trimming options
- View album covers

# Note
- If an album art was expected to be found but was not, email me

# How to use
- `pip install -r requirements.txt --user`
- Have ffmpeg installed and available in PATH.
- Run main.py is for a command line interface (GUI for later)
- All the useful functions are in functions.py (if you want to do everything with code)
- Make sure to create a config.json file to store your API keys and music directory. Will turn into .env later.
- For the album cover feature, you need to have your own Spotify API.

# Note
This has not been tested on Linux and Mac.
This program assumes that a audio file onyl requires at most one album cover.
Optimize covers converts PNG images to JPEG.

# config.json format
```json
{
    "MUSIC_FOLDERS": ["paths/no quotation marks/music directory"],
    "SPOTIFY_CLIENT_ID": "your_client_id",
    "SPOTIFY_SECRET": "your_secret",
    "LASTFM_API": "OPTIONAL",
    "LASTFM_SECRET": "OPTIONAL"
}
```
