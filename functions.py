from urllib import parse
from mutagen.easyid3 import EasyID3
import base64
from urllib.request import urlopen
import requests
from mutagen import File
import mutagen.id3
# noinspection PyProtectedMember
from mutagen.id3 import Encoding
from mutagen.mp3 import MP3
import pathlib

# this dictionary store the api keys
config = {}

# load the api keys
with open('config.txt') as f:
    for line in f.read().splitlines():
        i = line.index(' ')  # the file is formatted: VARIABLE = KEY
        varValue = line[i + 3:]
        try:
            varValue = int(varValue)
        except ValueError:
            try:
                varValue = float(varValue)
            except ValueError:
                pass
        config[line[:i]] = varValue

# set the spotify auth str (needs to be base64 encoded)
SPOTIFY_AUTH_STR = f"{config['SPOTIFY_CLIENT_ID']}:{config['SPOTIFY_SECRET']}"
SPOTIFY_B64_AUTH_STR = base64.urlsafe_b64encode(SPOTIFY_AUTH_STR.encode()).decode()


# this is for future when I get a soundcloud api key
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


def add_simple_meta(mp3_path: str, artist='', title='', album='', albumartist='', override=False):
    """
    Automatically sets the metadata for an mp3 file
    :param mp3_path: the path to the mp3 file
    :param artist: given artist name
    :param title: given title name
    :param album: given album name
    :param albumartist: given album artist
    :param override: if True, files metadata is overriden
    :return: True or False
    """
    audio = EasyID3(mp3_path)
    filename = pathlib.Path(mp3_path).name  # or filename = mp3_path[:-4]
    try:
        if artist == '':
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
        return True
    except ValueError:
        print('Error with', filename)
        return False


set_simple_meta = add_simple_meta


def has_album_art(file_path: str) -> bool:
    """
    Checks if the file has an album coover
    :param file_path:
    :return:
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


def get_album_art(artist: str, title: str, access_token='', select_index=0, return_all=False):
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
    if return_all:
        results = [item['album']['images'][0]['url'] for item in r.json()['tracks']['items']]
        return results
    return r.json()['tracks']['items'][select_index]['album']['images'][0]['url']


def set_album_cover(file_path: str, img_path='', url='', title='', artist='', select_index=0) -> bool:
    audio = MP3(file_path, ID3=mutagen.id3.ID3)
    # with open('b.txt', 'w') as f:
    #     f.writelines(audio)
    file = pathlib.Path(file_path).name

    if title and artist:
        try:
            img_path = get_album_art(artist, title)
            image_data = urlopen(img_path).read()
        except (KeyError, ValueError, IndexError):
            print(f'Album art not found for: {file}')
            return False
    elif not img_path and not url:
        if 'title' in audio: title = audio['title']
        else:
            add_simple_meta(file_path)
            title = file[file.index('-') + 2:-4]
        if 'artist' in audio:
            artist = audio['artist']
            if type(artist) == list:
                artist = artist[0]
        else:
            add_simple_meta(file_path)
            artist = file[:file.index(' -')]
            if artist.count(', ') > 0:
                artist = artist.split(', ')[0]
            elif artist.count(' vs') > 0:
                artist = artist.split(' vs')[0]
            elif artist.count(' &') > 0:
                artist = artist.split(' &')[0]
            elif artist.count(' ft') > 0:
                artist = artist.split(' ft')[0]
        try:
            img_path = get_album_art(artist, title, select_index=select_index)
            image_data = urlopen(img_path).read()
        except (KeyError, ValueError, IndexError):
            print(f'Album art not found for: {file}')
            return False

    elif img_path:
        with open(img_path, 'rb') as bits:  # better than open(albumart, 'rb').read() ?
            image_data = bits.read()
    else:
        url = url.replace(' ', '')
        image_data = urlopen(url).read()
        img_path = url
    if img_path.endswith('png'):
        mime = 'image/png'
    else:
        mime = 'image/jpeg'
    # image.desc = 'front cover'
    try:
        audio.add_tags()
    except mutagen.id3.error:
        pass
    audio['APIC:'] = mutagen.id3.APIC(
        encoding=0,  # 3 is for utf-8
        mime=mime,  # image/jpeg or image/png
        type=3,  # 3 is for the cover image
        # desc=u'Cover',
        data=image_data
    )
    audio.save()
    return True


add_mp3_cover = add_album_cover = set_album_cover

# def trim(filename, start: float, end: float):  # TODO
#     elapsed = end - start
#     # ffmpeg -ss 10 -t 6 -i input.mp3 output.mp3
#     return
