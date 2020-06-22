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


def translation(ox, oy, oz):
    """
    Строит матрицу переноса точки в направлении (ox, oy, oz).
    """
    return [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        ox, oy, oz, 1
    ]


def scale(sx, sy, sz):
    """
    Строит матрицу масштабирования координат с коэфициентами масштабирования (sx, sy, sz).
    """
    return [
        sx, 0, 0, 0,
        0, sy, 0, 0,
        0, 0, sz, 0,
        0, 0, 0, 1
    ]


def mirror(mirror_surface):
    """
    Строит матрицу отражения точки относительно некоторой плоскости mirror_surface.

    Возможные значения mirror_surface:
    * xy - отражение относительно плоскости XY
    * yz - отражение относительно плоскости YZ
    * xz - отражение относительно плоскости XZ
    """
    sx, sy, sz = 1, 1, 1

    if mirror_surface == "xy":
        sz = -1
    elif mirror_surface == "yz":
        sx = -1
    elif mirror_surface == "xz":
        sy = -1

    return scale(sx, sy, sz)


def rotation(angle, axis):
    """
    Строит матрицу поворота на угол angle относительно оси axis.

    Возможные значения axis:
    * x - производит вращения относительно оси OX.
    * y - производит вращения относительно оси OY.
    * z - производит вращения относительно оси OZ.
    """
    if axis == "x":
        return [
            1, 0, 0, 0,
            0, cos(angle), sin(angle), 0,
            0, -sin(angle), cos(angle), 0,
            0, 0, 0, 1
        ]
    elif axis == "y":
        return [
            cos(angle), 0, -sin(angle), 0,
            0, 1, 0, 0,
            sin(angle), 0, cos(angle), 0,
            0, 0, 0, 1
        ]
    elif axis == "z":
        return [
            cos(angle), sin(angle), 0, 0,
            -sin(angle), cos(angle), 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]

    return [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]


def mm(m1, m2):
    """
    Вычисляет произведение матриц m1 x m2 в однородной системе координат (x, y, z, w)
    """
    return [
        m1[0] * m2[0] + m1[1] * m2[4] + m1[2] * m2[8] + m1[3] * m2[12],
        m1[0] * m2[1] + m1[1] * m2[5] + m1[2] * m2[9] + m1[3] * m2[13],
        m1[0] * m2[2] + m1[1] * m2[6] + m1[2] * m2[10] + m1[3] * m2[14],
        m1[0] * m2[3] + m1[1] * m2[7] + m1[2] * m2[11] + m1[3] * m2[15],

        m1[4] * m2[0] + m1[5] * m2[4] + m1[6] * m2[8] + m1[7] * m2[12],
        m1[4] * m2[1] + m1[5] * m2[5] + m1[6] * m2[9] + m1[7] * m2[13],
        m1[4] * m2[2] + m1[5] * m2[6] + m1[6] * m2[10] + m1[7] * m2[14],
        m1[4] * m2[3] + m1[5] * m2[7] + m1[6] * m2[11] + m1[7] * m2[15],

        m1[8] * m2[0] + m1[9] * m2[4] + m1[10] * m2[8] + m1[11] * m2[12],
        m1[8] * m2[1] + m1[9] * m2[5] + m1[10] * m2[9] + m1[11] * m2[13],
        m1[8] * m2[2] + m1[9] * m2[6] + m1[10] * m2[10] + m1[11] * m2[14],
        m1[8] * m2[3] + m1[9] * m2[7] + m1[10] * m2[11] + m1[11] * m2[15],

        m1[12] * m2[0] + m1[13] * m2[4] + m1[14] * m2[8] + m1[15] * m2[12],
        m1[12] * m2[1] + m1[13] * m2[5] + m1[14] * m2[9] + m1[15] * m2[13],
        m1[12] * m2[2] + m1[13] * m2[6] + m1[14] * m2[10] + m1[15] * m2[14],
        m1[12] * m2[3] + m1[13] * m2[7] + m1[14] * m2[11] + m1[15] * m2[15],
    ]


def transform(p, m):
    """
    Применяет матричное преобразование m к заданной точке p.
    """
    return (p[0] * m[0] + p[1] * m[4] + p[2] * m[8] + m[12],
            p[0] * m[1] + p[1] * m[5] + p[2] * m[9] + m[13],
            p[0] * m[2] + p[1] * m[6] + p[2] * m[10] + m[14])


vertices = []  # Список координат вершин 3D-объекта
surfaces = []  # Список вершин поверхностей, составляющих 3D-объект

# Преобразование, корректирующее представление модели в формате OBJ (меняет оси)
viewport_adjustment = mm(rotation(-3.14 / 2, 'x'), rotation(3.14 / 2, 'z'))

# Парсинг 3D-модели из файла
with open(MODEL_SOURCE) as f:
    for ll in f.readlines():
        d = ll.split(' ')
        if d[0] == 'v':
            # Преобразует тройку в кортеж вещественных чисел и производит поворот модели по двум осям
            vertex = transform((float(d[1]), float(d[2]), float(d[3])), viewport_adjustment)
            vertices.append(vertex)
        elif d[0] == 'f':
            surface = tuple(map(lambda v: int(v.split('/')[0]), d[1:]))
            surfaces.append(surface)

# Начальная матрица преобразований - единичная.
transformation = [
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
]

# Коэфициент смещения центра картинной плоскости (см. комментарий ниже)
pk = 10

# Матрица преобразования перспективного проецирования.
# Центр проектирования лежит в точке (pk, 0, 0).
project_transformation = [
    0, 0, 0, -1 / pk,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
]

# Матрица, по которой координаты (_,y,z) преобразуются в (y,z,0).
yz_to_xy_transformation = [
    0, 0, 0, 0,
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 0, 1
]


def cull(v):
    x, y = v
    return min(max(0, round(x)), SCREEN_WIDTH - 1), min(max(0, round(y)), SCREEN_HEIGHT - 1)


def project(point):
    """
    Проецирует точку (x,y,z) на некоторую картинную плоскость.

    Возвращает пару значений в оконных координатах.
    """
    x, y, z = transform(point, project_transformation)

    w = point[0] * project_transformation[3] + \
        point[1] * project_transformation[7] + \
        point[2] * project_transformation[11] + \
        project_transformation[15]

    x, y, z = x / w, y / w, z / w

    x, y, _ = transform((x, y, z), yz_to_xy_transformation)

    scale = 250
    offset_x = SCREEN_WIDTH / 2
    offset_y = SCREEN_HEIGHT / 2

    return cull((x * scale + offset_x, y * scale + offset_y))


def draw():
    """
    Отрисовка модели
    """

    # Очистка буффера
    sdl2.ext.fill(window_surface, BLACK)

    pixels = sdl2.ext.PixelView(window_surface)

    # Итерирование по списку граней, отрисовка ребер, входящих в грани
    for s in surfaces:
        a, b = tee(s)
        next(b, None)
        for e in zip(a, b):
            e1 = transform(vertices[e[0] - 1], transformation)
            e2 = transform(vertices[e[1] - 1], transformation)

            x1, y1 = project(e1)
            x2, y2 = project(e2)

            line(pixels, x1, y1, x2, y2, WHITE)

    del pixels


def repl():
    """
    Запуск интерактивного ввода.
    """
    lock = threading.Lock()

    global transformation

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
            transformation = mm(translation(ox, oy, oz), transformation)

        elif command == 'scale' or command == 's':
            sx, sy, sz = map(lambda v: 1. if v == '_' else float(v), args[:3])
            transformation = mm(scale(sx, sy, sz), transformation)

        elif command == 'rotate' or command == 'r':
            angle = float(args[0])
            direction = args[1]
            transformation = mm(rotation(angle, direction), transformation)

        elif command == 'mirror' or command == 'm':
            transformation = mm(mirror(args[0]), transformation)

        elif command == 'reset':
            transformation = [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1
            ]

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
