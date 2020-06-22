#!/usr/bin/env python

import ctypes
import sdl2.ext
import sdl2.events

import threading
from itertools import tee
from math import sin, cos

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)

MODEL_SOURCE = 'suzanne.obj'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

sdl2.ext.init()
window = sdl2.ext.Window("Афинные преобразования", size=(SCREEN_WIDTH, SCREEN_HEIGHT))
window.show()

window_surface = window.get_surface()


def line(pixels, x0, y0, x1, y1, color):
    """
    Растеризует отрезок [(x0,y0),(x1,y1)] при помощи алгоритма Брезенхема.

    Закрашивает пиксели в цвет color.
    """
    steep = False
    if abs(x0 - x1) < abs(y0 - y1):
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        steep = True

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    derror2 = abs(dy) * 2
    error2 = 0
    y = y0
    for x in range(x0, x1 + 1):
        if steep:
            pixels[x][y] = color
        else:
            pixels[y][x] = color
        error2 += derror2

        if error2 > dx:
            y += 1 if y1 > y0 else -1
            error2 -= dx * 2


def cull(v):
    x, y = v
    return min(max(0, round(x)), SCREEN_WIDTH - 1), min(max(0, round(y)), SCREEN_HEIGHT - 1)


def project(point):
    """
    Проецирует точку (x,y,z) на некоторую картинную плоскость.

    Возвращает пару значений в оконных координатах.
    """
    x, y, z = rotate(rotate(point, -3.14 / 2, 'x'), 3.14 / 2, 'z')

    scale = 250
    offset_x = 400
    offset_y = 300

    return cull((y * scale + offset_x, z * scale + offset_y))


def translate(point, ox, oy, oz):
    """
    Применяет к радиус-вектору R(x, y, z) матрицу переноса с заданными параметрами.

    Возвращает вектор (x+ox, y+oy, z+oz).
    """
    x, y, z = point
    return x + ox, y + oy, z + oz


def scale(point, sx, sy, sz):
    """
    Применяет к радиус-вектору R(x, y, z) матрицу масштабирования с заданными параметрами.

    Возвращает вектор (x*sx, y*sy, z*sz).
    """
    x, y, z = point
    return x * sx, y * sy, z * sz


def mirror(point, direction):
    """
    Применяет к радиус-вектору R(x, y, z) матрицу отражения с заданными параметрами.

    Возможные значения direction:
    * xy - отражение относительно плоскости XY
    * yz - отражение относительно плоскости YZ
    * xz - отражение относительно плоскости XZ

    Возвращает отраженный вектор.
    """
    sx, sy, sz = 1, 1, 1

    if direction == "xy":
        sz = -1
    elif direction == "yz":
        sx = -1
    elif direction == "xz":
        sy = -1

    return scale(point, sx, sy, sz)


def rotate(point, angle, direction):
    """
    Применяет к радиус-вектору R(x, y, z) матрицу поворота с заданными параметрами.

    Возможные значения direction:
    * x - производит вращения относительно оси OX.
    * y - производит вращения относительно оси OY.
    * z - производит вращения относительно оси OZ.

    Возвращает повернутый на угол angle вектор.
    """
    x, y, z = point

    if direction == "x":
        return x, y * cos(angle) - z * sin(angle), y * sin(angle) + z * cos(angle)
    elif direction == "y":
        return x * cos(angle) + z * sin(angle), y, -x * sin(angle) + z * cos(angle)
    elif direction == "z":
        return x * cos(angle) - y * sin(angle), x * sin(angle) + y * cos(angle), z

    return point


vertices = []  # Список координат вершин 3D-объекта
surfaces = []  # Список вершин поверхностей, составляющих 3D-объект

# Парсинг 3D-модели из файла
with open(MODEL_SOURCE) as f:
    for ll in f.readlines():
        d = ll.split(' ')
        if d[0] == 'v':
            vertices.append((float(d[1]), float(d[2]), float(d[3])))
        elif d[0] == 'f':
            surface = tuple(map(lambda v: int(v.split('/')[0]), d[1:]))
            surfaces.append(surface)

# Последовательность преобразований пространства
transformations = [lambda v: v]


def draw():
    """
    Отрисовка модели
    """

    # Очистка буффера
    sdl2.ext.fill(window_surface, BLACK)

    pixels = sdl2.ext.PixelView(window_surface)

    for s in surfaces:
        a, b = tee(s)
        next(b, None)
        for e in zip(a, b):
            e1 = vertices[e[0] - 1]
            e2 = vertices[e[1] - 1]
            for t in transformations:
                e1 = t(e1)
                e2 = t(e2)

            x1, y1 = project(e1)
            x2, y2 = project(e2)

            line(pixels, x1, y1, x2, y2, WHITE)

    del pixels


def repl():
    """
    Запуск интерактивного ввода.
    """
    lock = threading.Lock()

    while True:
        command, *args = input('> ').split()

        if command == 'quit' or command == 'q':
            # Посылает сигнал для завершения потока окна и текущего потока.
            with lock:
                e = (sdl2.events.SDL_Event * 1)()
                e[0].type = sdl2.SDL_QUIT
                sdl2.events.SDL_PushEvent(ctypes.cast(e, ctypes.POINTER(sdl2.events.SDL_Event)))
            break
        elif command == 'translate' or command == 't':
            ox, oy, oz = map(lambda v: 0. if v == '_' else float(v), args[:3])
            transformations.append(lambda v: translate(v, ox, oy, oz))

        elif command == 'scale' or command == 's':
            sx, sy, sz = map(lambda v: 1. if v == '_' else float(v), args[:3])
            transformations.append(lambda v: scale(v, sx, sy, sz))

        elif command == 'rotate' or command == 'r':
            angle = float(args[0])
            direction = args[1]
            transformations.append(lambda v: rotate(v, angle, direction))

        elif command == 'mirror' or command == 'm':
            transformations.append(lambda v: mirror(v, args[0]))

        with lock:
            draw()


# Первичная отрисовка модели
draw()

# Создание и запуск потока интерактивного ввода
repl_thread = threading.Thread(target=repl)
repl_thread.start()

# Петля событий SDL
running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
    window.refresh()

sdl2.ext.quit()
