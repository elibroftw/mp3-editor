import os
from urllib import parse
import base64
from urllib.request import urlopen
import requests
from mutagen import File
from mutagen.easyid3 import EasyID3
import mutagen.id3
# noinspection PyProtectedMember
from mutagen.id3 import Encoding
from mutagen.mp3 import MP3
import pathlib

# this dictionary store the api keys
config = {}

try:
    # load the config values
    with open('config.txt') as f:
        for line in f.read().splitlines():
            space_index = line.index(' ')  # the file is formatted: VARIABLE = KEY
            varValue = line[space_index + 3:]
            if varValue.isdigit():
                varValue = int(varValue)
            else:
                varValue = float(varValue) if varValue.replace('.', '', 1).isdigit() else varValue
            config[line[:space_index]] = varValue

    # set the spotify auth str (needs to be base64 encoded)
    SPOTIFY_AUTH_STR = f"{config['SPOTIFY_CLIENT_ID']}:{config['SPOTIFY_SECRET']}"
    SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()
except (FileNotFoundError, KeyError):
    print('Limited functionality')


# this is for future when I get a Soundcloud api key
# SOUNDCLOUD_CLIENT_ID = config['SOUNDCLOUD_CLIENT_ID']
# SOUNDCLOUD_CLIENT_SECRET = config['SOUNDCLOUD_CLIENT_SECRET']


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
    artist = filename[:filename.index(' -')]

    # Extraction of artist(s) name(s) from filename
    # Different ways to name a file
    # Lots of these are just-in-case situations
    # The standard for naming multiple artists is comma sepearted values with a space after each comma
    # Eg. path = "artist_1, artist_2, artist_3 - title.mp3"

    # ,
    if artist.count(' , '):
        artist.split(' , ')
    elif artist.count(', '):
        artist = artist.split(', ')
    elif artist.count(','):
        artist = artist.split(',')

    # vs
    if artist.count(' vs. '):
        artist = artist.split(' vs. ')
    elif artist.count(' vs '):
        artist = artist.split(' vs ')
    elif artist.count(' vs.'):
        artist = artist.split(' vs.')
    elif artist.count(' vs'):
        artist = artist.split(' vs')

    # if artist.count(' & '):  # dimitri vegas & like mike are one artist so I can't use this statement
    #     artist = artist.split(' & ')

    # and
    if artist.count(' and '):
        artist = artist.split(' and ')
    elif artist.count(' and'):
        artist = artist.split(' and')

    # ft
    if artist.count(' ft '):
        artist = artist.split(' ft ')
    elif artist.count(' ft. '):
        artist = artist.split(' ft. ')
    elif artist.count(' ft.'):
        artist = artist.split(' ft.')
    elif artist.count(' ft'):
        artist.split(' ft')

    # feat
    if artist.count(' feat '):
        artist = artist.split(' feat ')
    elif artist.count(' feat. '):
        artist = artist.split(' feat. ')
    elif artist.count(' feat.'):
        artist = artist.split(' feat.')
    elif artist.count(' feat'):
        artist = artist.split(' feat')

    return artist


def add_simple_meta(mp3_path, artist='', title='', album='', albumartist='', override=False):
    """
    Automatically sets the metadata for an mp3 file
    :param mp3_path: the path to the mp3 file
    :param artist: given artist name
    :param title: given title name
    :param album: given album name
    :param albumartist: given album artist
    :param override: if True, files metadata is overridden
    :return: True or False
    """
    audio = EasyID3(mp3_path)
    filename = pathlib.Path(mp3_path).name  # or filename = mp3_path[:-4]
    try:
        if artist == '':
            artist = get_artist(filename)
        else:
            if artist.count(' , '):
                artist.split(' , ')
            elif artist.count(', '):
                artist = artist.split(', ')
            elif artist.count(','):
                artist = artist.split(',')
        if title == '': title = filename[filename.index('-') + 2:-4]
        if override:
            audio['title'] = title
            audio['artist'] = artist
            if album != '': audio['album'] = album
            if albumartist != '': audio['albumartist'] = albumartist
        else:
            if 'album' not in audio:
                if album == '':
                    audio['album'] = title
                else:
                    audio['album'] = album
            if 'title' not in audio: audio['title'] = title
            if 'artist' not in audio: audio['artist'] = artist
            if 'albumartist' not in audio:
                if albumartist == '':
                    audio['albumartist'] = artist
                else:
                    audio['albumartist'] = albumartist
        audio.save()
        if not has_album_art(mp3_path):
            set_album_cover(mp3_path)
        return True
    except ValueError:
        print('Error with', filename)
        return False


set_simple_meta = add_simple_meta


def has_album_art(mp3_path) -> bool:
    """
    Checks if the file at mp3_path has an album coover
    :param mp3_path:
    :return:
    """
    audio: File = File(mp3_path)
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


def get_album_art(artist, title, access_token='', select_index=0, return_all=False):
    """
    Fetches max resolution album art(s) for track (artist and title specified) using Spotify API
    :param artist: artist
    :param title: title of track
    :param access_token: Spotify access token
    :param select_index: which result to pick (by default the first)
    :param return_all: if set to True, function returns all max res album art
    :return: url(s) of the highest resolution album art for the track
    """
    # TODO: add soundcloud search as well if spotify comes up with no results.
    #  Soundcloud has it disabled
    artist, title = parse.quote_plus(artist), parse.quote_plus(title)
    if not access_token:
        header = {'Authorization': 'Basic ' + SPOTIFY_B64_AUTH_STR}
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post('https://accounts.spotify.com/api/token', headers=header, data=data)
        access_token = access_token_response.json()['access_token']
    header = {'Authorization': 'Bearer ' + access_token}
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
        url = url.replace(' ', '')
        image_data = urlopen(url).read()
        img_path = url
    elif copy_from:
        audio['APIC:'] = MP3(copy_from, ID3=mutagen.id3.ID3)['APIC:']
        audio.save()
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

    if img_path.endswith('png'):
        mime = 'image/png'
    else:
        mime = 'image/jpeg'
    # image.desc = 'front cover'

    audio['APIC:'] = mutagen.id3.APIC(
        encoding=0,  # 3 is for utf-8
        mime=mime,  # image/jpeg or image/png
        type=3,  # 3 is for the cover image
        # desc=u'Cover',
        data=image_data
    )
    audio.save()
    return


add_mp3_cover = add_album_cover = set_album_cover


def trim(filename, start: int, end: int):
    audio = EasyID3(filename)
    artists = audio['artist']
    title = audio['title']
    album = audio['album']
    album_artist = audio['albumartist']
    album_cover = MP3(filename, ID3=mutagen.id3.ID3)['APIC:']
    base = os.path.basename(filename)
    base = f'TEMP {base}'
    directory = os.path.dirname(filename)
    temp_path = directory + '\\' + base
    os.rename(filename, temp_path)
    command = f'ffmpeg -i "{temp_path}" -ss {start} -t {end} -c copy "{filename}" > ffmpeg.log 2>&1'
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

