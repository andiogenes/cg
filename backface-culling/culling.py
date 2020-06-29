#!/usr/bin/env python

import random
import sys
import time
from itertools import tee
from math import sin, cos, pi

import sdl2.events
import sdl2.ext

ANGLE_CONSTRAINT = 2 * pi

TIMER_ESTIMATION = 4.5

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)

RED = sdl2.ext.Color(255, 0, 0)
GREEN = sdl2.ext.Color(0, 255, 0)
BLUE = sdl2.ext.Color(0, 0, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

model_source = 'cube.obj'
if len(sys.argv) > 1:
    model_source = sys.argv[1]

sdl2.ext.init()
window = sdl2.ext.Window(
    "Удаление невидимых линий и поверхностей • {}".format(model_source),
    size=(SCREEN_WIDTH, SCREEN_HEIGHT)
)
window.show()

window_surface = window.get_surface()


def line(x0, y0, x1, y1, color):
    """
    Рисует линию заданного цвета, начинающуюся в (x0, y0) и заканчивающуюся в (x1, y1).
    """
    sdl2.ext.line(window_surface, color, (x0, y0, x1, y1))


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


def triaxis_rotation(a, b, c):
    """
    Строит матрицу поворота относительно Z:Y:X.
    """
    return [
        cos(c) * cos(b), cos(a) * sin(c) + cos(c) * sin(b) * sin(a), sin(c) * sin(a) - cos(c) * sin(b) * cos(a), 0,
        -sin(c) * cos(b), cos(c) * cos(a) - sin(c) * sin(b) * sin(a), sin(c) * cos(a) * sin(b) + cos(c) * sin(a), 0,
        sin(b), -cos(b) * sin(a), cos(b) * cos(a), 0,
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


def dot(v1, v2):
    """
    Вычисляет скалярное произведение векторов v1 и v2.
    """
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def transform(p, m):
    """
    Применяет матричное преобразование m к заданной точке p.
    """
    return (p[0] * m[0] + p[1] * m[4] + p[2] * m[8] + m[12],
            p[0] * m[1] + p[1] * m[5] + p[2] * m[9] + m[13],
            p[0] * m[2] + p[1] * m[6] + p[2] * m[10] + m[14])


vertices = []  # Список координат вершин 3D-объекта
surfaces = []  # Список вершин поверхностей, составляющих 3D-объект
normals = []  # Список нормалей к поверхностям

# Преобразование, корректирующее представление модели в формате OBJ (меняет оси)
viewport_adjustment = mm(rotation(-3.14 / 2, 'x'), rotation(3.14 / 2, 'z'))

# Парсинг 3D-модели из файла
with open(model_source) as f:
    for ll in f.readlines():
        d = ll.split(' ')
        if d[0] == 'v':
            # Преобразует тройку в кортеж вещественных чисел и производит поворот модели по двум осям
            vertex = transform((float(d[1]), float(d[2]), float(d[3])), viewport_adjustment)
            vertices.append(vertex)
        elif d[0] == 'f':
            surface = tuple(map(lambda v: int(v.split('/')[0]), d[1:]))
            surfaces.append(surface)
        elif d[0] == 'vn':
            normal = transform((float(d[1]), float(d[2]), float(d[3])), viewport_adjustment)
            normals.append(normal)

# Начальная матрица преобразований - единичная.
transformation = [
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
]

# Матрица преобразований координатной оси.
axis_transformation = [
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
]


def clip(v):
    x, y = v
    return min(max(0, round(x)), SCREEN_WIDTH - 1), min(max(0, round(y)), SCREEN_HEIGHT - 1)


def project(point):
    """
    Проецирует точку (x,y,z) на некоторую картинную плоскость.

    Возвращает пару значений в оконных координатах.
    """

    _, y, z = point

    scale = 125
    offset_x = SCREEN_WIDTH / 2
    offset_y = SCREEN_HEIGHT / 2

    return clip((y * scale + offset_x, z * scale + offset_y))


visible_normals = False  # Если значение истинно, происходит отрисовка нормалей к граням фигуры.
visible_axis = False  # Если значение истинно, происходит отрисовка координатных осей.
flipped_axis = False  # Если значение истинно, происходит переход из системы координат (x, y, z) в (y, x, z).
use_culling = True  # Если значение истинно, используется отсечение невидимых граней.


def draw():
    """
    Отрисовка модели
    """

    # Очистка буффера
    sdl2.ext.fill(window_surface, BLACK)

    # Преобразование (x, y, z) к (y, x, z)
    flip_transformation = None

    if flipped_axis:
        flip_transformation = rotation(-pi / 2, 'z')

    ft = mm(flip_transformation, transformation) if flipped_axis else transformation
    fat = mm(flip_transformation, axis_transformation) if flipped_axis else axis_transformation

    # Отрисовка координатных осей
    if visible_axis:
        ox, oy = project(transform((0, 0, 0), fat))
        xx, xy = project(transform((2, 0, 0), fat))
        yx, yy = project(transform((0, 2, 0), fat))
        zx, zy = project(transform((0, 0, -2), fat))

        line(ox, oy, xx, xy, RED)
        line(ox, oy, yx, yy, GREEN)
        line(ox, oy, zx, zy, BLUE)

    # Итерирование по списку граней, отрисовка ребер, входящих в грани
    for i, s in enumerate(surfaces):
        norm = transform(normals[i], ft)
        face_orientation = dot((0, -1, 0) if flipped_axis else (-1, 0, 0), norm)

        # Отрисовка нормалей
        if visible_normals:
            nx0, ny0 = project(norm)
            nx1, ny1 = project(transform([1.25 * c for c in normals[i]], ft))

            if face_orientation > 0:
                line(nx0, ny0, nx1, ny1, WHITE)
            else:
                line(nx0, ny0, nx1, ny1, RED)

        if use_culling and face_orientation < 0:
            continue

        vs = [transform(vertices[j - 1], ft) for j in s]

        draw_polygon(vs, WHITE)


def draw_polygon(p, color):
    """
    Рисует многоугольник, заданный списком координат [(x0, y0), ..., (xn, yn)], (x0,y0) != (xn, yn).
    Ребра многоугольника окрашиваются в цвет color.
    """
    a, b = tee(p)
    next(b, None)
    for v in zip(a, b):
        x1, y1 = project(v[0])
        x2, y2 = project(v[1])

        line(x1, y1, x2, y2, color)

    # Соединяем первую вершину грани с последней
    x1, y1 = project(p[0])
    x2, y2 = project(p[len(p) - 1])
    line(x1, y1, x2, y2, color)


# Счетчик времени, при пересечении определенной отметки меняется ускорение
timer = 0

# Углы, на которые поворачивается объект
a_angle = 0
b_angle = 0
c_angle = 0

# Скорость, с которой меняются углы поворота
a_vel = 0
b_vel = 0
c_vel = 0

# Ускорение смены углов поворота
a_accel = random.random()
b_accel = random.random()
c_accel = random.random()

last_time = None


def update():
    """
    Обновляет положение объекта за промежуток времени.
    """
    global last_time, timer, a_angle, b_angle, c_angle, a_vel, b_vel, c_vel, a_accel, b_accel, c_accel, transformation

    cur_time = time.time()
    if last_time:
        dt = cur_time - last_time

        timer += dt

        # Если счетчик времени пересек TIMER_ESTIMATION:..
        if timer > TIMER_ESTIMATION:
            # Обнулить счетчик
            timer = 0

            ap = random.random()
            bp = random.random()
            cp = random.random()

            # Изменить ускорение
            a_accel = (1 if ap > 0.5 else -1) * random.random()
            b_accel = (1 if bp > 0.5 else -1) * random.random()
            c_accel = (1 if cp > 0.5 else -1) * random.random()

        # Прирост скорости
        a_vel += a_accel * dt * 0.001
        b_vel += b_accel * dt * 0.001
        c_vel += c_accel * dt * 0.001

        # Прирост углов
        a_angle = (a_angle + a_vel) % ANGLE_CONSTRAINT
        b_angle = (b_angle + b_vel) % ANGLE_CONSTRAINT
        c_angle = (c_angle + c_vel) % ANGLE_CONSTRAINT

        transformation = triaxis_rotation(a_angle, b_angle, c_angle)

    last_time = cur_time

    # Перерисовка изображения
    draw()


# Первичная отрисовка модели
draw()

# Петля событий SDL
running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_r:
                flipped_axis = not flipped_axis
            elif event.key.keysym.sym == sdl2.SDLK_n:
                visible_normals = not visible_normals
            elif event.key.keysym.sym == sdl2.SDLK_a:
                visible_axis = not visible_axis
            elif event.key.keysym.sym == sdl2.SDLK_z:
                use_culling = not use_culling
    update()
    window.refresh()

sdl2.ext.quit()
