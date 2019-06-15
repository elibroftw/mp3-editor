import io
import os
import tkinter as tk
from tkinter.font import Font
import urllib.request
import webbrowser

from win10toast import ToastNotifier
from PIL import Image, ImageTk

from functions import copy


def center(top_level):
    top_level.update_idletasks()
    w = top_level.winfo_screenwidth()
    h = top_level.winfo_screenheight()
    size = tuple(int(_) for _ in top_level.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2 - 100
    # noinspection PyStringFormat
    top_level.geometry('%dx%d+%d+%d' % (size + (x, y)))


current_image_index = 0
toaster = ToastNotifier()


def main(image_urls, artist='Placeholder', track='Placeholder'):
    global current_image_index
    if __name__ == "__main__":
        root = tk.Tk()
    else:
        root = tk.Toplevel()
        root.geometry('800x480')
        root.deiconify()

    root.wm_title('Image selector')
    images = {}
    current_image_index = 0
    images = image_urls.copy()

    def copy_url():
        copy(image_urls[current_image_index])
        toaster.show_toast('Image Selector', 'Copied image url to clipboard', duration=4, threaded=True)

    def open_browser():
        webbrowser.open_new(image_urls[current_image_index])

    def save_to_device():
        raise NotImplementedError
        # 1. get location to save image
        # 2. download image to location

    pop_up = tk.Menu(tearoff=0)  # image right click menu
    pop_up.add_command(label='Copy URL', command=copy_url)
    pop_up.add_command(label='Open in browser', command=open_browser)
    # pop_up.add_command(label='Save to device', command=save_to_device)

    def image_right_click(event):
        pop_up.post(event.x_root, event.y_root)

    def load_image(index):
        image = images[index]
        if type(image) != ImageTk.PhotoImage:
            raw_data = urllib.request.urlopen(image).read()
            image = Image.open(io.BytesIO(raw_data))
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
        if current_image_index < 0: current_image_index = len(images) - 1
        new_text = f'Image {current_image_index + 1}/{len(image_urls)}'
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
        if current_image_index >= len(images): current_image_index = 0
        new_text = f'Image {current_image_index + 1}/{len(image_urls)}'
        label2.configure(text=new_text)
        image_label.configure(image=load_image(current_image_index))

    def on_close():
        root.withdraw()
        root.quit()

    button_font = Font(family='Verdana', size=11)
    bg = '#0EABE0'
    abg = '#68CBED'

    label2 = tk.Label(root, text=f'Image 1/{len(image_urls)}', foreground='white', width=15, font=button_font,
                      borderwidth=0, background='#121212')
    label2.grid(row=1, column=3)

    search_label = tk.Label(root, text=f'TRACK\n{track}\n\nARTIST\n{artist}', foreground='white',
                            width=max(len(track), len(artist), 15), font=button_font, borderwidth=0,
                            background='#121212')
    search_label.grid(row=1, column=1)

    tk.Button(root, command=prev_image, text='Previous image', width=15, font=button_font, background=bg,
              activebackground=abg, borderwidth=0).grid(row=2, column=1)
    root.bind('<Left>', lambda _: prev_image())
    root.bind('a', lambda _: prev_image())
    root.bind('A', lambda _: prev_image())
    root.bind('s', lambda _: prev_image())
    root.bind('S', lambda _: prev_image())
    root.bind('<Down>', lambda _: prev_image())

    tk.Button(root, command=select_image, text='Select', width=15, font=button_font, background=bg,
              activebackground=abg, borderwidth=0).grid(row=2, column=2)
    root.bind('<space>', lambda _: select_image())
    root.bind('<Return>', lambda _: select_image())

    tk.Button(root, command=next_image, text='Next image', width=15, font=button_font, background=bg,
              activebackground=abg, borderwidth=0).grid(row=2, column=3)
    image_label.bind('<Button-1>', lambda _: next_image())
    root.bind('<Right>', lambda _: next_image())
    root.bind('d', lambda _: next_image())
    root.bind('D', lambda _: next_image())
    root.bind('w', lambda _: next_image())
    root.bind('W', lambda _: next_image())
    root.bind('<Up>', lambda _: next_image())

    root.bind('<Escape>', lambda _: on_close())
    root.bind('c', lambda _: copy_url())
    root.bind('C', lambda _: copy_url())

    root.configure(background='#121212')
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)
    center(root)
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
    main(sample_urls, artist='88GLAM', track='Lil Boat (Remix)')
    selected_url = os.environ.pop('SELECTED_URL', None)
    if selected_url: print(selected_url)
