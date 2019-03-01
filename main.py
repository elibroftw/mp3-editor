import platform
from os import chdir, system, rename, path, getcwd
from tkinter import filedialog
from tqdm import tqdm
from functions import get_album_art, config, add_simple_meta, EasyID3, set_title, set_artist, set_album, set_album_artist, pathlib, set_album_cover
from glob import glob

starting_directory = getcwd()


def copy(text):
    if platform.system() == 'Windows':
        command = f'echo|set/p={text}|clip'
        # command = 'echo ' + text.strip() + '| clip'  # this added a new line character
        system(command)
        return True
    return False


def individual_select(filename):
    with open(starting_directory+'/individual_select.txt') as f:
        individual_select_menu_text = f.read()
    print('You selected:', filename)
    print(individual_select_menu_text, end='')
    on_menu = True
    while on_menu:
        audio = EasyID3(filename)
        try:
            sub_menu_user_choice = int(input())
            if sub_menu_user_choice == 1:
                add_simple_meta(filename)
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
                        set_album_cover(filename)
                    elif album_art_choice == 2:
                        set_album_cover(filename, url=input('Enter url: '))
                    elif album_art_choice == 3:
                        set_album_cover(filename, img_path=filedialog.askopenfilename(title='Select album art', filetypes=[('Image', '*.jpg *.jpeg *.png')]))
                    elif album_art_choice == 4:
                        set_album_cover(filename, copy_from=filedialog.askopenfilename(title='Select 2nd track', filetypes=[('Audio', '*.mp3')]))
                    elif album_art_choice == 5:
                        search_title = input('Enter the title: ')
                        search_artist = input('Enter the artist: ')
                        try:
                            set_album_cover(filename, artist=search_artist, title=search_title)
                            print('Album cover set')
                        except IndexError:
                            print('Album art not found')
                    if album_art_choice in (1, 2, 3, 4):
                        print('Album cover set')
                except ValueError:
                    pass
            elif sub_menu_user_choice == 9:
                # set_genre(audio, input('Enter genre: '))
                pass
            elif sub_menu_user_choice == 10:
                # set_date(audio, input('Enter data (MM/DD/YYYY):)
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
                on_menu = False
            if 0 < sub_menu_user_choice < 13:
                print(individual_select_menu_text)
                print('Enter an option')
            else: print('Please enter an integer from 1 to 13')
        except ValueError: print('Please enter an integer from 1 to 13')


def main():
    music_directory = config.get('MUSIC_LOCATION', '')
    if music_directory == '':
        music_directory = filedialog.askdirectory(title='Select Music Directory')

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
            try:
                results = get_album_art(search_artist, search_title, return_all=True)
                for i, result in enumerate(results): print(f'{i + 1}. {result}')
                print('Enter a valid integer to copy the respective url to your clipboard (Windows Only)'
                      'Entering anything else will let you go back to the main menu')
                try:
                    url = results[int(input()) - 1]
                    if copy(url): print('Copied url to clipboard!')
                except (ValueError, IndexError): pass
            except IndexError:
                print('No results found :(')
        elif user_choice == 7: return
        else:
            output_intro = False
            print('Please enter an integer from 1 to 7')


if __name__ == '__main__': main()
