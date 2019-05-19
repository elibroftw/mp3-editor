import io
import tkinter as tk
import urllib.request
import os

from PIL import Image, ImageTk


def center(top_level):
    top_level.update_idletasks()
    w = top_level.winfo_screenwidth()
    h = top_level.winfo_screenheight()
    size = tuple(int(_) for _ in top_level.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2 - 100
    # noinspection PyStringFormat
    top_level.geometry("%dx%d+%d+%d" % (size + (x, y)))


# https://stackoverflow.com/questions/38173526/displaying-images-from-url-in-tkinter#
current_image_index = 0


def main(image_urls):
    global current_image_index
    root = tk.Tk()
    root.wm_title('Image selector')
    images = {}
    current_image_index = 0
    images = image_urls.copy()

    def load_image(index):
        image = images[index]
        if type(image) != ImageTk.PhotoImage:
            raw_data = urllib.request.urlopen(image).read()
            image = Image.open(io.BytesIO(raw_data))
            image = image.resize((450, 450), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            images[0] = image
        return image

    label = tk.Label(root, image=load_image(0))
    label.grid(row=1, column=2, sticky='w')

    def prev_image():
        global current_image_index
        current_image_index -= 1
        if current_image_index < 0: current_image_index = len(images) - 1
        label.configure(image=load_image(current_image_index))

    def select_image():
        url = image_urls[current_image_index]
        os.environ['SELECTED_URL'] = url
        root.destroy()

    def next_image():
        global current_image_index
        current_image_index += 1
        if current_image_index >= len(images) - 1: current_image_index = 0
        label.configure(image=load_image(current_image_index))

    # TODO: make it look nicer
    # TODO: dark background
    tk.Button(command=prev_image, text='Previous image', width=15).grid(row=2, column=1)
    tk.Button(command=select_image, text='Select image', width=15).grid(row=2, column=2)
    tk.Button(command=next_image, text='Next image', width=15).grid(row=2, column=3)

    root.wm_minsize(450, 300)
    root.resizable(False, False)
    center(root)
    root.mainloop()


if __name__ == '__main__':

    sample_urls = [
        'https://i.scdn.co/image/7c138e2d5934d4f52cdd501324c17a24c5c9c2ff',
        'https://i.scdn.co/image/c3dd41f02ef12dd7d516dc9871d723c865ea731d',
        'https://i.scdn.co/image/c3dd41f02ef12dd7d516dc9871d723c865ea731d',
        'https://i.scdn.co/image/22be564ad21aa651260be4b9174bf03140782ffe',
        'https://i.scdn.co/image/a173d8fa19dbdd4f109e56c7c429b5fbca71c397',
        'https://i.scdn.co/image/e22b78f31c106bbec4b61709bd6fa2e393e2eaaf',
        'https://i.scdn.co/image/e22b78f31c106bbec4b61709bd6fa2e393e2eaaf',
    ]
    main(sample_urls)
    selected_url = os.environ.pop('SELECTED_URL', None)
    if selected_url: print(selected_url)
