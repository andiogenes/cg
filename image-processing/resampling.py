from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import sys


def open_image():
    """
    Открывает диалоговое окно для выбора изображения и загружает изображение в память.
    :return: открытое изображение
    """
    file_name = filedialog.askopenfilename()
    if not isinstance(file_name, str):
        sys.exit(1)
    return Image.open(file_name).convert('RGB')


def nearest_neighbour(original, size):
    """
    Масштабирует изображение при помощи метода ближайшего соседа.
    """
    temp = Image.new("RGB", size, "white")
    w, h = size
    ow, oh = original.size

    sx, sy = (ow - 1) / w, (oh - 1) / h

    o_pix = original.load()
    t_pix = temp.load()

    for x in range(w):
        for y in range(h):
            x1 = round(sx * x)
            y1 = round(sy * y)
            t_pix[x, y] = o_pix[x1, y1]

    del o_pix, t_pix
    return temp


def bilinear_interpolation(original, size):
    """
    Масштабирует изображение при помощи метода билинейной интерполяции.
    """

    def lerp(s, e, t):
        return s + (e - s) * t

    def blerp(c00, c10, c01, c11, tx, ty):
        return lerp(lerp(c00, c10, tx), lerp(c01, c11, tx), ty)

    temp = Image.new("RGB", size, "white")
    w, h = size
    ow, oh = original.size

    sx, sy = (ow - 1) / w, (oh - 1) / h

    o_pix = original.load()
    t_pix = temp.load()

    for x in range(w):
        for y in range(h):
            gx = sx * x
            gy = sy * y

            gxi = int(gx)
            gyi = int(gy)

            c00 = o_pix[gxi, gyi]
            c10 = o_pix[gxi + 1, gyi]
            c01 = o_pix[gxi, gyi + 1]
            c11 = o_pix[gxi + 1, gyi + 1]

            rgb = [0, 0, 0]

            for i in range(3):
                b00, b10, b01, b11 = c00[i], c10[i], c01[i], c11[i]
                ble = blerp(b00, b10, b01, b11, gx - gxi, gy - gyi)
                rgb[i] = ble

            t_pix[x, y] = (int(rgb[0]), int(rgb[1]), int(rgb[2]))

    del o_pix, t_pix
    return temp


def new_image_view(image, title=''):
    """
    Создает окно с заданным изображением, заголовком
    и опционально присваивает изображение глобальной
    переменной pil_img.
    """
    tk_image = ImageTk.PhotoImage(image)

    window = tk.Toplevel(root)
    window.title(title)

    label = tk.Label(window, image=tk_image)
    label.image = tk_image
    label.pack()

    window.lift()

    return window


if __name__ == '__main__':
    WIDGET_WIDTH = 30

    root = tk.Tk()
    root.title("Лабораторная работа №7")

    img = Image

    width_var = tk.StringVar()
    height_var = tk.StringVar()

    label = tk.Label(root)
    label.pack()


    def load_img():
        global img
        img = open_image()
        if label:
            label.config(text='Размер изображения: {}'.format(img.size))
        width_var.set(img.size[0])
        height_var.set(img.size[1])

        new_image_view(img, title='Original')


    def get_size():
        return int(w_field.get()), int(h_field.get())


    load_img()

    tk.Button(root, text='Открыть изображение', width=WIDGET_WIDTH, command=lambda: load_img()).pack()

    tk.Label(root, text='Новая ширина:').pack()
    w_field = tk.Entry(root, textvariable=width_var)
    w_field.pack()

    tk.Label(root, text='Новая высота:').pack()
    h_field = tk.Entry(root, textvariable=height_var)
    h_field.pack()

    tk.Button(root, text='Nearest neighbour', width=WIDGET_WIDTH,
              command=lambda: new_image_view(nearest_neighbour(img, get_size()), title='Nearest neighbour')).pack()
    tk.Button(root, text='Bilinear interpolation', width=WIDGET_WIDTH,
              command=lambda: new_image_view(
                  bilinear_interpolation(img, get_size()), title='Bilinear interpolation')).pack()

    root.mainloop()
