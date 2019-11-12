import base64
from contextlib import suppress
from glob import glob
import io
import json
import os
from os import system
from pprint import pprint
import subprocess
from time import time
from urllib import parse
from urllib.request import urlopen
import sys
import re


try:   
    import shlex
    import platform
    import pathlib
    from mutagen import File, MutagenError
    from mutagen.easyid3 import EasyID3
    import mutagen.id3
    from mutagen.id3 import Encoding
    from mutagen.mp3 import MP3
    from PIL import Image
    import requests
except ImportError as e:
    print(e)
    print('Press Enter to exit...')
    sys.exit()

# TODO: Add ffmpeg binary to the repo
# TODO: Support multiple folders
starting_dir = os.getcwd()
COUNTRY_CODES = ['MX', 'CA', 'US', 'UK', 'HK']
p = subprocess.Popen('ffmpeg', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = p.communicate()
ar = b"'ffmpeg' is not recognized as an internal or external command,\r\noperable program or batch file.\r\n"
if ar == err:
    print('FFMPEG NOT ON PATH')
    input('Press enter to go to FFMPEG website and learn how to add to path...')
    import webbrowser
    webbrowser.open('https://ffmpeg.org/download.html')
    webbrowser.open('http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/')
    sys.exit()

# this dictionary store the api keys
config = {}
spotify_access_token_creation = 0
spotify_access_token = ''


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
    with open('config.json') as config_file:
        config: dict = json.load(config_file)
    SPOTIFY_AUTH_STR = f"{config['SPOTIFY_CLIENT_ID']}:{config['SPOTIFY_SECRET']}"
    SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()
    print('Spotify API keys loaded')
    LASTFM_API = config['LASTFM_API']
    LASTFM_SECRET = config['LASTFM_SECRET']
    print('LASTFM API keys loaded')
    # TODO: support multiple directories
    # this is for future when I get a Soundcloud api key
    # SOUNDCLOUD_CLIENT_ID = config['SOUNDCLOUD_CLIENT_ID']
    # SOUNDCLOUD_CLIENT_SECRET = config['SOUNDCLOUD_CLIENT_SECRET']
except (FileNotFoundError, KeyError): print('config.json not found. Limited functionality')


def set_title(audio: EasyID3, title: str):
    """
    Sets a title for an EasyID3 object
    :param audio: EasyID3 Object
    :param title: string
    """
    audio['title'] = title
    audio.save()


def set_artists(audio: EasyID3, artists):
    """
    Sets an artist for an EasyID3 object
    :param audio: EasyID3
    :param artist: string or list[str] of the artist or artists
    """
    audio['artist'] = artists
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
    Sets an album coverist for an EasyID3 object
    :param audio: EasyID3
    :param album_artist: name of the album coverist
    """
    audio['albumartist'] = album_artist
    audio.save()


def auto_set_year(audio: MP3, artist, title):
    url1 = f'https://api.spotify.com/v1/search?q={title}+artist:{artist}&type=track&market=US'
    url2 = f'https://api.spotify.com/v1/search?q={title}+artist:{artist}&type=track&market=CA'
    urls = [url1, url2]
    artist, title = parse.quote(artist), parse.quote(title)
    header = {'Authorization': 'Bearer ' + get_spotify_access_token()}
    for url in urls:
        r = requests.get(url, headers=header).json()
        if 'tracks' in r:
            p = re.compile('[1-9][0-9]{3}')
            min_year = None
            for item in r['tracks']['items']:
                release_year = int(p.search(item['album']['release_date']).group())
                if min_year is None: min_year = release_year
                else: min_year = min(min_year, release_year)
            if min_year is not None:
                set_year(audio, str(min_year))
                return True
    return False

def set_year(audio: MP3, year: int):
    audio['TDRC'] = mutagen.id3.TDRC(encoding=3, text=year)
    audio.save()


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
    if type(filename) not in (MP3, File): audio = MP3(filename)
    else: audio = filename
    audio['TCON'] = mutagen.id3.TCON(encoding=3, text=';'.join(genres))  # genre key is TCON
    audio.save()
    return True


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


def add_simple_metadata(file_path, artist='', title='', album='', albumartist='', override=False):
    """
    Automatically sets the metadata for a music file
    :param file_path: the path to the music file
    :param artist: given artist name
    :param title: given title name
    :param album: given album name
    :param albumartist: given album coverist
    :param override: if True, all of the metadata is overridden
    :return: True or False depending on whether audio file was changed or not
    """
    audio = EasyID3(file_path)
    filename = pathlib.Path(file_path).name
    advanced_audio = File(file_path)
    try:
        if (not override and audio.get('title', '') and audio.get('artist', '')
            and audio.get('albumartist', '') and has_album_cover(file_path)) and 'TDRC' in advanced_audio: return False
        if not artist: artist = get_artist(filename)
        else:
            if artist.count(' , '): artist.split(' , ')
            elif artist.count(' ,'): artist = artist.split(' ,')
            elif artist.count(', '): artist = artist.split(', ')
            elif artist.count(','): artist = artist.split(',')
        if not title: title = filename[filename.index('-') + 2:-4]
        if override:
            audio['title'] = title
            audio['artist'] = artist
            if album: audio['album'] = album
            if albumartist: audio['albumartist'] = albumartist
        else:
            if 'album' not in audio:
                if album == '': audio['album'] = title
                else: audio['album'] = album
            if 'title' not in audio: audio['title'] = title
            if 'artist' not in audio: audio['artist'] = artist
            if 'albumartist' not in audio:
                if albumartist: audio['albumartist'] = albumartist
                else: audio['albumartist'] = artist        
        audio.save()
        audio = MP3(file_path)
        if artist and title and override or audio.get('TDRC', False):
            auto_set_year(audio, artist, title)
        if not has_album_cover(file_path): set_album_cover(file_path)
        return True
    except MutagenError:
        print(f'{filename} in use')
    except ValueError:
        print('Error adding metadata to', filename)
        return False


auto_set_metadata = auto_set_simple_metadata = set_simple_meta = add_simple_metadata


def has_album_cover(audio) -> bool:
    """
    Checks if the file has an album cover
    Also fixes album cover key + Encoding
    :param audio: Either file path or audio object
    :return: boolean expressing whether the file contains album cover
    """
    if type(audio) == str: audio: File = File(audio)
    try:
        fix_cover(audio)
        if 'APIC:' in audio:
            apic: mutagen.id3.APIC = audio['APIC:']
            if apic.encoding != Encoding.LATIN1:
                apic.encoding = Encoding.LATIN1
                audio['APIC:'] = apic
                audio.save()
            return True
    except KeyError: audio.add_tags()
    return False


def retrieve_album_art(audio: MP3):
    apics = [v for k, v in audio.items() if k.startswith('APIC')]
    if apics: return apics[0]
    return None


get_album_art = retrieve_album_art


def search_album_art(artist, title, select_index=0, return_all=False):
    """
    Fetches max resolution album cover(s) for track (artist and title specified) using Spotify API
    :param artist: artist
    :param title: title of track
    :param select_index: which result to pick (by default the first)
    :param return_all: if set to True, function returns all max res album cover
    :return: url(s) of the highest resolution album cover for the track
    """
    # TODO: add soundcloud search as well if spotify comes up with no results.
    #  Soundcloud has it disabled
    artist, title = parse.quote(artist), parse.quote(title)
    header = {'Authorization': 'Bearer ' + get_spotify_access_token()}
    # TODO: search through playlists too
    links = []
    links_set = set()
    for code in COUNTRY_CODES:
        url = f'https://api.spotify.com/v1/search?q={title}+artist:{artist}&type=track&market={code}'
        r = requests.get(url, headers=header).json()
        if 'tracks' in r:
            links_from_country = [item['album']['images'][0]['url'] for item in r['tracks']['items']]
            for link in links_from_country:
                if link not in links_set:
                    links.append(link)
                    links_set.add(link)
    if return_all: return links
    return links[0]


find_album_covers = search_album_covers = search_album_art

def set_album_cover(file_path, img_path='', url='', copy_from='', title='', artist='', select_index=0):
    audio = MP3(file_path, ID3=mutagen.id3.ID3)
    filename = pathlib.Path(file_path).name
    with suppress(mutagen.id3.error):
        audio.add_tags()
    if title and artist:
        try:
            img_path = search_album_art(artist, title)
            image_data = urlopen(img_path).read()
        except (KeyError, ValueError, IndexError):
            print(f'Album cover not found for: {filename}')
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
            return True
        except KeyError:
            other_audio = other_audio.items()
            unchanged = True
            for k, v in other_audio:
                if k.startswith('APIC:'):
                    audio['APIC:'] = v
                    audio.save()
                    unchanged = False
            if unchanged: print('That file is incompatible.')
    else:
        easy_audio = EasyID3(file_path)
        if 'title' in easy_audio and not title:
            title = easy_audio['title'][0]
        else:
            add_simple_metadata(file_path)
            title = filename[filename.index('-') + 2:-4]
        if 'artist' in easy_audio and not artist:
            artist = easy_audio['artist'][0]
        else:
            add_simple_metadata(file_path)
            artist = get_artist(filename)
        try:
            img_path = search_album_art(artist, title, select_index=select_index)
            image_data = urlopen(img_path).read()
        except (KeyError, ValueError, IndexError):
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
    return True


add_mp3_cover = add_album_cover = set_album_cover


# @memoize
def get_temp_path(filename):
    base = os.path.basename(filename)
    base = f'BACKUP {base}'
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
    album_cover = MP3(filename, ID3=mutagen.id3.ID3).get('APIC:')
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
    if album_cover is not None: audio['APIC:'] = album_cover
    audio.save()
    os.remove(temp_path)
    os.remove('ffmpeg.log')


def get_song_length(filename):
    return File(filename).info.length


def trim(filename, start, end):
    song_length = get_song_length(filename)
    set_simple_meta(filename)
    if type(start) == str and start.count(':') == 1:
        mins, secs = [int(t) for t in start.split(':')]
        start = min(max(mins * 60 + secs, 0), song_length)
    if type(end) == str and end.count(':') == 1:
        mins, secs = [int(t) for t in end.split(':')]
        end = max(mins * 60 + secs, song_length)
    if end == '': end = song_length
    with suppress(ValueError): start = float(start)
    with suppress(ValueError): end = float(end)
    if type(start) == str or type(end) == str: return False
    temp_path = get_temp_path(filename)
    command = f'ffmpeg -i "{temp_path}" -ss {start} -t {end} -c copy "{filename}" > ffmpeg.log 2>&1'
    ffmpeg_helper(filename, command)
    return True


def remove_silence(filename):
    temp_path = get_temp_path(filename)
    command = f'ffmpeg -i "{temp_path}" -af silenceremove=start_periods=1:stop_periods=1:detection=peak "{filename}" ' \
              f'> ffmpeg.log 2>&1'
    ffmpeg_helper(filename, command)


def get_genre(audio: MP3):
    return audio.get('TCON')


def get_year(audio: MP3):
    return audio.get('TDRC')

# audio[u"USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
def get_lyrics(audio: MP3):
    return audio.get(u"USLT::'eng'")


def remove_covers(audio: MP3):
    for key in audio.keys():
        if key.startswith('APIC'): audio.pop(key)
    audio.save()


def optimize_cover(audio: MP3):
    apic = retrieve_album_art(audio)
    if apic:
        data = apic.data
        data = io.BytesIO(data)
        im = Image.open(data)
        new_data = io.BytesIO()
        try: im.save(new_data, optimize=True, format='JPEG')
        except OSError: im.convert('RGB').save(new_data, optimize=True, format='JPEG')
        if len(data.getvalue()) - len(new_data.getvalue()) > 0:
            audio['APIC:'] = mutagen.id3.APIC(
                encoding=0,  # 3 is for utf-8
                mime='image/jpeg',  # image/jpeg or image/png
                type=3,  # 3 is for the cover image
                # desc=u'Cover',
                data=new_data.getvalue()
            )
            audio.save()


def fix_cover(audio: File):
    """
    Transfers album cover from audio key APIC:XXXX to APIC:
    Example
    audio['APIC: Payday 2.jpg'] = APIC() becomes audio['APIC:'] = APIC()
    """
    restart = False
    for k in audio.keys():
        if k.startswith('APIC:') and k != 'APIC:':
            audio['APIC:'] = audio.pop(k)
            audio.save()
            restart = True
            break
    if restart: fix_cover(audio)


def get_bitrate(audio: File):
    return audio.info.bitrate


def find_bitrates_under(files, bitrate_thresh):
    low_quality_files = []
    for file in files:
        a = File(file)
        if get_bitrate(a) < bitrate_thresh:
            low_quality_files.append(file)
    with open(f'{starting_dir}/files under bitrate_thresh.txt', 'w') as f:
        f.write('\n'.join(low_quality_files))
    return low_quality_files
            

if __name__ == '__main__':
    # search_album_art('Afrojack', 'No Beef', return_all=True)
    find_bitrates_under(glob(r'C:\Users\maste\OneDrive\Music\*.mp3'), 192000)
    a = MP3(r"C:\Users\maste\OneDrive\Music\Afrojack, Steve Aoki, Miss Palmer - No Beef.mp3")
    a2 = MP3(r"C:\Users\maste\OneDrive\Music\Adam K & Soha - Twilight.mp3")
    # auto_set_year(a, 'Afrojack', 'No Beef')
    # auto_set_year(a2, 'Adam K', 'Twilight')
    assert get_year(a2) == '2007'
    assert get_year(a)  == '2011'
