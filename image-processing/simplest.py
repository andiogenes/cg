import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import sys

BUTTON_WIDTH = 40

root = tk.Tk()
root.title("Лабораторная работа №5")


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


def lum(p):
    """
    :param p кортеж трёх чисел
    :return: Яркость пикселя p
    """
    return 0.299 * p[0] + 0.5876 * p[1] + 0.114 * p[2]


def create_hist(image):
    """
    Строит гистограмму яркости изображения.
    """
    values = [0 for _ in range(256)]
    colors = image.getcolors(image.size[0] * image.size[1])

    for (n, c) in colors:
        idx = int(lum(c))
        values[idx] += n

    return values


def draw_hist(values, w=800, h=600):
    """
    Создаёт изображение гистограммы hist.
    """
    _hist = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(_hist)

    max_v = max(values)
    bar_w = w / 256

    if max_v != 0:
        for (i, v) in enumerate(values):
            draw.rectangle((bar_w * i, h - (v / max_v) * h, bar_w * (i + 1), h), fill='black')

    del draw

    return _hist


def grayscale(image):
    """
    Приводит изображение image к оттенкам серого.
    """
    temp = image.copy()
    w, h = temp.size

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            v = int(lum(pixels[x, y]))
            pixels[x, y] = (v, v, v)

    del pixels
    return temp


def negative(image):
    """
    Создает негатив изображения image.
    """
    temp = image.copy()
    w, h = temp.size

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            r, g, b = pixels[x, y]
            pixels[x, y] = (255 - r, 255 - g, 255 - b)

    del pixels
    return temp


def luminosity(image, value):
    """
    Увеличивает/уменьшает яркость изображения image на value.
    """
    temp = image.copy()
    w, h = temp.size

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            r, g, b = pixels[x, y]
            pixels[x, y] = (max(0, min((r + value), 255)),
                            max(0, min((g + value), 255)),
                            max(0, min((b + value), 255)))

    del pixels
    return temp


def contrast(image, value):
    """
    Увеличивает/уменьшает контрастность изображения image в k раз, где k = (value + 255) / 255.
    """
    temp = image.copy()
    w, h = temp.size
    wh = w * h
    k = (value + 255) / 255

    pixels = temp.load()

    r_avg = 0
    g_avg = 0
    b_avg = 0

    for x in range(w):
        for y in range(h):
            r, g, b = pixels[x, y]
            r_avg += r
            g_avg += g
            b_avg += b

    r_avg /= wh
    g_avg /= wh
    b_avg /= wh

    for x in range(w):
        for y in range(h):
            r, g, b = pixels[x, y]
            pixels[x, y] = (int(max(0, min(k * (r - r_avg) + r_avg, 255))),
                            int(max(0, min(k * (g - g_avg) + g_avg, 255))),
                            int(max(0, min(k * (b - b_avg) + b_avg, 255))))

    del pixels
    return temp


def binarization(image, threshold=0.5):
    """
    Приводит изображение image к двум цветам по пороговому значению яркости threshold (от 0.0 до 1.0).
    """
    temp = grayscale(image)
    w, h = temp.size

    pixels = temp.load()

    for x in range(w):
        for y in range(h):
            (v, _, _) = pixels[x, y]
            v /= 255
            v = int(0 if v < threshold else 255)

            pixels[x, y] = (v, v, v)

    del pixels
    return temp


def otsu(image):
    """
    Вычисляет порог бинаризации по методу Оцу и рисует бинаризированное изображение.
    """
    w, h = image.size
    wh = w * h

    hist = create_hist(image)

    intensity = 0
    for (n, c) in image.getcolors(image.size[0] * image.size[1]):
        intensity += int(lum(c)) * n

    best_thresh = 0
    best_sigma = 0.0

    fcpc = 0.0000000001
    fcis = 0.0000000001

    for thresh in range(255):
        fcpc += hist[thresh]
        fcis += thresh * hist[thresh]

        fcp = fcpc / wh
        scp = 1 - fcp

        fcm = fcis / fcpc
        scm = (intensity - fcis) / (wh - fcpc)

        delta = fcm - scm
        sigma = fcp * scp * delta * delta

        if sigma > best_sigma:
            best_sigma = sigma
            best_thresh = thresh

    return new_image_view(binarization(image, best_thresh / 255),
                          title='Бинаризация по Оцу, порог {}%'.format(best_thresh * 100 / 255),
                          reassign=reassign_var.get())


def equalisation(image):
    """
    Выравнивает изображение image по гистограмме.
    """
    hist = create_hist(image)

    def cdf(values, count):
        return sum(values[:count])

    temp = image.copy()
    w, h = temp.size
    wh = w * h

    pixels = temp.load()

    min_cdf = cdf(hist, int(min(map(lambda _v: lum(_v[1]), image.getcolors(image.size[0] * image.size[1])))))
    for x in range(w):
        for y in range(h):
            r, g, b = pixels[x, y]

            v = int(lum((r, g, b)))
            cdf_v = min(255 * (cdf(hist, v) - min_cdf) / wh, 255)

            k = 0 if v == 0 else cdf_v / v

            pixels[x, y] = (min(int(r * k), 255), min(int(g * k), 255), min(int(b * k), 255))

    del pixels

    new_image_view(draw_hist(create_hist(temp)), title='Выровненная гистограмма яркости')

    return temp


reassign_var = tk.BooleanVar()

pil_img = Image
pil_img_bak = Image


def load():
    global pil_img, pil_img_bak

    pil_img = open_image()
    pil_img_bak = pil_img.copy()
    new_image_view(pil_img, title='Исходное изображение')


load()

tk.Button(root, text="Открыть изображение", width=BUTTON_WIDTH,
          command=lambda: load()).pack()
tk.Button(root, text="Построить гистограмму яркости", width=BUTTON_WIDTH,
          command=lambda: new_image_view(draw_hist(create_hist(pil_img)), title='Гистограмма яркости')).pack()

tk.Label(root, text='Δ яркости:').pack()
lum_modifier = tk.Scale(root, from_=-255, to=255, orient=tk.HORIZONTAL)
lum_modifier.pack()

tk.Button(root, text="Преобразование яркости", width=BUTTON_WIDTH,
          command=lambda: new_image_view(luminosity(pil_img, lum_modifier.get()),
                                         title="Преобразование яркости", reassign=reassign_var.get())).pack()

tk.Label(root, text='Δ контрастности:').pack()
cont_modifier = tk.Scale(root, from_=-255, to=255, orient=tk.HORIZONTAL)
cont_modifier.pack()

tk.Button(root, text="Преобразование контрастности", width=BUTTON_WIDTH,
          command=lambda: new_image_view(contrast(pil_img, cont_modifier.get()),
                                         title="Преобразование контрастности", reassign=reassign_var.get())).pack()
tk.Button(root, text="Бинаризация по уровню 50%", width=BUTTON_WIDTH,
          command=lambda: new_image_view(binarization(pil_img), title="Бинаризация по уровню 50%",
                                         reassign=reassign_var.get())).pack()
tk.Button(root, text="Бинаризация по Оцу", width=BUTTON_WIDTH, command=lambda: otsu(pil_img)).pack()
tk.Button(root, text="Переход к оттенкам серого", width=BUTTON_WIDTH,
          command=lambda: new_image_view(grayscale(pil_img), title="Переход к оттенкам серого",
                                         reassign=reassign_var.get())).pack()
tk.Button(root, text="Получение негатива", width=BUTTON_WIDTH,
          command=lambda: new_image_view(negative(pil_img), title="Получение негатива",
                                         reassign=reassign_var.get())).pack()
tk.Button(root, text="Выравнивание гистограммы", width=BUTTON_WIDTH,
          command=lambda: new_image_view(equalisation(pil_img), title="Выравнивание гистограммы")).pack()
tk.Button(root, text="Ресет", width=BUTTON_WIDTH,
          command=lambda: new_image_view(pil_img_bak, title="Исходное изображение", reassign=True)).pack()
tk.Checkbutton(text="Использовать следующее изображение\nкак исходное", variable=reassign_var).pack()

root.lift()

if __name__ == '__main__':
    root.mainloop()
