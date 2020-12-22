import math
import tkinter as tk
from functools import reduce
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import random
import sys

BUTTON_WIDTH = 40

root = tk.Tk()
root.title("Лабораторная работа №6")


def open_image():
    """
    Открывает диалоговое окно для выбора изображения и загружает изображение в память.
    :return: открытое изображение
    """
    file_name = filedialog.askopenfilename()
    if not isinstance(file_name, str):
        sys.exit(1)
    return Image.open(file_name).convert('RGB')


def new_image_view(image, title='', reassign=False):
    """
    Создает окно с заданным изображением, заголовком
    и опционально присваивает изображение глобальной
    переменной pil_img.
    """
    global pil_img

    if reassign:
        pil_img = image

    tk_image = ImageTk.PhotoImage(image)

    window = tk.Toplevel(root)
    window.title(title)

    label = tk.Label(window, image=tk_image)
    label.image = tk_image
    label.pack()

    window.lift()

    return window


def noise(image):
    temp = image.copy()
    w, h = temp.size

    pixels = temp.load()

    for _ in range(random.randint(0, w * h / 2)):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        r, g, b = pixels[x, y]
        d = random.randint(-128, 128)
        pixels[x, y] = (max(0, min(r + d, 255)), max(0, min(g + d, 255)), max(0, min(b + d, 255)))

    del pixels
    return temp


def noise_lines(image):
    temp = image.copy()
    w, h = temp.size

    draw = ImageDraw.Draw(temp)

    for _ in range(random.randint(0, 10)):
        x1, x2 = random.randint(0, w - 1), random.randint(0, w - 1)
        y1, y2 = random.randint(0, h - 1), random.randint(0, h - 1)

        draw.line((x1, y1, x2, y2), fill='white', width=1)

    return temp


def noise_circles(image):
    temp = image.copy()
    w, h = temp.size

    draw = ImageDraw.Draw(temp)

    for _ in range(random.randint(0, 10)):
        x1, x2 = random.randint(0, w - 1), random.randint(0, w - 1)
        y1, y2 = random.randint(0, h - 1), random.randint(0, h - 1)

        draw.ellipse((x1, y1, x2, y2), outline='white', width=1)

    return temp


def get_filter_window(pixels, x, y, n, m, w, h):
    """
    Получает окно фильтра для точки (x,y).
    """
    from_x = abs(x - int(n / 2))
    from_y = abs(y - int(m / 2))
    to_x = x + int(n / 2)
    to_y = y + int(m / 2)

    def adjust(v, mx):
        vv = abs(v)
        return max(0, vv if vv < mx else mx - vv - 1)

    return [pixels[adjust(x, w), adjust(y, h)] for x in range(from_x, to_x + 1) for y in range(from_y, to_y + 1)]


def uniform(image, n, m):
    temp = image.copy()
    w, h = temp.size

    aperture = [1 / (n * m) for _ in range(n) for _ in range(m)]

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            kernel = get_filter_window(pixels, x, y, n, m, w, h)
            filtered = reduce(
                lambda acc, v: (min(acc[0] + v[0], 255), min(acc[1] + v[1], 255), min(acc[2] + v[2], 255)),
                map(lambda v: (v[0] * v[1][0], v[0] * v[1][1], v[0] * v[1][2]), zip(aperture, kernel)))
            pixels[x, y] = tuple(map(int, filtered))

    del pixels
    return temp


def gauss(image, n, m):
    temp = image.copy()
    w, h = temp.size

    sigma = 0.8

    aperture = [math.exp(-(_x * _x + _y * _y) / (2 * sigma * sigma)) for _x in
                range(-int(n / 2), int(n / 2) + 1)
                for _y in range(-int(m / 2), int(m / 2) + 1)]
    aperture_sum = sum(aperture)
    aperture = [v / aperture_sum for v in aperture]

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            kernel = get_filter_window(pixels, x, y, n, m, w, h)
            filtered = reduce(
                lambda acc, v: (min(acc[0] + v[0], 255), min(acc[1] + v[1], 255), min(acc[2] + v[2], 255)),
                map(lambda v: (v[0] * v[1][0], v[0] * v[1][1], v[0] * v[1][2]), zip(aperture, kernel)))
            pixels[x, y] = tuple(map(int, filtered))

    del pixels
    return temp


def sharpness(image, n, m, k):
    temp = image.copy()
    w, h = temp.size

    k /= 10

    aperture = [-k / (n * m - 1) for _ in range(n) for _ in range(m)]
    aperture[int(len(aperture) / 2)] = k + 1

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            kernel = get_filter_window(pixels, x, y, n, m, w, h)
            filtered = reduce(
                lambda acc, v: (min(acc[0] + v[0], 255), min(acc[1] + v[1], 255), min(acc[2] + v[2], 255)),
                map(lambda v: (v[0] * v[1][0], v[0] * v[1][1], v[0] * v[1][2]), zip(aperture, kernel)))
            pixels[x, y] = tuple(map(int, filtered))

    del pixels
    return temp


def median(image, n, m):
    temp = image.copy()
    w, h = temp.size

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            kernel = get_filter_window(pixels, x, y, n, m, w, h)
            i = int(len(kernel) / 2)
            r_val = sorted(kernel, key=lambda v: v[0])[i][0]
            g_val = sorted(kernel, key=lambda v: v[0])[i][1]
            b_val = sorted(kernel, key=lambda v: v[0])[i][2]
            pixels[x, y] = (r_val, g_val, b_val)

    del pixels
    return temp


def watercolor(image, n, m):
    return sharpness(median(image, n, m), n, m, 10)


reassign_var = tk.BooleanVar()

pil_img = Image
pil_img_bak = Image


def load():
    global pil_img, pil_img_bak

    pil_img = open_image()
    pil_img_bak = pil_img.copy()
    new_image_view(pil_img, title='Исходное изображение')


load()

tk.Button(root, text="Открыть изображение", width=BUTTON_WIDTH, command=lambda: load()).pack()

tk.Button(root, text="Наложение шума (точки)", width=BUTTON_WIDTH,
          command=lambda: new_image_view(noise(pil_img), title='Наложение шума (точки)',
                                         reassign=reassign_var.get())).pack()

tk.Button(root, text="Наложение шума (линии)", width=BUTTON_WIDTH,
          command=lambda: new_image_view(noise_lines(pil_img), title='Наложение шума (линии)',
                                         reassign=reassign_var.get())).pack()

tk.Button(root, text="Наложение шума (окружности)", width=BUTTON_WIDTH,
          command=lambda: new_image_view(noise_circles(pil_img), title='Наложение шума (окружности)',
                                         reassign=reassign_var.get())).pack()

tk.Label(root, text='n:').pack()
n = tk.Scale(root, from_=1, to=11, tickinterval=2, orient=tk.HORIZONTAL)
n.pack()

tk.Label(root, text='m:').pack()
m = tk.Scale(root, from_=1, to=11, tickinterval=2, orient=tk.HORIZONTAL)
m.pack()

tk.Button(root, text="Равномерный фильтр", width=BUTTON_WIDTH,
          command=lambda: new_image_view(uniform(pil_img, n.get(), m.get()),
                                         title='Равномерный фильтр, апертура {}*{}'.format(n.get(), m.get()),
                                         reassign=reassign_var.get())).pack()

tk.Button(root, text="Фильтр Гаусса", width=BUTTON_WIDTH,
          command=lambda: new_image_view(gauss(pil_img, n.get(), m.get()),
                                         title='Фильтр Гаусса, апертура {}*{}'.format(n.get(), m.get()),
                                         reassign=reassign_var.get())).pack()

tk.Label(root, text='Степень увеличения резкости:').pack()
k = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL)
k.pack()

tk.Button(root, text="Повышение резкости", width=BUTTON_WIDTH,
          command=lambda: new_image_view(sharpness(pil_img, n.get(), m.get(), k.get()),
                                         title='Повышение резкости, апертура {}*{}, k={}'.format(n.get(), m.get(),
                                                                                                 k.get()),
                                         reassign=reassign_var.get())).pack()

tk.Button(root, text="Акварелизация", width=BUTTON_WIDTH,
          command=lambda: new_image_view(watercolor(pil_img, n.get(), m.get()),
                                         title='Акварелизация, апертура {}*{}'.format(n.get(), m.get()),
                                         reassign=reassign_var.get())).pack()

tk.Button(root, text="Ресет", width=BUTTON_WIDTH,
          command=lambda: new_image_view(pil_img_bak, title="Исходное изображение", reassign=True)).pack()
tk.Checkbutton(text="Использовать следующее изображение\nкак исходное", variable=reassign_var).pack()

root.lift()

if __name__ == '__main__':
    root.mainloop()
