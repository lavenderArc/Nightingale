#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: geometry

import random
from collections import namedtuple

# Box tuple, leftTop pos stores in (left, top) with width and height
from src.common.utils.logger import get_log

Box = namedtuple('Box', ['left', 'top', 'width', 'height'])  # pyautogui.locateOnScreen(fp_pic)的返回结构

# Rectangle tuple, leftTop pos stores in (left, top), rightBottom pos stores in (right, bottom)
Rectangle = namedtuple('Rectangle', ['left', 'top', 'right', 'bottom'])

# The size of the Box
Size = namedtuple('Size', ['width', 'height'])

# The Pos
Point = namedtuple('Point', ['x', 'y'])

log = get_log()


def to_rectangle(box: Box) -> Rectangle:
    return Rectangle(box.left, box.top, box.left + box.width, box.top + box.height)


def to_box(rectangle: Rectangle) -> Box:
    return Box(rectangle.left, rectangle.top, rectangle.right - rectangle.left, rectangle.bottom - rectangle.top)


def to_size(geo: Box | Rectangle) -> Size:
    _b = geo
    if isinstance(geo, Rectangle):
        _b = to_box(geo)
    return Size(_b.width, _b.height)


def center(geo: Box | Rectangle) -> Point:
    _b = geo
    if isinstance(geo, Rectangle):
        _b = to_box(geo)
    return Point(_b.left + _b.width // 2, _b.top + _b.height // 2)


def random_point(pt: Point, buffer: Rectangle | Size) -> Point:
    _r = buffer
    if isinstance(buffer, Size):
        _r = Rectangle(-buffer.width, -buffer.height, buffer.width, buffer.height)
    x_random, y_random = random.randint(_r.left, _r.right), random.randint(_r.top, _r.bottom)
    return Point(pt.x + x_random, pt.y + y_random)


def random_center(geo: Box | Rectangle, buffer: Rectangle | Size) -> Point:
    _p = center(geo)
    _buffer = buffer
    if buffer is None:
        _buffer = Size(10, 10)
    return random_point(_p, _buffer)


def random_center_default(geo: Box | Rectangle) -> Point:
    _p = center(geo)
    _buffer = Size(10, 10)
    return random_point(_p, _buffer)


def box_offset(b: Box, left_offset: int, top_offset: int) -> Box:
    return Box(b.left + left_offset, b.top + top_offset, b.width, b.height)
