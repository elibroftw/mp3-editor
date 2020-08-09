from contextlib import suppress
import io
import os
import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog
import webbrowser
import urllib.request

from win10toast import ToastNotifier
from PIL import Image, ImageTk, UnidentifiedImageError
from functions import copy


def center(top_level):
    top_level.update_idletasks()
    w, h = top_level.winfo_screenwidth(), top_level.winfo_screenheight()
    size = tuple(int(_) for _ in top_level.geometry().split('+', 1)[0].split('x'))
    # x = int(w / 2 - size[0] / 2)
    # y = int(h / 2 - size[1] / 2 - 100)
    y = int(h / 2 - top_level.winfo_height() / 2 - 100)
    x = int(w / 2 - top_level.winfo_width() / 2)
    top_level.geometry(f'+{x}+{y}')
    # top_level.geometry('%dx%d+%d+%d' % (size + (x, y)))


current_image_index = 0
toaster = ToastNotifier()

# def display_images(image_bits):
#     images = [Image.open(io.BytesIO(image)) for image in image_bits]


def image_selector(image_urls=None, artist='', track='', image_bits=None, root=None):
    if image_bits is None: image_bits = []
    if image_urls is None: image_urls = []
    global current_image_index
    if root is None:
        root_is_main = True
        root = tk.Tk()
    else:
        root_is_main = False
        root = tk.Toplevel(root)

    root.wm_title('Image Selector')
    current_image_index = 0

    if image_urls: images = image_urls.copy()
    elif image_bits: images = image_bits.copy()
    else:
        print('ERROR: no images to display')
        return
    images_data = {}

    def copy_url():
        copy(image_urls[current_image_index])
        toaster.show_toast('Image Selector', 'Copied image url to clipboard', duration=4, threaded=True)

    def open_browser():
        webbrowser.open_new(image_urls[current_image_index])

    def save_to_device():
        image = images_data[current_image_index]
        with suppress(ValueError):
            filename = filedialog.asksaveasfilename(title='Specify Save filename', initialfile=f'{artist} - {track} - Album art {current_image_index + 1}', filetypes=(('PNG file', '*.png'), ('JPEG file', '*.jpg')), defaultextension='*.*')
            image.save(filename)
            toaster.show_toast('Image Selector', 'Saved image to device', duration=4, threaded=True)
        # 1. get location to save image
        # 2. download image to location

    pop_up = tk.Menu(tearoff=0)  # image right click menu
    pop_up.config(bg='black', fg='#eee', bd=0, activebackground='#242424')
    image_exists_commands = [('Copy URL', copy_url), ('Open in browser', open_browser)]
    right_click_commands = [('Save to device', save_to_device)]
    if image_urls:
        right_click_commands = image_exists_commands + right_click_commands
    for label, cmd in right_click_commands:
        pop_up.add_command(label=label, command=cmd, background='black', font=('Verdana', 10))

    def image_right_click(event):
        pop_up.post(event.x_root, event.y_root)

    def load_image(index):
        image = images[index]
        if type(image) != ImageTk.PhotoImage:
            if image_urls:
                raw_data = urllib.request.urlopen(image).read()
            else:
                raw_data = image
            image = Image.open(io.BytesIO(raw_data))
            images_data[index] = image
            image = image.resize((450, 450), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            images[index] = image
        return image

    image_label = tk.Label(root, image=load_image(0), background='#454545', borderwidth=1)
    image_label.grid(row=1, column=2, sticky=tk.N)
    image_label.bind('<Button-3>', image_right_click)

    def prev_image():
        global current_image_index
        current_image_index -= 1
        number_of_images = len(images)
        if current_image_index < 0: current_image_index = number_of_images - 1
        new_text = f'Image {current_image_index + 1}/{number_of_images}'
        label2.configure(text=new_text)
        image_label.configure(image=load_image(current_image_index))

    def select_image():
        url = image_urls[current_image_index]
        os.environ['SELECTED_URL'] = url
        root.withdraw()
        root.quit()

    def next_image():
        global current_image_index
        current_image_index += 1
        number_of_images = len(images)
        if current_image_index >= number_of_images: current_image_index = 0
        new_text = f'Image {current_image_index + 1}/{number_of_images}'
        label2.configure(text=new_text)
        image_label.configure(image=load_image(current_image_index))

    def on_close():
        root.withdraw()
        root.quit()

    default_font = Font(family='Verdana', size=11)
    bg = '#0EABE0'
    abg = '#68CBED'

    label2 = tk.Label(root, text=f'Image 1/{len(images)}', foreground='white', width=15, font=default_font,
                      borderwidth=0, background='#121212')
    label2.grid(row=1, column=3)

    if track and artist:
        # TODO: make fancier
        artist = artist.replace(', ', ',\n')
        search_label_text = f'TRACK\n{track}\n\nARTIST(S)\n{artist}'
        lft_side_width = max([15] + [len(line) for line in search_label_text.splitlines()])
        search_label = tk.Label(root, text=search_label_text, foreground='white',
                                width=lft_side_width, font=default_font, borderwidth=0,
                                background='#121212')
        search_label.grid(row=1, column=1)
    else: lft_side_width = 15
    tk.Button(root, command=prev_image, text='Previous image', width=lft_side_width, font=default_font, background=bg,
              activebackground=abg, borderwidth=0).grid(row=2, column=1)
    root.bind('<Left>', lambda _: prev_image())
    root.bind('a', lambda _: prev_image())
    root.bind('A', lambda _: prev_image())
    root.bind('s', lambda _: prev_image())
    root.bind('S', lambda _: prev_image())
    root.bind('<Down>', lambda _: prev_image())

    if image_urls:
        tk.Button(root, command=select_image, text='Select', width=15, font=default_font, background=bg,
                activebackground=abg, borderwidth=0).grid(row=2, column=2)
        root.bind('<space>', lambda _: select_image())
        root.bind('<Return>', lambda _: select_image())

    tk.Button(root, command=next_image, text='Next image', width=15, font=default_font, background=bg,
              activebackground=abg, borderwidth=0).grid(row=2, column=3)
    image_label.bind('<Button-1>', lambda _: next_image())
    root.bind('<Right>', lambda _: next_image())
    root.bind('d', lambda _: next_image())
    root.bind('D', lambda _: next_image())
    root.bind('w', lambda _: next_image())
    root.bind('W', lambda _: next_image())
    root.bind('<Up>', lambda _: next_image())

    root.bind('<Escape>', lambda _: on_close())
    root.bind('<q>', lambda _: on_close())
    root.bind('<Q>', lambda _: on_close())

    root.bind('c', lambda _: copy_url())
    root.bind('C', lambda _: copy_url())

    root.configure(background='#121212')
    root.resizable(False, False)
    root.protocol('WM_DELETE_WINDOW', on_close)
    center(root)
    if not root_is_main:
        root.deiconify()
        root.lift()
    root.mainloop()


if __name__ == '__main__':
    # For testing purposes
    sample_urls = [
        'https://i.scdn.co/image/7c138e2d5934d4f52cdd501324c17a24c5c9c2ff',
        'https://i.scdn.co/image/c3dd41f02ef12dd7d516dc9871d723c865ea731d',
        'https://i.scdn.co/image/c3dd41f02ef12dd7d516dc9871d723c865ea731d',
        'https://i.scdn.co/image/22be564ad21aa651260be4b9174bf03140782ffe',
        'https://i.scdn.co/image/a173d8fa19dbdd4f109e56c7c429b5fbca71c397',
        'https://i.scdn.co/image/e22b78f31c106bbec4b61709bd6fa2e393e2eaaf',
        'https://i.scdn.co/image/e22b78f31c106bbec4b61709bd6fa2e393e2eaaf',
    ]
    image_selector(sample_urls, artist='88GLAM', track='Lil Boat (Remix)')
    selected_url = os.environ.pop('SELECTED_URL', None)
    if selected_url: print(selected_url)
