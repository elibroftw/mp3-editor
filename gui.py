import tkinter as tk


def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2 - 100
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


window = tk.Tk()
window.wm_title('ID3 Editor')
window.wm_minsize(450, 100)

# window.rowconfigure(4, {'minsize': 25})
center(window)
window.mainloop()

