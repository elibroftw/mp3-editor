from glob import glob
from os import chdir, rename, path, getcwd
from tkinter import filedialog
import tkinter as tk

try:
    from tqdm import tqdm
    from functions import *
    import image_selector
except ImportError as e:
    print(e)
    input('Press Enter to exit....')
    quit()

starting_directory = getcwd()
root = tk.Tk()
root.withdraw()
# TODO: make into a gui


def individual_select(filename):
    with open(starting_directory+'/individual_select.txt') as f:
        individual_select_menu_text = f.read()
    print('You selected:', filename)
    print(individual_select_menu_text, end='')
    on_menu = True
    while on_menu:
        try: audio = EasyID3(filename)
        except mutagen.id3.ID3NoHeaderError:
            audio = mutagen.File(filename, easy=True)
            audio.add_tags()
        try:
            sub_menu_user_choice = int(input())
            if sub_menu_user_choice == 1:
                add_simple_meta(filename)
                print('Simple metadata set')
            elif sub_menu_user_choice == 2:
                add_simple_meta(filename, override=True)
                print('Simple metadata set')
            elif sub_menu_user_choice == 3:
                set_title(audio, input('Enter title: '))
                print('Title set')
            elif sub_menu_user_choice == 4:
                set_artist(audio, input('Enter artist: '))
                print('Artist set')
            elif sub_menu_user_choice == 5:
                set_artist(audio, input('Enter artists (comma separated eg. "Elijah, Lopez"): ').split(', '))
                print('Artists set')
            elif sub_menu_user_choice == 6:
                set_album(audio, input('Enter album: '))
                print('Album title set')
            elif sub_menu_user_choice == 7:
                set_album_artist(audio, input('Enter album artist: '))
            elif sub_menu_user_choice == 8:
                print('1. Auto')
                print('2. Url')
                print('3. Local Image')
                print('4. Another File')
                print('5. Manual')
                print('6. Exit')
                try:
                    album_art_choice = int(input('Enter an option: '))
                    if album_art_choice == 1:
                        set_simple_meta(filename)
                    elif album_art_choice == 2:
                        set_album_cover(filename, url=input('Enter url: '))
                    elif album_art_choice == 3:
                        set_album_cover(filename, img_path=filedialog.askopenfilename(title='Select album art', filetypes=[('Image', '*.jpg *.jpeg *.png')]))
                        root.withdraw()
                    elif album_art_choice == 4:
                        set_album_cover(filename, copy_from=filedialog.askopenfilename(title='Select 2nd track', filetypes=[('Audio', '*.mp3')]))
                        root.withdraw()
                    elif album_art_choice == 5:
                        search_title = input('Enter the title: ')
                        search_artist = input('Enter the artist: ')
                        results = get_album_art(search_artist, search_title, return_all=True)
                        if results:
                            image_selector.main(results, artist=search_artist, track=search_title)
                            url = os.environ.pop('SELECTED_URL', None)
                            if url:
                                set_album_cover(filename, url=url)
                                print('Album cover set')
                        else:
                            print('No album art found :(')
                    if album_art_choice in (1, 2, 3, 4):
                        print('Album cover set')
                except ValueError:
                    pass
            elif sub_menu_user_choice == 9:
                # set_genre(audio, input('Enter genre: '))
                pass
            elif sub_menu_user_choice == 10:
                # set_year(audio, input('Enter year (YYYY):)
                pass
            elif sub_menu_user_choice == 11:  # TODO: Rename file
                print('Enter new file name (with extension)')
                new_filename = path.dirname(filename) + '/' + input()
                if not new_filename.count('.mp3'): new_filename += '.mp3'
                rename(filename, new_filename)
                print('file name changed from ', pathlib.Path(filename).name, 'to', pathlib.Path(new_filename).name)
                filename = new_filename
            elif sub_menu_user_choice == 12:
                for k, v in audio.items():
                    print(k, ':', v)
                print('album cover :', has_album_art(filename))
            elif sub_menu_user_choice == 13:
                start = int(input('Enter start time (seconds): '))
                end = int(input('Enter end time (seconds): '))
                trim(filename, start, end)
            elif sub_menu_user_choice == 14:
                on_menu = False
            else:
                print(individual_select_menu_text)
            if 0 < sub_menu_user_choice < 15:
                print('Enter an option')
            else: print('Please enter an integer from 1 to 15')
        except ValueError: print('Please enter an integer from 1 to 15')


def main():
    music_directory = config.get('MUSIC_LOCATION', '')
    while music_directory == '' or not os.path.exists(music_directory):
        music_directory = filedialog.askdirectory(title='Select Music Directory')
        root.withdraw()
    chdir(music_directory)
    output_intro = True
    while True:
        if output_intro:
            print('What would you like to do?')
            print(f'1. Change Directory (currently: {music_directory})')
            print('2. Set metadata for tracks with missing covers (No override)')
            print('3. Set album covers for all tracks missing album art')
            print('4. Select an individual track')
            print('5. View mp3 files in directory (and then select)')
            print('6. Search for album covers')  # make menu better
            print('7. Exit')
        try:
            user_choice = int(input())
        except ValueError:
            user_choice = 0
        output_intro = True
        if user_choice == 1:
            music_directory = filedialog.askdirectory(title='Select Music Directory')
            root.withdraw()
            if os.path.exists(music_directory):
                chdir(music_directory)
                print('Directory changed to', music_directory)
        elif user_choice == 2:
            for file in glob('*.mp3'):
                add_simple_meta(file)
            print('Metadata for all tracks set')
        elif user_choice == 3:
            for file in tqdm(glob('*.mp3')):
                if not has_album_art(file):
                    add_simple_meta(file)
                    set_album_cover(file)
        elif user_choice == 4:
            file = filedialog.askopenfilename(title='Select track', filetypes=[('Audio', '*.mp3')])
            root.withdraw()
            individual_select(file)
        elif user_choice == 5:
            files = glob('*.mp3')
            for i, file in enumerate(files): print(f'{i + 1}. {file}')

            print('Enter a valid integer to select the respective file')
            print('Entering anything else will let you go back to the main menu')

            try: individual_select(files[int(input()) - 1])
            except (ValueError, IndexError): pass
        elif user_choice == 6:
            search_title = input('Enter the title: ')
            search_artist = input('Enter the artist: ')
            results = get_album_art(search_artist, search_title, return_all=True)
            if results:
                image_selector.main(results, artist=search_artist, track=search_title)
                url = os.environ.pop('SELECTED_URL', None)
                if url:
                    if copy(url): print('Copied url to clipboard!')
                    else: print(url)
            else: print('No album art found :(')
        elif user_choice == 7: return
        else:
            output_intro = False
            print('Please enter an integer from 1 to 7')


if __name__ == '__main__':
    main()
