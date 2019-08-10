import tkinter as tk
from tkinter import Label, Button, Listbox
from tkinter import filedialog
from os import chdir
from functions import *
import image_selector
from image_selector import center

LARGE_FONT= ('Verdana', 12)
music_directory = config.get('MUSIC_LOCATION', '')
# bbg = '#4285f4'  # button background
bbg = '#0088ff'
babg = '#00bbff'  # button active background
# TODO: make button text larger
# TODO: indivual select

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
        
        self.show_frame(StartPage)
        self.title('Music Metadata Editor')

    def show_frame(self, cont, kwargs={}):
        if cont not in self.frames:
            if kwargs: frame = cont(self.container, self, kwargs)
            else: frame = cont(self.container, self)
            frame.grid(row=0, column=0, sticky='nsew')
        else:
            frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        global music_directory
        while music_directory == '' or not os.path.exists(music_directory):
            music_directory = filedialog.askdirectory(title='Select Music Directory')
        chdir(music_directory)
        tk.Frame.__init__(self, parent, bg='#141414')
        # label = tk.Label(self, text='Music metadata editor', font=LARGE_FONT)
        # label.pack(pady=10,padx=10)
        self.controller = controller

        self.label1 = Label(self, text=f'Working Directory: {music_directory}', bg='#141414', fg='white', font=LARGE_FONT)
        self.label1.pack(pady=20)

        button1 = Button(self, text=f'Change Directory', bg=bbg, activebackground=babg, command=self.change_directory)
        button1.pack(pady=10)
        self.bind('1', lambda _: self.change_directory())

        button2 = Button(self, text='Autoset metadata for files with missing metadata and album art', bg=bbg, activebackground=babg, command=self.set_missing_metadata)
        button2.pack(pady=10)
        self.bind('2', lambda _: self.set_missing_metadata())

        button3 = Button(self, text='Select an individual track', bg=bbg, activebackground=babg, command=self.select_individual_track)
        button3.pack(pady=10)
        self.bind('3', lambda _: self.select_individual_track())

        button4 = Button(self, text='View music files in directory', bg=bbg, activebackground=babg, command=self.view_music_files)
        button4.pack(pady=10)
        self.bind('4', lambda _: self.view_music_files())

        button5 = Button(self, text='Search for album covers', bg=bbg, activebackground=babg, command=self.search_for_album_covers)
        button5.pack(pady=10)
        self.bind('5', lambda _: self.search_for_album_covers())

        controller.bind('<Escape>', lambda _: self.quit())
        controller.bind('<q>', lambda _: self.quit())
        controller.bind('<Q>', lambda _: self.quit())
        controller.unbind('<Return>')
        self.focus()

    def change_directory(self):
        global music_directory
        old_length = len(music_directory)
        temp_music_directory = filedialog.askdirectory(title='Select Music Directory')
        if os.path.exists(temp_music_directory):
            music_directory = temp_music_directory
            new_length = len(music_directory)
            diff = new_length - old_length
            chdir(music_directory)
            if diff > 0: self.label1.configure(text=f'Working Directory: ...{music_directory[diff:]}')
            else: self.label1.configure(text=f'Working Directory: {music_directory}')

    def set_missing_metadata(self):
        for file in glob('*.mp3'): add_simple_meta(file)
        print('Metadata for all tracks set')

    def select_individual_track(self):
        file = filedialog.askopenfilename(initialdir=f'{music_directory}', title='Select track', filetypes=[('Audio', '*.mp3')])
        if file: self.controller.show_frame(InvidualTrackPage, {'filename': file})

    def view_music_files(self):
        self.controller.show_frame(MusicFilesPage, {'directory': music_directory})

    def search_for_album_covers(self):
        self.controller.show_frame(AlbumCoverSearcher)
    

class MusicFilesPage(tk.Frame):

    def __init__(self, parent, controller, kwargs):
        tk.Frame.__init__(self, parent, width=200, height=400, bg='#141414')
        # controller.geometry(f'{controller.winfo_width()}x250')
        center(controller)
        self.controller = controller
        self.directory = kwargs['directory']
        label = tk.Label(self, text=f'Music files in .../{os.path.basename(self.directory)}', font=LARGE_FONT, bg='#141414', fg='white')
        label.pack(pady=10, padx=10, side=tk.TOP)
        self.files = glob(f'{self.directory}/*.mp3')
        
        buttons = tk.Frame(self, bg='#141414')
        buttons.pack(side=tk.TOP)
        
        button1 = tk.Button(self, text='Back', bg=bbg, activebackground=babg, command=lambda: controller.show_frame(StartPage))
        button1.pack(in_=buttons, side=tk.LEFT, padx=50)
        # blank = tk.Label(self, text='                   ', bg='#141414', activebackground='#141414', highlightbackground='#141414', relief=tk.FLAT, pady=4)
        # blank.pack(in_=buttons, side=tk.LEFT)
        button2 = tk.Button(self, text='Select File', bg=bbg, activebackground=babg, command=self.select_individual_track)
        button2.pack(in_=buttons, side=tk.RIGHT, padx=50)
        # add listbox
        self.listbox = Listbox(self, width=200, bg='#141414', fg='white')
        self.listbox.pack(side=tk.BOTTOM)
        for file in self.files:
            self.listbox.insert(tk.END, os.path.basename(file))

    def select_individual_track(self):
        file = self.files[self.listbox.curselection()[0]]
        self.controller.bind('<Escape>', lambda _: self.controller.show_frame(MusicFilesPage, {'directory': self.directory}))
        if file: self.controller.show_frame(InvidualTrackPage, {'filename': file})


class InvidualTrackPage(tk.Frame):

    def __init__(self, parent, controller, kwargs):
        tk.Frame.__init__(self, parent, bg='#141414')
        self.file = kwargs['filename']
        label = tk.Label(self, text=os.path.basename(self.file), font=LARGE_FONT, bg='#141414', fg='white', highlightbackground='#303030', highlightcolor='blue')
        label.pack(pady=10,padx=10)

        button1 = tk.Button(self, text='Back', bg=bbg, activebackground=babg, command=lambda: controller.show_frame(StartPage))
        button1.pack()

        # button2 = tk.Button(self, text='Page Two', bg=bbg, activebackground=babg, command=None)
        # button2.pack()


class AlbumCoverSearcher(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#141414')
        self.controller = controller
        label1 = Label(self, text='Search For Album Art', bg='#141414', fg='white', font=LARGE_FONT)
        label1.pack()

        top_stuff = tk.Frame(self, bg='#141414')
        top_stuff.pack(side=tk.TOP)

        button1 = tk.Button(self, text='Back', bg=bbg, activebackground=babg, command=lambda: controller.show_frame(StartPage))
        button1.pack(in_=top_stuff, side=tk.LEFT)

        self.artist_variable = tk.StringVar(value='Artist name')
        artist_entry = tk.Entry(self, textvariable=self.artist_variable)
        artist_entry.pack(in_=top_stuff, side=tk.LEFT, padx=30)

        self.track_variable = tk.StringVar(value='Track name')
        track_entry = tk.Entry(self, textvariable=self.track_variable)
        track_entry.pack(in_=top_stuff, side=tk.LEFT, padx=30)

        button2 = tk.Button(self, text='Search!', bg=bbg, activebackground=babg, command=self.search_art)
        button2.pack(in_=top_stuff, side=tk.RIGHT)

        self.label2 = Label(self, text='', bg='#141414', fg='white', font=('Verdana', 10))
        self.label2.pack()
        
        self.bind('<Escape>', lambda _: controller.show_frame(StartPage))
        controller.bind('<Return>', lambda _: self.search_art())
        artist_entry.focus()
    
    def search_art(self):
        search_title = self.track_variable.get()
        search_artist = self.artist_variable.get()
        results = get_album_art(search_artist, search_title, return_all=True)
        if results:
            self.controller.withdraw()
            image_selector.main(results, artist=search_artist, track=search_title)
            self.controller.deiconify()
            url = os.environ.pop('SELECTED_URL', None)
            if url:
                if copy(url):
                    self.label2.configure(text='URL copied to clipboard!')
                else: self.label2.configure(text=url)
        else: self.label2.configure(text='No album art found :(')


app = MainGUI()
center(app)
# style = Style()
# style.configure('TButton', background='#141414')
app.mainloop()