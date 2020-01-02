import tkinter as tk
from tkinter import Label, Button, Listbox
from tkinter import filedialog
from tkinter import messagebox
from os import chdir
from functions import *
import image_selector
from win10toast import ToastNotifier
toaster = ToastNotifier()
center = image_selector.center


LARGE_FONT = ('Verdana', 12)
music_directory = config.get('MUSIC_LOCATION', '')
# bbg = '#4285f4'  # button background
bbg = '#0088ff'
babg = '#00bbff'  # button active background


# TODO: make button text larger
# TODO: individual select


class MainGUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        frame = StartPage(self.container, self)
        self.frames = {StartPage: frame}
        frame.grid(row=0, column=0, sticky='nsew')

        # for F in (StartPage):
        #     frame = F(container, self)
        #     self.frames[F] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")
        self.title('Music Metadata Editor by Elijah Lopez')
        self.show_frame(StartPage)

    def show_frame(self, cont, kwargs={}):
        if cont not in self.frames:
            if kwargs:
                frame = cont(self.container, self, kwargs)
            else:
                frame = cont(self.container, self)
            frame.grid(row=0, column=0, sticky='nsew')
        else:
            frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        global music_directory
        while music_directory == '' or not os.path.exists(music_directory):
            music_directory = filedialog.askdirectory(title='Select Music Directory')
        music_directory = music_directory.replace('\\', '/')
        if config.get('MUSIC_LOCATION', '') != music_directory:
            config['MUSIC_LOCATION'] = music_directory
            with open('config.json', 'w') as json_file: json.dump(config, json_file, indent=4)
        chdir(music_directory)
        tk.Frame.__init__(self, parent, bg='#141414')
        self.controller = controller

        self.label1 = Label(self, text=f'Working Directory: {music_directory}', bg='#141414', fg='white',
                            font=LARGE_FONT)
        self.label1.pack(pady=20)

        button1 = Button(self, text=f'Change Directory', bg=bbg, activebackground=babg, command=self.change_directory)
        button1.pack(pady=10)

        button2 = Button(self, text='Auto-set metadata for files with missing metadata and album cover', bg=bbg,
                         activebackground=babg, command=self.set_missing_metadata)
        button2.pack(pady=10)

        button3 = Button(self, text='Select an individual track', bg=bbg, activebackground=babg,
                         command=self.select_individual_track)
        button3.pack(pady=10)

        button4 = Button(self, text='View music files in directory', bg=bbg, activebackground=babg,
                         command=self.view_music_files)
        button4.pack(pady=10)

        button5 = Button(self, text='Search for album covers', bg=bbg, activebackground=babg,
                         command=self.search_for_album_covers)
        button5.pack(pady=10)

        self.bindings()
        # self.focus()

    def change_directory(self):
        global music_directory
        old_length = len(music_directory)
        temp_music_directory = filedialog.askdirectory(title='Select Music Directory')
        if os.path.exists(temp_music_directory):
            music_directory = temp_music_directory
            new_length = len(music_directory)
            diff = new_length - old_length
            chdir(music_directory)
            if diff > 0:
                self.label1.configure(text=f'Working Directory: ...{music_directory[diff:]}')
            else:
                self.label1.configure(text=f'Working Directory: {music_directory}')

    @staticmethod
    def set_missing_metadata():
        for file in glob('*.mp3'): add_simple_metadata(file)
        # TODO: status message

    def select_individual_track(self):
        file = filedialog.askopenfilename(initialdir=f'{music_directory}', title='Select track',
                                          filetypes=[('Audio', '*.mp3')])
        if file:
            self.bind_on_frame_change()
            self.unbind_numbers()
            self.controller.show_frame(IndividualTrackPage, {'filename': file})

    def view_music_files(self):
        self.bind_on_frame_change()
        self.unbind_numbers()
        self.controller.show_frame(MusicFilesPage, {'directory': music_directory})

    def search_for_album_covers(self):
        self.bind_on_frame_change()
        self.unbind_numbers()
        self.controller.show_frame(AlbumCoverSearcher)

    def unbind_numbers(self):
        for i in range(1, 6): self.controller.unbind(str(i))

    def bindings(self):
        self.controller.bind('1', lambda _: self.change_directory())
        self.controller.bind('2', lambda _: self.set_missing_metadata())
        self.controller.bind('3', lambda _: self.select_individual_track())
        self.controller.bind('4', lambda _: self.view_music_files())
        self.controller.bind('5', lambda _: self.search_for_album_covers())
        self.controller.bind('<Escape>', lambda _: self.quit())
        self.controller.bind('<q>', lambda _: self.quit())
        self.controller.bind('<Q>', lambda _: self.quit())
        self.controller.unbind('<Return>')

    def bind_on_frame_change(self):
        self.controller.bind('<Escape>', lambda _: self.controller.show_frame(StartPage))
        self.controller.bind('<Alt-Left>', lambda _: self.controller.show_frame(StartPage))

    def tkraise(self, above_this=None):
        self.bindings()
        return super().tkraise(aboveThis=above_this)


class MusicFilesPage(tk.Frame):

    def __init__(self, parent, controller, kwargs):
        tk.Frame.__init__(self, parent, width=200, height=400, bg='#141414')
        # controller.geometry(f'{controller.winfo_width()}x250')
        self.old_w, self.old_h = self.winfo_reqwidth(), self.winfo_reqheight()
        self.controller = controller
        self.directory = kwargs['directory']

        controller.geometry(f'{app.winfo_screenwidth() // 3}x{app.winfo_screenheight() // 3}')
        center(controller)

        top_stuff = tk.Frame(self, bg='#141414')
        top_stuff.pack(side=tk.TOP, pady=20)
        for i in range(1, 10): top_stuff.columnconfigure(i, minsize=60)

        button1 = tk.Button(self, text='Back', bg=bbg, activebackground=babg,
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(in_=top_stuff, row=0, column=0)

        label = tk.Label(self, text='Music files', font=LARGE_FONT, bg='#141414', fg='white')
        label.grid(in_=top_stuff, row=0, column=5)

        self.files = glob(f'{self.directory}/*.mp3')

        listbox_height = int(app.winfo_screenheight() * 0.0133)
        self.listbox = Listbox(self, width=200, height=listbox_height, bg='#141414', fg='white')
        self.listbox.pack()
        self.listbox.focus()
        for file in self.files:
            self.listbox.insert(tk.END, os.path.basename(file))

        button2 = tk.Button(self, text='Select File', bg=bbg, activebackground=babg,
                            command=self.select_individual_track)
        button2.pack(pady=20)

        controller.bind('<Return>', lambda _: self.select_individual_track())

    def select_individual_track(self):
        with suppress(IndexError):
            file = self.files[self.listbox.curselection()[0]]
            self.controller.bind('<Escape>',
                                 lambda _: self.controller.show_frame(MusicFilesPage, {'directory': self.directory}))
            self.controller.bind('<Alt-Left>',
                                 lambda _: self.controller.show_frame(MusicFilesPage, {'directory': self.directory}))
            if file: self.controller.show_frame(IndividualTrackPage, {'filename': file, 'previous_page': MusicFilesPage,
                                                                      'directory': self.directory})

    def resize(self):
        self.controller.geometry(f'{self.old_w}x{self.old_h}')


class IndividualTrackPage(tk.Frame):

    def __init__(self, parent, controller, kwargs):
        tk.Frame.__init__(self, parent, bg='#141414')
        self.filename = kwargs['filename']
        self.previous_page = kwargs.get('previous_page', StartPage)
        self.controller = controller
        self.old_w, self.old_h = self.controller.winfo_width(), self.controller.winfo_height()
        # controller.geometry(f'{self.old_w}x{int(self.old_h * 2)}')
        controller.geometry(f'{int(self.old_w * 1.1)}x{int(app.winfo_screenheight() / 1.8)}')
        center(controller)
        self.kwargs = kwargs
        try:
            self.audio = EasyID3(self.filename)
        except mutagen.id3.ID3NoHeaderError:
            self.audio = mutagen.File(self.filename, easy=True)
            self.audio.add_tags()
            self.audio = EasyID3(self.filename)

        top_stuff = tk.Frame(self, bg='#141414')
        top_stuff.pack(side=tk.TOP, pady=20)
        label_text = os.path.basename(self.filename)
        for i in range(1, 10): top_stuff.columnconfigure(i, minsize=75 - len(label_text))
        label = tk.Label(self, text=label_text, font=LARGE_FONT, bg='#141414', fg='white',
                         highlightbackground='#303030', highlightcolor='blue')
        label.grid(in_=top_stuff, row=0, column=5)
        # label.pack(pady=20, padx=10)
        button1 = tk.Button(self, text='Back', bg=bbg, activebackground=babg, command=self.back)
        # button1.pack(pady=10, padx=10)
        button1.grid(in_=top_stuff, row=0, column=0)

        info = tk.Frame(self, bg='#141414')
        buttons = tk.Frame(self, bg='#141414')

        # info.pack(side=tk.LEFT)
        # buttons.pack(side=tk.RIGHT)

        button2 = tk.Button(self, text='Auto-set metadata and album cover', bg=bbg, activebackground=babg,
                            command=self.auto_set_metadata)
        button2.pack(pady=10, padx=10)
        # button2.pack(in_=buttons, pady=10, padx=10)
        tk.Label(self, text='', bg=bbg).pack(in_=info, pady=10, padx=10)

        button3 = tk.Button(self, text='Auto-set (override) artist and title', bg=bbg, activebackground=babg,
                            command=lambda: self.auto_set_metadata(True))
        button3.pack(pady=10, padx=10)

        button4 = tk.Button(self, text='Set artist(s) (comma separated)', bg=bbg, activebackground=babg,
                            command=self.set_artists)
        button4.pack(pady=10, padx=10)

        button5 = tk.Button(self, text='Set title', bg=bbg, activebackground=babg, command=self.set_title)
        button5.pack(pady=10, padx=10)

        button6 = tk.Button(self, text='Set album', bg=bbg, activebackground=babg, command=self.set_album)
        button6.pack(pady=10, padx=10)

        button7 = tk.Button(self, text='Set album artist', bg=bbg, activebackground=babg, command=self.set_album_artist)
        button7.pack(pady=10, padx=10)

        # put a combobox to the left of this; (auto, url, local image, from another file, manual search)
        button8 = tk.Button(self, text='Set album cover', bg=bbg, activebackground=babg, command=self.set_album_cover)
        button8.pack(pady=10, padx=10)

        button9 = tk.Button(self, text='Set genre', bg=bbg, activebackground=babg, command=self.set_genre)
        button9.pack(pady=10, padx=10)

        button10 = tk.Button(self, text='Set year', bg=bbg, activebackground=babg, command=self.set_year)
        button10.pack(pady=10, padx=10)

        button11 = tk.Button(self, text='Rename File', bg=bbg, activebackground=babg, command=self.rename_file)
        button11.pack(pady=10, padx=10)

        button12 = tk.Button(self, text='Trim audio (seconds)', bg=bbg, activebackground=babg, command=self.trim_audio)
        button12.pack(pady=10, padx=10)

        button13 = tk.Button(self, text='View album covers', bg=bbg, activebackground=babg,
                             command=self.view_album_covers)
        button13.pack(pady=10, padx=10)

        self.controller.bind('1', lambda _: self.auto_set_metadata())
        self.controller.bind('2', lambda _: self.auto_set_metadata(True))
        self.controller.bind('3', lambda _: self.set_title())
        self.controller.bind('4', lambda _: self.set_artists())
        self.controller.bind('5', lambda _: self.set_album())
        self.controller.bind('6', lambda _: self.set_album_artist())
        self.controller.bind('7', lambda _: self.set_album_cover())
        self.controller.bind('8', lambda _: self.set_genre())
        self.controller.bind('9', lambda _: self.set_album())
        self.controller.bind('y', lambda _: self.set_year())
        self.controller.bind('Y', lambda _: self.set_year())
        self.controller.bind('r', lambda _: self.rename_file())
        self.controller.bind('R', lambda _: self.rename_file())
        self.controller.bind('t', lambda _: self.trim_audio())
        self.controller.bind('T', lambda _: self.trim_audio())
        self.controller.bind('v', lambda _: self.view_album_covers())
        self.controller.bind('V', lambda _: self.view_album_covers())

        # have all the properties beside the options

    def auto_set_metadata(self, override=False):
        temp = add_simple_metadata(self.filename, override=override)
        toaster.show_toast('Metadata Setter', f'Metadata set {"with errors" if temp else ""}', duration=3, threaded=True)

    def set_title(self):
        pass
        # new_title = self.pop_up(('Enter title',))[0]
        # if 'Enter title' not in new_title: set_title(self.audio, new_title)

    def set_artists(self):
        pass
        # new_artists = self.pop_up(('Enter artists',))[0].split(', ')
        # if 'Enter artists' not in new_artists: set_artists(self.audio, new_artists)

    def set_album(self):
        pass
        # new_album = self.pop_up(('Enter album',))[0]
        # if 'Enter album' not in new_album: set_album(self.audio, new_album)

    def set_album_artist(self):
        pass

    def set_album_cover(self):
        pass

    def set_genre(self):
        pass

    def set_year(self):
        pass

    def rename_file(self):
        pass

    def trim_audio(self):
        pass

    def remove_silence(self):
        pass

    def view_album_covers(self):
        self.controller.withdraw()
        audio_mp3 = MP3(self.filename)
        covers = [audio_mp3[key].data for key in audio_mp3.keys() if key.startswith('APIC')]
        image_selector.main(image_bits=covers)
        self.controller.deiconify()

    def back(self):
        if self.previous_page == StartPage:
            self.controller.show_frame(self.previous_page)
        else:
            self.controller.show_frame(self.previous_page, self.kwargs)
        self.controller.geometry(f'{self.old_w}x{self.old_h}')
        center(self.controller)

    def pop_up(self, entries):
        pop_up_window = PopUpWindow(self.controller, entries)
        pop_up_window.top.transient(self)
        self.controller.wm_attributes('-disabled', True)
        self.controller.wait_window(pop_up_window.top)
        self.controller.wm_attributes('-disabled', False)
        self.controller.lift()
        print(pop_up_window.entries)
        return [entry.get() for entry in pop_up_window.entries]


class AlbumCoverSearcher(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#141414')
        self.controller = controller

        top_stuff = tk.Frame(self, bg='#141414')
        top_stuff.pack(side=tk.TOP, pady=20)

        button1 = tk.Button(self, text='Back', bg=bbg, activebackground=babg,
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(in_=top_stuff, side=tk.LEFT)

        label1 = Label(self, text='Search For Album Cover', bg='#141414', fg='white', font=LARGE_FONT)
        label1.pack(in_=top_stuff, side=tk.RIGHT, padx=90)

        search_stuff = tk.Frame(self, bg='#141414')
        search_stuff.pack(side=tk.TOP)

        self.artist_variable = tk.StringVar(value='Artist name')
        artist_entry = tk.Entry(self, textvariable=self.artist_variable)
        artist_entry.pack(in_=search_stuff, side=tk.LEFT, padx=30)

        self.track_variable = tk.StringVar(value='Track name')
        track_entry = tk.Entry(self, textvariable=self.track_variable)
        track_entry.pack(in_=search_stuff, side=tk.LEFT, padx=30)

        button2 = tk.Button(self, text='Search!', bg=bbg, activebackground=babg, command=self.search_art)
        button2.pack(in_=search_stuff, side=tk.RIGHT)

        self.label2 = Label(self, text='', bg='#141414', fg='white', font=('Verdana', 10))
        self.label2.pack()

        controller.bind('<Return>', lambda _: self.search_art())
        artist_entry.focus()

    def search_art(self):
        search_title = self.track_variable.get()
        search_artist = self.artist_variable.get()
        results = search_album_art(search_artist, search_title, return_all=True)
        if results:
            self.controller.withdraw()
            image_selector.main(results, artist=search_artist, track=search_title)
            self.controller.deiconify()
            url = os.environ.pop('SELECTED_URL', None)
            if url:
                if copy(url):
                    self.label2.configure(text='URL copied to clipboard!')
                else:
                    self.label2.configure(text=url)
        else:
            self.label2.configure(text='No album cover found :(')


if __name__ == '__main__':
    app = MainGUI()
    app.geometry(f'{app.winfo_screenwidth() // 3}x{app.winfo_screenheight() // 3}')
    center(app)
    # style = Style()
    # style.configure('TButton', background='#141414')
    app.mainloop()
