from pprint import pprint
from time import time
import base64
from glob import glob
import io
import os
from os import system
import subprocess
from urllib import parse
from urllib.request import urlopen

try:   
    import json
    import shlex
    import platform
    import pathlib
    from mutagen import File
    from mutagen.easyid3 import EasyID3
    import mutagen.id3
    from mutagen.id3 import Encoding
    from mutagen.mp3 import MP3
    from PIL import Image
    import requests
except ImportError as e:
    print(e)
    print('Press Enter to quit...')
    quit()

# TODO: Add ffmpeg binary to the repo
p = subprocess.Popen('ffmpeg', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = p.communicate()
ar = b"'ffmpeg' is not recognized as an internal or external command,\r\noperable program or batch file.\r\n"
if ar == err:
    print('FFMPEG NOT ON PATH')
    input('Press enter to go to FFMPEG website and how to add to path...')
    import webbrowser
    webbrowser.open('https://ffmpeg.org/download.html')
    webbrowser.open('http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/')
    quit()

# this dictionary store the api keys
config = {}
spotify_access_token_creation = 0
spotify_access_token = ''
# TODO: don't change album cover if its already the album cover


def copy(text):
    if platform.system() == 'Windows':
        command = f'echo|set/p={text}|clip'
        system(command)
        return True
    return False


def get_spotify_access_token():
    global spotify_access_token, spotify_access_token_creation
    if time() - spotify_access_token_creation > 21600:
        spotify_access_token_creation = time()
        header = {'Authorization': 'Basic ' + SPOTIFY_B64_AUTH_STR}
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
        spotify_access_token = access_token_response.json()['access_token']
    return spotify_access_token


try:
    with open('config.json') as json_file:
        config: dict = json.load(json_file)

    SPOTIFY_AUTH_STR = f"{config['SPOTIFY_CLIENT_ID']}:{config['SPOTIFY_SECRET']}"
    SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()

    LASTFM_API = config['LASTFM_API']
    LASTFM_SECRET = config['LASTFM_SECRET']

    # this is for future when I get a Soundcloud api key
    # SOUNDCLOUD_CLIENT_ID = config['SOUNDCLOUD_CLIENT_ID']
    # SOUNDCLOUD_CLIENT_SECRET = config['SOUNDCLOUD_CLIENT_SECRET']
except (FileNotFoundError, KeyError):
    print('Limited functionality')


def set_title(audio: EasyID3, title: str):
    """
    Sets a title for an EasyID3 object
    :param audio: EasyID3 Object
    :param title: string
    """
    audio['title'] = title
    audio.save()


def set_artist(audio: EasyID3, artist):
    """
    Sets an artist for an EasyID3 object
    :param audio: EasyID3
    :param artist: string or list[str] of the artist or artists
    """
    audio['artist'] = artist
    audio.save()


def set_album(audio: EasyID3, album):
    """
    Sets an album for an EasyID3 object
    :param audio: EasyID3
    :param album: string name of the album
    """
    audio['album'] = album
    audio.save()


def set_album_artist(audio: EasyID3, album_artist):
    """
    Sets an album artist for an EasyID3 object
    :param audio: EasyID3
    :param album_artist: name of the album artist
    """
    audio['albumartist'] = album_artist
    audio.save()


def get_artist(filename):
    """
    Extraction of artist name(s) from filename
    Different ways to name a file
    Lots of these are just-in-case situations
    The standard for naming multiple artists is comma separated values with a space after each comma
    Eg. filename = "artist_1, artist_2, artist_3 - title.mp3"
    """

    artist = filename[:filename.index(' -')]

    if artist.count(' , '): artist.split(' , ')
    elif artist.count(', '): artist = artist.split(', ')
    elif artist.count(','): artist = artist.split(',')

    if artist.count(' vs. '): artist = artist.split(' vs. ')
    elif artist.count(' vs '): artist = artist.split(' vs ')
    elif artist.count(' vs.'): artist = artist.split(' vs.')
    elif artist.count(' vs'): artist = artist.split(' vs')

    # Cannot split on & because "Dimitri Vegas & Like Mike" is considered as one artist

    if artist.count(' and '): artist = artist.split(' and ')
    elif artist.count(' and'): artist = artist.split(' and')

    if artist.count(' ft '): artist = artist.split(' ft ')
    elif artist.count(' ft. '): artist = artist.split(' ft. ')
    elif artist.count(' ft.'): artist = artist.split(' ft.')
    elif artist.count(' ft'): artist.split(' ft')

    if artist.count(' feat '): artist = artist.split(' feat ')
    elif artist.count(' feat. '): artist = artist.split(' feat. ')
    elif artist.count(' feat.'): artist = artist.split(' feat.')
    elif artist.count(' feat'): artist = artist.split(' feat')

    return artist


def add_simple_meta(file_path, artist='', title='', album='', albumartist='', override=False):
    """
    Automatically sets the metadata for a music file
    :param file_path: the path to the music file
    :param artist: given artist name
    :param title: given title name
    :param album: given album name
    :param albumartist: given album artist
    :param override: if True, all of the metadata is overridden
    :return: True or False depending on whether audio file was changed or not
    """
    audio = EasyID3(file_path)
    filename = pathlib.Path(file_path).name  # or filename = file_path[:-4]
    try:
        if (not override and audio.get('title') and audio.get('artist')
            and audio.get('albumartist') and has_album_art(file_path)): return False
        if artist == '': artist = get_artist(filename)
        else:
            if artist.count(' , '): artist.split(' , ')
            elif artist.count(', '): artist = artist.split(', ')
            elif artist.count(','): artist = artist.split(',')
        if title == '': title = filename[filename.index('-') + 2:-4]
        if override:
            audio['title'] = title
            audio['artist'] = artist
            if album != '': audio['album'] = album
            if albumartist != '': audio['albumartist'] = albumartist
        else:
            if 'album' not in audio:
                if album == '': audio['album'] = title
                else: audio['album'] = album
            if 'title' not in audio: audio['title'] = title
            if 'artist' not in audio: audio['artist'] = artist
            if 'albumartist' not in audio:
                if albumartist == '': audio['albumartist'] = artist
                else: audio['albumartist'] = albumartist
        audio.save()
        if not has_album_art(file_path): set_album_cover(file_path)
        return True
    except ValueError:
        print('Error with', filename)
        return False


set_simple_meta = add_simple_meta


def has_album_art(file_path) -> bool:
    """
    Checks if the file at file_path has an album coover
    :param file_path: the path to the music file
    :return: boolean expressing whether the file contains album art
    """
    audio: File = File(file_path)
    try:
        if 'APIC:' in audio:
            apic: mutagen.id3.APIC = audio['APIC:']
            if apic.encoding != Encoding.LATIN1:
                apic.encoding = Encoding.LATIN1
                audio['APIC:'] = apic
                audio.save()
            return True
        return False
    except KeyError:
        audio.add_tags()


has_mp3_cover = has_album_cover = has_album_art


def get_album_art(artist, title, select_index=0, return_all=False):
    """
    Fetches max resolution album art(s) for track (artist and title specified) using Spotify API
    :param artist: artist
    :param title: title of track
    :param select_index: which result to pick (by default the first)
    :param return_all: if set to True, function returns all max res album art
    :return: url(s) of the highest resolution album art for the track
    """
    # TODO: add soundcloud search as well if spotify comes up with no results.
    #  Soundcloud has it disabled
    artist, title = parse.quote_plus(artist), parse.quote_plus(title)
    header = {'Authorization': 'Bearer ' + get_spotify_access_token()}
    r = requests.get(f'https://api.spotify.com/v1/search?q={title}+artist:{artist}&type=track', headers=header)
    if return_all: return [item['album']['images'][0]['url'] for item in r.json()['tracks']['items']]
    return r.json()['tracks']['items'][select_index]['album']['images'][0]['url']


def set_album_cover(mp3_path, img_path='', url='', copy_from='', title='', artist='', select_index=0):
    audio = MP3(mp3_path, ID3=mutagen.id3.ID3)
    filename = pathlib.Path(mp3_path).name
    try:
        audio.add_tags()
    except mutagen.id3.error:
        pass
    if title and artist:
        try:
            img_path = get_album_art(artist, title)
            image_data = urlopen(img_path).read()
        except (KeyError, ValueError, IndexError):
            print(f'Album art not found for: {filename}')
            return False
    elif img_path:
        with open(img_path, 'rb') as bits:  # better than open(albumart, 'rb').read() ?
            image_data = bits.read()
    elif url:
        img_path = url = url.replace(' ', '')
        image_data = urlopen(url).read()
    elif copy_from:
        other_audio = MP3(copy_from, ID3=mutagen.id3.ID3)
        try:
            audio['APIC:'] = other_audio['APIC:']
            audio.save()
        except KeyError:
            other_audio = other_audio.items()
            unchanged = True
            for k, v in other_audio:
                if k.startswith('APIC:'):
                    audio['APIC:'] = v
                    audio.save()
                    unchanged = False
            if unchanged: print('That file is incompatible.')
        return
    else:
        easy_audio = EasyID3(mp3_path)
        if 'title' in easy_audio and not title:
            title = easy_audio['title'][0]
        else:
            add_simple_meta(mp3_path)
            title = filename[filename.index('-') + 2:-4]
        if 'artist' in easy_audio and not artist:
            artist = easy_audio['artist'][0]
        else:
            add_simple_meta(mp3_path)
            artist = get_artist(filename)
        try:
            img_path = get_album_art(artist, title, select_index=select_index)
            image_data = urlopen(img_path).read()
        except (KeyError, ValueError, IndexError):
            print(f'Album art not found for: {filename}')
            return False

    if img_path.endswith('png'): mime = 'image/png'
    else: mime = 'image/jpeg'
    data = io.BytesIO(image_data)
    im = Image.open(data)
    image_data = io.BytesIO()
    im.save(image_data, optimize=True, format='JPEG')
    # image.desc = 'front cover'
    audio['APIC:'] = mutagen.id3.APIC(
        encoding=0,  # 3 is for utf-8
        mime=mime,  # image/jpeg or image/png
        type=3,  # 3 is for the cover image
        # desc=u'Album Cover',
        data=image_data.getvalue()
    )
    audio.save()


add_mp3_cover = add_album_cover = set_album_cover


# @memoize
def get_temp_path(filename):
    base = os.path.basename(filename)
    base = f'TEMP {base}'
    directory = os.path.dirname(filename)
    temp_path = directory + '/' + base
    # os.rename(filename, temp_path)
    return temp_path


def ffmpeg_helper(filename, command):
    audio = EasyID3(filename)
    artists = audio['artist']
    title = audio['title']
    album = audio['album']
    album_artist = audio['albumartist']
    album_cover = MP3(filename, ID3=mutagen.id3.ID3)['APIC:']
    temp_path = get_temp_path(filename)
    os.rename(filename, temp_path)
    os.system(command)
    audio = EasyID3(filename)
    audio['artist'] = artists
    audio['title'] = title
    audio['album'] = album
    audio['albumartist'] = album_artist
    audio.save()
    audio = MP3(filename, ID3=mutagen.id3.ID3)
    audio['APIC:'] = album_cover
    audio.save()
    os.remove(temp_path)
    os.remove(os.path.dirname(filename) + '/ffmpeg.log')


def trim(filename, start: int, end: int):
    temp_path = get_temp_path(filename)
    command = f'ffmpeg -i "{temp_path}" -ss {start} -t {end} -c copy "{filename}" > ffmpeg.log 2>&1'
    ffmpeg_helper(filename, command)


def remove_silence(filename):
    temp_path = get_temp_path(filename)
    command = f'ffmpeg -i "{temp_path}" -af silenceremove=start_periods=1:stop_periods=1:detection=peak "{filename}" ' \
              f'> ffmpeg.log 2>&1'
    ffmpeg_helper(filename, command)


def set_genre(filename, genres=None):
    # requires last fm api
    if genres is None:
        easy_audio = EasyID3(filename)
        artist, title = easy_audio['artist'][0], easy_audio['title'][0]
        error_string = f'Genre not set for {artist} - {title}'
        artist, title = parse.quote_plus(artist), parse.quote_plus(title)
        url = f'https://ws.audioscrobbler.com/2.0/?method=track.getInfo&track={title}&artist={artist}&api_key={LASTFM_API}&format=json'
        r = requests.get(url)
        try: sample = r.json()['track']['toptags']['tag']
        except KeyError:
            print(error_string)
            return False
        genres = [tag['name'] for tag in sample][:3]
    audio = MP3(filename)
    audio['TCON'] = mutagen.id3.TCON(encoding=3, text=u';'.join(genres))  # genre key is TCON
    audio.save()
    return True


def get_genre(filename):
    audio = MP3(filename)
    return audio.get('TCON')


# audio[u"USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
def get_lyrics(filename):
    audio = MP3(filename)
    return audio.get(u"USLT::'eng'")


def remove_covers(filename):
    audio = MP3(filename)
    for key in audio.keys():
        if key.startswith('APIC'):
            audio.pop(key)
    audio.save()


def optimize_cover(filename):
    if has_album_art(filename):
        audio = MP3(filename)
        apic = audio['APIC:']
        data = apic.data
        data = io.BytesIO(data)
        im = Image.open(data)
        new_data = io.BytesIO()
        im.save(new_data, optimize=True, format='JPEG')
        if len(data.getvalue()) - len(new_data.getvalue()) > 0:
            audio['APIC:'] = mutagen.id3.APIC(
                encoding=0,  # 3 is for utf-8
                mime='image/jpeg',  # image/jpeg or image/png
                type=3,  # 3 is for the cover image
                # desc=u'Cover',
                data=new_data.getvalue()
            )
            audio.save()


if __name__ == '__main__':
    os.chdir(config['MUSIC_LOCATION'])
    for file in glob('*.mp3'):
        try: optimize_cover(file)
        except mutagen.MutagenError:
            pass
