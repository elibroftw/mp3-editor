from os import chdir, rename, path, getcwd
import tkinter as tk
import threading
import sys
try:
    from tqdm import tqdm
    from functions import *
    from image_selector import image_selector, center, UnidentifiedImageError
except ImportError as e:
    print(e)
    input('Press Enter to exit....')
    sys.exit()


def init_tkinter():
    global root
    if root is None:
        root = tk.Tk()
        root.withdraw()
    # root.focus_force()


MAIN_MENU = '''
1. Auto-set missing metadata and album covers (optimized)
2. Select an individual track
3. View mp3 files in directories
4. Search for album covers
5. Optimize all album covers
6. Trim (remove starting & ending) silence from all files
7. Exit
'''
INDIVIDUAL_MENU = '''
1. Auto set simple metadata and album art
2. Set title
3. Set artist(s)
4. Set album
5. Set album artist
6. Set album cover (auto, url, local image, from another file, manual search)
# Optimize album cover (DISALBED)
8. View album covers
9. Set genre (BETA)
10. Set year  (BETA)
11. Rename file
12. Print properties
13. Trim audio
14. Remove (start & end) silence
15. Exit to main menu
16. Reprint menu
'''
starting_directory = getcwd()
root = None
music_folders = config.get('MUSIC_FOLDERS', [])
while not music_folders or not os.path.exists(music_folders[0]):
    init_tkinter()
    music_folder = tk.filedialog.askdirectory(title='Select Music Directory')
    if music_folders: music_folders[0] = music_folder
    else: music_folders.append(music_folder)

for i, folder in enumerate(music_folders):
    music_folders[i] = folder.replace('\\', '/')
# music_folders = music_folders.replace('\\', '/')
if config.get('MUSIC_FOLDERS', []) != music_folders:
    config['MUSIC_FOLDERS'] = music_folders
    with open('config.json', 'w') as json_file: json.dump(config, json_file, indent=4)


def individual_select(filename):
    global music_folders, root
    print('You selected:', filename)
    print(INDIVIDUAL_MENU)
    on_menu = True
    while on_menu:
        try:
            easy_audio = EasyID3(filename)
            audio = File(filename)
        except mutagen.id3.ID3NoHeaderError:
            audio = mutagen.File(filename)
            audio.add_tags()
            audio.save()
            easy_audio = EasyID3(filename)
        except PermissionError: break
        try:
            sub_menu_user_choice = int(input('Enter an option (1 - 16): '))
            if sub_menu_user_choice == 1:
                add_simple_metadata(filename)
                print('    Simple metadata set')
            elif sub_menu_user_choice == 2:
                title = input('    Enter title: ')
                if title:
                    set_title(easy_audio, title)
                    print('    Title set')
                else:
                    print('    Cancelled')
            elif sub_menu_user_choice == 3:
                artists = input('    Enter artist(s) (comma separated eg. "Calvin Harris, Alesso"): ')
                if artists:
                    if ', ' in artists: artists = artists.split(', ')
                    set_artists(easy_audio, artists)
                    print('    Artist(s) set')
                else:
                    print('    Cancelled')
            elif sub_menu_user_choice == 4:
                album = input('    Enter album: ')
                if album:
                    set_album(easy_audio, album)
                    print('    Album set')
                else: print('    Cancelled')
            elif sub_menu_user_choice == 5:
                album_artist = input('    Enter album artist: ')
                if album_artist:
                    set_album_artist(easy_audio, album_artist)
                    print('    Album artist set')
                else: print('    Cancelled')
            elif sub_menu_user_choice == 6:  # set album cover
                print('    1. Auto')
                print('    2. Url')
                print('    3. Local Image')
                print('    4. Another File')
                print('    5. Manual')
                print('    6. Back')
                with suppress(ValueError):
                    album_art_choice = int(input('    Enter an option (1 - 8): '))
                    if album_art_choice == 1: add_simple_metadata(filename)
                    elif album_art_choice == 2:
                        if set_album_cover(filename, url=input('    Enter url: ')): print('    Album cover set')
                    elif album_art_choice == 3:
                        init_tkinter()
                        img_path = tk.filedialog.askopenfilename(title='Select album cover',
                                                                 filetypes=[('Image', '*.jpg *.jpeg *.png')])
                        if set_album_cover(filename, img_path=img_path):
                            print(f'    Album cover set')
                        root.withdraw()
                    elif album_art_choice == 4:
                        init_tkinter()
                        copy_from = tk.filedialog.askopenfilename(initialdir=music_folders[0], title='Select 2nd track',
                                                                  filetypes=[('Audio', '*.mp3')])
                        if not set_album_cover(filename, copy_from=copy_from):
                            print(f'    Album cover not found for: {filename}')
                        else: print('    Album cover set')
                        root.withdraw()
                    elif album_art_choice == 5:
                        search_title = input('    Enter the title: ')
                        search_artist = input('    Enter the artist: ')
                        results = search_album_art(search_artist, search_title, return_all=True)
                        if results:
                            init_tkinter()
                            image_selector(results, artist=search_artist, track=search_title, root=root)
                            url = os.environ.pop('SELECTED_URL', None)
                            if url and set_album_cover(filename, url=url): print('    Album cover set')
                        else: print('    No album covers found :(')
            elif sub_menu_user_choice == 8:  # view album covers
                covers = [audio[key].data for key in audio.keys() if key.startswith('APIC')]
                init_tkinter()
                artists = ', '.join(easy_audio['artist'])
                try:
                    image_selector(image_bits=covers, artist=artists, track=easy_audio['title'][0], root=root)
                except UnidentifiedImageError:
                    print('ERROR: invalid image data. Auto setting album cover now')
                    if set_album_cover(filename): print('Album art set')
                    else: print('Album art could not be found automatically')
                    print('Exiting due to tkinter errors...')
                    sys.exit()
            elif sub_menu_user_choice == 9:
                genres = input('Enter genres (comma separated, e.g. "Hip-Hop, House"): ')
                if genres: set_genre(audio, genres.split(', '))
            elif sub_menu_user_choice == 10:
                set_year(audio, input('Enter year (YYYY): '))
            elif sub_menu_user_choice == 11:  # TODO: Rename file
                new_filename = path.dirname(filename) + '/' + input('    Enter new file name: ')
                if new_filename and not new_filename.count('.'): new_filename += os.path.splitext(filename)[1]
                if new_filename:
                    rename(filename, new_filename)
                    print('    File name changed from ', pathlib.Path(filename).name, 'to', pathlib.Path(new_filename).name)
                    filename = new_filename
                else:
                    print('    Renaming cancelled')
            elif sub_menu_user_choice == 12:
                print(f'    title: {easy_audio["title"][0]}')
                print(f"    artist: {', '.join(easy_audio['artist'])}")
                if 'album' in easy_audio: print(f'    album: {easy_audio["album"][0]}')
                if 'date' in easy_audio: print(f'    date: {easy_audio["date"][0]}')
                song_length = get_song_length(filename)
                minutes = int(song_length / 60)
                seconds = round(song_length % 60)
                if seconds < 10: seconds = f'0{seconds}'
                song_length = f'{minutes}:{seconds}'
                print('    song length:', song_length)
                print('    album cover:', has_album_cover(audio))
                print('    bitrate:', get_bitrate(audio))
            elif sub_menu_user_choice == 13:
                start = input('    Enter start time (seconds / MM:SS): ')
                end = input('    Enter end time (seconds / MM:SS): ')
                del audio
                del easy_audio
                if trim(filename, start, end): print('Successfully trimmed file')
                else: print('Incorrect format given')
            elif sub_menu_user_choice == 14:
                print('Removing silence...')
                remove_silence(filename)
                print('Silence Removed')
            elif sub_menu_user_choice == 15: on_menu = False
            else: print(INDIVIDUAL_MENU)
            if 0 > sub_menu_user_choice or sub_menu_user_choice > 16: print('Please enter an integer from 1 to 15')
        except ValueError: print('Please enter an integer from 1 to 15')


def main():
    global music_folders, root
    chdir(music_folders[0])
    output_intro = True
    while True:
        if output_intro:
            print('Welcome to Metadata Editor by Elijah Lopez')
            print(f'Directories: {"; ".join(music_folders)}')
            print(MAIN_MENU)
        try: main_choice = int(input('Enter an option [1 - 8]: '))
        except ValueError: main_choice = 0
        output_intro = True
        if main_choice == 1:
            # started_threads = []
            # n_started_threads = []
            for file in tqdm(glob('*.mp3'), desc='Setting metadata'):
                if add_simple_metadata(file):
                    optimize_cover(MP3(file))
            #         t = threading.Thread(target=remove_silence, args=[os.path.abspath(file)])
            #         if threading.active_count() < 10:
            #             started_threads.append(t)
            #             t.start()
            #         else: n_started_threads.append(t)
            # for t in tqdm(n_started_threads, desc='Start Trimming Silence Threads'):
            #     while threading.active_count() > 15: time.sleep(1)
            #     t.start()
            #     started_threads.append(t)
            # for t in tqdm(started_threads, desc='Trimming Silence'):
            #     t.join()
            print('Done')
        elif main_choice == 2:
            init_tkinter()
            file = tk.filedialog.askopenfilename(initialdir=music_folders, title='Select track',
                                                 filetypes=[('Audio', '*.mp3')])
            if file: individual_select(file)
        elif main_choice == 3:
            files = []
            for _folder in music_folders:
                files += glob(f'{_folder}/**/*.mp3', recursive=True)
            for index, file in enumerate(files): print(f'{index + 1}. {file.replace("\\", "/")}')
            print('Enter an integer to select the corresponding file')
            print('Entering anything else will take you back to the main menu')
            with suppress(ValueError, IndexError): individual_select(files[int(input()) - 1])
        elif main_choice == 4:
            search_title = input('Enter the title: ')
            search_artist = input('Enter the artist: ')
            results = search_album_art(search_artist, search_title, return_all=True)
            if results:
                init_tkinter()
                image_selector(results, artist=search_artist, track=search_title, root=root)
                url = os.environ.pop('SELECTED_URL', None)
                if url:
                    if copy(url): print('Copied url to clipboard!')
                    else: print(url)
            else: print('No album covers found :(')
        elif main_choice == 5:
            for file in tqdm(glob('*.mp3'), desc='Fix covers/APIC encoding'):
                with suppress(PermissionError, mutagen.MutagenError):
                    temp = MP3(file)
                    fix_cover(temp)
                    # optimize_cover(temp)
            print('Optimized album covers for all tracks')
        elif main_choice == 6:
            for file in tqdm(glob('*.mp3'), desc='Optimizing covers'):
                with suppress(PermissionError, mutagen.MutagenError):
                    remove_silence(file)
            print('Removed silence from for all tracks')
        elif main_choice == 7: return
        else:
            output_intro = False
            print('Please enter an integer from 1 to 7')


if __name__ == '__main__':
    main()
