from os import chdir, rename, path, getcwd
import tkinter as tk
try:
    from tqdm import tqdm
    from functions import *
    from image_selector import image_selector
except ImportError as e:
    print(e)
    input('Press Enter to exit....')
    sys.exit()

starting_directory = getcwd()
root = tk.Tk()
root.withdraw()
music_directory = config.get('MUSIC_LOCATION', '')
while music_directory == '' or not os.path.exists(music_directory):
    music_directory = tk.filedialog.askdirectory(title='Select Music Directory')

music_directory = music_directory.replace('\\', '/')
if config.get('MUSIC_LOCATION', '') != music_directory:
    config['MUSIC_LOCATION'] = music_directory
    with open('config.json', 'w') as json_file: json.dump(config, json_file, indent=4)


def individual_select(filename):
    global music_directory, root
    with open(starting_directory+'/individual_select.txt') as f:
        individual_select_menu_text = f.read()
    print('You selected:', filename)
    print(individual_select_menu_text)
    on_menu = True
    while on_menu:
        try:
            easy_audio = EasyID3(filename)
            audio = File(filename)
        except mutagen.id3.ID3NoHeaderError:
            audio = mutagen.File(filename, easy=True)
            audio.add_tags()
            easy_audio = EasyID3(filename)
        except PermissionError: break
        try:
            sub_menu_user_choice = int(input('Enter an option (1 - 16): '))
            if sub_menu_user_choice == 1:
                add_simple_metadata(filename)
                print('    Simple metadata set')
            elif sub_menu_user_choice == 2:
                add_simple_metadata(filename, override=True)
                print('    Simple metadata set')
            elif sub_menu_user_choice == 3:
                set_title(easy_audio, input('    Enter title: '))
                print('    Title set')
            elif sub_menu_user_choice == 4:
                artists = input('    Enter artist(s) (comma separated eg. "Calvin Harris, Alesso"): ')
                if ', ' in artists: artists = artists.split(', ')
                set_artists(easy_audio, artists)
                print('    Artist(s) set')
            elif sub_menu_user_choice == 5:
                set_album(easy_audio, input('    Enter album: '))
                print('    Album title set')
            elif sub_menu_user_choice == 6:
                set_album_artist(easy_audio, input('    Enter album artist: '))
            elif sub_menu_user_choice == 7:
                print('    1. Auto')
                print('    2. Url')
                print('    3. Local Image')
                print('    4. Another File')
                print('    5. Manual')
                print('    6. Back')
                with suppress(ValueError):
                    album_art_choice = int(input('    Enter an option (1 - 6): '))
                    if album_art_choice == 1:
                        add_simple_metadata(filename)
                    elif album_art_choice == 2:
                        if set_album_cover(filename, url=input('    Enter url: ')): print('    Album cover set')
                    elif album_art_choice == 3:
                        if set_album_cover(filename, img_path=tk.filedialog.askopenfilename(title='Select album cover', filetypes=[('Image', '*.jpg *.jpeg *.png')])):
                            print(f'    Album cover set')
                        root.withdraw()
                    elif album_art_choice == 4:
                        if not set_album_cover(filename, copy_from=tk.filedialog.askopenfilename(initialdir=f'{music_directory}', title='Select 2nd track', filetypes=[('Audio', '*.mp3')])):
                            print(f'    Album cover not found for: {filename}')
                        else: print('    Album cover set')
                        root.withdraw()
                    elif album_art_choice == 5:
                        search_title = input('    Enter the title: ')
                        search_artist = input('    Enter the artist: ')
                        results = search_album_art(search_artist, search_title, return_all=True)
                        if results:
                            image_selector(results, artist=search_artist, track=search_title)
                            url = os.environ.pop('SELECTED_URL', None)
                            if url and set_album_cover(filename, url=url): print('    Album cover set')
                        else: print('    No album covers found :(')
            elif sub_menu_user_choice == 9:
                covers = [audio[key].data for key in audio.keys() if key.startswith('APIC')]
                # root.lift()
                image_selector(image_bits=covers, artist=', '.join(easy_audio['artist']), track=easy_audio['title'][0])
            elif sub_menu_user_choice == 10:
                # set_genre(audio, input('Enter genre: '))
                pass
            elif sub_menu_user_choice == 11:
                # set_year(audio, input('Enter year (YYYY):)
                pass
            elif sub_menu_user_choice == 12:  # TODO: Rename file
                new_filename = path.dirname(filename) + '/' + input('    Enter new file name (with extension)')
                if not new_filename.count('.'): new_filename += '.mp3'
                rename(filename, new_filename)
                print('    File name changed from ', pathlib.Path(filename).name, 'to', pathlib.Path(new_filename).name)
                filename = new_filename
            elif sub_menu_user_choice == 13:
                for k, v in easy_audio.items(): print(f'    {k}:', v)
                print('    album cover:', has_album_cover(audio))
                print('    bitrate:', get_bitrate(audio))
            elif sub_menu_user_choice == 14:
                start = int(input('    Enter start time (seconds / MM:SS): '))
                end = int(input('    Enter end time (seconds / MM:SS): '))
                del audio
                del easy_audio
                if trim(filename, start, end): print('Succesfully trimmed file')
                else: print('Incorrect format given')
            elif sub_menu_user_choice == 15: on_menu = False
            else: print(individual_select_menu_text)
            if 0 > sub_menu_user_choice or sub_menu_user_choice > 16: print('Please enter an integer from 1 to 15')
        except ValueError: print('Please enter an integer from 1 to 15')


def main():
    global music_directory, root
    chdir(music_directory)
    output_intro = True
    while True:
        if output_intro:
            print('Welcome to Metadata Editor by Elijah Lopez')
            print(f'1. Change Directory (currently: {music_directory})')
            print('2. Auto-set missing metadata and album covers')
            print('3. Select an individual track')
            print('4. View mp3 files in directory')
            print('5. Search for album covers')  # make menu better
            print('6. Optimize all album covers')
            print('7. Exit')
        try: user_choice = int(input('Enter an option [1 - 7]: '))
        except ValueError: user_choice = 0
        output_intro = True
        if user_choice == 1:
            music_directory = tk.filedialog.askdirectory(title='Select Music Directory')
            root.withdraw()
            if os.path.exists(music_directory):
                chdir(music_directory)
                print('Directory changed to', music_directory)
        elif user_choice == 2:
            for file in tqdm(glob('*.mp3'), desc='Setting metadata'): add_simple_metadata(file)
            print('Metadata set for all tracks')
        elif user_choice == 3:
            file = tk.filedialog.askopenfilename(initialdir=f'{music_directory}', title='Select track', filetypes=[('Audio', '*.mp3')])
            root.withdraw()
            if file: individual_select(file)
        elif user_choice == 4:
            files = glob('*.mp3')
            for i, file in enumerate(files): print(f'{i + 1}. {file}')
            print('Enter an integer to select the corresponding file')
            print('Entering anything else will take you back to the main menu')
            with suppress(ValueError, IndexError): individual_select(files[int(input()) - 1])
        elif user_choice == 5:
            search_title = input('Enter the title: ')
            search_artist = input('Enter the artist: ')
            results = search_album_art(search_artist, search_title, return_all=True)
            if results:
                image_selector(results, artist=search_artist, track=search_title)
                url = os.environ.pop('SELECTED_URL', None)
                if url:
                    if copy(url): print('Copied url to clipboard!')
                    else: print(url)
            else: print('No album covers found :(')
        elif user_choice == 6:
            for file in tqdm(glob('*.mp3'), desc='Optimizing covers'):
                with suppress(PermissionError, mutagen.MutagenError):
                    temp = MP3(file)
                    fix_cover(temp)
                    optimize_cover(temp)
            print('Optimized album covers for all tracks')
        elif user_choice == 7: return
        else:
            output_intro = False
            print('Please enter an integer from 1 to 7')


if __name__ == '__main__':
    main()
